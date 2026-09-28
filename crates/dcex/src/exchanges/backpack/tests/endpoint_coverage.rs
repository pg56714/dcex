//! Offline route coverage for every Backpack dispatch name.
//!
//! Each case sends one request through `public_request` / `private_request`
//! against a local one-shot HTTP server and asserts the HTTP method and the
//! REST path from the official Backpack OpenAPI spec
//! (https://docs.backpack.exchange/). Private cases also verify the ED25519
//! `X-Signature` against the documented signing instruction, so a wrong
//! instruction name fails the test.

use std::time::Duration;
use std::{
    io::{Read, Write},
    net::TcpListener,
    thread,
};

use base64::Engine;
use ed25519_dalek::{Signature, SigningKey, Verifier};
use serde_json::Value;

use crate::exchanges::backpack::BackpackClient;
use crate::exchanges::backpack::params::signature_payload_from_value;
use crate::exchanges::backpack::signing::signature_message;

struct Case {
    name: &'static str,
    /// `None` for public endpoints, otherwise the documented instruction.
    instruction: Option<&'static str>,
    params: &'static [(&'static str, &'static str)],
    route: &'static str,
}

const fn public(
    name: &'static str,
    params: &'static [(&'static str, &'static str)],
    route: &'static str,
) -> Case {
    Case {
        name,
        instruction: None,
        params,
        route,
    }
}

const fn private(
    name: &'static str,
    instruction: &'static str,
    params: &'static [(&'static str, &'static str)],
    route: &'static str,
) -> Case {
    Case {
        name,
        instruction: Some(instruction),
        params,
        route,
    }
}

const PERP: &str = "BTC-USDC-SWAP";
const SPOT: &str = "BTC-USDC-SPOT";
const RFQ: &str = "AAPL.US-USDC-RFQ";

const PUBLIC_CASES: &[Case] = &[
    public("get_prediction_events", &[], "GET /api/v1/prediction"),
    public("get_prediction_tags", &[], "GET /api/v1/prediction/tags"),
    public("get_vaults", &[], "GET /api/v1/vaults"),
    public(
        "get_vault_history",
        &[("interval", "1d")],
        "GET /api/v1/vaults/history?interval=1d",
    ),
    public("get_assets", &[], "GET /api/v1/assets"),
    public("get_collateral", &[], "GET /api/v1/collateral"),
    public(
        "get_borrow_lend_markets",
        &[],
        "GET /api/v1/borrowLend/markets",
    ),
    public(
        "get_borrow_lend_market_history",
        &[("interval", "1d"), ("symbol", "USDC")],
        "GET /api/v1/borrowLend/markets/history?interval=1d&symbol=USDC",
    ),
    public("get_borrow_lend_apy", &[], "GET /api/v1/borrowLend/apy"),
    public(
        "get_borrow_lend_liquidation_price",
        // base64 of {"quantity":"1","side":"Borrow","symbol":"BTC"}
        &[(
            "borrow",
            "eyJxdWFudGl0eSI6IjEiLCJzaWRlIjoiQm9ycm93Iiwic3ltYm9sIjoiQlRDIn0=",
        )],
        "GET /api/v1/borrowLend/position/liquidationPrice",
    ),
    public(
        "get_markets",
        &[("marketType", "PERP")],
        "GET /api/v1/markets?marketType=PERP",
    ),
    public(
        "get_market",
        &[("product_symbol", PERP)],
        "GET /api/v1/market?symbol=BTC_USDC_PERP",
    ),
    public(
        "get_order_book_depth",
        &[("product_symbol", SPOT), ("limit", "5")],
        "GET /api/v1/depth?symbol=BTC_USDC",
    ),
    public("get_market_sessions", &[], "GET /api/v1/market-sessions"),
    public("get_market_holidays", &[], "GET /api/v1/market-holidays"),
    public("get_securities", &[], "GET /api/v1/securities"),
    public(
        "get_mark_prices",
        &[("product_symbol", PERP)],
        "GET /api/v1/markPrices?symbol=BTC_USDC_PERP",
    ),
    public(
        "get_open_interest",
        &[("product_symbol", PERP)],
        "GET /api/v1/openInterest?symbol=BTC_USDC_PERP",
    ),
    public(
        "get_funding_rates",
        &[("product_symbol", PERP)],
        "GET /api/v1/fundingRates?symbol=BTC_USDC_PERP",
    ),
    public(
        "get_klines",
        &[
            ("product_symbol", PERP),
            ("interval", "1m"),
            ("startTime", "1700000000"),
        ],
        "GET /api/v1/klines?symbol=BTC_USDC_PERP&interval=1m&startTime=1700000000",
    ),
    public(
        "get_ticker",
        &[("product_symbol", PERP)],
        "GET /api/v1/ticker?symbol=BTC_USDC_PERP",
    ),
    public("get_tickers", &[], "GET /api/v1/tickers"),
    public("get_status", &[], "GET /api/v1/status"),
    public("ping", &[], "GET /api/v1/ping"),
    public("get_time", &[], "GET /api/v1/time"),
    public("get_wallets", &[], "GET /api/v1/wallets"),
    public(
        "get_recent_trades",
        &[("product_symbol", PERP)],
        "GET /api/v1/trades?symbol=BTC_USDC_PERP",
    ),
    public(
        "get_historical_trades",
        &[("product_symbol", PERP)],
        "GET /api/v1/trades/history?symbol=BTC_USDC_PERP",
    ),
];

