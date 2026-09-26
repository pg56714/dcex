//! Route coverage for every Kraken dispatch name against the official REST docs
//! (https://docs.kraken.com/api-reference/), exercised through a local server.

use std::collections::{BTreeSet, HashMap};
use std::time::Duration;

use super::{KrakenClient, SECRET};

/// Rows: (public, method name, params, HTTP method, path).
#[allow(clippy::type_complexity)]
const ROUTE_CASES: &[(bool, &str, &[(&str, &str)], &str, &str)] = &[
    (true, "get_server_time", &[], "GET", "/0/public/Time"),
    (
        true,
        "get_spot_system_status",
        &[],
        "GET",
        "/0/public/SystemStatus",
    ),
    (true, "get_spot_assets", &[], "GET", "/0/public/Assets"),
    (
        true,
        "get_spot_asset_pairs",
        &[("info", "info")],
        "GET",
        "/0/public/AssetPairs",
    ),
    (
        true,
        "get_spot_ticker",
        &[("product_symbol", "BTC-USD-SPOT")],
        "GET",
        "/0/public/Ticker",
    ),
    (
        true,
        "get_spot_orderbook",
        &[("product_symbol", "BTC-USD-SPOT")],
        "GET",
        "/0/public/Depth",
    ),
    (
        true,
        "get_spot_public_trades",
        &[("product_symbol", "BTC-USD-SPOT")],
        "GET",
        "/0/public/Trades",
    ),
    (
        true,
        "get_spot_kline",
        &[("product_symbol", "BTC-USD-SPOT"), ("interval", "1")],
        "GET",
        "/0/public/OHLC",
    ),
    (
        true,
        "get_spot_spread",
        &[("product_symbol", "BTC-USD-SPOT")],
        "GET",
        "/0/public/Spread",
    ),
    (
        true,
        "get_futures_instruments",
        &[],
        "GET",
        "/derivatives/api/v3/instruments",
    ),
    (
        true,
        "get_futures_tickers",
        &[],
        "GET",
        "/derivatives/api/v3/tickers",
    ),
    (
        true,
        "get_futures_orderbook",
        &[("product_symbol", "BTC-USD-SWAP")],
        "GET",
        "/derivatives/api/v3/orderbook",
    ),
    (
        true,
        "get_futures_public_trades",
        &[("product_symbol", "BTC-USD-SWAP")],
        "GET",
        "/derivatives/api/v3/history",
    ),
    (
        true,
        "get_futures_kline",
        &[
            ("product_symbol", "BTC-USD-SWAP"),
            ("timeframe", "1m"),
            ("tick_type", "trade"),
        ],
        "GET",
        "/api/charts/v1/trade/PF_XBTUSD/1m",
    ),
    (
        false,
        "get_spot_account_balance",
        &[],
        "POST",
        "/0/private/Balance",
    ),
    (
        false,
        "get_spot_trade_balance",
        &[],
        "POST",
        "/0/private/TradeBalance",
    ),
    (
        false,
        "get_spot_open_positions",
        &[],
        "POST",
        "/0/private/OpenPositions",
    ),
    (false, "get_spot_ledgers", &[], "POST", "/0/private/Ledgers"),
    (
        false,
        "get_spot_trade_volume",
        &[],
        "POST",
        "/0/private/TradeVolume",
    ),
    (
        false,
        "wallet_transfer_to_futures",
        &[
            ("asset", "USD"),
            ("amount", "1"),
            ("from", "Spot Wallet"),
            ("to", "Futures Wallet"),
        ],
        "POST",
        "/0/private/WalletTransfer",
    ),
    (
        false,
        "get_earn_strategies",
        &[],
        "POST",
        "/0/private/Earn/Strategies",
    ),
    (
        false,
        "get_earn_allocations",
        &[],
        "POST",
        "/0/private/Earn/Allocations",
    ),
    (
        false,
        "allocate_earn_funds",
        &[("strategy_id", "strategy"), ("amount", "1")],
        "POST",
        "/0/private/Earn/Allocate",
    ),
    (
        false,
        "deallocate_earn_funds",
        &[("strategy_id", "strategy"), ("amount", "1")],
        "POST",
        "/0/private/Earn/Deallocate",
    ),
    (
        false,
        "get_earn_allocation_status",
        &[("strategy_id", "strategy")],
        "POST",
        "/0/private/Earn/AllocateStatus",
    ),
    (
        false,
        "get_earn_deallocation_status",
        &[("strategy_id", "strategy")],
        "POST",
        "/0/private/Earn/DeallocateStatus",
    ),
    (
        false,
        "place_spot_order",
        &[
            ("product_symbol", "BTC-USD-SPOT"),
            ("side", "buy"),
            ("ordertype", "limit"),
            ("volume", "0.01"),
            ("price", "100"),
        ],
        "POST",
        "/0/private/AddOrder",
    ),
    (
        false,
        "place_spot_market_order",
        &[
            ("product_symbol", "BTC-USD-SPOT"),
            ("side", "buy"),
            ("volume", "0.01"),
        ],
        "POST",
        "/0/private/AddOrder",
    ),
    (
        false,
        "place_spot_market_buy_order",
        &[("product_symbol", "BTC-USD-SPOT"), ("volume", "0.01")],
        "POST",
        "/0/private/AddOrder",
    ),
    (
        false,
        "place_spot_market_sell_order",
        &[("product_symbol", "BTC-USD-SPOT"), ("volume", "0.01")],
        "POST",
        "/0/private/AddOrder",
    ),
    (
        false,
        "place_spot_limit_order",
        &[
            ("product_symbol", "BTC-USD-SPOT"),
            ("side", "buy"),
            ("volume", "0.01"),
            ("price", "100"),
        ],
        "POST",
        "/0/private/AddOrder",
    ),
    (
        false,
        "place_spot_limit_buy_order",
        &[
            ("product_symbol", "BTC-USD-SPOT"),
            ("volume", "0.01"),
            ("price", "100"),
        ],
        "POST",
        "/0/private/AddOrder",
    ),
    (
        false,
        "place_spot_limit_sell_order",
        &[
            ("product_symbol", "BTC-USD-SPOT"),
            ("volume", "0.01"),
            ("price", "100"),
        ],
        "POST",
        "/0/private/AddOrder",
    ),
    (
        false,
        "place_spot_post_only_limit_order",
        &[
            ("product_symbol", "BTC-USD-SPOT"),
            ("side", "sell"),
            ("volume", "0.01"),
            ("price", "100"),
        ],
        "POST",
        "/0/private/AddOrder",
    ),
    (
        false,
        "place_spot_post_only_limit_buy_order",
        &[
            ("product_symbol", "BTC-USD-SPOT"),
            ("volume", "0.01"),
            ("price", "100"),
        ],
        "POST",
        "/0/private/AddOrder",
    ),
    (
        false,
        "place_spot_post_only_limit_sell_order",
        &[
            ("product_symbol", "BTC-USD-SPOT"),
            ("volume", "0.01"),
            ("price", "100"),
        ],
        "POST",
        "/0/private/AddOrder",
    ),
    (
        false,
        "get_spot_open_orders",
        &[],
        "POST",
        "/0/private/OpenOrders",
    ),
    (
        false,
        "get_spot_closed_orders",
        &[],
        "POST",
        "/0/private/ClosedOrders",
    ),
    (
        false,
        "get_spot_orders",
        &[("txid", "OABC-123")],
        "POST",
        "/0/private/QueryOrders",
    ),
    (
        false,
        "get_spot_trade_history",
        &[],
        "POST",
        "/0/private/TradesHistory",
    ),
    (
        false,
        "amend_spot_order",
        &[("txid", "OABC-123"), ("order_qty", "1.25")],
        "POST",
        "/0/private/AmendOrder",
    ),
    (
        false,
        "cancel_spot_order",
        &[("txid", "OABC-123")],
        "POST",
        "/0/private/CancelOrder",
    ),
    (
        false,
        "cancel_spot_all_orders",
        &[],
        "POST",
        "/0/private/CancelAll",
    ),
    (
        false,
        "cancel_spot_all_orders_after",
        &[("timeout", "60")],
        "POST",
        "/0/private/CancelAllOrdersAfter",
    ),
    (
        false,
        "get_spot_websocket_token",
        &[],
        "POST",
        "/0/private/GetWebSocketsToken",
    ),
    (
        false,
        "get_futures_accounts",
        &[],
        "GET",
        "/derivatives/api/v3/accounts",
    ),
    (
        false,
        "get_futures_open_positions",
        &[],
        "GET",
        "/derivatives/api/v3/openpositions",
    ),
    (
        false,
        "get_futures_fills",
        &[],
        "GET",
        "/derivatives/api/v3/fills",
    ),
    (
        false,
        "futures_wallet_transfer",
        &[
            ("amount", "1"),
            ("fromAccount", "cash"),
            ("toAccount", "flex"),
            ("unit", "USD"),
        ],
        "POST",
        "/derivatives/api/v3/transfer",
    ),
    (
        false,
        "withdraw_futures_to_spot_wallet",
        &[("amount", "1"), ("currency", "USD")],
        "POST",
        "/derivatives/api/v3/withdrawal",
    ),
    (
        false,
        "place_futures_order",
        &[
            ("product_symbol", "BTC-USD-SWAP"),
            ("side", "buy"),
            ("orderType", "lmt"),
            ("size", "1"),
            ("limitPrice", "100"),
        ],
        "POST",
        "/derivatives/api/v3/sendorder",
    ),
    (
        false,
        "place_futures_market_order",
        &[
            ("product_symbol", "BTC-USD-SWAP"),
            ("side", "buy"),
            ("size", "1"),
        ],
        "POST",
        "/derivatives/api/v3/sendorder",
    ),
    (
        false,
        "place_futures_market_buy_order",
        &[("product_symbol", "BTC-USD-SWAP"), ("size", "1")],
        "POST",
        "/derivatives/api/v3/sendorder",
    ),
    (
        false,
        "place_futures_market_sell_order",
        &[("product_symbol", "BTC-USD-SWAP"), ("size", "1")],
        "POST",
        "/derivatives/api/v3/sendorder",
    ),
    (
        false,
        "place_futures_limit_order",
        &[
            ("product_symbol", "BTC-USD-SWAP"),
            ("side", "buy"),
            ("size", "1"),
            ("price", "100"),
        ],
        "POST",
        "/derivatives/api/v3/sendorder",
    ),
    (
        false,
        "place_futures_limit_buy_order",
        &[
            ("product_symbol", "BTC-USD-SWAP"),
            ("size", "1"),
            ("price", "100"),
        ],
        "POST",
        "/derivatives/api/v3/sendorder",
    ),
    (
        false,
        "place_futures_limit_sell_order",
        &[
            ("product_symbol", "BTC-USD-SWAP"),
            ("size", "1"),
            ("price", "100"),
        ],
        "POST",
        "/derivatives/api/v3/sendorder",
    ),
    (
        false,
        "place_futures_post_only_limit_order",
        &[
            ("product_symbol", "BTC-USD-SWAP"),
            ("side", "sell"),
            ("size", "1"),
            ("price", "100"),
        ],
        "POST",
        "/derivatives/api/v3/sendorder",
    ),
    (
        false,
        "place_futures_post_only_limit_buy_order",
        &[
            ("product_symbol", "BTC-USD-SWAP"),
            ("size", "1"),
            ("price", "100"),
        ],
        "POST",
        "/derivatives/api/v3/sendorder",
    ),
    (
        false,
        "place_futures_post_only_limit_sell_order",
        &[
            ("product_symbol", "BTC-USD-SWAP"),
            ("size", "1"),
            ("price", "100"),
        ],
        "POST",
        "/derivatives/api/v3/sendorder",
    ),
    (
        false,
        "get_futures_open_orders",
        &[],
        "GET",
        "/derivatives/api/v3/openorders",
    ),
    (
        false,
        "get_futures_order_status",
        &[("orderIds", "order-1")],
        "POST",
        "/derivatives/api/v3/orders/status",
    ),
    (
        false,
        "edit_futures_order",
        &[("orderId", "order-1"), ("limitPrice", "101")],
        "POST",
        "/derivatives/api/v3/editorder",
    ),
    (
        false,
        "cancel_futures_order",
        &[("order_id", "order-1")],
        "POST",
        "/derivatives/api/v3/cancelorder",
    ),
    (
        false,
        "cancel_futures_all_orders",
        &[],
        "POST",
        "/derivatives/api/v3/cancelallorders",
    ),
    (
        false,
        "cancel_futures_all_orders_after",
        &[("timeout", "60")],
        "POST",
        "/derivatives/api/v3/cancelallordersafter",
    ),
];

