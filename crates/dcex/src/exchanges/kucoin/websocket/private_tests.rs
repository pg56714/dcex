//! The signed bullet-token request, the token-scoped stream URL and the private topic
//! frames, against local peers only.

use std::time::Duration;

use serde_json::json;

use super::KucoinPrivateWebSocket;
use crate::exchanges::kucoin::KucoinMarket;
use crate::ws::test_peer::{TestPeer, http_sequence};

fn bullet(endpoint: &str) -> String {
    json!({
        "code": "200000",
        "data": {"token": "bullet-token", "instanceServers": [{"endpoint": endpoint}]},
    })
    .to_string()
}

fn client(http: &str, market: KucoinMarket) -> KucoinPrivateWebSocket {
    KucoinPrivateWebSocket::with_market_base_urls(
        "api-key".into(),
        "api-secret".into(),
        "passphrase".into(),
        Duration::from_secs(5),
        http.into(),
        http.into(),
        market,
    )
    .unwrap()
}

#[tokio::test]
async fn spot_stream_uses_a_signed_bullet_token_and_private_topics() {
    let mut peer = TestPeer::start().await;
    let (http, calls) = http_sequence(vec![bullet(&peer.url)]);
    let mut ws = client(&http, KucoinMarket::Spot);
    ws.connect().await.unwrap();
    // Connecting again keeps the open stream.
    ws.connect().await.unwrap();
    let handshake = peer.next_handshake().await;
    assert_eq!(handshake.path, "/?token=bullet-token&connectId=dcex-1");

    let calls = calls.join().unwrap();
    assert_eq!(calls.len(), 1);
    assert_eq!(calls[0].method, "POST");
    assert_eq!(calls[0].target, "/api/v1/bullet-private");
    assert_eq!(calls[0].header("KC-API-KEY"), Some("api-key"));
    assert_eq!(calls[0].header("KC-API-KEY-VERSION"), Some("2"));
    for name in ["KC-API-SIGN", "KC-API-TIMESTAMP", "KC-API-PASSPHRASE"] {
        assert!(calls[0].header(name).is_some(), "{name}");
    }

    let id = ws.subscribe_orders().await.unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({
            "id": id,
            "type": "subscribe",
            "topic": "/spotMarket/tradeOrders",
            "privateChannel": true,
            "response": true,
        })
    );
    ws.subscribe_balances().await.unwrap();
    assert_eq!(peer.next_json().await["topic"], "/account/balance");
    ws.unsubscribe("/account/balance").await.unwrap();
    assert_eq!(peer.next_json().await["type"], "unsubscribe");
    let id = ws.ping().await.unwrap();
    assert_eq!(peer.next_json().await, json!({"id": id, "type": "ping"}));
    assert!(ws.subscribe("bad topic!").await.is_err());
    assert!(peer.quiet(Duration::from_millis(200)).await);

    peer.push_json(&json!({"type": "message", "topic": "/account/balance"}));
    assert_eq!(ws.recv().await.unwrap()["topic"], "/account/balance");
    peer.push("{}");
    assert_eq!(ws.recv_bytes().await.unwrap(), b"{}");
    ws.close().await.unwrap();
    assert!(!ws.is_connected());
}

#[tokio::test]
async fn futures_stream_uses_contract_topics() {
    let mut peer = TestPeer::start().await;
    let (http, calls) = http_sequence(vec![bullet(&peer.url)]);
    let mut ws = client(&http, KucoinMarket::Futures);
    ws.connect().await.unwrap();
    ws.subscribe_orders().await.unwrap();
    ws.subscribe_balances().await.unwrap();
    assert_eq!(
        peer.next_json().await["topic"],
        "/contractMarket/tradeOrders"
    );
    assert_eq!(peer.next_json().await["topic"], "/contractAccount/wallet");
    assert_eq!(calls.join().unwrap()[0].target, "/api/v1/bullet-private");
}

#[tokio::test]
async fn missing_tokens_and_unconnected_use_are_errors() {
    let (http, calls) = http_sequence(vec![json!({"code": "200000", "data": {}}).to_string()]);
    let mut ws = client(&http, KucoinMarket::Spot);
    assert!(ws.connect().await.is_err());
    assert!(!ws.is_connected());
    assert!(ws.subscribe_orders().await.is_err());
    assert!(ws.ping().await.is_err());
    calls.join().unwrap();
}

#[test]
fn broker_market_and_blank_credentials_are_rejected() {
    let build = |key: &str, secret: &str, passphrase: &str, market| {
        KucoinPrivateWebSocket::with_market_base_urls(
            key.into(),
            secret.into(),
            passphrase.into(),
            Duration::from_secs(1),
            "http://127.0.0.1:9".into(),
            "http://127.0.0.1:9".into(),
            market,
        )
    };
    assert!(build("k", "s", "p", KucoinMarket::Broker).is_err());
    assert!(build(" ", "s", "p", KucoinMarket::Spot).is_err());
    assert!(build("k", " ", "p", KucoinMarket::Spot).is_err());
    assert!(build("k", "s", " ", KucoinMarket::Spot).is_err());
}
