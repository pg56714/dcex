//! Offline route coverage for every Binance REST dispatch name.
//!
//! Each case sends one dispatch name through `public_request` / `private_request`
//! against a local recording server and asserts the HTTP method and path that
//! reach the wire match the official Binance API documentation.

use std::io::{ErrorKind, Read, Write};
use std::net::TcpListener;
use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

use super::super::client::BinanceClient;
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
    path: &'static str,
}

const fn public(
    name: &'static str,
    params: &'static [(&'static str, &'static str)],
    method: &'static str,
    path: &'static str,
) -> Case {
    Case {
        kind: Kind::Public,
        name,
        params,
        method,
        path,
    }
}

const fn private(
    name: &'static str,
    params: &'static [(&'static str, &'static str)],
    method: &'static str,
    path: &'static str,
) -> Case {
    Case {
        kind: Kind::Private,
        name,
        params,
        method,
        path,
    }
}

/// Accepts every connection until stopped and records each request line.
fn multi_request_server() -> (String, Arc<AtomicBool>, JoinHandle<Vec<String>>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    listener.set_nonblocking(true).expect("nonblocking");
    let address = listener.local_addr().expect("address");
    let stop = Arc::new(AtomicBool::new(false));
    let stop_flag = Arc::clone(&stop);
    let handle = thread::spawn(move || {
        let deadline = Instant::now() + Duration::from_secs(10);
        let mut lines = Vec::new();
        loop {
            match listener.accept() {
                Ok((mut stream, _)) => {
                    stream.set_nonblocking(false).expect("blocking stream");
                    stream
                        .set_read_timeout(Some(Duration::from_secs(2)))
                        .expect("read timeout");
                    let mut buffer = [0u8; 8192];
                    let size = stream.read(&mut buffer).unwrap_or(0);
                    let request = String::from_utf8_lossy(&buffer[..size]).into_owned();
                    if let Some(line) = request.lines().next() {
                        lines.push(line.to_string());
                    }
                    let body = r#"{"serverTime":1700000000000,"listenKey":"test-listen-key"}"#;
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
                        return lines;
                    }
                    thread::sleep(Duration::from_millis(2));
                }
                Err(error) => panic!("accept failed: {error}"),
            }
        }
    });
    (format!("http://{address}"), stop, handle)
}

fn is_time_sync(line: &str) -> bool {
    [
        "GET /api/v3/time ",
        "GET /fapi/v1/time ",
        "GET /dapi/v1/time ",
        "GET /eapi/v1/time ",
    ]
    .iter()
    .any(|prefix| line.starts_with(prefix))
}

fn run_case(case: &Case) -> Result<String, String> {
    let (base_url, stop, handle) = multi_request_server();
    let client = BinanceClient::with_all_base_urls(
        Some("api-key".to_string()),
        Some("api-secret".to_string()),
        Duration::from_secs(2),
        base_url.clone(),
        base_url.clone(),
        base_url.clone(),
    )
    .expect("client")
    .with_portfolio_margin_base_url(base_url.clone())
    .with_coin_futures_base_url(base_url);
    let params: Vec<(String, String)> = case
        .params
        .iter()
        .map(|(key, value)| ((*key).to_string(), (*value).to_string()))
        .collect();
    let kind = case.kind;
    let name = case.name;
    let result = block_on(async move {
        match kind {
            Kind::Public => client.public_request(name, params).await,
            Kind::Private => client.private_request(name, params).await,
        }
    });
    stop.store(true, Ordering::SeqCst);
    let lines = handle.join().expect("server thread");
    if let Err(error) = result {
        return Err(format!("{name}: request failed: {error} (wire: {lines:?})"));
    }
    let expects_time = is_time_sync(&format!("{} {} ", case.method, case.path));
    let requests: Vec<&String> = lines
        .iter()
        .filter(|line| expects_time || !is_time_sync(line))
        .collect();
    let [line] = requests.as_slice() else {
        return Err(format!(
            "{name}: expected exactly one non-time request, got {lines:?}"
        ));
    };
    let expected_query = format!("{} {}?", case.method, case.path);
    let expected_bare = format!("{} {} ", case.method, case.path);
    if line.starts_with(&expected_query) || line.starts_with(&expected_bare) {
        Ok((*line).clone())
    } else {
        Err(format!(
            "{name}: expected `{} {}`, wire was `{line}`",
            case.method, case.path
        ))
    }
}

fn assert_cases(cases: &[Case]) {
    let failures: Vec<String> = cases
        .iter()
        .filter_map(|case| run_case(case).err())
        .collect();
    assert!(
        failures.is_empty(),
        "{} of {} Binance route(s) failed:\n{}",
        failures.len(),
        cases.len(),
        failures.join("\n")
    );
}

const SPOT: &str = "BTC-USDT-SPOT";
const SWAP: &str = "BTC-USDT-SWAP";

#[test]
fn spot_and_usdm_market_data_routes_match_official_paths() {
    assert_cases(&[
        public(
            "get_server_time",
            &[("market_type", "spot")],
            "GET",
            "/api/v3/time",
        ),
        public("get_spot_exchange_info", &[], "GET", "/api/v3/exchangeInfo"),
        public(
            "get_spot_orderbook",
            &[("product_symbol", SPOT)],
            "GET",
            "/api/v3/depth",
        ),
        public(
            "get_spot_trades",
            &[("product_symbol", SPOT)],
            "GET",
            "/api/v3/trades",
        ),
        public(
            "get_spot_price",
            &[("product_symbol", SPOT)],
            "GET",
            "/api/v3/ticker/price",
        ),
        public(
            "get_klines",
            &[("product_symbol", SPOT), ("interval", "1m")],
            "GET",
            "/api/v3/klines",
        ),
        public(
            "get_klines",
            &[("product_symbol", SWAP), ("interval", "1m")],
            "GET",
            "/fapi/v1/klines",
        ),
        public(
            "get_futures_exchange_info",
            &[],
            "GET",
            "/fapi/v1/exchangeInfo",
        ),
        public(
            "get_futures_orderbook",
            &[("product_symbol", SWAP)],
            "GET",
            "/fapi/v1/depth",
        ),
        public(
            "get_futures_ticker",
            &[("product_symbol", SWAP)],
            "GET",
            "/fapi/v1/ticker/bookTicker",
        ),
        public(
            "get_futures_premium_index",
            &[("product_symbol", SWAP)],
            "GET",
            "/fapi/v1/premiumIndex",
        ),
        public(
            "get_futures_funding_rate",
            &[("product_symbol", SWAP)],
            "GET",
            "/fapi/v1/fundingRate",
        ),
        public(
            "get_futures_open_interest",
            &[("product_symbol", SWAP)],
            "GET",
            "/fapi/v1/openInterest",
        ),
        public(
            "get_futures_open_interest_history",
            &[("product_symbol", SWAP)],
            "GET",
            "/futures/data/openInterestHist",
        ),
        public(
            "get_futures_global_long_short_account_ratio",
            &[("product_symbol", SWAP)],
            "GET",
            "/futures/data/globalLongShortAccountRatio",
        ),
        public(
            "get_futures_top_long_short_account_ratio",
            &[("product_symbol", SWAP)],
            "GET",
            "/futures/data/topLongShortAccountRatio",
        ),
        public(
            "get_futures_top_long_short_position_ratio",
            &[("product_symbol", SWAP)],
            "GET",
            "/futures/data/topLongShortPositionRatio",
        ),
        public(
            "get_futures_taker_buy_sell_volume",
            &[("product_symbol", SWAP)],
            "GET",
            "/futures/data/takerlongshortRatio",
        ),
        public(
            "get_futures_basis",
            &[("product_symbol", SWAP)],
            "GET",
            "/futures/data/basis",
        ),
    ]);
}

#[test]
fn spot_and_usdm_trading_routes_match_official_paths() {
    assert_cases(&[
        private(
            "set_leverage",
            &[("product_symbol", SWAP), ("leverage", "5")],
            "POST",
            "/fapi/v1/leverage",
        ),
        private(
            "place_order",
            &[
                ("product_symbol", SPOT),
                ("side", "BUY"),
                ("type_", "LIMIT"),
                ("quantity", "1"),
                ("price", "100"),
                ("timeInForce", "GTC"),
            ],
            "POST",
            "/api/v3/order",
        ),
        private(
            "place_order",
            &[
                ("product_symbol", SWAP),
                ("side", "SELL"),
                ("type_", "MARKET"),
                ("quantity", "1"),
            ],
            "POST",
            "/fapi/v1/order",
        ),
        private(
            "test_order",
            &[
                ("product_symbol", SPOT),
                ("side", "BUY"),
                ("type_", "MARKET"),
                ("quantity", "1"),
            ],
            "POST",
            "/api/v3/order/test",
        ),
        private(
            "test_order",
            &[
                ("product_symbol", SWAP),
                ("side", "BUY"),
                ("type_", "MARKET"),
                ("quantity", "1"),
            ],
            "POST",
            "/fapi/v1/order/test",
        ),
        private(
            "place_market_order",
            &[("product_symbol", SWAP), ("side", "BUY"), ("quantity", "1")],
            "POST",
            "/fapi/v1/order",
        ),
        private(
            "place_market_buy_order",
            &[("product_symbol", SPOT), ("quantity", "1")],
            "POST",
            "/api/v3/order",
        ),
        private(
            "place_market_sell_order",
            &[("product_symbol", SWAP), ("quantity", "1")],
            "POST",
            "/fapi/v1/order",
        ),
        private(
            "place_limit_order",
            &[
                ("product_symbol", SWAP),
                ("side", "BUY"),
                ("quantity", "1"),
                ("price", "100"),
            ],
            "POST",
            "/fapi/v1/order",
        ),
        private(
            "place_limit_buy_order",
            &[
                ("product_symbol", SPOT),
                ("quantity", "1"),
                ("price", "100"),
            ],
            "POST",
            "/api/v3/order",
        ),
        private(
            "place_limit_sell_order",
            &[
                ("product_symbol", SWAP),
                ("quantity", "1"),
                ("price", "100"),
            ],
            "POST",
            "/fapi/v1/order",
        ),
        private(
            "place_post_only_limit_order",
            &[
                ("product_symbol", SPOT),
                ("side", "BUY"),
                ("quantity", "1"),
                ("price", "100"),
            ],
            "POST",
            "/api/v3/order",
        ),
        private(
            "place_post_only_limit_order",
            &[
                ("product_symbol", SWAP),
                ("side", "BUY"),
                ("quantity", "1"),
                ("price", "100"),
            ],
            "POST",
            "/fapi/v1/order",
        ),
        private(
            "place_post_only_limit_buy_order",
            &[
                ("product_symbol", SWAP),
                ("quantity", "1"),
                ("price", "100"),
            ],
            "POST",
            "/fapi/v1/order",
        ),
        private(
            "place_post_only_limit_sell_order",
            &[
                ("product_symbol", SPOT),
                ("quantity", "1"),
                ("price", "100"),
            ],
            "POST",
            "/api/v3/order",
        ),
        private(
            "cancel_order",
            &[("product_symbol", SPOT), ("orderId", "1")],
            "DELETE",
            "/api/v3/order",
        ),
        private(
            "cancel_order",
            &[("product_symbol", SWAP), ("orderId", "1")],
            "DELETE",
            "/fapi/v1/order",
        ),
        private(
            "get_order",
            &[("product_symbol", SPOT), ("orderId", "1")],
            "GET",
            "/api/v3/order",
        ),
        private(
            "get_order",
            &[("product_symbol", SWAP), ("origClientOrderId", "abc")],
            "GET",
            "/fapi/v1/order",
        ),
        private(
            "get_open_orders",
            &[("product_symbol", SPOT)],
            "GET",
            "/api/v3/openOrders",
        ),
        private(
            "get_open_orders",
            &[("product_symbol", SWAP), ("orderId", "1")],
            "GET",
            "/fapi/v1/openOrder",
        ),
        private(
            "get_all_open_orders",
            &[("market_type", "spot")],
            "GET",
            "/api/v3/openOrders",
        ),
        private(
            "get_all_open_orders",
            &[("market_type", "swap")],
            "GET",
            "/fapi/v1/openOrders",
        ),
        private(
            "cancel_all_open_orders",
            &[("product_symbol", SPOT)],
            "DELETE",
            "/api/v3/openOrders",
        ),
        private(
            "cancel_all_open_orders",
            &[("product_symbol", SWAP)],
            "DELETE",
            "/fapi/v1/allOpenOrders",
        ),
        private(
            "get_future_all_order",
            &[("product_symbol", SWAP)],
            "GET",
            "/fapi/v1/allOrders",
        ),
        private(
            "get_all_orders",
            &[("product_symbol", SPOT)],
            "GET",
            "/api/v3/allOrders",
        ),
        private(
            "get_account_trades",
            &[("product_symbol", SPOT)],
            "GET",
            "/api/v3/myTrades",
        ),
        private(
            "get_account_trades",
            &[("product_symbol", SWAP)],
            "GET",
            "/fapi/v1/userTrades",
        ),
        private("get_future_position", &[], "GET", "/fapi/v3/positionRisk"),
        private(
            "create_oco_order",
            &[
                ("product_symbol", SPOT),
                ("side", "SELL"),
                ("quantity", "1"),
                ("aboveType", "LIMIT_MAKER"),
                ("belowType", "STOP_LOSS"),
                ("abovePrice", "110"),
                ("belowStopPrice", "90"),
            ],
            "POST",
            "/api/v3/orderList/oco",
        ),
        private(
            "create_oto_order",
            &[
                ("product_symbol", SPOT),
                ("workingType", "LIMIT"),
                ("workingSide", "BUY"),
                ("workingPrice", "100"),
                ("workingQuantity", "1"),
                ("workingTimeInForce", "GTC"),
                ("pendingType", "MARKET"),
                ("pendingSide", "SELL"),
                ("pendingQuantity", "1"),
            ],
            "POST",
            "/api/v3/orderList/oto",
        ),
        private(
            "create_otoco_order",
            &[
                ("product_symbol", SPOT),
                ("workingType", "LIMIT"),
                ("workingSide", "BUY"),
                ("workingPrice", "100"),
                ("workingQuantity", "1"),
                ("workingTimeInForce", "GTC"),
                ("pendingSide", "SELL"),
                ("pendingQuantity", "1"),
                ("pendingAboveType", "LIMIT_MAKER"),
                ("pendingAbovePrice", "110"),
            ],
            "POST",
            "/api/v3/orderList/otoco",
        ),
        private(
            "get_prevented_matches",
            &[("product_symbol", SPOT), ("preventedMatchId", "1")],
            "GET",
            "/api/v3/myPreventedMatches",
        ),
        private(
            "get_allocations",
            &[("product_symbol", SPOT)],
            "GET",
            "/api/v3/myAllocations",
        ),
        private(
            "get_order_rate_limit",
            &[],
            "GET",
            "/api/v3/rateLimit/order",
        ),
        private(
            "place_futures_algo_order",
            &[
                ("product_symbol", SWAP),
                ("side", "SELL"),
                ("type_", "STOP_MARKET"),
                ("quantity", "1"),
                ("triggerPrice", "90"),
            ],
            "POST",
            "/fapi/v1/algoOrder",
        ),
        private(
            "cancel_futures_algo_order",
            &[("algoId", "1")],
            "DELETE",
            "/fapi/v1/algoOrder",
        ),
        private(
            "get_futures_algo_order",
            &[("clientAlgoId", "abc")],
            "GET",
            "/fapi/v1/algoOrder",
        ),
        private(
            "get_all_open_futures_algo_orders",
            &[],
            "GET",
            "/fapi/v1/openAlgoOrders",
        ),
        private(
            "get_all_futures_algo_orders",
            &[("product_symbol", SWAP)],
            "GET",
            "/fapi/v1/allAlgoOrders",
        ),
        private(
            "cancel_all_open_futures_algo_orders",
            &[("product_symbol", SWAP)],
            "DELETE",
            "/fapi/v1/algoOpenOrders",
        ),
    ]);
}

