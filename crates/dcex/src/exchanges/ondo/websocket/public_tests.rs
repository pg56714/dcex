//! Market names without a product table follow the REST rules: `BASE-QUOTE-SWAP` becomes
//! the native `BASE-QUOTE.P`, spot drops `-SPOT`, and malformed names never reach the wire.

use std::time::Duration;

use serde_json::json;

use super::OndoPublicWebSocket;
use crate::ws::test_peer::TestPeer;

#[tokio::test]
async fn unified_symbols_map_to_native_markets() {
    let mut peer = TestPeer::start().await;
    let mut ws = OndoPublicWebSocket::with_url(peer.url.clone(), Duration::from_secs(5)).unwrap();
    ws.connect().await.unwrap();
    ws.subscribe_top_of_book(vec!["BTC-USD-SWAP".into(), "ETH-USD.P".into()])
        .await
        .unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"op": "subscribe", "channel": "topOfBooksPerps", "markets": ["BTC-USD.P", "ETH-USD.P"]})
    );
    ws.subscribe_funding_rates(vec!["BTC-USD-SWAP".into()])
        .await
        .unwrap();
    assert_eq!(peer.next_json().await["markets"], json!(["BTC-USD.P"]));
    ws.subscribe_spot_trades(vec!["SPY-USDC-SPOT".into()])
        .await
        .unwrap();
    assert_eq!(peer.next_json().await["markets"], json!(["SPY-USDC"]));
    for bad in ["BTC-USD", "SPY-USDC-SPOT"] {
        assert!(
            ws.subscribe_trades(vec![bad.into()]).await.is_err(),
            "{bad}"
        );
    }
    assert!(peer.quiet(Duration::from_millis(200)).await);
}

#[tokio::test]
async fn private_perps_channels_map_markets_like_rest() {
    use super::OndoPrivateWebSocket;

    let mut peer = TestPeer::start().await;
    // Queued before the handshake: delivered right after the login frame.
    peer.push(r#"{"type":"loggedIn"}"#);
    let mut ws = OndoPrivateWebSocket::with_url(
        Some("key".into()),
        Some("ondoApiSecret_SECRET".into()),
        peer.url.clone(),
        Duration::from_secs(5),
    )
    .unwrap();
    ws.connect().await.unwrap();
    assert_eq!(peer.next_json().await["op"], "login");
    ws.subscribe_orders(vec!["BTC-USD-SWAP".into(), "ETH-USD.P".into()])
        .await
        .unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"op": "subscribe", "channel": "ordersPerps", "markets": ["BTC-USD.P", "ETH-USD.P"]})
    );
    ws.subscribe("deposits", vec![]).await.unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"op": "subscribe", "channel": "deposits"})
    );
    assert!(ws.subscribe_fills(vec!["BTC-USD".into()]).await.is_err());
    assert!(peer.quiet(Duration::from_millis(200)).await);
}

fn private_client(url: &str) -> super::OndoPrivateWebSocket {
    super::OndoPrivateWebSocket::with_url(
        Some("key".into()),
        Some("ondoApiSecret_SECRET".into()),
        url.to_string(),
        Duration::from_secs(5),
    )
    .unwrap()
}