const PRIVATE_CASES: &[Case] = &[
    // Cases retained from the independent Python endpoint wire suite.
    private(
        "submit_rfq_quote",
        "quoteSubmit",
        &[
            ("rfqId", "rfq-1"),
            ("bidPrice", "100.000000000000000001"),
            ("askPrice", "101"),
        ],
        "POST /api/v1/rfq/quote",
    ),
    private(
        "create_withdrawal",
        "withdraw",
        &[
            ("address", "offline-address"),
            ("blockchain", "Solana"),
            ("symbol", "USDC"),
            ("quantity", "1.000000000000000001"),
        ],
        "POST /wapi/v1/capital/withdrawals",
    ),
    private(
        "execute_borrow_lend",
        "borrowLendExecute",
        &[("quantity", "1"), ("side", "Borrow"), ("symbol", "BTC")],
        "POST /api/v1/borrowLend",
    ),
    private(
        "vault_mint",
        "vaultMint",
        &[("vaultId", "1"), ("symbol", "USDC"), ("quantity", "1")],
        "POST /api/v1/vault/mint",
    ),
    private(
        "vault_redeem",
        "vaultRedeemRequest",
        &[("all", "true"), ("vaultId", "1")],
        "POST /api/v1/vault/redeem",
    ),
    private(
        "vault_redeem_cancel",
        "vaultRedeemCancel",
        &[("vaultId", "1")],
        "DELETE /api/v1/vault/redeem",
    ),
    private(
        "get_vault_pending_redeems",
        "vaultPendingRedeemsQuery",
        &[("vaultId", "1")],
        "GET /api/v1/vault/redeems/pending?vaultId=1",
    ),
    private(
        "get_vault_nav",
        "vaultNavQuery",
        &[],
        "GET /api/v1/vault/nav",
    ),
    private(
        "create_strategy",
        "strategyCreate",
        &[
            ("product_symbol", "BTC-USDC-SWAP"),
            ("side", "Bid"),
            ("strategyType", "Scheduled"),
            ("quantity", "1"),
            ("duration", "60000"),
            ("interval", "10000"),
        ],
        "POST /api/v1/strategy",
    ),
    private(
        "get_open_strategy",
        "strategyQuery",
        &[("product_symbol", "BTC-USDC-SWAP"), ("strategyId", "100")],
        "GET /api/v1/strategy",
    ),
    private(
        "cancel_strategy",
        "strategyCancel",
        &[
            ("product_symbol", "BTC-USDC-SWAP"),
            ("clientStrategyId", "7"),
        ],
        "DELETE /api/v1/strategy",
    ),
    private(
        "get_open_strategies",
        "strategyQueryAll",
        &[
            ("product_symbol", "BTC-USDC-SWAP"),
            ("strategyType", "Scheduled"),
        ],
        "GET /api/v1/strategies",
    ),
    private(
        "cancel_open_strategies",
        "strategyCancelAll",
        &[("product_symbol", "BTC-USDC-SWAP")],
        "DELETE /api/v1/strategies",
    ),
    private(
        "get_strategy_history",
        "strategyHistoryQueryAll",
        &[("limit", "10"), ("marketType", "PERP")],
        "GET /wapi/v1/history/strategies",
    ),
    // Account.
    private("get_account", "accountQuery", &[], "GET /api/v1/account"),
    private(
        "update_account",
        "accountUpdate",
        &[("leverageLimit", "5"), ("autoLend", "true")],
        "PATCH /api/v1/account",
    ),
    private(
        "get_max_borrow_quantity",
        "maxBorrowQuantity",
        &[("symbol", "USDC")],
        "GET /api/v1/account/limits/borrow?symbol=USDC",
    ),
    private(
        "get_max_order_quantity",
        "maxOrderQuantity",
        &[("symbol", "BTC_USDC_PERP"), ("side", "Bid")],
        "GET /api/v1/account/limits/order?symbol=BTC_USDC_PERP&side=Bid",
    ),
    private(
        "get_max_withdrawal_quantity",
        "maxWithdrawalQuantity",
        &[("symbol", "USDC")],
        "GET /api/v1/account/limits/withdrawal?symbol=USDC",
    ),
    // Borrow lend.
    private(
        "get_borrow_lend_positions",
        "borrowLendPositionQuery",
        &[],
        "GET /api/v1/borrowLend/positions",
    ),
    private(
        "get_borrow_history",
        "borrowHistoryQueryAll",
        &[("limit", "10")],
        "GET /wapi/v1/history/borrowLend?limit=10",
    ),
    private(
        "get_interest_history",
        "interestHistoryQueryAll",
        &[("limit", "10")],
        "GET /wapi/v1/history/interest?limit=10",
    ),
    private(
        "get_borrow_position_history",
        "borrowPositionHistoryQueryAll",
        &[("limit", "10")],
        "GET /wapi/v1/history/borrowLend/positions?limit=10",
    ),
    // Capital.
    private("get_balances", "balanceQuery", &[], "GET /api/v1/capital"),
    private(
        "convert_dust",
        "convertDust",
        &[("symbol", "SOL")],
        "POST /api/v1/account/convertDust",
    ),
    private(
        "get_private_collateral",
        "collateralQuery",
        &[],
        "GET /api/v1/capital/collateral",
    ),
    private(
        "get_deposits",
        "depositQueryAll",
        &[("limit", "10")],
        "GET /wapi/v1/capital/deposits?limit=10",
    ),
    private(
        "get_deposit_address",
        "depositAddressQuery",
        &[("blockchain", "Solana")],
        "GET /wapi/v1/capital/deposit/address?blockchain=Solana",
    ),
    private(
        "get_withdrawals",
        "withdrawalQueryAll",
        &[("limit", "10")],
        "GET /wapi/v1/capital/withdrawals?limit=10",
    ),
    private(
        "get_dust_conversion_history",
        "dustHistoryQueryAll",
        &[("limit", "10")],
        "GET /wapi/v1/history/dust?limit=10",
    ),
    private(
        "get_settlement_history",
        "settlementHistoryQueryAll",
        &[("limit", "10")],
        "GET /wapi/v1/history/settlement?limit=10",
    ),
    // Orders.
    private(
        "get_open_order",
        "orderQuery",
        &[("product_symbol", PERP), ("orderId", "111")],
        "GET /api/v1/order?orderId=111&symbol=BTC_USDC_PERP",
    ),
    private(
        "place_order",
        "orderExecute",
        &[
            ("product_symbol", PERP),
            ("side", "Bid"),
            ("orderType", "Limit"),
            ("quantity", "1"),
            ("price", "100"),
        ],
        "POST /api/v1/order",
    ),
    private(
        "place_market_order",
        "orderExecute",
        &[("product_symbol", PERP), ("side", "Ask"), ("quantity", "1")],
        "POST /api/v1/order",
    ),
    private(
        "place_limit_order",
        "orderExecute",
        &[
            ("product_symbol", SPOT),
            ("side", "Bid"),
            ("quantity", "1"),
            ("price", "100"),
        ],
        "POST /api/v1/order",
    ),
    private(
        "cancel_order",
        "orderCancel",
        &[("product_symbol", PERP), ("orderId", "111")],
        "DELETE /api/v1/order",
    ),
    private(
        "place_batch_orders",
        "orderExecute",
        &[(
            "orders",
            r#"[{"product_symbol":"BTC-USDC-SWAP","side":"Bid","orderType":"Limit","quantity":"1","price":"100"},{"product_symbol":"BTC-USDC-SWAP","side":"Ask","orderType":"Limit","quantity":"1","price":"200"}]"#,
        )],
        "POST /api/v1/orders",
    ),
    private(
        "get_open_orders",
        "orderQueryAll",
        &[("product_symbol", PERP)],
        "GET /api/v1/orders?symbol=BTC_USDC_PERP",
    ),
    private(
        "cancel_open_orders",
        "orderCancelAll",
        &[("product_symbol", PERP)],
        "DELETE /api/v1/orders",
    ),
    private(
        "get_fill_history",
        "fillHistoryQueryAll",
        &[("limit", "10")],
        "GET /wapi/v1/history/fills?limit=10",
    ),
    private(
        "get_order_history",
        "orderHistoryQueryAll",
        &[("limit", "10")],
        "GET /wapi/v1/history/orders?limit=10",
    ),
    // Positions.
    private(
        "get_open_positions",
        "positionQuery",
        &[],
        "GET /api/v1/position",
    ),
    private(
        "get_funding_payments",
        "fundingHistoryQueryAll",
        &[("limit", "10")],
        "GET /wapi/v1/history/funding?limit=10",
    ),
    private(
        "get_position_history",
        "positionHistoryQueryAll",
        &[("limit", "10")],
        "GET /wapi/v1/history/position?limit=10",
    ),
    // RFQ.
    private("get_rfqs", "rfqQuery", &[], "GET /api/v1/rfqs"),
    private(
        "submit_rfq",
        "rfqSubmit",
        &[("product_symbol", RFQ), ("side", "Bid"), ("quantity", "1")],
        "POST /api/v1/rfq",
    ),
    private(
        "accept_rfq_quote",
        "quoteAccept",
        &[("rfqId", "r1"), ("quoteId", "q1")],
        "POST /api/v1/rfq/accept",
    ),
    private(
        "refresh_rfq",
        "rfqRefresh",
        &[("rfqId", "r1")],
        "POST /api/v1/rfq/refresh",
    ),
    private(
        "cancel_rfq",
        "rfqCancel",
        &[("rfqId", "r1")],
        "POST /api/v1/rfq/cancel",
    ),
    private(
        "get_rfq_history",
        "rfqHistoryQueryAll",
        &[("limit", "10")],
        "GET /wapi/v1/history/rfq?limit=10",
    ),
    private(
        "get_quote_history",
        "quoteHistoryQueryAll",
        &[("limit", "10")],
        "GET /wapi/v1/history/quote?limit=10",
    ),
    private(
        "get_rfq_fill_history",
        "rfqFillHistoryQueryAll",
        &[("limit", "10")],
        "GET /wapi/v1/history/rfq/fill?limit=10",
    ),
    private(
        "get_quote_fill_history",
        "quoteFillHistoryQueryAll",
        &[("limit", "10")],
        "GET /wapi/v1/history/quote/fill?limit=10",
    ),
];