#[test]
fn account_wallet_and_stream_routes_match_official_paths() {
    assert_cases(&[
        private(
            "get_spot_fee_rates",
            &[("product_symbol", SPOT)],
            "GET",
            "/api/v3/account/commission",
        ),
        private(
            "get_futures_fee_rates",
            &[("product_symbol", SWAP)],
            "GET",
            "/fapi/v1/commissionRate",
        ),
        private(
            "get_account_balance",
            &[("market_type", "spot")],
            "GET",
            "/api/v3/account",
        ),
        private(
            "get_account_balance",
            &[("market_type", "swap")],
            "GET",
            "/fapi/v3/balance",
        ),
        private("get_income_history", &[], "GET", "/fapi/v1/income"),
        private("get_futures_account_info", &[], "GET", "/fapi/v3/account"),
        private(
            "get_wallet_balance",
            &[],
            "GET",
            "/sapi/v1/asset/wallet/balance",
        ),
        private(
            "get_funding_wallet",
            &[],
            "POST",
            "/sapi/v1/asset/get-funding-asset",
        ),
        private(
            "create_universal_transfer",
            &[
                ("type", "MAIN_UMFUTURE"),
                ("asset", "USDT"),
                ("amount", "1"),
            ],
            "POST",
            "/sapi/v1/asset/transfer",
        ),
        private(
            "get_universal_transfer_history",
            &[("type", "MAIN_UMFUTURE")],
            "GET",
            "/sapi/v1/asset/transfer",
        ),
        private(
            "create_futures_listen_key",
            &[],
            "POST",
            "/fapi/v1/listenKey",
        ),
        private(
            "keep_alive_futures_listen_key",
            &[("listenKey", "k")],
            "PUT",
            "/fapi/v1/listenKey",
        ),
        private(
            "close_futures_listen_key",
            &[("listenKey", "k")],
            "DELETE",
            "/fapi/v1/listenKey",
        ),
    ]);
}

#[test]
fn coin_futures_routes_match_official_paths() {
    assert_cases(&[
        public(
            "get_coin_futures_exchange_info",
            &[],
            "GET",
            "/dapi/v1/exchangeInfo",
        ),
        public(
            "get_coin_futures_orderbook",
            &[("symbol", "BTCUSD_PERP")],
            "GET",
            "/dapi/v1/depth",
        ),
        public(
            "get_coin_futures_trades",
            &[("symbol", "BTCUSD_PERP")],
            "GET",
            "/dapi/v1/trades",
        ),
        public(
            "get_coin_futures_klines",
            &[("symbol", "BTCUSD_PERP"), ("interval", "1m")],
            "GET",
            "/dapi/v1/klines",
        ),
        public(
            "get_coin_futures_ticker",
            &[("pair", "BTCUSD")],
            "GET",
            "/dapi/v1/ticker/price",
        ),
        public(
            "get_coin_futures_mark_price",
            &[("symbol", "BTCUSD_PERP")],
            "GET",
            "/dapi/v1/premiumIndex",
        ),
        public(
            "get_coin_futures_funding_rate",
            &[("symbol", "BTCUSD_PERP")],
            "GET",
            "/dapi/v1/fundingRate",
        ),
        private("get_coin_futures_balance", &[], "GET", "/dapi/v1/balance"),
        private("get_coin_futures_account", &[], "GET", "/dapi/v1/account"),
        private(
            "get_coin_futures_positions",
            &[("pair", "BTCUSD")],
            "GET",
            "/dapi/v1/positionRisk",
        ),
        private(
            "get_coin_futures_open_orders",
            &[("symbol", "BTCUSD_PERP")],
            "GET",
            "/dapi/v1/openOrders",
        ),
        private(
            "get_coin_futures_order",
            &[("symbol", "BTCUSD_PERP"), ("orderId", "1")],
            "GET",
            "/dapi/v1/order",
        ),
        private(
            "place_coin_futures_order",
            &[
                ("symbol", "BTCUSD_PERP"),
                ("side", "BUY"),
                ("type", "LIMIT"),
                ("quantity", "1"),
                ("price", "100"),
                ("timeInForce", "GTC"),
            ],
            "POST",
            "/dapi/v1/order",
        ),
        private(
            "cancel_coin_futures_order",
            &[("symbol", "BTCUSD_PERP"), ("origClientOrderId", "abc")],
            "DELETE",
            "/dapi/v1/order",
        ),
        private(
            "cancel_all_coin_futures_orders",
            &[("symbol", "BTCUSD_PERP")],
            "DELETE",
            "/dapi/v1/allOpenOrders",
        ),
    ]);
}

#[test]
fn convert_routes_match_official_paths() {
    assert_cases(&[
        public(
            "get_convert_pairs",
            &[("fromAsset", "BTC")],
            "GET",
            "/sapi/v1/convert/exchangeInfo",
        ),
        private(
            "get_convert_asset_info",
            &[],
            "GET",
            "/sapi/v1/convert/assetInfo",
        ),
        private(
            "get_convert_quote",
            &[
                ("fromAsset", "BTC"),
                ("toAsset", "USDT"),
                ("fromAmount", "1"),
            ],
            "POST",
            "/sapi/v1/convert/getQuote",
        ),
        private(
            "accept_convert_quote",
            &[("quoteId", "q1")],
            "POST",
            "/sapi/v1/convert/acceptQuote",
        ),
        private(
            "get_convert_order_status",
            &[("orderId", "1")],
            "GET",
            "/sapi/v1/convert/orderStatus",
        ),
        private(
            "get_convert_trade_history",
            &[("startTime", "1700000000000"), ("endTime", "1700086400000")],
            "GET",
            "/sapi/v1/convert/tradeFlow",
        ),
        private(
            "place_convert_limit_order",
            &[
                ("baseAsset", "BTC"),
                ("quoteAsset", "USDT"),
                ("limitPrice", "100"),
                ("side", "BUY"),
                ("expiredType", "1_D"),
                ("baseAmount", "1"),
            ],
            "POST",
            "/sapi/v1/convert/limit/placeOrder",
        ),
        private(
            "cancel_convert_limit_order",
            &[("orderId", "1")],
            "POST",
            "/sapi/v1/convert/limit/cancelOrder",
        ),
        private(
            "get_open_convert_limit_orders",
            &[],
            "GET",
            "/sapi/v1/convert/limit/queryOpenOrders",
        ),
    ]);
}

#[test]
fn margin_routes_match_official_paths() {
    assert_cases(&[
        private(
            "get_all_margin_assets",
            &[],
            "GET",
            "/sapi/v1/margin/allAssets",
        ),
        private(
            "get_all_cross_margin_pairs",
            &[],
            "GET",
            "/sapi/v1/margin/allPairs",
        ),
        private(
            "get_all_isolated_margin_symbols",
            &[],
            "GET",
            "/sapi/v1/margin/isolated/allPairs",
        ),
        private(
            "get_margin_price_index",
            &[("symbol", "BTCUSDT")],
            "GET",
            "/sapi/v1/margin/priceIndex",
        ),
        private(
            "get_cross_margin_account",
            &[],
            "GET",
            "/sapi/v1/margin/account",
        ),
        private(
            "get_isolated_margin_account",
            &[],
            "GET",
            "/sapi/v1/margin/isolated/account",
        ),
        private(
            "margin_borrow_repay",
            &[("asset", "USDT"), ("amount", "1"), ("type", "BORROW")],
            "POST",
            "/sapi/v1/margin/borrow-repay",
        ),
        private(
            "get_margin_borrow_repay_records",
            &[("type", "REPAY")],
            "GET",
            "/sapi/v1/margin/borrow-repay",
        ),
        private(
            "get_margin_interest_history",
            &[],
            "GET",
            "/sapi/v1/margin/interestHistory",
        ),
        private(
            "get_margin_max_borrowable",
            &[("asset", "USDT")],
            "GET",
            "/sapi/v1/margin/maxBorrowable",
        ),
        private(
            "get_margin_max_transferable",
            &[("asset", "USDT")],
            "GET",
            "/sapi/v1/margin/maxTransferable",
        ),
        private(
            "place_margin_order",
            &[
                ("product_symbol", SPOT),
                ("side", "BUY"),
                ("type", "MARKET"),
                ("quantity", "1"),
            ],
            "POST",
            "/sapi/v1/margin/order",
        ),
        private(
            "cancel_margin_order",
            &[("product_symbol", SPOT), ("orderId", "1")],
            "DELETE",
            "/sapi/v1/margin/order",
        ),
        private(
            "get_margin_order",
            &[("product_symbol", SPOT), ("orderId", "1")],
            "GET",
            "/sapi/v1/margin/order",
        ),
        private(
            "get_open_margin_orders",
            &[],
            "GET",
            "/sapi/v1/margin/openOrders",
        ),
        private(
            "cancel_all_open_margin_orders",
            &[("product_symbol", SPOT)],
            "DELETE",
            "/sapi/v1/margin/openOrders",
        ),
        private(
            "get_all_margin_orders",
            &[("product_symbol", SPOT)],
            "GET",
            "/sapi/v1/margin/allOrders",
        ),
        private(
            "get_margin_account_trades",
            &[("product_symbol", SPOT)],
            "GET",
            "/sapi/v1/margin/myTrades",
        ),
    ]);
}