fn serve_one(
    spot_body: &'static str,
    futures_body: &'static str,
) -> (String, std::thread::JoinHandle<(String, String)>) {
    use std::io::{Read, Write};
    use std::net::TcpListener;

    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let url = format!("http://{}", listener.local_addr().expect("address"));
    let handle = std::thread::spawn(move || {
        let (mut stream, _) = listener.accept().expect("accept");
        let mut data = Vec::new();
        let mut buffer = [0u8; 4096];
        loop {
            let size = stream.read(&mut buffer).expect("read");
            if size == 0 {
                break;
            }
            data.extend_from_slice(&buffer[..size]);
            let text = String::from_utf8_lossy(&data);
            if let Some(end) = text.find("\r\n\r\n") {
                let length = text[..end]
                    .lines()
                    .find_map(|line| {
                        let (name, value) = line.split_once(':')?;
                        if name.eq_ignore_ascii_case("content-length") {
                            value.trim().parse::<usize>().ok()
                        } else {
                            None
                        }
                    })
                    .unwrap_or(0);
                if data.len() >= end + 4 + length {
                    break;
                }
            }
        }
        let text = String::from_utf8_lossy(&data).into_owned();
        let (head, body) = text.split_once("\r\n\r\n").unwrap_or((text.as_str(), ""));
        let response = if head.lines().next().unwrap_or_default().contains(" /0/") {
            spot_body
        } else {
            futures_body
        };
        write!(
            stream,
            "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
            response.len(),
            response
        )
        .expect("write");
        (head.to_string(), body.to_string())
    });
    (url, handle)
}

