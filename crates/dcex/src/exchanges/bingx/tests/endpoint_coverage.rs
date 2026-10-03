//! Route coverage: every BingX dispatch name must reach the documented
//! METHOD + path from the official API docs, fully offline.

use std::io::{BufRead, BufReader, Read, Write};
use std::net::TcpListener;
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

use crate::http::block_on;

use super::helpers::BingxClient;

struct Recorded {
    method: String,
    path: String,
    query: Vec<(String, String)>,
    api_key_header: bool,
    body: serde_json::Value,
}

impl Recorded {
    fn get(&self, key: &str) -> Option<&str> {
        self.query
            .iter()
            .find(|(candidate, _)| candidate == key)
            .map(|(_, value)| value.as_str())
    }
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
            let mut api_key_header = false;
            loop {
                let mut line = String::new();
                if reader.read_line(&mut line).is_err() || line == "\r\n" || line.is_empty() {
                    break;
                }
                let lower = line.to_ascii_lowercase();
                if let Some(value) = lower.strip_prefix("content-length:") {
                    content_length = value.trim().parse().unwrap_or(0);
                }
                if lower.starts_with("x-bx-apikey:") {
                    api_key_header = true;
                }
            }
            let mut body = vec![0u8; content_length];
            if content_length > 0 {
                reader.read_exact(&mut body).expect("body");
            }
            let payload = br#"{"code":0,"msg":"","data":{"listenKey":"k"}}"#;
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
            let query = url::form_urlencoded::parse(query.as_bytes())
                .into_owned()
                .collect();
            let recorded = Recorded {
                method,
                path,
                query,
                api_key_header,
                body: serde_json::from_slice(&body).unwrap_or(serde_json::Value::Null),
            };
            if sender.send(recorded).is_err() {
                break;
            }
        }
    });
    (url, receiver)
}

type Case = (
    &'static str,
    &'static [(&'static str, &'static str)],
    &'static str,
    &'static str,
);

const SWAP: (&str, &str) = ("product_symbol", "BTC-USDT");
const SPOT: (&str, &str) = ("product_symbol", "BTC-USDT-SPOT");

/// (dispatch name, params, HTTP method, documented path)
const PUBLIC_ROUTES: &[Case] = &[
    (
        "get_swap_instrument_info",
        &[SWAP],
        "GET",
        "/openApi/swap/v2/quote/contracts",
    ),
    (
        "get_spot_instrument_info",
        &[SPOT],
        "GET",
        "/openApi/spot/v1/common/symbols",
    ),
    (
        "get_orderbook",
        &[SWAP, ("limit", "5")],
        "GET",
        "/openApi/swap/v2/quote/depth",
    ),
    (
        "get_spot_orderbook",
        &[SPOT, ("limit", "5")],
        "GET",
        "/openApi/spot/v1/market/depth",
    ),
    (
        "get_spot_orderbook_v2",
        &[SPOT, ("depth", "20")],
        "GET",
        "/openApi/spot/v2/market/depth",
    ),
    (
        "get_public_trades",
        &[SWAP, ("limit", "10")],
        "GET",
        "/openApi/swap/v2/quote/trades",
    ),
    (
        "get_spot_public_trades",
        &[SPOT, ("limit", "5")],
        "GET",
        "/openApi/spot/v1/market/trades",
    ),
    (
        "get_kline",
        &[SWAP, ("interval", "1h")],
        "GET",
        "/openApi/swap/v3/quote/klines",
    ),
    (
        "get_spot_kline",
        &[SPOT, ("interval", "1m")],
        "GET",
        "/openApi/spot/v2/market/kline",
    ),
    (
        "get_spot_kline_v2",
        &[SPOT, ("interval", "1m")],
        "GET",
        "/openApi/spot/v2/market/kline",
    ),
    (
        "get_open_interest",
        &[SWAP],
        "GET",
        "/openApi/swap/v2/quote/openInterest",
    ),
    (
        "get_mark_price_kline",
        &[SWAP, ("interval", "1h")],
        "GET",
        "/openApi/swap/v1/market/markPriceKlines",
    ),
    (
        "get_ticker",
        &[SWAP],
        "GET",
        "/openApi/swap/v2/quote/ticker",
    ),
    (
        "get_swap_premium_index",
        &[SWAP],
        "GET",
        "/openApi/swap/v2/quote/premiumIndex",
    ),
    (
        "get_swap_funding_rate",
        &[SWAP, ("limit", "2")],
        "GET",
        "/openApi/swap/v2/quote/fundingRate",
    ),
    (
        "get_swap_book_ticker",
        &[SWAP],
        "GET",
        "/openApi/swap/v2/quote/bookTicker",
    ),
    (
        "get_swap_trading_rules",
        &[SWAP],
        "GET",
        "/openApi/swap/v1/tradingRules",
    ),
    (
        "get_spot_ticker",
        &[SPOT],
        "GET",
        "/openApi/spot/v1/ticker/24hr",
    ),
    (
        "get_spot_book_ticker",
        &[SPOT],
        "GET",
        "/openApi/spot/v1/ticker/bookTicker",
    ),
    (
        "get_spot_price_ticker",
        &[SPOT],
        "GET",
        "/openApi/spot/v2/ticker/price",
    ),
];

const SPOT_LIMIT: &[(&str, &str)] = &[SPOT, ("side", "BUY"), ("quantity", "1"), ("price", "1")];
const SPOT_SIDED_LIMIT: &[(&str, &str)] = &[SPOT, ("quantity", "1"), ("price", "1")];
const SWAP_LIMIT: &[(&str, &str)] = &[SWAP, ("side", "BUY"), ("quantity", "1"), ("price", "1")];
const SWAP_SIDED_LIMIT: &[(&str, &str)] = &[
    SWAP,
    ("quantity", "1"),
    ("price", "1"),
    ("positionSide", "SHORT"),
];