#[test]
fn options_routes_match_official_paths() {
    const OPT: &str = "BTC-260925-100000-C";
    assert_cases(&[
        public(
            "get_options_exchange_info",
            &[],
            "GET",
            "/eapi/v1/exchangeInfo",
        ),
        public(
            "get_options_exercise_history",
            &[],
            "GET",
            "/eapi/v1/exerciseHistory",
        ),
        public(
            "get_options_index_price",
            &[("underlying", "BTCUSDT")],
            "GET",
            "/eapi/v1/index",
        ),
        public(
            "get_options_klines",
            &[("product_symbol", OPT), ("interval", "1m")],
            "GET",
            "/eapi/v1/klines",
        ),
        public(
            "get_options_open_interest",
            &[("underlyingAsset", "BTC"), ("expiration", "260925")],
            "GET",
            "/eapi/v1/openInterest",
        ),
        public(
            "get_options_mark_price",
            &[("product_symbol", OPT)],
            "GET",
            "/eapi/v1/mark",
        ),
        public(
            "get_options_orderbook",
            &[("product_symbol", OPT)],
            "GET",
            "/eapi/v1/depth",
        ),
        public(
            "get_options_block_trades",
            &[],
            "GET",
            "/eapi/v1/blockTrades",
        ),
        public(
            "get_options_trades",
            &[("product_symbol", OPT)],
            "GET",
            "/eapi/v1/trades",
        ),
        public("ping_options", &[], "GET", "/eapi/v1/ping"),
        public(
            "get_options_ticker",
            &[("product_symbol", OPT)],
            "GET",
            "/eapi/v1/ticker",
        ),
        private(
            "get_options_account_bill",
            &[("currency", "USDT")],
            "GET",
            "/eapi/v1/bill",
        ),
        private(
            "get_options_margin_account",
            &[],
            "GET",
            "/eapi/v1/marginAccount",
        ),
        private(
            "get_options_account_trades",
            &[("product_symbol", OPT)],
            "GET",
            "/eapi/v1/userTrades",
        ),
        private(
            "cancel_all_options_orders_by_underlying",
            &[("underlying", "BTCUSDT")],
            "DELETE",
            "/eapi/v1/allOpenOrdersByUnderlying",
        ),
        private(
            "cancel_all_options_orders",
            &[("product_symbol", OPT)],
            "DELETE",
            "/eapi/v1/allOpenOrders",
        ),
        private(
            "place_options_batch_orders",
            &[(
                "orders",
                r#"[{"symbol":"BTC-260925-100000-C","side":"BUY","type":"LIMIT","quantity":"1","price":"5"}]"#,
            )],
            "POST",
            "/eapi/v1/batchOrders",
        ),
        private(
            "cancel_options_batch_orders",
            &[("product_symbol", OPT), ("orderIds", "[1,2]")],
            "DELETE",
            "/eapi/v1/batchOrders",
        ),
        private(
            "get_options_order",
            &[("product_symbol", OPT), ("orderId", "1")],
            "GET",
            "/eapi/v1/order",
        ),
        private(
            "place_options_order",
            &[
                ("product_symbol", OPT),
                ("side", "BUY"),
                ("type", "LIMIT"),
                ("quantity", "1"),
                ("price", "5"),
                ("timeInForce", "GTC"),
            ],
            "POST",
            "/eapi/v1/order",
        ),
        private(
            "cancel_options_order",
            &[("product_symbol", OPT), ("orderId", "1")],
            "DELETE",
            "/eapi/v1/order",
        ),
        private("get_options_positions", &[], "GET", "/eapi/v1/position"),
        private("get_open_options_orders", &[], "GET", "/eapi/v1/openOrders"),
        private(
            "get_options_order_history",
            &[("product_symbol", OPT)],
            "GET",
            "/eapi/v1/historyOrders",
        ),
        private("get_options_commission", &[], "GET", "/eapi/v1/commission"),
        private(
            "get_options_exercise_records",
            &[],
            "GET",
            "/eapi/v1/exerciseRecord",
        ),
        private(
            "create_options_listen_key",
            &[],
            "POST",
            "/eapi/v1/listenKey",
        ),
        private(
            "keep_alive_options_listen_key",
            &[],
            "PUT",
            "/eapi/v1/listenKey",
        ),
        private(
            "close_options_listen_key",
            &[],
            "DELETE",
            "/eapi/v1/listenKey",
        ),
    ]);
}

#[test]
fn equity_routes_match_official_paths() {
    assert_cases(&[
        public(
            "get_equity_quote",
            &[("product_symbol", "AAPL-USDC-EQUITY")],
            "GET",
            "/sapi/v1/equity/market/quote",
        ),
        private(
            "place_equity_order",
            &[
                ("product_symbol", "AAPL-USDC-EQUITY"),
                ("side", "BUY"),
                ("orderType", "MARKET"),
                ("notional", "10"),
            ],
            "POST",
            "/sapi/v1/equity/order/place",
        ),
        public(
            "get_equity_exchange_info",
            &[],
            "GET",
            "/sapi/v1/equity/market/exchangeInfo",
        ),
        public(
            "get_equity_tokenized_assets",
            &[],
            "GET",
            "/sapi/v1/equity/market/tokenized-assets",
        ),
        private(
            "cancel_equity_order",
            &[("orderId", "1")],
            "POST",
            "/sapi/v1/equity/order/cancel",
        ),
        private(
            "cancel_all_equity_orders",
            &[],
            "POST",
            "/sapi/v1/equity/order/cancel-all",
        ),
        private(
            "get_open_equity_orders",
            &[],
            "GET",
            "/sapi/v1/equity/order/open-orders",
        ),
        private(
            "get_equity_order_history",
            &[("startTime", "1700000000000"), ("endTime", "1700086400000")],
            "GET",
            "/sapi/v1/equity/order/history",
        ),
        private(
            "get_equity_order_detail",
            &[("orderId", "1")],
            "GET",
            "/sapi/v1/equity/order/detail",
        ),
        private(
            "get_equity_trade_history",
            &[("startTime", "1700000000000"), ("endTime", "1700086400000")],
            "GET",
            "/sapi/v1/equity/trade/history",
        ),
        private(
            "mint_equity_token",
            &[("underlyingAsset", "AAPL"), ("underlyingAssetAmount", "1")],
            "POST",
            "/sapi/v1/equity/tokenized/mint",
        ),
        private(
            "redeem_equity_token",
            &[("tokenizedAsset", "AAPLON"), ("tokenizedAssetAmount", "1")],
            "POST",
            "/sapi/v1/equity/tokenized/redeem",
        ),
        private(
            "get_equity_convert_status",
            &[("issuerRequestId", "r1"), ("convertType", "MINT")],
            "GET",
            "/sapi/v1/equity/tokenized/convert-status",
        ),
        private(
            "get_equity_convert_history",
            &[],
            "GET",
            "/sapi/v1/equity/tokenized/history",
        ),
        private(
            "sign_equity_disclaimer",
            &[],
            "POST",
            "/sapi/v1/equity/account/disclaimer",
        ),
        private(
            "create_or_renew_equity_listen_key",
            &[],
            "POST",
            "/sapi/v1/equity/listenKey",
        ),
    ]);
}

#[test]
fn simple_earn_and_loan_routes_match_official_paths() {
    assert_cases(&[
        private(
            "get_simple_earn_account",
            &[],
            "GET",
            "/sapi/v1/simple-earn/account",
        ),
        private(
            "get_flexible_earn_products",
            &[],
            "GET",
            "/sapi/v1/simple-earn/flexible/list",
        ),
        private(
            "get_locked_earn_products",
            &[],
            "GET",
            "/sapi/v1/simple-earn/locked/list",
        ),
        private(
            "get_flexible_earn_positions",
            &[],
            "GET",
            "/sapi/v1/simple-earn/flexible/position",
        ),
        private(
            "get_locked_earn_positions",
            &[],
            "GET",
            "/sapi/v1/simple-earn/locked/position",
        ),
        private(
            "subscribe_flexible_earn",
            &[("productId", "USDT001"), ("amount", "1")],
            "POST",
            "/sapi/v1/simple-earn/flexible/subscribe",
        ),
        private(
            "subscribe_locked_earn",
            &[("projectId", "USDT*30"), ("amount", "1")],
            "POST",
            "/sapi/v1/simple-earn/locked/subscribe",
        ),
        private(
            "redeem_flexible_earn",
            &[("productId", "USDT001"), ("redeemAll", "true")],
            "POST",
            "/sapi/v1/simple-earn/flexible/redeem",
        ),
        private(
            "redeem_locked_earn",
            &[("positionId", "1")],
            "POST",
            "/sapi/v1/simple-earn/locked/redeem",
        ),
        private(
            "get_flexible_earn_subscription_history",
            &[],
            "GET",
            "/sapi/v1/simple-earn/flexible/history/subscriptionRecord",
        ),
        private(
            "get_locked_earn_subscription_history",
            &[],
            "GET",
            "/sapi/v1/simple-earn/locked/history/subscriptionRecord",
        ),
        private(
            "get_flexible_earn_redemption_history",
            &[],
            "GET",
            "/sapi/v1/simple-earn/flexible/history/redemptionRecord",
        ),
        private(
            "get_locked_earn_redemption_history",
            &[],
            "GET",
            "/sapi/v1/simple-earn/locked/history/redemptionRecord",
        ),
        private(
            "get_flexible_earn_rewards_history",
            &[("type", "BONUS")],
            "GET",
            "/sapi/v1/simple-earn/flexible/history/rewardsRecord",
        ),
        private(
            "get_locked_earn_rewards_history",
            &[],
            "GET",
            "/sapi/v1/simple-earn/locked/history/rewardsRecord",
        ),
        private(
            "check_flexible_loan_collateral_repay_rate",
            &[("loanCoin", "USDT"), ("collateralCoin", "BTC")],
            "GET",
            "/sapi/v2/loan/flexible/repay/rate",
        ),
        private(
            "adjust_flexible_loan_ltv",
            &[
                ("loanCoin", "USDT"),
                ("collateralCoin", "BTC"),
                ("adjustmentAmount", "1"),
                ("direction", "ADDITIONAL"),
            ],
            "POST",
            "/sapi/v2/loan/flexible/adjust/ltv",
        ),
        private(
            "borrow_flexible_loan",
            &[
                ("loanCoin", "USDT"),
                ("collateralCoin", "BTC"),
                ("loanAmount", "1"),
            ],
            "POST",
            "/sapi/v2/loan/flexible/borrow",
        ),
        private(
            "repay_flexible_loan",
            &[
                ("loanCoin", "USDT"),
                ("collateralCoin", "BTC"),
                ("repayAmount", "1"),
            ],
            "POST",
            "/sapi/v2/loan/flexible/repay",
        ),
        private(
            "get_flexible_loan_assets",
            &[],
            "GET",
            "/sapi/v2/loan/flexible/loanable/data",
        ),
        private(
            "get_flexible_loan_borrow_history",
            &[],
            "GET",
            "/sapi/v2/loan/flexible/borrow/history",
        ),
        private(
            "get_flexible_loan_collateral_assets",
            &[],
            "GET",
            "/sapi/v2/loan/flexible/collateral/data",
        ),
        private(
            "get_flexible_loan_interest_rate_history",
            &[("coin", "USDT")],
            "GET",
            "/sapi/v2/loan/interestRateHistory",
        ),
        private(
            "get_flexible_loan_liquidation_history",
            &[],
            "GET",
            "/sapi/v2/loan/flexible/liquidation/history",
        ),
        private(
            "get_flexible_loan_ltv_adjustment_history",
            &[],
            "GET",
            "/sapi/v2/loan/flexible/ltv/adjustment/history",
        ),
        private(
            "get_flexible_loan_ongoing_orders",
            &[],
            "GET",
            "/sapi/v2/loan/flexible/ongoing/orders",
        ),
        private(
            "get_flexible_loan_repayment_history",
            &[],
            "GET",
            "/sapi/v2/loan/flexible/repay/history",
        ),
        private(
            "get_crypto_loan_income_history",
            &[],
            "GET",
            "/sapi/v1/loan/income",
        ),
        private(
            "get_stable_loan_borrow_history",
            &[],
            "GET",
            "/sapi/v1/loan/borrow/history",
        ),
        private(
            "get_stable_loan_ltv_adjustment_history",
            &[],
            "GET",
            "/sapi/v1/loan/ltv/adjustment/history",
        ),
        private(
            "get_stable_loan_repayment_history",
            &[],
            "GET",
            "/sapi/v1/loan/repay/history",
        ),
    ]);
}