fn client_for(url: String) -> KrakenClient {
    KrakenClient::with_base_urls(
        Some("spot-key".into()),
        Some(SECRET.into()),
        Some("futures-key".into()),
        Some(SECRET.into()),
        Duration::from_secs(2),
        url.clone(),
        url,
    )
    .expect("client")
}

fn pairs(params: &[(&str, &str)]) -> Vec<(String, String)> {
    params
        .iter()
        .map(|(key, value)| (key.to_string(), value.to_string()))
        .collect()
}

#[test]
fn every_dispatch_name_uses_official_route() {
    for (public, method, params, http_method, path) in ROUTE_CASES {
        let (url, server) = serve_one(
            r#"{"error":[],"result":{"token":"ws-token"}}"#,
            r#"{"result":"success"}"#,
        );
        let client = client_for(url);
        let params = pairs(params);
        let method_name = method.to_string();
        let public = *public;
        crate::http::block_on(async move {
            if public {
                client.public_request(&method_name, params).await
            } else {
                client.private_request(&method_name, params).await
            }
        })
        .unwrap_or_else(|error| panic!("{method}: {error}"));
        let (head, _body) = server.join().expect("server");
        let request_line = head.lines().next().unwrap_or_default();
        let expected = format!("{http_method} {path}");
        assert!(
            request_line == format!("{expected} HTTP/1.1")
                || request_line.starts_with(&format!("{expected}?")),
            "{method}: {request_line}"
        );
        let lowered = head.to_ascii_lowercase();
        if path.starts_with("/0/private/") {
            assert!(lowered.contains("api-sign:"), "{method} must be signed");
        } else if path.starts_with("/0/public/") {
            assert!(!lowered.contains("api-sign:"), "{method} must be unsigned");
        } else if !public {
            assert!(lowered.contains("authent:"), "{method} must be signed");
        }
    }
}