fn one_shot_server(response: &'static str) -> (String, thread::JoinHandle<String>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let address = listener.local_addr().expect("address");
    let handle = thread::spawn(move || {
        let (mut stream, _) = listener.accept().expect("accept");
        let mut buffer = [0u8; 8192];
        let mut request = String::new();
        while !request.contains("\r\n\r\n") {
            let size = stream.read(&mut buffer).expect("read headers");
            assert!(size > 0, "request ended before headers were complete");
            request.push_str(&String::from_utf8_lossy(&buffer[..size]));
        }
        let content_length = request
            .lines()
            .find_map(|line| {
                line.to_ascii_lowercase()
                    .strip_prefix("content-length: ")
                    .and_then(|value| value.trim().parse::<usize>().ok())
            })
            .unwrap_or(0);
        while request.split("\r\n\r\n").nth(1).map_or(0, str::len) < content_length {
            let size = stream.read(&mut buffer).expect("read body");
            assert!(size > 0, "request ended before the declared body length");
            request.push_str(&String::from_utf8_lossy(&buffer[..size]));
        }
        let head = format!(
            "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n",
            response.len()
        );
        stream.write_all(head.as_bytes()).expect("write head");
        stream.write_all(response.as_bytes()).expect("write body");
        request
    });
    (format!("http://{address}"), handle)
}

