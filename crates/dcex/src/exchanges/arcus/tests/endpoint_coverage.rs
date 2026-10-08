//! Offline route coverage for every Arcus REST dispatch name.
//!
//! Each case drives one dispatch name through the Perps `public_request` /
//! `private_request` or the Spot router against a local recording server and
//! asserts the HTTP method, path and key query/body fields match the official
//! Arcus API reference (<https://docs.arcus.xyz/api-reference/introduction>).

use std::io::{ErrorKind, Read, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

use ed25519_dalek::SigningKey;
use serde_json::{Value, json};

use super::super::client::{ArcusClient, ArcusSpotClient};
use crate::http::block_on;

const MARKETS: &str = r#"{"markets":[{"marketId":7,"marketDisplayName":"BTC-USD","tickSize":"0.1","stepSize":"0.001","minOrderSize":"0.001","maxOrderSize":"100","minOrderNotional":"1"}]}"#;
const ACK: &str = r#"{"status":"ACK"}"#;
const ADDRESS: &str = "0x4444444444444444444444444444444444444444";
const TOKEN_A: &str = "0x1111111111111111111111111111111111111111";
const TOKEN_B: &str = "0x2222222222222222222222222222222222222222";

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

/// Records every request; `GET /v1/markets` gets market metadata, others ACK.
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
                    let request = read_request(&mut stream);
                    let body = if request.starts_with("GET /v1/markets ") {
                        MARKETS
                    } else {
                        ACK
                    };
                    requests.push(request);
                    let response = format!(
                        "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\
                         Content-Length: {}\r\nConnection: close\r\n\r\n{}",
                        body.len(),
                        body
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

fn perps_client(base_url: &str) -> ArcusClient {
    let key = SigningKey::from_bytes(&[5u8; 32]);
    ArcusClient::new(
        Some(hex::encode(key.verifying_key().to_bytes())),
        Some(hex::encode(key.to_bytes())),
        Some(ADDRESS.to_string()),
        0,
        true,
        Duration::from_secs(10),
    )
    .expect("client")
    .with_base_url(base_url.to_string())
    .expect("base URL")
}

#[derive(Clone, Copy)]
enum Kind {
    Public,
    Private,
    Spot,
}

fn pairs(params: &[(&str, &str)]) -> Vec<(String, String)> {
    params
        .iter()
        .map(|(key, value)| ((*key).to_string(), (*value).to_string()))
        .collect()
}

fn run(
    kind: Kind,
    name: &'static str,
    params: Vec<(String, String)>,
) -> (Result<Value, String>, Vec<String>) {
    let (base_url, stop, handle) = multi_request_server();
    let result = match kind {
        Kind::Public | Kind::Private => {
            let client = perps_client(&base_url);
            block_on(async move {
                match kind {
                    Kind::Public => client.public_request(name, params).await,
                    _ => client.private_request(name, params).await,
                }
            })
        }
        Kind::Spot => {
            let client = ArcusSpotClient::new(None, true, Duration::from_secs(10))
                .expect("spot client")
                .with_base_url(base_url.clone())
                .expect("spot base URL");
            block_on(async move { client.public_request(name, params).await })
        }
    };
    stop.store(true, Ordering::SeqCst);
    let requests = handle.join().expect("server thread");
    (
        result
            .map(|response| response.data)
            .map_err(|error| error.to_string()),
        requests,
    )
}

fn line(request: &str) -> &str {
    request.lines().next().unwrap_or_default()
}

fn body(request: &str) -> Value {
    serde_json::from_str(request.split_once("\r\n\r\n").map_or("", |(_, body)| body))
        .expect("JSON body")
}

fn header<'a>(request: &'a str, name: &str) -> Option<&'a str> {
    let head = request
        .split_once("\r\n\r\n")
        .map_or(request, |(head, _)| head);
    head.lines().find_map(|line| {
        let (key, value) = line.split_once(':')?;
        key.eq_ignore_ascii_case(name).then_some(value.trim())
    })
}

