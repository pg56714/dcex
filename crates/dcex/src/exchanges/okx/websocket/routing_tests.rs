//! Managed routing between the public/private and business endpoints, the remaining public
//! helpers and argument checks, against a local peer standing in for the OKX hosts.

use std::time::Duration;

use serde_json::json;

use super::{OkxPrivateWebSocket, OkxPrivateWebSocketArg, OkxPublicWebSocket, OkxWebSocketArg};
use crate::ws::test_peer::TestPeer;

const LOGIN_ACK: &str = r#"{"event":"login","code":0,"msg":""}"#;

#[tokio::test]
async fn public_client_moves_to_business_only_before_subscribing() {
    let mut peer = TestPeer::start().await;
    let mut ws = OkxPublicWebSocket::with_managed_route(&peer.url, Duration::from_secs(5)).unwrap();
    ws.connect().await.unwrap();
    assert_eq!(peer.next_handshake().await.path, "/public");
    // Candles live on the business endpoint: the idle client reconnects there.
    ws.subscribe_klines("BTC-USDT-SWAP", "1H").await.unwrap();
    assert_eq!(peer.next_handshake().await.path, "/business");
    assert_eq!(
        peer.next_json().await,
        json!({"op": "subscribe", "args": [{"channel": "candle1H", "instId": "BTC-USDT-SWAP"}]})
    );
    // With a business subscription open, public channels need their own client.
    let error = ws
        .subscribe_ticker("BTC-USDT")
        .await
        .unwrap_err()
        .to_string();
    assert!(error.contains("separate WebSocket connections"), "{error}");
    let error = ws
        .unsubscribe_channel("tickers")
        .await
        .unwrap_err()
        .to_string();
    assert!(error.contains("separate WebSocket connections"), "{error}");
    ws.unsubscribe(vec![
        OkxWebSocketArg::with_inst_id("candle1H", "BTC-USDT-SWAP").unwrap(),
    ])
    .await
    .unwrap();
    assert_eq!(peer.next_json().await["op"], "unsubscribe");
    // Once nothing is subscribed the client may move back to the public endpoint.
    ws.subscribe_trades("BTC-USDT").await.unwrap();
    assert_eq!(peer.next_handshake().await.path, "/public");
    assert_eq!(peer.next_json().await["args"][0]["channel"], "trades");
}

#[tokio::test]
async fn private_client_logs_in_again_after_moving_to_business() {
    let mut peer = TestPeer::start().await;
    let mut ws = OkxPrivateWebSocket::with_managed_route(
        "api-key".into(),
        "api-secret".into(),
        "passphrase".into(),
        &peer.url,
        Duration::from_secs(5),
    )
    .unwrap();
    peer.push(LOGIN_ACK);
    ws.connect().await.unwrap();
    assert_eq!(peer.next_handshake().await.path, "/private");
    assert_eq!(peer.next_json().await["op"], "login");

    let algo = vec![OkxPrivateWebSocketArg::with_inst_type("orders-algo", "SWAP").unwrap()];
    let driver = async {
        assert_eq!(peer.next_handshake().await.path, "/business");
        assert_eq!(peer.next_json().await["op"], "login");
        peer.push(LOGIN_ACK);
        peer.next_json().await
    };
    let (subscribed, frame) = tokio::join!(ws.subscribe(algo.clone()), driver);
    subscribed.unwrap();
    assert!(ws.is_logged_in());
    assert_eq!(frame["args"][0]["channel"], "orders-algo");

    let error = ws.subscribe_account().await.unwrap_err().to_string();
    assert!(error.contains("separate WebSocket connections"), "{error}");
    let account = vec![OkxPrivateWebSocketArg::new("account").unwrap()];
    let error = ws.unsubscribe(account).await.unwrap_err().to_string();
    assert!(error.contains("separate WebSocket connections"), "{error}");
    ws.unsubscribe(algo).await.unwrap();
    assert_eq!(peer.next_json().await["op"], "unsubscribe");
}

