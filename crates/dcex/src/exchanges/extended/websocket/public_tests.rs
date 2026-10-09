//! Each public stream is its own URL path; the client reconnects only when the path changes.

use std::time::Duration;

use super::{ExtendedPublicWebSocket, USER_AGENT};
use crate::ws::test_peer::TestPeer;

const PREFIX: &str = "/stream.extended.exchange/v1";

#[tokio::test]
async fn streams_open_their_documented_paths() {
    let mut peer = TestPeer::start().await;
    let mut ws =
        ExtendedPublicWebSocket::with_url(format!("{}/", peer.url), Duration::from_secs(5))
            .unwrap();
    ws.subscribe_orderbook(Some("BTC-USD"), Some(1))
        .await
        .unwrap();
    let handshake = peer.next_handshake().await;
    assert_eq!(
        handshake.path,
        format!("{PREFIX}/orderbooks/BTC-USD?depth=1")
    );
    assert_eq!(handshake.header("User-Agent"), Some(USER_AGENT));
    // The same stream keeps its connection.
    ws.subscribe_orderbook(Some("BTC-USD"), Some(1))
        .await
        .unwrap();
    ws.subscribe_orderbook(None, None).await.unwrap();
    ws.subscribe_trades(Some("ETH-USD")).await.unwrap();
    ws.subscribe_rfq_orderbook(Some("BTC-USD"), Some(1))
        .await
        .unwrap();
    ws.subscribe_rfq_orderbook(None, None).await.unwrap();
    ws.subscribe_funding(None).await.unwrap();
    ws.subscribe_candles("BTC-USD", "mark-prices", "PT1H")
        .await
        .unwrap();
    ws.subscribe_mark_price(Some("BTC-USD")).await.unwrap();
    ws.subscribe_index_price(None).await.unwrap();
    ws.subscribe_trades(Some("BTC-USD-SPOT")).await.unwrap();
    for path in [
        "orderbooks",
        "publicTrades/ETH-USD",
        "orderbooks/rfq/BTC-USD?depth=1",
        "orderbooks/rfq",
        "funding",
        "candles/BTC-USD/mark-prices?interval=PT1H",
        "prices/mark/BTC-USD",
        "prices/index",
        "publicTrades/BTCSPOT-USD",
    ] {
        assert_eq!(peer.next_handshake().await.path, format!("{PREFIX}/{path}"));
    }
    ws.ping().await.unwrap();
    peer.push("{\"type\":\"TRADE\"}");
    assert_eq!(ws.recv_bytes().await.unwrap(), b"{\"type\":\"TRADE\"}");
    assert!(ws.is_connected());
    ws.close().await.unwrap();
    assert!(!ws.is_connected());
}

#[tokio::test]
async fn invalid_streams_are_rejected_before_connecting() {
    let mut peer = TestPeer::start().await;
    let mut ws =
        ExtendedPublicWebSocket::with_url(peer.url.clone(), Duration::from_secs(5)).unwrap();
    assert!(
        ws.subscribe_orderbook(Some("BTC-USD"), Some(5))
            .await
            .is_err()
    );
    assert!(ws.subscribe_rfq_orderbook(None, Some(2)).await.is_err());
    assert!(
        ws.subscribe_candles("BTC-USD", "volume", "PT1H")
            .await
            .is_err()
    );
    assert!(
        ws.subscribe_candles("BTC-USD", "trades", "PT3H")
            .await
            .is_err()
    );
    assert!(ws.subscribe_trades(Some("BTC/USD")).await.is_err());
    assert!(ws.subscribe_trades(Some("BTC-USD-SWAP")).await.is_err());
    assert!(ws.ping().await.is_err());
    assert!(ws.recv_bytes().await.is_err());
    assert!(
        tokio::time::timeout(Duration::from_millis(200), peer.next_handshake())
            .await
            .is_err()
    );
    assert!(
        ExtendedPublicWebSocket::with_url("https://127.0.0.1:9", Duration::from_secs(1)).is_err()
    );
    assert!(ExtendedPublicWebSocket::new(Duration::from_secs(1)).is_ok());
}