/// (dispatch name, params, exact expected request line target)
#[allow(clippy::type_complexity)]
const PUBLIC_CASES: &[(&str, &[(&str, &str)], &str)] = &[
    (
        "get_leaderboard",
        &[("window", "30d"), ("sortBy", "pnl"), ("limit", "10")],
        "/v1/leaderboard?limit=10&sortBy=pnl&window=30d",
    ),
    ("get_service_info", &[], "/"),
    ("health", &[], "/health"),
    ("get_time", &[], "/v1/time"),
    ("get_markets", &[], "/v1/markets"),
    ("get_fee_tiers", &[], "/v1/feetiers"),
    ("get_commission_rates", &[], "/v1/commissionrates"),
    ("get_spot_assets", &[], "/v1/spotAssets"),
    ("get_compliance", &[], "/v1/compliance"),
    ("get_bbo", &[("market", "BTC-USD")], "/v1/bbo/BTC-USD"),
    (
        "get_l2_orderbook",
        &[("market", "BTC-USD"), ("nLevels", "5")],
        "/v1/l2OrderBook/BTC-USD?nLevels=5",
    ),
    ("get_mid_prices", &[], "/v1/mids"),
    ("get_live_prices", &[], "/v1/prices"),
    (
        "get_trades",
        &[("market", "BTC-USD"), ("limit", "10")],
        "/v1/trades?limit=10&market=BTC-USD",
    ),
    (
        "get_trade",
        &[("trade_id", "123"), ("market", "BTC-USD")],
        "/v1/trade/123?market=BTC-USD",
    ),
    (
        "get_candles",
        &[
            ("market", "BTC-USD"),
            ("timeframe", "1m"),
            ("to", "1700000000000000"),
        ],
        "/v1/candles?market=BTC-USD&timeframe=1m&to=1700000000000000",
    ),
    (
        "get_account",
        &[("address", ADDRESS), ("accountIndex", "0")],
        "/v1/account?accountIndex=0&address=0x4444444444444444444444444444444444444444",
    ),
    (
        "get_account_stats",
        &[("address", ADDRESS)],
        "/v1/account/stats?address=0x4444444444444444444444444444444444444444",
    ),
    (
        "get_positions",
        &[("address", ADDRESS)],
        "/v1/positions?address=0x4444444444444444444444444444444444444444",
    ),
    (
        "get_leverages",
        &[("address", ADDRESS)],
        "/v1/leverages?address=0x4444444444444444444444444444444444444444",
    ),
    (
        "get_open_orders",
        &[("address", ADDRESS)],
        "/v1/openOrders?address=0x4444444444444444444444444444444444444444",
    ),
    (
        "get_order_history",
        &[("address", ADDRESS)],
        "/v1/orders?address=0x4444444444444444444444444444444444444444",
    ),
    (
        "get_order_status",
        &[("order_id", "abc-1")],
        "/v1/order/abc-1",
    ),
    (
        "get_fills",
        &[("address", ADDRESS)],
        "/v1/fills?address=0x4444444444444444444444444444444444444444",
    ),
    (
        "get_fill",
        &[("trade_id", "123"), ("address", ADDRESS)],
        "/v1/fill/123?address=0x4444444444444444444444444444444444444444",
    ),
    (
        "get_transfer_updates",
        &[("address", ADDRESS)],
        "/v1/accountTransferUpdates?address=0x4444444444444444444444444444444444444444",
    ),
    (
        "get_funding",
        &[("address", ADDRESS)],
        "/v1/funding?address=0x4444444444444444444444444444444444444444",
    ),
    (
        "get_interest",
        &[("address", ADDRESS)],
        "/v1/interest?address=0x4444444444444444444444444444444444444444",
    ),
    (
        "get_funding_rates",
        &[("market", "BTC-USD")],
        "/v1/fundingRates?market=BTC-USD",
    ),
    (
        "get_portfolio_history",
        &[("address", ADDRESS)],
        "/v1/portfolio?address=0x4444444444444444444444444444444444444444",
    ),
    (
        "get_rate_limit",
        &[("address", ADDRESS)],
        "/v1/rateLimit?address=0x4444444444444444444444444444444444444444",
    ),
    (
        "get_spot_positions",
        &[("address", ADDRESS)],
        "/v1/spotPositions?address=0x4444444444444444444444444444444444444444",
    ),
    (
        "get_spot_fills",
        &[("address", ADDRESS)],
        "/v1/spotFills?address=0x4444444444444444444444444444444444444444",
    ),
];