/// (dispatch name, params, HTTP method, documented path)
const PRIVATE_ROUTES: &[Case] = &[
    (
        "get_withdrawal_history",
        &[],
        "GET",
        "/openApi/api/v3/capital/withdraw/history",
    ),
    (
        "get_internal_transfer_records",
        &[("coin", "USDT")],
        "GET",
        "/openApi/wallets/v1/capital/innerTransfer/records",
    ),
    (
        "get_sub_account_internal_transfer_records",
        &[("coin", "USDT")],
        "GET",
        "/openApi/wallets/v1/capital/subAccount/innerTransfer/records",
    ),
    // Account / wallet / sub-accounts.
    (
        "get_account_balance",
        &[],
        "GET",
        "/openApi/swap/v3/user/balance",
    ),
    (
        "get_swap_account_balance",
        &[("recvWindow", "5000")],
        "GET",
        "/openApi/swap/v3/user/balance",
    ),
    (
        "get_swap_commission_rate",
        &[],
        "GET",
        "/openApi/swap/v2/user/commissionRate",
    ),
    (
        "get_spot_account_balance",
        &[],
        "GET",
        "/openApi/spot/v1/account/balance",
    ),
    (
        "get_fund_account_balance",
        &[("asset", "USDT")],
        "GET",
        "/openApi/fund/v1/account/balance",
    ),
    (
        "get_all_account_balance",
        &[("accountType", "USDTMPerp")],
        "GET",
        "/openApi/account/v1/allAccountBalance",
    ),
    ("get_account_uid", &[], "GET", "/openApi/account/v1/uid"),
    (
        "get_api_key_info",
        &[("uid", "1")],
        "GET",
        "/openApi/account/v1/apiKey/query",
    ),
    (
        "get_transferable_coins",
        &[("fromAccount", "fund"), ("toAccount", "spot")],
        "GET",
        "/openApi/api/asset/v1/transfer/supportCoins",
    ),
    (
        "asset_transfer",
        &[
            ("fromAccount", "fund"),
            ("toAccount", "spot"),
            ("asset", "USDT"),
            ("amount", "1"),
        ],
        "POST",
        "/openApi/api/asset/v1/transfer",
    ),
    (
        "get_asset_transfer_records",
        &[("fromAccount", "fund"), ("toAccount", "spot")],
        "GET",
        "/openApi/api/v3/asset/transferRecord",
    ),
    (
        "get_subaccounts",
        &[("page", "1"), ("limit", "10")],
        "GET",
        "/openApi/subAccount/v1/list",
    ),
    (
        "get_subaccount_assets",
        &[("subUid", "1")],
        "GET",
        "/openApi/subAccount/v1/assets",
    ),
    (
        "get_subaccount_all_account_balance",
        &[("pageIndex", "1"), ("pageSize", "10")],
        "GET",
        "/openApi/subAccount/v1/allAccountBalance",
    ),
    (
        "get_subaccount_transfer_history",
        &[("uid", "1")],
        "GET",
        "/openApi/account/transfer/v1/subAccount/asset/transferHistory",
    ),
    (
        "get_subaccount_transferable_amounts",
        &[
            ("fromUid", "1"),
            ("fromAccountType", "1"),
            ("toUid", "2"),
            ("toAccountType", "1"),
        ],
        "POST",
        "/openApi/account/transfer/v1/subAccount/transferAsset/supportCoins",
    ),
    (
        "transfer_subaccount_assets",
        &[
            ("assetName", "USDT"),
            ("transferAmount", "1"),
            ("fromUid", "1"),
            ("fromType", "1"),
            ("fromAccountType", "1"),
            ("toUid", "2"),
            ("toType", "1"),
            ("toAccountType", "1"),
            ("remark", "r"),
        ],
        "POST",
        "/openApi/account/transfer/v1/subAccount/transferAsset",
    ),
    (
        "get_open_positions",
        &[SWAP],
        "GET",
        "/openApi/swap/v2/user/positions",
    ),
    (
        "get_fund_flow",
        &[SWAP],
        "GET",
        "/openApi/swap/v2/user/income",
    ),
    (
        "keep_alive_listen_key",
        &[("listen_key", "k")],
        "PUT",
        "/openApi/user/auth/userDataStream",
    ),
    (
        "close_listen_key",
        &[("listen_key", "k")],
        "DELETE",
        "/openApi/user/auth/userDataStream",
    ),
    // Spot trading.
    (
        "place_spot_order",
        &[
            SPOT,
            ("side", "BUY"),
            ("type_", "LIMIT"),
            ("quantity", "1"),
            ("price", "1"),
        ],
        "POST",
        "/openApi/spot/v1/trade/order",
    ),
    (
        "place_spot_market_buy_order",
        &[SPOT, ("quoteOrderQty", "10")],
        "POST",
        "/openApi/spot/v1/trade/order",
    ),
    (
        "place_spot_market_sell_order",
        &[SPOT, ("quantity", "1")],
        "POST",
        "/openApi/spot/v1/trade/order",
    ),
    (
        "place_spot_limit_order",
        SPOT_LIMIT,
        "POST",
        "/openApi/spot/v1/trade/order",
    ),
    (
        "place_spot_limit_buy_order",
        SPOT_SIDED_LIMIT,
        "POST",
        "/openApi/spot/v1/trade/order",
    ),
    (
        "place_spot_limit_sell_order",
        SPOT_SIDED_LIMIT,
        "POST",
        "/openApi/spot/v1/trade/order",
    ),
    (
        "place_spot_post_only_order",
        SPOT_LIMIT,
        "POST",
        "/openApi/spot/v1/trade/order",
    ),
    (
        "place_spot_post_only_buy_order",
        SPOT_SIDED_LIMIT,
        "POST",
        "/openApi/spot/v1/trade/order",
    ),
    (
        "place_spot_post_only_sell_order",
        SPOT_SIDED_LIMIT,
        "POST",
        "/openApi/spot/v1/trade/order",
    ),
    (
        "place_spot_batch_order",
        &[(
            "data",
            r#"[{"symbol":"BTC-USDT","side":"BUY","type":"LIMIT","quantity":"1","price":"1"}]"#,
        )],
        "POST",
        "/openApi/spot/v1/trade/batchOrders",
    ),
    (
        "replace_spot_order",
        &[
            SPOT,
            ("cancelOrderId", "123"),
            ("cancelReplaceMode", "STOP_ON_FAILURE"),
            ("side", "BUY"),
            ("type_", "LIMIT"),
            ("quantity", "0.1"),
            ("price", "50000"),
        ],
        "POST",
        "/openApi/spot/v1/trade/order/cancelReplace",
    ),
    (
        "cancel_spot_order",
        &[SPOT, ("orderId", "1")],
        "POST",
        "/openApi/spot/v1/trade/cancel",
    ),
    (
        "cancel_spot_batch_orders",
        &[SPOT, ("orderIds", "1,2")],
        "POST",
        "/openApi/spot/v1/trade/cancelOrders",
    ),
    (
        "cancel_spot_open_orders",
        &[SPOT],
        "POST",
        "/openApi/spot/v1/trade/cancelOpenOrders",
    ),
    (
        "set_spot_cancel_all_after",
        &[("type_", "CLOSE")],
        "POST",
        "/openApi/spot/v1/trade/cancelAllAfter",
    ),
    (
        "get_spot_order",
        &[SPOT, ("orderId", "1")],
        "GET",
        "/openApi/spot/v1/trade/query",
    ),
    (
        "get_spot_open_orders",
        &[SPOT],
        "GET",
        "/openApi/spot/v1/trade/openOrders",
    ),
    (
        "get_spot_order_history",
        &[SPOT],
        "GET",
        "/openApi/spot/v1/trade/historyOrders",
    ),
    (
        "get_spot_my_trades",
        &[SPOT],
        "GET",
        "/openApi/spot/v1/trade/myTrades",
    ),
    (
        "get_spot_commission_rate",
        &[SPOT],
        "GET",
        "/openApi/spot/v1/user/commissionRate",
    ),
    // USDT-M perpetual trading.
    (
        "place_swap_order",
        &[
            SWAP,
            ("side", "BUY"),
            ("type_", "LIMIT"),
            ("positionSide", "LONG"),
            ("quantity", "1"),
            ("price", "1"),
        ],
        "POST",
        "/openApi/swap/v2/trade/order",
    ),
    (
        "test_swap_order",
        &[
            SWAP,
            ("side", "SELL"),
            ("type_", "MARKET"),
            ("quantity", "1"),
        ],
        "POST",
        "/openApi/swap/v2/trade/order/test",
    ),
    (
        "place_swap_market_order",
        &[SWAP, ("side", "BUY"), ("quantity", "1")],
        "POST",
        "/openApi/swap/v2/trade/order",
    ),
    (
        "place_swap_market_buy_order",
        &[SWAP, ("quantity", "1"), ("positionSide", "SHORT")],
        "POST",
        "/openApi/swap/v2/trade/order",
    ),
    (
        "place_swap_market_sell_order",
        &[SWAP, ("quantity", "1"), ("positionSide", "SHORT")],
        "POST",
        "/openApi/swap/v2/trade/order",
    ),
    (
        "place_swap_limit_order",
        SWAP_LIMIT,
        "POST",
        "/openApi/swap/v2/trade/order",
    ),
    (
        "place_swap_limit_buy_order",
        SWAP_SIDED_LIMIT,
        "POST",
        "/openApi/swap/v2/trade/order",
    ),
    (
        "place_swap_limit_sell_order",
        SWAP_SIDED_LIMIT,
        "POST",
        "/openApi/swap/v2/trade/order",
    ),
    (
        "place_swap_post_only_order",
        SWAP_LIMIT,
        "POST",
        "/openApi/swap/v2/trade/order",
    ),
    (
        "place_swap_post_only_buy_order",
        SWAP_SIDED_LIMIT,
        "POST",
        "/openApi/swap/v2/trade/order",
    ),
    (
        "place_swap_post_only_sell_order",
        SWAP_SIDED_LIMIT,
        "POST",
        "/openApi/swap/v2/trade/order",
    ),
    (
        "place_swap_batch_order",
        &[(
            "batchOrders",
            r#"[{"symbol":"BTC-USDT","side":"BUY","type":"LIMIT","positionSide":"LONG","quantity":"1","price":"1"}]"#,
        )],
        "POST",
        "/openApi/swap/v2/trade/batchOrders",
    ),
    (
        "cancel_swap_order",
        &[SWAP, ("orderId", "1")],
        "DELETE",
        "/openApi/swap/v2/trade/order",
    ),
    (
        "cancel_swap_batch_order",
        &[SWAP, ("orderIdList", "[1,2]")],
        "DELETE",
        "/openApi/swap/v2/trade/batchOrders",
    ),
    (
        "cancel_swap_all_orders",
        &[SWAP],
        "DELETE",
        "/openApi/swap/v2/trade/allOpenOrders",
    ),
    (
        "replace_swap_order",
        &[
            SWAP,
            ("cancelOrderId", "1"),
            ("cancelReplaceMode", "STOP_ON_FAILURE"),
            ("type_", "LIMIT"),
            ("side", "BUY"),
            ("positionSide", "LONG"),
            ("quantity", "1"),
            ("price", "1"),
        ],
        "POST",
        "/openApi/swap/v1/trade/cancelReplace",
    ),
    (
        "close_swap_position",
        &[("positionId", "1")],
        "POST",
        "/openApi/swap/v1/trade/closePosition",
    ),
    (
        "close_swap_all_positions",
        &[SWAP],
        "POST",
        "/openApi/swap/v2/trade/closeAllPositions",
    ),
    (
        "get_order_detail",
        &[SWAP, ("orderId", "1")],
        "GET",
        "/openApi/swap/v2/trade/order",
    ),
    (
        "get_open_orders",
        &[SWAP],
        "GET",
        "/openApi/swap/v2/trade/openOrders",
    ),
    (
        "get_order_history",
        &[SWAP, ("limit", "10")],
        "GET",
        "/openApi/swap/v2/trade/allOrders",
    ),
    (
        "change_margin_type",
        &[SWAP, ("marginType", "CROSSED")],
        "POST",
        "/openApi/swap/v2/trade/marginType",
    ),
    (
        "get_margin_type",
        &[SWAP],
        "GET",
        "/openApi/swap/v2/trade/marginType",
    ),
    (
        "set_leverage",
        &[SWAP, ("side", "LONG"), ("leverage", "5")],
        "POST",
        "/openApi/swap/v2/trade/leverage",
    ),
    (
        "get_leverage",
        &[SWAP],
        "GET",
        "/openApi/swap/v2/trade/leverage",
    ),
    (
        "set_position_mode",
        &[("dualSidePosition", "true")],
        "POST",
        "/openApi/swap/v1/positionSide/dual",
    ),
    (
        "get_position_mode",
        &[],
        "GET",
        "/openApi/swap/v1/positionSide/dual",
    ),
];

