//! Transport behaviour shared by every exchange stream: config checks, control frames,
//! timeouts and disconnects, against a local peer only.

use std::time::Duration;

use serde_json::json;
use tokio::net::TcpListener;
use tokio_tungstenite::tungstenite::Message;

use super::test_peer::TestPeer;
use super::{WebSocketConfig, WebSocketConnection};
use crate::DcexError;

fn connection(url: &str, timeout: Duration) -> WebSocketConnection {
    WebSocketConnection::new(WebSocketConfig::new(url, timeout).unwrap())
}

#[test]
fn config_rejects_empty_url_and_zero_timeout() {
    assert!(WebSocketConfig::new("  ", Duration::from_secs(1)).is_err());
    assert!(WebSocketConfig::new("ws://127.0.0.1:9", Duration::ZERO).is_err());
    let config = WebSocketConfig::new("ws://127.0.0.1:9", Duration::from_secs(1)).unwrap();
    assert_eq!(connection(&config.url, config.timeout).config(), &config);
}

#[tokio::test]
async fn using_a_connection_before_connect_is_an_input_error() {
    let mut conn = connection("ws://127.0.0.1:9", Duration::from_secs(1));
    assert!(!conn.is_connected());
    for error in [
        conn.send_text("x").await.unwrap_err(),
        conn.send_ping(Vec::new()).await.unwrap_err(),
        conn.recv_text().await.unwrap_err(),
        conn.recv_bytes().await.unwrap_err(),
    ] {
        assert!(matches!(error, DcexError::InvalidInput(_)), "{error}");
    }
    // Closing an unopened connection is a no-op.
    conn.close().await.unwrap();
}

#[tokio::test]
async fn invalid_urls_and_headers_fail_before_dialing() {
    let mut conn = connection("not a url", Duration::from_secs(1));
    assert!(matches!(
        conn.connect().await.unwrap_err(),
        DcexError::InvalidInput(_)
    ));
    let peer = TestPeer::start().await;
    let mut conn = connection(&peer.url, Duration::from_secs(1));
    for header in [("bad name", "v"), ("X-Ok", "bad\nvalue")] {
        let error = conn
            .connect_with_headers(vec![(header.0.into(), header.1.into())])
            .await
            .unwrap_err();
        assert!(matches!(error, DcexError::InvalidInput(_)), "{error}");
    }
    assert!(!conn.is_connected());
}

#[tokio::test]
async fn refused_and_stalled_handshakes_are_transport_errors() {
    let closed = TcpListener::bind("127.0.0.1:0").await.unwrap();
    let url = format!("ws://{}", closed.local_addr().unwrap());
    drop(closed);
    // Windows retries a refused SYN until the timeout, so either message is a transport error.
    let error = connection(&url, Duration::from_millis(500))
        .connect()
        .await
        .unwrap_err();
    assert!(matches!(error, DcexError::Transport(_)), "{error}");

    // Accepts TCP but never answers the upgrade.
    let stalled = TcpListener::bind("127.0.0.1:0").await.unwrap();
    let url = format!("ws://{}", stalled.local_addr().unwrap());
    let holder = tokio::spawn(async move {
        let (_socket, _) = stalled.accept().await.unwrap();
        tokio::time::sleep(Duration::from_secs(5)).await;
    });
    let error = connection(&url, Duration::from_millis(200))
        .connect()
        .await
        .unwrap_err();
    assert!(error.to_string().contains("timed out"), "{error}");
    holder.abort();
}

#[tokio::test]
async fn reconnecting_while_open_keeps_the_existing_stream() {
    let mut peer = TestPeer::start().await;
    let mut conn = connection(&peer.url, Duration::from_secs(5));
    conn.connect_with_headers(vec![("X-Trace".into(), "1".into())])
        .await
        .unwrap();
    assert_eq!(peer.next_handshake().await.header("x-trace"), Some("1"));
    conn.connect().await.unwrap();
    conn.send_json(&json!({"n": 1})).await.unwrap();
    assert_eq!(peer.next_json().await, json!({"n": 1}));
    // No second handshake was made.
    assert!(
        tokio::time::timeout(Duration::from_millis(200), peer.next_handshake())
            .await
            .is_err()
    );
}

#[tokio::test]
async fn server_pings_are_answered_and_control_frames_skipped() {
    let mut peer = TestPeer::start().await;
    let mut conn = connection(&peer.url, Duration::from_secs(5));
    conn.connect().await.unwrap();
    peer.push_message(Message::Ping(b"hb-1".to_vec().into()));
    peer.push_message(Message::Pong(Vec::new().into()));
    peer.push("text");
    assert_eq!(conn.recv_text().await.unwrap(), "text");
    assert_eq!(peer.next_pong().await, b"hb-1");

    peer.push_message(Message::Ping(b"hb-2".to_vec().into()));
    peer.push_message(Message::Binary(vec![0xff, 0x00].into()));
    assert_eq!(conn.recv_bytes().await.unwrap(), vec![0xff, 0x00]);
    assert_eq!(peer.next_pong().await, b"hb-2");

    conn.send_ping(b"client".to_vec()).await.unwrap();
    // The peer answers the client ping; recv skips that pong and returns the next frame.
    peer.push("after");
    assert_eq!(conn.recv_text().await.unwrap(), "after");
}

#[tokio::test]
async fn binary_frames_decode_as_utf8_text_or_fail() {
    let peer = TestPeer::start().await;
    let mut conn = connection(&peer.url, Duration::from_secs(5));
    conn.connect().await.unwrap();
    peer.push_message(Message::Binary(b"{\"a\":1}".to_vec().into()));
    assert_eq!(conn.recv_json().await.unwrap(), json!({"a": 1}));
    peer.push_message(Message::Binary(vec![0xff].into()));
    assert!(matches!(
        conn.recv_text().await.unwrap_err(),
        DcexError::Decode(_)
    ));
    peer.push("not json");
    assert!(matches!(
        conn.recv_json().await.unwrap_err(),
        DcexError::Decode(_)
    ));
}

#[tokio::test]
async fn receive_timeouts_keep_the_connection_open() {
    let mut peer = TestPeer::start().await;
    let mut conn = connection(&peer.url, Duration::from_millis(300));
    conn.connect().await.unwrap();
    assert!(
        conn.recv_text()
            .await
            .unwrap_err()
            .to_string()
            .contains("timed out")
    );
    assert!(
        conn.recv_bytes()
            .await
            .unwrap_err()
            .to_string()
            .contains("timed out")
    );
    assert!(conn.is_connected());
    conn.send_text("still here").await.unwrap();
    assert_eq!(peer.next_text().await, "still here");
}

#[tokio::test]
async fn server_close_marks_the_connection_closed_and_allows_reconnect() {
    let mut peer = TestPeer::start().await;
    let mut conn = connection(&peer.url, Duration::from_secs(5));
    conn.connect().await.unwrap();
    peer.wait_connections(1).await;
    peer.close_connection();
    assert!(
        conn.recv_text()
            .await
            .unwrap_err()
            .to_string()
            .contains("closed")
    );
    assert!(!conn.is_connected());

    conn.connect().await.unwrap();
    peer.wait_connections(1).await;
    peer.close_connection();
    assert!(
        conn.recv_bytes()
            .await
            .unwrap_err()
            .to_string()
            .contains("closed")
    );
    assert!(!conn.is_connected());

    conn.connect().await.unwrap();
    conn.send_text("again").await.unwrap();
    assert_eq!(peer.next_text().await, "again");
    conn.close().await.unwrap();
    assert!(!conn.is_connected());
}
