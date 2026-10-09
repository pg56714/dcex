//! Public topics per category, the subscription budget and local rejection, against a local peer.

use std::time::Duration;

use serde_json::json;

use super::BybitPublicWebSocket;
use crate::ws::test_peer::TestPeer;

async fn connected(category: &str) -> (BybitPublicWebSocket, TestPeer) {
    let peer = TestPeer::start().await;
    let mut ws =
        BybitPublicWebSocket::with_url(category, peer.url.clone(), Duration::from_secs(5)).unwrap();
    ws.connect().await.unwrap();
    (ws, peer)
}

#[tokio::test]
async fn linear_topics_use_contract_symbols() {
    let (mut ws, mut peer) = connected("linear").await;
    assert_eq!(ws.category(), "linear");
    assert!(ws.is_connected());
    ws.subscribe_trades("BTC-USDT-SWAP").await.unwrap();
    ws.subscribe_ticker("ETH-USDC-SWAP").await.unwrap();
    ws.subscribe_orderbook("BTCUSDT", 50).await.unwrap();
    ws.subscribe_klines("BTCUSDT", "1h").await.unwrap();
    for topic in [
        "publicTrade.BTCUSDT",
        "tickers.ETHPERP",
        "orderbook.50.BTCUSDT",
        "kline.60.BTCUSDT",
    ] {
        let frame = peer.next_json().await;
        assert_eq!(frame["op"], "subscribe");
        assert_eq!(frame["args"], json!([topic]));
    }
    let id = ws
        .unsubscribe(vec!["tickers.ETHPERP".into()])
        .await
        .unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"req_id": id, "op": "unsubscribe", "args": ["tickers.ETHPERP"]})
    );
    let id = ws.ping().await.unwrap();
    assert_eq!(peer.next_json().await, json!({"req_id": id, "op": "ping"}));
    peer.push_json(&json!({"topic": "publicTrade.BTCUSDT"}));
    assert_eq!(ws.recv().await.unwrap()["topic"], "publicTrade.BTCUSDT");
    peer.push("{}");
    assert_eq!(ws.recv_bytes().await.unwrap(), b"{}");
    ws.close().await.unwrap();
    assert!(!ws.is_connected());
}

#[tokio::test]
async fn categories_reject_mismatched_products_and_options() {
    let (mut ws, mut peer) = connected("linear").await;
    for (result, reason) in [
        (
            ws.subscribe_ticker("BTC-USD-SWAP").await,
            "settlement currency does not match",
        ),
        (
            ws.subscribe_ticker("BTC-USDT-SPOT").await,
            "product type does not match",
        ),
        (
            ws.subscribe_orderbook("BTCUSDT", 25).await,
            "unsupported Bybit orderbook depth 25",
        ),
        (
            ws.subscribe_ticker("BTC USDT").await,
            "unsupported Bybit option symbol",
        ),
        (
            ws.subscribe(vec![]).await,
            "at least one Bybit WebSocket topic",
        ),
        (
            ws.subscribe(vec![" ".into()]).await,
            "topic must not be empty",
        ),
        (
            ws.subscribe(vec!["a".repeat(21_001)]).await,
            "must not exceed 21,000 characters",
        ),
    ] {
        let error = result.unwrap_err().to_string();
        assert!(error.contains(reason), "{reason}: {error}");
    }
    assert!(peer.quiet(Duration::from_millis(200)).await);

    let (mut spot, mut peer) = connected("spot").await;
    spot.subscribe_orderbook("BTC-USDT-SPOT", 1).await.unwrap();
    assert_eq!(
        peer.next_json().await["args"],
        json!(["orderbook.1.BTCUSDT"])
    );
    assert!(
        spot.subscribe_ticker(" ")
            .await
            .unwrap_err()
            .to_string()
            .contains("symbol must not be empty")
    );

    let (mut option, mut peer) = connected("option").await;
    option
        .subscribe_trades("BTC-27DEC24-100000-C")
        .await
        .unwrap();
    assert_eq!(peer.next_json().await["args"], json!(["publicTrade.BTC"]));

    let (mut spread, _peer) = connected("spread").await;
    assert!(
        spread
            .subscribe_klines("SOLUSDT_SOL/USDT", "1h")
            .await
            .is_err()
    );
    assert!(BybitPublicWebSocket::new("perp", Duration::from_secs(1)).is_err());
    for category in ["spot", "linear", "inverse", "option", "rfq", "spread"] {
        assert!(
            BybitPublicWebSocket::new(category, Duration::from_secs(1)).is_ok(),
            "{category}"
        );
    }
}