fn owned(params: &[(&str, &str)]) -> Vec<(String, String)> {
    params
        .iter()
        .map(|(key, value)| (key.to_string(), value.to_string()))
        .collect()
}

fn signed_client(url: String) -> BingxClient {
    BingxClient::with_base_url(
        Some("api-key".into()),
        Some("secret".into()),
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

fn private_call(client: &BingxClient, name: &str, params: &[(&str, &str)]) {
    let client = client.clone();
    let method = name.to_string();
    let params = owned(params);
    block_on(async move { client.private_request(&method, params).await })
        .unwrap_or_else(|error| panic!("{name}: {error}"));
}

#[test]
fn public_dispatch_names_reach_documented_routes() {
    let (url, receiver) = recording_server();
    let client =
        BingxClient::with_base_url(None, None, Duration::from_secs(10), url).expect("client");
    for (name, params, method, path) in PUBLIC_ROUTES {
        let client = client.clone();
        let method_name = name.to_string();
        let params_owned = owned(params);
        block_on(async move { client.public_request(&method_name, params_owned).await })
            .unwrap_or_else(|error| panic!("{name}: {error}"));
        let recorded = next(&receiver, name);
        assert_eq!(recorded.method, *method, "{name}: HTTP method");
        assert_eq!(recorded.path, *path, "{name}: request path");
        assert!(
            recorded.get("signature").is_none(),
            "{name}: must be unsigned"
        );
        let expected_symbol = if *name == "get_spot_orderbook_v2" {
            "BTC_USDT"
        } else {
            "BTC-USDT"
        };
        assert_eq!(
            recorded.get("symbol"),
            Some(expected_symbol),
            "{name}: symbol"
        );
    }
}

#[test]
fn public_routes_send_timestamp_where_documented_required() {
    // The official request tables list no timestamp only for these spot routes.
    const WITHOUT_TIMESTAMP: &[&str] = &[
        "/openApi/spot/v2/market/depth",
        "/openApi/spot/v2/ticker/price",
        "/openApi/spot/v1/ticker/bookTicker",
    ];
    let (url, receiver) = recording_server();
    let client =
        BingxClient::with_base_url(None, None, Duration::from_secs(10), url).expect("client");
    for (name, params, _, path) in PUBLIC_ROUTES {
        let client = client.clone();
        let method_name = name.to_string();
        let params = owned(params);
        block_on(async move { client.public_request(&method_name, params).await })
            .unwrap_or_else(|error| panic!("{name}: {error}"));
        let recorded = next(&receiver, name);
        if WITHOUT_TIMESTAMP.contains(path) {
            assert!(recorded.get("timestamp").is_none(), "{name}: no timestamp");
        } else {
            let timestamp = recorded.get("timestamp").expect("timestamp");
            assert!(
                timestamp.parse::<u64>().is_ok(),
                "{name}: numeric timestamp"
            );
        }
        assert!(recorded.get("signature").is_none(), "{name}: unsigned");
    }
}

#[test]
fn spot_orderbook_v2_requires_depth() {
    let client = BingxClient::with_base_url(
        None,
        None,
        Duration::from_secs(10),
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");
    let error = block_on(async move {
        client
            .public_request(
                "get_spot_orderbook_v2",
                owned(&[("product_symbol", "BTC-USDT-SPOT")]),
            )
            .await
    })
    .expect_err("depth is required");
    assert!(error.to_string().contains("depth"), "{error}");
}

#[test]
fn private_dispatch_names_reach_documented_routes() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    for (name, params, method, path) in PRIVATE_ROUTES {
        private_call(&client, name, params);
        let recorded = next(&receiver, name);
        assert_eq!(recorded.method, *method, "{name}: HTTP method");
        assert_eq!(recorded.path, *path, "{name}: request path");
        assert!(
            recorded.get("signature").is_some(),
            "{name}: must be signed"
        );
        assert!(recorded.get("timestamp").is_some(), "{name}: timestamp");
        assert!(recorded.api_key_header, "{name}: X-BX-APIKEY header");
        assert!(
            recorded.get("type_").is_none(),
            "{name}: Python alias type_ must never reach the wire"
        );
    }
}

#[test]
fn listen_key_creation_is_unsigned_post_with_api_key_header() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    private_call(&client, "get_listen_key", &[]);
    let recorded = next(&receiver, "get_listen_key");
    assert_eq!(recorded.method, "POST");
    assert_eq!(recorded.path, "/openApi/user/auth/userDataStream");
    assert!(recorded.api_key_header);
    assert!(recorded.get("signature").is_none());
}

#[test]
fn order_helpers_force_side_type_position_side_and_time_in_force() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    let cases: &[(&str, &[(&str, &str)], &[(&str, &str)])] = &[
        (
            "place_swap_market_buy_order",
            &[SWAP, ("quantity", "1"), ("positionSide", "SHORT")],
            &[
                ("side", "BUY"),
                ("type", "MARKET"),
                ("positionSide", "SHORT"),
            ],
        ),
        (
            "place_swap_market_sell_order",
            &[SWAP, ("quantity", "1"), ("positionSide", "SHORT")],
            &[("side", "SELL"), ("type", "MARKET")],
        ),
        (
            "place_swap_post_only_buy_order",
            SWAP_SIDED_LIMIT,
            &[
                ("side", "BUY"),
                ("type", "LIMIT"),
                ("timeInForce", "PostOnly"),
            ],
        ),
        (
            "place_spot_post_only_sell_order",
            SPOT_SIDED_LIMIT,
            &[
                ("side", "SELL"),
                ("type", "LIMIT"),
                ("timeInForce", "PostOnly"),
            ],
        ),
        (
            "place_spot_market_buy_order",
            &[SPOT, ("quoteOrderQty", "10")],
            &[("side", "BUY"), ("type", "MARKET"), ("quoteOrderQty", "10")],
        ),
    ];
    for (name, params, expected) in cases {
        private_call(&client, name, params);
        let recorded = next(&receiver, name);
        for (key, value) in *expected {
            assert_eq!(recorded.get(key), Some(*value), "{name}: {key}");
        }
    }
}

