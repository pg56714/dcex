//! Public and private stream frames, including the signed private subscription.

use std::time::Duration;

use base64::Engine;
use serde_json::json;

use super::{BackpackPrivateWebSocket, BackpackPublicWebSocket};
use crate::ws::test_peer::TestPeer;

fn key_pair() -> (String, String) {
    let engine = base64::engine::general_purpose::STANDARD;
    (engine.encode([b'2'; 32]), engine.encode([b'1'; 32]))
}

#[tokio::test]
async fn public_streams_use_documented_names() {
    let mut peer = TestPeer::start().await;
    let mut client =
        BackpackPublicWebSocket::with_url(peer.url.clone(), Duration::from_secs(5)).unwrap();
    client.connect().await.unwrap();
    client.subscribe_book_ticker("SOL_USDC").await.unwrap();
    client.subscribe_depth("SOL_USDC").await.unwrap();
    client
        .subscribe_depth_with_speed("SOL_USDC", "200ms")
        .await
        .unwrap();
    client.subscribe_orderbook("SOL_USDC").await.unwrap();
    client
        .subscribe_orderbook_with_speed("SOL_USDC", "1000ms")
        .await
        .unwrap();
    client.subscribe_klines("SOL_USDC", "1h").await.unwrap();
    client.subscribe_liquidation("SOL-USDC-SWAP").await.unwrap();
    client.subscribe_mark_price("SOL-USDC-SWAP").await.unwrap();
    client.subscribe_ticker("SOL_USDC").await.unwrap();
    client
        .subscribe_open_interest("SOL-USDC-SWAP")
        .await
        .unwrap();
    client.subscribe_trades("SOL_USDC").await.unwrap();
    for stream in [
        "bookTicker.SOL_USDC",
        "depth.SOL_USDC",
        "depth.200ms.SOL_USDC",
        "depth.SOL_USDC",
        "depth.1000ms.SOL_USDC",
        "kline.1h.SOL_USDC",
        "liquidation.SOL_USDC_PERP",
        "markPrice.SOL_USDC_PERP",
        "ticker.SOL_USDC",
        "openInterest.SOL_USDC_PERP",
        "trade.SOL_USDC",
    ] {
        assert_eq!(
            peer.next_json().await,
            json!({"method": "SUBSCRIBE", "params": [stream]})
        );
    }
    client
        .unsubscribe(vec!["trade.SOL_USDC".into()])
        .await
        .unwrap();
    assert_eq!(
        peer.next_json().await,
        json!({"method": "UNSUBSCRIBE", "params": ["trade.SOL_USDC"]})
    );
    assert!(
        client
            .subscribe_depth_with_speed("SOL_USDC", "5ms")
            .await
            .is_err()
    );
    assert!(client.subscribe_klines("SOL_USDC", "7m").await.is_err());
    assert!(client.subscribe(vec![]).await.is_err());
    assert!(peer.quiet(Duration::from_millis(200)).await);
    client.ping().await.unwrap();
    peer.push_json(&json!({"stream": "trade.SOL_USDC", "data": {}}));
    assert_eq!(client.recv().await.unwrap()["stream"], "trade.SOL_USDC");
    peer.push("{}");
    assert_eq!(client.recv_bytes().await.unwrap(), b"{}");
    assert!(client.is_connected());
    client.close().await.unwrap();
}

#[tokio::test]
async fn private_subscriptions_are_signed_and_unsubscribes_are_not() {
    let mut peer = TestPeer::start().await;
    let (key, secret) = key_pair();
    let mut client = BackpackPrivateWebSocket::with_url(
        key.clone(),
        secret,
        5_000,
        peer.url.clone(),
        Duration::from_secs(5),
    )
    .unwrap();
    client.connect().await.unwrap();
    client.subscribe_orders().await.unwrap();
    client
        .subscribe_orders_for_symbol("SOL_USDC")
        .await
        .unwrap();
    client.subscribe_positions().await.unwrap();
    client
        .subscribe_positions_for_symbol("SOL-USDC-SWAP")
        .await
        .unwrap();
    client.subscribe_rfq().await.unwrap();
    client.subscribe_rfq_for_symbol("SOL_USDC").await.unwrap();
    for stream in [
        "account.orderUpdate",
        "account.orderUpdate.SOL_USDC",
        "account.positionUpdate",
        "account.positionUpdate.SOL_USDC_PERP",
        "account.rfqUpdate",
        "account.rfqUpdate.SOL_USDC",
    ] {
        let frame = peer.next_json().await;
        assert_eq!(frame["method"], "SUBSCRIBE");
        assert_eq!(frame["params"], json!([stream]));
        // [verifying key, signature, timestamp, window] per the documented auth array.
        let signature = frame["signature"].as_array().expect("signature array");
        assert_eq!(signature.len(), 4);
        assert_eq!(signature[0], key);
        assert!(!signature[1].as_str().unwrap().is_empty());
        assert!(signature[2].as_str().unwrap().parse::<u64>().is_ok());
        assert_eq!(signature[3], "5000");
    }
    client
        .unsubscribe(vec!["account.orderUpdate".into()])
        .await
        .unwrap();
    let frame = peer.next_json().await;
    assert_eq!(frame["method"], "UNSUBSCRIBE");
    assert!(frame.get("signature").is_none());
    client.ping().await.unwrap();
    peer.push_json(&json!({"stream": "account.orderUpdate", "data": {}}));
    assert_eq!(
        client.recv().await.unwrap()["stream"],
        "account.orderUpdate"
    );
    peer.push("{}");
    assert_eq!(client.recv_bytes().await.unwrap(), b"{}");
    client.close().await.unwrap();
    assert!(!client.is_connected());
}
