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

#[tokio::test]
async fn trade_headers_use_the_server_clock_once_synced() {
    use crate::ws::test_peer::http_sequence;

    let mut peer = TestPeer::start().await;
    let (http, calls) = http_sequence(vec![
        json!({"retCode": 0, "result": {"timeSecond": "0", "timeNano": ((now_ms() - 5_000) * 1_000_000).to_string()}})
            .to_string(),
    ]);
    let mut client = BybitPrivateWebSocket::with_url(
        "api-key".into(),
        "api-secret".into(),
        format!("{}/v5/trade", peer.url),
        Duration::from_secs(5),
    )
    .expect("client")
    .with_server_time_url(Some(format!("{http}/v5/market/time")));
    peer.push_json(&json!({"op": "auth", "retCode": 0, "retMsg": "OK"}));
    client.connect().await.expect("connect");
    peer.next_json().await;
    for _ in 0..2 {
        client
            .send_trade_order(
                "order.cancel",
                json!({"category": "linear", "symbol": "BTCUSDT", "orderId": "1"}),
            )
            .await
            .unwrap();
        let header: u64 = peer.next_json().await["header"]["X-BAPI-TIMESTAMP"]
            .as_str()
            .unwrap()
            .parse()
            .unwrap();
        assert!(header.abs_diff(now_ms() - 5_000) < 1_000, "offset applied");
    }
    let calls = calls.join().unwrap();
    assert_eq!(calls.len(), 1);
    assert_eq!(calls[0].target, "/v5/market/time");
}

#[test]
fn only_the_official_trade_url_syncs_the_server_clock() {
    let build = |url: &str| {
        BybitPrivateWebSocket::with_url(
            "k".into(),
            "s".into(),
            url.to_string(),
            Duration::from_secs(1),
        )
        .unwrap()
    };
    let official =
        BybitPrivateWebSocket::new_trade("k".into(), "s".into(), Duration::from_secs(1)).unwrap();
    assert_eq!(
        official.clock.url(),
        Some("https://api.bybit.com/v5/market/time")
    );
    assert_eq!(
        build("wss://stream.bybit.com/v5/trade/").clock.url(),
        Some("https://api.bybit.com/v5/market/time")
    );
    assert_eq!(build("wss://stream.bybit.com/v5/private").clock.url(), None);
    assert_eq!(
        build("wss://stream-testnet.bybit.com/v5/trade").clock.url(),
        None
    );
}

#[tokio::test]
async fn private_stream_rejects_malformed_topics_and_trade_args() {
    let (mut client, mut peer) =
        authenticated("/v5/private", json!({"op": "auth", "success": true})).await;
    for (result, reason) in [
        (
            client.subscribe(vec![]).await,
            "at least one Bybit private WebSocket topic",
        ),
        (
            client.subscribe(vec![" ".into()]).await,
            "topic must not be empty",
        ),
    ] {
        let error = result.unwrap_err().to_string();
        assert!(error.contains(reason), "{reason}: {error}");
    }
    peer.push("{\"op\":\"pong\"}");
    assert_eq!(client.recv_bytes().await.unwrap(), b"{\"op\":\"pong\"}");
    assert!(peer.quiet(Duration::from_millis(200)).await);

    let (mut trade, _peer) = authenticated(
        "/v5/trade",
        json!({"op": "auth", "retCode": 0, "retMsg": "OK"}),
    )
    .await;
    let error = trade
        .unsubscribe(vec!["order".into()])
        .await
        .unwrap_err()
        .to_string();
    assert!(
        error.contains("does not support topic subscriptions"),
        "{error}"
    );
    let error = trade
        .send_trade_order("order.create", json!([1]))
        .await
        .unwrap_err()
        .to_string();
    assert!(error.contains("args must be a JSON object"), "{error}");
    assert!(BybitPrivateWebSocket::new("k".into(), "s".into(), Duration::from_secs(1)).is_ok());
}