#[test]
fn perps_read_routes_match_official_paths() {
    let mut failures = Vec::new();
    for (name, params, target) in PUBLIC_CASES {
        let (result, requests) = run(Kind::Public, name, pairs(params));
        let lines: Vec<&str> = requests.iter().map(|request| line(request)).collect();
        let expected = format!("GET {target} HTTP/1.1");
        match (&result, requests.as_slice()) {
            (Ok(_), [request]) if line(request) == expected => {
                if *name == "get_commission_rates" {
                    assert!(header(request, "x-api-key").is_none());
                    assert!(header(request, "x-signature").is_none());
                } else if header(request, "x-api-key").is_none() {
                    failures.push(format!("{name}: missing X-API-Key"));
                }
            }
            _ => failures.push(format!(
                "{name}: expected `{expected}`, got {result:?} / {lines:?}"
            )),
        }
    }
    assert!(failures.is_empty(), "{}", failures.join("\n"));
}

fn assert_signed_post(request: &str, path: &str) -> Value {
    assert!(
        line(request).starts_with(&format!("POST {path}?address={ADDRESS} ")),
        "{}",
        line(request)
    );
    assert!(header(request, "x-api-key").is_some_and(|value| value.len() == 64));
    assert!(header(request, "x-timestamp").is_some_and(|value| value.parse::<u64>().is_ok()));
    assert!(header(request, "x-signature").is_some_and(|value| value.len() == 128));
    let sent = body(request);
    if let Some(orders) = sent["orders"].as_array() {
        assert!(!orders.is_empty());
        for order in orders {
            assert_eq!(order["address"], ADDRESS);
            assert_eq!(order["accountIndex"], 0);
        }
    } else {
        assert_eq!(sent["address"], ADDRESS);
        assert_eq!(sent["accountIndex"], 0);
    }
    sent
}

#[test]
fn place_order_resolves_market_then_posts_signed_body() {
    let (result, requests) = run(
        Kind::Private,
        "place_order",
        pairs(&[
            ("product_symbol", "BTC-USD-SWAP"),
            ("side", "sell"),
            ("price", "50000.5"),
            ("quantity", "0.002"),
            ("time_in_force", "ALO"),
            ("reduce_only", "true"),
            ("client_order_id", "cid_1"),
        ]),
    );
    result.expect("place order");
    assert_eq!(requests.len(), 2, "{requests:?}");
    assert_eq!(line(&requests[0]), "GET /v1/markets HTTP/1.1");
    let sent = assert_signed_post(&requests[1], "/v1/placeOrder");
    assert_eq!(sent["marketId"], 7);
    assert_eq!(sent["orderSide"], "SELL");
    assert_eq!(sent["orderType"], "LIMIT");
    assert_eq!(sent["timeInForce"], "ALO");
    assert_eq!(sent["reduceOnly"], true);
    assert_eq!(sent["clientId"], "cid_1");
    assert_eq!(sent["price"], "50000.5");
    assert_eq!(sent["quantity"], "0.002");
}

#[test]
fn cancel_order_posts_order_id_kind() {
    let (result, requests) = run(
        Kind::Private,
        "cancel_order",
        pairs(&[("product_symbol", "BTC-USD"), ("order_id", "ord-9")]),
    );
    result.expect("cancel order");
    assert_eq!(requests.len(), 2, "{requests:?}");
    let sent = assert_signed_post(&requests[1], "/v1/cancelOrder");
    assert_eq!(sent["kind"], "orderId");
    assert_eq!(sent["orderId"], "ord-9");
    assert_eq!(sent["marketId"], 7);
}

