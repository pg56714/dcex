//! Login, subscription and trading frames on a fixed-URL connection, against a local peer.

use std::time::{Duration, SystemTime, UNIX_EPOCH};

use serde_json::json;

use super::OkxPrivateWebSocket;
use crate::ws::test_peer::TestPeer;

async fn logged_in() -> (OkxPrivateWebSocket, TestPeer) {
    let mut peer = TestPeer::start().await;
    let mut ws = OkxPrivateWebSocket::with_url(
        "api-key".into(),
        "api-secret".into(),
        "passphrase".into(),
        peer.url.clone(),
        Duration::from_secs(5),
    )
    .unwrap();
    // Queued before the handshake: delivered right after the login frame.
    peer.push_json(&json!({"event": "login", "code": "0", "msg": ""}));
    ws.connect().await.unwrap();
    assert!(ws.is_logged_in());
    let login = peer.next_json().await;
    assert_eq!(login["op"], "login");
    let arg = &login["args"][0];
    assert_eq!(arg["apiKey"], "api-key");
    assert_eq!(arg["passphrase"], "passphrase");
    let now = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs();
    let timestamp: u64 = arg["timestamp"].as_str().unwrap().parse().unwrap();
    assert!(timestamp.abs_diff(now) < 60, "seconds, not milliseconds");
    assert!(!arg["sign"].as_str().unwrap().is_empty());
    (ws, peer)
}

#[tokio::test]
async fn convenience_channels_send_documented_args() {
    let (mut ws, mut peer) = logged_in().await;
    ws.subscribe_orders().await.unwrap();
    ws.subscribe_orders_for_type("SWAP").await.unwrap();
    ws.subscribe_orders_for_family("FUTURES", "BTC-USD")
        .await
        .unwrap();
    ws.subscribe_orders_for_instrument("SPOT", "BTC-USDT")
        .await
        .unwrap();
    ws.subscribe_account().await.unwrap();
    ws.subscribe_account_for_ccy("BTC").await.unwrap();
    ws.subscribe_positions().await.unwrap();
    ws.subscribe_positions_for_type("MARGIN").await.unwrap();
    for arg in [
        json!({"channel": "orders", "instType": "ANY"}),
        json!({"channel": "orders", "instType": "SWAP"}),
        json!({"channel": "orders", "instType": "FUTURES", "instFamily": "BTC-USD"}),
        json!({"channel": "orders", "instType": "SPOT", "instId": "BTC-USDT"}),
        json!({"channel": "account"}),
        json!({"channel": "account", "ccy": "BTC"}),
        json!({"channel": "positions", "instType": "ANY"}),
        json!({"channel": "positions", "instType": "MARGIN"}),
    ] {
        assert_eq!(
            peer.next_json().await,
            json!({"op": "subscribe", "args": [arg]})
        );
    }
    ws.subscription_args(
        "unsubscribe",
        vec![json!({"channel": "orders", "instType": "SWAP"})],
    )
    .await
    .unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"op": "unsubscribe", "args": [{"channel": "orders", "instType": "SWAP"}]})
    );
    // orders without instType is rejected locally.
    assert!(
        ws.subscription_args("subscribe", vec![json!({"channel": "orders"})])
            .await
            .is_err()
    );
    assert!(ws.subscribe(vec![]).await.is_err());
    assert!(peer.quiet(Duration::from_millis(200)).await);
}

#[tokio::test]
async fn trading_operations_are_validated_then_sent() {
    let (mut ws, mut peer) = logged_in().await;
    let order = json!({"instId": "BTC-USDT", "tdMode": "cash", "side": "buy", "ordType": "limit", "sz": "1", "px": "100"});
    ws.send_operation(
        "req1",
        "order",
        vec![order.clone()],
        Some(1_700_000_000_000),
        false,
    )
    .await
    .unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"id": "req1", "op": "order", "args": [order], "expTime": "1700000000000"})
    );
    ws.send_operation(
        "req2",
        "mass-cancel",
        vec![json!({"instType": "OPTION", "instFamily": "BTC-USD"})],
        None,
        false,
    )
    .await
    .unwrap();
    assert_eq!(peer.next_json().await["op"], "mass-cancel");
    ws.send_operation(
        "req3",
        "sprd-order",
        vec![json!({"sprdId": "BTC-USDT_BTC-USDT-SWAP", "side": "buy", "ordType": "limit", "sz": "1", "px": "-5"})],
        None,
        false,
    )
    .await
    .unwrap();
    assert_eq!(peer.next_json().await["args"][0]["px"], "-5");

    for (id, op, args, all) in [
        ("req4", "withdraw", vec![json!({})], false),
        ("bad id!", "order", vec![order.clone()], false),
        ("req5", "order", vec![order.clone(), order.clone()], false),
        ("req6", "order", vec![json!({"sz": "1e3"})], false),
        ("req7", "order", vec![order.clone()], true),
        (
            "req8",
            "mass-cancel",
            vec![json!({"instType": "OPTION"})],
            false,
        ),
        ("req9", "batch-orders", vec![], false),
    ] {
        assert!(
            ws.send_operation(id, op, args, None, all).await.is_err(),
            "{id} {op}"
        );
    }
    assert!(peer.quiet(Duration::from_millis(200)).await);
    peer.push_json(&json!({"id": "req1", "op": "order", "code": "0"}));
    assert_eq!(ws.recv().await.unwrap()["id"], "req1");
    peer.push("pong");
    assert_eq!(ws.recv_bytes().await.unwrap(), b"pong");
    ws.close().await.unwrap();
    assert!(!ws.is_logged_in() && !ws.is_connected());
}

#[tokio::test]
async fn rejected_login_and_blank_credentials_fail() {
    let peer = TestPeer::start().await;
    let mut ws = OkxPrivateWebSocket::with_url(
        "api-key".into(),
        "api-secret".into(),
        "passphrase".into(),
        peer.url.clone(),
        Duration::from_secs(5),
    )
    .unwrap();
    peer.push_json(&json!({"event": "error", "code": "60009", "msg": "Login failed."}));
    assert!(
        ws.connect()
            .await
            .unwrap_err()
            .to_string()
            .contains("login rejected")
    );
    assert!(!ws.is_logged_in());
    // Trading needs a logged-in connection.
    assert!(
        ws.send_operation(
            "req1",
            "cancel-order",
            vec![json!({"instId": "BTC-USDT", "ordId": "1"})],
            None,
            false
        )
        .await
        .is_err()
    );
    for (key, secret, passphrase) in [(" ", "s", "p"), ("k", " ", "p"), ("k", "s", " ")] {
        assert!(
            OkxPrivateWebSocket::with_url(
                key.into(),
                secret.into(),
                passphrase.into(),
                peer.url.clone(),
                Duration::from_secs(1),
            )
            .is_err()
        );
    }
}
