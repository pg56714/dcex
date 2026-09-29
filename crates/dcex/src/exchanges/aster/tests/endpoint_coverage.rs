//! Offline route coverage for every Aster REST dispatch name.
//!
//! Each case sends one dispatch name through `public_request` /
//! `private_request` against a local recording server and asserts that the
//! HTTP method, path and key parameters that reach the wire match the official
//! Aster V3 spot / futures API documentation
//! (<https://github.com/asterdex/api-docs>).

use std::io::{ErrorKind, Read, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

use super::super::AsterClient;
use crate::http::block_on;

const USER: &str = "0x0000000000000000000000000000000000000001";
const SIGNER: &str = "0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a";
const SPOT: &str = "BTC-USDT-SPOT";
const SWAP: &str = "BTC-USDT-SWAP";

#[test]
fn guarded_cancel_future_nonce_does_not_poison_automatic_nonce() {
    use crate::exchanges::aster::AsterMarket;
    use crate::http::HttpMethod;
    let client = client("http://127.0.0.1:1");
    let before = client.reserve_nonce().unwrap();
    for path in ["/fapi/v3/guardedCancelOrder", "/fapi/v3/guardedBatchOrders"] {
        client
            .build_request(
                HttpMethod::Delete,
                AsterMarket::Futures,
                path,
                vec![],
                true,
                Some(before * 1000),
            )
            .unwrap();
        let after = client.reserve_nonce().unwrap();
        assert!(after > before && after - before < 60_000_000);
    }
}

#[test]
fn withdrawal_signature_chain_requires_positive_decimal_integer() {
    for name in ["withdraw_spot_signed", "withdraw_futures_signed"] {
        for chain in ["56", "0", "-1", "0x38", "1.5", "abc"] {
            let fields = [
                ("chainId", "56"),
                ("asset", "USDT"),
                ("amount", "1"),
                ("fee", "0.1"),
                ("receiver", USER),
                ("userNonce", "123"),
                ("userSignature", "signed-by-wallet"),
                ("signatureChainId", chain),
            ];
            let (result, requests) = run(Kind::Private, name, &fields);
            if chain == "56" {
                result.unwrap();
                assert_eq!(requests.len(), 1);
                assert!(requests[0].contains("signatureChainId=56"));
            } else {
                assert!(result.unwrap_err().contains("signatureChainId"));
                assert!(requests.is_empty());
            }
        }
    }
}

#[derive(Clone, Copy)]
enum Kind {
    Public,
    Private,
}

struct Case<'a> {
    kind: Kind,
    name: &'static str,
    params: &'a [(&'a str, &'a str)],
    method: &'static str,
    path: &'static str,
    /// Substrings that must appear in the query string or form body.
    contains: &'a [&'a str],
}

const fn public<'a>(
    name: &'static str,
    params: &'a [(&'a str, &'a str)],
    method: &'static str,
    path: &'static str,
    contains: &'a [&'a str],
) -> Case<'a> {
    Case {
        kind: Kind::Public,
        name,
        params,
        method,
        path,
        contains,
    }
}

