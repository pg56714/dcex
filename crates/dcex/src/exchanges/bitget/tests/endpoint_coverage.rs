//! Route coverage: every Bitget dispatch name must reach the documented
//! METHOD + path from the official API docs, fully offline.

use std::io::{BufRead, BufReader, Read, Write};
use std::net::TcpListener;
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

use super::helpers::BitgetClient;

struct Recorded {
    method: String,
    path: String,
    query: String,
    body: String,
    signed: bool,
}

fn recording_server() -> (String, mpsc::Receiver<Recorded>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let url = format!("http://{}", listener.local_addr().expect("address"));
    let (sender, receiver) = mpsc::channel();
    thread::spawn(move || {
        for stream in listener.incoming() {
            let Ok(mut stream) = stream else { break };
            stream
                .set_read_timeout(Some(Duration::from_secs(10)))
                .expect("timeout");
            let mut reader = BufReader::new(stream.try_clone().expect("clone"));
            let mut request_line = String::new();
            if reader.read_line(&mut request_line).is_err() || request_line.is_empty() {
                continue;
            }
            let mut content_length = 0usize;
            let mut signed = false;
            loop {
                let mut line = String::new();
                if reader.read_line(&mut line).is_err() || line == "\r\n" || line.is_empty() {
                    break;
                }
                let lower = line.to_ascii_lowercase();
                if let Some(value) = lower.strip_prefix("content-length:") {
                    content_length = value.trim().parse().unwrap_or(0);
                }
                if lower.starts_with("access-sign:") {
                    signed = true;
                }
            }
            let mut body = vec![0u8; content_length];
            if content_length > 0 {
                reader.read_exact(&mut body).expect("body");
            }
            let payload = br#"{"code":"00000","msg":"success","data":{}}"#;
            let head = format!(
                "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n",
                payload.len()
            );
            let _ = stream.write_all(head.as_bytes());
            let _ = stream.write_all(payload);
            let _ = stream.flush();
            let mut parts = request_line.split_whitespace();
            let method = parts.next().unwrap_or_default().to_string();
            let target = parts.next().unwrap_or_default().to_string();
            let (path, query) = match target.split_once('?') {
                Some((path, query)) => (path.to_string(), query.to_string()),
                None => (target, String::new()),
            };
            let recorded = Recorded {
                method,
                path,
                query,
                body: String::from_utf8_lossy(&body).to_string(),
                signed,
            };
            if sender.send(recorded).is_err() {
                break;
            }
        }
    });
    (url, receiver)
}

fn base_params() -> Vec<(String, String)> {
    [
        ("product_symbol", "BTC-USDT-SWAP"),
        ("productType", "USDT-FUTURES"),
        ("marginCoin", "USDT"),
        ("marginMode", "crossed"),
        ("granularity", "1min"),
        ("interval", "1m"),
        ("category", "USDT-FUTURES"),
        ("startTime", "1690000000000"),
        ("endTime", "1700000000000"),
        ("orderId", "1"),
        ("clientOid", "c1"),
        ("qty", "1"),
        ("size", "1"),
        ("side", "buy"),
        ("orderType", "limit"),
        ("force", "gtc"),
        ("price", "1"),
        ("orderList", r#"[{"size":"1"}]"#),
        ("coin", "USDT"),
        ("amount", "1"),
        ("fromType", "spot"),
        ("toType", "usdt_futures"),
        ("leverage", "5"),
        ("posMode", "one_way_mode"),
        ("holdMode", "one_way_mode"),
        ("productId", "p1"),
        ("periodType", "flexible"),
        ("productSubId", "s1"),
        ("redeemType", "standard"),
        ("receiveAccount", "spot"),
        ("type", "interest"),
        ("loanCoin", "USDT"),
        ("pledgeCoin", "BTC"),
        ("daily", "SEVEN"),
        ("pledgeAmount", "1"),
        ("repayAll", "yes"),
        ("reviseType", "IN"),
        ("repayableCoinList", r#"["USDT"]"#),
        ("paymentCoinList", r#"["USDT"]"#),
        ("limit", "10"),
    ]
    .into_iter()
    .map(|(key, value)| (key.to_string(), value.to_string()))
    .collect()
}

fn params_for(name: &str) -> Vec<(String, String)> {
    let mut params = base_params();
    if name == "get_savings_records" {
        params.retain(|(key, _)| key != "orderType");
    }
    params
}

/// (dispatch name, HTTP method, documented path)
const PUBLIC_ROUTES: &[(&str, &str, &str)] = &[
    ("get_spot_coins", "GET", "/api/v2/spot/public/coins"),
    ("get_spot_symbols", "GET", "/api/v2/spot/public/symbols"),
    ("get_spot_tickers", "GET", "/api/v2/spot/market/tickers"),
    ("get_spot_orderbook", "GET", "/api/v2/spot/market/orderbook"),
    ("get_spot_kline", "GET", "/api/v2/spot/market/candles"),
    (
        "get_spot_history_kline",
        "GET",
        "/api/v2/spot/market/history-candles",
    ),
    ("get_spot_recent_trades", "GET", "/api/v2/spot/market/fills"),
    (
        "get_spot_market_trades",
        "GET",
        "/api/v2/spot/market/fills-history",
    ),
    (
        "get_futures_contracts",
        "GET",
        "/api/v2/mix/market/contracts",
    ),
    ("get_futures_ticker", "GET", "/api/v2/mix/market/ticker"),
    ("get_futures_tickers", "GET", "/api/v2/mix/market/tickers"),
    (
        "get_futures_orderbook",
        "GET",
        "/api/v2/mix/market/merge-depth",
    ),
    ("get_futures_kline", "GET", "/api/v2/mix/market/candles"),
    (
        "get_futures_history_kline",
        "GET",
        "/api/v2/mix/market/history-candles",
    ),
    (
        "get_futures_recent_trades",
        "GET",
        "/api/v2/mix/market/fills",
    ),
    (
        "get_futures_current_funding_rate",
        "GET",
        "/api/v2/mix/market/current-fund-rate",
    ),
    (
        "get_futures_history_funding_rate",
        "GET",
        "/api/v2/mix/market/history-fund-rate",
    ),
    (
        "get_futures_open_interest",
        "GET",
        "/api/v2/mix/market/open-interest",
    ),
    ("get_uta_instruments", "GET", "/api/v3/market/instruments"),
    ("get_uta_tickers", "GET", "/api/v3/market/tickers"),
    ("get_uta_orderbook", "GET", "/api/v3/market/orderbook"),
    ("get_uta_public_fills", "GET", "/api/v3/market/fills"),
    ("get_uta_kline", "GET", "/api/v3/market/candles"),
    (
        "get_uta_history_kline",
        "GET",
        "/api/v3/market/history-candles",
    ),
    ("get_uta_liquidations", "GET", "/api/v3/market/liquidations"),
    (
        "get_reality_stock_info",
        "GET",
        "/api/v3/reality/market/stock-info",
    ),
    (
        "get_reality_market_states",
        "GET",
        "/api/v3/reality/market/states",
    ),
    (
        "get_reality_market_calendar",
        "GET",
        "/api/v3/reality/market/calendar",
    ),
];

/// (dispatch name, HTTP method, documented path)
const PRIVATE_ROUTES: &[(&str, &str, &str)] = &[
    // Account / fees / transfers.
    ("get_spot_fee_rates", "GET", "/api/v2/common/trade-rate"),
    ("get_futures_fee_rates", "GET", "/api/v2/common/trade-rate"),
    (
        "get_all_account_balance",
        "GET",
        "/api/v2/account/all-account-balance",
    ),
    (
        "get_funding_assets",
        "GET",
        "/api/v2/account/funding-assets",
    ),
    ("get_spot_account_info", "GET", "/api/v2/spot/account/info"),
    (
        "get_spot_account_assets",
        "GET",
        "/api/v2/spot/account/assets",
    ),
    (
        "get_spot_account_bills",
        "GET",
        "/api/v2/spot/account/bills",
    ),
    ("transfer", "POST", "/api/v2/spot/wallet/transfer"),
    (
        "get_transfer_records",
        "GET",
        "/api/v2/spot/account/transferRecords",
    ),
    (
        "get_transferable_coins",
        "GET",
        "/api/v2/spot/wallet/transfer-coin-info",
    ),
    (
        "get_deposit_records",
        "GET",
        "/api/v2/spot/wallet/deposit-records",
    ),
    ("get_uta_account_assets", "GET", "/api/v3/account/assets"),
    (
        "get_reality_orderbook",
        "GET",
        "/api/v3/account/reality-orderbook",
    ),
    ("get_reality_fills", "GET", "/api/v3/account/reality-fills"),
    ("get_uta_account_info", "GET", "/api/v3/account/info"),
    (
        "get_uta_all_fee_rates",
        "GET",
        "/api/v3/account/all-fee-rate",
    ),
    ("get_uta_loan_data", "GET", "/api/v3/trade/loan-data"),
    (
        "get_uta_collateral_type",
        "GET",
        "/api/v3/account/collateral-type",
    ),
    (
        "get_uta_custom_collateral_coins",
        "GET",
        "/api/v3/account/custom-collateral-coins",
    ),
    (
        "get_uta_pre_set_leverage",
        "GET",
        "/api/v3/account/pre-set-leverage",
    ),
    ("set_uta_leverage", "POST", "/api/v3/account/set-leverage"),
    ("set_uta_hold_mode", "POST", "/api/v3/account/set-hold-mode"),
    ("get_futures_account", "GET", "/api/v2/mix/account/account"),
    (
        "get_futures_accounts",
        "GET",
        "/api/v2/mix/account/accounts",
    ),
    (
        "get_futures_account_bills",
        "GET",
        "/api/v2/mix/account/bill",
    ),
    (
        "set_futures_leverage",
        "POST",
        "/api/v2/mix/account/set-leverage",
    ),
    (
        "set_futures_margin_mode",
        "POST",
        "/api/v2/mix/account/set-margin-mode",
    ),
    (
        "set_futures_position_mode",
        "POST",
        "/api/v2/mix/account/set-position-mode",
    ),
    (
        "get_futures_positions",
        "GET",
        "/api/v2/mix/position/all-position",
    ),
    (
        "get_futures_position",
        "GET",
        "/api/v2/mix/position/single-position",
    ),
    // Earn.
    (
        "get_earn_account_assets",
        "GET",
        "/api/v2/earn/account/assets",
    ),
    ("get_savings_account", "GET", "/api/v2/earn/savings/account"),
    (
        "get_savings_products",
        "GET",
        "/api/v2/earn/savings/product",
    ),
    ("get_savings_assets", "GET", "/api/v2/earn/savings/assets"),
    ("get_savings_records", "GET", "/api/v2/earn/savings/records"),
    (
        "get_savings_subscription_info",
        "GET",
        "/api/v2/earn/savings/subscribe-info",
    ),
    (
        "subscribe_savings",
        "POST",
        "/api/v2/earn/savings/subscribe",
    ),
    (
        "get_savings_subscription_result",
        "GET",
        "/api/v2/earn/savings/subscribe-result",
    ),
    ("redeem_savings", "POST", "/api/v2/earn/savings/redeem"),
    (
        "get_savings_redemption_result",
        "GET",
        "/api/v2/earn/savings/redeem-result",
    ),
    (
        "get_elite_earn_products",
        "GET",
        "/api/v3/earn/elite-product",
    ),
    (
        "get_elite_earn_subscription_info",
        "GET",
        "/api/v3/earn/elite-subscribe-info",
    ),
    (
        "subscribe_elite_earn",
        "POST",
        "/api/v3/earn/elite-subscribe",
    ),
    (
        "get_elite_earn_subscription_result",
        "GET",
        "/api/v3/earn/elite-subscribe-result",
    ),
    (
        "get_elite_earn_redemption_info",
        "GET",
        "/api/v3/earn/elite-redeem-info",
    ),
    ("redeem_elite_earn", "POST", "/api/v3/earn/elite-redeem"),
    ("get_elite_earn_assets", "GET", "/api/v3/earn/elite-assets"),
    (
        "get_elite_earn_records",
        "GET",
        "/api/v3/earn/elite-records",
    ),
    // Crypto loans and UTA liability repayment.
    ("get_crypto_loan_coins", "GET", "/api/v3/loan/coins"),
    ("get_crypto_loan_interest", "GET", "/api/v3/loan/interest"),
    ("borrow_crypto_loan", "POST", "/api/v3/loan/borrow"),
    (
        "get_crypto_loan_ongoing",
        "GET",
        "/api/v3/loan/borrow-ongoing",
    ),
    (
        "get_crypto_loan_borrow_history",
        "GET",
        "/api/v3/loan/borrow-history",
    ),
    ("repay_crypto_loan", "POST", "/api/v3/loan/repay"),
    (
        "get_crypto_loan_repay_history",
        "GET",
        "/api/v3/loan/repay-history",
    ),
    (
        "revise_crypto_loan_pledge",
        "POST",
        "/api/v3/loan/revise-pledge",
    ),
    (
        "get_crypto_loan_pledge_history",
        "GET",
        "/api/v3/loan/pledge-rate-history",
    ),
    (
        "get_crypto_loan_liquidations",
        "GET",
        "/api/v3/loan/reduces",
    ),
    ("get_crypto_loan_debts", "GET", "/api/v3/loan/debts"),
    ("repay_uta_liability", "POST", "/api/v3/account/repay"),
    // Classic spot trading.
    ("place_spot_order", "POST", "/api/v2/spot/trade/place-order"),
    (
        "place_spot_market_order",
        "POST",
        "/api/v2/spot/trade/place-order",
    ),
    (
        "place_spot_market_buy_order",
        "POST",
        "/api/v2/spot/trade/place-order",
    ),
    (
        "place_spot_market_sell_order",
        "POST",
        "/api/v2/spot/trade/place-order",
    ),
    (
        "place_spot_limit_order",
        "POST",
        "/api/v2/spot/trade/place-order",
    ),
    (
        "place_spot_limit_buy_order",
        "POST",
        "/api/v2/spot/trade/place-order",
    ),
    (
        "place_spot_limit_sell_order",
        "POST",
        "/api/v2/spot/trade/place-order",
    ),
    (
        "place_spot_post_only_limit_order",
        "POST",
        "/api/v2/spot/trade/place-order",
    ),
    (
        "place_spot_post_only_limit_buy_order",
        "POST",
        "/api/v2/spot/trade/place-order",
    ),
    (
        "place_spot_post_only_limit_sell_order",
        "POST",
        "/api/v2/spot/trade/place-order",
    ),
    (
        "place_spot_batch_orders",
        "POST",
        "/api/v2/spot/trade/batch-orders",
    ),
    (
        "cancel_spot_order",
        "POST",
        "/api/v2/spot/trade/cancel-order",
    ),
    (
        "cancel_spot_batch_orders",
        "POST",
        "/api/v2/spot/trade/batch-cancel-order",
    ),
    ("get_spot_order", "GET", "/api/v2/spot/trade/orderInfo"),
    (
        "get_spot_open_orders",
        "GET",
        "/api/v2/spot/trade/unfilled-orders",
    ),
    (
        "get_spot_history_orders",
        "GET",
        "/api/v2/spot/trade/history-orders",
    ),
    ("get_spot_fills", "GET", "/api/v2/spot/trade/fills"),
    // UTA trading.
    ("place_uta_order", "POST", "/api/v3/trade/place-order"),
    (
        "place_reality_order",
        "POST",
        "/api/v3/trade/place-reality-order",
    ),
    (
        "place_uta_batch_orders",
        "POST",
        "/api/v3/trade/place-batch",
    ),
    ("cancel_uta_order", "POST", "/api/v3/trade/cancel-order"),
    (
        "cancel_reality_order",
        "POST",
        "/api/v3/trade/cancel-reality-order",
    ),
    (
        "cancel_uta_batch_orders",
        "POST",
        "/api/v3/trade/cancel-batch",
    ),
    ("get_uta_order", "GET", "/api/v3/trade/order-info"),
    (
        "get_uta_open_orders",
        "GET",
        "/api/v3/trade/unfilled-orders",
    ),
    (
        "get_uta_history_orders",
        "GET",
        "/api/v3/trade/history-orders",
    ),
    ("get_uta_fills", "GET", "/api/v3/trade/fills"),
    (
        "get_uta_positions",
        "GET",
        "/api/v3/position/current-position",
    ),
    (
        "place_uta_strategy_order",
        "POST",
        "/api/v3/trade/place-strategy-order",
    ),
    (
        "modify_uta_strategy_order",
        "POST",
        "/api/v3/trade/modify-strategy-order",
    ),
    (
        "cancel_uta_strategy_order",
        "POST",
        "/api/v3/trade/cancel-strategy-order",
    ),
    (
        "get_uta_unfilled_strategy_orders",
        "GET",
        "/api/v3/trade/unfilled-strategy-orders",
    ),
    (
        "get_uta_history_strategy_orders",
        "GET",
        "/api/v3/trade/history-strategy-orders",
    ),
    // Classic futures trading.
    (
        "place_futures_order",
        "POST",
        "/api/v2/mix/order/place-order",
    ),
    (
        "place_futures_market_order",
        "POST",
        "/api/v2/mix/order/place-order",
    ),
    (
        "place_futures_market_buy_order",
        "POST",
        "/api/v2/mix/order/place-order",
    ),
    (
        "place_futures_market_sell_order",
        "POST",
        "/api/v2/mix/order/place-order",
    ),
    (
        "place_futures_limit_order",
        "POST",
        "/api/v2/mix/order/place-order",
    ),
    (
        "place_futures_limit_buy_order",
        "POST",
        "/api/v2/mix/order/place-order",
    ),
    (
        "place_futures_limit_sell_order",
        "POST",
        "/api/v2/mix/order/place-order",
    ),
    (
        "place_futures_post_only_limit_order",
        "POST",
        "/api/v2/mix/order/place-order",
    ),
    (
        "place_futures_post_only_limit_buy_order",
        "POST",
        "/api/v2/mix/order/place-order",
    ),
    (
        "place_futures_post_only_limit_sell_order",
        "POST",
        "/api/v2/mix/order/place-order",
    ),
    (
        "place_futures_batch_orders",
        "POST",
        "/api/v2/mix/order/batch-place-order",
    ),
    (
        "cancel_futures_order",
        "POST",
        "/api/v2/mix/order/cancel-order",
    ),
    (
        "cancel_futures_batch_orders",
        "POST",
        "/api/v2/mix/order/batch-cancel-orders",
    ),
    ("get_futures_order", "GET", "/api/v2/mix/order/detail"),
    (
        "get_futures_open_orders",
        "GET",
        "/api/v2/mix/order/orders-pending",
    ),
    (
        "get_futures_history_orders",
        "GET",
        "/api/v2/mix/order/orders-history",
    ),
    ("get_futures_fills", "GET", "/api/v2/mix/order/fills"),
];

fn signed_client(url: String) -> BitgetClient {
    BitgetClient::with_base_url(
        Some("test_api_key_0000".to_string()),
        Some("test_api_secret_0000".to_string()),
        Some("test-passphrase".to_string()),
        Duration::from_secs(10),
        url,
    )
    .expect("client")
}

fn next(receiver: &mpsc::Receiver<Recorded>, name: &str) -> Recorded {
    receiver
        .recv_timeout(Duration::from_secs(10))
        .unwrap_or_else(|_| panic!("{name}: no request recorded"))
}

fn assert_route(recorded: &Recorded, name: &str, method: &str, path: &str) {
    assert_eq!(recorded.method, method, "{name}: HTTP method");
    assert_eq!(recorded.path, path, "{name}: request path");
    if method == "GET" {
        assert!(recorded.body.is_empty(), "{name}: GET must not send a body");
    } else {
        assert!(
            recorded.body.starts_with('{') || recorded.body.starts_with('['),
            "{name}: POST must send a JSON body, got {:?}",
            recorded.body
        );
    }
}

fn json_body(recorded: &Recorded) -> serde_json::Value {
    serde_json::from_str(&recorded.body).expect("json body")
}

#[tokio::test]
async fn public_dispatch_names_reach_documented_routes() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    for (name, method, path) in PUBLIC_ROUTES {
        client
            .public_request(name, params_for(name))
            .await
            .unwrap_or_else(|error| panic!("{name}: {error}"));
        let recorded = next(&receiver, name);
        assert_route(&recorded, name, method, path);
        assert!(!recorded.signed, "{name}: public route must not be signed");
    }
}

#[tokio::test]
async fn private_dispatch_names_reach_documented_routes() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    for (name, method, path) in PRIVATE_ROUTES {
        client
            .private_request(name, params_for(name))
            .await
            .unwrap_or_else(|error| panic!("{name}: {error}"));
        let recorded = next(&receiver, name);
        assert_route(&recorded, name, method, path);
        assert!(recorded.signed, "{name}: private route must be signed");
    }
}

#[tokio::test]
async fn unknown_dispatch_names_are_rejected_before_transport() {
    let client = signed_client("http://127.0.0.1:9".to_string());
    let public = client
        .public_request("get_not_a_route", Vec::new())
        .await
        .expect_err("unknown public method");
    assert!(
        public
            .to_string()
            .contains("unsupported Bitget public method")
    );
    let private = client
        .private_request("place_not_a_route", Vec::new())
        .await
        .expect_err("unknown private method");
    assert!(
        private
            .to_string()
            .contains("unsupported Bitget private method")
    );
}

#[tokio::test]
async fn fee_rate_routes_select_business_line() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    for (name, business) in [
        ("get_spot_fee_rates", "businessType=spot"),
        ("get_futures_fee_rates", "businessType=mix"),
    ] {
        client
            .private_request(name, params_for(name))
            .await
            .expect("fee rate");
        let recorded = next(&receiver, name);
        assert!(recorded.query.contains(business), "{}", recorded.query);
        assert!(
            recorded.query.contains("symbol=BTCUSDT"),
            "{}",
            recorded.query
        );
    }
}