#[test]
fn staking_routes_match_official_paths() {
    assert_cases(&[
        private(
            "get_eth_staking_account",
            &[],
            "GET",
            "/sapi/v2/eth-staking/account",
        ),
        private(
            "get_eth_staking_quota",
            &[],
            "GET",
            "/sapi/v1/eth-staking/eth/quota",
        ),
        private(
            "get_eth_redemption_history",
            &[],
            "GET",
            "/sapi/v1/eth-staking/eth/history/redemptionHistory",
        ),
        private(
            "get_eth_staking_history",
            &[],
            "GET",
            "/sapi/v1/eth-staking/eth/history/stakingHistory",
        ),
        private(
            "get_wbeth_rate_history",
            &[],
            "GET",
            "/sapi/v1/eth-staking/eth/history/rateHistory",
        ),
        private(
            "get_wbeth_rewards_history",
            &[],
            "GET",
            "/sapi/v1/eth-staking/eth/history/wbethRewardsHistory",
        ),
        private(
            "get_wbeth_unwrap_history",
            &[],
            "GET",
            "/sapi/v1/eth-staking/wbeth/history/unwrapHistory",
        ),
        private(
            "get_wbeth_wrap_history",
            &[],
            "GET",
            "/sapi/v1/eth-staking/wbeth/history/wrapHistory",
        ),
        private(
            "redeem_eth_staking",
            &[("amount", "1")],
            "POST",
            "/sapi/v1/eth-staking/eth/redeem",
        ),
        private(
            "subscribe_eth_staking",
            &[("amount", "1")],
            "POST",
            "/sapi/v2/eth-staking/eth/stake",
        ),
        private(
            "wrap_beth",
            &[("amount", "1")],
            "POST",
            "/sapi/v1/eth-staking/wbeth/wrap",
        ),
        private(
            "get_onchain_yields_personal_quota",
            &[("projectId", "p1")],
            "GET",
            "/sapi/v1/onchain-yields/locked/personalLeftQuota",
        ),
        private(
            "get_onchain_yields_products",
            &[],
            "GET",
            "/sapi/v1/onchain-yields/locked/list",
        ),
        private(
            "get_onchain_yields_positions",
            &[],
            "GET",
            "/sapi/v1/onchain-yields/locked/position",
        ),
        private(
            "get_onchain_yields_redemption_history",
            &[],
            "GET",
            "/sapi/v1/onchain-yields/locked/history/redemptionRecord",
        ),
        private(
            "get_onchain_yields_rewards_history",
            &[],
            "GET",
            "/sapi/v1/onchain-yields/locked/history/rewardsRecord",
        ),
        private(
            "preview_onchain_yields_subscription",
            &[("projectId", "p1"), ("amount", "1")],
            "GET",
            "/sapi/v1/onchain-yields/locked/subscriptionPreview",
        ),
        private(
            "get_onchain_yields_subscription_history",
            &[],
            "GET",
            "/sapi/v1/onchain-yields/locked/history/subscriptionRecord",
        ),
        private(
            "get_onchain_yields_account",
            &[],
            "GET",
            "/sapi/v1/onchain-yields/account",
        ),
        private(
            "redeem_onchain_yields",
            &[("positionId", "1")],
            "POST",
            "/sapi/v1/onchain-yields/locked/redeem",
        ),
        private(
            "set_onchain_yields_auto_subscribe",
            &[("positionId", "1"), ("autoSubscribe", "true")],
            "POST",
            "/sapi/v1/onchain-yields/locked/setAutoSubscribe",
        ),
        private(
            "set_onchain_yields_redeem_option",
            &[("positionId", "1"), ("redeemTo", "SPOT")],
            "POST",
            "/sapi/v1/onchain-yields/locked/setRedeemOption",
        ),
        private(
            "subscribe_onchain_yields",
            &[("projectId", "p1"), ("amount", "1")],
            "POST",
            "/sapi/v1/onchain-yields/locked/subscribe",
        ),
        private(
            "get_soft_staking_products",
            &[],
            "GET",
            "/sapi/v1/soft-staking/list",
        ),
        private(
            "get_soft_staking_rewards_history",
            &[],
            "GET",
            "/sapi/v1/soft-staking/history/rewardsRecord",
        ),
        private(
            "set_soft_staking",
            &[("softStaking", "true")],
            "GET",
            "/sapi/v1/soft-staking/set",
        ),
        private(
            "claim_sol_boost_rewards",
            &[],
            "POST",
            "/sapi/v1/sol-staking/sol/claim",
        ),
        private(
            "get_bnsol_rate_history",
            &[],
            "GET",
            "/sapi/v1/sol-staking/sol/history/rateHistory",
        ),
        private(
            "get_bnsol_rewards_history",
            &[],
            "GET",
            "/sapi/v1/sol-staking/sol/history/bnsolRewardsHistory",
        ),
        private(
            "get_sol_boost_rewards_history",
            &[("type", "CLAIM")],
            "GET",
            "/sapi/v1/sol-staking/sol/history/boostRewardsHistory",
        ),
        private(
            "get_sol_redemption_history",
            &[],
            "GET",
            "/sapi/v1/sol-staking/sol/history/redemptionHistory",
        ),
        private(
            "get_sol_staking_history",
            &[],
            "GET",
            "/sapi/v1/sol-staking/sol/history/stakingHistory",
        ),
        private(
            "get_sol_staking_quota",
            &[],
            "GET",
            "/sapi/v1/sol-staking/sol/quota",
        ),
        private(
            "get_sol_unclaimed_rewards",
            &[],
            "GET",
            "/sapi/v1/sol-staking/sol/history/unclaimedRewards",
        ),
        private(
            "redeem_sol_staking",
            &[("amount", "1")],
            "POST",
            "/sapi/v1/sol-staking/sol/redeem",
        ),
        private(
            "get_sol_staking_account",
            &[],
            "GET",
            "/sapi/v1/sol-staking/account",
        ),
        private(
            "subscribe_sol_staking",
            &[("amount", "1")],
            "POST",
            "/sapi/v1/sol-staking/sol/stake",
        ),
    ]);
}

#[test]
fn subaccount_routes_match_official_paths() {
    const EMAIL: &str = "sub@example.com";
    assert_cases(&[
        private("get_subaccounts", &[], "GET", "/sapi/v1/sub-account/list"),
        private(
            "get_subaccount_status",
            &[],
            "GET",
            "/sapi/v1/sub-account/status",
        ),
        private(
            "get_subaccount_transaction_statistics",
            &[("email", EMAIL)],
            "GET",
            "/sapi/v1/sub-account/transaction-statistics",
        ),
        private(
            "get_subaccount_futures_position_risk",
            &[("email", EMAIL), ("futuresType", "1")],
            "GET",
            "/sapi/v2/sub-account/futures/positionRisk",
        ),
        private(
            "get_subaccount_futures_account",
            &[("email", EMAIL), ("futuresType", "1")],
            "GET",
            "/sapi/v2/sub-account/futures/account",
        ),
        private(
            "get_subaccount_margin_account",
            &[("email", EMAIL)],
            "GET",
            "/sapi/v1/sub-account/margin/account",
        ),
        private(
            "get_subaccount_futures_summary",
            &[("futuresType", "1")],
            "GET",
            "/sapi/v2/sub-account/futures/accountSummary",
        ),
        private(
            "get_subaccount_margin_summary",
            &[],
            "GET",
            "/sapi/v1/sub-account/margin/accountSummary",
        ),
        private(
            "get_subaccount_assets",
            &[("email", EMAIL)],
            "GET",
            "/sapi/v4/sub-account/assets",
        ),
        private(
            "get_subaccount_spot_summary",
            &[],
            "GET",
            "/sapi/v1/sub-account/spotSummary",
        ),
        private(
            "transfer_subaccount_futures",
            &[
                ("email", EMAIL),
                ("asset", "USDT"),
                ("amount", "1"),
                ("type", "1"),
            ],
            "POST",
            "/sapi/v1/sub-account/futures/transfer",
        ),
        private(
            "transfer_subaccount_margin",
            &[
                ("email", EMAIL),
                ("asset", "USDT"),
                ("amount", "1"),
                ("type", "1"),
            ],
            "POST",
            "/sapi/v1/sub-account/margin/transfer",
        ),
        private(
            "get_subaccount_futures_transfer_history",
            &[("email", EMAIL), ("futuresType", "1")],
            "GET",
            "/sapi/v1/sub-account/futures/internalTransfer",
        ),
        private(
            "transfer_between_subaccount_futures",
            &[
                ("fromEmail", EMAIL),
                ("toEmail", "other@example.com"),
                ("futuresType", "1"),
                ("asset", "USDT"),
                ("amount", "1"),
            ],
            "POST",
            "/sapi/v1/sub-account/futures/internalTransfer",
        ),
        private(
            "get_subaccount_spot_transfer_history",
            &[],
            "GET",
            "/sapi/v1/sub-account/sub/transfer/history",
        ),
        private(
            "get_subaccount_universal_transfer_history",
            &[],
            "GET",
            "/sapi/v1/sub-account/universalTransfer",
        ),
        private(
            "transfer_between_subaccounts",
            &[
                ("fromAccountType", "SPOT"),
                ("toAccountType", "USDT_FUTURE"),
                ("asset", "USDT"),
                ("amount", "1"),
            ],
            "POST",
            "/sapi/v1/sub-account/universalTransfer",
        ),
        private(
            "get_subaccount_transfer_history",
            &[],
            "GET",
            "/sapi/v1/sub-account/transfer/subUserHistory",
        ),
        private(
            "transfer_subaccount_to_master",
            &[("asset", "USDT"), ("amount", "1")],
            "POST",
            "/sapi/v1/sub-account/transfer/subToMaster",
        ),
        private(
            "transfer_subaccount_to_subaccount",
            &[("toEmail", EMAIL), ("asset", "USDT"), ("amount", "1")],
            "POST",
            "/sapi/v1/sub-account/transfer/subToSub",
        ),
    ]);
}

#[test]
fn portfolio_margin_account_routes_match_official_paths() {
    assert_cases(&[
        private("get_pm_account", &[], "GET", "/papi/v1/account"),
        private("get_pm_balance", &[], "GET", "/papi/v1/balance"),
        private("get_pm_um_account", &[], "GET", "/papi/v1/um/account"),
        private("get_pm_cm_account", &[], "GET", "/papi/v1/cm/account"),
        private(
            "get_pm_um_position_risk",
            &[],
            "GET",
            "/papi/v1/um/positionRisk",
        ),
        private(
            "get_pm_cm_position_risk",
            &[],
            "GET",
            "/papi/v1/cm/positionRisk",
        ),
        private(
            "get_pm_um_account_config",
            &[],
            "GET",
            "/papi/v1/um/accountConfig",
        ),
        private(
            "get_pm_um_symbol_config",
            &[],
            "GET",
            "/papi/v1/um/symbolConfig",
        ),
        private(
            "get_pm_um_leverage_bracket",
            &[],
            "GET",
            "/papi/v1/um/leverageBracket",
        ),
        private(
            "get_pm_cm_leverage_bracket",
            &[],
            "GET",
            "/papi/v1/cm/leverageBracket",
        ),
        private(
            "get_pm_um_api_trading_status",
            &[],
            "GET",
            "/papi/v1/um/apiTradingStatus",
        ),
        private(
            "get_pm_um_adl_quantile",
            &[],
            "GET",
            "/papi/v1/um/adlQuantile",
        ),
        private(
            "get_pm_cm_adl_quantile",
            &[("product_symbol", "BTCUSD_PERP")],
            "GET",
            "/papi/v1/cm/adlQuantile",
        ),
        private(
            "get_pm_margin_max_borrowable",
            &[("asset", "USDT")],
            "GET",
            "/papi/v1/margin/maxBorrowable",
        ),
        private(
            "get_pm_um_force_orders",
            &[],
            "GET",
            "/papi/v1/um/forceOrders",
        ),
        private(
            "get_pm_cm_force_orders",
            &[],
            "GET",
            "/papi/v1/cm/forceOrders",
        ),
        private(
            "get_pm_margin_force_orders",
            &[],
            "GET",
            "/papi/v1/margin/forceOrders",
        ),
        private(
            "borrow_pm_margin",
            &[("asset", "USDT"), ("amount", "1")],
            "POST",
            "/papi/v1/marginLoan",
        ),
        private(
            "repay_pm_margin",
            &[("asset", "USDT"), ("amount", "1")],
            "POST",
            "/papi/v1/repayLoan",
        ),
        private(
            "repay_pm_margin_debt",
            &[("asset", "USDT")],
            "POST",
            "/papi/v1/margin/repay-debt",
        ),
        private(
            "set_pm_um_leverage",
            &[("product_symbol", SWAP), ("leverage", "5")],
            "POST",
            "/papi/v1/um/leverage",
        ),
        private(
            "set_pm_cm_leverage",
            &[("product_symbol", "BTCUSD_PERP"), ("leverage", "5")],
            "POST",
            "/papi/v1/cm/leverage",
        ),
        private(
            "get_pm_um_position_mode",
            &[],
            "GET",
            "/papi/v1/um/positionSide/dual",
        ),
        private(
            "get_pm_cm_position_mode",
            &[],
            "GET",
            "/papi/v1/cm/positionSide/dual",
        ),
        private(
            "set_pm_um_position_mode",
            &[("dualSidePosition", "true")],
            "POST",
            "/papi/v1/um/positionSide/dual",
        ),
        private(
            "set_pm_cm_position_mode",
            &[("dualSidePosition", "false")],
            "POST",
            "/papi/v1/cm/positionSide/dual",
        ),
    ]);
}