fn secret() -> String {
    base64::engine::general_purpose::STANDARD.encode([b'1'; 32])
}

fn client(base_url: String) -> BackpackClient {
    BackpackClient::with_base_url(
        Some(base64::engine::general_purpose::STANDARD.encode([b'2'; 32])),
        Some(secret()),
        5_000,
        Duration::from_secs(2),
        base_url,
    )
    .expect("client")
}

async fn run_case(case: &Case, response: &'static str) -> String {
    let (base_url, handle) = one_shot_server(response);
    let client = client(base_url);
    let params = case
        .params
        .iter()
        .map(|(key, value)| ((*key).to_string(), (*value).to_string()))
        .collect::<Vec<_>>();
    let result = if case.instruction.is_some() {
        client.private_request(case.name, params).await
    } else {
        client.public_request(case.name, params).await
    };
    if let Err(error) = result {
        panic!("{} failed: {error}", case.name);
    }
    handle.join().expect("server")
}

fn header<'a>(request: &'a str, name: &str) -> Option<&'a str> {
    let head = request.split("\r\n\r\n").next().unwrap_or_default();
    head.lines().skip(1).find_map(|line| {
        let (key, value) = line.split_once(':')?;
        key.trim()
            .eq_ignore_ascii_case(name)
            .then_some(value.trim())
    })
}