#[test]
fn cancel_all_and_set_leverage_use_legacy_signed_routes() {
    let (result, requests) = run(Kind::Private, "cancel_all_orders", Vec::new());
    result.expect("cancel all");
    let [request] = requests.as_slice() else {
        panic!("account-wide cancel-all must not look up markets: {requests:?}");
    };
    let sent = assert_signed_post(request, "/v1/cancelAllOrders");
    assert!(sent.get("marketId").is_none());

    let (result, requests) = run(
        Kind::Private,
        "cancel_all_orders",
        pairs(&[
            ("product_symbol", "BTC-USD"),
            ("valid_until", "1900000000000"),
        ]),
    );
    result.expect("market cancel all");
    let sent = assert_signed_post(requests.last().expect("post"), "/v1/cancelAllOrders");
    assert_eq!(sent["marketId"], 7);
    assert_eq!(sent["validUntil"], 1_900_000_000_000u64);

    let (result, requests) = run(
        Kind::Private,
        "set_leverage",
        pairs(&[
            ("product_symbol", "BTC-USD-SWAP"),
            ("leverage", "10"),
            ("isolated", "true"),
        ]),
    );
    result.expect("set leverage");
    let sent = assert_signed_post(requests.last().expect("post"), "/v1/setLeverage");
    assert_eq!(sent["marketId"], 7);
    assert_eq!(sent["leverage"], 10);
    assert_eq!(sent["isolated"], true);
}

#[test]
fn batch_place_and_modify_sign_every_item() {
    let good_til = (SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("time")
        .as_micros() as u64
        + 40 * 86_400 * 1_000_000)
        .to_string();
    let orders = json!([
        {"product_symbol": "BTC-USD", "side": "BUY", "price": "100", "quantity": "0.01"},
        {"product_symbol": "BTC-USD", "side": "SELL", "price": "200", "quantity": "0.01", "reduce_only": true}
    ]);
    let (result, requests) = run(
        Kind::Private,
        "batch_place_orders",
        vec![("orders".to_string(), orders.to_string())],
    );
    result.expect("batch place");
    let sent = body(requests.last().expect("post"));
    assert!(
        line(requests.last().unwrap())
            .starts_with(&format!("POST /v1/batchPlaceOrders?address={ADDRESS} "))
    );
    let items = sent["orders"].as_array().expect("orders");
    assert_eq!(items.len(), 2);
    assert_eq!(items[0]["orderSide"], "BUY");
    assert_eq!(items[1]["reduceOnly"], true);
    assert!(items.iter().all(|item| {
        item["signature"]
            .as_str()
            .is_some_and(|value| value.len() == 128)
    }));

    let modifies = json!([{
        "product_symbol": "BTC-USD", "side": "BUY", "price": "101", "quantity": "0.02",
        "good_til_time": good_til, "time_in_force": "GTT", "reduce_only": false, "order_id": "o-1"
    }]);
    let (result, requests) = run(
        Kind::Private,
        "batch_modify_orders",
        vec![("modifies".to_string(), modifies.to_string())],
    );
    result.expect("batch modify");
    let request = requests.last().expect("post");
    assert!(line(request).starts_with(&format!("POST /v1/batchModifyOrders?address={ADDRESS} ")));
    let sent = body(request);
    assert_eq!(sent["modifies"][0]["orderId"], "o-1");
    assert_eq!(sent["modifies"][0]["side"], "BUY");
}