#[test]
fn portfolio_margin_trading_routes_match_official_paths() {
    const CM: &str = "BTCUSD_PERP";
    assert_cases(&[
        private(
            "place_pm_um_order",
            &[
                ("product_symbol", SWAP),
                ("side", "BUY"),
                ("type_", "MARKET"),
                ("quantity", "1"),
            ],
            "POST",
            "/papi/v1/um/order",
        ),
        private(
            "get_pm_um_order",
            &[("product_symbol", SWAP), ("orderId", "1")],
            "GET",
            "/papi/v1/um/order",
        ),
        private(
            "cancel_pm_um_order",
            &[("product_symbol", SWAP), ("orderId", "1")],
            "DELETE",
            "/papi/v1/um/order",
        ),
        private(
            "modify_pm_um_order",
            &[
                ("product_symbol", SWAP),
                ("orderId", "1"),
                ("side", "BUY"),
                ("quantity", "1"),
                ("price", "100"),
            ],
            "PUT",
            "/papi/v1/um/order",
        ),
        private(
            "get_pm_um_open_orders",
            &[],
            "GET",
            "/papi/v1/um/openOrders",
        ),
        private(
            "cancel_all_pm_um_orders",
            &[("product_symbol", SWAP)],
            "DELETE",
            "/papi/v1/um/allOpenOrders",
        ),
        private(
            "get_pm_um_all_orders",
            &[("product_symbol", SWAP)],
            "GET",
            "/papi/v1/um/allOrders",
        ),
        private(
            "get_pm_um_user_trades",
            &[("product_symbol", SWAP)],
            "GET",
            "/papi/v1/um/userTrades",
        ),
        private(
            "get_pm_um_order_amendments",
            &[("product_symbol", SWAP), ("orderId", "1")],
            "GET",
            "/papi/v1/um/orderAmendment",
        ),
        private(
            "place_pm_um_algo_order",
            &[
                ("product_symbol", SWAP),
                ("side", "SELL"),
                ("type_", "STOP_MARKET"),
                ("quantity", "1"),
                ("triggerPrice", "90"),
            ],
            "POST",
            "/papi/v1/um/algo/order",
        ),
        private(
            "get_pm_um_algo_order",
            &[("algoId", "1")],
            "GET",
            "/papi/v1/um/algo/algoOrder",
        ),
        private(
            "cancel_pm_um_algo_order",
            &[("algoId", "1")],
            "DELETE",
            "/papi/v1/um/algo/order",
        ),
        private(
            "cancel_all_pm_um_algo_orders",
            &[("product_symbol", SWAP)],
            "DELETE",
            "/papi/v1/um/algo/allOpenOrders",
        ),
        private(
            "get_pm_um_open_algo_orders",
            &[],
            "GET",
            "/papi/v1/um/algo/openAlgoOrders",
        ),
        private(
            "get_pm_um_algo_order_history",
            &[("product_symbol", SWAP)],
            "GET",
            "/papi/v1/um/algo/allAlgoOrders",
        ),
        private(
            "place_pm_cm_order",
            &[
                ("product_symbol", CM),
                ("side", "BUY"),
                ("type_", "LIMIT"),
                ("quantity", "1"),
                ("price", "100"),
                ("timeInForce", "GTC"),
            ],
            "POST",
            "/papi/v1/cm/order",
        ),
        private(
            "get_pm_cm_order",
            &[("product_symbol", CM), ("orderId", "1")],
            "GET",
            "/papi/v1/cm/order",
        ),
        private(
            "cancel_pm_cm_order",
            &[("product_symbol", CM), ("orderId", "1")],
            "DELETE",
            "/papi/v1/cm/order",
        ),
        private(
            "modify_pm_cm_order",
            &[
                ("product_symbol", CM),
                ("orderId", "1"),
                ("side", "BUY"),
                ("quantity", "1"),
                ("price", "100"),
            ],
            "PUT",
            "/papi/v1/cm/order",
        ),
        private(
            "get_pm_cm_open_orders",
            &[],
            "GET",
            "/papi/v1/cm/openOrders",
        ),
        private(
            "cancel_all_pm_cm_orders",
            &[("product_symbol", CM)],
            "DELETE",
            "/papi/v1/cm/allOpenOrders",
        ),
        private(
            "get_pm_cm_all_orders",
            &[("product_symbol", CM)],
            "GET",
            "/papi/v1/cm/allOrders",
        ),
        private(
            "get_pm_cm_user_trades",
            &[("product_symbol", CM)],
            "GET",
            "/papi/v1/cm/userTrades",
        ),
        private(
            "get_pm_cm_order_amendments",
            &[("product_symbol", CM), ("orderId", "1")],
            "GET",
            "/papi/v1/cm/orderAmendment",
        ),
        private(
            "place_pm_cm_conditional_order",
            &[
                ("product_symbol", CM),
                ("side", "SELL"),
                ("strategyType", "STOP_MARKET"),
                ("quantity", "1"),
                ("stopPrice", "90"),
            ],
            "POST",
            "/papi/v1/cm/conditional/order",
        ),
        private(
            "cancel_pm_cm_conditional_order",
            &[("product_symbol", CM), ("strategyId", "1")],
            "DELETE",
            "/papi/v1/cm/conditional/order",
        ),
        private(
            "cancel_all_pm_cm_conditional_orders",
            &[("product_symbol", CM)],
            "DELETE",
            "/papi/v1/cm/conditional/allOpenOrders",
        ),
        private(
            "get_pm_cm_conditional_order",
            &[("product_symbol", CM), ("strategyId", "1")],
            "GET",
            "/papi/v1/cm/conditional/openOrder",
        ),
        private(
            "get_pm_cm_conditional_order_history",
            &[("product_symbol", CM), ("strategyId", "1")],
            "GET",
            "/papi/v1/cm/conditional/orderHistory",
        ),
        private(
            "get_pm_cm_open_conditional_orders",
            &[],
            "GET",
            "/papi/v1/cm/conditional/openOrders",
        ),
        private(
            "get_pm_cm_all_conditional_orders",
            &[],
            "GET",
            "/papi/v1/cm/conditional/allOrders",
        ),
        private(
            "place_pm_margin_order",
            &[
                ("product_symbol", SPOT),
                ("side", "BUY"),
                ("type_", "MARKET"),
                ("quantity", "1"),
            ],
            "POST",
            "/papi/v1/margin/order",
        ),
        private(
            "get_pm_margin_order",
            &[("product_symbol", SPOT), ("orderId", "1")],
            "GET",
            "/papi/v1/margin/order",
        ),
        private(
            "cancel_pm_margin_order",
            &[("product_symbol", SPOT), ("orderId", "1")],
            "DELETE",
            "/papi/v1/margin/order",
        ),
        private(
            "get_pm_margin_open_orders",
            &[("product_symbol", SPOT)],
            "GET",
            "/papi/v1/margin/openOrders",
        ),
        private(
            "cancel_all_pm_margin_orders",
            &[("product_symbol", SPOT)],
            "DELETE",
            "/papi/v1/margin/allOpenOrders",
        ),
        private(
            "get_pm_margin_all_orders",
            &[("product_symbol", SPOT)],
            "GET",
            "/papi/v1/margin/allOrders",
        ),
        private(
            "get_pm_margin_trades",
            &[("product_symbol", SPOT)],
            "GET",
            "/papi/v1/margin/myTrades",
        ),
        private(
            "place_pm_margin_oco",
            &[
                ("product_symbol", SPOT),
                ("side", "SELL"),
                ("quantity", "1"),
                ("price", "110"),
                ("stopPrice", "90"),
            ],
            "POST",
            "/papi/v1/margin/order/oco",
        ),
        private(
            "get_pm_margin_oco",
            &[("orderListId", "1")],
            "GET",
            "/papi/v1/margin/orderList",
        ),
        private(
            "cancel_pm_margin_oco",
            &[("product_symbol", SPOT), ("orderListId", "1")],
            "DELETE",
            "/papi/v1/margin/orderList",
        ),
        private(
            "get_pm_margin_open_oco",
            &[],
            "GET",
            "/papi/v1/margin/openOrderList",
        ),
        private(
            "get_pm_margin_all_oco",
            &[],
            "GET",
            "/papi/v1/margin/allOrderList",
        ),
    ]);
}

#[test]
fn trading_controls_use_documented_routes() {
    assert_cases(&[
        private(
            "create_coin_futures_listen_key",
            &[],
            "POST",
            "/dapi/v1/listenKey",
        ),
        private(
            "keep_alive_coin_futures_listen_key",
            &[],
            "PUT",
            "/dapi/v1/listenKey",
        ),
        private(
            "close_coin_futures_listen_key",
            &[],
            "DELETE",
            "/dapi/v1/listenKey",
        ),
        private("create_pm_listen_key", &[], "POST", "/papi/v1/listenKey"),
        private("keep_alive_pm_listen_key", &[], "PUT", "/papi/v1/listenKey"),
        private("close_pm_listen_key", &[], "DELETE", "/papi/v1/listenKey"),
        private(
            "cancel_replace_spot_order",
            &[
                ("product_symbol", "BTC-USDT-SPOT"),
                ("side", "BUY"),
                ("type", "MARKET"),
                ("cancelReplaceMode", "STOP_ON_FAILURE"),
                ("quantity", "1"),
                ("cancelOrderId", "123"),
            ],
            "POST",
            "/api/v3/order/cancelReplace",
        ),
        private(
            "place_futures_batch_orders",
            &[(
                "batchOrders",
                "[{\"product_symbol\":\"BTC-USDT-SWAP\",\"side\":\"BUY\",\"quantity\":\"1\",\"type\":\"MARKET\"}]",
            )],
            "POST",
            "/fapi/v1/batchOrders",
        ),
        private(
            "amend_futures_batch_orders",
            &[(
                "batchOrders",
                "[{\"product_symbol\":\"BTC-USDT-SWAP\",\"side\":\"BUY\",\"quantity\":\"1\",\"priceMatch\":\"QUEUE\",\"orderId\":1}]",
            )],
            "PUT",
            "/fapi/v1/batchOrders",
        ),
        private(
            "cancel_futures_batch_orders",
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("orderIdList", "[1,2]"),
            ],
            "DELETE",
            "/fapi/v1/batchOrders",
        ),
        private(
            "place_coin_futures_batch_orders",
            &[(
                "batchOrders",
                "[{\"symbol\":\"BTCUSD_PERP\",\"side\":\"BUY\",\"quantity\":\"1\",\"type\":\"MARKET\"}]",
            )],
            "POST",
            "/dapi/v1/batchOrders",
        ),
        private(
            "amend_coin_futures_batch_orders",
            &[(
                "batchOrders",
                "[{\"symbol\":\"BTCUSD_PERP\",\"side\":\"BUY\",\"quantity\":\"1\",\"priceMatch\":\"QUEUE\",\"orderId\":1}]",
            )],
            "PUT",
            "/dapi/v1/batchOrders",
        ),
        private(
            "cancel_coin_futures_batch_orders",
            &[("symbol", "BTCUSD_PERP"), ("orderIdList", "[1,2]")],
            "DELETE",
            "/dapi/v1/batchOrders",
        ),
        private(
            "get_spot_order_list",
            &[("orderListId", "1")],
            "GET",
            "/api/v3/orderList",
        ),
        private(
            "get_spot_all_order_lists",
            &[("limit", "20")],
            "GET",
            "/api/v3/allOrderList",
        ),
        private(
            "get_spot_open_order_lists",
            &[],
            "GET",
            "/api/v3/openOrderList",
        ),
        private(
            "cancel_spot_order_list",
            &[
                ("product_symbol", "BTC-USDT-SPOT"),
                ("listClientOrderId", "list-1"),
            ],
            "DELETE",
            "/api/v3/orderList",
        ),
        private(
            "amend_spot_order_keep_priority",
            &[
                ("product_symbol", "BTC-USDT-SPOT"),
                ("newQty", "0.1"),
                ("orderId", "1"),
                ("recvWindow", "5000.125"),
            ],
            "PUT",
            "/api/v3/order/amend/keepPriority",
        ),
        private(
            "get_futures_position_mode",
            &[],
            "GET",
            "/fapi/v1/positionSide/dual",
        ),
        private(
            "set_futures_position_mode",
            &[("dualSidePosition", "true")],
            "POST",
            "/fapi/v1/positionSide/dual",
        ),
        private(
            "set_futures_margin_type",
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("marginType", "ISOLATED"),
            ],
            "POST",
            "/fapi/v1/marginType",
        ),
        private(
            "set_futures_cancel_countdown",
            &[("product_symbol", "BTC-USDT-SWAP"), ("countdownTime", "0")],
            "POST",
            "/fapi/v1/countdownCancelAll",
        ),
        private(
            "get_futures_leverage_brackets",
            &[("product_symbol", "BTC-USDT-SWAP")],
            "GET",
            "/fapi/v1/leverageBracket",
        ),
        private(
            "amend_futures_order",
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("side", "BUY"),
                ("quantity", "1"),
                ("price", "60000"),
                ("orderId", "42"),
            ],
            "PUT",
            "/fapi/v1/order",
        ),
        private(
            "get_coin_futures_position_mode",
            &[],
            "GET",
            "/dapi/v1/positionSide/dual",
        ),
        private(
            "set_coin_futures_position_mode",
            &[("dualSidePosition", "true")],
            "POST",
            "/dapi/v1/positionSide/dual",
        ),
        private(
            "set_coin_futures_margin_type",
            &[("symbol", "BTCUSD_PERP"), ("marginType", "ISOLATED")],
            "POST",
            "/dapi/v1/marginType",
        ),
        private(
            "set_coin_futures_cancel_countdown",
            &[("symbol", "BTCUSD_PERP"), ("countdownTime", "0")],
            "POST",
            "/dapi/v1/countdownCancelAll",
        ),
        private(
            "get_coin_futures_leverage_brackets",
            &[("symbol", "BTCUSD_PERP")],
            "GET",
            "/dapi/v2/leverageBracket",
        ),
        private(
            "amend_coin_futures_order",
            &[
                ("symbol", "BTCUSD_PERP"),
                ("side", "BUY"),
                ("quantity", "1"),
                ("price", "60000"),
                ("orderId", "42"),
            ],
            "PUT",
            "/dapi/v1/order",
        ),
        private(
            "set_coin_futures_leverage",
            &[("symbol", "BTCUSD_PERP"), ("leverage", "5")],
            "POST",
            "/dapi/v1/leverage",
        ),
        private(
            "get_coin_futures_pair_leverage_brackets",
            &[("pair", "BTCUSD")],
            "GET",
            "/dapi/v1/leverageBracket",
        ),
        private(
            "get_coin_futures_all_orders",
            &[("symbol", "BTCUSD_PERP"), ("limit", "20")],
            "GET",
            "/dapi/v1/allOrders",
        ),
        private(
            "get_coin_futures_account_trades",
            &[("symbol", "BTCUSD_PERP"), ("limit", "20")],
            "GET",
            "/dapi/v1/userTrades",
        ),
    ]);
}