fn assert_route(case: &Case, request: &str) {
    let request_line = request.lines().next().unwrap_or_default();
    let target = request_line
        .strip_suffix(" HTTP/1.1")
        .unwrap_or(request_line);
    let route_path = case.route.split('?').next().unwrap_or(case.route);
    let target_path = target.split('?').next().unwrap_or(target);
    assert_eq!(
        target_path, route_path,
        "{} sent `{request_line}`, expected `{}`",
        case.name, case.route
    );
    if let Some((_, expected_query)) = case.route.split_once('?') {
        let query = target.split_once('?').map_or("", |(_, query)| query);
        for pair in expected_query.split('&') {
            assert!(
                query.split('&').any(|actual| actual == pair),
                "{} query `{query}` is missing `{pair}`",
                case.name
            );
        }
    }
}

fn assert_signed_with_instruction(case: &Case, request: &str) {
    let instruction = case.instruction.expect("private case");
    let signature = header(request, "X-Signature")
        .unwrap_or_else(|| panic!("{} is missing X-Signature", case.name));
    let timestamp = header(request, "X-Timestamp").expect("X-Timestamp");
    let window = header(request, "X-Window")
        .expect("X-Window")
        .parse::<u64>()
        .expect("window");
    assert!(header(request, "X-API-Key").is_some(), "{}", case.name);

    let target = request.lines().next().unwrap_or_default();
    let body = request.split("\r\n\r\n").nth(1).unwrap_or_default();
    let payload = if body.is_empty() {
        let query = target
            .strip_suffix(" HTTP/1.1")
            .and_then(|target| target.split_once('?'))
            .map_or("", |(_, query)| query);
        let pairs = url::form_urlencoded::parse(query.as_bytes())
            .into_owned()
            .collect::<Vec<_>>();
        if pairs.is_empty() {
            Vec::new()
        } else {
            vec![pairs]
        }
    } else {
        let value: Value = serde_json::from_str(body)
            .unwrap_or_else(|error| panic!("{} body is not JSON ({error}): {body}", case.name));
        signature_payload_from_value(&value)
    };
    let message = signature_message(instruction, &payload, timestamp, window);
    let signing_key = SigningKey::from_bytes(&[b'1'; 32]);
    let bytes = base64::engine::general_purpose::STANDARD
        .decode(signature)
        .expect("signature base64");
    let signature = Signature::from_slice(&bytes).expect("signature bytes");
    assert!(
        signing_key
            .verifying_key()
            .verify(message.as_bytes(), &signature)
            .is_ok(),
        "{} was not signed with instruction `{instruction}`",
        case.name
    );
}