#[test]
fn type_alias_is_translated_for_swap_cancel_all_and_open_orders() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    for name in ["cancel_swap_all_orders", "get_open_orders"] {
        private_call(&client, name, &[SWAP, ("type_", "LIMIT")]);
        let recorded = next(&receiver, name);
        assert_eq!(recorded.get("type"), Some("LIMIT"), "{name}");
        assert!(recorded.get("type_").is_none(), "{name}");
    }
    private_call(
        &client,
        "get_spot_order_history",
        &[SPOT, ("type_", "LIMIT")],
    );
    let recorded = next(&receiver, "get_spot_order_history");
    assert_eq!(recorded.get("type"), Some("LIMIT"));
    assert_eq!(recorded.get("pageIndex"), Some("1"));
    assert_eq!(recorded.get("pageSize"), Some("100"));
}

#[test]
fn identifier_lists_and_client_ids_use_official_keys() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    private_call(
        &client,
        "cancel_spot_order",
        &[SPOT, ("clientOrderId", "cid-1")],
    );
    let recorded = next(&receiver, "cancel_spot_order");
    assert_eq!(recorded.get("clientOrderID"), Some("cid-1"));

    private_call(
        &client,
        "cancel_spot_batch_orders",
        &[SPOT, ("orderIds", "[1, 2]")],
    );
    let recorded = next(&receiver, "cancel_spot_batch_orders");
    assert_eq!(recorded.get("orderIds"), Some("1,2"));

    private_call(&client, "get_asset_transfer_records", &[("tranId", "9")]);
    let recorded = next(&receiver, "get_asset_transfer_records");
    assert_eq!(recorded.get("transferId"), Some("9"));

    private_call(&client, "keep_alive_listen_key", &[("listen_key", "abc")]);
    let recorded = next(&receiver, "keep_alive_listen_key");
    assert_eq!(recorded.get("listenKey"), Some("abc"));

    private_call(
        &client,
        "get_fund_flow",
        &[SWAP, ("income_type", "FUNDING_FEE"), ("limit", "5")],
    );
    let recorded = next(&receiver, "get_fund_flow");
    assert_eq!(recorded.get("incomeType"), Some("FUNDING_FEE"));
    assert_eq!(recorded.get("limit"), Some("5"));
}

#[test]
fn invalid_parameters_fail_before_transport() {
    let client = signed_client("http://127.0.0.1:9".to_string());
    let cases: &[(&str, &[(&str, &str)])] = &[
        ("get_swap_account_balance", &[("unknown", "1")]),
        ("get_swap_account_balance", &[("recvWindow", "6000")]),
        ("set_leverage", &[SWAP, ("side", "UP"), ("leverage", "5")]),
        ("change_margin_type", &[SWAP, ("marginType", "PORTFOLIO")]),
        ("cancel_swap_order", &[SWAP]),
        (
            "cancel_swap_batch_order",
            &[SWAP, ("orderIdList", "[1,2,3,4,5,6,7,8,9,10,11]")],
        ),
        (
            "place_swap_limit_order",
            &[SWAP, ("side", "BUY"), ("quantity", "1")],
        ),
        ("place_swap_market_order", &[SWAP, ("side", "BUY")]),
        (
            "place_swap_order",
            &[
                SWAP,
                ("side", "BUY"),
                ("type_", "STOP_MARKET"),
                ("quantity", "1"),
            ],
        ),
        (
            "place_swap_order",
            &[
                SWAP,
                ("side", "BUY"),
                ("type_", "MARKET"),
                ("quantity", "1"),
                ("positionSide", "LONG"),
                ("reduceOnly", "true"),
            ],
        ),
        ("place_spot_batch_order", &[("data", "[]")]),
        (
            "set_spot_cancel_all_after",
            &[("type_", "CLOSE"), ("timeOut", "30")],
        ),
        (
            "get_order_history",
            &[SWAP, ("startTime", "0"), ("endTime", "999999999999")],
        ),
        (
            "asset_transfer",
            &[
                ("fromAccount", "fund"),
                ("toAccount", "spot"),
                ("asset", "USDT"),
                ("amount", "-1"),
            ],
        ),
        ("get_listen_key", &[("extra", "1")]),
    ];
    for (name, params) in cases {
        let client = client.clone();
        let method = name.to_string();
        let params_owned = owned(params);
        assert!(
            block_on(async move { client.private_request(&method, params_owned).await }).is_err(),
            "{name} {params:?} must be rejected"
        );
    }
    let client = BingxClient::public(Duration::from_secs(10)).expect("client");
    for (name, params) in [
        ("get_orderbook", vec![SWAP, ("limit", "7")]),
        ("get_kline", vec![SWAP, ("interval", "2m")]),
        ("get_spot_orderbook_v2", vec![SPOT, ("depth", "0")]),
        ("get_nope", vec![]),
    ] {
        let client = client.clone();
        let params_owned = owned(&params);
        assert!(
            block_on(async move { client.public_request(name, params_owned).await }).is_err(),
            "{name} must be rejected"
        );
    }
}