#[test]
fn additional_risk_endpoints_use_documented_routes() {
    assert_cases(&[
        private(
            "get_coin_futures_income_history",
            &[("symbol", "BTCUSD_PERP")],
            "GET",
            "/dapi/v1/income",
        ),
        private(
            "get_coin_futures_commission_rate",
            &[("symbol", "BTCUSD_PERP")],
            "GET",
            "/dapi/v1/commissionRate",
        ),
        public(
            "get_coin_futures_aggregate_trades",
            &[("symbol", "BTCUSD_PERP")],
            "GET",
            "/dapi/v1/aggTrades",
        ),
        public(
            "get_coin_futures_continuous_klines",
            &[
                ("pair", "BTCUSD"),
                ("contractType", "PERPETUAL"),
                ("interval", "1m"),
            ],
            "GET",
            "/dapi/v1/continuousKlines",
        ),
        public(
            "get_coin_futures_funding_info",
            &[],
            "GET",
            "/dapi/v1/fundingInfo",
        ),
        public(
            "get_coin_futures_index_price_klines",
            &[("pair", "BTCUSD"), ("interval", "1m")],
            "GET",
            "/dapi/v1/indexPriceKlines",
        ),
        public(
            "get_coin_futures_mark_price_klines",
            &[("symbol", "BTCUSD_PERP"), ("interval", "1m")],
            "GET",
            "/dapi/v1/markPriceKlines",
        ),
        public(
            "get_coin_futures_open_interest",
            &[("symbol", "BTCUSD_PERP")],
            "GET",
            "/dapi/v1/openInterest",
        ),
        public(
            "get_coin_futures_premium_index_klines",
            &[("symbol", "BTCUSD_PERP"), ("interval", "1m")],
            "GET",
            "/dapi/v1/premiumIndexKlines",
        ),
        public(
            "get_coin_futures_book_ticker",
            &[("symbol", "BTCUSD_PERP")],
            "GET",
            "/dapi/v1/ticker/bookTicker",
        ),
        public(
            "get_coin_futures_24h_ticker",
            &[("symbol", "BTCUSD_PERP")],
            "GET",
            "/dapi/v1/ticker/24hr",
        ),
        private(
            "adjust_coin_futures_position_margin",
            &[("symbol", "BTCUSD_PERP"), ("amount", "1.25"), ("type", "1")],
            "POST",
            "/dapi/v1/positionMargin",
        ),
        private(
            "get_coin_futures_adl_quantiles",
            &[("symbol", "BTCUSD_PERP")],
            "GET",
            "/dapi/v1/adlQuantile",
        ),
        private(
            "get_coin_futures_force_orders",
            &[("symbol", "BTCUSD_PERP")],
            "GET",
            "/dapi/v1/forceOrders",
        ),
        private(
            "get_pm_coin_income_history",
            &[("symbol", "BTCUSD_PERP")],
            "GET",
            "/papi/v1/cm/income",
        ),
        private(
            "get_pm_margin_interest_history",
            &[("recvWindow", "5000")],
            "GET",
            "/papi/v1/margin/marginInterestHistory",
        ),
        private(
            "get_pm_futures_income_history",
            &[("product_symbol", "BTC-USDT-SWAP")],
            "GET",
            "/papi/v1/um/income",
        ),
        private(
            "get_pm_coin_commission_rate",
            &[("symbol", "BTCUSD_PERP")],
            "GET",
            "/papi/v1/cm/commissionRate",
        ),
        private(
            "get_pm_futures_commission_rate",
            &[("product_symbol", "BTC-USDT-SWAP")],
            "GET",
            "/papi/v1/um/commissionRate",
        ),
        private(
            "get_pm_margin_loan_records",
            &[("asset", "USDT"), ("txId", "1")],
            "GET",
            "/papi/v1/margin/marginLoan",
        ),
        private(
            "get_pm_margin_transferable_amount",
            &[("asset", "USDT")],
            "GET",
            "/papi/v1/margin/maxWithdraw",
        ),
        private(
            "get_pm_margin_repayment_records",
            &[("asset", "USDT"), ("txId", "1")],
            "GET",
            "/papi/v1/margin/repayLoan",
        ),
        private(
            "get_pm_order_rate_limits",
            &[("recvWindow", "5000")],
            "GET",
            "/papi/v1/rateLimit/order",
        ),
        private(
            "get_futures_account_config",
            &[("recvWindow", "5000")],
            "GET",
            "/fapi/v1/accountConfig",
        ),
        private(
            "get_futures_trading_status",
            &[("product_symbol", "BTC-USDT-SWAP")],
            "GET",
            "/fapi/v1/apiTradingStatus",
        ),
        private(
            "get_futures_multi_assets_mode",
            &[("recvWindow", "5000")],
            "GET",
            "/fapi/v1/multiAssetsMargin",
        ),
        private(
            "get_futures_order_rate_limits",
            &[("recvWindow", "5000")],
            "GET",
            "/fapi/v1/rateLimit/order",
        ),
        private(
            "get_futures_symbol_config",
            &[("product_symbol", "BTC-USDT-SWAP")],
            "GET",
            "/fapi/v1/symbolConfig",
        ),
        public(
            "get_futures_aggregate_trades",
            &[("product_symbol", "BTC-USDT-SWAP")],
            "GET",
            "/fapi/v1/aggTrades",
        ),
        public(
            "get_futures_continuous_klines",
            &[
                ("pair", "BTCUSDT"),
                ("contractType", "PERPETUAL"),
                ("interval", "1m"),
            ],
            "GET",
            "/fapi/v1/continuousKlines",
        ),
        public(
            "get_futures_funding_info",
            &[],
            "GET",
            "/fapi/v1/fundingInfo",
        ),
        public(
            "get_futures_index_price_klines",
            &[("pair", "BTCUSDT"), ("interval", "1m")],
            "GET",
            "/fapi/v1/indexPriceKlines",
        ),
        public(
            "get_futures_mark_price_klines",
            &[("product_symbol", "BTC-USDT-SWAP"), ("interval", "1m")],
            "GET",
            "/fapi/v1/markPriceKlines",
        ),
        public(
            "get_futures_premium_index_klines",
            &[("product_symbol", "BTC-USDT-SWAP"), ("interval", "1m")],
            "GET",
            "/fapi/v1/premiumIndexKlines",
        ),
        public(
            "get_futures_recent_trades",
            &[("product_symbol", "BTC-USDT-SWAP")],
            "GET",
            "/fapi/v1/trades",
        ),
        public(
            "get_futures_price_ticker_v1",
            &[("product_symbol", "BTC-USDT-SWAP")],
            "GET",
            "/fapi/v1/ticker/price",
        ),
        public(
            "get_futures_price_ticker",
            &[("product_symbol", "BTC-USDT-SWAP")],
            "GET",
            "/fapi/v2/ticker/price",
        ),
        public(
            "get_futures_24h_ticker",
            &[("product_symbol", "BTC-USDT-SWAP")],
            "GET",
            "/fapi/v1/ticker/24hr",
        ),
        private(
            "set_futures_multi_assets_mode",
            &[("multiAssetsMargin", "true")],
            "POST",
            "/fapi/v1/multiAssetsMargin",
        ),
        private(
            "adjust_futures_position_margin",
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("amount", "1.25"),
                ("type", "1"),
            ],
            "POST",
            "/fapi/v1/positionMargin",
        ),
        private(
            "get_futures_adl_quantiles",
            &[("product_symbol", "BTC-USDT-SWAP")],
            "GET",
            "/fapi/v1/adlQuantile",
        ),
        private(
            "get_futures_force_orders",
            &[("product_symbol", "BTC-USDT-SWAP")],
            "GET",
            "/fapi/v1/forceOrders",
        ),
        private(
            "get_margin_risk_coefficients",
            &[("recvWindow", "5000")],
            "GET",
            "/sapi/v1/margin/tradeCoeff",
        ),
        private(
            "get_margin_capital_flow",
            &[("product_symbol", "BTC-USDT-SPOT")],
            "GET",
            "/sapi/v1/margin/capital-flow",
        ),
        public(
            "get_margin_delist_schedule",
            &[("recvWindow", "5000")],
            "GET",
            "/sapi/v1/margin/delist-schedule",
        ),
        private(
            "get_margin_liquidation_records",
            &[("recvWindow", "5000")],
            "GET",
            "/sapi/v1/margin/forceLiquidationRec",
        ),
        private(
            "cancel_margin_order_list",
            &[("product_symbol", "BTC-USDT-SPOT"), ("orderListId", "1")],
            "DELETE",
            "/sapi/v1/margin/orderList",
        ),
        private(
            "get_margin_order_rate_limits",
            &[("product_symbol", "BTC-USDT-SPOT")],
            "GET",
            "/sapi/v1/margin/rateLimit/order",
        ),
        private(
            "get_margin_all_order_lists",
            &[("product_symbol", "BTC-USDT-SPOT")],
            "GET",
            "/sapi/v1/margin/allOrderList",
        ),
        private(
            "get_margin_order_list",
            &[("orderListId", "1")],
            "GET",
            "/sapi/v1/margin/orderList",
        ),
        private(
            "get_margin_open_order_lists",
            &[("product_symbol", "BTC-USDT-SPOT")],
            "GET",
            "/sapi/v1/margin/openOrderList",
        ),
        private(
            "close_margin_listen_key",
            &[],
            "DELETE",
            "/sapi/v1/margin/listen-key",
        ),
        private(
            "keep_alive_margin_listen_key",
            &[("listenKey", "listen-token")],
            "PUT",
            "/sapi/v1/margin/listen-key",
        ),
        private(
            "create_margin_listen_key",
            &[],
            "POST",
            "/sapi/v1/margin/listen-key",
        ),
        public(
            "get_spot_aggregate_trades",
            &[("product_symbol", "BTC-USDT-SPOT")],
            "GET",
            "/api/v3/aggTrades",
        ),
        public(
            "get_spot_average_price",
            &[("product_symbol", "BTC-USDT-SPOT")],
            "GET",
            "/api/v3/avgPrice",
        ),
        public(
            "get_spot_24h_ticker",
            &[("product_symbol", "BTC-USDT-SPOT")],
            "GET",
            "/api/v3/ticker/24hr",
        ),
        public(
            "get_spot_book_ticker",
            &[("product_symbol", "BTC-USDT-SPOT")],
            "GET",
            "/api/v3/ticker/bookTicker",
        ),
        private(
            "get_account_trading_status",
            &[("recvWindow", "5000")],
            "GET",
            "/sapi/v1/account/apiTradingStatus",
        ),
        private(
            "get_account_status",
            &[("recvWindow", "5000")],
            "GET",
            "/sapi/v1/account/status",
        ),
        private(
            "get_api_key_permissions",
            &[("recvWindow", "5000")],
            "GET",
            "/sapi/v1/account/apiRestrictions",
        ),
        private(
            "get_spot_trade_fees",
            &[("product_symbol", "BTC-USDT-SPOT")],
            "GET",
            "/sapi/v1/asset/tradeFee",
        ),
        private(
            "get_user_assets",
            &[("recvWindow", "5000")],
            "POST",
            "/sapi/v3/asset/getUserAsset",
        ),
        private(
            "get_coin_network_config",
            &[("recvWindow", "5000")],
            "GET",
            "/sapi/v1/capital/config/getall",
        ),
        private(
            "get_deposit_address",
            &[("coin", "BTC")],
            "GET",
            "/sapi/v1/capital/deposit/address",
        ),
        private(
            "get_deposit_history",
            &[("recvWindow", "5000")],
            "GET",
            "/sapi/v1/capital/deposit/hisrec",
        ),
        public(
            "get_spot_delist_schedule",
            &[("recvWindow", "5000")],
            "GET",
            "/sapi/v1/spot/delist-schedule",
        ),
        public("get_system_status", &[], "GET", "/sapi/v1/system/status"),
    ]);
}

#[test]
fn new_order_lists_use_documented_routes() {
    assert_cases(&[
        private(
            "place_margin_oco",
            &[
                ("product_symbol", "BTC-USDT-SPOT"),
                ("side", "SELL"),
                ("quantity", "1"),
                ("price", "110"),
                ("stopPrice", "90"),
            ],
            "POST",
            "/sapi/v1/margin/order/oco",
        ),
        private(
            "place_margin_oto",
            &[
                ("product_symbol", "BTC-USDT-SPOT"),
                ("workingType", "LIMIT"),
                ("workingSide", "BUY"),
                ("workingPrice", "100"),
                ("workingQuantity", "1"),
                ("workingIcebergQty", "0.5"),
                ("pendingType", "MARKET"),
                ("pendingSide", "SELL"),
                ("pendingQuantity", "1"),
                ("workingTimeInForce", "GTC"),
            ],
            "POST",
            "/sapi/v1/margin/order/oto",
        ),
        private(
            "place_margin_otoco",
            &[
                ("product_symbol", "BTC-USDT-SPOT"),
                ("workingType", "LIMIT"),
                ("workingSide", "BUY"),
                ("workingPrice", "100"),
                ("workingQuantity", "1"),
                ("pendingSide", "SELL"),
                ("pendingQuantity", "1"),
                ("pendingAboveType", "LIMIT_MAKER"),
                ("workingTimeInForce", "GTC"),
                ("pendingAbovePrice", "110"),
                ("pendingBelowType", "STOP_LOSS"),
                ("pendingBelowStopPrice", "90"),
            ],
            "POST",
            "/sapi/v1/margin/order/otoco",
        ),
        private(
            "place_spot_opo",
            &[
                ("product_symbol", "BTC-USDT-SPOT"),
                ("workingType", "LIMIT"),
                ("workingSide", "BUY"),
                ("workingPrice", "100"),
                ("workingQuantity", "1"),
                ("pendingType", "MARKET"),
                ("pendingSide", "SELL"),
                ("workingTimeInForce", "GTC"),
            ],
            "POST",
            "/api/v3/orderList/opo",
        ),
        private(
            "place_spot_opoco",
            &[
                ("product_symbol", "BTC-USDT-SPOT"),
                ("workingType", "LIMIT"),
                ("workingSide", "BUY"),
                ("workingPrice", "100"),
                ("workingQuantity", "1"),
                ("pendingSide", "SELL"),
                ("pendingAboveType", "LIMIT_MAKER"),
                ("workingTimeInForce", "GTC"),
                ("pendingAbovePrice", "110"),
                ("pendingBelowType", "STOP_LOSS"),
                ("pendingBelowStopPrice", "90"),
            ],
            "POST",
            "/api/v3/orderList/opoco",
        ),
    ]);
}