#[tokio::test]
async fn order_helpers_force_side_type_and_time_in_force() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    let cases: &[(&str, &[(&str, &str)])] = &[
        (
            "place_spot_market_sell_order",
            &[("side", "sell"), ("orderType", "market")],
        ),
        (
            "place_spot_post_only_limit_buy_order",
            &[
                ("side", "buy"),
                ("orderType", "limit"),
                ("force", "post_only"),
            ],
        ),
        (
            "place_spot_limit_sell_order",
            &[("side", "sell"), ("orderType", "limit"), ("force", "gtc")],
        ),
        (
            "place_futures_limit_sell_order",
            &[("side", "sell"), ("orderType", "limit"), ("force", "gtc")],
        ),
        (
            "place_futures_post_only_limit_buy_order",
            &[
                ("side", "buy"),
                ("orderType", "limit"),
                ("force", "post_only"),
            ],
        ),
        (
            "place_futures_market_buy_order",
            &[("side", "buy"), ("orderType", "market")],
        ),
    ];
    for (name, expected) in cases {
        let mut params = params_for(name);
        params.retain(|(key, _)| !matches!(key.as_str(), "side" | "orderType" | "force"));
        client
            .private_request(name, params)
            .await
            .unwrap_or_else(|error| panic!("{name}: {error}"));
        let body = json_body(&next(&receiver, name));
        for (key, value) in *expected {
            assert_eq!(body[*key], *value, "{name}: {key}");
        }
        assert_eq!(body["symbol"], "BTCUSDT", "{name}: symbol mapping");
    }
}

#[tokio::test]
async fn futures_order_defaults_and_batch_bodies() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    client
        .private_request(
            "place_futures_market_order",
            vec![
                ("product_symbol".into(), "ETH-USDT-SWAP".into()),
                ("side".into(), "sell".into()),
                ("size".into(), "2".into()),
            ],
        )
        .await
        .expect("futures order");
    let body = json_body(&next(&receiver, "place_futures_market_order"));
    assert_eq!(body["symbol"], "ETHUSDT");
    assert_eq!(body["productType"], "USDT-FUTURES");
    assert_eq!(body["marginMode"], "crossed");
    assert_eq!(body["marginCoin"], "USDT");
    assert_eq!(body["orderType"], "market");

    client
        .private_request(
            "cancel_futures_batch_orders",
            vec![
                ("productType".into(), "USDT-FUTURES".into()),
                ("product_symbol".into(), "BTC-USDT-SWAP".into()),
                ("orderIdList".into(), r#"[{"orderId":"1"}]"#.into()),
            ],
        )
        .await
        .expect("batch cancel");
    let body = json_body(&next(&receiver, "cancel_futures_batch_orders"));
    assert_eq!(body["orderIdList"][0]["orderId"], "1");
    assert_eq!(body["symbol"], "BTCUSDT");

    client
        .private_request(
            "place_uta_batch_orders",
            vec![(
                "orderList".into(),
                r#"[{"category":"SPOT","symbol":"BTCUSDT","qty":"1"}]"#.into(),
            )],
        )
        .await
        .expect("uta batch");
    let body = json_body(&next(&receiver, "place_uta_batch_orders"));
    assert!(
        body.is_array(),
        "UTA batch body must be the raw order array"
    );

    client
        .private_request(
            "place_spot_batch_orders",
            vec![
                ("product_symbol".into(), "BTC-USDT-SPOT".into()),
                ("batchMode".into(), "single".into()),
                ("orderList".into(), r#"[{"side":"buy","size":"1"}]"#.into()),
            ],
        )
        .await
        .expect("spot batch");
    let body = json_body(&next(&receiver, "place_spot_batch_orders"));
    assert_eq!(body["batchMode"], "single");
    assert_eq!(body["orderList"][0]["side"], "buy");
}

#[tokio::test]
async fn uta_routes_accept_native_symbol_and_forward_protection_fields() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    client
        .private_request(
            "place_uta_order",
            vec![
                ("category".into(), "USDT-FUTURES".into()),
                ("symbol".into(), "BTCUSDT".into()),
                ("side".into(), "buy".into()),
                ("orderType".into(), "limit".into()),
                ("qty".into(), "1".into()),
                ("price".into(), "100".into()),
                ("takeProfit".into(), "110".into()),
                ("stopLoss".into(), "90".into()),
                ("reduceOnly".into(), "no".into()),
            ],
        )
        .await
        .expect("uta order");
    let body = json_body(&next(&receiver, "place_uta_order"));
    assert_eq!(body["symbol"], "BTCUSDT");
    assert_eq!(body["takeProfit"], "110");
    assert_eq!(body["stopLoss"], "90");
    assert_eq!(body["reduceOnly"], "no");

    client
        .private_request(
            "get_uta_positions",
            vec![
                ("category".into(), "USDT-FUTURES".into()),
                ("product_symbol".into(), "BTC-USDT-SWAP".into()),
            ],
        )
        .await
        .expect("positions");
    let recorded = next(&receiver, "get_uta_positions");
    assert!(recorded.query.contains("category=USDT-FUTURES"));
    assert!(recorded.query.contains("symbol=BTCUSDT"));
}