#[test]
fn internal_transfer_posts_wallet_signed_body_without_api_headers() {
    let transfer = json!({
        "ethereumAddress": ADDRESS,
        "fromAccountIndex": 0,
        "toAccountIndex": 1,
        "amount": "1000000",
        "nonce": "1718644999000",
        "signature": {"r": format!("0x{}", "ab".repeat(32)), "s": format!("0x{}", "cd".repeat(32)), "v": "0x1b"}
    });
    let (result, requests) = run(
        Kind::Private,
        "submit_internal_transfer",
        vec![("signed_transfer_json".to_string(), transfer.to_string())],
    );
    result.expect("transfer");
    let [request] = requests.as_slice() else {
        panic!("expected one request, got {requests:?}");
    };
    assert_eq!(line(request), "POST /v1/transfer HTTP/1.1");
    assert!(header(request, "x-signature").is_none());
    assert_eq!(body(request), transfer);
}

#[test]
fn spot_router_routes_match_official_paths() {
    #[allow(clippy::type_complexity)]
    let cases: &[(&str, Vec<(String, String)>, &str)] = &[
        ("health", Vec::new(), "/health"),
        ("get_tokens", Vec::new(), "/v1/tokens"),
        (
            "get_price",
            pairs(&[
                ("sellToken", TOKEN_A),
                ("buyToken", TOKEN_B),
                ("sellAmount", "1000"),
            ]),
            "/v1/price",
        ),
        (
            "get_quote",
            pairs(&[
                ("sellToken", TOKEN_A),
                ("buyToken", TOKEN_B),
                ("sellAmount", "1000"),
                ("taker", ADDRESS),
                ("slippageBps", "50"),
            ]),
            "/v1/quote",
        ),
    ];
    for (name, params, path) in cases {
        let (result, requests) = run(Kind::Spot, name, params.clone());
        result.unwrap_or_else(|error| panic!("{name}: {error}"));
        let [request] = requests.as_slice() else {
            panic!("{name}: expected one request, got {requests:?}");
        };
        let target = line(request).split(' ').nth(1).unwrap_or_default();
        assert_eq!(target.split('?').next(), Some(*path), "{name}");
        assert!(line(request).starts_with("GET "), "{name}");
        for (key, value) in params {
            assert!(
                target.contains(&format!("{key}={value}")),
                "{name}: {key} missing from {target}"
            );
        }
    }
}

fn assert_rejected_offline(kind: Kind, name: &'static str, params: Vec<(String, String)>) {
    let (result, requests) = run(kind, name, params.clone());
    assert!(result.is_err(), "{name} should be rejected: {params:?}");
    assert!(
        requests
            .iter()
            .all(|request| line(request).starts_with("GET /v1/markets ")),
        "{name} sent a non-lookup request before validation: {requests:?}"
    );
}

