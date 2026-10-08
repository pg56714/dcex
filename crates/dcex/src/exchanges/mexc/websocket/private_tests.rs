//! The listen-key lifecycle and the subscription frames, against local peers only.

use std::time::Duration;

use serde_json::json;

use super::MexcPrivateWebSocket;
use crate::ws::test_peer::{TestPeer, http_sequence};

fn client(http: &str, ws: &str) -> MexcPrivateWebSocket {
    MexcPrivateWebSocket::with_urls(
        "api-key".into(),
        "api-secret".into(),
        Duration::from_secs(5),
        http,
        ws,
    )
    .unwrap()
}

fn signed_query(target: &str, listen_key: Option<&str>) {
    let query = target.split_once('?').expect("query").1;
    let keys: Vec<&str> = query
        .split('&')
        .map(|pair| pair.split_once('=').expect("pair").0)
        .collect();
    match listen_key {
        Some(key) => {
            assert_eq!(keys, ["listenKey", "timestamp", "signature"]);
            assert!(query.starts_with(&format!("listenKey={key}&")));
        }
        None => assert_eq!(keys, ["timestamp", "signature"]),
    }
}

#[tokio::test]
async fn listen_key_lifecycle_is_signed_and_scopes_the_stream() {
    let mut peer = TestPeer::start().await;
    let (http, calls) = http_sequence(vec![
        json!({"listenKey": "lk-1"}).to_string(),
        json!({"listenKey": "lk-1"}).to_string(),
        "{}".into(),
    ]);
    let mut ws = client(&http, &format!("{}/ws", peer.url));
    assert_eq!(ws.connect().await.unwrap(), "lk-1");
    assert_eq!(ws.listen_key(), Some("lk-1"));
    assert_eq!(peer.next_handshake().await.path, "/ws?listenKey=lk-1");
    assert_eq!(ws.keep_alive().await.unwrap(), "lk-1");
    ws.close().await.unwrap();
    assert!(!ws.is_connected());
    assert_eq!(ws.listen_key(), None);

    let calls = calls.join().unwrap();
    let methods: Vec<&str> = calls.iter().map(|call| call.method.as_str()).collect();
    assert_eq!(methods, ["POST", "PUT", "DELETE"]);
    for call in &calls {
        assert!(call.target.starts_with("/api/v3/userDataStream?"));
        assert_eq!(call.header("X-MEXC-APIKEY"), Some("api-key"));
    }
    signed_query(&calls[0].target, None);
    signed_query(&calls[1].target, Some("lk-1"));
    signed_query(&calls[2].target, Some("lk-1"));
}

#[tokio::test]
async fn subscriptions_use_documented_protobuf_channels() {
    let mut peer = TestPeer::start().await;
    let (http, calls) = http_sequence(vec![json!({"listenKey": "lk-2"}).to_string()]);
    let mut ws = client(&http, &format!("{}/ws", peer.url));
    ws.connect().await.unwrap();
    ws.subscribe_account().await.unwrap();
    ws.subscribe_deals().await.unwrap();
    ws.subscribe_orders().await.unwrap();
    for channel in [
        "spot@private.account.v3.api.pb",
        "spot@private.deals.v3.api.pb",
        "spot@private.orders.v3.api.pb",
    ] {
        assert_eq!(
            peer.next_json().await,
            json!({"method": "SUBSCRIPTION", "params": [channel]})
        );
    }
    ws.unsubscribe(vec!["spot@private.deals.v3.api.pb".into()])
        .await
        .unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"method": "UNSUBSCRIPTION", "params": ["spot@private.deals.v3.api.pb"]})
    );
    ws.ping().await.unwrap();
    assert_eq!(peer.next_json().await, json!({"method": "PING"}));
    assert!(ws.subscribe(vec![]).await.is_err());
    assert!(ws.subscribe(vec!["bad channel".into()]).await.is_err());
    assert!(peer.quiet(Duration::from_millis(200)).await);
    peer.push("{\"code\":0}");
    assert_eq!(ws.recv().await.unwrap(), b"{\"code\":0}");
    assert_eq!(calls.join().unwrap().len(), 1);
}

#[tokio::test]
async fn missing_listen_keys_are_errors() {
    let (http, calls) = http_sequence(vec!["{}".into()]);
    let mut ws = client(&http, "ws://127.0.0.1:9");
    assert!(ws.keep_alive().await.is_err());
    // Closing without a listen key sends nothing.
    ws.close_listen_key().await.unwrap();
    assert!(ws.create_listen_key().await.is_err());
    assert_eq!(calls.join().unwrap().len(), 1);
    assert!(MexcPrivateWebSocket::new(" ".into(), "s".into(), Duration::from_secs(1)).is_err());
    assert!(MexcPrivateWebSocket::new("k".into(), " ".into(), Duration::from_secs(1)).is_err());
}
