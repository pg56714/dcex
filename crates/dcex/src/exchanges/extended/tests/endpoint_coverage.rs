//! Offline route coverage for every Extended REST dispatch name.
//!
//! Each case sends one dispatch name through `public_request` /
//! `private_request` against a local recording server and asserts that the
//! HTTP method, path and query that reach the wire match the official Extended
//! API documentation (<https://api.docs.extended.exchange/>).

use std::io::{ErrorKind, Read, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use serde_json::{Value, json};

use super::super::ExtendedClient;
use crate::http::block_on;

const STARK_PRIVATE_KEY: &str = "0x1";
const STARK_PUBLIC_KEY: &str = "0x1ef15c18599971b7beced415a40f0c7deacfd9b0d1819e03d723d8bc943cfca";
const VAULT: u64 = 4_272_448_241_247_734_333;

/// One response body that satisfies both the market-config and fee lookups
/// performed while auto-signing an order.
const RESPONSE: &str = r#"{"status":"OK","data":[{"name":"BTC-USD","market":"BTC-USD","makerFeeRate":"0.0001","takerFeeRate":"0.00025","l2Config":{"collateralId":"0x555344430000000000000000000000","collateralResolution":1000000,"syntheticId":"0x4254432d31300000000000000000000","syntheticResolution":100000000}}]}"#;

#[derive(Clone, Copy)]
enum Kind {
    Public,
    Private,
}

struct Case {
    kind: Kind,
    name: &'static str,
    params: &'static [(&'static str, &'static str)],
    /// Exact expected request line target (path plus query string).
    target: &'static str,
    method: &'static str,
}

const fn public(
    name: &'static str,
    params: &'static [(&'static str, &'static str)],
    method: &'static str,
    target: &'static str,
) -> Case {
    Case {
        kind: Kind::Public,
        name,
        params,
        target,
        method,
    }
}

const fn private(
    name: &'static str,
    params: &'static [(&'static str, &'static str)],
    method: &'static str,
    target: &'static str,
) -> Case {
    Case {
        kind: Kind::Private,
        name,
        params,
        target,
        method,
    }
}

fn read_request(stream: &mut TcpStream) -> String {
    let mut data = Vec::new();
    let mut buffer = [0u8; 8192];
    loop {
        let size = stream.read(&mut buffer).unwrap_or(0);
        if size == 0 {
            break;
        }
        data.extend_from_slice(&buffer[..size]);
        let text = String::from_utf8_lossy(&data);
        if let Some(header_end) = text.find("\r\n\r\n") {
            let content_length = text[..header_end]
                .lines()
                .find_map(|line| {
                    let (key, value) = line.split_once(':')?;
                    key.eq_ignore_ascii_case("content-length")
                        .then(|| value.trim().parse::<usize>().ok())
                        .flatten()
                })
                .unwrap_or(0);
            if data.len() >= header_end + 4 + content_length {
                break;
            }
        }
    }
    String::from_utf8_lossy(&data).into_owned()
}

fn multi_request_server() -> (String, Arc<AtomicBool>, JoinHandle<Vec<String>>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    listener.set_nonblocking(true).expect("nonblocking");
    let address = listener.local_addr().expect("address");
    let stop = Arc::new(AtomicBool::new(false));
    let stop_flag = Arc::clone(&stop);
    let handle = thread::spawn(move || {
        let deadline = Instant::now() + Duration::from_secs(10);
        let mut requests = Vec::new();
        loop {
            match listener.accept() {
                Ok((mut stream, _)) => {
                    stream.set_nonblocking(false).expect("blocking stream");
                    stream
                        .set_read_timeout(Some(Duration::from_secs(10)))
                        .expect("read timeout");
                    requests.push(read_request(&mut stream));
                    let response = format!(
                        "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\
                         Content-Length: {}\r\nConnection: close\r\n\r\n{}",
                        RESPONSE.len(),
                        RESPONSE
                    );
                    let _ = stream.write_all(response.as_bytes());
                }
                Err(error) if error.kind() == ErrorKind::WouldBlock => {
                    if stop_flag.load(Ordering::SeqCst) || Instant::now() >= deadline {
                        return requests;
                    }
                    thread::sleep(Duration::from_millis(2));
                }
                Err(error) => panic!("accept failed: {error}"),
            }
        }
    });
    (format!("http://{address}"), stop, handle)
}

fn client(base_url: &str) -> ExtendedClient {
    ExtendedClient::with_base_url_and_stark(
        Some("extended-key".to_string()),
        Some(STARK_PRIVATE_KEY.to_string()),
        Some(STARK_PUBLIC_KEY.to_string()),
        Some(VAULT),
        None,
        Duration::from_secs(10),
        base_url.to_string(),
        "dcex-test".to_string(),
    )
    .expect("client")
}

fn run(
    kind: Kind,
    name: &'static str,
    params: Vec<(String, String)>,
) -> (Result<Value, String>, Vec<String>) {
    let (base_url, stop, handle) = multi_request_server();
    let client = client(&base_url);
    let result = block_on(async move {
        match kind {
            Kind::Public => client.public_request(name, params).await,
            Kind::Private => client.private_request(name, params).await,
        }
    });
    stop.store(true, Ordering::SeqCst);
    let requests = handle.join().expect("server thread");
    (
        result
            .map(|response| response.data)
            .map_err(|error| error.to_string()),
        requests,
    )
}

fn pairs(params: &[(&str, &str)]) -> Vec<(String, String)> {
    params
        .iter()
        .map(|(key, value)| ((*key).to_string(), (*value).to_string()))
        .collect()
}

fn request_line(request: &str) -> &str {
    request.lines().next().unwrap_or_default()
}

fn body(request: &str) -> &str {
    request.split_once("\r\n\r\n").map_or("", |(_, body)| body)
}

fn run_case(case: &Case) -> Result<(), String> {
    let name = case.name;
    let (result, requests) = run(case.kind, name, pairs(case.params));
    let lines: Vec<&str> = requests
        .iter()
        .map(|request| request_line(request))
        .collect();
    if let Err(error) = result {
        return Err(format!("{name}: request failed: {error} (wire: {lines:?})"));
    }
    let [request] = requests.as_slice() else {
        return Err(format!(
            "{name}: expected exactly one request, got {lines:?}"
        ));
    };
    let expected = format!("{} {} HTTP/1.1", case.method, case.target);
    if request_line(request) != expected {
        return Err(format!(
            "{name}: expected `{expected}`, wire was `{}`",
            request_line(request)
        ));
    }
    let has_key = request
        .to_ascii_lowercase()
        .contains("x-api-key: extended-key");
    // The client always attaches X-Api-Key when configured; private calls must
    // never be sent without it.
    if matches!(case.kind, Kind::Private) && !has_key {
        return Err(format!("{name}: private request missing X-Api-Key"));
    }
    Ok(())
}

fn assert_cases(cases: &[Case]) {
    let failures: Vec<String> = cases
        .iter()
        .filter_map(|case| run_case(case).err())
        .collect();
    assert!(
        failures.is_empty(),
        "{} of {} Extended route(s) failed:\n{}",
        failures.len(),
        cases.len(),
        failures.join("\n")
    );
}

fn assert_rejected_offline(kind: Kind, name: &'static str, params: Vec<(String, String)>) {
    let (result, requests) = run(kind, name, params.clone());
    assert!(result.is_err(), "{name} should be rejected: {params:?}");
    assert!(
        requests.is_empty(),
        "{name} reached the wire before validation: {requests:?}"
    );
}

fn now_ms() -> u64 {
    u64::try_from(
        SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("time")
            .as_millis(),
    )
    .expect("millis")
}

#[test]
fn public_info_routes_match_official_paths() {
    assert_cases(&[
        public("get_markets", &[], "GET", "/api/v1/info/markets"),
        public(
            "get_markets",
            &[("market", "BTC-USD"), ("market", "ETH-USD")],
            "GET",
            "/api/v1/info/markets?market=BTC-USD&market=ETH-USD",
        ),
        public(
            "get_markets",
            &[("product_symbol", "BTC-USD")],
            "GET",
            "/api/v1/info/markets?market=BTC-USD",
        ),
        public(
            "get_assets",
            &[("asset", "BTC"), ("type", "PERPETUAL")],
            "GET",
            "/api/v1/info/assets?asset=BTC&type=PERPETUAL",
        ),
        public(
            "get_asset_index_price",
            &[("asset", "BTC")],
            "GET",
            "/api/v1/info/assets/BTC/price",
        ),
        public(
            "get_market_stats",
            &[("product_symbol", "BTC-USD")],
            "GET",
            "/api/v1/info/markets/BTC-USD/stats",
        ),
        public(
            "get_orderbook",
            &[("market", "ETH-USD")],
            "GET",
            "/api/v1/info/markets/ETH-USD/orderbook",
        ),
        public(
            "get_trades",
            &[("market", "ETH-USD")],
            "GET",
            "/api/v1/info/markets/ETH-USD/trades",
        ),
        public(
            "get_candles",
            &[("market", "BTC-USD"), ("interval", "PT5M"), ("limit", "10")],
            "GET",
            "/api/v1/info/candles/BTC-USD/trades?interval=PT5M&limit=10",
        ),
        public(
            "get_candles",
            &[
                ("market", "BTC-USD"),
                ("candle_type", "index-prices"),
                ("interval", "P1D"),
                ("limit", "1"),
            ],
            "GET",
            "/api/v1/info/candles/BTC-USD/index-prices?interval=P1D&limit=1",
        ),
        public(
            "get_funding",
            &[
                ("market", "BTC-USD"),
                ("startTime", "1"),
                ("endTime", "2"),
                ("cursor", "3"),
            ],
            "GET",
            "/api/v1/info/BTC-USD/funding?startTime=1&endTime=2&cursor=3",
        ),
        public(
            "get_open_interest",
            &[
                ("market", "BTC-USD"),
                ("interval", "P1D"),
                ("startTime", "1"),
                ("endTime", "2"),
            ],
            "GET",
            "/api/v1/info/BTC-USD/open-interests?interval=P1D&startTime=1&endTime=2",
        ),
    ]);
}

#[test]
fn private_account_routes_match_official_paths() {
    assert_cases(&[
        private("get_account_info", &[], "GET", "/api/v1/user/account/info"),
        private(
            "get_account_details",
            &[],
            "GET",
            "/api/v1/user/account/info",
        ),
        private("get_accounts", &[], "GET", "/api/v1/user/accounts"),
        private("get_sub_accounts", &[], "GET", "/api/v1/user/accounts"),
        private("get_balance", &[], "GET", "/api/v1/user/balance"),
        private(
            "get_spot_balances",
            &[],
            "GET",
            "/api/v1/user/spot/balances",
        ),
        private(
            "get_asset_operations",
            &[("type", "DEPOSIT"), ("type", "WITHDRAWAL"), ("id", "5")],
            "GET",
            "/api/v1/user/assetOperations?type=DEPOSIT&type=WITHDRAWAL&id=5",
        ),
        private(
            "get_account_health",
            &[("accountId", "7")],
            "GET",
            "/api/v1/portfolio/accounts/health?accountId=7",
        ),
        private("get_positions", &[], "GET", "/api/v1/user/positions"),
        private(
            "get_positions",
            &[
                ("market", "BTC-USD"),
                ("market", "ETH-USD"),
                ("side", "LONG"),
            ],
            "GET",
            "/api/v1/user/positions?market=BTC-USD&market=ETH-USD&side=LONG",
        ),
        private(
            "get_positions_history",
            &[("market", "BTC-USD"), ("side", "SHORT"), ("limit", "5")],
            "GET",
            "/api/v1/user/positions/history?market=BTC-USD&side=SHORT&limit=5",
        ),
        private(
            "get_trades_history",
            &[
                ("market", "BTC-USD"),
                ("type", "LIQUIDATION"),
                ("side", "SELL"),
            ],
            "GET",
            "/api/v1/user/trades?market=BTC-USD&type=LIQUIDATION&side=SELL",
        ),
        private(
            "get_fills",
            &[("cursor", "9")],
            "GET",
            "/api/v1/user/trades?cursor=9",
        ),
        private(
            "get_funding_payments",
            &[("market", "BTC-USD"), ("startTime", "100"), ("limit", "20")],
            "GET",
            "/api/v1/user/funding/history?market=BTC-USD&startTime=100&limit=20",
        ),
        private(
            "get_leverage",
            &[("market", "BTC-USD")],
            "GET",
            "/api/v1/user/leverage?market=BTC-USD",
        ),
        private("get_fees", &[], "GET", "/api/v1/user/fees"),
        private("get_rebates", &[], "GET", "/api/v1/user/rebates/stats"),
        private(
            "get_builder_dashboard",
            &[],
            "GET",
            "/api/v1/info/builder/dashboard",
        ),
        private(
            "get_builder_trades",
            &[("limit", "10")],
            "GET",
            "/api/v1/builder/trades?limit=10",
        ),
        private(
            "get_bridge_config",
            &[],
            "GET",
            "/api/v1/user/bridge/config",
        ),
        private(
            "get_bridge_quote",
            &[("chainIn", "ARB"), ("chainOut", "STRK"), ("amount", "5")],
            "GET",
            "/api/v1/user/bridge/quote?chainIn=ARB&chainOut=STRK&amount=5",
        ),
    ]);
}

#[test]
fn private_order_routes_match_official_paths() {
    assert_cases(&[
        private("get_open_orders", &[], "GET", "/api/v1/user/orders"),
        private(
            "get_open_orders",
            &[("market", "BTC-USD"), ("type", "TPSL"), ("side", "BUY")],
            "GET",
            "/api/v1/user/orders?market=BTC-USD&type=TPSL&side=BUY",
        ),
        private(
            "get_orders_history",
            &[("id", "1"), ("id", "2"), ("sort", "UPDATED_AT")],
            "GET",
            "/api/v1/user/orders/history?id=1&id=2&sort=UPDATED_AT",
        ),
        private(
            "get_order_history",
            &[("externalId", "abc"), ("limit", "3")],
            "GET",
            "/api/v1/user/orders/history?externalId=abc&limit=3",
        ),
        private(
            "get_order",
            &[("id", "42")],
            "GET",
            "/api/v1/user/orders/42",
        ),
        private(
            "get_order_by_external_id",
            &[("external_id", "cid-1")],
            "GET",
            "/api/v1/user/orders/external/cid-1",
        ),
        private(
            "cancel_order",
            &[("id", "42")],
            "DELETE",
            "/api/v1/user/order/42",
        ),
        private(
            "cancel_order_by_external_id",
            &[("externalId", "cid-1")],
            "DELETE",
            "/api/v1/user/order?externalId=cid-1",
        ),
        private(
            "mass_cancel",
            &[("body", r#"{"markets":["BTC-USD"],"cancelAll":false}"#)],
            "POST",
            "/api/v1/user/order/massCancel",
        ),
        private(
            "mass_cancel",
            &[("body", r#"{"cancelAll":true}"#)],
            "POST",
            "/api/v1/user/order/massCancel",
        ),
        private(
            "set_deadman_switch",
            &[("countdownTime", "0")],
            "POST",
            "/api/v1/user/deadmanswitch?countdownTime=0",
        ),
    ]);
}

#[test]
fn mass_cancel_forwards_body_verbatim() {
    let expected = json!({"orderIds": [1, 2], "externalOrderIds": ["a"]});
    let (result, requests) = run(
        Kind::Private,
        "mass_cancel",
        vec![("body".to_string(), expected.to_string())],
    );
    result.expect("mass cancel");
    let [request] = requests.as_slice() else {
        panic!("expected one request, got {requests:?}");
    };
    let sent: Value = serde_json::from_str(body(request)).expect("JSON body");
    assert_eq!(sent, expected);
}

fn presigned_order(order_type: &str, time_in_force: &str) -> Value {
    json!({
        "id": "order-1",
        "market": "BTC-USD",
        "type": order_type,
        "side": "BUY",
        "qty": "0.001",
        "price": "10000",
        "reduceOnly": false,
        "postOnly": false,
        "timeInForce": time_in_force,
        "expiryEpochMillis": now_ms() + 3_600_000,
        "fee": "0.00025",
        "nonce": "1",
        "selfTradeProtectionLevel": "ACCOUNT",
        "cancelId": "previous-order",
        "settlement": {
            "signature": {"r": "0x1", "s": "0x2"},
            "starkKey": "0x3",
            "collateralPosition": "4"
        }
    })
}

#[test]
fn presigned_order_body_is_posted_verbatim() {
    for (name, order_type, tif) in [
        ("place_order", "LIMIT", "GTT"),
        ("create_order", "MARKET", "IOC"),
    ] {
        let order = presigned_order(order_type, tif);
        let (result, requests) = run(
            Kind::Private,
            name,
            vec![("body".to_string(), order.to_string())],
        );
        result.expect("pre-signed order");
        let [request] = requests.as_slice() else {
            panic!("{name}: expected one request, got {requests:?}");
        };
        assert_eq!(request_line(request), "POST /api/v1/user/order HTTP/1.1");
        let sent: Value = serde_json::from_str(body(request)).expect("JSON body");
        assert_eq!(sent, order, "{name}");
    }
}

#[test]
fn auto_signed_limit_order_fetches_market_and_fee_then_posts() {
    let params = pairs(&[
        ("market", "BTC-USD"),
        ("side", "BUY"),
        ("qty", "0.001"),
        ("price", "10000"),
        ("post_only", "true"),
        ("nonce", "123"),
    ]);
    let (result, requests) = run(Kind::Private, "place_limit_order", params);
    result.expect("signed limit order");
    let lines: Vec<&str> = requests
        .iter()
        .map(|request| request_line(request))
        .collect();
    assert_eq!(
        lines,
        vec![
            "GET /api/v1/info/markets?market=BTC-USD HTTP/1.1",
            "GET /api/v1/user/fees?market=BTC-USD HTTP/1.1",
            "POST /api/v1/user/order HTTP/1.1",
        ]
    );
    let sent: Value = serde_json::from_str(body(&requests[2])).expect("JSON body");
    assert_eq!(sent["market"], "BTC-USD");
    assert_eq!(sent["type"], "LIMIT");
    assert_eq!(sent["side"], "BUY");
    assert_eq!(sent["postOnly"], true);
    // Post-only orders must use the maker fee rate from GET /user/fees.
    assert_eq!(sent["fee"], "0.0001");
    assert_eq!(sent["nonce"], "123");
    assert!(
        sent["settlement"]["signature"]["r"]
            .as_str()
            .is_some_and(|value| value.starts_with("0x"))
    );
}

#[test]
fn sign_create_order_returns_signature_without_posting() {
    let params = pairs(&[
        ("product_symbol", "BTC-USD"),
        ("side", "SELL"),
        ("qty", "0.001"),
        ("price", "10000"),
        ("fee", "0.0005"),
    ]);
    let (result, requests) = run(Kind::Private, "sign_create_order", params);
    let data = result.expect("signed order");
    let lines: Vec<&str> = requests
        .iter()
        .map(|request| request_line(request))
        .collect();
    // An explicit fee skips the fee lookup; only the market config is fetched.
    assert_eq!(
        lines,
        vec!["GET /api/v1/info/markets?market=BTC-USD HTTP/1.1"]
    );
    assert_eq!(data["order"]["side"], "SELL");
    assert_eq!(data["order"]["fee"], "0.0005");
    assert!(
        data["orderHash"]
            .as_str()
            .is_some_and(|value| value.starts_with("0x"))
    );
}

#[test]
fn unsafe_requests_are_rejected_before_any_request() {
    // Auto-signing only supports LIMIT orders.
    assert_rejected_offline(
        Kind::Private,
        "place_order",
        pairs(&[
            ("market", "BTC-USD"),
            ("side", "BUY"),
            ("qty", "1"),
            ("price", "1"),
            ("type", "MARKET"),
        ]),
    );
    // FOK is not an Extended time-in-force.
    assert_rejected_offline(
        Kind::Private,
        "place_limit_order",
        pairs(&[
            ("market", "BTC-USD"),
            ("side", "BUY"),
            ("qty", "1"),
            ("price", "1"),
            ("time_in_force", "FOK"),
        ]),
    );
    // Both market aliases at once are ambiguous.
    assert_rejected_offline(
        Kind::Private,
        "place_limit_order",
        pairs(&[
            ("market", "BTC-USD"),
            ("product_symbol", "BTC-USD"),
            ("side", "BUY"),
            ("qty", "1"),
            ("price", "1"),
        ]),
    );
    // MARKET pre-signed bodies must be IOC.
    assert_rejected_offline(
        Kind::Private,
        "place_order",
        vec![(
            "body".to_string(),
            presigned_order("MARKET", "GTT").to_string(),
        )],
    );
    // Empty mass-cancel bodies are rejected.
    assert_rejected_offline(
        Kind::Private,
        "mass_cancel",
        vec![("body".to_string(), "{}".to_string())],
    );
    assert_rejected_offline(
        Kind::Private,
        "mass_cancel",
        vec![("body".to_string(), r#"{"orderIds":[0]}"#.to_string())],
    );
    // Cancels require a positive id.
    assert_rejected_offline(Kind::Private, "cancel_order", pairs(&[("id", "0")]));
    assert_rejected_offline(Kind::Private, "cancel_order_by_external_id", Vec::new());
    // Internal transfers between the same account are rejected.
    assert_rejected_offline(
        Kind::Private,
        "submit_internal_transfer",
        vec![(
            "body".to_string(),
            json!({"fromAccount": 1, "toAccount": 1, "amount": "1"}).to_string(),
        )],
    );
    // Path segments cannot be injected.
    assert_rejected_offline(
        Kind::Private,
        "get_order_by_external_id",
        pairs(&[("externalId", "../x")]),
    );
    assert_rejected_offline(
        Kind::Public,
        "get_order_book",
        pairs(&[("market", "BTC-USD/../x")]),
    );
    // Unsupported candle intervals and unknown names never reach the wire.
    assert_rejected_offline(
        Kind::Public,
        "get_candles",
        pairs(&[("market", "BTC-USD"), ("interval", "1m"), ("limit", "1")]),
    );
    assert_rejected_offline(Kind::Private, "create_withdrawal", Vec::new());
    assert_rejected_offline(Kind::Public, "get_unknown", Vec::new());
}

#[test]
fn update_leverage_patches_documented_body() {
    let (result, requests) = run(
        Kind::Private,
        "update_leverage",
        pairs(&[("market", "BTC-USD"), ("leverage", "10")]),
    );
    result.expect("update leverage");
    let [request] = requests.as_slice() else {
        panic!("expected one request, got {requests:?}");
    };
    assert_eq!(
        request_line(request),
        "PATCH /api/v1/user/leverage HTTP/1.1"
    );
    assert!(
        request
            .to_ascii_lowercase()
            .contains("x-api-key: extended-key")
    );
    let sent: Value = serde_json::from_str(body(request)).expect("JSON body");
    assert_eq!(sent, json!({"market": "BTC-USD", "leverage": "10"}));

    for params in [
        pairs(&[("market", "BTC-USD")]),
        pairs(&[("leverage", "10")]),
        pairs(&[("market", "BTC-USD"), ("leverage", "0")]),
        pairs(&[("market", "BTC-USD"), ("leverage", "abc")]),
        pairs(&[("market", "BTC-USD"), ("leverage", "10"), ("extra", "1")]),
    ] {
        assert_rejected_offline(Kind::Private, "update_leverage", params);
    }
}

const MARKET_JSON: &str = r#"{"name":"BTC-USD","l2Config":{"collateralId":"0x555344430000000000000000000000","collateralResolution":1000000,"syntheticId":"0x4254432d31300000000000000000000","syntheticResolution":100000000}}"#;

#[test]
fn market_json_skips_markets_lookup_when_signing() {
    for key in ["market_json", "marketJson"] {
        let params = pairs(&[
            ("market", "BTC-USD"),
            ("side", "BUY"),
            ("qty", "0.001"),
            ("price", "10000"),
            ("fee", "0.0005"),
            (key, MARKET_JSON),
        ]);
        let (result, requests) = run(Kind::Private, "sign_create_order", params);
        let data = result.expect("signed order from market_json");
        assert!(
            requests.is_empty(),
            "{key}: unexpected lookups {requests:?}"
        );
        assert_eq!(data["order"]["market"], "BTC-USD");
        assert!(
            data["orderHash"]
                .as_str()
                .is_some_and(|value| value.starts_with("0x"))
        );
    }
    // A response-shaped payload (`{"data": [...]}`) is accepted too.
    let wrapped = format!(r#"{{"status":"OK","data":[{MARKET_JSON}]}}"#);
    let (result, requests) = run(
        Kind::Private,
        "sign_create_order",
        vec![
            ("market".to_string(), "BTC-USD".to_string()),
            ("side".to_string(), "SELL".to_string()),
            ("qty".to_string(), "0.001".to_string()),
            ("price".to_string(), "10000".to_string()),
            ("fee".to_string(), "0.0005".to_string()),
            ("market_json".to_string(), wrapped),
        ],
    );
    result.expect("signed order from wrapped market_json");
    assert!(requests.is_empty());
}

#[test]
fn market_json_for_another_market_or_duplicated_is_rejected_offline() {
    let order = |market: &str, extra: &[(&str, &str)]| {
        let mut params = pairs(&[
            ("market", market),
            ("side", "BUY"),
            ("qty", "0.001"),
            ("price", "10000"),
            ("fee", "0.0005"),
        ]);
        params.extend(pairs(extra));
        params
    };
    assert_rejected_offline(
        Kind::Private,
        "sign_create_order",
        order("ETH-USD", &[("market_json", MARKET_JSON)]),
    );
    assert_rejected_offline(
        Kind::Private,
        "place_limit_order",
        order("BTC-USD", &[("market_json", "not json")]),
    );
    assert_rejected_offline(
        Kind::Private,
        "place_limit_order",
        order(
            "BTC-USD",
            &[("market_json", MARKET_JSON), ("marketJson", MARKET_JSON)],
        ),
    );
}

#[test]
fn portfolio_and_interest_routes_preserve_account_filters() {
    assert_cases(&[
        private(
            "get_account_equity_history",
            &[
                ("accountId", "1000"),
                ("accountId", "1001"),
                ("interval", "WEEK"),
            ],
            "GET",
            "/api/v1/portfolio/charts/equities?accountId=1000&accountId=1001&interval=WEEK",
        ),
        private(
            "get_account_pnl_history",
            &[
                ("accountId", "1000"),
                ("accountId", "1001"),
                ("interval", "WEEK"),
                ("pnlType", "TOTAL_PNL"),
                ("instrumentType", "SPOT"),
            ],
            "GET",
            "/api/v1/portfolio/charts/pnl?accountId=1000&accountId=1001&interval=WEEK&pnlType=TOTAL_PNL&instrumentType=SPOT",
        ),
        private(
            "get_account_pnl_percentage_history",
            &[
                ("accountId", "1000"),
                ("accountId", "1001"),
                ("interval", "WEEK"),
                ("pnlType", "TOTAL_PNL"),
                ("priceMarket", "BTC-USD"),
                ("priceMarket", "ETH-USD"),
                ("instrumentType", "SPOT"),
            ],
            "GET",
            "/api/v1/portfolio/charts/pnl/percentage?accountId=1000&accountId=1001&interval=WEEK&pnlType=TOTAL_PNL&priceMarket=BTC-USD&priceMarket=ETH-USD&instrumentType=SPOT",
        ),
        private(
            "get_cumulative_account_pnl_history",
            &[
                ("accountId", "1000"),
                ("accountId", "1001"),
                ("interval", "WEEK"),
                ("pnlType", "TOTAL_PNL"),
                ("instrumentType", "SPOT"),
            ],
            "GET",
            "/api/v1/portfolio/charts/pnl/cumulative?accountId=1000&accountId=1001&interval=WEEK&pnlType=TOTAL_PNL&instrumentType=SPOT",
        ),
        private(
            "get_cumulative_account_pnl_percentage_history",
            &[
                ("accountId", "1000"),
                ("accountId", "1001"),
                ("interval", "WEEK"),
                ("pnlType", "TOTAL_PNL"),
                ("priceMarket", "BTC-USD"),
                ("priceMarket", "ETH-USD"),
                ("instrumentType", "SPOT"),
            ],
            "GET",
            "/api/v1/portfolio/charts/pnl/cumulative/percentage?accountId=1000&accountId=1001&interval=WEEK&pnlType=TOTAL_PNL&priceMarket=BTC-USD&priceMarket=ETH-USD&instrumentType=SPOT",
        ),
        private(
            "get_account_vault_equity_history",
            &[
                ("accountId", "1000"),
                ("accountId", "1001"),
                ("interval", "WEEK"),
            ],
            "GET",
            "/api/v1/portfolio/charts/vault-equities?accountId=1000&accountId=1001&interval=WEEK",
        ),
        private(
            "get_account_max_drawdown_history",
            &[
                ("accountId", "1000"),
                ("accountId", "1001"),
                ("interval", "WEEK"),
            ],
            "GET",
            "/api/v1/portfolio/charts/max-drawdown?accountId=1000&accountId=1001&interval=WEEK",
        ),
        private(
            "get_account_funding_chart",
            &[
                ("accountId", "1000"),
                ("accountId", "1001"),
                ("interval", "WEEK"),
                ("market", "BTC-USD"),
                ("market", "ETH-USD"),
            ],
            "GET",
            "/api/v1/portfolio/charts/funding?accountId=1000&accountId=1001&interval=WEEK&market=BTC-USD&market=ETH-USD",
        ),
        private(
            "get_account_portfolio_summary",
            &[
                ("accountId", "1000"),
                ("accountId", "1001"),
                ("interval", "WEEK"),
                ("instrumentType", "SPOT"),
            ],
            "GET",
            "/api/v1/portfolio/accounts/summary?accountId=1000&accountId=1001&interval=WEEK&instrumentType=SPOT",
        ),
        private(
            "get_account_performance",
            &[
                ("accountId", "1000"),
                ("accountId", "1001"),
                ("interval", "WEEK"),
                ("marketType", "PERPS"),
            ],
            "GET",
            "/api/v1/portfolio/accounts/performance?accountId=1000&accountId=1001&interval=WEEK&marketType=PERPS",
        ),
        private(
            "get_account_funding_stats",
            &[
                ("accountId", "1000"),
                ("accountId", "1001"),
                ("interval", "WEEK"),
                ("market", "BTC-USD"),
                ("market", "ETH-USD"),
            ],
            "GET",
            "/api/v1/portfolio/funding/stats?accountId=1000&accountId=1001&interval=WEEK&market=BTC-USD&market=ETH-USD",
        ),
        private(
            "get_account_funding_history",
            &[
                ("accountId", "1000"),
                ("accountId", "1001"),
                ("interval", "WEEK"),
                ("market", "BTC-USD"),
                ("market", "ETH-USD"),
                ("cursor", "1"),
                ("limit", "50"),
            ],
            "GET",
            "/api/v1/portfolio/funding/history?accountId=1000&accountId=1001&interval=WEEK&market=BTC-USD&market=ETH-USD&cursor=1&limit=50",
        ),
        public(
            "get_interest_rate_curves_history",
            &[("interval", "WEEK")],
            "GET",
            "/api/v1/interest/info/rate-curves?interval=WEEK",
        ),
        public(
            "get_latest_interest_rate_curve",
            &[],
            "GET",
            "/api/v1/interest/info/latest-rate-curves",
        ),
        private(
            "get_interest_key_metrics",
            &[("accountId", "1000"), ("accountId", "1001")],
            "GET",
            "/api/v1/interest/key-metrics?accountId=1000&accountId=1001",
        ),
        private(
            "get_interest_daily_metrics",
            &[
                ("accountId", "1000"),
                ("accountId", "1001"),
                ("interval", "WEEK"),
            ],
            "GET",
            "/api/v1/interest/daily-metrics?accountId=1000&accountId=1001&interval=WEEK",
        ),
        private(
            "get_interest_payment_chart",
            &[
                ("accountId", "1000"),
                ("accountId", "1001"),
                ("interval", "WEEK"),
                ("bucket", "DAILY"),
            ],
            "GET",
            "/api/v1/interest/payment-chart?accountId=1000&accountId=1001&interval=WEEK&bucket=DAILY",
        ),
        private(
            "get_interest_payments_history",
            &[
                ("accountId", "1000"),
                ("accountId", "1001"),
                ("interval", "WEEK"),
            ],
            "GET",
            "/api/v1/interest/payments?accountId=1000&accountId=1001&interval=WEEK",
        ),
    ]);
}

#[test]
fn remaining_vault_and_rewards_routes() {
    assert_cases(&[
        public(
            "get_vault_performance",
            &[("interval", "WEEK")],
            "GET",
            "/api/v1/vault/public/performance?interval=WEEK",
        ),
        public(
            "get_vault_summary",
            &[],
            "GET",
            "/api/v1/vault/public/summary",
        ),
        private(
            "get_earned_points",
            &[],
            "GET",
            "/api/v1/user/rewards/earned",
        ),
        private(
            "get_points_leaderboard_stats",
            &[],
            "GET",
            "/api/v1/user/rewards/leaderboard/stats",
        ),
    ]);
}