#[tokio::test]
async fn public_helpers_and_raw_arguments() {
    let mut peer = TestPeer::start().await;
    let mut ws = OkxPublicWebSocket::with_url(peer.url.clone(), Duration::from_secs(5)).unwrap();
    ws.connect().await.unwrap();
    assert!(ws.is_connected());
    ws.subscribe_ticker("BTC-USDT").await.unwrap();
    ws.subscribe_orderbook5("BTC-USDT-SWAP").await.unwrap();
    ws.subscribe_channel("instruments").await.unwrap();
    ws.unsubscribe_channel_for_symbol("tickers", "BTC-USDT")
        .await
        .unwrap();
    for (op, arg) in [
        (
            "subscribe",
            json!({"channel": "tickers", "instId": "BTC-USDT"}),
        ),
        (
            "subscribe",
            json!({"channel": "books5", "instId": "BTC-USDT-SWAP"}),
        ),
        ("subscribe", json!({"channel": "instruments"})),
        (
            "unsubscribe",
            json!({"channel": "tickers", "instId": "BTC-USDT"}),
        ),
    ] {
        assert_eq!(peer.next_json().await, json!({"op": op, "args": [arg]}));
    }
    for (op, args, reason) in [
        ("subscribe", vec![], "requires at least one argument"),
        (
            "resubscribe",
            vec![json!({"channel": "tickers"})],
            "requires at least one argument",
        ),
        (
            "subscribe",
            vec![json!("tickers")],
            "subscription argument must be an object",
        ),
        (
            "subscribe",
            vec![json!({"channel": "tickers", "depth": "5"})],
            "unsupported subscription field",
        ),
        (
            "subscribe",
            vec![json!({"channel": "tickers", "instId": 1})],
            "unsupported subscription field",
        ),
    ] {
        let error = ws
            .subscription_args(op, args)
            .await
            .unwrap_err()
            .to_string();
        assert!(error.contains(reason), "{reason}: {error}");
    }
    assert!(ws.subscribe(vec![]).await.is_err());
    assert!(ws.subscribe_klines("BTC-USDT", "7m").await.is_err());
    assert!(ws.subscribe_channel(" ").await.is_err());
    assert!(OkxWebSocketArg::with_inst_id("tickers", " ").is_err());
    assert!(peer.quiet(Duration::from_millis(200)).await);
    peer.push(r#"{"arg":{"channel":"tickers"},"data":[]}"#);
    assert_eq!(ws.recv().await.unwrap()["arg"]["channel"], "tickers");
}

#[test]
fn private_argument_builders() {
    let json = |arg: OkxPrivateWebSocketArg| arg.to_json();
    assert_eq!(
        json(OkxPrivateWebSocketArg::with_inst_id("positions", "BTC-USDT-SWAP").unwrap()),
        json!({"channel": "positions", "instId": "BTC-USDT-SWAP"})
    );
    assert_eq!(
        json(
            OkxPrivateWebSocketArg::with_inst_type_and_ccy("balance_and_position", "SWAP", "BTC")
                .unwrap()
        ),
        json!({"channel": "balance_and_position", "instType": "SWAP", "ccy": "BTC"})
    );
    assert_eq!(
        json(
            OkxPrivateWebSocketArg::with_inst_id_and_ccy("account-greeks", "BTC-USD-SWAP", "BTC")
                .unwrap()
        ),
        json!({"channel": "account-greeks", "instId": "BTC-USD-SWAP", "ccy": "BTC"})
    );
    assert_eq!(
        json(
            OkxPrivateWebSocketArg::with_inst_type_and_id_and_ccy(
                "orders",
                "SWAP",
                "BTC-USDT-SWAP",
                "USDT"
            )
            .unwrap()
        ),
        json!({"channel": "orders", "instType": "SWAP", "instId": "BTC-USDT-SWAP", "ccy": "USDT"})
    );
    assert!(OkxPrivateWebSocketArg::new(" ").is_err());
    assert!(OkxPrivateWebSocketArg::with_inst_id("positions", " ").is_err());
    assert!(OkxPrivateWebSocketArg::with_ccy("account", " ").is_err());
    assert!(
        OkxPrivateWebSocket::new("k".into(), "s".into(), "p".into(), Duration::from_secs(1))
            .is_ok()
    );
    assert!(OkxPublicWebSocket::new(Duration::from_secs(1)).is_ok());
}