#[test]
fn remaining_account_and_market_endpoints_use_documented_routes() {
    assert_cases(&[
        private(
            "get_coin_futures_download_id_for_futures_order_history",
            &[("startTime", "1700000000000"), ("endTime", "1700000010000")],
            "GET",
            "/dapi/v1/order/asyn",
        ),
        private(
            "get_coin_futures_download_id_for_futures_trade_history",
            &[("startTime", "1700000000000"), ("endTime", "1700000010000")],
            "GET",
            "/dapi/v1/trade/asyn",
        ),
        private(
            "get_coin_futures_download_id_for_futures_transaction_history",
            &[("startTime", "1700000000000"), ("endTime", "1700000010000")],
            "GET",
            "/dapi/v1/income/asyn",
        ),
        private(
            "get_coin_futures_futures_order_history_download_link_by_id",
            &[("downloadId", "example")],
            "GET",
            "/dapi/v1/order/asyn/id",
        ),
        private(
            "get_coin_futures_futures_trade_download_link_by_id",
            &[("downloadId", "example")],
            "GET",
            "/dapi/v1/trade/asyn/id",
        ),
        private(
            "get_coin_futures_futures_transaction_history_download_link_by_id",
            &[("downloadId", "example")],
            "GET",
            "/dapi/v1/income/asyn/id",
        ),
        public(
            "coin_futures_old_trades_lookup",
            &[("symbol", "BTCUSD_PERP")],
            "GET",
            "/dapi/v1/historicalTrades",
        ),
        public(
            "query_coin_futures_index_price_constituents",
            &[("symbol", "BTCUSD_PERP")],
            "GET",
            "/dapi/v1/constituents",
        ),
        public(
            "coin_futures_taker_buy_sell_volume",
            &[
                ("pair", "BTCUSD"),
                ("contractType", "ALL"),
                ("period", "5m"),
            ],
            "GET",
            "/futures/data/takerBuySellVol",
        ),
        public(
            "coin_futures_test_connectivity",
            &[],
            "GET",
            "/dapi/v1/ping",
        ),
        private(
            "get_coin_futures_order_modify_history",
            &[("symbol", "BTCUSD_PERP")],
            "GET",
            "/dapi/v1/orderAmendment",
        ),
        private(
            "get_coin_futures_position_margin_change_history",
            &[("symbol", "BTCUSD_PERP")],
            "GET",
            "/dapi/v1/positionMargin/history",
        ),
        private(
            "query_coin_futures_current_open_order",
            &[("symbol", "BTCUSD_PERP"), ("orderId", "123")],
            "GET",
            "/dapi/v1/openOrder",
        ),
        private(
            "pm_bnb_transfer",
            &[("amount", "1.25"), ("transferSide", "TO_UM")],
            "POST",
            "/papi/v1/bnb-transfer",
        ),
        private(
            "change_pm_auto_repay_futures_status",
            &[("autoRepay", "true")],
            "POST",
            "/papi/v1/repay-futures-switch",
        ),
        private(
            "pm_fund_auto_collection",
            &[],
            "POST",
            "/papi/v1/auto-collection",
        ),
        private(
            "pm_fund_collection_by_asset",
            &[("asset", "USDT")],
            "POST",
            "/papi/v1/asset-collection",
        ),
        private(
            "get_pm_auto_repay_futures_status",
            &[],
            "GET",
            "/papi/v1/repay-futures-switch",
        ),
        private(
            "get_pm_download_id_for_um_futures_order_history",
            &[("startTime", "1700000000000"), ("endTime", "1700000010000")],
            "GET",
            "/papi/v1/um/order/asyn",
        ),
        private(
            "get_pm_download_id_for_um_futures_trade_history",
            &[("startTime", "1700000000000"), ("endTime", "1700000010000")],
            "GET",
            "/papi/v1/um/trade/asyn",
        ),
        private(
            "get_pm_download_id_for_um_futures_transaction_history",
            &[("startTime", "1700000000000"), ("endTime", "1700000010000")],
            "GET",
            "/papi/v1/um/income/asyn",
        ),
        private(
            "get_pm_um_account_detail_v2",
            &[],
            "GET",
            "/papi/v2/um/account",
        ),
        private(
            "get_pm_um_futures_order_download_link_by_id",
            &[("downloadId", "example")],
            "GET",
            "/papi/v1/um/order/asyn/id",
        ),
        private(
            "get_pm_um_futures_trade_download_link_by_id",
            &[("downloadId", "example")],
            "GET",
            "/papi/v1/um/trade/asyn/id",
        ),
        private(
            "get_pm_um_futures_transaction_download_link_by_id",
            &[("downloadId", "example")],
            "GET",
            "/papi/v1/um/income/asyn/id",
        ),
        private(
            "query_pm_portfolio_margin_negative_balance_interest_history",
            &[],
            "GET",
            "/papi/v1/portfolio/interest-history",
        ),
        private(
            "query_pm_user_negative_balance_auto_exchange_record",
            &[("startTime", "1700000000000"), ("endTime", "1700000010000")],
            "GET",
            "/papi/v1/portfolio/negative-balance-exchange-record",
        ),
        private(
            "repay_pm_futures_negative_balance",
            &[],
            "POST",
            "/papi/v1/repay-futures-negative-balance",
        ),
        public("pm_test_connectivity", &[], "GET", "/papi/v1/ping"),
        private(
            "pm_futures_tradfi_perps_contract",
            &[],
            "POST",
            "/papi/v1/um/stock/contract",
        ),
        private(
            "get_pm_um_futures_bnb_burn_status",
            &[],
            "GET",
            "/papi/v1/um/feeBurn",
        ),
        private(
            "query_pm_current_cm_open_order",
            &[("symbol", "BTCUSD_PERP"), ("orderId", "123")],
            "GET",
            "/papi/v1/cm/openOrder",
        ),
        private(
            "query_pm_current_um_open_order",
            &[("symbol", "BTCUSDT"), ("orderId", "123")],
            "GET",
            "/papi/v1/um/openOrder",
        ),
        private(
            "toggle_pm_bnb_burn_on_um_futures_trade",
            &[("feeBurn", "true")],
            "POST",
            "/papi/v1/um/feeBurn",
        ),
        private(
            "get_futures_bnb_burn_status",
            &[],
            "GET",
            "/fapi/v1/feeBurn",
        ),
        private(
            "get_futures_download_id_for_futures_order_history",
            &[("startTime", "1700000000000"), ("endTime", "1700000010000")],
            "GET",
            "/fapi/v1/order/asyn",
        ),
        private(
            "get_futures_download_id_for_futures_trade_history",
            &[("startTime", "1700000000000"), ("endTime", "1700000010000")],
            "GET",
            "/fapi/v1/trade/asyn",
        ),
        private(
            "get_futures_download_id_for_futures_transaction_history",
            &[("startTime", "1700000000000"), ("endTime", "1700000010000")],
            "GET",
            "/fapi/v1/income/asyn",
        ),
        private(
            "get_futures_futures_order_history_download_link_by_id",
            &[("downloadId", "example")],
            "GET",
            "/fapi/v1/order/asyn/id",
        ),
        private(
            "get_futures_futures_trade_download_link_by_id",
            &[("downloadId", "example")],
            "GET",
            "/fapi/v1/trade/asyn/id",
        ),
        private(
            "get_futures_futures_transaction_history_download_link_by_id",
            &[("downloadId", "example")],
            "GET",
            "/fapi/v1/income/asyn/id",
        ),
        private(
            "toggle_futures_bnb_burn_on_futures_trade",
            &[("feeBurn", "true")],
            "POST",
            "/fapi/v1/feeBurn",
        ),
        private(
            "futures_accept_the_offered_quote",
            &[("quoteId", "example")],
            "POST",
            "/fapi/v1/convert/acceptQuote",
        ),
        public(
            "futures_list_all_convert_pairs",
            &[],
            "GET",
            "/fapi/v1/convert/exchangeInfo",
        ),
        private(
            "futures_order_status",
            &[("orderId", "123")],
            "GET",
            "/fapi/v1/convert/orderStatus",
        ),
        private(
            "futures_send_quote_request",
            &[
                ("fromAsset", "USDT"),
                ("toAsset", "USDC"),
                ("fromAmount", "1.25"),
            ],
            "POST",
            "/fapi/v1/convert/getQuote",
        ),
        public("futures_adl_risk", &[], "GET", "/fapi/v1/symbolAdlRisk"),
        public("futures_asset_index", &[], "GET", "/fapi/v1/assetIndex"),
        public(
            "futures_composite_index_symbol_information",
            &[],
            "GET",
            "/fapi/v1/indexInfo",
        ),
        public(
            "futures_old_trades_lookup",
            &[("symbol", "BTCUSDT")],
            "GET",
            "/fapi/v1/historicalTrades",
        ),
        public(
            "futures_quarterly_contract_settlement_price",
            &[("pair", "BTCUSDT")],
            "GET",
            "/futures/data/delivery-price",
        ),
        public(
            "query_futures_index_price_constituents",
            &[("symbol", "BTCUSDT")],
            "GET",
            "/fapi/v1/constituents",
        ),
        public(
            "query_futures_insurance_fund_balance_snapshot",
            &[],
            "GET",
            "/fapi/v1/insuranceBalance",
        ),
        public(
            "futures_rpi_order_book",
            &[("symbol", "BTCUSDT")],
            "GET",
            "/fapi/v1/rpiDepth",
        ),
        public("futures_test_connectivity", &[], "GET", "/fapi/v1/ping"),
        public(
            "futures_trading_schedule",
            &[],
            "GET",
            "/fapi/v1/tradingSchedule",
        ),
        private(
            "futures_classic_portfolio_margin_account_information",
            &[("asset", "USDT")],
            "GET",
            "/fapi/v1/pmAccountInfo",
        ),
        private(
            "futures_futures_tradfi_perps_contract",
            &[],
            "POST",
            "/fapi/v1/stock/contract",
        ),
        private(
            "get_futures_order_modify_history",
            &[("symbol", "BTCUSDT")],
            "GET",
            "/fapi/v1/orderAmendment",
        ),
        private(
            "get_futures_position_margin_change_history",
            &[("symbol", "BTCUSDT")],
            "GET",
            "/fapi/v1/positionMargin/history",
        ),
        private(
            "adjust_margin_cross_margin_max_leverage",
            &[("maxLeverage", "5")],
            "POST",
            "/sapi/v1/margin/max-leverage",
        ),
        private("get_margin_bnb_burn_status", &[], "GET", "/sapi/v1/bnbBurn"),
        private(
            "query_margin_cross_margin_fee_data",
            &[],
            "GET",
            "/sapi/v1/margin/crossMarginData",
        ),
        private(
            "query_margin_enabled_isolated_margin_account_limit",
            &[],
            "GET",
            "/sapi/v1/margin/isolated/accountLimit",
        ),
        private(
            "query_margin_isolated_margin_fee_data",
            &[],
            "GET",
            "/sapi/v1/margin/isolatedMarginData",
        ),
        private(
            "get_margin_future_hourly_interest_rate",
            &[("assets", "USDT,BTC"), ("isIsolated", "TRUE")],
            "GET",
            "/sapi/v1/margin/next-hourly-interest-rate",
        ),
        private(
            "query_margin_margin_interest_rate_history",
            &[("asset", "USDT")],
            "GET",
            "/sapi/v1/margin/interestRateHistory",
        ),
        public(
            "margin_cross_margin_collateral_ratio",
            &[],
            "GET",
            "/sapi/v1/margin/crossMarginCollateralRatio",
        ),
        public(
            "get_margin_limit_price_pairs",
            &[],
            "GET",
            "/sapi/v1/margin/limit-price-pairs",
        ),
        public(
            "get_margin_list_schedule",
            &[],
            "GET",
            "/sapi/v1/margin/list-schedule",
        ),
        public(
            "get_margin_margin_asset_risk_based_liquidation_ratio",
            &[],
            "GET",
            "/sapi/v1/margin/risk-based-liquidation-ratio",
        ),
        public(
            "get_margin_margin_restricted_assets",
            &[],
            "GET",
            "/sapi/v1/margin/restricted-asset",
        ),
        private(
            "query_margin_isolated_margin_tier_data",
            &[("symbol", "BTCUSDT")],
            "GET",
            "/sapi/v1/margin/isolatedMarginTier",
        ),
        public(
            "query_margin_liability_coin_leverage_bracket_in_cross_margin_pro_mode",
            &[],
            "GET",
            "/sapi/v1/margin/leverageBracket",
        ),
        private(
            "query_margin_margin_available_inventory",
            &[("type", "MARGIN")],
            "GET",
            "/sapi/v1/margin/available-inventory",
        ),
        private(
            "create_margin_special_key",
            &[("apiName", "example")],
            "POST",
            "/sapi/v1/margin/apiKey",
        ),
        private(
            "delete_margin_special_key",
            &[],
            "DELETE",
            "/sapi/v1/margin/apiKey",
        ),
        private(
            "edit_margin_ip_for_special_key",
            &[("ip", "127.0.0.1")],
            "PUT",
            "/sapi/v1/margin/apiKey/ip",
        ),
        private(
            "margin_exit_special_key_mode",
            &[],
            "POST",
            "/sapi/v1/margin/exit-special-key-mode",
        ),
        private(
            "get_margin_small_liability_exchange_coin_list",
            &[],
            "GET",
            "/sapi/v1/margin/exchange-small-liability",
        ),
        private(
            "get_margin_small_liability_exchange_history",
            &[("current", "1"), ("size", "1")],
            "GET",
            "/sapi/v1/margin/exchange-small-liability-history",
        ),
        private(
            "margin_liquidation_loan_repay",
            &[("asset", "USDT"), ("amount", "1.25")],
            "POST",
            "/sapi/v1/margin/liquidation-loan/repay",
        ),
        private(
            "margin_margin_manual_liquidation",
            &[("type", "MARGIN")],
            "POST",
            "/sapi/v1/margin/manual-liquidation",
        ),
        private(
            "query_margin_liquidation_loan",
            &[],
            "GET",
            "/sapi/v1/margin/liquidation-loan",
        ),
        private(
            "query_margin_liquidation_loan_repay_history",
            &[],
            "GET",
            "/sapi/v1/margin/liquidation-loan/repay-history",
        ),
        private(
            "query_margin_prevented_matches",
            &[("symbol", "BTCUSDT"), ("orderId", "123")],
            "GET",
            "/sapi/v1/margin/myPreventedMatches",
        ),
        private(
            "query_margin_special_key",
            &[],
            "GET",
            "/sapi/v1/margin/apiKey",
        ),
        private(
            "query_margin_special_key_list",
            &[],
            "GET",
            "/sapi/v1/margin/api-key-list",
        ),
        private(
            "margin_small_liability_exchange",
            &[("assetNames", "USDT")],
            "POST",
            "/sapi/v1/margin/exchange-small-liability",
        ),
        private(
            "get_margin_cross_margin_transfer_history",
            &[],
            "GET",
            "/sapi/v1/margin/transfer",
        ),
        private(
            "spot_my_filters",
            &[("symbol", "BTCUSDT")],
            "GET",
            "/api/v3/myFilters",
        ),
        private(
            "spot_order_amendments",
            &[("symbol", "BTCUSDT"), ("orderId", "1")],
            "GET",
            "/api/v3/order/amendments",
        ),
        public("spot_execution_rules", &[], "GET", "/api/v3/executionRules"),
        public("spot_ping", &[], "GET", "/api/v3/ping"),
        public(
            "spot_historical_block_trades",
            &[("symbol", "BTCUSDT"), ("fromId", "1")],
            "GET",
            "/api/v3/historicalBlockTrades",
        ),
        public(
            "spot_historical_trades",
            &[("symbol", "BTCUSDT")],
            "GET",
            "/api/v3/historicalTrades",
        ),
        public(
            "spot_reference_price",
            &[("symbol", "BTCUSDT")],
            "GET",
            "/api/v3/referencePrice",
        ),
        public(
            "spot_reference_price_calculation",
            &[("symbol", "BTCUSDT")],
            "GET",
            "/api/v3/referencePrice/calculation",
        ),
        public("spot_ticker", &[], "GET", "/api/v3/ticker"),
        public(
            "spot_ticker_trading_day",
            &[],
            "GET",
            "/api/v3/ticker/tradingDay",
        ),
        public(
            "spot_ui_klines",
            &[("symbol", "BTCUSDT"), ("interval", "1s")],
            "GET",
            "/api/v3/uiKlines",
        ),
        private(
            "spot_sor_order",
            &[
                ("symbol", "BTCUSDT"),
                ("side", "BUY"),
                ("type", "LIMIT"),
                ("quantity", "1.25"),
                ("timeInForce", "GTC"),
                ("price", "50000"),
            ],
            "POST",
            "/api/v3/sor/order",
        ),
        private(
            "spot_sor_order_test",
            &[
                ("symbol", "BTCUSDT"),
                ("side", "BUY"),
                ("type", "LIMIT"),
                ("quantity", "1.25"),
                ("timeInForce", "GTC"),
                ("price", "50000"),
            ],
            "POST",
            "/api/v3/sor/order/test",
        ),
        private("wallet_account_info", &[], "GET", "/sapi/v1/account/info"),
        private(
            "wallet_daily_account_snapshot",
            &[("type", "SPOT")],
            "GET",
            "/sapi/v1/accountSnapshot",
        ),
        private(
            "wallet_asset_detail",
            &[],
            "GET",
            "/sapi/v1/asset/assetDetail",
        ),
        private(
            "wallet_asset_dividend_record",
            &[],
            "GET",
            "/sapi/v1/asset/assetDividend",
        ),
        private(
            "wallet_dust_convert",
            &[("asset", "USDT")],
            "POST",
            "/sapi/v1/asset/dust-convert/convert",
        ),
        private(
            "wallet_dust_convertible_assets",
            &[("targetAsset", "BNB")],
            "POST",
            "/sapi/v1/asset/dust-convert/query-convertible-assets",
        ),
        private(
            "wallet_dust_transfer",
            &[("asset", "USDT")],
            "POST",
            "/sapi/v1/asset/dust",
        ),
        private("wallet_dustlog", &[], "GET", "/sapi/v1/asset/dribblet"),
        private(
            "get_wallet_assets_that_can_be_converted_into_bnb",
            &[],
            "POST",
            "/sapi/v1/asset/dust-btc",
        ),
        public(
            "get_wallet_open_symbol_list",
            &[],
            "GET",
            "/sapi/v1/spot/open-symbol-list",
        ),
        public(
            "get_wallet_spot_asset_tags",
            &[],
            "GET",
            "/sapi/v1/spot/asset/tags",
        ),
        private(
            "toggle_wallet_bnb_burn_on_spot_trade_and_margin_interest",
            &[("spotBNBBurn", "true")],
            "POST",
            "/sapi/v1/bnbBurn",
        ),
        private(
            "wallet_fetch_deposit_address_list_with_network",
            &[("coin", "BTC")],
            "GET",
            "/sapi/v1/capital/deposit/address/list",
        ),
        private(
            "wallet_one_click_arrival_deposit_apply",
            &[("depositId", "123")],
            "POST",
            "/sapi/v1/capital/deposit/credit-apply",
        ),
    ]);
}

