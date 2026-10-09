//! Spot v2 public channels: documented options, symbol forms and local rejection.

use std::time::Duration;

use serde_json::json;

use super::KrakenPublicWebSocket;
use crate::ws::test_peer::TestPeer;

async fn connected() -> (KrakenPublicWebSocket, TestPeer) {
    let peer = TestPeer::start().await;
    let mut ws = KrakenPublicWebSocket::with_url(peer.url.clone(), Duration::from_secs(5)).unwrap();
    ws.connect().await.unwrap();
    (ws, peer)
}

#[tokio::test]
async fn channels_send_documented_parameters() {
    let (mut ws, mut peer) = connected().await;
    ws.subscribe_ticker("BTC-USD-SPOT").await.unwrap();
    ws.subscribe_ticker_with_options("eth/usd", "bbo", false)
        .await
        .unwrap();
    ws.subscribe_trades("BTC/USD").await.unwrap();
    ws.subscribe_trades_with_options("BTC/USD", true)
        .await
        .unwrap();
    ws.subscribe_orderbook("BTC/USD", 10).await.unwrap();
    ws.subscribe_orderbook_with_options("BTC/USD", 1000, false)
        .await
        .unwrap();
    ws.subscribe_klines("BTC/USD", 60).await.unwrap();
    let id = ws
        .subscribe_klines_with_options("BTC/USD", 21600, false)
        .await
        .unwrap();
    for (index, params) in [
        json!({"channel": "ticker", "symbol": ["BTC/USD"], "event_trigger": "trades", "snapshot": true}),
        json!({"channel": "ticker", "symbol": ["ETH/USD"], "event_trigger": "bbo", "snapshot": false}),
        json!({"channel": "trade", "symbol": ["BTC/USD"], "snapshot": false}),
        json!({"channel": "trade", "symbol": ["BTC/USD"], "snapshot": true}),
        json!({"channel": "book", "symbol": ["BTC/USD"], "depth": 10, "snapshot": true}),
        json!({"channel": "book", "symbol": ["BTC/USD"], "depth": 1000, "snapshot": false}),
        json!({"channel": "ohlc", "symbol": ["BTC/USD"], "interval": 60, "snapshot": true}),
        json!({"channel": "ohlc", "symbol": ["BTC/USD"], "interval": 21600, "snapshot": false}),
    ]
    .into_iter()
    .enumerate()
    {
        assert_eq!(
            peer.next_json().await,
            json!({"method": "subscribe", "params": params, "req_id": index + 1})
        );
    }
    assert_eq!(id, 8);
    ws.subscribe_channel("trade", vec!["BTC/USD".into(), "ETH/USD".into()])
        .await
        .unwrap();
    assert_eq!(
        peer.next_json().await["params"],
        json!({"channel": "trade", "symbol": ["BTC/USD", "ETH/USD"]})
    );
    ws.unsubscribe_channel("trade", vec!["BTC/USD".into()])
        .await
        .unwrap();
    assert_eq!(peer.next_json().await["method"], "unsubscribe");
    let id = ws.ping().await.unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"method": "ping", "req_id": id})
    );
    peer.push_json(&json!({"channel": "heartbeat"}));
    assert_eq!(ws.recv().await.unwrap()["channel"], "heartbeat");
    peer.push("{}");
    assert_eq!(ws.recv_bytes().await.unwrap(), b"{}");
    ws.close().await.unwrap();
    assert!(!ws.is_connected());
}

#[tokio::test]
async fn invalid_options_and_symbols_are_rejected_before_sending() {
    let (mut ws, mut peer) = connected().await;
    assert!(
        ws.subscribe_ticker_with_options("BTC/USD", "last", true)
            .await
            .is_err()
    );
    assert!(ws.subscribe_orderbook("BTC/USD", 50).await.is_err());
    assert!(ws.subscribe_klines("BTC/USD", 120).await.is_err());
    assert!(
        ws.subscribe_channel("spread", vec!["BTC/USD".into()])
            .await
            .is_err()
    );
    assert!(ws.subscribe_channel("trade", vec![]).await.is_err());
    assert!(ws.subscribe_trades("BTC-USD-SWAP").await.is_err());
    assert!(ws.subscribe_trades("XBTUSD").await.is_err());
    assert!(ws.subscribe_trades("BTC/USD!").await.is_err());
    assert!(ws.subscribe_trades(" ").await.is_err());
    assert!(peer.quiet(Duration::from_millis(200)).await);
    assert!(KrakenPublicWebSocket::new(Duration::from_secs(1)).is_ok());
}
