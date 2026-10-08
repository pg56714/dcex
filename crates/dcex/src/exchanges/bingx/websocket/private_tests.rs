//! The listen-key lifecycle, gzip frames and application pings, against local peers only.

use std::io::Write;
use std::time::Duration;

use flate2::Compression;
use flate2::write::GzEncoder;
use serde_json::json;
use tokio_tungstenite::tungstenite::Message;

use super::BingxPrivateWebSocket;
use crate::ws::test_peer::{TestPeer, http_sequence};

fn gzip(text: &str) -> Vec<u8> {
    let mut encoder = GzEncoder::new(Vec::new(), Compression::default());
    encoder.write_all(text.as_bytes()).unwrap();
    encoder.finish().unwrap()
}

fn spot(http: &str, ws: &str) -> BingxPrivateWebSocket {
    BingxPrivateWebSocket::with_spot_urls(
        "api-key".into(),
        "api-secret".into(),
        Duration::from_secs(5),
        http.into(),
        ws.into(),
    )
    .unwrap()
}

#[tokio::test]
async fn listen_key_lifecycle_uses_the_documented_routes() {
    let mut peer = TestPeer::start().await;
    let (http, calls) = http_sequence(vec![
        json!({"listenKey": "lk-1"}).to_string(),
        json!({"code": 0}).to_string(),
        json!({"code": 0}).to_string(),
    ]);
    let mut ws = spot(&http, &format!("{}/market", peer.url));
    assert_eq!(ws.connect().await.unwrap(), "lk-1");
    let handshake = peer.next_handshake().await;
    assert_eq!(handshake.path, "/market?listenKey=lk-1");
    assert_eq!(handshake.header("Accept-Encoding"), Some("gzip"));
    // A second connect reuses the open stream and its key.
    assert_eq!(ws.connect().await.unwrap(), "lk-1");
    assert_eq!(ws.keep_alive().await.unwrap(), "lk-1");
    ws.close().await.unwrap();
    assert_eq!(ws.listen_key(), None);
    assert!(!ws.is_connected());

    let calls = calls.join().unwrap();
    let methods: Vec<&str> = calls.iter().map(|call| call.method.as_str()).collect();
    assert_eq!(methods, ["POST", "PUT", "DELETE"]);
    for call in &calls {
        assert!(call.target.starts_with("/openApi/user/auth/userDataStream"));
        assert_eq!(call.header("X-BX-APIKEY"), Some("api-key"));
    }
    assert!(calls[1].target.contains("listenKey=lk-1"));
    assert!(calls[2].target.contains("listenKey=lk-1"));
}

#[tokio::test]
async fn spot_orders_subscribe_and_gzip_pings_are_answered() {
    let mut peer = TestPeer::start().await;
    let mut ws = spot("http://127.0.0.1:9", &format!("{}/market", peer.url));
    ws.connect_with_listen_key(" lk-2 ".into()).await.unwrap();
    assert_eq!(ws.listen_key(), Some("lk-2"));
    let id = ws.subscribe_orders().await.unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"id": id, "reqType": "sub", "dataType": "spot.executionReport"})
    );
    let id = ws.unsubscribe("spot.executionReport").await.unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"id": id, "reqType": "unsub", "dataType": "spot.executionReport"})
    );

    peer.push_message(Message::Binary(gzip("Ping").into()));
    peer.push_message(Message::Binary(
        gzip("{\"dataType\":\"spot.executionReport\"}").into(),
    ));
    assert_eq!(ws.recv().await.unwrap()["dataType"], "spot.executionReport");
    assert_eq!(peer.next_text().await, "Pong");

    peer.push("ping");
    peer.push("Pong");
    assert_eq!(ws.recv_bytes().await.unwrap(), b"\"Pong\"");
    assert_eq!(peer.next_text().await, "Pong");

    ws.ping().await.unwrap();
    assert_eq!(peer.next_text().await, "Ping");
    assert!(ws.subscribe("bad type!").await.is_err());
    assert!(ws.connect_with_listen_key("a/b".into()).await.is_err());
    assert!(peer.quiet(Duration::from_millis(200)).await);
}

#[tokio::test]
async fn swap_streams_push_without_subscriptions() {
    let peer = TestPeer::start().await;
    let mut ws = BingxPrivateWebSocket::with_urls(
        "api-key".into(),
        "api-secret".into(),
        Duration::from_secs(5),
        "http://127.0.0.1:9".into(),
        format!("{}/swap-market", peer.url),
    )
    .unwrap();
    ws.connect_with_listen_key("lk-3".into()).await.unwrap();
    assert!(ws.subscribe_orders().await.is_err());
    assert!(ws.unsubscribe("spot.executionReport").await.is_err());
}

#[test]
fn credentials_and_urls_are_validated() {
    let timeout = Duration::from_secs(1);
    assert!(BingxPrivateWebSocket::new(" ".into(), "s".into(), timeout).is_err());
    assert!(BingxPrivateWebSocket::new("k".into(), " ".into(), timeout).is_err());
    assert!(
        BingxPrivateWebSocket::with_spot_urls(
            "k".into(),
            "s".into(),
            timeout,
            "http://127.0.0.1:9".into(),
            " / ".into(),
        )
        .is_err()
    );
}