#[tokio::test]
async fn every_public_dispatch_name_hits_documented_route() {
    for case in PUBLIC_CASES {
        let request = run_case(case, "{}").await;
        assert_route(case, &request);
        assert!(
            header(&request, "X-Signature").is_none(),
            "{} public request must not be signed",
            case.name
        );
    }
}

#[tokio::test]
async fn every_private_dispatch_name_hits_documented_route_and_instruction() {
    for case in PRIVATE_CASES {
        let request = run_case(case, "{}").await;
        assert_route(case, &request);
        assert_signed_with_instruction(case, &request);
    }
}

#[tokio::test]
async fn batch_orders_sign_one_instruction_chunk_per_order() {
    let case = PRIVATE_CASES
        .iter()
        .find(|case| case.name == "place_batch_orders")
        .expect("case");
    let request = run_case(case, "[]").await;
    let body: Value =
        serde_json::from_str(request.split("\r\n\r\n").nth(1).expect("body")).expect("JSON");
    let orders = body.as_array().expect("batch body is an array");
    assert_eq!(orders.len(), 2);
    for order in orders {
        assert_eq!(order["symbol"], "BTC_USDC_PERP");
        assert!(order.get("product_symbol").is_none());
    }
    let payload = signature_payload_from_value(&body);
    assert_eq!(payload.len(), 2, "each order is its own signed chunk");
}

#[tokio::test]
async fn limit_helper_defaults_time_in_force_and_market_helper_sets_type() {
    for (name, expected_type, expected_tif) in [
        ("place_limit_order", "Limit", Some("GTC")),
        ("place_market_order", "Market", None),
    ] {
        let case = PRIVATE_CASES
            .iter()
            .find(|case| case.name == name)
            .expect("case");
        let request = run_case(case, "{}").await;
        let body: Value =
            serde_json::from_str(request.split("\r\n\r\n").nth(1).expect("body")).expect("JSON");
        assert_eq!(body["orderType"], expected_type, "{name}");
        assert_eq!(
            body.get("timeInForce").and_then(Value::as_str),
            expected_tif,
            "{name}"
        );
        assert!(body.get("product_symbol").is_none(), "{name}");
    }
}

