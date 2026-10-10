//! UTA V3 private topics, classic margin and equity channels, Reality order books and
//! trading-frame checks, against a local peer.

use std::time::Duration;

use serde_json::{Value, json};

use super::{BitgetPrivateWebSocket, BitgetPrivateWebSocketArg};
use crate::ws::test_peer::TestPeer;

async fn logged_in(path: &str) -> (BitgetPrivateWebSocket, TestPeer) {
    let mut peer = TestPeer::start().await;
    let mut ws = BitgetPrivateWebSocket::with_url(
        "api-key".into(),
        "api-secret".into(),
        "passphrase".into(),
        format!("{}{path}", peer.url),
        Duration::from_secs(5),
    )
    .unwrap();
    // Queued before the handshake: delivered right after the login frame.
    peer.push(r#"{"event":"login","code":0}"#);
    ws.connect().await.unwrap();
    assert!(ws.is_connected() && ws.is_logged_in());
    assert_eq!(peer.next_json().await["op"], "login");
    (ws, peer)
}

#[tokio::test]
async fn uta_topics_and_reality_order_books() {
    let (mut ws, mut peer) = logged_in("/v3/ws/private").await;
    assert!(ws.is_uta_v3());
    ws.subscribe_orders().await.unwrap();
    ws.subscribe_fills().await.unwrap();
    ws.subscribe_positions().await.unwrap();
    ws.subscribe_account().await.unwrap();
    for topic in ["order", "fill", "position", "account"] {
        assert_eq!(
            peer.next_json().await,
            json!({"op": "subscribe", "args": [{"instType": "UTA", "topic": topic}]})
        );
    }
    ws.subscribe_channel_with_inst_id("UTA", "fast-fill", "BTCUSDT")
        .await
        .unwrap();
    assert_eq!(
        peer.next_json().await["args"][0],
        json!({"instType": "UTA", "topic": "fast-fill", "symbol": "BTCUSDT"})
    );
    ws.subscribe(vec![
        BitgetPrivateWebSocketArg::uta("strategy-order").unwrap(),
    ])
    .await
    .unwrap();
    assert_eq!(peer.next_json().await["args"][0]["symbol"], "default");
    ws.subscribe_reality_orderbook("BTCUSDT").await.unwrap();
    ws.unsubscribe_reality_orderbook("BTCUSDT").await.unwrap();
    for op in ["subscribe", "unsubscribe"] {
        assert_eq!(
            peer.next_json().await,
            json!({"op": op, "args": [{"instType": "UTA", "topic": "reality-orderbook", "symbol": "BTCUSDT"}]})
        );
    }
    ws.unsubscribe_channel("UTA", "order").await.unwrap();
    ws.unsubscribe_channel_with_inst_id("UTA", "fast-fill", "BTCUSDT")
        .await
        .unwrap();
    assert_eq!(peer.next_json().await["op"], "unsubscribe");
    assert_eq!(peer.next_json().await["op"], "unsubscribe");
    ws.ping().await.unwrap();
    assert_eq!(peer.next_text().await, "ping");
    peer.push_json(&json!({"arg": {"topic": "order"}, "data": []}));
    assert_eq!(ws.recv().await.unwrap()["arg"]["topic"], "order");
    ws.close().await.unwrap();
    assert!(!ws.is_logged_in());
}

#[tokio::test]
async fn uta_endpoint_rejects_classic_and_malformed_topics() {
    let (mut ws, mut peer) = logged_in("/v3/ws/private").await;
    for (result, reason) in [
        (ws.subscribe_equity("UTA").await, "UTA has no equity topic"),
        (
            ws.subscribe_equity("USDT-FUTURES").await,
            "only accepts instType=UTA topics",
        ),
        (
            ws.subscribe_channel("UTA", "orders").await,
            "unsupported Bitget UTA private topic",
        ),
        (
            ws.subscribe_channel_with_coin("UTA", "account", "USDT")
                .await,
            "do not support instId or coin",
        ),
        (
            ws.subscribe_channel_with_inst_id_and_coin("UTA", "order", "BTCUSDT", "USDT")
                .await,
            "do not support instId or coin",
        ),
        (
            ws.subscribe_channel("UTA", " ").await,
            "channel must not be empty",
        ),
        (
            ws.subscribe_channel("OPTIONS", "order").await,
            "unsupported Bitget WebSocket instrument type",
        ),
        (
            ws.subscribe_channel_with_inst_id("UTA", "fast-fill", " ")
                .await,
            "instrument ID must not be empty",
        ),
        (
            ws.subscribe_channel_with_inst_id("UTA", "fast-fill", "BTC/USDT")
                .await,
            "unsupported Bitget instrument ID",
        ),
        (
            ws.subscribe(vec![]).await,
            "at least one Bitget private WebSocket channel",
        ),
    ] {
        let error = result.unwrap_err().to_string();
        assert!(error.contains(reason), "{reason}: {error}");
    }
    assert!(BitgetPrivateWebSocketArg::uta("reality-orderbook").is_err());
    assert!(BitgetPrivateWebSocketArg::with_inst_id("UTA", "strategy-order", "BTCUSDT").is_err());
    assert!(BitgetPrivateWebSocketArg::with_coin("UTA", "order", " ").is_err());
    assert!(BitgetPrivateWebSocketArg::with_coin("MARGIN", "account-crossed", "US$").is_err());
    assert!(peer.quiet(Duration::from_millis(200)).await);
}

#[tokio::test]
async fn classic_endpoint_keeps_margin_and_equity_channels() {
    let (mut ws, mut peer) = logged_in("/v2/ws/private").await;
    assert!(!ws.is_uta_v3());
    ws.subscribe_equity("USDT-FUTURES").await.unwrap();
    ws.subscribe_channel_with_coin("MARGIN", "account-crossed", "USDT")
        .await
        .unwrap();
    ws.unsubscribe_channel_with_coin("MARGIN", "account-crossed", "USDT")
        .await
        .unwrap();
    ws.unsubscribe_channel_with_inst_id_and_coin("MARGIN", "orders-isolated", "BTCUSDT", "USDT")
        .await
        .unwrap();
    for (op, arg) in [
        (
            "subscribe",
            json!({"instType": "USDT-FUTURES", "channel": "equity"}),
        ),
        (
            "subscribe",
            json!({"instType": "MARGIN", "channel": "account-crossed", "coin": "USDT"}),
        ),
        (
            "unsubscribe",
            json!({"instType": "MARGIN", "channel": "account-crossed", "coin": "USDT"}),
        ),
        (
            "unsubscribe",
            json!({"instType": "MARGIN", "channel": "orders-isolated", "instId": "BTCUSDT", "coin": "USDT"}),
        ),
    ] {
        assert_eq!(peer.next_json().await, json!({"op": op, "args": [arg]}));
    }
    for (result, reason) in [
        (
            ws.subscribe_orders().await,
            "require the UTA V3 private WebSocket",
        ),
        (
            ws.subscribe_equity("SPOT").await,
            "equity channel supports futures instrument types",
        ),
        (
            ws.subscribe_channel("SPOT", "orders").await,
            "classic subscription was replaced by UTA",
        ),
        (
            ws.subscribe_reality_orderbook("BTCUSDT").await,
            "requires an authenticated UTA V3",
        ),
        (
            ws.trade_request("r1", "cancel-order", None, json!([{"orderId": "1"}]), None)
                .await,
            "requires a logged-in V3 private connection",
        ),
    ] {
        let error = result.unwrap_err().to_string();
        assert!(error.contains(reason), "{reason}: {error}");
    }
    assert!(peer.quiet(Duration::from_millis(200)).await);
}

#[tokio::test]
async fn trading_frames_and_login_rejection() {
    let (mut ws, mut peer) = logged_in("/v3/ws/private").await;
    let order = json!([{"symbol": "BTCUSDT", "orderType": "limit", "qty": "0.01", "price": "100", "side": "buy"}]);
    ws.trade_request(
        "r1",
        "place-order",
        Some("spot"),
        order.clone(),
        Some(1_700_000_000_000),
    )
    .await
    .unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"op": "trade", "id": "r1", "topic": "place-order", "category": "spot",
               "requestTime": "1700000000000", "args": order})
    );

    let mut rejected = TestPeer::start().await;
    let mut ws = BitgetPrivateWebSocket::with_url(
        "k".into(),
        "s".into(),
        "p".into(),
        format!("{}/v3/ws/private", rejected.url),
        Duration::from_secs(5),
    )
    .unwrap();
    rejected.push(r#"{"event":"error","code":30005,"msg":"Invalid ACCESS_KEY"}"#);
    let error = ws.connect().await.unwrap_err().to_string();
    assert!(error.contains("login rejected"), "{error}");
    assert!(!ws.is_logged_in());
    rejected.next_json().await;
    for (key, secret, passphrase) in [(" ", "s", "p"), ("k", " ", "p"), ("k", "s", " ")] {
        assert!(
            BitgetPrivateWebSocket::new(
                key.into(),
                secret.into(),
                passphrase.into(),
                Duration::from_secs(1)
            )
            .is_err()
        );
    }
}