#[tokio::test]
async fn required_parameters_fail_before_transport() {
    let client = signed_client("http://127.0.0.1:9".to_string());
    for name in [
        "get_futures_positions",
        "get_futures_position",
        "set_futures_leverage",
        "set_futures_margin_mode",
        "set_futures_position_mode",
        "get_uta_positions",
        "get_uta_history_orders",
        "place_uta_order",
        "place_futures_order",
        "place_spot_order",
        "place_futures_batch_orders",
        "cancel_futures_order",
        "get_futures_order",
        "get_deposit_records",
        "transfer",
        "get_transferable_coins",
    ] {
        assert!(
            client.private_request(name, Vec::new()).await.is_err(),
            "{name} must reject empty params"
        );
    }
    for name in [
        "get_futures_tickers",
        "get_uta_tickers",
        "get_spot_orderbook",
    ] {
        assert!(
            client.public_request(name, Vec::new()).await.is_err(),
            "{name} must reject empty params"
        );
    }
}

#[tokio::test]
async fn signed_requests_require_all_credentials() {
    let client = BitgetClient::public(Duration::from_secs(10)).expect("client");
    let error = client
        .private_request("get_spot_account_info", Vec::new())
        .await
        .expect_err("missing credentials");
    assert!(
        error
            .to_string()
            .contains("api_key, api_secret, and passphrase")
    );
}

#[tokio::test]
async fn additional_trading_controls_preserve_wire_types() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    client
        .private_request(
            "modify_futures_tpsl_order",
            vec![
                ("marginCoin".into(), "USDT".into()),
                ("productType".into(), "USDT-FUTURES".into()),
                ("product_symbol".into(), "BTC-USDT-SWAP".into()),
                ("triggerPrice".into(), "59000".into()),
                ("size".into(), "".into()),
                ("orderId".into(), "123".into()),
                ("executePrice".into(), "0".into()),
            ],
        )
        .await
        .expect("modify_futures_tpsl_order");
    let request = next(&receiver, "modify_futures_tpsl_order");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v2/mix/order/modify-tpsl-order", true)
    );
    assert_eq!(
        json_body(&request),
        serde_json::json!({"marginCoin": "USDT", "productType": "USDT-FUTURES", "symbol": "BTCUSDT", "triggerPrice": "59000", "size": "", "orderId": "123", "executePrice": "0"})
    );
    client
        .private_request(
            "place_futures_plan_order",
            vec![
                ("planType".into(), "normal_plan".into()),
                ("product_symbol".into(), "BTC-USDT-SWAP".into()),
                ("productType".into(), "USDT-FUTURES".into()),
                ("marginMode".into(), "isolated".into()),
                ("marginCoin".into(), "USDT".into()),
                ("size".into(), "1".into()),
                ("triggerPrice".into(), "59000".into()),
                ("triggerType".into(), "mark_price".into()),
                ("side".into(), "buy".into()),
                ("orderType".into(), "market".into()),
            ],
        )
        .await
        .expect("place_futures_plan_order");
    let request = next(&receiver, "place_futures_plan_order");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v2/mix/order/place-plan-order", true)
    );
    assert_eq!(
        json_body(&request),
        serde_json::json!({"planType": "normal_plan", "symbol": "BTCUSDT", "productType": "USDT-FUTURES", "marginMode": "isolated", "marginCoin": "USDT", "size": "1", "triggerPrice": "59000", "triggerType": "mark_price", "side": "buy", "orderType": "market"})
    );
    client
        .private_request(
            "place_futures_position_tpsl",
            vec![
                ("marginCoin".into(), "USDT".into()),
                ("productType".into(), "USDT-FUTURES".into()),
                ("product_symbol".into(), "BTC-USDT-SWAP".into()),
                ("holdSide".into(), "long".into()),
                ("stopLossTriggerPrice".into(), "59000".into()),
            ],
        )
        .await
        .expect("place_futures_position_tpsl");
    let request = next(&receiver, "place_futures_position_tpsl");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v2/mix/order/place-pos-tpsl", true)
    );
    assert_eq!(
        json_body(&request),
        serde_json::json!({"marginCoin": "USDT", "productType": "USDT-FUTURES", "symbol": "BTCUSDT", "holdSide": "long", "stopLossTriggerPrice": "59000"})
    );
    client
        .private_request(
            "place_futures_tpsl_order",
            vec![
                ("marginCoin".into(), "USDT".into()),
                ("productType".into(), "USDT-FUTURES".into()),
                ("product_symbol".into(), "BTC-USDT-SWAP".into()),
                ("planType".into(), "loss_plan".into()),
                ("triggerPrice".into(), "59000".into()),
                ("holdSide".into(), "long".into()),
                ("size".into(), "1".into()),
            ],
        )
        .await
        .expect("place_futures_tpsl_order");
    let request = next(&receiver, "place_futures_tpsl_order");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v2/mix/order/place-tpsl-order", true)
    );
    assert_eq!(
        json_body(&request),
        serde_json::json!({"marginCoin": "USDT", "productType": "USDT-FUTURES", "symbol": "BTCUSDT", "planType": "loss_plan", "triggerPrice": "59000", "holdSide": "long", "size": "1"})
    );
    client
        .private_request(
            "get_futures_plan_sub_order",
            vec![
                ("planType".into(), "normal_plan".into()),
                ("planOrderId".into(), "123".into()),
                ("productType".into(), "USDT-FUTURES".into()),
            ],
        )
        .await
        .expect("get_futures_plan_sub_order");
    let request = next(&receiver, "get_futures_plan_sub_order");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("GET", "/api/v2/mix/order/plan-sub-order", true)
    );
    let actual: std::collections::BTreeMap<String, String> =
        url::form_urlencoded::parse(request.query.as_bytes())
            .into_owned()
            .collect();
    assert_eq!(
        serde_json::to_value(actual).unwrap(),
        serde_json::json!({"planType": "normal_plan", "planOrderId": "123", "productType": "USDT-FUTURES"})
    );
    client
        .private_request(
            "modify_futures_plan_order",
            vec![
                ("productType".into(), "USDT-FUTURES".into()),
                ("orderId".into(), "123".into()),
                ("newTriggerPrice".into(), "0.05".into()),
                ("newStopLossTriggerPrice".into(), "0".into()),
            ],
        )
        .await
        .expect("modify_futures_plan_order");
    let request = next(&receiver, "modify_futures_plan_order");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v2/mix/order/modify-plan-order", true)
    );
    assert_eq!(
        json_body(&request),
        serde_json::json!({"productType": "USDT-FUTURES", "orderId": "123", "newTriggerPrice": "0.05", "newStopLossTriggerPrice": "0"})
    );
    client
        .private_request(
            "cancel_futures_plan_orders",
            vec![
                ("productType".into(), "USDT-FUTURES".into()),
                ("product_symbol".into(), "BTC-USDT-SWAP".into()),
                ("orderIdList".into(), "[{\"orderId\":\"123\"}]".into()),
            ],
        )
        .await
        .expect("cancel_futures_plan_orders");
    let request = next(&receiver, "cancel_futures_plan_orders");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v2/mix/order/cancel-plan-order", true)
    );
    assert_eq!(
        json_body(&request),
        serde_json::json!({"productType": "USDT-FUTURES", "symbol": "BTCUSDT", "orderIdList": [{"orderId": "123"}]})
    );
    client
        .private_request(
            "get_pending_futures_plan_orders",
            vec![
                ("planType".into(), "normal_plan".into()),
                ("productType".into(), "USDT-FUTURES".into()),
            ],
        )
        .await
        .expect("get_pending_futures_plan_orders");
    let request = next(&receiver, "get_pending_futures_plan_orders");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("GET", "/api/v2/mix/order/orders-plan-pending", true)
    );
    let actual: std::collections::BTreeMap<String, String> =
        url::form_urlencoded::parse(request.query.as_bytes())
            .into_owned()
            .collect();
    assert_eq!(
        serde_json::to_value(actual).unwrap(),
        serde_json::json!({"planType": "normal_plan", "productType": "USDT-FUTURES"})
    );
    client
        .private_request(
            "get_futures_plan_order_history",
            vec![
                ("planType".into(), "normal_plan".into()),
                ("productType".into(), "USDT-FUTURES".into()),
            ],
        )
        .await
        .expect("get_futures_plan_order_history");
    let request = next(&receiver, "get_futures_plan_order_history");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("GET", "/api/v2/mix/order/orders-plan-history", true)
    );
    let actual: std::collections::BTreeMap<String, String> =
        url::form_urlencoded::parse(request.query.as_bytes())
            .into_owned()
            .collect();
    assert_eq!(
        serde_json::to_value(actual).unwrap(),
        serde_json::json!({"planType": "normal_plan", "productType": "USDT-FUTURES"})
    );
    client
        .private_request(
            "place_spot_plan_order",
            vec![
                ("product_symbol".into(), "BTC-USDT-SPOT".into()),
                ("side".into(), "buy".into()),
                ("triggerPrice".into(), "59000".into()),
                ("orderType".into(), "market".into()),
                ("size".into(), "1".into()),
                ("triggerType".into(), "fill_price".into()),
            ],
        )
        .await
        .expect("place_spot_plan_order");
    let request = next(&receiver, "place_spot_plan_order");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v2/spot/trade/place-plan-order", true)
    );
    assert_eq!(
        json_body(&request),
        serde_json::json!({"symbol": "BTCUSDT", "side": "buy", "triggerPrice": "59000", "orderType": "market", "size": "1", "triggerType": "fill_price"})
    );
    client
        .private_request(
            "modify_spot_plan_order",
            vec![
                ("triggerPrice".into(), "59000".into()),
                ("orderType".into(), "market".into()),
                ("size".into(), "1".into()),
                ("orderId".into(), "123".into()),
            ],
        )
        .await
        .expect("modify_spot_plan_order");
    let request = next(&receiver, "modify_spot_plan_order");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v2/spot/trade/modify-plan-order", true)
    );
    assert_eq!(
        json_body(&request),
        serde_json::json!({"triggerPrice": "59000", "orderType": "market", "size": "1", "orderId": "123"})
    );
    client
        .private_request(
            "cancel_spot_plan_order",
            vec![("orderId".into(), "123".into())],
        )
        .await
        .expect("cancel_spot_plan_order");
    let request = next(&receiver, "cancel_spot_plan_order");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v2/spot/trade/cancel-plan-order", true)
    );
    assert_eq!(json_body(&request), serde_json::json!({"orderId": "123"}));
    client
        .private_request(
            "cancel_spot_plan_orders",
            vec![("symbolList".into(), "[\"BTC-USDT-SPOT\"]".into())],
        )
        .await
        .expect("cancel_spot_plan_orders");
    let request = next(&receiver, "cancel_spot_plan_orders");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v2/spot/trade/batch-cancel-plan-order", true)
    );
    assert_eq!(
        json_body(&request),
        serde_json::json!({"symbolList": ["BTCUSDT"]})
    );
    client
        .private_request("get_pending_spot_plan_orders", vec![])
        .await
        .expect("get_pending_spot_plan_orders");
    let request = next(&receiver, "get_pending_spot_plan_orders");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("GET", "/api/v2/spot/trade/current-plan-order", true)
    );
    let actual: std::collections::BTreeMap<String, String> =
        url::form_urlencoded::parse(request.query.as_bytes())
            .into_owned()
            .collect();
    assert_eq!(serde_json::to_value(actual).unwrap(), serde_json::json!({}));
    client
        .private_request("get_spot_plan_order_history", vec![])
        .await
        .expect("get_spot_plan_order_history");
    let request = next(&receiver, "get_spot_plan_order_history");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("GET", "/api/v2/spot/trade/history-plan-order", true)
    );
    let actual: std::collections::BTreeMap<String, String> =
        url::form_urlencoded::parse(request.query.as_bytes())
            .into_owned()
            .collect();
    assert_eq!(serde_json::to_value(actual).unwrap(), serde_json::json!({}));
    client
        .private_request(
            "get_spot_plan_sub_order",
            vec![("planOrderId".into(), "123".into())],
        )
        .await
        .expect("get_spot_plan_sub_order");
    let request = next(&receiver, "get_spot_plan_sub_order");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("GET", "/api/v2/spot/trade/plan-sub-order", true)
    );
    let actual: std::collections::BTreeMap<String, String> =
        url::form_urlencoded::parse(request.query.as_bytes())
            .into_owned()
            .collect();
    assert_eq!(
        serde_json::to_value(actual).unwrap(),
        serde_json::json!({"planOrderId": "123"})
    );
    client
        .private_request(
            "modify_futures_order",
            vec![
                ("product_symbol".into(), "BTC-USDT-SWAP".into()),
                ("productType".into(), "USDT-FUTURES".into()),
                ("newClientOid".into(), "replacement".into()),
                ("orderId".into(), "123".into()),
                ("newPrice".into(), "61000".into()),
                ("newSize".into(), "1".into()),
            ],
        )
        .await
        .expect("modify_futures_order");
    let request = next(&receiver, "modify_futures_order");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v2/mix/order/modify-order", true)
    );
    assert_eq!(
        json_body(&request),
        serde_json::json!({"symbol": "BTCUSDT", "productType": "USDT-FUTURES", "newClientOid": "replacement", "orderId": "123", "newPrice": "61000", "newSize": "1"})
    );
    client
        .private_request(
            "close_futures_positions",
            vec![
                ("all_symbols".into(), "true".into()),
                ("productType".into(), "USDT-FUTURES".into()),
            ],
        )
        .await
        .expect("close_futures_positions");
    let request = next(&receiver, "close_futures_positions");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v2/mix/order/close-positions", true)
    );
    assert_eq!(
        json_body(&request),
        serde_json::json!({"productType": "USDT-FUTURES"})
    );
    client
        .private_request(
            "cancel_all_futures_orders",
            vec![("productType".into(), "USDT-FUTURES".into())],
        )
        .await
        .expect("cancel_all_futures_orders");
    let request = next(&receiver, "cancel_all_futures_orders");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v2/mix/order/cancel-all-orders", true)
    );
    assert_eq!(
        json_body(&request),
        serde_json::json!({"productType": "USDT-FUTURES"})
    );
    client
        .private_request(
            "cancel_spot_orders_by_symbol",
            vec![("product_symbol".into(), "BTC-USDT-SPOT".into())],
        )
        .await
        .expect("cancel_spot_orders_by_symbol");
    let request = next(&receiver, "cancel_spot_orders_by_symbol");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v2/spot/trade/cancel-symbol-order", true)
    );
    assert_eq!(
        json_body(&request),
        serde_json::json!({"symbol": "BTCUSDT"})
    );
    client
        .private_request(
            "cancel_replace_spot_order",
            vec![
                ("product_symbol".into(), "BTC-USDT-SPOT".into()),
                ("price".into(), "60000".into()),
                ("size".into(), "1".into()),
                ("orderId".into(), "123".into()),
            ],
        )
        .await
        .expect("cancel_replace_spot_order");
    let request = next(&receiver, "cancel_replace_spot_order");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v2/spot/trade/cancel-replace-order", true)
    );
    assert_eq!(
        json_body(&request),
        serde_json::json!({"symbol": "BTCUSDT", "price": "60000", "size": "1", "orderId": "123"})
    );
    client
        .private_request(
            "adjust_futures_position_margin",
            vec![
                ("product_symbol".into(), "BTC-USDT-SWAP".into()),
                ("productType".into(), "USDT-FUTURES".into()),
                ("marginCoin".into(), "USDT".into()),
                ("holdSide".into(), "long".into()),
                ("amount".into(), "-1".into()),
            ],
        )
        .await
        .expect("adjust_futures_position_margin");
    let request = next(&receiver, "adjust_futures_position_margin");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v2/mix/account/set-margin", true)
    );
    assert_eq!(
        json_body(&request),
        serde_json::json!({"symbol": "BTCUSDT", "productType": "USDT-FUTURES", "marginCoin": "USDT", "holdSide": "long", "amount": "-1"})
    );
    client
        .public_request(
            "get_futures_symbol_price",
            vec![
                ("product_symbol".into(), "BTC-USDT-SWAP".into()),
                ("productType".into(), "USDT-FUTURES".into()),
            ],
        )
        .await
        .expect("get_futures_symbol_price");
    let request = next(&receiver, "get_futures_symbol_price");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("GET", "/api/v2/mix/market/symbol-price", false)
    );
    let actual: std::collections::BTreeMap<String, String> =
        url::form_urlencoded::parse(request.query.as_bytes())
            .into_owned()
            .collect();
    assert_eq!(
        serde_json::to_value(actual).unwrap(),
        serde_json::json!({"symbol": "BTCUSDT", "productType": "USDT-FUTURES"})
    );
    client
        .private_request(
            "modify_uta_order",
            vec![
                ("product_symbol".into(), "BTC-USDT-SWAP".into()),
                ("category".into(), "USDT-FUTURES".into()),
                ("orderId".into(), "123".into()),
                ("qty".into(), "2".into()),
                ("requestId".into(), "123456789012345678".into()),
                ("takeProfit".into(), "0".into()),
                ("stopLoss".into(), "0".into()),
            ],
        )
        .await
        .expect("modify_uta_order");
    let request = next(&receiver, "modify_uta_order");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v3/trade/modify-order", true)
    );
    assert_eq!(
        json_body(&request),
        serde_json::json!({"symbol": "BTCUSDT", "category": "USDT-FUTURES", "orderId": "123", "qty": "2", "requestId": 123456789012345678_i64, "takeProfit": "0", "stopLoss": "0"})
    );
    client
        .private_request(
            "cancel_uta_orders_by_symbol",
            vec![("category".into(), "USDT-FUTURES".into())],
        )
        .await
        .expect("cancel_uta_orders_by_symbol");
    let request = next(&receiver, "cancel_uta_orders_by_symbol");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v3/trade/cancel-symbol-order", true)
    );
    assert_eq!(
        json_body(&request),
        serde_json::json!({"category": "USDT-FUTURES"})
    );
    client
        .private_request(
            "set_uta_cancel_countdown",
            vec![("countdown".into(), "10".into())],
        )
        .await
        .expect("set_uta_cancel_countdown");
    let request = next(&receiver, "set_uta_cancel_countdown");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v3/trade/countdown-cancel-all", true)
    );
    assert_eq!(json_body(&request), serde_json::json!({"countdown": "10"}));
    client
        .private_request(
            "close_uta_positions",
            vec![
                ("all_symbols".into(), "true".into()),
                ("category".into(), "USDT-FUTURES".into()),
            ],
        )
        .await
        .expect("close_uta_positions");
    let request = next(&receiver, "close_uta_positions");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v3/trade/close-positions", true)
    );
    assert_eq!(
        json_body(&request),
        serde_json::json!({"category": "USDT-FUTURES"})
    );
    client
        .private_request(
            "get_uta_position_history",
            vec![("category".into(), "USDT-FUTURES".into())],
        )
        .await
        .expect("get_uta_position_history");
    let request = next(&receiver, "get_uta_position_history");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("GET", "/api/v3/position/history-position", true)
    );
    let actual: std::collections::BTreeMap<String, String> =
        url::form_urlencoded::parse(request.query.as_bytes())
            .into_owned()
            .collect();
    assert_eq!(
        serde_json::to_value(actual).unwrap(),
        serde_json::json!({"category": "USDT-FUTURES"})
    );
    client
        .private_request(
            "adjust_uta_position_margin",
            vec![
                ("category".into(), "USDT-FUTURES".into()),
                ("product_symbol".into(), "BTC-USDT-SWAP".into()),
                ("posSide".into(), "long".into()),
                ("operation".into(), "add".into()),
                ("amount".into(), "1".into()),
            ],
        )
        .await
        .expect("adjust_uta_position_margin");
    let request = next(&receiver, "adjust_uta_position_margin");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("POST", "/api/v3/account/set-margin", true)
    );
    assert_eq!(
        json_body(&request),
        serde_json::json!({"category": "USDT-FUTURES", "symbol": "BTCUSDT", "posSide": "long", "operation": "add", "amount": "1"})
    );
    client
        .private_request(
            "get_uta_financial_records",
            vec![("category".into(), "USDT-FUTURES".into())],
        )
        .await
        .expect("get_uta_financial_records");
    let request = next(&receiver, "get_uta_financial_records");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("GET", "/api/v3/account/financial-records", true)
    );
    let actual: std::collections::BTreeMap<String, String> =
        url::form_urlencoded::parse(request.query.as_bytes())
            .into_owned()
            .collect();
    assert_eq!(
        serde_json::to_value(actual).unwrap(),
        serde_json::json!({"category": "USDT-FUTURES"})
    );
    client
        .public_request(
            "get_uta_open_interest",
            vec![("category".into(), "USDT-FUTURES".into())],
        )
        .await
        .expect("get_uta_open_interest");
    let request = next(&receiver, "get_uta_open_interest");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("GET", "/api/v3/market/open-interest", false)
    );
    let actual: std::collections::BTreeMap<String, String> =
        url::form_urlencoded::parse(request.query.as_bytes())
            .into_owned()
            .collect();
    assert_eq!(
        serde_json::to_value(actual).unwrap(),
        serde_json::json!({"category": "USDT-FUTURES"})
    );
    client
        .public_request(
            "get_uta_current_funding_rate",
            vec![("category".into(), "USDT-FUTURES".into())],
        )
        .await
        .expect("get_uta_current_funding_rate");
    let request = next(&receiver, "get_uta_current_funding_rate");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.signed
        ),
        ("GET", "/api/v3/market/current-fund-rate", false)
    );
    let actual: std::collections::BTreeMap<String, String> =
        url::form_urlencoded::parse(request.query.as_bytes())
            .into_owned()
            .collect();
    assert_eq!(
        serde_json::to_value(actual).unwrap(),
        serde_json::json!({"category": "USDT-FUTURES"})
    );
}

