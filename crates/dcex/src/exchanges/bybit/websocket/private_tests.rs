//! Private and trade stream frames: auth handshake, topic subscriptions and order ops.

use std::time::{Duration, SystemTime, UNIX_EPOCH};

use serde_json::json;

use super::BybitPrivateWebSocket;
use crate::ws::test_peer::TestPeer;

fn now_ms() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("clock")
        .as_millis() as u64
}

async fn authenticated(path: &str, ack: serde_json::Value) -> (BybitPrivateWebSocket, TestPeer) {
    let mut peer = TestPeer::start().await;
    let mut client = BybitPrivateWebSocket::with_url(
        "api-key".into(),
        "api-secret".into(),
        format!("{}{path}", peer.url),
        Duration::from_secs(5),
    )
    .expect("client");
    // Queued before the handshake: delivered right after the client's auth frame.
    peer.push_json(&ack);
    client.connect().await.expect("connect and auth");
    let auth = peer.next_json().await;
    assert_eq!(auth["op"], "auth");
    let args = auth["args"].as_array().expect("auth args");
    assert_eq!(args[0], "api-key");
    assert!(args[1].as_u64().expect("expires") > now_ms());
    let signature = args[2].as_str().expect("signature");
    assert_eq!(signature.len(), 64);
    assert!(signature.bytes().all(|c| c.is_ascii_hexdigit()));
    (client, peer)
}

#[tokio::test]
async fn private_stream_authenticates_then_subscribes_topics() {
    let (mut client, mut peer) =
        authenticated("/v5/private", json!({"op": "auth", "success": true})).await;
    assert!(client.is_connected() && client.is_authenticated());
    client.subscribe_orders().await.unwrap();
    client.subscribe_executions().await.unwrap();
    client.subscribe_positions().await.unwrap();
    client.subscribe_wallet().await.unwrap();
    for topic in ["order", "execution", "position", "wallet"] {
        let frame = peer.next_json().await;
        assert_eq!(frame["op"], "subscribe");
        assert_eq!(frame["args"], json!([topic]));
        assert!(frame["req_id"].is_string());
    }
    let id = client.unsubscribe(vec!["order".into()]).await.unwrap();
    let frame = peer.next_json().await;
    assert_eq!(
        (frame["op"].as_str(), frame["req_id"].as_str()),
        (Some("unsubscribe"), Some(id.as_str()))
    );
    client.ping().await.unwrap();
    assert_eq!(peer.next_json().await["op"], "ping");
    // Orders go through the trade stream only.
    assert!(
        client
            .send_trade_order("order.create", json!({"category": "linear"}))
            .await
            .is_err()
    );
    peer.push_json(&json!({"topic": "order", "data": []}));
    assert_eq!(client.recv().await.unwrap()["topic"], "order");
    client.close().await.unwrap();
    assert!(!client.is_authenticated());
}

#[tokio::test]
async fn trade_stream_uses_req_id_casing_and_order_headers() {
    let (mut client, mut peer) = authenticated(
        "/v5/trade",
        json!({"op": "auth", "retCode": 0, "retMsg": "OK"}),
    )
    .await;
    assert!(client.subscribe_orders().await.is_err());
    let order = json!({
        "category": "linear",
        "symbol": "BTCUSDT",
        "side": "Buy",
        "orderType": "Limit",
        "qty": "0.001",
        "price": "10000",
    });
    let id = client
        .send_trade_order("order.create", order.clone())
        .await
        .unwrap();
    let frame = peer.next_json().await;
    assert_eq!(frame["reqId"], id);
    assert_eq!(frame["op"], "order.create");
    assert_eq!(frame["args"], json!([order]));
    let timestamp: u64 = frame["header"]["X-BAPI-TIMESTAMP"]
        .as_str()
        .expect("timestamp header")
        .parse()
        .expect("numeric timestamp");
    assert!(timestamp.abs_diff(now_ms()) < 60_000);
    assert!(
        client
            .send_trade_order("order.transfer", json!({}))
            .await
            .is_err()
    );
    assert!(peer.quiet(Duration::from_millis(200)).await);
}

#[tokio::test]
async fn rejected_auth_fails_the_connection() {
    let peer = TestPeer::start().await;
    let mut client = BybitPrivateWebSocket::with_url(
        "api-key".into(),
        "api-secret".into(),
        format!("{}/v5/private", peer.url),
        Duration::from_secs(5),
    )
    .expect("client");
    peer.push_json(&json!({"op": "auth", "success": false, "ret_msg": "invalid key"}));
    let error = client.connect().await.unwrap_err();
    assert!(error.to_string().contains("auth rejected"));
    assert!(!client.is_authenticated());
    assert!(
        BybitPrivateWebSocket::with_url(
            String::new(),
            "s".into(),
            peer.url.clone(),
            Duration::from_secs(1)
        )
        .is_err()
    );
}
