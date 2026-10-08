//! The signed token request and the token-carrying subscription and trading frames,
//! against local peers only.

use std::time::Duration;

use base64::Engine;
use serde_json::json;

use super::KrakenPrivateWebSocket;
use crate::ws::test_peer::{TestPeer, http_sequence};

fn token_body() -> String {
    json!({"error": [], "result": {"token": "ws-token", "expires": 900}}).to_string()
}

async fn connected() -> (KrakenPrivateWebSocket, TestPeer) {
    let peer = TestPeer::start().await;
    let (http, calls) = http_sequence(vec![token_body()]);
    let secret = base64::engine::general_purpose::STANDARD.encode([7u8; 64]);
    let mut ws = KrakenPrivateWebSocket::with_urls(
        "api-key".into(),
        secret,
        Duration::from_secs(5),
        http,
        peer.url.clone(),
    )
    .unwrap();
    assert_eq!(ws.connect().await.unwrap(), "ws-token");
    assert_eq!(ws.token(), Some("ws-token"));
    let calls = calls.join().unwrap();
    assert_eq!(calls[0].method, "POST");
    assert_eq!(calls[0].target, "/0/private/GetWebSocketsToken");
    assert_eq!(calls[0].header("API-Key"), Some("api-key"));
    assert!(calls[0].header("API-Sign").is_some());
    assert!(calls[0].body.contains("nonce="));
    (ws, peer)
}

#[tokio::test]
async fn private_channels_carry_the_token_and_their_options() {
    let (mut ws, mut peer) = connected().await;
    let id = ws
        .subscribe_balances(true, false, Some("all".into()))
        .await
        .unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({
            "method": "subscribe",
            "params": {
                "channel": "balances", "token": "ws-token",
                "snapshot": true, "rebased": false, "users": "all",
            },
            "req_id": id,
        })
    );
    ws.subscribe_executions(true, false, true, false, true, None)
        .await
        .unwrap();
    assert_eq!(
        peer.next_json().await["params"],
        json!({
            "channel": "executions", "token": "ws-token", "snap_orders": true,
            "snap_trades": false, "order_status": true, "rebased": false, "ratecounter": true,
        })
    );
    ws.unsubscribe_balances().await.unwrap();
    ws.unsubscribe_executions().await.unwrap();
    for channel in ["balances", "executions"] {
        let frame = peer.next_json().await;
        assert_eq!(frame["method"], "unsubscribe");
        assert_eq!(
            frame["params"],
            json!({"channel": channel, "token": "ws-token"})
        );
    }
    ws.subscribe_level3(vec!["BTC/USD".into()], 10, true)
        .await
        .unwrap();
    assert_eq!(
        peer.next_json().await["params"],
        json!({"channel": "level3", "token": "ws-token", "symbol": ["BTC/USD"], "depth": 10, "snapshot": true})
    );
    ws.unsubscribe_level3(vec!["BTC/USD".into()], 10)
        .await
        .unwrap();
    assert!(peer.next_json().await["params"].get("snapshot").is_none());
    let id = ws.ping().await.unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"method": "ping", "req_id": id})
    );
}

#[tokio::test]
async fn invalid_subscriptions_are_rejected_before_sending() {
    let (mut ws, mut peer) = connected().await;
    assert!(
        ws.subscribe_balances(true, true, Some("me".into()))
            .await
            .is_err()
    );
    assert!(
        ws.subscribe_level3(vec!["BTC/USD".into()], 50, true)
            .await
            .is_err()
    );
    assert!(ws.subscribe_level3(vec![], 10, true).await.is_err());
    assert!(
        ws.subscribe_level3(vec!["BTC/USD".into(), "BTC/USD".into()], 10, true)
            .await
            .is_err()
    );
    assert!(ws.add_order(json!({"symbol": "BTC/USD"})).await.is_err());
    assert!(ws.trade_request("withdraw", json!({})).await.is_err());
    assert!(peer.quiet(Duration::from_millis(200)).await);
}

#[tokio::test]
async fn trading_requests_carry_the_token() {
    let (mut ws, mut peer) = connected().await;
    let order = json!({
        "symbol": "BTC/USD", "side": "buy", "order_type": "limit",
        "order_qty": 1, "limit_price": 100,
    });
    let id = ws.add_order(order.clone()).await.unwrap();
    let frame = peer.next_json().await;
    assert_eq!(frame["method"], "add_order");
    assert_eq!(frame["req_id"], id);
    let mut expected = order;
    expected["token"] = "ws-token".into();
    assert_eq!(frame["params"], expected);

    ws.amend_order(json!({"order_id": "OABC", "order_qty": 2}))
        .await
        .unwrap();
    ws.cancel_order(json!({"order_id": ["OABC"]}))
        .await
        .unwrap();
    ws.batch_cancel(json!({"orders": ["OABC"]})).await.unwrap();
    ws.cancel_all().await.unwrap();
    ws.cancel_after(60).await.unwrap();
    for method in [
        "amend_order",
        "cancel_order",
        "batch_cancel",
        "cancel_all",
        "cancel_after",
    ] {
        let frame = peer.next_json().await;
        assert_eq!(frame["method"], method);
        assert_eq!(frame["params"]["token"], "ws-token");
    }
    peer.push_json(&json!({"method": "add_order", "success": true}));
    assert_eq!(ws.recv().await.unwrap()["success"], true);
    peer.push("{}");
    assert_eq!(ws.recv_bytes().await.unwrap(), b"{}");
    ws.close().await.unwrap();
    assert!(!ws.is_connected());
}

#[tokio::test]
async fn requests_without_a_token_are_rejected() {
    let peer = TestPeer::start().await;
    let mut ws = KrakenPrivateWebSocket::with_urls(
        "api-key".into(),
        "c2VjcmV0".into(),
        Duration::from_secs(5),
        "http://127.0.0.1:9",
        peer.url.clone(),
    )
    .unwrap();
    assert!(ws.subscribe_balances(true, false, None).await.is_err());
    assert!(ws.cancel_all().await.is_err());
    assert!(KrakenPrivateWebSocket::new(" ".into(), "s".into(), Duration::from_secs(1)).is_err());
    assert!(KrakenPrivateWebSocket::new("k".into(), " ".into(), Duration::from_secs(1)).is_err());
}