const fn private<'a>(
    name: &'static str,
    params: &'a [(&'a str, &'a str)],
    method: &'static str,
    path: &'static str,
    contains: &'a [&'a str],
) -> Case<'a> {
    Case {
        kind: Kind::Private,
        name,
        params,
        method,
        path,
        contains,
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

/// Accepts every connection until stopped and records each full request.
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
                    let body = r#"{"ok":true,"listenKey":"test-listen-key"}"#;
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

fn client(base_url: &str) -> AsterClient {
    AsterClient::with_base_urls(
        Some(USER.to_string()),
        Some(SIGNER.to_string()),
        Some(format!("0x{}", "11".repeat(32))),
        Duration::from_secs(10),
        base_url.to_string(),
        base_url.to_string(),
    )
    .expect("client")
    .with_prediction_base_url(base_url.into())
    .expect("prediction host")
}

fn run(
    kind: Kind,
    name: &'static str,
    params: &[(&str, &str)],
) -> (Result<(), String>, Vec<String>) {
    let (base_url, stop, handle) = multi_request_server();
    let client = if name.contains("prediction") {
        client("http://127.0.0.1:1")
            .with_prediction_base_url(base_url.clone())
            .expect("prediction host")
    } else {
        client(&base_url)
    };
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
    let line = lines[0];
    let expected_query = format!("{} {}?", case.method, case.path);
    let expected_bare = format!("{} {} ", case.method, case.path);
    if !(line.starts_with(&expected_query) || line.starts_with(&expected_bare)) {
        return Err(format!(
            "{name}: expected `{} {}`, wire was `{line}`",
            case.method, case.path
        ));
    }
    let body = request.split_once("\r\n\r\n").map_or("", |(_, body)| body);
    let payload = format!("{line}\n{body}");
    for needle in case.contains {
        if !payload.contains(needle) {
            return Err(format!("{name}: `{needle}` missing from `{payload}`"));
        }
    }
    let signed = payload.contains("signature=0x");
    match case.kind {
        Kind::Private if !signed => Err(format!("{name}: private request was not signed")),
        Kind::Public if signed => Err(format!("{name}: public request was signed")),
        _ => Ok(()),
    }
}

fn assert_cases(cases: &[Case]) {
    let failures: Vec<String> = cases
        .iter()
        .filter_map(|case| run_case(case).err())
        .collect();
    assert!(
        failures.is_empty(),
        "{} of {} Aster route(s) failed:\n{}",
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

#[test]
fn spot_market_data_routes_match_official_paths() {
    assert_cases(&[
        public("ping_spot", &[], "GET", "/api/v3/ping", &[]),
        public("get_spot_server_time", &[], "GET", "/api/v3/time", &[]),
        public(
            "get_spot_exchange_info",
            &[],
            "GET",
            "/api/v3/exchangeInfo",
            &[],
        ),
        public(
            "get_spot_orderbook",
            &[("product_symbol", SPOT), ("limit", "5")],
            "GET",
            "/api/v3/depth",
            &["symbol=BTCUSDT", "limit=5"],
        ),
        public(
            "get_spot_recent_trades",
            &[("product_symbol", SPOT), ("limit", "10")],
            "GET",
            "/api/v3/trades",
            &["symbol=BTCUSDT", "limit=10"],
        ),
        public(
            "get_spot_historical_trades",
            &[("product_symbol", SPOT), ("fromId", "7")],
            "GET",
            "/api/v3/historicalTrades",
            &["symbol=BTCUSDT", "fromId=7"],
        ),
        public(
            "get_spot_agg_trades",
            &[
                ("product_symbol", SPOT),
                ("startTime", "1"),
                ("endTime", "2"),
            ],
            "GET",
            "/api/v3/aggTrades",
            &["symbol=BTCUSDT", "startTime=1", "endTime=2"],
        ),
        public(
            "get_spot_klines",
            &[("product_symbol", SPOT), ("interval", "1m"), ("limit", "3")],
            "GET",
            "/api/v3/klines",
            &["symbol=BTCUSDT", "interval=1m", "limit=3"],
        ),
        public(
            "get_spot_ticker_24hr",
            &[("product_symbol", SPOT)],
            "GET",
            "/api/v3/ticker/24hr",
            &["symbol=BTCUSDT"],
        ),
        public(
            "get_spot_ticker_price",
            &[],
            "GET",
            "/api/v3/ticker/price",
            &[],
        ),
        public(
            "get_spot_book_ticker",
            &[("product_symbol", SPOT)],
            "GET",
            "/api/v3/ticker/bookTicker",
            &["symbol=BTCUSDT"],
        ),
        public(
            "get_spot_withdraw_fee",
            &[("chainId", "56"), ("asset", "USDT")],
            "GET",
            "/api/v3/aster/withdraw/estimateFee",
            &["chainId=56", "asset=USDT"],
        ),
    ]);
}

#[test]
fn futures_market_data_routes_match_official_paths() {
    assert_cases(&[
        public("ping_futures", &[], "GET", "/fapi/v3/ping", &[]),
        public("get_futures_server_time", &[], "GET", "/fapi/v3/time", &[]),
        public(
            "get_futures_exchange_info",
            &[],
            "GET",
            "/fapi/v3/exchangeInfo",
            &[],
        ),
        public(
            "get_futures_orderbook",
            &[("product_symbol", SWAP), ("limit", "10")],
            "GET",
            "/fapi/v3/depth",
            &["symbol=BTCUSDT", "limit=10"],
        ),
        public(
            "get_futures_recent_trades",
            &[("product_symbol", SWAP)],
            "GET",
            "/fapi/v3/trades",
            &["symbol=BTCUSDT"],
        ),
        public(
            "get_futures_historical_trades",
            &[("product_symbol", SWAP), ("limit", "5")],
            "GET",
            "/fapi/v3/historicalTrades",
            &["symbol=BTCUSDT", "limit=5"],
        ),
        public(
            "get_futures_agg_trades",
            &[("product_symbol", SWAP), ("fromId", "3")],
            "GET",
            "/fapi/v3/aggTrades",
            &["symbol=BTCUSDT", "fromId=3"],
        ),
        public(
            "get_futures_klines",
            &[("product_symbol", SWAP), ("interval", "1h")],
            "GET",
            "/fapi/v3/klines",
            &["symbol=BTCUSDT", "interval=1h"],
        ),
        public(
            "get_futures_index_price_klines",
            &[("pair", "BTCUSDT"), ("interval", "1m")],
            "GET",
            "/fapi/v3/indexPriceKlines",
            &["pair=BTCUSDT", "interval=1m"],
        ),
        public(
            "get_futures_mark_price_klines",
            &[("product_symbol", SWAP), ("interval", "5m")],
            "GET",
            "/fapi/v3/markPriceKlines",
            &["symbol=BTCUSDT", "interval=5m"],
        ),
        public(
            "get_futures_premium_index",
            &[("product_symbol", SWAP)],
            "GET",
            "/fapi/v3/premiumIndex",
            &["symbol=BTCUSDT"],
        ),
        public(
            "get_futures_funding_rate",
            &[("product_symbol", SWAP), ("limit", "100")],
            "GET",
            "/fapi/v3/fundingRate",
            &["symbol=BTCUSDT", "limit=100"],
        ),
        public(
            "get_futures_funding_info",
            &[],
            "GET",
            "/fapi/v3/fundingInfo",
            &[],
        ),
        public(
            "get_futures_ticker_24hr",
            &[("product_symbol", SWAP)],
            "GET",
            "/fapi/v3/ticker/24hr",
            &["symbol=BTCUSDT"],
        ),
        public(
            "get_futures_ticker_price",
            &[("product_symbol", SWAP)],
            "GET",
            "/fapi/v3/ticker/price",
            &["symbol=BTCUSDT"],
        ),
        public(
            "get_futures_book_ticker",
            &[],
            "GET",
            "/fapi/v3/ticker/bookTicker",
            &[],
        ),
        public(
            "get_futures_index_references",
            &[("product_symbol", SWAP)],
            "GET",
            "/fapi/v3/indexreferences",
            &["symbol=BTCUSDT"],
        ),
        public(
            "get_futures_remaining_openable_notional",
            &[("product_symbol", SWAP), ("leverage", "3")],
            "GET",
            "/fapi/v3/remainingOpenableNotionalValue",
            &["symbol=BTCUSDT", "leverage=3"],
        ),
    ]);
}

#[test]
fn spot_account_and_trade_routes_match_official_paths() {
    assert_cases(&[
        private("get_spot_account", &[], "GET", "/api/v3/account", &[]),
        private(
            "get_spot_transaction_history",
            &[("asset", "USDT"), ("type", "TRADE_TARGET"), ("limit", "10")],
            "GET",
            "/api/v3/transactionHistory",
            &["asset=USDT", "type=TRADE_TARGET", "limit=10"],
        ),
        private(
            "transfer_spot_futures",
            &[
                ("amount", "1"),
                ("asset", "USDT"),
                ("clientTranId", "tx-1"),
                ("kindType", "SPOT_FUTURE"),
            ],
            "POST",
            "/api/v3/asset/wallet/transfer",
            &["amount=1", "asset=USDT", "kindType=SPOT_FUTURE"],
        ),
        private(
            "get_spot_commission_rate",
            &[("product_symbol", SPOT)],
            "GET",
            "/api/v3/commissionRate",
            &["symbol=BTCUSDT"],
        ),
        private(
            "place_spot_order",
            &[
                ("product_symbol", SPOT),
                ("side", "BUY"),
                ("type", "LIMIT"),
                ("timeInForce", "GTC"),
                ("quantity", "1"),
                ("price", "100"),
            ],
            "POST",
            "/api/v3/order",
            &["symbol=BTCUSDT", "side=BUY", "type=LIMIT", "price=100"],
        ),
        private(
            "cancel_spot_order",
            &[("product_symbol", SPOT), ("orderId", "11")],
            "DELETE",
            "/api/v3/order",
            &["symbol=BTCUSDT", "orderId=11"],
        ),
        private(
            "get_spot_order",
            &[("product_symbol", SPOT), ("origClientOrderId", "mine")],
            "GET",
            "/api/v3/order",
            &["symbol=BTCUSDT", "origClientOrderId=mine"],
        ),
        private(
            "get_spot_open_order",
            &[("product_symbol", SPOT), ("orderId", "12")],
            "GET",
            "/api/v3/openOrder",
            &["symbol=BTCUSDT", "orderId=12"],
        ),
        private(
            "get_spot_open_orders",
            &[("product_symbol", SPOT)],
            "GET",
            "/api/v3/openOrders",
            &["symbol=BTCUSDT"],
        ),
        private(
            "cancel_all_spot_open_orders",
            &[("product_symbol", SPOT)],
            "DELETE",
            "/api/v3/allOpenOrders",
            &["symbol=BTCUSDT"],
        ),
        private(
            "get_spot_all_orders",
            &[("product_symbol", SPOT), ("limit", "50")],
            "GET",
            "/api/v3/allOrders",
            &["symbol=BTCUSDT", "limit=50"],
        ),
        private(
            "get_spot_user_trades",
            &[("product_symbol", SPOT), ("fromId", "4")],
            "GET",
            "/api/v3/userTrades",
            &["symbol=BTCUSDT", "fromId=4"],
        ),
        private(
            "create_spot_listen_key",
            &[],
            "POST",
            "/api/v3/listenKey",
            &[],
        ),
        private(
            "keep_alive_spot_listen_key",
            &[("listenKey", "abc")],
            "PUT",
            "/api/v3/listenKey",
            &[],
        ),
        private(
            "close_spot_listen_key",
            &[("listenKey", "abc")],
            "DELETE",
            "/api/v3/listenKey",
            &[],
        ),
    ]);
}

#[test]
fn futures_account_routes_match_official_paths() {
    assert_cases(&[
        private(
            "transfer_spot_futures",
            &[
                ("amount", "2"),
                ("asset", "USDT"),
                ("clientTranId", "tx-2"),
                ("kindType", "FUTURE_SPOT"),
                ("market", "futures"),
            ],
            "POST",
            "/fapi/v3/asset/wallet/transfer",
            &[
                "kindType=FUTURE_SPOT",
                "user=0x0000000000000000000000000000000000000001",
            ],
        ),
        private(
            "get_futures_position_mode",
            &[],
            "GET",
            "/fapi/v3/positionSide/dual",
            &[],
        ),
        private(
            "set_futures_position_mode",
            &[("dualSidePosition", "true")],
            "POST",
            "/fapi/v3/positionSide/dual",
            &["dualSidePosition=true"],
        ),
        private("get_futures_stp_mode", &[], "GET", "/fapi/v3/stpMode", &[]),
        private(
            "set_futures_stp_mode",
            &[("stpMode", "EXPIRE_MAKER")],
            "POST",
            "/fapi/v3/stpMode",
            &["stpMode=EXPIRE_MAKER"],
        ),
        private(
            "get_futures_multi_assets_mode",
            &[],
            "GET",
            "/fapi/v3/multiAssetsMargin",
            &[],
        ),
        private(
            "set_futures_multi_assets_mode",
            &[("multiAssetsMargin", "false")],
            "POST",
            "/fapi/v3/multiAssetsMargin",
            &["multiAssetsMargin=false"],
        ),
        private("get_futures_balance", &[], "GET", "/fapi/v3/balance", &[]),
        private(
            "get_futures_account",
            &[],
            "GET",
            "/fapi/v3/accountWithJoinMargin",
            &[],
        ),
        private(
            "modify_futures_position_margin",
            &[("product_symbol", SWAP), ("amount", "5"), ("type", "1")],
            "POST",
            "/fapi/v3/positionMargin",
            &["symbol=BTCUSDT", "amount=5", "type=1"],
        ),
        private(
            "get_futures_position_margin_history",
            &[("product_symbol", SWAP), ("type", "2")],
            "GET",
            "/fapi/v3/positionMargin/history",
            &["symbol=BTCUSDT", "type=2"],
        ),
        private(
            "get_futures_position_risk",
            &[("product_symbol", SWAP)],
            "GET",
            "/fapi/v3/positionRisk",
            &["symbol=BTCUSDT"],
        ),
        private(
            "get_futures_user_trades",
            &[("product_symbol", SWAP), ("limit", "20")],
            "GET",
            "/fapi/v3/userTrades",
            &["symbol=BTCUSDT", "limit=20"],
        ),
        private(
            "get_futures_income",
            &[("incomeType", "FUNDING_FEE")],
            "GET",
            "/fapi/v3/income",
            &["incomeType=FUNDING_FEE"],
        ),
        // The official docs recommend the plural `/fapi/v3/leverageBrackets`;
        // the singular `/fapi/v3/leverageBracket` is documented as deprecated.
        private(
            "get_futures_leverage_bracket",
            &[("product_symbol", SWAP)],
            "GET",
            "/fapi/v3/leverageBrackets",
            &["symbol=BTCUSDT"],
        ),
        private(
            "get_futures_adl_quantile",
            &[],
            "GET",
            "/fapi/v3/adlQuantile",
            &[],
        ),
        private(
            "get_futures_force_orders",
            &[("autoCloseType", "LIQUIDATION"), ("limit", "10")],
            "GET",
            "/fapi/v3/forceOrders",
            &["autoCloseType=LIQUIDATION", "limit=10"],
        ),
        private(
            "get_futures_commission_rate",
            &[("product_symbol", SWAP)],
            "GET",
            "/fapi/v3/commissionRate",
            &["symbol=BTCUSDT"],
        ),
        private(
            "update_futures_mmp",
            &[
                ("product_symbol", SWAP),
                ("windowTimeInMilliseconds", "1000"),
                ("frozenTimeInMilliseconds", "5000"),
                ("qtyLimit", "10"),
            ],
            "POST",
            "/fapi/v3/mmp",
            &[
                "symbol=BTCUSDT",
                "windowTimeInMilliseconds=1000",
                "qtyLimit=10",
            ],
        ),
        private("get_futures_mmp", &[], "GET", "/fapi/v3/mmp", &[]),
        private(
            "delete_futures_mmp",
            &[("product_symbol", SWAP)],
            "DELETE",
            "/fapi/v3/mmp",
            &["symbol=BTCUSDT"],
        ),
        private(
            "reset_futures_mmp",
            &[("product_symbol", SWAP)],
            "POST",
            "/fapi/v3/mmpReset",
            &["symbol=BTCUSDT"],
        ),
        private(
            "create_futures_listen_key",
            &[],
            "POST",
            "/fapi/v3/listenKey",
            &[],
        ),
        private(
            "keep_alive_futures_listen_key",
            &[],
            "PUT",
            "/fapi/v3/listenKey",
            &[],
        ),
        private(
            "close_futures_listen_key",
            &[],
            "DELETE",
            "/fapi/v3/listenKey",
            &[],
        ),
    ]);
}

const BATCH_ORDERS: &str = r#"[{"product_symbol":"BTC-USDT-SWAP","side":"buy","type":"LIMIT","timeInForce":"GTC","quantity":"1","price":"100"}]"#;
const BATCH_AMENDS: &str =
    r#"[{"product_symbol":"BTC-USDT-SWAP","orderId":1,"quantity":"1","price":"101"}]"#;
const OCO_LEGS: &str = r#"[{"strategySubId":1,"securityType":"USDT_FUTURES","product_symbol":"BTC-USDT-SWAP","side":"SELL","type":"TAKE_PROFIT_MARKET","quantity":"1","stopPrice":"120"},{"strategySubId":2,"securityType":"USDT_FUTURES","product_symbol":"BTC-USDT-SWAP","side":"SELL","type":"STOP_MARKET","quantity":"1","stopPrice":"80"}]"#;
const OCO_UPDATE: &str = r#"[{"strategySubId":2,"securityType":"USDT_FUTURES","symbol":"BTCUSDT","side":"SELL","type":"STOP_MARKET","stopPrice":"85"}]"#;

#[test]
fn futures_trade_routes_match_official_paths() {
    assert_cases(&[
        private(
            "place_futures_order",
            &[
                ("product_symbol", SWAP),
                ("side", "SELL"),
                ("type", "STOP_MARKET"),
                ("stopPrice", "90"),
                ("closePosition", "true"),
                ("workingType", "MARK_PRICE"),
            ],
            "POST",
            "/fapi/v3/order",
            &[
                "symbol=BTCUSDT",
                "side=SELL",
                "type=STOP_MARKET",
                "closePosition=true",
            ],
        ),
        private(
            "modify_futures_order",
            &[
                ("product_symbol", SWAP),
                ("orderId", "5"),
                ("quantity", "2"),
                ("price", "99"),
            ],
            "PUT",
            "/fapi/v3/order",
            &["symbol=BTCUSDT", "orderId=5", "quantity=2", "price=99"],
        ),
        private(
            "place_futures_chase_order",
            &[
                ("product_symbol", SWAP),
                ("side", "BUY"),
                ("quantityUnit", "BASE"),
                ("quantity", "0.001"),
            ],
            "POST",
            "/fapi/v3/chase",
            &["symbol=BTCUSDT", "side=BUY", "quantityUnit=BASE"],
        ),
        private(
            "place_futures_batch_orders",
            &[("batchOrders", BATCH_ORDERS)],
            "POST",
            "/fapi/v3/batchOrders",
            &["batchOrders=", "BTCUSDT"],
        ),
        private(
            "modify_futures_batch_orders",
            &[("batchOrders", BATCH_AMENDS)],
            "PUT",
            "/fapi/v3/batchOrders",
            &["batchOrders=", "BTCUSDT"],
        ),
        private(
            "get_futures_order",
            &[("product_symbol", SWAP), ("orderId", "6")],
            "GET",
            "/fapi/v3/order",
            &["symbol=BTCUSDT", "orderId=6"],
        ),
        private(
            "cancel_futures_order",
            &[("product_symbol", SWAP), ("origClientOrderId", "cid")],
            "DELETE",
            "/fapi/v3/order",
            &["symbol=BTCUSDT", "origClientOrderId=cid"],
        ),
        private(
            "cancel_all_futures_open_orders",
            &[("product_symbol", SWAP)],
            "DELETE",
            "/fapi/v3/allOpenOrders",
            &["symbol=BTCUSDT"],
        ),
        private(
            "cancel_futures_batch_orders",
            &[("product_symbol", SWAP), ("orderIdList", "[1,2]")],
            "DELETE",
            "/fapi/v3/batchOrders",
            &["symbol=BTCUSDT", "orderIdList="],
        ),
        private(
            "set_futures_countdown_cancel_all",
            &[("product_symbol", SWAP), ("countdownTime", "60000")],
            "POST",
            "/fapi/v3/countdownCancelAll",
            &["symbol=BTCUSDT", "countdownTime=60000"],
        ),
        private(
            "get_futures_open_order",
            &[("product_symbol", SWAP), ("orderId", "7")],
            "GET",
            "/fapi/v3/openOrder",
            &["symbol=BTCUSDT", "orderId=7"],
        ),
        private(
            "get_futures_open_orders",
            &[],
            "GET",
            "/fapi/v3/openOrders",
            &[],
        ),
        private(
            "get_futures_all_orders",
            &[("product_symbol", SWAP), ("limit", "10")],
            "GET",
            "/fapi/v3/allOrders",
            &["symbol=BTCUSDT", "limit=10"],
        ),
        private(
            "set_futures_leverage",
            &[("product_symbol", SWAP), ("leverage", "10")],
            "POST",
            "/fapi/v3/leverage",
            &["symbol=BTCUSDT", "leverage=10"],
        ),
        private(
            "set_futures_margin_type",
            &[("product_symbol", SWAP), ("marginType", "ISOLATED")],
            "POST",
            "/fapi/v3/marginType",
            &["symbol=BTCUSDT", "marginType=ISOLATED"],
        ),
        private(
            "place_futures_strategy_order",
            &[
                ("strategyType", "OCO"),
                ("clientStrategyId", "tpsl-1"),
                ("subOrderList", OCO_LEGS),
            ],
            "POST",
            "/fapi/v3/placeStrategyOrder",
            &["strategyType=OCO", "subOrderList=", "BTCUSDT"],
        ),
        private(
            "update_futures_strategy_order",
            &[
                ("strategyId", "9"),
                ("strategyType", "OCO"),
                ("subOrderList", OCO_UPDATE),
            ],
            "POST",
            "/fapi/v3/updateStrategyOrder",
            &["strategyId=9", "strategyType=OCO", "subOrderList="],
        ),
        private(
            "get_futures_strategy_open_order",
            &[("strategyId", "9"), ("strategyType", "OCO")],
            "GET",
            "/fapi/v3/strategyOpenOrder",
            &["strategyId=9", "strategyType=OCO"],
        ),
        private(
            "get_futures_strategy_history_order",
            &[("clientStrategyId", "tpsl-1"), ("strategyType", "OTO")],
            "GET",
            "/fapi/v3/strategyHistoryOrder",
            &["clientStrategyId=tpsl-1", "strategyType=OTO"],
        ),
    ]);
}

#[test]
fn single_orders_accept_lowercase_side_like_batch_orders() {
    assert_cases(&[
        private(
            "place_spot_order",
            &[
                ("product_symbol", SPOT),
                ("side", "buy"),
                ("type", "MARKET"),
                ("quantity", "1"),
            ],
            "POST",
            "/api/v3/order",
            &["symbol=BTCUSDT", "side=BUY"],
        ),
        private(
            "place_futures_order",
            &[
                ("product_symbol", SWAP),
                ("side", "sell"),
                ("type", "MARKET"),
                ("quantity", "1"),
            ],
            "POST",
            "/fapi/v3/order",
            &["symbol=BTCUSDT", "side=SELL"],
        ),
        private(
            "place_futures_chase_order",
            &[
                ("product_symbol", SWAP),
                ("side", "Buy"),
                ("quantityUnit", "BASE"),
                ("quantity", "0.001"),
            ],
            "POST",
            "/fapi/v3/chase",
            &["symbol=BTCUSDT", "side=BUY"],
        ),
    ]);
    for name in ["place_spot_order", "place_futures_order"] {
        let product = if name == "place_spot_order" {
            SPOT
        } else {
            SWAP
        };
        assert_rejected_offline(
            Kind::Private,
            name,
            &[
                ("product_symbol", product),
                ("side", "hold"),
                ("type", "MARKET"),
                ("quantity", "1"),
            ],
        );
    }
}

#[test]
fn unsafe_orders_are_rejected_before_any_request() {
    // closePosition=true cannot be combined with quantity.
    assert_rejected_offline(
        Kind::Private,
        "place_futures_order",
        &[
            ("product_symbol", SWAP),
            ("side", "SELL"),
            ("type", "STOP_MARKET"),
            ("stopPrice", "90"),
            ("closePosition", "true"),
            ("quantity", "1"),
        ],
    );
    // LIMIT orders require timeInForce.
    assert_rejected_offline(
        Kind::Private,
        "place_futures_order",
        &[
            ("product_symbol", SWAP),
            ("side", "BUY"),
            ("type", "LIMIT"),
            ("quantity", "1"),
            ("price", "100"),
        ],
    );
    // Spot MARKET orders need exactly one of quantity / quoteOrderQty.
    assert_rejected_offline(
        Kind::Private,
        "place_spot_order",
        &[
            ("product_symbol", SPOT),
            ("side", "BUY"),
            ("type", "MARKET"),
            ("quantity", "1"),
            ("quoteOrderQty", "10"),
        ],
    );
    // Cancel/modify must identify the order.
    assert_rejected_offline(
        Kind::Private,
        "cancel_futures_order",
        &[("product_symbol", SWAP)],
    );
    assert_rejected_offline(
        Kind::Private,
        "modify_futures_order",
        &[("product_symbol", SWAP), ("orderId", "1"), ("price", "1")],
    );
    // Batch cancel needs exactly one id list and at most ten ids.
    assert_rejected_offline(
        Kind::Private,
        "cancel_futures_batch_orders",
        &[
            ("product_symbol", SWAP),
            ("orderIdList", "[1]"),
            ("origClientOrderIdList", "[\"a\"]"),
        ],
    );
    assert_rejected_offline(
        Kind::Private,
        "cancel_futures_batch_orders",
        &[
            ("product_symbol", SWAP),
            ("orderIdList", "[1,2,3,4,5,6,7,8,9,10,11]"),
        ],
    );
    // Dead-man switch must be scoped to a symbol.
    assert_rejected_offline(
        Kind::Private,
        "set_futures_countdown_cancel_all",
        &[("countdownTime", "1000")],
    );
    // Cancel-all must be scoped to a symbol.
    assert_rejected_offline(Kind::Private, "cancel_all_futures_open_orders", &[]);
    // More than five batch orders are rejected.
    assert_rejected_offline(
        Kind::Private,
        "place_futures_batch_orders",
        &[(
            "batchOrders",
            r#"[{"symbol":"BTCUSDT","side":"BUY","type":"MARKET","quantity":"1"},{"symbol":"BTCUSDT","side":"BUY","type":"MARKET","quantity":"1"},{"symbol":"BTCUSDT","side":"BUY","type":"MARKET","quantity":"1"},{"symbol":"BTCUSDT","side":"BUY","type":"MARKET","quantity":"1"},{"symbol":"BTCUSDT","side":"BUY","type":"MARKET","quantity":"1"},{"symbol":"BTCUSDT","side":"BUY","type":"MARKET","quantity":"1"}]"#,
        )],
    );
    // OCO requires exactly two legs.
    assert_rejected_offline(
        Kind::Private,
        "place_futures_strategy_order",
        &[
            ("strategyType", "OCO"),
            (
                "subOrderList",
                r#"[{"strategySubId":1,"securityType":"USDT_FUTURES","symbol":"BTCUSDT","side":"SELL","type":"STOP_MARKET","quantity":"1","stopPrice":"80"}]"#,
            ),
        ],
    );
    // Leverage is bounded and margin type must be documented.
    assert_rejected_offline(
        Kind::Private,
        "set_futures_leverage",
        &[("product_symbol", SWAP), ("leverage", "0")],
    );
    assert_rejected_offline(
        Kind::Private,
        "set_futures_margin_type",
        &[("product_symbol", SWAP), ("marginType", "CROSS")],
    );
    // Unknown dispatch names never reach the wire.
    assert_rejected_offline(Kind::Private, "withdraw", &[("amount", "1")]);
    assert_rejected_offline(Kind::Public, "get_unknown", &[]);
}

#[test]
fn signed_futures_request_body_carries_user_signer_and_nonce() {
    let (result, requests) = run(
        Kind::Private,
        "set_futures_leverage",
        &[("product_symbol", SWAP), ("leverage", "5")],
    );
    result.expect("request");
    let [request] = requests.as_slice() else {
        panic!("expected one request, got {requests:?}");
    };
    assert!(
        request
            .to_ascii_lowercase()
            .contains("content-type: application/x-www-form-urlencoded")
    );
    let body = request.split_once("\r\n\r\n").expect("body").1;
    let keys: Vec<&str> = body
        .split('&')
        .map(|pair| pair.split_once('=').map_or(pair, |(key, _)| key))
        .collect();
    assert_eq!(
        keys,
        vec!["leverage", "symbol", "nonce", "user", "signer", "signature"]
    );
    assert!(body.contains(&format!("user={USER}")));
    assert!(body.contains(&format!("signer={SIGNER}")));
}

#[test]
fn signed_spot_request_omits_user() {
    let (result, requests) = run(Kind::Private, "get_spot_account", &[]);
    result.expect("request");
    let [request] = requests.as_slice() else {
        panic!("expected one request, got {requests:?}");
    };
    let line = request.lines().next().unwrap_or_default();
    assert!(line.starts_with("GET /api/v3/account?nonce="), "{line}");
    assert!(!line.contains("user="), "{line}");
    assert!(line.contains(&format!("signer={SIGNER}")), "{line}");
}

#[test]
fn nonce_controls_preserve_the_original_nonce() {
    let nonce = client("http://127.0.0.1:1")
        .reserve_nonce()
        .unwrap()
        .to_string();
    let expected_nonce = format!("nonce={nonce}");
    let old_nonce = (nonce.parse::<u64>().unwrap() - 300_000_000).to_string();
    let old_expected = format!("nonce={old_nonce}");
    assert_cases(&[
        private(
            "noop_spot",
            &[("nonce", nonce.as_str())],
            "POST",
            "/api/v3/noop",
            &[expected_nonce.as_str()],
        ),
        private(
            "noop_futures",
            &[("nonce", nonce.as_str())],
            "POST",
            "/fapi/v3/noop",
            &[expected_nonce.as_str()],
        ),
        private(
            "guarded_cancel_futures_order",
            &[
                ("product_symbol", SWAP),
                ("nonce", old_nonce.as_str()),
                ("orderId", "123"),
            ],
            "DELETE",
            "/fapi/v3/guardedCancelOrder",
            &["symbol=BTCUSDT", "orderId=123", old_expected.as_str()],
        ),
        private(
            "guarded_cancel_futures_batch_orders",
            &[
                ("product_symbol", SWAP),
                ("nonce", old_nonce.as_str()),
                ("orderIdList", "[123, 456]"),
            ],
            "DELETE",
            "/fapi/v3/guardedBatchOrders",
            &[old_expected.as_str(), "orderIdList=%5B123%2C456%5D"],
        ),
        private(
            "transfer_sub_account",
            &[
                ("toAccountAddress", USER),
                ("asset", "USDT"),
                ("amount", "10"),
                ("kindType", "FUTURE_FUTURE"),
            ],
            "POST",
            "/fapi/v3/subAccountTransfer",
            &["kindType=FUTURE_FUTURE", "amount=10"],
        ),
    ]);
    for name in [
        "noop_spot",
        "noop_futures",
        "guarded_cancel_futures_order",
        "guarded_cancel_futures_batch_orders",
    ] {
        assert_rejected_offline(Kind::Private, name, &[]);
        assert_rejected_offline(Kind::Private, name, &[("nonce", "0")]);
    }
    assert_rejected_offline(
        Kind::Private,
        "guarded_cancel_futures_batch_orders",
        &[
            ("product_symbol", SWAP),
            ("nonce", "123"),
            ("orderIdList", "[]"),
        ],
    );
    for name in ["place_spot_order", "place_futures_order"] {
        let (result, requests) = run(
            Kind::Private,
            name,
            &[
                ("symbol", "BTCUSDT"),
                ("side", "BUY"),
                ("type", "MARKET"),
                ("quantity", "1"),
                ("nonce", nonce.as_str()),
            ],
        );
        result.expect("explicit placement nonce");
        assert_eq!(requests[0].matches(expected_nonce.as_str()).count(), 1);
    }
}

#[test]
fn sub_account_transfer_signs_the_agent_identity_and_field_order() {
    let (result, requests) = run(
        Kind::Private,
        "transfer_sub_account",
        &[
            ("toAccountAddress", USER),
            ("asset", "USDT"),
            ("amount", "10"),
            ("kindType", "FUTURE_FUTURE"),
            ("fromAccountAddress", USER),
        ],
    );
    result.expect("internal transfer");
    let body = requests[0].split_once("\r\n\r\n").expect("body").1;
    let pairs: Vec<_> = url::form_urlencoded::parse(body.as_bytes())
        .into_owned()
        .collect();
    assert_eq!(
        pairs
            .iter()
            .map(|(key, _)| key.as_str())
            .collect::<Vec<_>>(),
        [
            "toAccountAddress",
            "asset",
            "amount",
            "kindType",
            "nonce",
            "signer",
            "fromAccountAddress",
            "signature"
        ]
    );
    let (message, signature) = body.rsplit_once("&signature=").expect("signature");
    assert_eq!(
        signature,
        super::super::signing::sign_message(message, &[0x11; 32]).expect("agent signature")
    );
}

#[test]
fn additional_account_routes() {
    assert_cases(&[
        public(
            "get_asset_logos",
            &[],
            "GET",
            "/fapi/v3/common/asset/all-asset-logo",
            &[],
        ),
        private(
            "exchange_futures_assets",
            &[("confirm", "true")],
            "POST",
            "/fapi/v3/assetExchange",
            &[],
        ),
        private(
            "get_sub_accounts",
            &[],
            "GET",
            "/fapi/v3/getSubAccountList",
            &[],
        ),
        private(
            "get_direct_announcements",
            &[],
            "GET",
            "/fapi/v3/announcement/direct",
            &[],
        ),
        private(
            "get_direct_announcement",
            &[("id", "1")],
            "GET",
            "/fapi/v3/announcement/directById",
            &[],
        ),
        private(
            "create_sub_account_signed",
            &[
                ("subAccountName", "desk"),
                (
                    "subSourceAddr",
                    "0x0000000000000000000000000000000000000002",
                ),
                ("nonce", "1700000000000123"),
                ("user", "0x0000000000000000000000000000000000000001"),
                ("signer", "0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a"),
                (
                    "childSignature",
                    "0x2222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222",
                ),
                (
                    "signature",
                    "0x1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111",
                ),
            ],
            "POST",
            "/fapi/v3/createSubAccount",
            &[],
        ),
        private(
            "update_sub_account_signed",
            &[
                (
                    "subSourceAddr",
                    "0x0000000000000000000000000000000000000002",
                ),
                ("nonce", "1700000000000123"),
                ("user", "0x0000000000000000000000000000000000000001"),
                ("signer", "0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a"),
                (
                    "signature",
                    "0x1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111",
                ),
                ("status", "FROZEN"),
            ],
            "POST",
            "/fapi/v3/updateSubAccount",
            &[],
        ),
        private(
            "bind_sub_account_signed",
            &[
                ("childAddress", "0x0000000000000000000000000000000000000002"),
                ("name", "desk"),
                ("nonce", "1700000000000123"),
                ("user", "0x0000000000000000000000000000000000000001"),
                (
                    "childSignature",
                    "0x2222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222",
                ),
                (
                    "signature",
                    "0x1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111",
                ),
            ],
            "POST",
            "/fapi/v3/sub-accounts/bind",
            &[],
        ),
        private(
            "register_agent_signed",
            &[
                ("user", "0x0000000000000000000000000000000000000001"),
                ("nonce", "1700000000000123"),
                ("agentName", "trader"),
                ("agentAddress", "0x0000000000000000000000000000000000000003"),
                ("expired", "1800000000000"),
                ("signatureChainId", "56"),
                ("canSpotTrade", "true"),
                ("canPerpTrade", "true"),
                ("canWithdraw", "false"),
                (
                    "signature",
                    "0x1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111",
                ),
            ],
            "POST",
            "/fapi/v3/registerAndApproveAgent",
            &[],
        ),
    ]);
}

#[test]
fn prediction_routes_use_dedicated_host() {
    assert_cases(&[
        public("get_prediction_ping", &[], "GET", "/api/v3/ping", &[]),
        public("get_prediction_time", &[], "GET", "/api/v3/time", &[]),
        public(
            "get_prediction_exchange_info",
            &[],
            "GET",
            "/api/v3/prediction/exchangeInfo",
            &[],
        ),
        public(
            "get_prediction_depth",
            &[("symbol", "EVENT4_ALGERIA_WIN_YUSDT")],
            "GET",
            "/api/v3/depth",
            &[],
        ),
        public(
            "get_prediction_trades",
            &[("symbol", "EVENT4_ALGERIA_WIN_YUSDT")],
            "GET",
            "/api/v3/trades",
            &[],
        ),
        public(
            "get_prediction_historical_trades",
            &[("symbol", "EVENT4_ALGERIA_WIN_YUSDT")],
            "GET",
            "/api/v3/historicalTrades",
            &[],
        ),
        public(
            "get_prediction_agg_trades",
            &[("symbol", "EVENT4_ALGERIA_WIN_YUSDT")],
            "GET",
            "/api/v3/aggTrades",
            &[],
        ),
        public(
            "get_prediction_klines",
            &[("symbol", "EVENT4_ALGERIA_WIN_YUSDT"), ("interval", "1m")],
            "GET",
            "/api/v3/klines",
            &[],
        ),
        public(
            "get_prediction_ticker_24hr",
            &[],
            "GET",
            "/api/v3/ticker/24hr",
            &[],
        ),
        public(
            "get_prediction_ticker_price",
            &[],
            "GET",
            "/api/v3/ticker/price",
            &[],
        ),
        public(
            "get_prediction_ticker_book_ticker",
            &[],
            "GET",
            "/api/v3/ticker/bookTicker",
            &[],
        ),
        private(
            "get_prediction_commission_rate",
            &[("symbol", "EVENT4_ALGERIA_WIN_YUSDT")],
            "GET",
            "/api/v3/commissionRate",
            &[],
        ),
        private(
            "create_prediction_order",
            &[
                ("symbol", "EVENT4_ALGERIA_WIN_YUSDT"),
                ("side", "BUY"),
                ("type", "LIMIT"),
                ("quantity", "1"),
                ("price", "0.5"),
                ("timeInForce", "GTC"),
            ],
            "POST",
            "/api/v3/order",
            &[],
        ),
        private(
            "cancel_prediction_order",
            &[("symbol", "EVENT4_ALGERIA_WIN_YUSDT"), ("orderId", "1")],
            "DELETE",
            "/api/v3/order",
            &[],
        ),
        private(
            "get_prediction_order",
            &[("symbol", "EVENT4_ALGERIA_WIN_YUSDT"), ("orderId", "1")],
            "GET",
            "/api/v3/order",
            &[],
        ),
        private(
            "get_prediction_open_order",
            &[("symbol", "EVENT4_ALGERIA_WIN_YUSDT"), ("orderId", "1")],
            "GET",
            "/api/v3/openOrder",
            &[],
        ),
        private(
            "get_prediction_open_orders",
            &[],
            "GET",
            "/api/v3/openOrders",
            &[],
        ),
        private(
            "get_prediction_all_orders",
            &[("symbol", "EVENT4_ALGERIA_WIN_YUSDT")],
            "GET",
            "/api/v3/allOrders",
            &[],
        ),
        private(
            "create_prediction_asset_wallet_transfer",
            &[
                ("amount", "1"),
                ("asset", "USDT"),
                ("clientTranId", "example"),
                ("kindType", "FUTURE_SPOT"),
            ],
            "POST",
            "/api/v3/asset/wallet/transfer",
            &[],
        ),
        private(
            "create_prediction_mint",
            &[("symbol", "EVENT4_ALGERIA_WIN_YUSDT"), ("quantity", "1")],
            "POST",
            "/api/v3/prediction/mint",
            &[],
        ),
        private(
            "create_prediction_burn",
            &[("symbol", "EVENT4_ALGERIA_WIN_YUSDT"), ("quantity", "1")],
            "POST",
            "/api/v3/prediction/burn",
            &[],
        ),
        private(
            "create_prediction_split",
            &[
                ("event", "EVENT4"),
                ("symbol", "EVENT4_ALGERIA_WIN_YUSDT"),
                ("quantity", "1"),
            ],
            "POST",
            "/api/v3/prediction/split",
            &[],
        ),
        private(
            "create_prediction_merge",
            &[("event", "EVENT4"), ("quantity", "1")],
            "POST",
            "/api/v3/prediction/merge",
            &[],
        ),
        private(
            "get_prediction_positions",
            &[],
            "GET",
            "/api/v3/prediction/positions",
            &[],
        ),
        private(
            "get_prediction_position_histories",
            &[],
            "GET",
            "/api/v3/prediction/positionHistories",
            &[],
        ),
        private(
            "get_prediction_settlement_histories",
            &[],
            "GET",
            "/api/v3/prediction/settlementHistories",
            &[],
        ),
        private("get_prediction_account", &[], "GET", "/api/v3/account", &[]),
        private(
            "get_prediction_user_trades",
            &[],
            "GET",
            "/api/v3/userTrades",
            &[],
        ),
        private(
            "create_prediction_listen_key",
            &[],
            "POST",
            "/api/v3/listenKey",
            &[],
        ),
        private(
            "update_prediction_listen_key",
            &[("listenKey", "example")],
            "PUT",
            "/api/v3/listenKey",
            &[],
        ),
        private(
            "cancel_prediction_listen_key",
            &[("listenKey", "example")],
            "DELETE",
            "/api/v3/listenKey",
            &[],
        ),
    ]);
}

#[test]
fn withdraw_permission_requires_an_ip_whitelist() {
    for whitelist in [None, Some("192.0.2.1")] {
        let signature = format!("0x{}", "11".repeat(65));
        let mut params = vec![
            ("user", USER),
            ("nonce", "1700000000000123"),
            ("agentName", "trader"),
            ("agentAddress", SIGNER),
            ("expired", "1800000000000"),
            ("signatureChainId", "56"),
            ("canSpotTrade", "true"),
            ("canPerpTrade", "true"),
            ("canWithdraw", "true"),
            ("signature", signature.as_str()),
        ];
        if let Some(ip) = whitelist {
            params.push(("ipWhitelist", ip));
        }
        let (result, requests) = run(Kind::Private, "register_agent_signed", &params);
        if whitelist.is_none() {
            assert!(result.unwrap_err().to_string().contains("ipWhitelist"));
            assert!(requests.is_empty());
            continue;
        }
        result.unwrap();
        assert_eq!(requests.len(), 1);
        assert!(requests[0].starts_with("POST /fapi/v3/registerAndApproveAgent "));
        assert!(requests[0].contains("canWithdraw=true"));
        assert_eq!(
            requests[0].contains("ipWhitelist=192.0.2.1"),
            whitelist.is_some()
        );
    }
}

#[test]
fn migration_history_route() {
    assert_cases(&[private(
        "get_asset_migration_history",
        &[("batchId", "batch1")],
        "GET",
        "/fapi/v3/asset/migrateUser/history",
        &["batchId=batch1"],
    )]);
}
