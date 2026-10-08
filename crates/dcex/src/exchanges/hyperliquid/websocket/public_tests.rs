//! Frames the public client sends, checked against the documented subscription shapes.

use std::time::Duration;

use serde_json::json;

use super::HyperliquidPublicWebSocket;
use crate::ws::test_peer::TestPeer;

async fn connected() -> (HyperliquidPublicWebSocket, TestPeer) {
    let peer = TestPeer::start().await;
    let mut client =
        HyperliquidPublicWebSocket::with_url(peer.url.clone(), Duration::from_secs(5)).unwrap();
    client.connect().await.unwrap();
    (client, peer)
}

#[tokio::test]
async fn market_channels_name_the_coin() {
    let (mut client, mut peer) = connected().await;
    client.subscribe_all_mids().await.unwrap();
    client.subscribe_all_mids_for_dex("xyz").await.unwrap();
    client.subscribe_trades("BTC-USDC-SWAP").await.unwrap();
    client.subscribe_orderbook("ETH").await.unwrap();
    client.subscribe_l2_book("ETH").await.unwrap();
    client
        .subscribe_l2_book_with_n_sig_figs("ETH", 3)
        .await
        .unwrap();
    client
        .subscribe_l2_book_with_mantissa("ETH", 2)
        .await
        .unwrap();
    client
        .subscribe_l2_book_with_precision("ETH", 5, 5)
        .await
        .unwrap();
    client.subscribe_bbo("xyz:TSLA-USD-SWAP").await.unwrap();
    client.subscribe_klines("BTC", "15m").await.unwrap();
    client.subscribe_active_asset_ctx("@107").await.unwrap();
    for subscription in [
        json!({"type": "allMids"}),
        json!({"type": "allMids", "dex": "xyz"}),
        json!({"type": "trades", "coin": "BTC"}),
        json!({"type": "l2Book", "coin": "ETH"}),
        json!({"type": "l2Book", "coin": "ETH"}),
        json!({"type": "l2Book", "coin": "ETH", "nSigFigs": 3}),
        json!({"type": "l2Book", "coin": "ETH", "nSigFigs": 5, "mantissa": 2}),
        json!({"type": "l2Book", "coin": "ETH", "nSigFigs": 5, "mantissa": 5}),
        json!({"type": "bbo", "coin": "xyz:TSLA"}),
        json!({"type": "candle", "coin": "BTC", "interval": "15m"}),
        json!({"type": "activeAssetCtx", "coin": "@107"}),
    ] {
        assert_eq!(
            peer.next_json().await,
            json!({"method": "subscribe", "subscription": subscription})
        );
    }
    client
        .unsubscribe(json!({"type": "trades", "coin": "BTC"}))
        .await
        .unwrap();
    assert_eq!(peer.next_json().await["method"], "unsubscribe");
    client.post_info(4, json!({"type": "meta"})).await.unwrap();
    let frame = peer.next_json().await;
    assert_eq!(
        (frame["method"].as_str(), frame["id"].as_u64()),
        (Some("post"), Some(4))
    );
    assert_eq!(
        frame["request"],
        json!({"type": "info", "payload": {"type": "meta"}})
    );
}

#[tokio::test]
async fn invalid_subscriptions_are_rejected_before_sending() {
    let (mut client, mut peer) = connected().await;
    assert!(client.subscribe_klines("BTC", "2m").await.is_err());
    assert!(
        client
            .subscribe_l2_book_with_n_sig_figs("ETH", 1)
            .await
            .is_err()
    );
    assert!(
        client
            .subscribe_l2_book_with_precision("ETH", 4, 2)
            .await
            .is_err()
    );
    assert!(client.subscribe_trades("HYPE-USDC-SPOT").await.is_err());
    assert!(client.subscribe(json!({})).await.is_err());
    assert!(client.post_info(1, json!({})).await.is_err());
    assert!(peer.quiet(Duration::from_millis(200)).await);
}

#[tokio::test]
async fn pushed_messages_are_received_and_close_disconnects() {
    let (mut client, peer) = connected().await;
    assert!(client.is_connected());
    peer.push_json(&json!({"channel": "trades", "data": []}));
    assert_eq!(client.recv().await.unwrap()["channel"], "trades");
    peer.push("{}");
    assert_eq!(client.recv_bytes().await.unwrap(), b"{}");
    client.close().await.unwrap();
    assert!(!client.is_connected());
}