#[tokio::test]
async fn swap_trading_controls_use_documented_parameters() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    client
        .private_request(
            "set_swap_cancel_all_after",
            vec![
                ("type_".into(), "ACTIVATE".into()),
                ("timeOut".into(), "30".into()),
            ],
        )
        .await
        .expect("set_swap_cancel_all_after");
    let request = next(&receiver, "set_swap_cancel_all_after");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("POST", "/openApi/swap/v2/trade/cancelAllAfter", true)
    );
    assert!(request.query.contains(&("type".into(), "ACTIVATE".into())));
    assert!(request.query.contains(&("timeOut".into(), "30".into())));
    client
        .private_request(
            "get_swap_open_order",
            vec![
                ("product_symbol".into(), "BTC-USDT".into()),
                ("orderId".into(), "123".into()),
            ],
        )
        .await
        .expect("get_swap_open_order");
    let request = next(&receiver, "get_swap_open_order");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("GET", "/openApi/swap/v2/trade/openOrder", true)
    );
    assert!(
        request
            .query
            .contains(&("symbol".into(), "BTC-USDT".into()))
    );
    assert!(request.query.contains(&("orderId".into(), "123".into())));
    client
        .private_request("get_swap_force_orders", vec![])
        .await
        .expect("get_swap_force_orders");
    let request = next(&receiver, "get_swap_force_orders");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("GET", "/openApi/swap/v2/trade/forceOrders", true)
    );
    client
        .private_request(
            "get_swap_trade_fills",
            vec![
                ("tradingUnit".into(), "COIN".into()),
                ("startTs".into(), "1700000000000".into()),
                ("endTs".into(), "1700000100000".into()),
            ],
        )
        .await
        .expect("get_swap_trade_fills");
    let request = next(&receiver, "get_swap_trade_fills");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("GET", "/openApi/swap/v2/trade/allFillOrders", true)
    );
    assert!(
        request
            .query
            .contains(&("tradingUnit".into(), "COIN".into()))
    );
    assert!(
        request
            .query
            .contains(&("startTs".into(), "1700000000000".into()))
    );
    assert!(
        request
            .query
            .contains(&("endTs".into(), "1700000100000".into()))
    );
    client
        .private_request(
            "adjust_swap_position_margin",
            vec![
                ("product_symbol".into(), "BTC-USDT".into()),
                ("amount".into(), "2".into()),
                ("type_".into(), "2".into()),
                ("positionSide".into(), "LONG".into()),
            ],
        )
        .await
        .expect("adjust_swap_position_margin");
    let request = next(&receiver, "adjust_swap_position_margin");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("POST", "/openApi/swap/v2/trade/positionMargin", true)
    );
    assert!(
        request
            .query
            .contains(&("symbol".into(), "BTC-USDT".into()))
    );
    assert!(request.query.contains(&("amount".into(), "2".into())));
    assert!(request.query.contains(&("type".into(), "2".into())));
    assert!(
        request
            .query
            .contains(&("positionSide".into(), "LONG".into()))
    );
    client
        .private_request(
            "amend_swap_order",
            vec![
                ("product_symbol".into(), "BTC-USDT".into()),
                ("quantity".into(), "1".into()),
                ("clientOrderId".into(), "amend-me".into()),
            ],
        )
        .await
        .expect("amend_swap_order");
    let request = next(&receiver, "amend_swap_order");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("POST", "/openApi/swap/v1/trade/amend", true)
    );
    assert!(
        request
            .query
            .contains(&("symbol".into(), "BTC-USDT".into()))
    );
    assert!(request.query.contains(&("quantity".into(), "1".into())));
    assert!(
        request
            .query
            .contains(&("clientOrderId".into(), "amend-me".into()))
    );
    client
        .private_request(
            "place_swap_twap_order",
            vec![
                ("product_symbol".into(), "BTC-USDT".into()),
                ("side".into(), "BUY".into()),
                ("positionSide".into(), "LONG".into()),
                ("priceType".into(), "constant".into()),
                ("priceVariance".into(), "1".into()),
                ("triggerPrice".into(), "60000".into()),
                ("interval".into(), "10".into()),
                ("amountPerOrder".into(), "1".into()),
                ("totalAmount".into(), "5".into()),
            ],
        )
        .await
        .expect("place_swap_twap_order");
    let request = next(&receiver, "place_swap_twap_order");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("POST", "/openApi/swap/v1/twap/order", true)
    );
    assert!(
        request
            .query
            .contains(&("symbol".into(), "BTC-USDT".into()))
    );
    assert!(request.query.contains(&("side".into(), "BUY".into())));
    assert!(
        request
            .query
            .contains(&("positionSide".into(), "LONG".into()))
    );
    assert!(
        request
            .query
            .contains(&("priceType".into(), "constant".into()))
    );
    assert!(
        request
            .query
            .contains(&("priceVariance".into(), "1".into()))
    );
    assert!(
        request
            .query
            .contains(&("triggerPrice".into(), "60000".into()))
    );
    assert!(request.query.contains(&("interval".into(), "10".into())));
    assert!(
        request
            .query
            .contains(&("amountPerOrder".into(), "1".into()))
    );
    assert!(request.query.contains(&("totalAmount".into(), "5".into())));
    client
        .private_request(
            "cancel_swap_twap_order",
            vec![("mainOrderId".into(), "123".into())],
        )
        .await
        .expect("cancel_swap_twap_order");
    let request = next(&receiver, "cancel_swap_twap_order");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("POST", "/openApi/swap/v1/twap/cancelOrder", true)
    );
    assert!(
        request
            .query
            .contains(&("mainOrderId".into(), "123".into()))
    );
    client
        .private_request("get_swap_open_twap_orders", vec![])
        .await
        .expect("get_swap_open_twap_orders");
    let request = next(&receiver, "get_swap_open_twap_orders");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("GET", "/openApi/swap/v1/twap/openOrders", true)
    );
    client
        .private_request(
            "get_swap_twap_order_history",
            vec![
                ("pageIndex".into(), "1".into()),
                ("pageSize".into(), "20".into()),
                ("startTime".into(), "1700000000000".into()),
                ("endTime".into(), "1700000100000".into()),
            ],
        )
        .await
        .expect("get_swap_twap_order_history");
    let request = next(&receiver, "get_swap_twap_order_history");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("GET", "/openApi/swap/v1/twap/historyOrders", true)
    );
    assert!(request.query.contains(&("pageIndex".into(), "1".into())));
    assert!(request.query.contains(&("pageSize".into(), "20".into())));
    assert!(
        request
            .query
            .contains(&("startTime".into(), "1700000000000".into()))
    );
    assert!(
        request
            .query
            .contains(&("endTime".into(), "1700000100000".into()))
    );
    client
        .private_request(
            "get_swap_twap_order",
            vec![("mainOrderId".into(), "123".into())],
        )
        .await
        .expect("get_swap_twap_order");
    let request = next(&receiver, "get_swap_twap_order");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("GET", "/openApi/swap/v1/twap/orderDetail", true)
    );
    assert!(
        request
            .query
            .contains(&("mainOrderId".into(), "123".into()))
    );
    client
        .private_request("get_swap_asset_mode", vec![])
        .await
        .expect("get_swap_asset_mode");
    let request = next(&receiver, "get_swap_asset_mode");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("GET", "/openApi/swap/v1/trade/assetMode", true)
    );
    client
        .private_request(
            "set_swap_asset_mode",
            vec![
                ("confirm".into(), "true".into()),
                ("assetMode".into(), "multiAssetsMode".into()),
            ],
        )
        .await
        .expect("set_swap_asset_mode");
    let request = next(&receiver, "set_swap_asset_mode");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("POST", "/openApi/swap/v1/trade/assetMode", true)
    );
    assert!(
        request
            .query
            .contains(&("assetMode".into(), "multiAssetsMode".into()))
    );
    client
        .private_request("get_swap_multi_asset_rules", vec![])
        .await
        .expect("get_swap_multi_asset_rules");
    let request = next(&receiver, "get_swap_multi_asset_rules");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("GET", "/openApi/swap/v1/trade/multiAssetsRules", true)
    );
    client
        .private_request("get_swap_margin_assets", vec![])
        .await
        .expect("get_swap_margin_assets");
    let request = next(&receiver, "get_swap_margin_assets");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("GET", "/openApi/swap/v1/user/marginAssets", true)
    );
    client
        .private_request("get_swap_full_orders", vec![("limit".into(), "20".into())])
        .await
        .expect("get_swap_full_orders");
    let request = next(&receiver, "get_swap_full_orders");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("GET", "/openApi/swap/v1/trade/fullOrder", true)
    );
    assert!(request.query.contains(&("limit".into(), "20".into())));
    client
        .private_request(
            "get_swap_fill_history",
            vec![
                ("product_symbol".into(), "BTC-USDT".into()),
                ("startTs".into(), "1700000000000".into()),
                ("endTs".into(), "1700000100000".into()),
            ],
        )
        .await
        .expect("get_swap_fill_history");
    let request = next(&receiver, "get_swap_fill_history");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("GET", "/openApi/swap/v2/trade/fillHistory", true)
    );
    assert!(
        request
            .query
            .contains(&("symbol".into(), "BTC-USDT".into()))
    );
    assert!(
        request
            .query
            .contains(&("startTs".into(), "1700000000000".into()))
    );
    assert!(
        request
            .query
            .contains(&("endTs".into(), "1700000100000".into()))
    );
    client
        .private_request(
            "get_swap_position_history",
            vec![
                ("product_symbol".into(), "BTC-USDT".into()),
                ("startTs".into(), "1700000000000".into()),
                ("endTs".into(), "1700000100000".into()),
            ],
        )
        .await
        .expect("get_swap_position_history");
    let request = next(&receiver, "get_swap_position_history");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("GET", "/openApi/swap/v1/trade/positionHistory", true)
    );
    assert!(
        request
            .query
            .contains(&("symbol".into(), "BTC-USDT".into()))
    );
    assert!(
        request
            .query
            .contains(&("startTs".into(), "1700000000000".into()))
    );
    assert!(
        request
            .query
            .contains(&("endTs".into(), "1700000100000".into()))
    );
    client
        .private_request(
            "get_swap_margin_history",
            vec![
                ("product_symbol".into(), "BTC-USDT".into()),
                ("positionId".into(), "123".into()),
                ("startTime".into(), "1700000000000".into()),
                ("endTime".into(), "1700000100000".into()),
                ("pageIndex".into(), "1".into()),
                ("pageSize".into(), "20".into()),
            ],
        )
        .await
        .expect("get_swap_margin_history");
    let request = next(&receiver, "get_swap_margin_history");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("GET", "/openApi/swap/v1/positionMargin/history", true)
    );
    assert!(
        request
            .query
            .contains(&("symbol".into(), "BTC-USDT".into()))
    );
    assert!(request.query.contains(&("positionId".into(), "123".into())));
    assert!(
        request
            .query
            .contains(&("startTime".into(), "1700000000000".into()))
    );
    assert!(
        request
            .query
            .contains(&("endTime".into(), "1700000100000".into()))
    );
    assert!(request.query.contains(&("pageIndex".into(), "1".into())));
    assert!(request.query.contains(&("pageSize".into(), "20".into())));
    client
        .private_request(
            "get_swap_maintenance_margin_ratios",
            vec![("product_symbol".into(), "BTC-USDT".into())],
        )
        .await
        .expect("get_swap_maintenance_margin_ratios");
    let request = next(&receiver, "get_swap_maintenance_margin_ratios");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("GET", "/openApi/swap/v1/maintMarginRatio", true)
    );
    assert!(
        request
            .query
            .contains(&("symbol".into(), "BTC-USDT".into()))
    );
    client
        .private_request(
            "set_swap_auto_add_margin",
            vec![
                ("product_symbol".into(), "BTC-USDT".into()),
                ("positionId".into(), "123".into()),
                ("functionSwitch".into(), "true".into()),
            ],
        )
        .await
        .expect("set_swap_auto_add_margin");
    let request = next(&receiver, "set_swap_auto_add_margin");
    assert_eq!(
        (
            request.method.as_str(),
            request.path.as_str(),
            request.api_key_header
        ),
        ("POST", "/openApi/swap/v1/trade/autoAddMargin", true)
    );
    assert!(
        request
            .query
            .contains(&("symbol".into(), "BTC-USDT".into()))
    );
    assert!(request.query.contains(&("positionId".into(), "123".into())));
    assert!(
        request
            .query
            .contains(&("functionSwitch".into(), "true".into()))
    );
}

