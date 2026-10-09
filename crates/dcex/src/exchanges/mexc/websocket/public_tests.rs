//! Spot protobuf channel names, speeds, levels and intervals, and the 30-stream limit.

use std::time::Duration;

use serde_json::json;

use super::MexcPublicWebSocket;
use crate::ws::test_peer::TestPeer;

async fn connected() -> (MexcPublicWebSocket, TestPeer) {
    let peer = TestPeer::start().await;
    let mut ws = MexcPublicWebSocket::with_url(peer.url.clone(), Duration::from_secs(5)).unwrap();
    ws.connect().await.unwrap();
    (ws, peer)
}

#[tokio::test]
async fn channels_use_documented_names() {
    let (mut ws, mut peer) = connected().await;
    ws.subscribe_trades("BTC-USDT-SPOT", "100ms").await.unwrap();
    ws.subscribe_orderbook("btcusdt", "10ms").await.unwrap();
    ws.subscribe_partial_orderbook("BTCUSDT", 5).await.unwrap();
    ws.subscribe_book_ticker("BTCUSDT", "100ms").await.unwrap();
    ws.subscribe_klines("BTCUSDT", "4h").await.unwrap();
    ws.subscribe_klines("BTCUSDT", "Month1").await.unwrap();
    for channel in [
        "spot@public.aggre.deals.v3.api.pb@100ms@BTCUSDT",
        "spot@public.aggre.depth.v3.api.pb@10ms@BTCUSDT",
        "spot@public.limit.depth.v3.api.pb@BTCUSDT@5",
        "spot@public.aggre.bookTicker.v3.api.pb@100ms@BTCUSDT",
        "spot@public.kline.v3.api.pb@BTCUSDT@Hour4",
        "spot@public.kline.v3.api.pb@BTCUSDT@Month1",
    ] {
        assert_eq!(
            peer.next_json().await,
            json!({"method": "SUBSCRIPTION", "params": [channel]})
        );
    }
    ws.unsubscribe(vec!["spot@public.kline.v3.api.pb@BTCUSDT@Month1".into()])
        .await
        .unwrap();
    assert_eq!(peer.next_json().await["method"], "UNSUBSCRIPTION");
    ws.ping().await.unwrap();
    assert_eq!(peer.next_json().await, json!({"method": "PING"}));
    peer.push("{\"code\":0}");
    assert_eq!(ws.recv().await.unwrap(), b"{\"code\":0}");
    ws.close().await.unwrap();
    assert!(!ws.is_connected());
}

#[tokio::test]
async fn invalid_input_and_the_stream_limit_are_enforced_locally() {
    let (mut ws, mut peer) = connected().await;
    assert!(ws.subscribe_trades("BTCUSDT", "1s").await.is_err());
    assert!(ws.subscribe_partial_orderbook("BTCUSDT", 50).await.is_err());
    assert!(ws.subscribe_klines("BTCUSDT", "2m").await.is_err());
    assert!(ws.subscribe_klines("BTCUSDT", " ").await.is_err());
    assert!(ws.subscribe_klines("BTCUSDT", "1 m").await.is_err());
    assert!(ws.subscribe_trades("BTC-USDT-SWAP", "100ms").await.is_err());
    assert!(ws.subscribe_trades("BTC/USDT", "100ms").await.is_err());
    assert!(ws.subscribe_trades(" ", "100ms").await.is_err());
    assert!(ws.subscribe(vec![]).await.is_err());
    assert!(ws.subscribe(vec!["bad channel".into()]).await.is_err());
    assert!(ws.subscribe(vec![" ".into()]).await.is_err());
    assert!(peer.quiet(Duration::from_millis(200)).await);

    // 30 streams per connection; unsubscribing frees a slot and reconnecting resets the count.
    let channels: Vec<String> = (0..30)
        .map(|index| format!("spot@public.kline.v3.api.pb@SYM{index}USDT@Min1"))
        .collect();
    ws.subscribe(channels.clone()).await.unwrap();
    peer.next_json().await;
    assert!(ws.subscribe(vec!["spot@extra".into()]).await.is_err());
    ws.unsubscribe(vec![channels[0].clone()]).await.unwrap();
    peer.next_json().await;
    ws.subscribe(vec!["spot@extra".into()]).await.unwrap();
    peer.next_json().await;
    ws.close().await.unwrap();
    ws.connect().await.unwrap();
    ws.subscribe(channels).await.unwrap();
    assert!(MexcPublicWebSocket::new(Duration::from_secs(1)).is_ok());
}