#[tokio::test]
async fn rfq_constraints_select_session_from_securities() {
    let (base_url, handle) = one_shot_server(
        r#"[{"asset":"AAPL.US","sessions":[{"name":"Regular","minQuantity":"1"}]}]"#,
    );
    let client = client(base_url);
    let response = client
        .public_request(
            "get_rfq_constraints",
            vec![
                ("product_symbol".into(), RFQ.into()),
                ("sessionName".into(), "regular".into()),
            ],
        )
        .await
        .expect("constraints");
    let request = handle.join().expect("server");
    assert!(request.starts_with("GET /api/v1/securities HTTP/1.1"));
    assert_eq!(response.data["asset"], "AAPL.US");
    assert_eq!(response.data["symbol"], "AAPL.US_USDC_RFQ");
    assert_eq!(response.data["session"]["minQuantity"], "1");
}

#[tokio::test]
async fn unknown_dispatch_names_are_rejected_before_network() {
    let client = client("http://127.0.0.1:9".into());
    let error = client
        .public_request("get_not_a_real_endpoint", Vec::new())
        .await
        .expect_err("unknown public name");
    assert!(error.to_string().contains("unsupported"), "{error}");
    let error = client
        .private_request("get_not_a_real_endpoint", Vec::new())
        .await
        .expect_err("unknown private name");
    assert!(error.to_string().contains("unsupported"), "{error}");
}

/// Names declared in `wrappers.rs`, split into its `public [...]` and
/// `private [...]` blocks, so a new wrapper without a route case fails here.
fn declared_wrapper_names() -> (Vec<&'static str>, Vec<&'static str>) {
    let source = include_str!("../wrappers.rs");
    let mut public = Vec::new();
    let mut private = Vec::new();
    let mut section: Option<bool> = None;
    for line in source.lines() {
        let trimmed = line.trim();
        if trimmed.starts_with("public [") {
            section = Some(false);
        } else if trimmed.starts_with("private [") {
            section = Some(true);
        } else if trimmed.starts_with("];") {
            section = None;
        } else if let (Some(is_private), Some((name, _))) = (section, trimmed.split_once('(')) {
            if !name.is_empty() && name.chars().all(|c| c.is_ascii_lowercase() || c == '_') {
                if is_private {
                    private.push(name);
                } else {
                    public.push(name);
                }
            }
        }
    }
    (public, private)
}

/// RFQ dispatch names live in `rfq.rs` and have no typed Rust wrapper, but the
/// Python clients call them by name.
const RFQ_DISPATCH_NAMES: &[&str] = &[
    "get_rfqs",
    "submit_rfq",
    "accept_rfq_quote",
    "refresh_rfq",
    "cancel_rfq",
    "get_rfq_history",
    "get_quote_history",
    "get_rfq_fill_history",
    "get_quote_fill_history",
];

#[test]
fn every_declared_wrapper_and_rfq_name_has_a_route_case() {
    let (public, private) = declared_wrapper_names();
    assert!(
        public.len() > 20 && private.len() > 20,
        "wrapper parse failed"
    );
    let public_cases: Vec<&str> = PUBLIC_CASES.iter().map(|case| case.name).collect();
    let private_cases: Vec<&str> = PRIVATE_CASES.iter().map(|case| case.name).collect();
    let missing_public: Vec<_> = public
        .iter()
        // `get_rfq_constraints` issues two requests and is covered by
        // `rfq_constraints_select_session_from_securities`.
        .filter(|name| **name != "get_rfq_constraints" && !public_cases.contains(name))
        .collect();
    let missing_private: Vec<_> = private
        .iter()
        .chain(RFQ_DISPATCH_NAMES)
        .filter(|name| !private_cases.contains(name))
        .collect();
    assert!(
        missing_public.is_empty(),
        "public wrappers without a route case: {missing_public:?}"
    );
    assert!(
        missing_private.is_empty(),
        "private wrappers without a route case: {missing_private:?}"
    );
}

