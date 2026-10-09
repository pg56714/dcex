//! Public market selection by URL, gzip pings, decoding failures and local checks.

use std::io::Write;
use std::time::Duration;

use flate2::Compression;
use flate2::write::GzEncoder;
use serde_json::json;
use tokio_tungstenite::tungstenite::Message;

use super::BingxPublicWebSocket;
use crate::ws::test_peer::TestPeer;

fn gzip(bytes: &[u8]) -> Vec<u8> {
    let mut encoder = GzEncoder::new(Vec::new(), Compression::default());
    encoder.write_all(bytes).unwrap();
    encoder.finish().unwrap()
}

#[tokio::test]
async fn swap_url_selects_the_swap_market() {
    let mut peer = TestPeer::start().await;
    let mut ws =
        BingxPublicWebSocket::with_url(format!("{}/swap-market", peer.url), Duration::from_secs(5))
            .unwrap();
    ws.connect().await.unwrap();
    assert!(ws.is_connected());
    ws.subscribe_orderbook("BTC-USDT", 20, "200ms")
        .await
        .unwrap();
    assert_eq!(peer.next_json().await["dataType"], "BTC-USDT@depth20@200ms");
    let id = ws.unsubscribe("BTC-USDT@depth20@200ms").await.unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"id": id, "reqType": "unsub", "dataType": "BTC-USDT@depth20@200ms"})
    );
    for (result, reason) in [
        (
            ws.subscribe_orderbook("BTC-USDT", 7, "500ms").await,
            "unsupported BingX orderbook depth",
        ),
        (
            ws.subscribe_klines("BTC-USDT", " ").await,
            "kline interval must not be empty",
        ),
        (ws.subscribe_ticker(" ").await, "symbol must not be empty"),
        (
            ws.subscribe_ticker("BTC_USDT").await,
            "unsupported BingX WebSocket symbol",
        ),
        (
            ws.subscribe_ticker("BTC-USDT-SPOT").await,
            "requires the matching public WebSocket URL",
        ),
        (ws.subscribe(" ").await, "dataType must not be empty"),
    ] {
        let error = result.unwrap_err().to_string();
        assert!(error.contains(reason), "{reason}: {error}");
    }
    assert!(peer.quiet(Duration::from_millis(200)).await);
}

#[tokio::test]
async fn gzip_pings_are_answered_and_bad_frames_are_decode_errors() {
    let mut peer = TestPeer::start().await;
    let mut ws =
        BingxPublicWebSocket::with_url(format!("{}/market", peer.url), Duration::from_secs(5))
            .unwrap();
    ws.connect().await.unwrap();
    ws.subscribe_ticker("BTC-USDT-SPOT").await.unwrap();
    assert_eq!(peer.next_json().await["dataType"], "BTC-USDT@ticker");
    peer.push_message(Message::Binary(gzip(b"Ping").into()));
    peer.push_message(Message::Binary(
        gzip(b"{\"dataType\":\"BTC-USDT@ticker\"}").into(),
    ));
    assert_eq!(ws.recv().await.unwrap()["dataType"], "BTC-USDT@ticker");
    assert_eq!(peer.next_text().await, "Pong");
    peer.push("Ping");
    peer.push("{}");
    assert_eq!(ws.recv_bytes().await.unwrap(), b"{}");
    assert_eq!(peer.next_text().await, "Pong");
    ws.ping().await.unwrap();
    assert_eq!(peer.next_text().await, "Ping");

    peer.push("not json");
    assert!(
        ws.recv()
            .await
            .unwrap_err()
            .to_string()
            .contains("failed to decode BingX WebSocket JSON")
    );
    // Binary that is neither UTF-8 nor gzip, and gzip that inflates to invalid UTF-8.
    peer.push_message(Message::Binary(vec![0xff, 0x00, 0x01].into()));
    assert!(
        ws.recv()
            .await
            .unwrap_err()
            .to_string()
            .contains("text payload")
    );
    peer.push_message(Message::Binary(vec![0x1f, 0x8b, 0x00].into()));
    assert!(
        ws.recv()
            .await
            .unwrap_err()
            .to_string()
            .contains("failed to inflate")
    );
    peer.push_message(Message::Binary(gzip(&[0xff, 0xfe]).into()));
    assert!(
        ws.recv()
            .await
            .unwrap_err()
            .to_string()
            .contains("inflated payload")
    );
    assert!(BingxPublicWebSocket::new_swap(Duration::from_secs(1)).is_ok());
}
