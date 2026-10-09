//! Equity stream URLs from every constructor, argument checks and a local round trip.

use std::time::Duration;

use serde_json::json;

use super::BinanceEquityWebSocket;
use crate::ws::test_peer::TestPeer;

const BASE: &str = "wss://nbstream.binance.com/equity/ws";

#[test]
fn convenience_constructors_target_the_documented_streams() {
    let t = Duration::from_secs(1);
    let url = |ws: BinanceEquityWebSocket| ws.url().to_string();
    assert_eq!(
        url(BinanceEquityWebSocket::price(t).unwrap()),
        format!("{BASE}/price")
    );
    assert_eq!(
        url(BinanceEquityWebSocket::quote("AAPL-USDC-EQUITY", t).unwrap()),
        format!("{BASE}/AAPL@quote")
    );
    assert_eq!(
        url(BinanceEquityWebSocket::klines("AAPL-USDC-EQUITY", "5m", t).unwrap()),
        format!("{BASE}/AAPL@kline_5m")
    );
    assert_eq!(
        url(BinanceEquityWebSocket::calendar(t).unwrap()),
        format!("{BASE}/calendar")
    );
    assert_eq!(
        url(BinanceEquityWebSocket::tradability("AAPL-USDC-EQUITY", t).unwrap()),
        format!("{BASE}/AAPL@tradability")
    );
    assert_eq!(
        url(BinanceEquityWebSocket::trading_status("AAPL-USDC-EQUITY", t).unwrap()),
        format!("{BASE}/AAPL@tradingStatus")
    );
    assert_eq!(
        url(BinanceEquityWebSocket::order_reports("lk-1", t).unwrap()),
        format!("{BASE}/lk-1@orderReport")
    );
    // The documented camelCase names select the same streams.
    for (stream, symbol, interval, key, path) in [
        (
            "klines",
            Some("AAPL-USDC-EQUITY"),
            Some("1d"),
            None,
            "AAPL@kline_1d",
        ),
        (
            "tradingStatus",
            Some("AAPL-USDC-EQUITY"),
            None,
            None,
            "AAPL@tradingStatus",
        ),
        ("orderReport", None, None, Some("lk-2"), "lk-2@orderReport"),
    ] {
        assert_eq!(
            url(BinanceEquityWebSocket::new(stream, symbol, interval, key, t).unwrap()),
            format!("{BASE}/{path}")
        );
    }
}

#[test]
fn streams_reject_missing_and_foreign_arguments() {
    let t = Duration::from_secs(1);
    let new = |stream, symbol, interval, key| {
        BinanceEquityWebSocket::new(stream, symbol, interval, key, t).is_err()
    };
    let aapl = Some("AAPL-USDC-EQUITY");
    // Arguments a stream does not take.
    assert!(new("price", aapl, None, None));
    assert!(new("price", None, Some("1m"), None));
    assert!(new("price", None, None, Some("lk")));
    assert!(new("calendar", aapl, None, None));
    assert!(new("calendar", None, Some("1m"), None));
    assert!(new("calendar", None, None, Some("lk")));
    assert!(new("quote", aapl, Some("1m"), None));
    assert!(new("quote", aapl, None, Some("lk")));
    assert!(new("kline", aapl, Some("1m"), Some("lk")));
    assert!(new("tradability", aapl, Some("1m"), None));
    assert!(new("tradability", aapl, None, Some("lk")));
    assert!(new("trading_status", aapl, Some("1m"), None));
    assert!(new("trading_status", aapl, None, Some("lk")));
    assert!(new("order_report", aapl, None, Some("lk")));
    assert!(new("order_report", None, Some("1m"), Some("lk")));
    // Required arguments.
    assert!(new("quote", None, None, None));
    assert!(new("kline", aapl, None, None));
    assert!(new("kline", aapl, Some("1 m"), None));
    assert!(new("order_report", None, None, None));
    // Only Equity symbols, and a base URL is required.
    assert!(new("tradability", Some("BTC-USDT-SWAP"), None, None));
    assert!(
        BinanceEquityWebSocket::with_base_url("price", None, None, None, t, " / ".into()).is_err()
    );
}

#[tokio::test]
async fn equity_stream_round_trip() {
    let mut peer = TestPeer::start().await;
    let mut ws = BinanceEquityWebSocket::with_base_url(
        "quote",
        Some("AAPL-USDC-EQUITY"),
        None,
        None,
        Duration::from_secs(5),
        format!("{}/equity/", peer.url),
    )
    .unwrap();
    ws.connect().await.unwrap();
    assert_eq!(peer.next_handshake().await.path, "/equity/ws/AAPL@quote");
    assert!(ws.is_connected());
    peer.push_json(&json!({"e": "quote", "s": "AAPL"}));
    assert_eq!(ws.recv().await.unwrap()["e"], "quote");
    peer.push("{}");
    assert_eq!(ws.recv_bytes().await.unwrap(), b"{}");
    ws.close().await.unwrap();
    assert!(!ws.is_connected());
}