#[track_caller]
fn trade_rejects(
    topic: &str,
    category: Option<&str>,
    args: Value,
    time: Option<u64>,
    reason: &str,
) {
    let error = super::trading::uta("r1", topic, category, args, time)
        .expect_err(reason)
        .to_string();
    assert!(error.contains(reason), "expected {reason:?}, got {error:?}");
}

#[test]
fn trading_validation_messages() {
    let limit =
        json!({"symbol": "BTCUSDT", "orderType": "limit", "qty": "1", "price": "1", "side": "buy"});
    let with = |extra: Value| {
        let mut order = limit.clone();
        order
            .as_object_mut()
            .unwrap()
            .extend(extra.as_object().unwrap().clone());
        json!([order])
    };
    trade_rejects(
        "place-order",
        Some("spot"),
        with(json!({"side": "long"})),
        None,
        "invalid side",
    );
    trade_rejects(
        "place-order",
        Some("spot"),
        with(json!({"leverage": "2"})),
        None,
        "unsupported field: leverage",
    );
    trade_rejects(
        "place-order",
        Some("spot"),
        with(json!({"tpOrderType": "limit", "takeprofit": "110"})),
        None,
        "tpLimitPrice must be a non-empty string",
    );
    trade_rejects(
        "place-order",
        Some("spot"),
        with(json!({"slLimitPrice": "90"})),
        None,
        "stoploss must be a non-empty string",
    );
    trade_rejects(
        "cancel-order",
        Some("spot"),
        json!([{}]),
        None,
        "orderId or clientOid is required",
    );
    trade_rejects(
        "close-position",
        Some("spot"),
        json!([limit.clone()]),
        None,
        "unsupported trading topic",
    );
    trade_rejects(
        "place-order",
        None,
        json!([limit.clone()]),
        None,
        "category is required for placing orders",
    );
    trade_rejects(
        "batch-cancel",
        Some("spot"),
        json!([{"orderId": "1"}]),
        None,
        "batch-cancel does not accept category",
    );
    trade_rejects(
        "cancel-order",
        Some("spot"),
        json!([{"orderId": "1"}]),
        Some(1),
        "requestTime is only supported for place-order",
    );
    trade_rejects(
        "modify-order",
        Some("spot"),
        json!([{"orderId": "1"}]),
        None,
        "modification requires qty or price",
    );
}