#[test]
fn unsafe_orders_are_rejected_before_any_state_changing_request() {
    // MARKET orders must be IOC.
    assert_rejected_offline(
        Kind::Private,
        "place_order",
        pairs(&[
            ("product_symbol", "BTC-USD"),
            ("side", "BUY"),
            ("order_type", "MARKET"),
            ("price", "100"),
            ("quantity", "0.01"),
        ]),
    );
    // Price must align with tickSize and quantity with stepSize.
    assert_rejected_offline(
        Kind::Private,
        "place_order",
        pairs(&[
            ("product_symbol", "BTC-USD"),
            ("side", "BUY"),
            ("price", "100.05"),
            ("quantity", "0.01"),
        ]),
    );
    assert_rejected_offline(
        Kind::Private,
        "place_order",
        pairs(&[
            ("product_symbol", "BTC-USD"),
            ("side", "BUY"),
            ("price", "100"),
            ("quantity", "0.0015"),
        ]),
    );
    // Orders above maxOrderSize or below minOrderNotional are rejected.
    assert_rejected_offline(
        Kind::Private,
        "place_order",
        pairs(&[
            ("product_symbol", "BTC-USD"),
            ("side", "BUY"),
            ("price", "100"),
            ("quantity", "101"),
        ]),
    );
    assert_rejected_offline(
        Kind::Private,
        "place_order",
        pairs(&[
            ("product_symbol", "BTC-USD"),
            ("side", "BUY"),
            ("price", "0.1"),
            ("quantity", "0.001"),
        ]),
    );
    // Undocumented keys are rejected instead of being silently dropped from the signed body.
    for (name, key) in [
        ("place_order", "post_only"),
        ("place_order", "stp_mode"),
        ("modify_order", "order_type"),
    ] {
        let mut params = pairs(&[
            ("product_symbol", "BTC-USD"),
            ("side", "BUY"),
            ("price", "100"),
            ("quantity", "0.01"),
            (key, "true"),
        ]);
        if name == "modify_order" {
            params.extend(pairs(&[
                ("order_id", "1"),
                ("time_in_force", "GTT"),
                ("reduce_only", "false"),
                ("good_til_time", "99999999999999999"),
            ]));
        }
        assert_rejected_offline(Kind::Private, name, params);
    }
    // Modify must identify exactly one order.
    assert_rejected_offline(
        Kind::Private,
        "modify_order",
        pairs(&[
            ("product_symbol", "BTC-USD"),
            ("side", "BUY"),
            ("price", "100"),
            ("quantity", "0.01"),
            ("time_in_force", "GTT"),
            ("reduce_only", "false"),
            ("good_til_time", "99999999999999999"),
        ]),
    );
    // Leverage bounds, dead-man switch window and batch limits.
    assert_rejected_offline(
        Kind::Private,
        "set_leverage",
        pairs(&[("product_symbol", "BTC-USD"), ("leverage", "0")]),
    );
    assert_rejected_offline(Kind::Private, "schedule_cancel", pairs(&[("time", "1")]));
    assert_rejected_offline(
        Kind::Private,
        "batch_place_orders",
        pairs(&[("orders", "[]")]),
    );
    // Transfers between the same account index are rejected.
    assert_rejected_offline(
        Kind::Private,
        "submit_internal_transfer",
        vec![(
            "signed_transfer_json".to_string(),
            json!({"ethereumAddress": ADDRESS, "fromAccountIndex": 1, "toAccountIndex": 1})
                .to_string(),
        )],
    );
    // Path identifiers cannot inject additional segments.
    assert_rejected_offline(
        Kind::Public,
        "get_order_status",
        pairs(&[("order_id", "../x")]),
    );
    assert_rejected_offline(Kind::Public, "get_bbo", pairs(&[("market", "BTC/USD")]));
    // Spot router validates addresses and distinct tokens.
    assert_rejected_offline(
        Kind::Spot,
        "get_price",
        pairs(&[
            ("sellToken", TOKEN_A),
            ("buyToken", TOKEN_A),
            ("sellAmount", "1"),
        ]),
    );
    // Withdrawals are intentionally unsupported.
    assert_rejected_offline(Kind::Private, "withdraw", Vec::new());
    assert_rejected_offline(Kind::Public, "get_unknown", Vec::new());
}

