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
