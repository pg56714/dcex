//! Frames the public client sends: documented channel names and local validation.

use std::time::Duration;

use serde_json::json;

use super::LighterPublicWebSocket;
use crate::ws::test_peer::TestPeer;

async fn connected() -> (LighterPublicWebSocket, TestPeer) {
    let peer = TestPeer::start().await;
    let mut client =
        LighterPublicWebSocket::with_url(peer.url.clone(), Duration::from_secs(5)).unwrap();
    client.connect().await.unwrap();
    (client, peer)
}

#[tokio::test]
async fn market_channels_use_numeric_market_ids() {
    let (mut client, mut peer) = connected().await;
    client.subscribe_orderbook(1).await.unwrap();
    client.subscribe_ticker("2").await.unwrap();
    client.subscribe_market_stats(3).await.unwrap();
    client.subscribe_all_market_stats().await.unwrap();
    client.subscribe_trades(4).await.unwrap();
    client.subscribe_klines(5, "1h").await.unwrap();
    client.subscribe_mark_price_klines(6, "1d").await.unwrap();
    client.subscribe_spot_market_stats(2048).await.unwrap();
    client.subscribe_all_spot_market_stats().await.unwrap();
    client.subscribe_height().await.unwrap();
    for channel in [
        "order_book/1",
        "ticker/2",
        "market_stats/3",
        "market_stats/all",
        "trade/4",
        "candle/5/1h",
        "mark_price_candle/6/1d",
        "spot_market_stats/2048",
        "spot_market_stats/all",
        "height",
    ] {
        assert_eq!(
            peer.next_json().await,
            json!({"type": "subscribe", "channel": channel})
        );
    }
    client.unsubscribe("height").await.unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"type": "unsubscribe", "channel": "height"})
    );
}

#[tokio::test]
async fn invalid_markets_and_resolutions_are_rejected_before_sending() {
    let (mut client, mut peer) = connected().await;
    // Without a product table only numeric ids resolve.
    assert!(client.subscribe_orderbook("ETH-USDC-SWAP").await.is_err());
    // 255 is the nil sentinel and 32768 exceeds MaxMarketIndex.
    assert!(client.subscribe_trades(255).await.is_err());
    assert!(client.subscribe_trades(32_768).await.is_err());
    assert!(client.subscribe_klines(1, "3m").await.is_err());
    assert!(client.subscribe_mark_price_klines(1, "1w").await.is_err());
    assert!(client.subscribe("order_book").await.is_err());
    assert!(client.subscribe(" ").await.is_err());
    assert!(peer.quiet(Duration::from_millis(200)).await);
}

#[tokio::test]
async fn pings_and_pushed_messages_flow_until_close() {
    let (mut client, peer) = connected().await;
    client.ping().await.unwrap();
    peer.push_json(&json!({"type": "update/order_book", "channel": "order_book:1"}));
    assert_eq!(client.recv().await.unwrap()["type"], "update/order_book");
    peer.push("{}");
    assert_eq!(client.recv_bytes().await.unwrap(), b"{}");
    assert!(client.is_connected());
    client.close().await.unwrap();
    assert!(!client.is_connected());
}
