//! The unsigned bullet token, spot and futures topics and interval rules, against local peers.

use std::time::Duration;

use serde_json::json;

use super::KucoinPublicWebSocket;
use crate::exchanges::kucoin::KucoinMarket;
use crate::ws::test_peer::{TestPeer, http_sequence};

fn bullet(endpoint: &str) -> String {
    json!({
        "code": "200000",
        "data": {"token": "public-token", "instanceServers": [{"endpoint": endpoint}]},
    })
    .to_string()
}

async fn connected(market: KucoinMarket) -> (KucoinPublicWebSocket, TestPeer) {
    let mut peer = TestPeer::start().await;
    let (http, calls) = http_sequence(vec![bullet(&peer.url)]);
    let mut ws = KucoinPublicWebSocket::with_market_base_urls(
        Duration::from_secs(5),
        http.clone(),
        http,
        market,
    )
    .unwrap();
    ws.connect().await.unwrap();
    ws.connect().await.unwrap();
    assert_eq!(
        peer.next_handshake().await.path,
        "/?token=public-token&connectId=dcex-1"
    );
    let calls = calls.join().unwrap();
    assert_eq!(calls.len(), 1);
    assert_eq!(
        (calls[0].method.as_str(), calls[0].target.as_str()),
        ("POST", "/api/v1/bullet-public")
    );
    // Public tokens are requested without credentials.
    assert!(calls[0].header("KC-API-KEY").is_none());
    (ws, peer)
}

#[tokio::test]
async fn spot_topics_use_spot_symbols() {
    let (mut ws, mut peer) = connected(KucoinMarket::Spot).await;
    ws.subscribe_ticker("BTC-USDT-SPOT").await.unwrap();
    ws.subscribe_trades("BTC-USDT").await.unwrap();
    ws.subscribe_orderbook("eth-usdt").await.unwrap();
    let id = ws.subscribe_klines("BTC-USDT-SPOT", "6hour").await.unwrap();
    for topic in [
        "/market/ticker:BTC-USDT",
        "/market/match:BTC-USDT",
        "/market/level2:ETH-USDT",
        "/market/candles:BTC-USDT_6hour",
    ] {
        let frame = peer.next_json().await;
        assert_eq!(frame["type"], "subscribe");
        assert_eq!(frame["topic"], topic);
        assert_eq!(frame["privateChannel"], false);
        assert_eq!(frame["response"], true);
    }
    assert_eq!(id, "dcex-5");
    ws.unsubscribe("/market/ticker:BTC-USDT").await.unwrap();
    assert_eq!(peer.next_json().await["type"], "unsubscribe");
    let id = ws.ping().await.unwrap();
    assert_eq!(peer.next_json().await, json!({"id": id, "type": "ping"}));
    peer.push_json(&json!({"type": "message", "topic": "/market/ticker:BTC-USDT"}));
    assert_eq!(ws.recv().await.unwrap()["type"], "message");
    peer.push("{}");
    assert_eq!(ws.recv_bytes().await.unwrap(), b"{}");
    ws.close().await.unwrap();
    assert!(!ws.is_connected());
}

#[tokio::test]
async fn futures_topics_use_contract_symbols() {
    let (mut ws, mut peer) = connected(KucoinMarket::Futures).await;
    ws.subscribe_ticker("BTC-USDT-SWAP").await.unwrap();
    ws.subscribe_trades("XBTUSDTM").await.unwrap();
    ws.subscribe_orderbook("ETH-USDT-SWAP").await.unwrap();
    ws.subscribe_klines("BTC-USDT-SWAP", "1month")
        .await
        .unwrap();
    for topic in [
        "/contractMarket/tickerV2:XBTUSDTM",
        "/contractMarket/execution:XBTUSDTM",
        "/contractMarket/level2:ETHUSDTM",
        "/contractMarket/limitCandle:XBTUSDTM_1month",
    ] {
        assert_eq!(peer.next_json().await["topic"], topic);
    }
}

#[tokio::test]
async fn invalid_input_is_rejected_before_sending() {
    let (mut ws, mut peer) = connected(KucoinMarket::Spot).await;
    // Spot candles have no 5min or 1month; a swap symbol is not a spot symbol.
    assert!(ws.subscribe_klines("BTC-USDT", "5min").await.is_err());
    assert!(ws.subscribe_klines("BTC-USDT", "1month").await.is_err());
    assert!(ws.subscribe_ticker("BTC-USDT-SWAP").await.is_err());
    assert!(ws.subscribe_ticker("BTC/USDT").await.is_err());
    assert!(ws.subscribe("bad topic!").await.is_err());
    assert!(peer.quiet(Duration::from_millis(200)).await);

    let (mut futures, mut peer) = connected(KucoinMarket::Futures).await;
    assert!(futures.subscribe_klines("XBTUSDTM", "6hour").await.is_err());
    // A two-part name is ambiguous for futures without a product table.
    assert!(futures.subscribe_ticker("BTC-USDT").await.is_err());
    assert!(peer.quiet(Duration::from_millis(200)).await);
}

#[tokio::test]
async fn unconnected_use_and_bad_tokens_are_errors() {
    let timeout = Duration::from_secs(1);
    let mut ws = KucoinPublicWebSocket::new(timeout).unwrap();
    assert!(ws.ping().await.is_err());
    assert!(ws.recv().await.is_err());
    ws.close().await.unwrap();
    assert!(KucoinPublicWebSocket::new_futures(timeout).is_ok());
    assert!(
        KucoinPublicWebSocket::with_market_base_urls(
            timeout,
            "http://127.0.0.1:9".into(),
            "http://127.0.0.1:9".into(),
            KucoinMarket::Broker,
        )
        .is_err()
    );
    let (http, calls) = http_sequence(vec![
        json!({"code": "200000", "data": {"token": "t"}}).to_string(),
    ]);
    let mut ws = KucoinPublicWebSocket::with_base_urls(timeout, http.clone(), http).unwrap();
    assert!(ws.connect().await.is_err());
    calls.join().unwrap();
}