#[test]
fn algorithm_and_pm_pro_endpoints_use_documented_routes() {
    assert_cases(&[
        private(
            "algo_cancel_algo_order_future_algo",
            &[("algoId", "123")],
            "DELETE",
            "/sapi/v1/algo/futures/order",
        ),
        private(
            "query_algo_current_algo_open_orders_future_algo",
            &[],
            "GET",
            "/sapi/v1/algo/futures/openOrders",
        ),
        private(
            "query_algo_historical_algo_orders_future_algo",
            &[],
            "GET",
            "/sapi/v1/algo/futures/historicalOrders",
        ),
        private(
            "query_algo_sub_orders_future_algo",
            &[("algoId", "1")],
            "GET",
            "/sapi/v1/algo/futures/subOrders",
        ),
        private(
            "algo_time_weighted_average_price_future_algo",
            &[
                ("symbol", "BTCUSDT"),
                ("side", "BUY"),
                ("quantity", "1.25"),
                ("duration", "300"),
            ],
            "POST",
            "/sapi/v1/algo/futures/newOrderTwap",
        ),
        private(
            "algo_volume_participation_future_algo",
            &[
                ("symbol", "BTCUSDT"),
                ("side", "BUY"),
                ("quantity", "1.25"),
                ("urgency", "LOW"),
            ],
            "POST",
            "/sapi/v1/algo/futures/newOrderVp",
        ),
        private(
            "algo_cancel_algo_order_spot_algo",
            &[("algoId", "123")],
            "DELETE",
            "/sapi/v1/algo/spot/order",
        ),
        private(
            "query_algo_current_algo_open_orders_spot_algo",
            &[],
            "GET",
            "/sapi/v1/algo/spot/openOrders",
        ),
        private(
            "query_algo_historical_algo_orders_spot_algo",
            &[],
            "GET",
            "/sapi/v1/algo/spot/historicalOrders",
        ),
        private(
            "query_algo_sub_orders_spot_algo",
            &[("algoId", "1")],
            "GET",
            "/sapi/v1/algo/spot/subOrders",
        ),
        private(
            "algo_time_weighted_average_price_spot_algo",
            &[
                ("symbol", "BTCUSDT"),
                ("side", "BUY"),
                ("quantity", "1.25"),
                ("duration", "300"),
            ],
            "POST",
            "/sapi/v1/algo/spot/newOrderTwap",
        ),
        private(
            "pm_pro_bnb_transfer",
            &[("amount", "1.25"), ("transferSide", "TO_UM")],
            "POST",
            "/sapi/v1/portfolio/bnb-transfer",
        ),
        private(
            "change_pm_pro_auto_repay_futures_status",
            &[("autoRepay", "true")],
            "POST",
            "/sapi/v1/portfolio/repay-futures-switch",
        ),
        private(
            "delete_pm_pro_margin_call_level",
            &[],
            "DELETE",
            "/sapi/v1/portfolio/margin-call-level",
        ),
        private(
            "pm_pro_fund_auto_collection",
            &[],
            "POST",
            "/sapi/v1/portfolio/auto-collection",
        ),
        private(
            "pm_pro_fund_collection_by_asset",
            &[("asset", "USDT")],
            "POST",
            "/sapi/v1/portfolio/asset-collection",
        ),
        private(
            "get_pm_pro_auto_repay_futures_status",
            &[],
            "GET",
            "/sapi/v1/portfolio/repay-futures-switch",
        ),
        private(
            "get_pm_pro_delta_mode_status",
            &[],
            "GET",
            "/sapi/v1/portfolio/delta-mode",
        ),
        private(
            "get_pm_pro_margin_call_level",
            &[],
            "GET",
            "/sapi/v1/portfolio/margin-call-level",
        ),
        private(
            "get_pm_pro_portfolio_margin_pro_account_balance",
            &[],
            "GET",
            "/sapi/v1/portfolio/balance",
        ),
        private(
            "get_pm_pro_portfolio_margin_pro_account_info",
            &[],
            "GET",
            "/sapi/v1/portfolio/account",
        ),
        private(
            "get_pm_pro_portfolio_margin_pro_span_account_info",
            &[],
            "GET",
            "/sapi/v2/portfolio/account",
        ),
        private(
            "pm_pro_portfolio_margin_pro_bankruptcy_loan_repay",
            &[],
            "POST",
            "/sapi/v1/portfolio/repay",
        ),
        private(
            "query_pm_pro_portfolio_margin_pro_bankruptcy_loan_amount",
            &[],
            "GET",
            "/sapi/v1/portfolio/pmLoan",
        ),
        private(
            "query_pm_pro_portfolio_margin_pro_bankruptcy_loan_repay_history",
            &[],
            "GET",
            "/sapi/v1/portfolio/pmloan-history",
        ),
        private(
            "query_pm_pro_portfolio_margin_pro_negative_balance_interest_history",
            &[],
            "GET",
            "/sapi/v1/portfolio/interest-history",
        ),
        private(
            "repay_pm_pro_futures_negative_balance",
            &[],
            "POST",
            "/sapi/v1/portfolio/repay-futures-negative-balance",
        ),
        private(
            "set_pm_pro_margin_call_level",
            &[("marginCallLevel", "1.25")],
            "POST",
            "/sapi/v1/portfolio/margin-call-level",
        ),
        private(
            "pm_pro_switch_delta_mode",
            &[("deltaEnabled", "true")],
            "POST",
            "/sapi/v1/portfolio/delta-mode",
        ),
        private(
            "get_pm_pro_portfolio_margin_asset_leverage",
            &[],
            "GET",
            "/sapi/v1/portfolio/margin-asset-leverage",
        ),
        public(
            "pm_pro_portfolio_margin_collateral_rate",
            &[],
            "GET",
            "/sapi/v1/portfolio/collateralRate",
        ),
        private(
            "pm_pro_portfolio_margin_pro_tiered_collateral_rate",
            &[],
            "GET",
            "/sapi/v2/portfolio/collateralRate",
        ),
        public(
            "query_pm_pro_portfolio_margin_asset_index_price",
            &[],
            "GET",
            "/sapi/v1/portfolio/asset-index-price",
        ),
    ]);
}
