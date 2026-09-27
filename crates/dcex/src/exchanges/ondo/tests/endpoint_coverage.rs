//! Offline route coverage for every Ondo Perps REST dispatch name.
//!
//! Each case sends one dispatch name through `public_request` /
//! `private_request` against a local recording server and asserts that the
//! HTTP method, path, query and JSON body that reach the wire match the
//! official Ondo Perps OpenAPI spec (<https://docs.ondoperps.xyz/api-reference>).

use std::io::{ErrorKind, Read, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

use serde_json::{Value, json};

use super::super::OndoClient;
use crate::http::block_on;

#[derive(Clone, Copy)]
enum Kind {
    Public,
    Private,
}

struct Case {
    kind: Kind,
    name: &'static str,
    params: &'static [(&'static str, &'static str)],
    method: &'static str,
    /// Exact request target (path plus encoded query string).
    target: &'static str,
    /// Expected JSON body, when the call sends one.
    body: Option<&'static str>,
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
        method,
        target,
        body: None,
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
        method,
        target,
        body: None,
    }
}

const fn private_body(
    name: &'static str,
    params: &'static [(&'static str, &'static str)],
    method: &'static str,
    target: &'static str,
    body: &'static str,
) -> Case {
    Case {
        kind: Kind::Private,
        name,
        params,
        method,
        target,
        body: Some(body),
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
                        .set_read_timeout(Some(Duration::from_secs(2)))
                        .expect("read timeout");
                    requests.push(read_request(&mut stream));
                    let body = r#"{"ok":true}"#;
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

fn run(
    kind: Kind,
    name: &'static str,
    params: &[(&str, &str)],
) -> (Result<(), String>, Vec<String>) {
    let (base_url, stop, handle) = multi_request_server();
    let client = OndoClient::with_base_url(
        Some("key-id".to_string()),
        Some("ondoApiSecret_SECRET".to_string()),
        Duration::from_secs(2),
        base_url,
    )
    .expect("client");
    let params: Vec<(String, String)> = params
        .iter()
        .map(|(key, value)| ((*key).to_string(), (*value).to_string()))
        .collect();
    let result = block_on(async move {
        match kind {
            Kind::Public => client.public_request(name, params).await,
            Kind::Private => client.private_request(name, params).await,
        }
    });
    stop.store(true, Ordering::SeqCst);
    let requests = handle.join().expect("server thread");
    (
        result.map(|_| ()).map_err(|error| error.to_string()),
        requests,
    )
}

fn run_case(case: &Case) -> Result<(), String> {
    let name = case.name;
    let (result, requests) = run(case.kind, name, case.params);
    let lines: Vec<&str> = requests
        .iter()
        .map(|request| request.lines().next().unwrap_or_default())
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
    if lines[0] != expected {
        return Err(format!(
            "{name}: expected `{expected}`, wire was `{}`",
            lines[0]
        ));
    }
    let headers = request.to_ascii_lowercase();
    let signed = headers.contains("ondo-key-id: key-id")
        && headers.contains("ondo-sign: ")
        && headers.contains("ondo-timestamp: ");
    match case.kind {
        Kind::Private if !signed => return Err(format!("{name}: private request not signed")),
        Kind::Public if headers.contains("ondo-sign") => {
            return Err(format!("{name}: public request was signed"));
        }
        _ => {}
    }
    let body = request.split_once("\r\n\r\n").map_or("", |(_, body)| body);
    match case.body {
        Some(expected) => {
            let sent: Value = serde_json::from_str(body)
                .map_err(|error| format!("{name}: body is not JSON ({error}): `{body}`"))?;
            let expected: Value = serde_json::from_str(expected).expect("expected JSON");
            if sent != expected {
                return Err(format!("{name}: body {sent} != {expected}"));
            }
        }
        None if !body.is_empty() => {
            return Err(format!("{name}: unexpected body `{body}`"));
        }
        None => {}
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
        "{} of {} Ondo route(s) failed:\n{}",
        failures.len(),
        cases.len(),
        failures.join("\n")
    );
}

fn assert_rejected_offline(kind: Kind, name: &'static str, params: &[(&str, &str)]) {
    let (result, requests) = run(kind, name, params);
    assert!(result.is_err(), "{name} should be rejected: {params:?}");
    assert!(
        requests.is_empty(),
        "{name} reached the wire before validation: {requests:?}"
    );
}

const MARKET: &str = "AAPL-USD.P";

#[test]
fn public_market_data_routes_match_official_paths() {
    assert_cases(&[
        public("get_status", &[], "GET", "/status"),
        Case {
            kind: Kind::Public,
            name: "get_login_challenge",
            params: &[
                (
                    "walletAddress",
                    "0x1111111111111111111111111111111111111111",
                ),
                ("chainId", "1"),
            ],
            method: "POST",
            target: "/v1/auth/erc-4361/login/get_challenge",
            body: Some(
                r#"{"walletAddress":"0x1111111111111111111111111111111111111111","chainId":"1"}"#,
            ),
        },
        Case {
            kind: Kind::Public,
            name: "complete_login_challenge",
            params: &[("id", "challenge1"), ("signature", "signed")],
            method: "POST",
            target: "/v1/auth/erc-4361/login/complete_challenge",
            body: Some(r#"{"id":"challenge1","signature":"signed"}"#),
        },
        private("invalidate_jwt", &[], "GET", "/v1/auth/invalidate_jwt"),
        public("hello", &[], "GET", "/hello"),
        public("ping", &[], "GET", "/hello"),
        public("get_markets", &[], "GET", "/v1/markets"),
        public(
            "get_trades",
            &[("market", MARKET), ("limit", "10")],
            "GET",
            "/v1/perps/trades?market=AAPL-USD.P&limit=10",
        ),
        public(
            "get_recent_trades",
            &[("product_symbol", "BTC-USD-SWAP")],
            "GET",
            "/v1/perps/trades?market=BTC-USD.P",
        ),
        public(
            "get_depth",
            &[("market", MARKET), ("depth", "20")],
            "GET",
            "/v1/perps/depth?market=AAPL-USD.P&depth=20",
        ),
        public(
            "get_order_book_depth",
            &[("market", MARKET)],
            "GET",
            "/v1/perps/depth?market=AAPL-USD.P",
        ),
        public("get_symbol_info", &[], "GET", "/v1/perps/symbol_info"),
        public(
            "get_price_history",
            &[
                ("symbol", MARKET),
                ("resolution", "60"),
                ("from", "1"),
                ("to", "2"),
            ],
            "GET",
            "/v1/perps/history?symbol=AAPL-USD.P&resolution=60&from=1&to=2",
        ),
        public(
            "get_funding_rates",
            &[("market", MARKET)],
            "GET",
            "/v1/perps/funding_rates?market=AAPL-USD.P",
        ),
        public(
            "get_funding_rate_history",
            &[("market", MARKET), ("limit", "5"), ("cursor", "c1")],
            "GET",
            "/v1/perps/funding_rate_history?market=AAPL-USD.P&limit=5&cursor=c1",
        ),
        public("get_mark_prices", &[], "GET", "/v1/perps/mark_prices"),
        public("get_open_interest", &[], "GET", "/v1/perps/open_interest"),
        public("get_volume", &[], "GET", "/v1/perps/volume"),
        public(
            "get_contracts",
            &[("sparkline", "true")],
            "GET",
            "/v1/perps/contracts?sparkline=true",
        ),
    ]);
}

#[test]
fn private_order_routes_match_official_paths() {
    assert_cases(&[
        private(
            "get_orders",
            &[("market", MARKET), ("status", "filled"), ("limit", "10")],
            "GET",
            "/v1/perps/orders?market=AAPL-USD.P&status=filled&limit=10",
        ),
        private(
            "get_orders",
            &[("startTime", "1"), ("endTime", "2")],
            "GET",
            "/v1/perps/orders?startTime=1&endTime=2",
        ),
        private(
            "get_open_orders",
            &[("market", MARKET)],
            "GET",
            "/v1/perps/orders?market=AAPL-USD.P&status=open",
        ),
        private_body(
            "place_order",
            &[
                ("market", "BTC-USD-SWAP"),
                ("side", "buy"),
                ("type", "limit"),
                ("price", "100"),
                ("size", "1"),
                ("timeInForce", "GTC"),
                ("postOnly", "true"),
                ("clientOrderId", "cid-1"),
            ],
            "POST",
            "/v1/perps/orders",
            r#"{"market":"BTC-USD.P","side":"buy","type":"limit","price":"100","size":"1","timeInForce":"GTC","postOnly":true,"clientOrderId":"cid-1"}"#,
        ),
        private_body(
            "place_order",
            &[
                ("market", MARKET),
                ("side", "buy"),
                ("type", "market"),
                ("quoteSize", "50"),
                ("reduceOnly", "false"),
            ],
            "POST",
            "/v1/perps/orders",
            r#"{"market":"AAPL-USD.P","side":"buy","type":"market","quoteSize":"50","reduceOnly":false}"#,
        ),
        private(
            "cancel_all_orders",
            &[("market", MARKET)],
            "DELETE",
            "/v1/perps/orders?market=AAPL-USD.P",
        ),
        private("cancel_open_orders", &[], "DELETE", "/v1/perps/orders"),
        private_body(
            "place_batch_orders",
            &[(
                "orders",
                r#"[{"market":"BTC-USD-SWAP","side":"sell","price":"101","size":"1"},{"market":"AAPL-USD.P","side":"buy","type":"market","size":"2"}]"#,
            )],
            "POST",
            "/v1/perps/orders/batch",
            r#"{"orders":[{"market":"BTC-USD.P","side":"sell","price":"101","size":"1"},{"market":"AAPL-USD.P","side":"buy","type":"market","size":"2"}]}"#,
        ),
        private(
            "batch_cancel_orders",
            &[("orderIDs", "o1")],
            "DELETE",
            "/v1/perps/orders/batch?orderIDs=o1",
        ),
        private_body(
            "place_twap_order",
            &[
                ("market", MARKET),
                ("side", "buy"),
                ("size", "10"),
                ("runningTime", "600"),
                ("frequency", "30"),
                ("reduceOnly", "false"),
            ],
            "POST",
            "/v1/perps/twap/order",
            r#"{"market":"AAPL-USD.P","side":"buy","size":"10","runningTime":600,"frequency":30,"reduceOnly":false}"#,
        ),
        private(
            "get_twap_order",
            &[("orderID", "t1")],
            "GET",
            "/v1/perps/twap/order/t1",
        ),
        private(
            "cancel_twap_order",
            &[("orderID", "t1")],
            "DELETE",
            "/v1/perps/twap/order/t1",
        ),
        private(
            "get_twap_order_fills",
            &[("orderID", "t1")],
            "GET",
            "/v1/perps/twap/order/t1/fills",
        ),
        private(
            "get_running_twap_orders",
            &[("market", MARKET)],
            "GET",
            "/v1/perps/twap/orders/running?market=AAPL-USD.P",
        ),
        private(
            "get_twap_order_history",
            &[("limit", "5")],
            "GET",
            "/v1/perps/twap/orders/history?limit=5",
        ),
        private(
            "get_order",
            &[("orderID", "o1")],
            "GET",
            "/v1/perps/orders/o1",
        ),
        private(
            "cancel_order",
            &[("orderID", "o1")],
            "DELETE",
            "/v1/perps/orders/o1",
        ),
        private(
            "get_fills_by_order",
            &[("orderID", "o1")],
            "GET",
            "/v1/perps/orders/o1/fills",
        ),
        private(
            "export_orders_csv",
            &[("market", MARKET), ("startTime", "1"), ("endTime", "2")],
            "GET",
            "/v1/perps/orders/csv?market=AAPL-USD.P&startTime=1&endTime=2",
        ),
        private(
            "get_fills",
            &[("market", MARKET), ("cursor", "c")],
            "GET",
            "/v1/perps/fills?market=AAPL-USD.P&cursor=c",
        ),
        private(
            "get_fills",
            &[("startTime", "1"), ("endTime", "2")],
            "GET",
            "/v1/perps/fills?startTime=1&endTime=2",
        ),
        private(
            "export_fills_csv",
            &[("startTime", "1")],
            "GET",
            "/v1/perps/fills/csv?startTime=1",
        ),
        private("get_stop_orders", &[], "GET", "/v1/perps/stop_order"),
        private_body(
            "set_stop_order",
            &[
                ("market", MARKET),
                ("positionDirection", "long"),
                ("type", "stopLoss"),
                ("triggerPrice", "90"),
                ("quantity", "1"),
            ],
            "POST",
            "/v1/perps/stop_order",
            r#"{"market":"AAPL-USD.P","positionDirection":"long","type":"stopLoss","triggerPrice":"90","quantity":"1"}"#,
        ),
        private(
            "remove_stop_order",
            &[("market", MARKET), ("type", "takeProfit")],
            "DELETE",
            "/v1/perps/stop_order?market=AAPL-USD.P&type=takeProfit",
        ),
    ]);
}

#[test]
fn private_account_routes_match_official_paths() {
    assert_cases(&[
        private("get_account", &[], "GET", "/v1/account"),
        private("get_open_order_counts", &[], "GET", "/v1/counts/orders"),
        private("get_positions", &[], "GET", "/v1/perps/positions"),
        private("get_balance", &[], "GET", "/v1/perps/balance"),
        private(
            "get_order_summaries",
            &[],
            "GET",
            "/v1/perps/orders_summaries",
        ),
        private("get_portfolio_summary", &[], "GET", "/v1/portfolio/summary"),
        private(
            "get_portfolio_summary_graph",
            &[("range", "7d")],
            "GET",
            "/v1/portfolio/summary/graph?range=7d",
        ),
        private(
            "get_candles",
            &[
                ("market", MARKET),
                ("resolution", "1H"),
                ("from", "1"),
                ("to", "2"),
            ],
            "GET",
            "/v1/perps/candles?market=AAPL-USD.P&resolution=1H&from=1&to=2",
        ),
        private(
            "get_klines",
            &[
                ("product_symbol", "BTC-USD-SWAP"),
                ("resolution", "1D"),
                ("from", "1"),
                ("to", "2"),
            ],
            "GET",
            "/v1/perps/candles?market=BTC-USD.P&resolution=1D&from=1&to=2",
        ),
        private(
            "get_funding_fee_payments",
            &[("market", MARKET), ("limit", "3")],
            "GET",
            "/v1/perps/funding_fees?market=AAPL-USD.P&limit=3",
        ),
        private(
            "get_liquidation_history",
            &[("startTime", "1"), ("endTime", "2")],
            "GET",
            "/v1/perps/liquidation_history?startTime=1&endTime=2",
        ),
        private(
            "get_max_order_size",
            &[("market", MARKET), ("buffer", "0.1")],
            "GET",
            "/v1/perps/max_order_size?market=AAPL-USD.P&buffer=0.1",
        ),
        private("get_leverage", &[], "GET", "/v1/perps/leverage"),
        private(
            "get_leverage",
            &[("product_symbol", "BTC-USD-SWAP")],
            "GET",
            "/v1/perps/leverage?market=BTC-USD.P",
        ),
        private_body(
            "set_leverage",
            &[("market", "BTC-USD-SWAP"), ("leverage", "5")],
            "POST",
            "/v1/perps/leverage",
            r#"{"market":"BTC-USD.P","leverage":"5"}"#,
        ),
    ]);
}

#[test]
fn private_wallet_and_key_routes_match_official_paths() {
    assert_cases(&[
        private("get_deposits", &[], "GET", "/v1/wallet/deposits"),
        private(
            "get_deposit",
            &[("depositID", "d1")],
            "GET",
            "/v1/wallet/deposits/d1",
        ),
        private("get_withdrawals", &[], "GET", "/v1/wallet/withdrawals"),
        private(
            "get_withdrawal",
            &[("withdrawalID", "w1")],
            "GET",
            "/v1/wallet/withdrawals/w1",
        ),
        private(
            "get_withdrawal_limits",
            &[],
            "GET",
            "/v1/wallet/withdrawals/limit",
        ),
        private_body(
            "get_withdrawal_status",
            &[("withdrawal_id", "w1")],
            "POST",
            "/v1/get_withdrawal_status",
            r#"{"withdrawal_id":"w1"}"#,
        ),
        private_body(
            "get_deposit_addresses",
            &[("coins", r#"["USDC"]"#), ("network", "ethereum")],
            "POST",
            "/v1/wallet/deposit_address/list",
            r#"{"coins":["USDC"],"network":"ethereum"}"#,
        ),
        private_body(
            "provision_deposit_address",
            &[
                ("network", "ethereum"),
                ("symbol", "USDC"),
                ("deposit_destination", r#"{"id":"acct","wallet":"margin"}"#),
            ],
            "POST",
            "/v1/provision_address",
            r#"{"network":"ethereum","symbol":"USDC","deposit_destination":{"id":"acct","wallet":"margin"}}"#,
        ),
        private_body(
            "sandbox_deposit",
            &[
                ("amount", "1"),
                ("symbol", "USDC"),
                ("deposit_destination", r#"{"id":"acct","wallet":"main"}"#),
                ("chain_id", "eth-sepolia"),
            ],
            "POST",
            "/v1/sandbox_deposit",
            r#"{"amount":"1","symbol":"USDC","deposit_destination":{"id":"acct","wallet":"main"},"chain_id":"eth-sepolia"}"#,
        ),
        private_body(
            "export_deposits_csv",
            &[("start_time", "1"), ("end_time", "2")],
            "POST",
            "/v1/wallet/deposits/csv",
            r#"{"start_time":1,"end_time":2}"#,
        ),
        private_body(
            "export_withdrawals_csv",
            &[("start_time", "1")],
            "POST",
            "/v1/wallet/withdrawals/csv",
            r#"{"start_time":1}"#,
        ),
        private("get_address_book", &[], "GET", "/v1/wallet/address_book"),
        private_body(
            "edit_address_book_entry",
            &[("withdrawalAddress", "0xabc"), ("addressLabel", "cold")],
            "PUT",
            "/v1/wallet/address_book",
            r#"{"withdrawalAddress":"0xabc","addressLabel":"cold"}"#,
        ),
        private_body(
            "remove_address_book_entry",
            &[("withdrawalAddress", "0xabc")],
            "DELETE",
            "/v1/wallet/address_book",
            r#"{"withdrawalAddress":"0xabc"}"#,
        ),
        private_body(
            "get_address_book_challenge",
            &[
                ("walletAddress", "0x1"),
                ("chainId", "1"),
                ("withdrawalAddress", "0x2"),
            ],
            "POST",
            "/v1/auth/erc-4361/address_book/get_challenge",
            r#"{"walletAddress":"0x1","chainId":"1","withdrawalAddress":"0x2"}"#,
        ),
        private_body(
            "complete_address_book_challenge",
            &[("id", "c1"), ("signature", "0xsig")],
            "POST",
            "/v1/auth/erc-4361/address_book/complete_challenge",
            r#"{"id":"c1","signature":"0xsig"}"#,
        ),
        private("list_api_keys", &[], "GET", "/v1/api_keys"),
        private_body(
            "create_api_key",
            &[("name", "bot"), ("scopes", r#"["trade"]"#)],
            "POST",
            "/v1/api_keys",
            r#"{"name":"bot","scopes":["trade"]}"#,
        ),
        private(
            "delete_api_key",
            &[("apiKeyID", "k1")],
            "DELETE",
            "/v1/api_keys/k1",
        ),
        private_body(
            "set_api_key_ip_whitelist",
            &[("apiKeyID", "k1"), ("ip", "10.0.0.1")],
            "POST",
            "/v1/api_keys/k1/ip_whitelist",
            r#"{"ip":"10.0.0.1"}"#,
        ),
        private_body(
            "remove_api_key_ip_whitelist",
            &[("apiKeyID", "k1"), ("ip", "10.0.0.1")],
            "DELETE",
            "/v1/api_keys/k1/ip_whitelist",
            r#"{"ip":"10.0.0.1"}"#,
        ),
    ]);
}

#[test]
fn unsafe_requests_are_rejected_before_any_request() {
    // Limit orders need price and size; market orders cannot carry a price.
    assert_rejected_offline(
        Kind::Private,
        "place_order",
        &[("market", MARKET), ("side", "buy"), ("size", "1")],
    );
    assert_rejected_offline(
        Kind::Private,
        "place_order",
        &[
            ("market", MARKET),
            ("side", "sell"),
            ("type", "market"),
            ("quoteSize", "10"),
        ],
    );
    assert_rejected_offline(
        Kind::Private,
        "place_order",
        &[
            ("market", MARKET),
            ("side", "BUY"),
            ("price", "1"),
            ("size", "1"),
        ],
    );
    assert_rejected_offline(
        Kind::Private,
        "place_order",
        &[
            ("market", MARKET),
            ("side", "buy"),
            ("price", "1"),
            ("size", "1"),
            ("timeInForce", "FOK"),
        ],
    );
    // Spot product symbols never map onto perps markets.
    assert_rejected_offline(
        Kind::Private,
        "place_order",
        &[
            ("market", "BTC-USD-SPOT"),
            ("side", "buy"),
            ("price", "1"),
            ("size", "1"),
        ],
    );
    // Batch limits are enforced.
    let too_many = format!(
        "[{}]",
        vec![r#"{"market":"AAPL-USD.P","side":"buy","price":"1","size":"1"}"#; 21].join(",")
    );
    let too_many: &'static str = Box::leak(too_many.into_boxed_str());
    assert_rejected_offline(Kind::Private, "place_batch_orders", &[("orders", too_many)]);
    assert_rejected_offline(Kind::Private, "place_batch_orders", &[("orders", "[]")]);
    assert_rejected_offline(Kind::Private, "batch_cancel_orders", &[]);
    // Stop orders and TWAPs require their mandatory fields.
    assert_rejected_offline(
        Kind::Private,
        "set_stop_order",
        &[("market", MARKET), ("type", "stopLoss")],
    );
    assert_rejected_offline(Kind::Private, "remove_stop_order", &[]);
    assert_rejected_offline(
        Kind::Private,
        "place_twap_order",
        &[("market", MARKET), ("side", "buy"), ("size", "1")],
    );
    // Path identifiers cannot inject extra segments.
    assert_rejected_offline(Kind::Private, "cancel_order", &[("orderID", "../all")]);
    assert_rejected_offline(Kind::Private, "get_deposit", &[("depositID", "a/b")]);
    // Undocumented extra parameters are rejected.
    assert_rejected_offline(Kind::Public, "get_markets", &[("market", MARKET)]);
    assert_rejected_offline(Kind::Private, "get_balance", &[("x", "1")]);
    // Withdrawal creation is intentionally unsupported.
    assert_rejected_offline(Kind::Private, "withdraw", &[]);
    // Inverted or non-numeric time windows never reach the wire.
    for name in ["get_orders", "get_fills"] {
        assert_rejected_offline(Kind::Private, name, &[("startTime", "2"), ("endTime", "1")]);
        assert_rejected_offline(Kind::Private, name, &[("startTime", "soon")]);
    }
}

#[test]
fn market_normalization_applies_to_batch_bodies_only_through_market_field() {
    let (result, requests) = run(
        Kind::Private,
        "place_batch_orders",
        &[(
            "orders",
            r#"[{"market":"ETH-USD-SWAP","side":"buy","price":"1","size":"1","takeProfit":{"triggerPrice":"2"}}]"#,
        )],
    );
    result.expect("batch");
    let [request] = requests.as_slice() else {
        panic!("expected one request, got {requests:?}");
    };
    let body: Value =
        serde_json::from_str(request.split_once("\r\n\r\n").expect("body").1).expect("JSON body");
    assert_eq!(
        body,
        json!({"orders": [{
            "market": "ETH-USD.P",
            "side": "buy",
            "price": "1",
            "size": "1",
            "takeProfit": {"triggerPrice": "2"}
        }]})
    );
}