#[tokio::test]
async fn ordinary_risk_routes_preserve_parameters_and_authentication() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    let cases: &[(&str, &str, &str, bool, &[(&str, &str)], &str)] = &[
        (
            "get_futures_trade_history",
            "GET",
            "/api/v2/mix/market/fills-history",
            true,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("productType", "USDT-FUTURES"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"productType\":\"USDT-FUTURES\"}",
        ),
        (
            "get_futures_index_candle_history",
            "GET",
            "/api/v2/mix/market/history-index-candles",
            true,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("productType", "USDT-FUTURES"),
                ("granularity", "1m"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"productType\":\"USDT-FUTURES\",\"granularity\":\"1m\"}",
        ),
        (
            "get_futures_mark_candle_history",
            "GET",
            "/api/v2/mix/market/history-mark-candles",
            true,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("productType", "USDT-FUTURES"),
                ("granularity", "1m"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"productType\":\"USDT-FUTURES\",\"granularity\":\"1m\"}",
        ),
        (
            "get_futures_next_funding_time",
            "GET",
            "/api/v2/mix/market/funding-time",
            true,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("productType", "USDT-FUTURES"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"productType\":\"USDT-FUTURES\"}",
        ),
        (
            "get_futures_open_interest_limit",
            "GET",
            "/api/v2/mix/market/oi-limit",
            true,
            &[("productType", "USDT-FUTURES")],
            "{\"productType\":\"USDT-FUTURES\"}",
        ),
        (
            "get_futures_position_tiers",
            "GET",
            "/api/v2/mix/market/query-position-lever",
            true,
            &[
                ("productType", "USDT-FUTURES"),
                ("product_symbol", "BTC-USDT-SWAP"),
            ],
            "{\"productType\":\"USDT-FUTURES\",\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "get_futures_discount_rates",
            "GET",
            "/api/v2/mix/market/discount-rate",
            true,
            &[],
            "{}",
        ),
        (
            "get_futures_interest_exchange_rates",
            "GET",
            "/api/v2/mix/market/exchange-rate",
            true,
            &[],
            "{}",
        ),
        (
            "get_futures_interest_rate_history",
            "GET",
            "/api/v2/mix/market/union-interest-rate-history",
            true,
            &[("coin", "USDT")],
            "{\"coin\":\"USDT\"}",
        ),
        (
            "get_futures_vip_fee_rates",
            "GET",
            "/api/v2/mix/market/vip-fee-rate",
            true,
            &[],
            "{}",
        ),
        (
            "get_futures_sub_account_assets",
            "GET",
            "/api/v2/mix/account/sub-account-assets",
            false,
            &[("productType", "USDT-FUTURES")],
            "{\"productType\":\"USDT-FUTURES\"}",
        ),
        (
            "get_futures_estimated_open_count",
            "GET",
            "/api/v2/mix/account/open-count",
            false,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("productType", "USDT-FUTURES"),
                ("marginCoin", "USDT"),
                ("openAmount", "10"),
                ("openPrice", "100"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"productType\":\"USDT-FUTURES\",\"marginCoin\":\"USDT\",\"openAmount\":\"10\",\"openPrice\":\"100\"}",
        ),
        (
            "get_futures_liquidation_price",
            "GET",
            "/api/v2/mix/account/liq-price",
            false,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("productType", "USDT-FUTURES"),
                ("marginCoin", "USDT"),
                ("posSide", "long"),
                ("orderType", "limit"),
                ("openAmount", "10"),
                ("openPrice", "100"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"productType\":\"USDT-FUTURES\",\"marginCoin\":\"USDT\",\"posSide\":\"long\",\"orderType\":\"limit\",\"openAmount\":\"10\",\"openPrice\":\"100\"}",
        ),
        (
            "get_futures_max_open_quantity",
            "GET",
            "/api/v2/mix/account/max-open",
            false,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("productType", "USDT-FUTURES"),
                ("marginCoin", "USDT"),
                ("posSide", "long"),
                ("orderType", "limit"),
                ("openPrice", "100"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"productType\":\"USDT-FUTURES\",\"marginCoin\":\"USDT\",\"posSide\":\"long\",\"orderType\":\"limit\",\"openPrice\":\"100\"}",
        ),
        (
            "get_futures_interest_history",
            "GET",
            "/api/v2/mix/account/interest-history",
            false,
            &[
                ("productType", "USDT-FUTURES"),
                ("startTime", "1700000000000"),
                ("endTime", "1700000001000"),
            ],
            "{\"productType\":\"USDT-FUTURES\",\"startTime\":\"1700000000000\",\"endTime\":\"1700000001000\"}",
        ),
        (
            "set_futures_all_leverage",
            "POST",
            "/api/v2/mix/account/set-all-leverage",
            false,
            &[("productType", "USDT-FUTURES"), ("leverage", "5")],
            "{\"productType\":\"USDT-FUTURES\",\"leverage\":\"5\"}",
        ),
        (
            "set_futures_auto_margin",
            "POST",
            "/api/v2/mix/account/set-auto-margin",
            false,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("autoMargin", "on"),
                ("marginCoin", "USDT"),
                ("holdSide", "long"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"autoMargin\":\"on\",\"marginCoin\":\"USDT\",\"holdSide\":\"long\"}",
        ),
        (
            "set_futures_asset_mode",
            "POST",
            "/api/v2/mix/account/set-asset-mode",
            false,
            &[
                ("confirm", "true"),
                ("productType", "USDT-FUTURES"),
                ("assetMode", "single"),
            ],
            "{\"productType\":\"USDT-FUTURES\",\"assetMode\":\"single\"}",
        ),
        (
            "convert_futures_union_asset",
            "POST",
            "/api/v2/mix/account/union-convert",
            false,
            &[("coin", "USDT"), ("amount", "1")],
            "{\"coin\":\"USDT\",\"amount\":\"1\"}",
        ),
        (
            "get_futures_union_transfer_limits",
            "GET",
            "/api/v2/mix/account/transfer-limits",
            false,
            &[("coin", "USDT")],
            "{\"coin\":\"USDT\"}",
        ),
        (
            "get_futures_union_config",
            "GET",
            "/api/v2/mix/account/union-config",
            false,
            &[],
            "{}",
        ),
        (
            "get_futures_isolated_symbols",
            "GET",
            "/api/v2/mix/account/isolated-symbols",
            false,
            &[("productType", "USDT-FUTURES")],
            "{\"productType\":\"USDT-FUTURES\"}",
        ),
        (
            "get_futures_position_history",
            "GET",
            "/api/v2/mix/position/history-position",
            false,
            &[],
            "{}",
        ),
        (
            "get_futures_adl_rank",
            "GET",
            "/api/v2/mix/position/adlRank",
            false,
            &[("productType", "USDT-FUTURES")],
            "{\"productType\":\"USDT-FUTURES\"}",
        ),
        (
            "reverse_futures_position",
            "POST",
            "/api/v2/mix/order/click-backhand",
            false,
            &[
                ("confirm", "true"),
                ("product_symbol", "BTC-USDT-SWAP"),
                ("marginCoin", "USDT"),
                ("productType", "USDT-FUTURES"),
                ("side", "buy"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"marginCoin\":\"USDT\",\"productType\":\"USDT-FUTURES\",\"side\":\"buy\"}",
        ),
        (
            "get_futures_fill_history",
            "GET",
            "/api/v2/mix/order/fill-history",
            false,
            &[("productType", "USDT-FUTURES")],
            "{\"productType\":\"USDT-FUTURES\"}",
        ),
        (
            "get_spot_sub_account_transfer_records",
            "GET",
            "/api/v2/spot/account/sub-main-trans-record",
            false,
            &[],
            "{}",
        ),
        (
            "get_spot_sub_account_assets",
            "GET",
            "/api/v2/spot/account/subaccount-assets",
            false,
            &[],
            "{}",
        ),
        (
            "transfer_spot_sub_account",
            "POST",
            "/api/v2/spot/wallet/subaccount-transfer",
            false,
            &[
                ("fromType", "spot"),
                ("toType", "spot"),
                ("amount", "1"),
                ("coin", "USDT"),
                ("fromUserId", "1"),
                ("toUserId", "2"),
            ],
            "{\"fromType\":\"spot\",\"toType\":\"spot\",\"amount\":\"1\",\"coin\":\"USDT\",\"fromUserId\":\"1\",\"toUserId\":\"2\"}",
        ),
        (
            "get_cross_margin_assets",
            "GET",
            "/api/v2/margin/crossed/account/assets",
            false,
            &[],
            "{}",
        ),
        (
            "borrow_cross_margin_asset",
            "POST",
            "/api/v2/margin/crossed/account/borrow",
            false,
            &[("coin", "USDT"), ("borrowAmount", "1")],
            "{\"coin\":\"USDT\",\"borrowAmount\":\"1\"}",
        ),
        (
            "repay_cross_margin_asset",
            "POST",
            "/api/v2/margin/crossed/account/repay",
            false,
            &[("coin", "USDT"), ("repayAmount", "1")],
            "{\"coin\":\"USDT\",\"repayAmount\":\"1\"}",
        ),
        (
            "get_cross_margin_risk_rate",
            "GET",
            "/api/v2/margin/crossed/account/risk-rate",
            false,
            &[],
            "{}",
        ),
        (
            "get_cross_margin_max_borrowable",
            "GET",
            "/api/v2/margin/crossed/account/max-borrowable-amount",
            false,
            &[("coin", "USDT")],
            "{\"coin\":\"USDT\"}",
        ),
        (
            "get_cross_margin_max_transferable",
            "GET",
            "/api/v2/margin/crossed/account/max-transfer-out-amount",
            false,
            &[("coin", "USDT")],
            "{\"coin\":\"USDT\"}",
        ),
        (
            "flash_repay_cross_margin_assets",
            "POST",
            "/api/v2/margin/crossed/account/flash-repay",
            false,
            &[],
            "{}",
        ),
        (
            "get_cross_margin_flash_repay_result",
            "POST",
            "/api/v2/margin/crossed/account/query-flash-repay-status",
            false,
            &[("idList", "[\"123\"]")],
            "{\"idList\":[\"123\"]}",
        ),
        (
            "get_cross_margin_interest_rate_limits",
            "GET",
            "/api/v2/margin/crossed/interest-rate-and-limit",
            false,
            &[("coin", "USDT")],
            "{\"coin\":\"USDT\"}",
        ),
        (
            "get_cross_margin_tiers",
            "GET",
            "/api/v2/margin/crossed/tier-data",
            false,
            &[("coin", "USDT")],
            "{\"coin\":\"USDT\"}",
        ),
        (
            "get_cross_margin_borrow_history",
            "GET",
            "/api/v2/margin/crossed/borrow-history",
            false,
            &[("startTime", "1700000000000")],
            "{\"startTime\":\"1700000000000\"}",
        ),
        (
            "get_cross_margin_repay_history",
            "GET",
            "/api/v2/margin/crossed/repay-history",
            false,
            &[("startTime", "1700000000000")],
            "{\"startTime\":\"1700000000000\"}",
        ),
        (
            "get_cross_margin_interest_history",
            "GET",
            "/api/v2/margin/crossed/interest-history",
            false,
            &[("startTime", "1700000000000")],
            "{\"startTime\":\"1700000000000\"}",
        ),
        (
            "get_cross_margin_liquidation_history",
            "GET",
            "/api/v2/margin/crossed/liquidation-history",
            false,
            &[("startTime", "1700000000000")],
            "{\"startTime\":\"1700000000000\"}",
        ),
        (
            "get_cross_margin_financial_records",
            "GET",
            "/api/v2/margin/crossed/financial-records",
            false,
            &[("startTime", "1700000000000")],
            "{\"startTime\":\"1700000000000\"}",
        ),
        (
            "place_cross_margin_order",
            "POST",
            "/api/v2/margin/crossed/place-order",
            false,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("orderType", "limit"),
                ("loanType", "normal"),
                ("force", "gtc"),
                ("side", "buy"),
                ("price", "100"),
                ("baseSize", "1"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"orderType\":\"limit\",\"loanType\":\"normal\",\"force\":\"gtc\",\"side\":\"buy\",\"price\":\"100\",\"baseSize\":\"1\"}",
        ),
        (
            "cancel_cross_margin_order",
            "POST",
            "/api/v2/margin/crossed/cancel-order",
            false,
            &[("product_symbol", "BTC-USDT-SWAP"), ("orderId", "123")],
            "{\"symbol\":\"BTCUSDT\",\"orderId\":\"123\"}",
        ),
        (
            "get_cross_margin_open_orders",
            "GET",
            "/api/v2/margin/crossed/open-orders",
            false,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("startTime", "1700000000000"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"startTime\":\"1700000000000\"}",
        ),
        (
            "get_cross_margin_order_history",
            "GET",
            "/api/v2/margin/crossed/history-orders",
            false,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("startTime", "1700000000000"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"startTime\":\"1700000000000\"}",
        ),
        (
            "get_cross_margin_fills",
            "GET",
            "/api/v2/margin/crossed/fills",
            false,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("startTime", "1700000000000"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"startTime\":\"1700000000000\"}",
        ),
        (
            "get_isolated_margin_assets",
            "GET",
            "/api/v2/margin/isolated/account/assets",
            false,
            &[],
            "{}",
        ),
        (
            "borrow_isolated_margin_asset",
            "POST",
            "/api/v2/margin/isolated/account/borrow",
            false,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("coin", "USDT"),
                ("borrowAmount", "1"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"coin\":\"USDT\",\"borrowAmount\":\"1\"}",
        ),
        (
            "repay_isolated_margin_asset",
            "POST",
            "/api/v2/margin/isolated/account/repay",
            false,
            &[
                ("repayAmount", "1"),
                ("coin", "USDT"),
                ("product_symbol", "BTC-USDT-SWAP"),
            ],
            "{\"repayAmount\":\"1\",\"coin\":\"USDT\",\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "get_isolated_margin_risk_rate",
            "GET",
            "/api/v2/margin/isolated/account/risk-rate",
            false,
            &[],
            "{}",
        ),
        (
            "get_isolated_margin_max_borrowable",
            "GET",
            "/api/v2/margin/isolated/account/max-borrowable-amount",
            false,
            &[("product_symbol", "BTC-USDT-SWAP")],
            "{\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "get_isolated_margin_max_transferable",
            "GET",
            "/api/v2/margin/isolated/account/max-transfer-out-amount",
            false,
            &[("product_symbol", "BTC-USDT-SWAP")],
            "{\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "flash_repay_isolated_margin_assets",
            "POST",
            "/api/v2/margin/isolated/account/flash-repay",
            false,
            &[],
            "{}",
        ),
        (
            "get_isolated_margin_flash_repay_result",
            "POST",
            "/api/v2/margin/isolated/account/query-flash-repay-status",
            false,
            &[("idList", "[\"123\"]")],
            "{\"idList\":[\"123\"]}",
        ),
        (
            "get_isolated_margin_interest_rate_limits",
            "GET",
            "/api/v2/margin/isolated/interest-rate-and-limit",
            false,
            &[("product_symbol", "BTC-USDT-SWAP")],
            "{\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "get_isolated_margin_tiers",
            "GET",
            "/api/v2/margin/isolated/tier-data",
            false,
            &[("product_symbol", "BTC-USDT-SWAP")],
            "{\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "get_isolated_margin_borrow_history",
            "GET",
            "/api/v2/margin/isolated/borrow-history",
            false,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("startTime", "1700000000000"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"startTime\":\"1700000000000\"}",
        ),
        (
            "get_isolated_margin_repay_history",
            "GET",
            "/api/v2/margin/isolated/repay-history",
            false,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("startTime", "1700000000000"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"startTime\":\"1700000000000\"}",
        ),
        (
            "get_isolated_margin_interest_history",
            "GET",
            "/api/v2/margin/isolated/interest-history",
            false,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("startTime", "1700000000000"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"startTime\":\"1700000000000\"}",
        ),
        (
            "get_isolated_margin_liquidation_history",
            "GET",
            "/api/v2/margin/isolated/liquidation-history",
            false,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("startTime", "1700000000000"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"startTime\":\"1700000000000\"}",
        ),
        (
            "get_isolated_margin_financial_records",
            "GET",
            "/api/v2/margin/isolated/financial-records",
            false,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("startTime", "1700000000000"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"startTime\":\"1700000000000\"}",
        ),
        (
            "place_isolated_margin_order",
            "POST",
            "/api/v2/margin/isolated/place-order",
            false,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("orderType", "limit"),
                ("loanType", "normal"),
                ("force", "gtc"),
                ("side", "buy"),
                ("price", "100"),
                ("baseSize", "1"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"orderType\":\"limit\",\"loanType\":\"normal\",\"force\":\"gtc\",\"side\":\"buy\",\"price\":\"100\",\"baseSize\":\"1\"}",
        ),
        (
            "cancel_isolated_margin_order",
            "POST",
            "/api/v2/margin/isolated/cancel-order",
            false,
            &[("product_symbol", "BTC-USDT-SWAP"), ("orderId", "123")],
            "{\"symbol\":\"BTCUSDT\",\"orderId\":\"123\"}",
        ),
        (
            "get_isolated_margin_open_orders",
            "GET",
            "/api/v2/margin/isolated/open-orders",
            false,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("startTime", "1700000000000"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"startTime\":\"1700000000000\"}",
        ),
        (
            "get_isolated_margin_order_history",
            "GET",
            "/api/v2/margin/isolated/history-orders",
            false,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("startTime", "1700000000000"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"startTime\":\"1700000000000\"}",
        ),
        (
            "get_isolated_margin_fills",
            "GET",
            "/api/v2/margin/isolated/fills",
            false,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("startTime", "1700000000000"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"startTime\":\"1700000000000\"}",
        ),
        (
            "get_uta_funding_rate_history",
            "GET",
            "/api/v3/market/history-fund-rate",
            true,
            &[
                ("category", "USDT-FUTURES"),
                ("product_symbol", "BTC-USDT-SWAP"),
            ],
            "{\"category\":\"USDT-FUTURES\",\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "get_uta_index_components",
            "GET",
            "/api/v3/market/index-components",
            true,
            &[("product_symbol", "BTC-USDT-SWAP")],
            "{\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "get_uta_margin_loan_rates",
            "GET",
            "/api/v3/market/margin-loans",
            true,
            &[("coin", "USDT")],
            "{\"coin\":\"USDT\"}",
        ),
        (
            "get_uta_position_tiers",
            "GET",
            "/api/v3/market/position-tier",
            true,
            &[("category", "USDT-FUTURES")],
            "{\"category\":\"USDT-FUTURES\"}",
        ),
        (
            "get_uta_open_interest_limit",
            "GET",
            "/api/v3/market/oi-limit",
            true,
            &[("category", "USDT-FUTURES")],
            "{\"category\":\"USDT-FUTURES\"}",
        ),
        (
            "get_uta_discount_rates",
            "GET",
            "/api/v3/market/discount-rate",
            true,
            &[],
            "{}",
        ),
        (
            "get_uta_rpi_orderbook",
            "GET",
            "/api/v3/market/rpi-orderbook",
            true,
            &[
                ("category", "USDT-FUTURES"),
                ("product_symbol", "BTC-USDT-SWAP"),
            ],
            "{\"category\":\"USDT-FUTURES\",\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "get_uta_rpi_symbols",
            "GET",
            "/api/v3/market/rpi-symbols",
            true,
            &[],
            "{}",
        ),
        (
            "get_uta_funding_assets",
            "GET",
            "/api/v3/account/funding-assets",
            false,
            &[],
            "{}",
        ),
        (
            "get_uta_funding_records",
            "GET",
            "/api/v3/account/funding-financial-records",
            false,
            &[],
            "{}",
        ),
        (
            "get_uta_fee_rate",
            "GET",
            "/api/v3/account/fee-rate",
            false,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("category", "USDT-FUTURES"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"category\":\"USDT-FUTURES\"}",
        ),
        (
            "get_uta_max_transferable",
            "GET",
            "/api/v3/account/max-transferable",
            false,
            &[("coin", "USDT")],
            "{\"coin\":\"USDT\"}",
        ),
        (
            "set_uta_collateral_type",
            "POST",
            "/api/v3/account/set-collateral-type",
            false,
            &[("collateralType", "all")],
            "{\"collateralType\":\"all\"}",
        ),
        (
            "get_uta_settings",
            "GET",
            "/api/v3/account/settings",
            false,
            &[],
            "{}",
        ),
        (
            "get_uta_delta_info",
            "GET",
            "/api/v3/account/delta-info",
            false,
            &[],
            "{}",
        ),
        (
            "get_uta_repayable_coins",
            "GET",
            "/api/v3/account/repayable-coins",
            false,
            &[],
            "{}",
        ),
        (
            "get_uta_payment_coins",
            "GET",
            "/api/v3/account/payment-coins",
            false,
            &[],
            "{}",
        ),
        (
            "borrow_uta_asset",
            "POST",
            "/api/v3/account/borrow",
            false,
            &[("coin", "USDT"), ("amount", "1")],
            "{\"coin\":\"USDT\",\"amount\":\"1\"}",
        ),
        (
            "get_uta_max_borrowable",
            "GET",
            "/api/v3/account/max-borrowable",
            false,
            &[("coin", "USDT")],
            "{\"coin\":\"USDT\"}",
        ),
        (
            "get_uta_account_open_interest_limit",
            "GET",
            "/api/v3/account/open-interest-limit",
            false,
            &[
                ("product_symbol", "BTC-USDT-SWAP"),
                ("category", "USDT-FUTURES"),
            ],
            "{\"symbol\":\"BTCUSDT\",\"category\":\"USDT-FUTURES\"}",
        ),
        (
            "get_uta_transferable_coins",
            "GET",
            "/api/v3/account/transferable-coins",
            false,
            &[("fromType", "spot"), ("toType", "spot")],
            "{\"fromType\":\"spot\",\"toType\":\"spot\"}",
        ),
        (
            "get_uta_max_open_available",
            "POST",
            "/api/v3/account/max-open-available",
            false,
            &[
                ("category", "USDT-FUTURES"),
                ("product_symbol", "BTC-USDT-SWAP"),
                ("orderType", "limit"),
                ("side", "buy"),
                ("price", "100"),
            ],
            "{\"category\":\"USDT-FUTURES\",\"symbol\":\"BTCUSDT\",\"orderType\":\"limit\",\"side\":\"buy\",\"price\":\"100\"}",
        ),
        (
            "get_uta_position_transfer_history",
            "GET",
            "/api/v3/account/move-position-history",
            false,
            &[("category", "USDT-FUTURES")],
            "{\"category\":\"USDT-FUTURES\"}",
        ),
        (
            "set_uta_repay_mode",
            "POST",
            "/api/v3/account/set-repay-mode",
            false,
            &[("repayMode", "manual")],
            "{\"repayMode\":\"manual\"}",
        ),
        (
            "get_uta_eligible_discount_rates",
            "GET",
            "/api/v3/account/eligible-discount-rate",
            false,
            &[],
            "{}",
        ),
        (
            "get_uta_eligible_loan_info",
            "GET",
            "/api/v3/account/eligible-loan-info",
            false,
            &[],
            "{}",
        ),
        (
            "get_uta_eligible_margin_tiers",
            "GET",
            "/api/v3/account/eligible-margin-tier",
            false,
            &[],
            "{}",
        ),
        (
            "get_uta_eligible_symbols",
            "GET",
            "/api/v3/account/eligible-symbols",
            false,
            &[],
            "{}",
        ),
        (
            "get_uta_convert_records",
            "GET",
            "/api/v3/account/convert-records",
            false,
            &[],
            "{}",
        ),
        (
            "set_uta_account_mode",
            "POST",
            "/api/v3/account/adjust-account-mode",
            false,
            &[("confirm", "true"), ("mode", "advanced")],
            "{\"mode\":\"advanced\"}",
        ),
        (
            "get_uta_adl_rank",
            "GET",
            "/api/v3/position/adlRank",
            false,
            &[],
            "{}",
        ),
    ];
    for (name, method, path, public, params, expected) in cases {
        let params = params
            .iter()
            .map(|(key, value)| ((*key).to_string(), (*value).to_string()))
            .collect();
        let response = if *public {
            client.public_request(name, params).await
        } else {
            client.private_request(name, params).await
        };
        response.unwrap_or_else(|error| panic!("{name}: {error}"));
        let request = next(&receiver, name);
        assert_route(&request, name, method, path);
        assert_eq!(request.signed, !public, "{name}");
        let actual = if *method == "GET" {
            let pairs: serde_json::Map<String, serde_json::Value> =
                url::form_urlencoded::parse(request.query.as_bytes())
                    .map(|(key, value)| {
                        (
                            key.into_owned(),
                            serde_json::Value::String(value.into_owned()),
                        )
                    })
                    .collect();
            serde_json::Value::Object(pairs)
        } else {
            serde_json::from_str(&request.body).expect("JSON body")
        };
        assert_eq!(
            actual,
            serde_json::from_str::<serde_json::Value>(expected).expect("fixture"),
            "{name}"
        );
    }
}

#[tokio::test]
async fn batch_controls_preserve_nested_and_root_array_bodies() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    client.private_request("place_cross_margin_batch_orders", vec![("orderList".into(), "[{\"orderType\":\"market\",\"side\":\"buy\",\"loanType\":\"normal\",\"force\":\"gtc\",\"quoteSize\":\"100\"}]".into()),("product_symbol".into(), "BTC-USDT-SPOT".into())]).await.expect("place_cross_margin_batch_orders");
    let request = next(&receiver, "place_cross_margin_batch_orders");
    assert_route(
        &request,
        "place_cross_margin_batch_orders",
        "POST",
        "/api/v2/margin/crossed/batch-place-order",
    );
    assert!(request.signed);
    assert_eq!(serde_json::from_str::<serde_json::Value>(&request.body).expect("body"), serde_json::from_str::<serde_json::Value>("{\"symbol\": \"BTCUSDT\", \"orderList\": [{\"orderType\": \"market\", \"side\": \"buy\", \"loanType\": \"normal\", \"force\": \"gtc\", \"quoteSize\": \"100\"}]}").expect("fixture"));
    client.private_request("place_isolated_margin_batch_orders", vec![("orderList".into(), "[{\"orderType\":\"market\",\"side\":\"buy\",\"loanType\":\"normal\",\"force\":\"gtc\",\"quoteSize\":\"100\"}]".into()),("product_symbol".into(), "BTC-USDT-SPOT".into())]).await.expect("place_isolated_margin_batch_orders");
    let request = next(&receiver, "place_isolated_margin_batch_orders");
    assert_route(
        &request,
        "place_isolated_margin_batch_orders",
        "POST",
        "/api/v2/margin/isolated/batch-place-order",
    );
    assert!(request.signed);
    assert_eq!(serde_json::from_str::<serde_json::Value>(&request.body).expect("body"), serde_json::from_str::<serde_json::Value>("{\"symbol\": \"BTCUSDT\", \"orderList\": [{\"orderType\": \"market\", \"side\": \"buy\", \"loanType\": \"normal\", \"force\": \"gtc\", \"quoteSize\": \"100\"}]}").expect("fixture"));
    client
        .private_request(
            "cancel_cross_margin_batch_orders",
            vec![
                (
                    "orderIdList".into(),
                    "[{\"orderId\":\"123\"},{\"clientOid\":\"order-2\"}]".into(),
                ),
                ("product_symbol".into(), "BTC-USDT-SPOT".into()),
            ],
        )
        .await
        .expect("cancel_cross_margin_batch_orders");
    let request = next(&receiver, "cancel_cross_margin_batch_orders");
    assert_route(
        &request,
        "cancel_cross_margin_batch_orders",
        "POST",
        "/api/v2/margin/crossed/batch-cancel-order",
    );
    assert!(request.signed);
    assert_eq!(serde_json::from_str::<serde_json::Value>(&request.body).expect("body"), serde_json::from_str::<serde_json::Value>("{\"symbol\": \"BTCUSDT\", \"orderIdList\": [{\"orderId\": \"123\"}, {\"clientOid\": \"order-2\"}]}").expect("fixture"));
    client
        .private_request(
            "cancel_isolated_margin_batch_orders",
            vec![
                (
                    "orderIdList".into(),
                    "[{\"orderId\":\"123\"},{\"clientOid\":\"order-2\"}]".into(),
                ),
                ("product_symbol".into(), "BTC-USDT-SPOT".into()),
            ],
        )
        .await
        .expect("cancel_isolated_margin_batch_orders");
    let request = next(&receiver, "cancel_isolated_margin_batch_orders");
    assert_route(
        &request,
        "cancel_isolated_margin_batch_orders",
        "POST",
        "/api/v2/margin/isolated/batch-cancel-order",
    );
    assert!(request.signed);
    assert_eq!(serde_json::from_str::<serde_json::Value>(&request.body).expect("body"), serde_json::from_str::<serde_json::Value>("{\"symbol\": \"BTCUSDT\", \"orderIdList\": [{\"orderId\": \"123\"}, {\"clientOid\": \"order-2\"}]}").expect("fixture"));
    client.private_request("batch_cancel_replace_spot_orders", vec![("orderList".into(), "[{\"product_symbol\":\"BTC-USDT-SPOT\",\"orderId\":\"123\",\"price\":\"100\",\"size\":\"1\"}]".into())]).await.expect("batch_cancel_replace_spot_orders");
    let request = next(&receiver, "batch_cancel_replace_spot_orders");
    assert_route(
        &request,
        "batch_cancel_replace_spot_orders",
        "POST",
        "/api/v2/spot/trade/batch-cancel-replace-order",
    );
    assert!(request.signed);
    assert_eq!(serde_json::from_str::<serde_json::Value>(&request.body).expect("body"), serde_json::from_str::<serde_json::Value>("{\"orderList\": [{\"symbol\": \"BTCUSDT\", \"orderId\": \"123\", \"price\": \"100\", \"size\": \"1\"}]}").expect("fixture"));
    client.private_request("modify_uta_batch_orders", vec![("orders".into(), "[{\"product_symbol\":\"BTC-USDT-SWAP\",\"category\":\"USDT-FUTURES\",\"orderId\":\"123\",\"qty\":\"2\",\"requestId\":123456789012345678}]".into())]).await.expect("modify_uta_batch_orders");
    let request = next(&receiver, "modify_uta_batch_orders");
    assert_route(
        &request,
        "modify_uta_batch_orders",
        "POST",
        "/api/v3/trade/batch-modify-order",
    );
    assert!(request.signed);
    assert_eq!(serde_json::from_str::<serde_json::Value>(&request.body).expect("body"), serde_json::from_str::<serde_json::Value>("[{\"symbol\": \"BTCUSDT\", \"category\": \"USDT-FUTURES\", \"orderId\": \"123\", \"qty\": \"2\", \"requestId\": 123456789012345678}]").expect("fixture"));
}

#[tokio::test]
async fn internal_transfer_routes_preserve_parameters_and_authentication() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    let cases: &[(&str, &str, &str, bool, &[(&str, &str)], &str)] = &[
        (
            "transfer_uta_account",
            "POST",
            "/api/v3/account/transfer",
            false,
            &[
                ("fromType", "spot"),
                ("toType", "uta"),
                ("amount", "1"),
                ("coin", "USDT"),
            ],
            "{\"fromType\":\"spot\",\"toType\":\"uta\",\"amount\":\"1\",\"coin\":\"USDT\"}",
        ),
        (
            "transfer_uta_sub_to_master",
            "POST",
            "/api/v3/account/sub-master-transfer",
            false,
            &[
                ("fromType", "spot"),
                ("toType", "uta"),
                ("amount", "1"),
                ("coin", "USDT"),
            ],
            "{\"fromType\":\"spot\",\"toType\":\"uta\",\"amount\":\"1\",\"coin\":\"USDT\"}",
        ),
        (
            "transfer_uta_sub_account",
            "POST",
            "/api/v3/account/sub-transfer",
            false,
            &[
                ("fromType", "spot"),
                ("toType", "uta"),
                ("amount", "1"),
                ("coin", "USDT"),
                ("fromUserId", "1"),
                ("toUserId", "2"),
                ("clientOid", "transfer-123"),
            ],
            "{\"fromType\":\"spot\",\"toType\":\"uta\",\"amount\":\"1\",\"coin\":\"USDT\",\"fromUserId\":\"1\",\"toUserId\":\"2\",\"clientOid\":\"transfer-123\"}",
        ),
        (
            "get_uta_sub_account_transfer_records",
            "GET",
            "/api/v3/account/sub-transfer-record",
            false,
            &[],
            "{}",
        ),
        (
            "get_uta_sub_accounts",
            "GET",
            "/api/v3/user/sub-list",
            false,
            &[],
            "{}",
        ),
        (
            "get_uta_sub_account_assets",
            "GET",
            "/api/v3/account/sub-unified-assets",
            false,
            &[],
            "{}",
        ),
    ];
    for (name, method, path, public, params, expected) in cases {
        let params = params
            .iter()
            .map(|(key, value)| ((*key).to_string(), (*value).to_string()))
            .collect();
        let response = if *public {
            client.public_request(name, params).await
        } else {
            client.private_request(name, params).await
        };
        response.unwrap_or_else(|error| panic!("{name}: {error}"));
        let request = next(&receiver, name);
        assert_route(&request, name, method, path);
        assert_eq!(request.signed, !public, "{name}");
        let actual = if *method == "GET" {
            let pairs: serde_json::Map<String, serde_json::Value> =
                url::form_urlencoded::parse(request.query.as_bytes())
                    .map(|(key, value)| {
                        (
                            key.into_owned(),
                            serde_json::Value::String(value.into_owned()),
                        )
                    })
                    .collect();
            serde_json::Value::Object(pairs)
        } else {
            serde_json::from_str(&request.body).expect("JSON body")
        };
        assert_eq!(
            actual,
            serde_json::from_str::<serde_json::Value>(expected).expect("fixture"),
            "{name}"
        );
    }
}

#[tokio::test]
async fn remaining_query_routes_preserve_parameters_and_authentication() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    let cases: &[(&str, &str, &str, bool, &[(&str, &str)], &str)] = &[
        (
            "get_uta_strategy_sub_orders",
            "GET",
            "/api/v3/trade/strategy-sub-orders",
            false,
            &[("orderId", "123")],
            "{\"orderId\":\"123\"}",
        ),
        (
            "get_uta_deposit_records",
            "GET",
            "/api/v3/account/deposit-records",
            false,
            &[("startTime", "1700000000000"), ("endTime", "1700000001000")],
            "{\"startTime\":\"1700000000000\",\"endTime\":\"1700000001000\"}",
        ),
        (
            "get_server_time",
            "GET",
            "/api/v2/public/time",
            true,
            &[],
            "{}",
        ),
        (
            "get_all_trade_rates",
            "GET",
            "/api/v2/common/all-trade-rate",
            false,
            &[("businessType", "mix")],
            "{\"businessType\":\"mix\"}",
        ),
    ];
    for (name, method, path, public, params, expected) in cases {
        let params = params
            .iter()
            .map(|(key, value)| ((*key).to_string(), (*value).to_string()))
            .collect();
        let response = if *public {
            client.public_request(name, params).await
        } else {
            client.private_request(name, params).await
        };
        response.unwrap_or_else(|error| panic!("{name}: {error}"));
        let request = next(&receiver, name);
        assert_route(&request, name, method, path);
        assert_eq!(request.signed, !public, "{name}");
        let actual = if *method == "GET" {
            let pairs: serde_json::Map<String, serde_json::Value> =
                url::form_urlencoded::parse(request.query.as_bytes())
                    .map(|(key, value)| {
                        (
                            key.into_owned(),
                            serde_json::Value::String(value.into_owned()),
                        )
                    })
                    .collect();
            serde_json::Value::Object(pairs)
        } else {
            serde_json::from_str(&request.body).expect("JSON body")
        };
        assert_eq!(
            actual,
            serde_json::from_str::<serde_json::Value>(expected).expect("fixture"),
            "{name}"
        );
    }
}

#[tokio::test]
async fn supplementary_routes_preserve_parameters_and_authentication() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    let cases: &[(&str, &str, &str, bool, &[(&str, &str)], &str)] = &[
        (
            "set_uta_fee_deduction",
            "POST",
            "/api/v3/account/switch-deduct",
            false,
            &[("deduct", "on")],
            "{\"deduct\":\"on\"}",
        ),
        (
            "get_uta_fee_deduction",
            "GET",
            "/api/v3/account/deduct-info",
            false,
            &[],
            "{}",
        ),
        (
            "upgrade_to_uta",
            "POST",
            "/api/v3/account/switch",
            false,
            &[("confirm", "true")],
            "{}",
        ),
        (
            "get_uta_upgrade_status",
            "GET",
            "/api/v3/account/switch-status",
            false,
            &[],
            "{}",
        ),
        (
            "get_futures_margin_mode_switch_quota",
            "GET",
            "/api/v2/mix/account/switch-union-usdt",
            false,
            &[],
            "{}",
        ),
        (
            "get_cross_margin_liquidation_orders",
            "GET",
            "/api/v2/margin/crossed/liquidation-order",
            false,
            &[],
            "{}",
        ),
        (
            "get_isolated_margin_liquidation_orders",
            "GET",
            "/api/v2/margin/isolated/liquidation-order",
            false,
            &[],
            "{}",
        ),
        (
            "get_classic_account_upgrade_status",
            "GET",
            "/api/v2/spot/account/upgrade-status",
            false,
            &[],
            "{}",
        ),
        (
            "upgrade_classic_account",
            "POST",
            "/api/v2/spot/account/upgrade",
            false,
            &[("confirm", "true")],
            "{}",
        ),
        (
            "get_spot_fee_deduction",
            "GET",
            "/api/v2/spot/account/deduct-info",
            false,
            &[],
            "{}",
        ),
        (
            "set_spot_fee_deduction",
            "POST",
            "/api/v2/spot/account/switch-deduct",
            false,
            &[("deduct", "on")],
            "{\"deduct\":\"on\"}",
        ),
        (
            "set_spot_deposit_account",
            "POST",
            "/api/v2/spot/wallet/modify-deposit-account",
            false,
            &[("accountType", "spot"), ("coin", "USDT")],
            "{\"accountType\":\"spot\",\"coin\":\"USDT\"}",
        ),
        (
            "get_deposit_address",
            "GET",
            "/api/v2/spot/wallet/deposit-address",
            false,
            &[("coin", "USDT")],
            "{\"coin\":\"USDT\"}",
        ),
        (
            "get_sub_account_deposit_address",
            "GET",
            "/api/v2/spot/wallet/subaccount-deposit-address",
            false,
            &[("subUid", "2"), ("coin", "USDT")],
            "{\"subUid\":\"2\",\"coin\":\"USDT\"}",
        ),
        (
            "get_sub_account_deposit_records",
            "GET",
            "/api/v2/spot/wallet/subaccount-deposit-records",
            false,
            &[("subUid", "2")],
            "{\"subUid\":\"2\"}",
        ),
        (
            "set_uta_deposit_account",
            "POST",
            "/api/v3/account/deposit-account",
            false,
            &[("coin", "USDT"), ("accountType", "unified")],
            "{\"coin\":\"USDT\",\"accountType\":\"unified\"}",
        ),
        (
            "create_uta_sub_account",
            "POST",
            "/api/v3/user/create-sub",
            false,
            &[("username", "trader")],
            "{\"username\":\"trader\"}",
        ),
        (
            "get_uta_cash_dividend_records",
            "GET",
            "/api/v3/market/cash-dividend-records",
            true,
            &[("product_symbol", "BTC-USDT-SWAP"), ("type", "pending")],
            "{\"symbol\":\"BTCUSDT\",\"type\":\"pending\"}",
        ),
        (
            "get_uta_risk_reserve",
            "GET",
            "/api/v3/market/risk-reserve",
            true,
            &[
                ("category", "USDT-FUTURES"),
                ("product_symbol", "BTC-USDT-SWAP"),
            ],
            "{\"category\":\"USDT-FUTURES\",\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "get_uta_all_risk_reserves",
            "GET",
            "/api/v3/market/risk-reserve-all",
            true,
            &[("category", "USDT-FUTURES")],
            "{\"category\":\"USDT-FUTURES\"}",
        ),
        (
            "get_uta_hourly_risk_reserve",
            "GET",
            "/api/v3/market/risk-reserve-hour",
            true,
            &[
                ("category", "USDT-FUTURES"),
                ("product_symbol", "BTC-USDT-SWAP"),
            ],
            "{\"category\":\"USDT-FUTURES\",\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "get_uta_split_records",
            "GET",
            "/api/v3/market/split-records",
            true,
            &[],
            "{}",
        ),
        (
            "get_uta_futures_long_short_ratio",
            "GET",
            "/api/v3/market/futures-account-long-short",
            true,
            &[("product_symbol", "BTC-USDT-SWAP")],
            "{\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "get_uta_spot_whale_flow",
            "GET",
            "/api/v3/market/spot-whale-flow",
            true,
            &[("product_symbol", "BTC-USDT-SWAP")],
            "{\"symbol\":\"BTCUSDT\"}",
        ),
    ];
    for (name, method, path, public, params, expected) in cases {
        let params = params
            .iter()
            .map(|(key, value)| ((*key).to_string(), (*value).to_string()))
            .collect();
        let response = if *public {
            client.public_request(name, params).await
        } else {
            client.private_request(name, params).await
        };
        response.unwrap_or_else(|error| panic!("{name}: {error}"));
        let request = next(&receiver, name);
        assert_route(&request, name, method, path);
        assert_eq!(request.signed, !public, "{name}");
        let actual = if *method == "GET" {
            let pairs: serde_json::Map<String, serde_json::Value> =
                url::form_urlencoded::parse(request.query.as_bytes())
                    .map(|(key, value)| {
                        (
                            key.into_owned(),
                            serde_json::Value::String(value.into_owned()),
                        )
                    })
                    .collect();
            serde_json::Value::Object(pairs)
        } else {
            serde_json::from_str(&request.body).expect("JSON body")
        };
        assert_eq!(
            actual,
            serde_json::from_str::<serde_json::Value>(expected).expect("fixture"),
            "{name}"
        );
    }
}

#[tokio::test]
async fn remaining_routes_preserve_parameters_and_authentication() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    let cases: &[(&str, &str, &str, bool, &[(&str, &str)], &str)] = &[
        (
            "get_uta_deposit_address",
            "GET",
            "/api/v3/account/deposit-address",
            false,
            &[("coin", "USDT")],
            "{\"coin\":\"USDT\"}",
        ),
        (
            "get_uta_sub_deposit_address",
            "GET",
            "/api/v3/account/sub-deposit-address",
            false,
            &[("subUid", "2"), ("coin", "USDT")],
            "{\"subUid\":\"2\",\"coin\":\"USDT\"}",
        ),
        (
            "get_uta_sub_deposit_records",
            "GET",
            "/api/v3/account/sub-deposit-records",
            false,
            &[
                ("subUid", "2"),
                ("startTime", "1700000000000"),
                ("endTime", "1700000001000"),
            ],
            "{\"subUid\":\"2\",\"startTime\":\"1700000000000\",\"endTime\":\"1700000001000\"}",
        ),
        (
            "get_uta_rate_limit_quota",
            "GET",
            "/api/v3/user/rate-limit-quota",
            false,
            &[("category", "spot")],
            "{\"category\":\"spot\"}",
        ),
        (
            "uta_set_rate_limit_quota",
            "POST",
            "/api/v3/user/set-rate-limit-quota",
            false,
            &[("category", "spot"), ("uids", "[\"2\"]"), ("quota", "5")],
            "{\"category\":\"spot\",\"uids\":[\"2\"],\"quota\":\"5\"}",
        ),
        (
            "get_uta_small_assets_history",
            "GET",
            "/api/v3/convert/small-assets-history",
            false,
            &[],
            "{}",
        ),
        (
            "get_uta_small_assets",
            "GET",
            "/api/v3/convert/small-assets",
            false,
            &[],
            "{}",
        ),
        (
            "uta_small_assets_trade",
            "POST",
            "/api/v3/convert/small-assets-trade",
            false,
            &[("fromCoinList", "[\"ETH\"]")],
            "{\"fromCoinList\":[\"ETH\"]}",
        ),
        (
            "uta_delete_sub",
            "POST",
            "/api/v3/user/delete-sub",
            false,
            &[("confirm", "true"), ("subUid", "2")],
            "{\"subUid\":\"2\"}",
        ),
        (
            "uta_freeze_sub",
            "POST",
            "/api/v3/user/freeze-sub",
            false,
            &[("subUid", "2"), ("operation", "freeze")],
            "{\"subUid\":\"2\",\"operation\":\"freeze\"}",
        ),
        (
            "uta_create_sub_api",
            "POST",
            "/api/v3/user/create-sub-api",
            false,
            &[
                ("subUid", "2"),
                ("note", "trading"),
                ("type", "read_only"),
                ("passphrase", "Trading123"),
                ("permissions", "[\"uta_trade\"]"),
                ("ips", "[\"127.0.0.1\"]"),
            ],
            "{\"subUid\":\"2\",\"note\":\"trading\",\"type\":\"read_only\",\"passphrase\":\"Trading123\",\"permissions\":[\"uta_trade\"],\"ips\":[\"127.0.0.1\"]}",
        ),
        (
            "uta_update_sub_api",
            "POST",
            "/api/v3/user/update-sub-api",
            false,
            &[("apiKey", "api-key"), ("passphrase", "Trading123")],
            "{\"apiKey\":\"api-key\",\"passphrase\":\"Trading123\"}",
        ),
        (
            "uta_delete_sub_api",
            "POST",
            "/api/v3/user/delete-sub-api",
            false,
            &[("apiKey", "api-key")],
            "{\"apiKey\":\"api-key\"}",
        ),
        (
            "get_uta_sub_api_list",
            "GET",
            "/api/v3/user/sub-api-list",
            false,
            &[("subUid", "2")],
            "{\"subUid\":\"2\"}",
        ),
        (
            "classic_create_virtual_subaccount",
            "POST",
            "/api/v2/user/create-virtual-subaccount",
            false,
            &[("subAccountList", "[\"traderab\"]")],
            "{\"subAccountList\":[\"traderab\"]}",
        ),
        (
            "classic_create_virtual_subaccount_apikey",
            "POST",
            "/api/v2/user/create-virtual-subaccount-apikey",
            false,
            &[
                ("subAccountUid", "2"),
                ("passphrase", "Trading123"),
                ("label", "trading"),
                ("permList", "[\"read\"]"),
            ],
            "{\"subAccountUid\":\"2\",\"passphrase\":\"Trading123\",\"label\":\"trading\",\"permList\":[\"read\"]}",
        ),
        (
            "classic_modify_virtual_subaccount",
            "POST",
            "/api/v2/user/modify-virtual-subaccount",
            false,
            &[
                ("subAccountUid", "2"),
                ("permList", "[\"read\"]"),
                ("status", "normal"),
            ],
            "{\"subAccountUid\":\"2\",\"permList\":[\"read\"],\"status\":\"normal\"}",
        ),
        (
            "classic_modify_virtual_subaccount_apikey",
            "POST",
            "/api/v2/user/modify-virtual-subaccount-apikey",
            false,
            &[
                ("subAccountUid", "2"),
                ("passphrase", "Trading123"),
                ("label", "trading"),
                ("subAccountApiKey", "api-key"),
            ],
            "{\"subAccountUid\":\"2\",\"passphrase\":\"Trading123\",\"label\":\"trading\",\"subAccountApiKey\":\"api-key\"}",
        ),
        (
            "get_classic_virtual_subaccount_list",
            "GET",
            "/api/v2/user/virtual-subaccount-list",
            false,
            &[],
            "{}",
        ),
        (
            "get_classic_virtual_subaccount_apikey_list",
            "GET",
            "/api/v2/user/virtual-subaccount-apikey-list",
            false,
            &[("subAccountUid", "2")],
            "{\"subAccountUid\":\"2\"}",
        ),
        (
            "get_classic_interest_rate_record",
            "GET",
            "/api/v2/margin/interest-rate-record",
            true,
            &[("coin", "USDT")],
            "{\"coin\":\"USDT\"}",
        ),
        (
            "get_classic_margin_currencies",
            "GET",
            "/api/v2/margin/currencies",
            true,
            &[],
            "{}",
        ),
        (
            "get_classic_convert_currencies",
            "GET",
            "/api/v2/convert/currencies",
            true,
            &[],
            "{}",
        ),
        (
            "get_classic_quoted_price",
            "GET",
            "/api/v2/convert/quoted-price",
            false,
            &[
                ("fromCoin", "BTC"),
                ("toCoin", "USDT"),
                ("fromCoinSize", "0.1"),
            ],
            "{\"fromCoin\":\"BTC\",\"toCoin\":\"USDT\",\"fromCoinSize\":\"0.1\"}",
        ),
        (
            "classic_trade",
            "POST",
            "/api/v2/convert/trade",
            false,
            &[
                ("fromCoin", "BTC"),
                ("fromCoinSize", "0.1"),
                ("cnvtPrice", "100000"),
                ("toCoin", "USDT"),
                ("toCoinSize", "10000"),
                ("traceId", "quote-1"),
            ],
            "{\"fromCoin\":\"BTC\",\"fromCoinSize\":\"0.1\",\"cnvtPrice\":\"100000\",\"toCoin\":\"USDT\",\"toCoinSize\":\"10000\",\"traceId\":\"quote-1\"}",
        ),
        (
            "get_classic_convert_record",
            "GET",
            "/api/v2/convert/convert-record",
            false,
            &[("startTime", "1700000000000"), ("endTime", "1700000001000")],
            "{\"startTime\":\"1700000000000\",\"endTime\":\"1700000001000\"}",
        ),
        (
            "get_classic_merge_depth",
            "GET",
            "/api/v2/spot/market/merge-depth",
            true,
            &[("product_symbol", "BTC-USDT-SWAP")],
            "{\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "get_classic_auction",
            "GET",
            "/api/v2/spot/market/auction",
            true,
            &[("product_symbol", "BTC-USDT-SWAP")],
            "{\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "get_classic_vip_fee_rate",
            "GET",
            "/api/v2/spot/market/vip-fee-rate",
            true,
            &[],
            "{}",
        ),
        (
            "get_uta_proof_of_reserves",
            "GET",
            "/api/v3/market/proof-of-reserves",
            true,
            &[],
            "{}",
        ),
        (
            "get_uta_score_weights",
            "GET",
            "/api/v3/market/score-weights",
            true,
            &[],
            "{}",
        ),
        (
            "get_uta_fee_group",
            "GET",
            "/api/v3/market/fee-group",
            true,
            &[("category", "USDT-FUTURES")],
            "{\"category\":\"USDT-FUTURES\"}",
        ),
        (
            "get_uta_spot_fund_flow",
            "GET",
            "/api/v3/market/spot-fund-flow",
            true,
            &[("product_symbol", "BTC-USDT-SWAP")],
            "{\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "get_uta_spot_net_flow",
            "GET",
            "/api/v3/market/spot-net-flow",
            true,
            &[("product_symbol", "BTC-USDT-SWAP")],
            "{\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "get_uta_margin_long_short",
            "GET",
            "/api/v3/market/margin-long-short",
            true,
            &[("product_symbol", "BTC-USDT-SWAP")],
            "{\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "get_uta_margin_loan_growth",
            "GET",
            "/api/v3/market/margin-loan-growth",
            true,
            &[("product_symbol", "BTC-USDT-SWAP")],
            "{\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "get_uta_margin_isolated_borrow",
            "GET",
            "/api/v3/market/margin-isolated-borrow",
            true,
            &[("product_symbol", "BTC-USDT-SWAP")],
            "{\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "get_uta_futures_active_buy_sell",
            "GET",
            "/api/v3/market/futures-active-buy-sell",
            true,
            &[("product_symbol", "BTC-USDT-SWAP")],
            "{\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "get_uta_futures_long_short",
            "GET",
            "/api/v3/market/futures-long-short",
            true,
            &[("product_symbol", "BTC-USDT-SWAP")],
            "{\"symbol\":\"BTCUSDT\"}",
        ),
        (
            "get_uta_futures_position_long_short",
            "GET",
            "/api/v3/market/futures-position-long-short",
            true,
            &[("product_symbol", "BTC-USDT-SWAP")],
            "{\"symbol\":\"BTCUSDT\"}",
        ),
    ];
    for (name, method, path, public, params, expected) in cases {
        let params = params
            .iter()
            .map(|(key, value)| ((*key).to_string(), (*value).to_string()))
            .collect();
        let response = if *public {
            client.public_request(name, params).await
        } else {
            client.private_request(name, params).await
        };
        response.unwrap_or_else(|error| panic!("{name}: {error}"));
        let request = next(&receiver, name);
        assert_route(&request, name, method, path);
        assert_eq!(request.signed, !public, "{name}");
        let actual = if *method == "GET" {
            let pairs: serde_json::Map<String, serde_json::Value> =
                url::form_urlencoded::parse(request.query.as_bytes())
                    .map(|(key, value)| {
                        (
                            key.into_owned(),
                            serde_json::Value::String(value.into_owned()),
                        )
                    })
                    .collect();
            serde_json::Value::Object(pairs)
        } else {
            serde_json::from_str(&request.body).expect("JSON body")
        };
        assert_eq!(
            actual,
            serde_json::from_str::<serde_json::Value>(expected).expect("fixture"),
            "{name}"
        );
    }
}

#[tokio::test]
async fn nested_sub_account_and_position_requests() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    let cases: &[(&str, &str, &[(&str, &str)], &str)] = &[
        (
            "batch_create_classic_sub_accounts",
            "/api/v2/user/batch-create-subaccount-and-apikey",
            &[(
                "accounts",
                "[{\"subAccountName\":\"traderab\",\"passphrase\":\"Trader123\",\"label\":\"trading\",\"permList\":[\"read\"],\"ipList\":[\"127.0.0.1\"]}]",
            )],
            "[{\"subAccountName\":\"traderab\",\"passphrase\":\"Trader123\",\"label\":\"trading\",\"permList\":[\"read\"],\"ipList\":[\"127.0.0.1\"]}]",
        ),
        (
            "move_uta_positions",
            "/api/v3/account/move-positions",
            &[
                ("confirm", "true"),
                ("fromUid", "1"),
                ("toUid", "2"),
                ("category", "USDT-FUTURES"),
                (
                    "positionList",
                    "[{\"symbol\":\"BTCUSDT\",\"side\":\"sell\",\"qty\":\"0.01\"}]",
                ),
            ],
            "{\"fromUid\":\"1\",\"toUid\":\"2\",\"category\":\"USDT-FUTURES\",\"positionList\":[{\"symbol\":\"BTCUSDT\",\"side\":\"sell\",\"qty\":\"0.01\"}]}",
        ),
    ];
    for (name, path, params, body) in cases {
        client
            .private_request(
                name,
                params
                    .iter()
                    .map(|(k, v)| ((*k).into(), (*v).into()))
                    .collect(),
            )
            .await
            .expect(name);
        let request = next(&receiver, name);
        assert_route(&request, name, "POST", path);
        assert_eq!(
            serde_json::from_str::<serde_json::Value>(&request.body).unwrap(),
            serde_json::from_str::<serde_json::Value>(body).unwrap()
        );
    }
}
