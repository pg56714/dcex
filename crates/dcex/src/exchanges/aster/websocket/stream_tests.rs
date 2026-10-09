//! Public stream names and the private listen-key lifecycle, against local peers only.

use std::time::Duration;

use serde_json::json;

use super::{AsterPrivateWebSocket, AsterPublicWebSocket};
use crate::exchanges::aster::AsterMarket;
use crate::ws::test_peer::{TestPeer, http_sequence};

const USER: &str = "0x0000000000000000000000000000000000000001";
const SIGNER: &str = "0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a";

fn private_key() -> String {
    format!("0x{}", "11".repeat(32))
}

async fn public(market: AsterMarket) -> (AsterPublicWebSocket, TestPeer) {
    let peer = TestPeer::start().await;
    let mut ws =
        AsterPublicWebSocket::with_url(market, peer.url.clone(), Duration::from_secs(5)).unwrap();
    ws.connect().await.unwrap();
    (ws, peer)
}

#[tokio::test]
async fn futures_streams_use_documented_names() {
    let (mut ws, mut peer) = public(AsterMarket::Futures).await;
    assert_eq!(ws.market(), AsterMarket::Futures);
    ws.subscribe_trades("BTC-USDT-SWAP").await.unwrap();
    ws.subscribe_agg_trades("BTC-USDT-SWAP").await.unwrap();
    ws.subscribe_orderbook("BTC-USDT-SWAP").await.unwrap();
    ws.subscribe_book_ticker("BTC-USDT-SWAP").await.unwrap();
    ws.subscribe_ticker("BTC-USDT-SWAP").await.unwrap();
    ws.subscribe_klines("BTC-USDT-SWAP", "1M").await.unwrap();
    ws.subscribe_mark_price("BTC-USDT-SWAP", false)
        .await
        .unwrap();
    let id = ws
        .subscribe_mark_price("BTC-USDT-SWAP", true)
        .await
        .unwrap();
    for (index, stream) in [
        "btcusdt@aggTrade",
        "btcusdt@aggTrade",
        "btcusdt@depth",
        "btcusdt@bookTicker",
        "btcusdt@ticker",
        "btcusdt@kline_1M",
        "btcusdt@markPrice",
        "btcusdt@markPrice@1s",
    ]
    .iter()
    .enumerate()
    {
        assert_eq!(
            peer.next_json().await,
            json!({"method": "SUBSCRIBE", "params": [stream], "id": index + 1})
        );
    }
    assert_eq!(id, 8);
    let id = ws.unsubscribe(vec!["btcusdt@depth".into()]).await.unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"method": "UNSUBSCRIBE", "params": ["btcusdt@depth"], "id": id})
    );
    let id = ws.list_subscriptions().await.unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"method": "LIST_SUBSCRIPTIONS", "id": id})
    );
    peer.push_json(&json!({"e": "aggTrade"}));
    assert_eq!(ws.recv().await.unwrap()["e"], "aggTrade");
    peer.push("{}");
    assert_eq!(ws.recv_bytes().await.unwrap(), b"{}");
    ws.close().await.unwrap();
    assert!(!ws.is_connected());
}

#[tokio::test]
async fn spot_streams_use_trade_and_reject_futures_only_input() {
    let (mut ws, mut peer) = public(AsterMarket::Spot).await;
    ws.subscribe_trades("BTCUSDT").await.unwrap();
    assert_eq!(peer.next_json().await["params"], json!(["btcusdt@trade"]));
    assert!(ws.subscribe_mark_price("BTCUSDT", false).await.is_err());
    assert!(ws.subscribe_klines("BTCUSDT", "2m").await.is_err());
    assert!(ws.subscribe_ticker("BTC/USDT").await.is_err());
    assert!(ws.subscribe(vec![]).await.is_err());
    assert!(ws.subscribe(vec![" ".into()]).await.is_err());
    assert!(peer.quiet(Duration::from_millis(200)).await);
}

fn private(market: AsterMarket, http: &str, ws: &str) -> AsterPrivateWebSocket {
    AsterPrivateWebSocket::with_urls(
        Some(USER.into()),
        SIGNER.into(),
        private_key(),
        market,
        Duration::from_secs(5),
        http.into(),
        http.into(),
        ws.into(),
    )
    .unwrap()
}

