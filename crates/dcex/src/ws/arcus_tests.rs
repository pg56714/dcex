//! Arcus subscriptions, read-only RPC and the signed trading-frame checks, against a local peer.

use std::time::Duration;

use serde_json::{Value, json};

use super::arcus::ArcusWebSocket;
use super::test_peer::TestPeer;

const T: u64 = 1_700_000_000_000;

fn signed_frame() -> Value {
    json!({
        "type": "post",
        "id": 7,
        "request": {
            "type": "placeOrder",
            "payload": {
                "address": format!("0x{}", "a".repeat(40)),
                "timestamp": T,
                "orders": [{"timestamp": T, "signature": "b".repeat(128)}],
            },
            "apiKey": "c".repeat(64),
            "timestamp": T.to_string(),
            "signature": "d".repeat(128),
        },
    })
}

async fn connected() -> (ArcusWebSocket, TestPeer) {
    let peer = TestPeer::start().await;
    let mut ws = ArcusWebSocket::with_url(peer.url.clone(), Duration::from_secs(5)).unwrap();
    ws.connect().await.unwrap();
    (ws, peer)
}

#[tokio::test]
async fn subscriptions_rpc_and_signed_frames_are_sent_unchanged() {
    let (mut ws, mut peer) = connected().await;
    assert!(ws.is_connected());
    ws.subscribe("l2Orderbook", Some("BTC-USD")).await.unwrap();
    ws.subscribe("markets", None).await.unwrap();
    ws.subscribe("oraclePrices", Some("BTC")).await.unwrap();
    ws.unsubscribe("orders", Some(&format!("0x{}", "a".repeat(40))))
        .await
        .unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"type": "subscribe", "channel": "l2Orderbook", "id": "BTC-USD"})
    );
    assert_eq!(
        peer.next_json().await,
        json!({"type": "subscribe", "channel": "markets"})
    );
    assert_eq!(peer.next_json().await["id"], "BTC");
    assert_eq!(peer.next_json().await["type"], "unsubscribe");
    ws.get_request(3, "markets", json!({})).await.unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"type": "get", "id": 3, "request": {"type": "markets", "payload": {}}})
    );
    ws.post_request(signed_frame()).await.unwrap();
    assert_eq!(peer.next_json().await, signed_frame());
    ws.ping().await.unwrap();
    peer.push("{\"channel\":\"markets\"}");
    assert_eq!(ws.recv_bytes().await.unwrap(), b"{\"channel\":\"markets\"}");
    ws.close().await.unwrap();
    assert!(!ws.is_connected());
    assert!(ArcusWebSocket::new(true, Duration::from_secs(1)).is_ok());
}

#[tokio::test]
async fn malformed_requests_never_reach_the_wire() {
    let (mut ws, mut peer) = connected().await;
    let rejects = |result: crate::Result<()>, reason: &str| {
        let error = result.unwrap_err().to_string();
        assert!(error.contains(reason), "{reason}: {error}");
    };
    rejects(
        ws.get_request(1, "withdraw", json!({})).await,
        "invalid read-only RPC",
    );
    rejects(
        ws.get_request(1, "markets", json!([])).await,
        "invalid read-only RPC",
    );
    rejects(
        ws.subscribe("markets", Some("BTC")).await,
        "markets does not use an id",
    );
    rejects(
        ws.subscribe("trades", Some("")).await,
        "trades subscription requires an id",
    );

    let incomplete = "complete signed trading RPC frame";
    let mutate = |change: &dyn Fn(&mut Value)| {
        let mut frame = signed_frame();
        change(&mut frame);
        frame
    };
    for frame in [
        json!([]),
        mutate(&|f| f["type"] = json!("get")),
        mutate(&|f| f["request"]["extra"] = json!(1)),
        mutate(&|f| f["request"]["type"] = json!("withdraw")),
        mutate(&|f| f["request"]["payload"] = json!([])),
        mutate(&|f| f["request"]["payload"]["address"] = json!("0x12")),
        mutate(&|f| f["request"]["apiKey"] = json!("c")),
        mutate(&|f| f["request"]["signature"] = json!("g".repeat(128))),
        mutate(&|f| f["request"]["timestamp"] = json!("now")),
        mutate(&|f| f["request"]["payload"]["orders"] = json!([])),
        mutate(&|f| f["request"]["payload"]["orders"][0]["timestamp"] = json!(T + 1)),
        mutate(&|f| f["request"]["payload"]["orders"][0]["signature"] = json!("b")),
    ] {
        rejects(ws.post_request(frame).await, incomplete);
    }
    rejects(
        ws.post_request(mutate(&|f| {
            f["request"]["payload"]["timestamp"] = json!(T + 1)
        }))
        .await,
        "payload timestamp differs",
    );
    rejects(
        ws.post_request(mutate(&|f| {
            f["request"]["payload"]["clientTime"] = json!("1")
        }))
        .await,
        "clientTime differs",
    );
    // Orders may carry their signing time as a clientTime string instead.
    ws.post_request(mutate(&|f| {
        f["request"]["payload"]["orders"][0] =
            json!({"clientTime": T.to_string(), "signature": "b".repeat(128)});
    }))
    .await
    .unwrap();
    peer.next_json().await;
    assert!(peer.quiet(Duration::from_millis(200)).await);
}
