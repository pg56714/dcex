//! Route coverage: every Bitget dispatch name must reach the documented
//! METHOD + path from the official API docs, fully offline.

use std::io::{BufRead, BufReader, Read, Write};
use std::net::TcpListener;
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

use super::BitgetClient;

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
                .set_read_timeout(Some(Duration::from_secs(5)))
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
        Duration::from_secs(5),
        url,
    )
    .expect("client")
}

fn next(receiver: &mpsc::Receiver<Recorded>, name: &str) -> Recorded {
    receiver
        .recv_timeout(Duration::from_secs(5))
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
    let client = BitgetClient::public(Duration::from_secs(1)).expect("client");
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