#[tokio::test]
async fn futures_listen_key_lifecycle_scopes_the_stream() {
    let mut peer = TestPeer::start().await;
    let (http, calls) = http_sequence(vec![
        json!({"listenKey": "lk-f"}).to_string(),
        "{}".into(),
        "{}".into(),
    ]);
    let mut ws = private(AsterMarket::Futures, &http, &peer.url);
    assert_eq!(ws.market(), AsterMarket::Futures);
    assert_eq!(ws.connect().await.unwrap(), "lk-f");
    assert_eq!(peer.next_handshake().await.path, "/ws/lk-f");
    // An open stream keeps its key instead of minting another.
    assert_eq!(ws.connect().await.unwrap(), "lk-f");
    ws.keep_alive().await.unwrap();
    peer.push_json(&json!({"e": "ORDER_TRADE_UPDATE"}));
    assert_eq!(ws.recv().await.unwrap()["e"], "ORDER_TRADE_UPDATE");
    ws.close().await.unwrap();
    assert_eq!(ws.listen_key(), None);
    assert!(!ws.is_connected());

    let calls = calls.join().unwrap();
    let methods: Vec<&str> = calls.iter().map(|call| call.method.as_str()).collect();
    assert_eq!(methods, ["POST", "PUT", "DELETE"]);
    assert!(
        calls
            .iter()
            .all(|call| call.target.starts_with("/fapi/v3/listenKey"))
    );
}

#[tokio::test]
async fn spot_listen_key_lifecycle_names_the_key() {
    let mut peer = TestPeer::start().await;
    let (http, calls) = http_sequence(vec![
        json!({"listenKey": "lk-s"}).to_string(),
        "{}".into(),
        "{}".into(),
    ]);
    let mut ws = private(AsterMarket::Spot, &http, &peer.url);
    ws.connect().await.unwrap();
    assert_eq!(peer.next_handshake().await.path, "/ws/lk-s");
    ws.keep_alive().await.unwrap();
    peer.push("{}");
    assert_eq!(ws.recv_bytes().await.unwrap(), b"{}");
    ws.close().await.unwrap();
    let calls = calls.join().unwrap();
    assert!(
        calls
            .iter()
            .all(|call| call.target.starts_with("/api/v3/listenKey"))
    );
    // Signed non-GET requests carry their parameters in the form body.
    for call in &calls[1..] {
        assert_eq!(
            call.header("Content-Type"),
            Some("application/x-www-form-urlencoded")
        );
        assert!(call.body.contains("listenKey=lk-s"), "{}", call.method);
    }
}

#[tokio::test]
async fn invalid_keys_credentials_and_unconnected_use_are_rejected() {
    let (http, calls) = http_sequence(vec!["{}".into()]);
    let mut ws = private(AsterMarket::Spot, &http, "ws://127.0.0.1:9");
    assert!(ws.keep_alive().await.is_err());
    assert!(ws.recv().await.is_err());
    // Closing without a key sends nothing; a response without listenKey is a decode error.
    ws.close().await.unwrap();
    assert!(ws.create_listen_key().await.is_err());
    assert!(ws.connect_with_listen_key(" ".into()).await.is_err());
    assert_eq!(calls.join().unwrap().len(), 1);

    let build = |user: Option<&str>, signer: &str, key: &str, market, ws_url: &str| {
        AsterPrivateWebSocket::with_urls(
            user.map(Into::into),
            signer.into(),
            key.into(),
            market,
            Duration::from_secs(1),
            "http://127.0.0.1:9".into(),
            "http://127.0.0.1:9".into(),
            ws_url.into(),
        )
    };
    let url = "ws://127.0.0.1:9";
    assert!(build(None, SIGNER, &private_key(), AsterMarket::Futures, url).is_err());
    assert!(
        build(
            Some("0x12"),
            SIGNER,
            &private_key(),
            AsterMarket::Futures,
            url
        )
        .is_err()
    );
    assert!(build(Some(USER), "0x12", &private_key(), AsterMarket::Spot, url).is_err());
    assert!(build(Some(USER), SIGNER, " ", AsterMarket::Spot, url).is_err());
    assert!(build(Some(USER), SIGNER, &private_key(), AsterMarket::Spot, " / ").is_err());
}