#[test]
fn tpsl_groupings_sign_each_leg_with_the_documented_operation() {
    for grouping in ["partialTpsl", "positionTpsl", "entryTpsl"] {
        let quantity = if grouping == "positionTpsl" {
            "0"
        } else {
            "0.01"
        };
        let mut orders = vec![
            json!({"product_symbol":"BTC-USD","side":"SELL","price":"100","quantity":quantity,"tpsl_type":"TAKE_PROFIT","stop_price":"110","reduce_only":true}),
            json!({"product_symbol":"BTC-USD","side":"SELL","price":"100","quantity":quantity,"tpsl_type":"STOP_LOSS","stop_price":"90","reduce_only":true}),
        ];
        if grouping == "entryTpsl" {
            orders.insert(
                0,
                json!({"product_symbol":"BTC-USD","side":"BUY","price":"100","quantity":"0.01"}),
            );
        }
        let (result, requests) = run(
            Kind::Private,
            "batch_place_orders",
            vec![
                ("orders".into(), serde_json::to_string(&orders).unwrap()),
                ("grouping".into(), grouping.into()),
            ],
        );
        result.expect(grouping);
        let sent = assert_signed_post(requests.last().unwrap(), "/v1/batchPlaceOrders");
        assert_eq!(sent["grouping"], grouping);
        let key = SigningKey::from_bytes(&[5; 32]).verifying_key();
        for (index, order) in sent["orders"].as_array().unwrap().iter().enumerate() {
            let entry = grouping == "entryTpsl" && index == 0;
            let canonical = json!({"ad":ADDRESS,"ai":0,"ct":order["timestamp"],
                "g":order["goodTilTime"].as_str().unwrap().parse::<u64>().unwrap()*1000,
                "m":7,"op":if entry {1} else {4},"p":1000,
                "q":if grouping == "positionTpsl" {0} else {10},
                "r":if entry {0} else {1},"s":if entry {0} else {1},"t":0,"v":1});
            let signature = ed25519_dalek::Signature::from_slice(
                &hex::decode(order["signature"].as_str().unwrap()).unwrap(),
            )
            .unwrap();
            key.verify_strict(&serde_json::to_vec(&canonical).unwrap(), &signature)
                .expect("typed signature");
            if !entry {
                assert_eq!(order["quantity"], quantity);
                assert!(order["stopPrice"].is_string());
            }
        }
    }
}

#[test]
fn invalid_tpsl_groups_never_submit_orders() {
    assert_rejected_offline(
        Kind::Private,
        "place_order",
        pairs(&[
            ("product_symbol", "BTC-USD"),
            ("side", "SELL"),
            ("price", "100"),
            ("quantity", "0.01"),
            ("tpsl_type", "STOP_LOSS"),
            ("stop_price", "90"),
        ]),
    );
    let leg = json!({"product_symbol":"BTC-USD","side":"SELL","price":"100","quantity":"0.01","tpsl_type":"STOP_LOSS","stop_price":"90","reduce_only":true});
    for (group, orders) in [
        ("positionTpsl", json!([leg.clone()])),
        ("partialTpsl", json!([leg.clone(), leg.clone()])),
        ("entryTpsl", json!([leg.clone()])),
        ("orderTpsl", json!([leg])),
    ] {
        assert_rejected_offline(
            Kind::Private,
            "batch_place_orders",
            vec![
                ("orders".into(), orders.to_string()),
                ("grouping".into(), group.into()),
            ],
        );
    }
}

#[test]
fn wallet_key_administration_preserves_scope_and_caller_signature() {
    let signed = serde_json::json!({"address":format!("0x{}","44".repeat(20)),"publicKey":"33".repeat(32),"apiWalletName":"trade","accountIndex":255,"nonce":"nonce1","signature":{"r":"11".repeat(32),"s":"22".repeat(32),"v":"1b"}});
    for (name, path) in [
        ("create_api_key_signed", "/v1/createApiKey"),
        ("revoke_api_key_signed", "/v1/revokeApiKey"),
    ] {
        let (result, requests) = run(
            Kind::Private,
            name,
            vec![("body".into(), signed.to_string())],
        );
        assert!(result.is_ok(), "{result:?}");
        assert_eq!(requests.len(), 1);
        assert_eq!(line(&requests[0]), format!("POST {path} HTTP/1.1"));
        assert_eq!(body(&requests[0]), signed);
        assert!(header(&requests[0], "x-api-key").is_none());
        assert!(header(&requests[0], "x-signature").is_none());
    }
    let (result, requests) = run(Kind::Public, "get_api_keys", vec![]);
    assert!(result.is_ok(), "{result:?}");
    assert!(!line(&requests[0]).contains("accountIndex"));
    assert!(header(&requests[0], "x-api-key").is_none());
    let (result, requests) = run(
        Kind::Public,
        "get_api_keys",
        pairs(&[("accountIndex", "255")]),
    );
    assert!(result.is_err());
    assert!(requests.is_empty());
}