#[test]
fn coin_swap_and_oco_routes_match_official_paths() {
    let (url, receiver) = recording_server();
    let client = BingxClient::with_base_url(
        Some("api-key".into()),
        Some("api-secret".into()),
        Duration::from_secs(10),
        url,
    )
    .unwrap();
    let cases: &[(bool, &str, &[(&str, &str)], &str, &str)] = &[
        (
            true,
            "get_spot_historical_trades",
            &[("product_symbol", "BTC-USDT-SPOT")],
            "GET",
            "/openApi/market/his/v1/trade",
        ),
        (
            false,
            "get_coin_network_config",
            &[],
            "GET",
            "/openApi/wallets/v1/capital/config/getall",
        ),
        (
            false,
            "get_deposit_addresses",
            &[("coin", "USDT")],
            "GET",
            "/openApi/wallets/v1/capital/deposit/address",
        ),
        (
            false,
            "get_deposit_risk_records",
            &[],
            "GET",
            "/openApi/wallets/v1/capital/deposit/riskRecords",
        ),
        (
            true,
            "get_swap_historical_trades",
            &[("product_symbol", "BTC-USDT")],
            "GET",
            "/openApi/swap/v1/market/historicalTrades",
        ),
        (
            false,
            "reverse_swap_position",
            &[
                ("confirm", "true"),
                ("type_", "Reverse"),
                ("product_symbol", "BTC-USDT"),
            ],
            "POST",
            "/openApi/swap/v1/trade/reverse",
        ),
        (
            false,
            "adjust_simulated_trading_balance",
            &[],
            "POST",
            "/openApi/swap/v2/trade/getVst",
        ),
        (
            false,
            "get_standard_futures_positions",
            &[],
            "GET",
            "/openApi/contract/v1/allPosition",
        ),
        (
            false,
            "get_standard_futures_orders",
            &[("product_symbol", "BTC-USDT")],
            "GET",
            "/openApi/contract/v1/allOrders",
        ),
        (
            false,
            "get_standard_futures_balance",
            &[],
            "GET",
            "/openApi/contract/v1/balance",
        ),
        (
            false,
            "get_api_permissions",
            &[],
            "GET",
            "/openApi/v1/account/apiPermissions",
        ),
        (
            false,
            "create_sub_account",
            &[("subAccountString", "trader123")],
            "POST",
            "/openApi/subAccount/v1/create",
        ),
        (
            false,
            "set_sub_account_frozen",
            &[("subUid", "123"), ("freeze", "true")],
            "POST",
            "/openApi/subAccount/v1/updateStatus",
        ),
        (
            false,
            "create_sub_account_api_key",
            &[
                ("subUid", "123"),
                ("note", "trading"),
                ("permissions", "[4,5]"),
            ],
            "POST",
            "/openApi/subAccount/v1/apiKey/create",
        ),
        (
            false,
            "modify_sub_account_api_key",
            &[
                ("subUid", "123"),
                ("apiKey", "query-key"),
                ("note", "trading"),
                ("permissions", "[4,5]"),
            ],
            "POST",
            "/openApi/subAccount/v1/apiKey/edit",
        ),
        (
            false,
            "delete_sub_account_api_key",
            &[("subUid", "123"), ("apiKey", "query-key")],
            "POST",
            "/openApi/subAccount/v1/apiKey/del",
        ),
        (
            false,
            "set_sub_account_transfer_authorization",
            &[("subUids", "123"), ("transferable", "true")],
            "POST",
            "/openApi/account/v1/innerTransfer/authorizeSubAccount",
        ),
        (
            false,
            "get_sub_account_deposit_addresses",
            &[("coin", "USDT"), ("subUid", "123")],
            "GET",
            "/openApi/wallets/v1/capital/subAccount/deposit/address",
        ),
        (
            false,
            "get_sub_account_deposit_history",
            &[],
            "GET",
            "/openApi/wallets/v1/capital/deposit/subHisrec",
        ),
        (
            false,
            "get_api_restrictions",
            &[],
            "GET",
            "/openApi/v1/account/apiRestrictions",
        ),
        (
            false,
            "create_sub_account_deposit_address",
            &[
                ("coin", "USDT"),
                ("subUid", "123"),
                ("network", "TRC20"),
                ("walletType", "1"),
            ],
            "POST",
            "/openApi/wallets/v1/capital/deposit/createSubAddress",
        ),
        (
            true,
            "get_swap_server_time",
            &[],
            "GET",
            "/openApi/swap/v2/server/time",
        ),
        (
            true,
            "get_swap_price_ticker",
            &[("product_symbol", "BTC-USDT")],
            "GET",
            "/openApi/swap/v1/ticker/price",
        ),
        (
            true,
            "get_coin_swap_contracts",
            &[("product_symbol", "BTC-USD")],
            "GET",
            "/openApi/cswap/v1/market/contracts",
        ),
        (
            true,
            "get_coin_swap_orderbook",
            &[("product_symbol", "BTC-USD")],
            "GET",
            "/openApi/cswap/v1/market/depth",
        ),
        (
            true,
            "get_coin_swap_kline",
            &[("product_symbol", "BTC-USD"), ("interval", "1m")],
            "GET",
            "/openApi/cswap/v1/market/klines",
        ),
        (
            true,
            "get_coin_swap_premium_index",
            &[("product_symbol", "BTC-USD")],
            "GET",
            "/openApi/cswap/v1/market/premiumIndex",
        ),
        (
            true,
            "get_coin_swap_open_interest",
            &[("product_symbol", "BTC-USD")],
            "GET",
            "/openApi/cswap/v1/market/openInterest",
        ),
        (
            true,
            "get_coin_swap_ticker",
            &[("product_symbol", "BTC-USD")],
            "GET",
            "/openApi/cswap/v1/market/ticker",
        ),
        (
            false,
            "place_coin_swap_order",
            &[
                ("product_symbol", "BTC-USD"),
                ("side", "SELL"),
                ("type_", "MARKET"),
                ("quantity", "1"),
            ],
            "POST",
            "/openApi/cswap/v1/trade/order",
        ),
        (
            false,
            "cancel_coin_swap_order",
            &[("product_symbol", "BTC-USD"), ("orderId", "1")],
            "DELETE",
            "/openApi/cswap/v1/trade/cancelOrder",
        ),
        (
            false,
            "cancel_coin_swap_all_orders",
            &[("product_symbol", "BTC-USD")],
            "POST",
            "/openApi/cswap/v1/trade/allOpenOrders",
        ),
        (
            false,
            "close_coin_swap_all_positions",
            &[("product_symbol", "BTC-USD")],
            "POST",
            "/openApi/cswap/v1/trade/closeAllPositions",
        ),
        (
            false,
            "get_coin_swap_open_orders",
            &[("product_symbol", "BTC-USD")],
            "GET",
            "/openApi/cswap/v1/trade/openOrders",
        ),
        (
            false,
            "get_coin_swap_order",
            &[("product_symbol", "BTC-USD"), ("orderId", "1")],
            "GET",
            "/openApi/cswap/v1/trade/orderDetail",
        ),
        (
            false,
            "get_coin_swap_order_history",
            &[("limit", "20"), ("product_symbol", "BTC-USD")],
            "GET",
            "/openApi/cswap/v1/trade/orderHistory",
        ),
        (
            false,
            "get_coin_swap_fills",
            &[("orderId", "1")],
            "GET",
            "/openApi/cswap/v1/trade/allFillOrders",
        ),
        (
            false,
            "get_coin_swap_force_orders",
            &[("product_symbol", "BTC-USD")],
            "GET",
            "/openApi/cswap/v1/trade/forceOrders",
        ),
        (
            false,
            "get_coin_swap_leverage",
            &[("product_symbol", "BTC-USD")],
            "GET",
            "/openApi/cswap/v1/trade/leverage",
        ),
        (
            false,
            "set_coin_swap_leverage",
            &[
                ("product_symbol", "BTC-USD"),
                ("side", "LONG"),
                ("leverage", "5"),
            ],
            "POST",
            "/openApi/cswap/v1/trade/leverage",
        ),
        (
            false,
            "get_coin_swap_margin_type",
            &[("product_symbol", "BTC-USD")],
            "GET",
            "/openApi/cswap/v1/trade/marginType",
        ),
        (
            false,
            "set_coin_swap_margin_type",
            &[("product_symbol", "BTC-USD"), ("marginType", "ISOLATED")],
            "POST",
            "/openApi/cswap/v1/trade/marginType",
        ),
        (
            false,
            "adjust_coin_swap_position_margin",
            &[
                ("product_symbol", "BTC-USD"),
                ("positionSide", "LONG"),
                ("amount", "1"),
                ("type_", "1"),
            ],
            "POST",
            "/openApi/cswap/v1/trade/positionMargin",
        ),
        (
            false,
            "get_coin_swap_commission_rate",
            &[],
            "GET",
            "/openApi/cswap/v1/user/commissionRate",
        ),
        (
            false,
            "get_coin_swap_balance",
            &[("product_symbol", "BTC-USD")],
            "GET",
            "/openApi/cswap/v1/user/balance",
        ),
        (
            false,
            "get_coin_swap_positions",
            &[("product_symbol", "BTC-USD")],
            "GET",
            "/openApi/cswap/v1/user/positions",
        ),
        (
            true,
            "get_spot_historical_kline",
            &[("product_symbol", "BTC-USDT-SPOT"), ("interval", "1m")],
            "GET",
            "/openApi/market/his/v1/kline",
        ),
        (
            false,
            "place_spot_oco",
            &[
                ("product_symbol", "BTC-USDT-SPOT"),
                ("side", "SELL"),
                ("quantity", "1"),
                ("limitPrice", "120"),
                ("triggerPrice", "90"),
                ("orderPrice", "89"),
            ],
            "POST",
            "/openApi/spot/v1/oco/order",
        ),
        (
            false,
            "cancel_spot_oco",
            &[("orderId", "1")],
            "POST",
            "/openApi/spot/v1/oco/cancel",
        ),
        (
            false,
            "get_spot_oco",
            &[("orderListId", "1")],
            "GET",
            "/openApi/spot/v1/oco/orderList",
        ),
        (
            false,
            "get_spot_open_oco",
            &[("pageIndex", "1"), ("pageSize", "20")],
            "GET",
            "/openApi/spot/v1/oco/openOrderList",
        ),
        (
            false,
            "get_spot_oco_history",
            &[("pageIndex", "1"), ("pageSize", "20")],
            "GET",
            "/openApi/spot/v1/oco/historyOrderList",
        ),
        (
            false,
            "get_deposit_history",
            &[],
            "GET",
            "/openApi/api/v3/capital/deposit/hisrec",
        ),
    ];
    for (public, name, params, verb, path) in cases {
        let client = client.clone();
        let name_owned = name.to_string();
        let params = owned(params);
        let public = *public;
        block_on(async move {
            if public {
                client.public_request(&name_owned, params).await
            } else {
                client.private_request(&name_owned, params).await
            }
        })
        .expect(name);
        let request = next(&receiver, name);
        assert_eq!(request.method, *verb);
        assert_eq!(request.path, *path);
        if matches!(
            name,
            &"create_sub_account_api_key" | &"modify_sub_account_api_key"
        ) {
            assert_eq!(request.body["permissions"], serde_json::json!([4, 5]));
        }
        assert_eq!(
            request.get("signature").is_some() || request.body.get("signature").is_some(),
            !public
        );
        if path.contains("/cswap/") && request.get("symbol").is_some() {
            assert_eq!(request.get("symbol"), Some("BTC-USD"));
        }
    }
}