#[test]
fn documented_websocket_streams_normalize_to_official_names() {
    use crate::exchanges::backpack::websocket::normalize_stream;

    for (input, expected) in [
        ("bookTicker.SOL_USDC", "bookTicker.SOL_USDC"),
        ("depth.SOL_USDC", "depth.SOL_USDC"),
        ("depth.200ms.SOL_USDC", "depth.200ms.SOL_USDC"),
        ("depth.600ms.SOL_USDC", "depth.600ms.SOL_USDC"),
        ("depth.1000ms.SOL_USDC", "depth.1000ms.SOL_USDC"),
        ("kline.1m.SOL_USDC", "kline.1m.SOL_USDC"),
        ("liquidation.SOL_USDC_PERP", "liquidation.SOL_USDC_PERP"),
        ("markPrice.SOL_USDC_PERP", "markPrice.SOL_USDC_PERP"),
        ("ticker.SOL_USDC", "ticker.SOL_USDC"),
        ("openInterest.SOL_USDC_PERP", "openInterest.SOL_USDC_PERP"),
        ("trade.SOL_USDC", "trade.SOL_USDC"),
        ("account.orderUpdate", "account.orderUpdate"),
        (
            "account.orderUpdate.SOL_USDC",
            "account.orderUpdate.SOL_USDC",
        ),
        ("account.positionUpdate", "account.positionUpdate"),
        ("account.rfqUpdate", "account.rfqUpdate"),
    ] {
        assert_eq!(
            normalize_stream(input).unwrap_or_else(|error| panic!("{input}: {error}")),
            expected
        );
    }
}

/// Streams documented under "Streams" in the Backpack OpenAPI spec that were
/// previously rejected. `stockPrice` takes a bare ticker (class shares keep
/// their dot); the docs say exchange symbols such as `AAPL.US` are rejected.
#[test]
fn documented_streams_missing_from_normalizer_are_accepted() {
    use crate::exchanges::backpack::websocket::normalize_stream;

    for (input, expected) in [
        ("account.balanceUpdate", "account.balanceUpdate"),
        ("account.rfq", "account.rfq"),
        ("account.rfq.SOL_USDC_RFQ", "account.rfq.SOL_USDC_RFQ"),
        ("externalTicker.SOL_USDC", "externalTicker.SOL_USDC"),
        (
            "externalTicker.BRK.B.US_USDC",
            "externalTicker.BRK.B.US_USDC",
        ),
        ("stockPrice.AAPL", "stockPrice.AAPL"),
        ("stockPrice.brk.b", "stockPrice.BRK.B"),
    ] {
        assert_eq!(
            normalize_stream(input).unwrap_or_else(|error| panic!("{input}: {error}")),
            expected
        );
    }
    for stream in [
        "account.balanceUpdate.USDC",
        "stockPrice.AAPL.US",
        "stockPrice.AAPL.US_USDC",
        "stockPrice.",
    ] {
        assert!(
            normalize_stream(stream).is_err(),
            "{stream} should be rejected"
        );
    }
}

#[tokio::test]
async fn update_account_patches_documented_settings() {
    let case = PRIVATE_CASES
        .iter()
        .find(|case| case.name == "update_account")
        .expect("case");
    // The documented success response has no body.
    let request = run_case(case, "").await;
    let body: Value =
        serde_json::from_str(request.split("\r\n\r\n").nth(1).expect("body")).expect("JSON");
    assert_eq!(
        body,
        serde_json::json!({"leverageLimit": "5", "autoLend": true})
    );

    let client = client("http://127.0.0.1:9".into());
    for params in [
        Vec::new(),
        vec![("leverageLimit".to_string(), "0".to_string())],
        vec![("autoLend".to_string(), "maybe".to_string())],
        vec![("autoRepay".to_string(), "true".to_string())],
    ] {
        assert!(
            client
                .private_request("update_account", params.clone())
                .await
                .is_err(),
            "{params:?} should be rejected before network"
        );
    }
}

#[tokio::test]
async fn funding_payments_reject_undocumented_subaccount_id() {
    let client = client("http://127.0.0.1:9".into());
    let error = client
        .private_request(
            "get_funding_payments",
            vec![("subaccountId".into(), "7".into())],
        )
        .await
        .expect_err("subaccountId is not documented for this route");
    assert!(error.to_string().contains("subaccountId"), "{error}");
}
