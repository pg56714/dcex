//! Contract channels, buffered pre-login events and local validation, against a local peer.

use std::time::Duration;

use serde_json::json;

use super::MexcFuturesWebSocket;
use crate::ws::test_peer::TestPeer;

#[tokio::test]
async fn public_contract_channels() {
    let mut peer = TestPeer::start().await;
    let mut ws = MexcFuturesWebSocket::with_url(peer.url.clone(), Duration::from_secs(5)).unwrap();
    ws.connect().await.unwrap();
    assert!(ws.is_connected());
    ws.subscribe_tickers().await.unwrap();
    ws.subscribe_ticker("BTC_USDT").await.unwrap();
    ws.subscribe_trades("BTC_USDT").await.unwrap();
    ws.subscribe_orderbook_step("BTC_USDT", "0.5")
        .await
        .unwrap();
    ws.subscribe_klines("BTC_USDT", "4h").await.unwrap();
    ws.subscribe_funding_rate("BTC_USDT").await.unwrap();
    ws.subscribe_index_price("BTC_USDT").await.unwrap();
    ws.subscribe_fair_price("BTC_USDT").await.unwrap();
    ws.subscribe("contract", None, None, None).await.unwrap();
    ws.unsubscribe("kline", Some("BTC_USDT"), None, None)
        .await
        .unwrap();
    let btc = json!({"symbol": "BTC_USDT"});
    for frame in [
        json!({"method": "sub.tickers", "param": {}, "gzip": false}),
        json!({"method": "sub.ticker", "param": btc, "gzip": false}),
        json!({"method": "sub.deal", "param": btc, "gzip": false}),
        json!({"method": "sub.depth.step", "param": {"symbol": "BTC_USDT", "step": "0.5"}, "gzip": false}),
        json!({"method": "sub.kline", "param": {"symbol": "BTC_USDT", "interval": "Hour4"}, "gzip": false}),
        json!({"method": "sub.funding.rate", "param": btc, "gzip": false}),
        json!({"method": "sub.index.price", "param": btc, "gzip": false}),
        json!({"method": "sub.fair.price", "param": btc, "gzip": false}),
        json!({"method": "sub.contract"}),
        json!({"method": "unsub.kline", "param": btc, "gzip": false}),
    ] {
        assert_eq!(peer.next_json().await, frame);
    }
    for (result, reason) in [
        (
            ws.subscribe("index", Some("BTC_USDT"), None, None).await,
            "unsupported futures channel",
        ),
        (
            ws.subscribe("tickers", Some("BTC_USDT"), None, None).await,
            "does not accept a symbol",
        ),
        (
            ws.subscribe_klines("BTC_USDT", "2h").await,
            "unsupported kline interval",
        ),
        (
            ws.subscribe("kline", Some("BTC_USDT"), None, None).await,
            "kline subscription requires interval",
        ),
        (
            ws.subscribe("deal", Some("BTC_USDT"), Some("1m"), None)
                .await,
            "interval is only valid for kline",
        ),
        (
            ws.subscribe_orderbook_step("BTC_USDT", "-1").await,
            "step must be positive",
        ),
        (
            ws.subscribe("deal", Some("BTC_USDT"), None, Some("1"))
                .await,
            "step is only valid for depth.step",
        ),
        (
            ws.subscribe_ticker("BTC-USDT-SWAP").await,
            "require a product table",
        ),
        (
            ws.subscribe_ticker("btc_usdt").await,
            "expected contract symbol",
        ),
        (
            ws.set_private_filters(json!([])).await,
            "require successful login",
        ),
    ] {
        let error = result.unwrap_err().to_string();
        assert!(error.contains(reason), "{reason}: {error}");
    }
    assert!(peer.quiet(Duration::from_millis(200)).await);
    assert!(MexcFuturesWebSocket::new(Duration::from_secs(1)).is_ok());
    assert!(
        MexcFuturesWebSocket::new(Duration::from_secs(1))
            .unwrap()
            .with_credentials(" ".into(), "s".into())
            .is_err()
    );
}

#[tokio::test]
async fn events_before_the_login_ack_are_kept_in_order() {
    let mut peer = TestPeer::start().await;
    let mut ws = MexcFuturesWebSocket::with_url(peer.url.clone(), Duration::from_secs(5))
        .unwrap()
        .with_credentials("api-key".into(), "api-secret".into())
        .unwrap();
    // Queued before the handshake: a market push arrives before the login result.
    peer.push(r#"{"channel":"push.ticker","data":{}}"#);
    peer.push(r#"{"channel":"rs.login","data":"success"}"#);
    ws.connect().await.unwrap();
    assert_eq!(peer.next_json().await["method"], "login");
    assert_eq!(
        ws.recv().await.unwrap(),
        br#"{"channel":"push.ticker","data":{}}"#
    );
    ws.set_private_filters(
        json!([{"filter": "order", "rules": ["BTC_USDT"]}, {"filter": "asset"}]),
    )
    .await
    .unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"method": "personal.filter", "param": {"filters": [
            {"filter": "order", "rules": ["BTC_USDT"]}, {"filter": "asset"}]}})
    );
    for (filters, reason) in [
        (json!({}), "filters must be an array"),
        (json!([1]), "filter must be an object"),
        (
            json!([{"filter": "order", "mode": "x"}]),
            "unsupported filter field",
        ),
        (
            json!([{"filter": "liquidation"}]),
            "unsupported private filter",
        ),
        (
            json!([{"filter": "asset", "rules": ["BTC_USDT"]}]),
            "cannot be filtered by symbol",
        ),
        (
            json!([{"filter": "order", "rules": "BTC_USDT"}]),
            "rules must be a symbol array",
        ),
    ] {
        let error = ws
            .set_private_filters(filters)
            .await
            .unwrap_err()
            .to_string();
        assert!(error.contains(reason), "{reason}: {error}");
    }
    ws.ping().await.unwrap();
    assert_eq!(peer.next_json().await, json!({"method": "ping"}));
    ws.close().await.unwrap();
}