#[test]
fn batch_replacement_keeps_json_number_quantity_for_conditional_order() {
    let (url, receiver) = recording_server();
    let client = BingxClient::with_base_url(
        Some("api-key".into()),
        Some("api-secret".into()),
        Duration::from_secs(10),
        url,
    )
    .unwrap();
    let orders = r#"[{"product_symbol":"BTC-USDT","cancelOrderId":"1","side":"SELL","positionSide":"BOTH","type":"STOP_MARKET","stopPrice":90,"quantity":1,"cancelReplaceMode":"STOP_ON_FAILURE"}]"#;
    block_on(async move {
        client
            .private_request(
                "replace_swap_batch_orders",
                vec![("batchOrders".into(), orders.into())],
            )
            .await
    })
    .unwrap();
    let request = next(&receiver, "replace_swap_batch_orders");
    assert_eq!(request.path, "/openApi/swap/v1/trade/batchCancelReplace");
    let batch: serde_json::Value =
        serde_json::from_str(request.get("batchOrders").unwrap()).unwrap();
    assert_eq!(batch[0]["quantity"], 1);
    assert_eq!(batch[0]["symbol"], "BTC-USDT");
    assert!(batch[0].get("closePosition").is_none());
    assert!(request.get("signature").is_some());
}

#[test]
fn sided_swap_helpers_require_and_preserve_explicit_position_side() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    for kind in ["market", "limit", "post_only"] {
        for side in ["buy", "sell"] {
            let method = format!("place_swap_{kind}_{side}_order");
            let mut params = vec![SWAP, ("quantity", "1")];
            if kind != "market" {
                params.push(("price", "1"));
            }
            let missing = params
                .iter()
                .map(|(k, v)| (k.to_string(), v.to_string()))
                .collect();
            let call_client = client.clone();
            let call_method = method.clone();
            let result =
                block_on(async move { call_client.private_request(&call_method, missing).await });
            assert!(result.unwrap_err().to_string().contains("positionSide"));
            assert!(receiver.try_recv().is_err());
            let position = if side == "buy" { "SHORT" } else { "LONG" };
            params.push(("positionSide", position));
            private_call(&client, &method, &params);
            assert_eq!(next(&receiver, &method).get("positionSide"), Some(position));
        }
    }
}