#[test]
fn route_cases_cover_every_dispatch_name() {
    let source = [
        include_str!("../market.rs"),
        include_str!("../account.rs"),
        include_str!("../earn.rs"),
        include_str!("../trade.rs"),
    ]
    .join("\n");
    let mut names = BTreeSet::new();
    for line in source.lines() {
        let trimmed = line.trim_start();
        if !trimmed.starts_with('"') || !trimmed.contains("=>") {
            continue;
        }
        let arm = trimmed.split("=>").next().unwrap_or_default();
        for part in arm.split('|') {
            let name = part.trim().trim_matches('"');
            if !name.is_empty() && name.chars().all(|c| c.is_ascii_lowercase() || c == '_') {
                names.insert(name.to_string());
            }
        }
    }
    let covered: BTreeSet<String> = ROUTE_CASES
        .iter()
        .map(|(_, method, ..)| method.to_string())
        .collect();
    assert!(
        names.len() >= 60,
        "parsed only {} dispatch names",
        names.len()
    );
    let missing: Vec<_> = names.difference(&covered).collect();
    assert!(
        missing.is_empty(),
        "dispatch names without route cases: {missing:?}"
    );
}

#[test]
fn spot_add_order_body_matches_documented_fields() {
    let (url, server) = serve_one(r#"{"error":[],"result":{}}"#, "{}");
    let client = client_for(url);
    crate::http::block_on(async move {
        client
            .private_request(
                "place_spot_post_only_limit_sell_order",
                pairs(&[
                    ("product_symbol", "ETH-USD-SPOT"),
                    ("volume", "0.5"),
                    ("price", "2000"),
                    ("cl_ord_id", "client-1"),
                ]),
            )
            .await
    })
    .expect("request");
    let (_head, body) = server.join().expect("server");
    let fields: HashMap<_, _> = body
        .split('&')
        .filter_map(|pair| pair.split_once('='))
        .collect();
    assert_eq!(fields.get("pair"), Some(&"ETHUSD"));
    assert_eq!(fields.get("type"), Some(&"sell"));
    assert_eq!(fields.get("ordertype"), Some(&"limit"));
    assert_eq!(fields.get("volume"), Some(&"0.5"));
    assert_eq!(fields.get("price"), Some(&"2000"));
    assert_eq!(fields.get("oflags"), Some(&"post"));
    assert_eq!(fields.get("cl_ord_id"), Some(&"client-1"));
    assert!(fields.contains_key("nonce"));
}

#[test]
fn futures_send_order_body_matches_documented_fields() {
    let (url, server) = serve_one("{}", r#"{"result":"success"}"#);
    let client = client_for(url);
    crate::http::block_on(async move {
        client
            .private_request(
                "place_futures_post_only_limit_buy_order",
                pairs(&[
                    ("product_symbol", "ETH-USD-SWAP"),
                    ("size", "3"),
                    ("price", "2000"),
                ]),
            )
            .await
    })
    .expect("request");
    let (head, body) = server.join().expect("server");
    let request_line = head.lines().next().unwrap_or_default();
    let encoded = if body.is_empty() {
        request_line
            .split_whitespace()
            .nth(1)
            .and_then(|target| target.split_once('?'))
            .map(|(_, query)| query.to_string())
            .unwrap_or_default()
    } else {
        body
    };
    let fields: HashMap<_, _> = encoded
        .split('&')
        .filter_map(|pair| pair.split_once('='))
        .collect();
    assert_eq!(fields.get("symbol"), Some(&"PF_ETHUSD"));
    assert_eq!(fields.get("side"), Some(&"buy"));
    assert_eq!(fields.get("orderType"), Some(&"post"));
    assert_eq!(fields.get("size"), Some(&"3"));
    assert_eq!(fields.get("limitPrice"), Some(&"2000"));
}

#[test]
fn unknown_dispatch_names_are_rejected_before_transport() {
    let client = KrakenClient::public(Duration::from_secs(1)).expect("client");
    let other = KrakenClient::public(Duration::from_secs(1)).expect("client");
    let public =
        crate::http::block_on(async move { client.public_request("get_nope", Vec::new()).await })
            .expect_err("unknown public");
    assert!(
        public
            .to_string()
            .contains("unsupported Kraken public method")
    );
    let private =
        crate::http::block_on(async move { other.private_request("place_nope", Vec::new()).await })
            .expect_err("unknown private");
    assert!(
        private
            .to_string()
            .contains("unsupported Kraken private method")
    );
}