#[tokio::test]
async fn login_retries_once_with_the_server_clock() {
    let mut peer = TestPeer::start().await;
    let mut ws = private_client(&peer.url);
    let server_ms = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_millis() as i64
        - 60_000;
    let driver = async {
        assert_eq!(peer.next_json().await["op"], "login");
        peer.push_json(&json!({
            "type": "error",
            "msg": format!("timestamp too far from current time unixMilli {server_ms}"),
        }));
        // The client reconnects and signs again with the corrected clock.
        peer.next_handshake().await;
        peer.next_handshake().await;
        let retry = peer.next_json().await;
        peer.push(r#"{"type":"loggedIn"}"#);
        retry
    };
    let (connected, retry) = tokio::join!(ws.connect(), driver);
    connected.unwrap();
    let time: i64 = retry["args"]["time"].as_str().unwrap().parse().unwrap();
    assert!(
        (time - (server_ms - 1_000)).abs() < 5_000,
        "time {time} vs server {server_ms}"
    );
    // An authenticated, open connection does not log in again.
    ws.connect().await.unwrap();
    assert!(peer.quiet(Duration::from_millis(200)).await);
}

#[tokio::test]
async fn rejected_logins_close_the_connection() {
    let mut peer = TestPeer::start().await;
    let mut ws = private_client(&peer.url);
    peer.push(r#"{"type":"error","msg":"invalid signature"}"#);
    let error = ws.connect().await.unwrap_err().to_string();
    assert!(error.contains("login failed"), "{error}");
    assert!(!ws.is_connected());
    assert_eq!(peer.next_json().await["op"], "login");

    // A second clock error after the retry is not retried again.
    let mut ws = private_client(&peer.url);
    let server_ms = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap()
        .as_millis()
        - 60_000;
    let too_far = json!({
        "type": "error",
        "msg": format!("timestamp too far from current time unixMilli {server_ms}"),
    });
    let driver = async {
        peer.next_json().await;
        peer.push_json(&too_far);
        peer.next_handshake().await;
        peer.next_handshake().await;
        peer.next_json().await;
        peer.push_json(&too_far);
    };
    let (connected, ()) = tokio::join!(ws.connect(), driver);
    assert!(connected.unwrap_err().to_string().contains("login failed"));
}

#[tokio::test]
async fn private_channels_and_reads() {
    let mut peer = TestPeer::start().await;
    peer.push(r#"{"type":"loggedIn"}"#);
    let mut ws = private_client(&peer.url);
    ws.connect().await.unwrap();
    peer.next_json().await;
    ws.subscribe_positions().await.unwrap();
    ws.subscribe_balance().await.unwrap();
    for channel in ["positionsPerps", "balancePerps"] {
        assert_eq!(
            peer.next_json().await,
            json!({"op": "subscribe", "channel": channel})
        );
    }
    assert!(ws.subscribe("bogusPerps", vec![]).await.is_err());
    assert!(ws.subscribe("ordersSummariesPerps", vec![]).await.is_err());
    assert!(peer.quiet(Duration::from_millis(200)).await);
    peer.push(r#"{"channel":"positionsPerps","data":[]}"#);
    assert_eq!(ws.recv().await.unwrap()["channel"], "positionsPerps");
    ws.close().await.unwrap();
    assert!(ws.subscribe_positions().await.is_err());
    let build = |key: Option<&str>, secret: Option<&str>| {
        super::OndoPrivateWebSocket::with_url(
            key.map(Into::into),
            secret.map(Into::into),
            peer.url.clone(),
            Duration::from_secs(1),
        )
    };
    assert!(build(None, None).is_err());
    assert!(build(Some("key"), None).is_err());
    assert!(build(Some(" "), Some("secret")).is_err());
}

#[tokio::test]
async fn public_helpers_and_unscoped_channels() {
    let mut peer = TestPeer::start().await;
    let mut ws = OndoPublicWebSocket::with_url(peer.url.clone(), Duration::from_secs(5)).unwrap();
    ws.connect().await.unwrap();
    ws.subscribe_spot_top_of_book(vec!["SPY-USDC-SPOT".into()])
        .await
        .unwrap();
    ws.subscribe_mark_prices(vec!["BTC-USD-SWAP".into()])
        .await
        .unwrap();
    ws.subscribe("fundingRatesPerps", vec![]).await.unwrap();
    ws.subscribe_klines("BTC-USD-SWAP".into(), "1H")
        .await
        .unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"op": "subscribe", "channel": "topOfBooksSpot", "markets": ["SPY-USDC"]})
    );
    assert_eq!(peer.next_json().await["markets"], json!(["BTC-USD.P"]));
    assert_eq!(
        peer.next_json().await,
        json!({"op": "subscribe", "channel": "fundingRatesPerps"})
    );
    assert_eq!(
        peer.next_json().await,
        json!({"op": "subscribe", "channel": "kLinePerps", "markets": ["BTC-USD.P"], "resolution": "1H"})
    );
    assert!(
        ws.subscribe_klines("BTC-USD-SWAP".into(), "2H")
            .await
            .is_err()
    );
    assert!(ws.subscribe("ordersPerps", vec![]).await.is_err());
    assert!(peer.quiet(Duration::from_millis(200)).await);
    peer.push(r#"{"channel":"markPricesPerps"}"#);
    assert_eq!(ws.recv().await.unwrap()["channel"], "markPricesPerps");
}