#[test]
fn coin_swap_attached_tpsl_preserves_fractional_json_numbers() {
    let (url, receiver) = recording_server();
    let client = signed_client(url);
    private_call(
        &client,
        "place_coin_swap_order",
        &[
            ("product_symbol", "BTC-USD"),
            ("side", "BUY"),
            ("type_", "MARKET"),
            ("quantity", "1"),
            (
                "takeProfit",
                r#"{"type":"TAKE_PROFIT","stopPrice":"61000.5","price":"61000.125000000000000001"}"#,
            ),
            (
                "stopLoss",
                r#"{"type":"STOP_MARKET","stopPrice":"59000.75"}"#,
            ),
        ],
    );
    let request = next(&receiver, "place_coin_swap_order");
    assert_eq!(request.method, "POST");
    assert_eq!(request.path, "/openApi/cswap/v1/trade/order");
    for (field, key, expected) in [
        ("takeProfit", "stopPrice", "61000.5"),
        ("takeProfit", "price", "61000.125000000000000001"),
        ("stopLoss", "stopPrice", "59000.75"),
    ] {
        let value: serde_json::Value = serde_json::from_str(request.get(field).unwrap()).unwrap();
        assert!(value[key].is_number());
        assert_eq!(value[key].to_string(), expected);
    }
}