#[test]
fn metadata_routes_and_preference_signature_are_exact() {
    for (name, params, target) in [
        (
            "get_market_metadata",
            vec![("market", "BTC-USD")],
            "/v1/api-meta/markets?market=BTC-USD",
        ),
        ("get_market_overview", vec![], "/v1/api-meta/overview"),
        (
            "get_spot_market_overview",
            vec![],
            "/v1/api-meta/spot/overview",
        ),
        (
            "get_user_preferences",
            vec![],
            "/v1/api-meta/userPreferences?address=0x4444444444444444444444444444444444444444",
        ),
        (
            "get_metadata_candles",
            vec![
                ("market", "BTC-USD"),
                ("timeframe", "1m"),
                ("to", "1700000060"),
                ("countback", "10"),
            ],
            "/v1/api-meta/candles?countback=10&market=BTC-USD&timeframe=1m&to=1700000060",
        ),
    ] {
        let (result, requests) = run(Kind::Public, name, pairs(&params));
        result.unwrap();
        assert_eq!(requests.len(), 1);
        assert_eq!(line(&requests[0]), format!("GET {target} HTTP/1.1"));
    }
    let (result, requests) = run(
        Kind::Private,
        "upsert_user_preferences",
        pairs(&[("preferences", r#"{"colorTheme":"dark"}"#)]),
    );
    result.unwrap();
    let request = &requests[0];
    assert!(line(request).starts_with("PATCH /v1/api-meta/userPreferences "));
    let timestamp = header(request, "X-Timestamp").unwrap();
    let message = format!("{}userPreferences{{\"colorTheme\":\"dark\"}}", timestamp);
    let pubkey: [u8; 32] = hex::decode(header(request, "X-API-Key").unwrap())
        .unwrap()
        .try_into()
        .unwrap();
    let sig = ed25519_dalek::Signature::from_slice(
        &hex::decode(header(request, "X-Signature").unwrap()).unwrap(),
    )
    .unwrap();
    ed25519_dalek::VerifyingKey::from_bytes(&pubkey)
        .unwrap()
        .verify_strict(message.as_bytes(), &sig)
        .unwrap();
    let sig = "11".repeat(64);
    let (result, requests) = run(
        Kind::Private,
        "delete_user_preference_signed",
        pairs(&[
            ("key", "colorTheme"),
            ("timestamp", "1700000000000000000"),
            ("signature", &sig),
        ]),
    );
    result.unwrap();
    assert_eq!(
        line(&requests[0]),
        "DELETE /v1/api-meta/userPreferences?key=colorTheme HTTP/1.1"
    );
    assert_eq!(header(&requests[0], "X-Signature"), Some(sig.as_str()));
}

#[tokio::test]
async fn every_typed_wrapper_reaches_dispatch() {
    // The typed Rust methods must reach the same dispatch Python calls by name.
    let url = crate::exchanges::wrapper_dispatch::instant_server();
    let client = perps_client(&url);
    crate::exchanges::wrapper_dispatch::assert_dispatch(
        "arcus",
        "ArcusClient",
        |name, public, params| {
            let client = &client;
            async move {
                if public {
                    client.public_request(name, params).await
                } else {
                    client.private_request(name, params).await
                }
            }
        },
    )
    .await;
}

#[tokio::test]
async fn every_typed_spot_wrapper_reaches_dispatch() {
    // The typed Rust methods must reach the same dispatch Python calls by name.
    let url = crate::exchanges::wrapper_dispatch::instant_server();
    let client = ArcusSpotClient::new(Some("spot-key".into()), true, Duration::from_secs(10))
        .expect("client")
        .with_base_url(url.clone())
        .expect("base URL");
    crate::exchanges::wrapper_dispatch::assert_dispatch(
        "arcus",
        "ArcusSpotClient",
        |name, public, params| {
            let client = &client;
            async move {
                if public {
                    client.public_request(name, params).await
                } else {
                    client.private_request(name, params).await
                }
            }
        },
    )
    .await;
}
