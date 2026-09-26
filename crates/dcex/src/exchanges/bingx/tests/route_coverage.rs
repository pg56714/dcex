//! Route coverage: every BingX dispatch name must reach the documented
//! METHOD + path from the official API docs, fully offline.

use std::io::{BufRead, BufReader, Read, Write};
use std::net::TcpListener;
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

use crate::http::block_on;

use super::BingxClient;

struct Recorded {
    method: String,
    path: String,
    query: Vec<(String, String)>,
    api_key_header: bool,
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
                .set_read_timeout(Some(Duration::from_secs(5)))
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

const SWAP: (&str, &str) = ("product_symbol", "BTC-USDT-SWAP");
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
const SWAP_SIDED_LIMIT: &[(&str, &str)] = &[SWAP, ("quantity", "1"), ("price", "1")];

/// (dispatch name, params, HTTP method, documented path)
const PRIVATE_ROUTES: &[Case] = &[
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
        &[SWAP, ("quantity", "1")],
        "POST",
        "/openApi/swap/v2/trade/order",
    ),
    (
        "place_swap_market_sell_order",
        &[SWAP, ("quantity", "1")],
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
        BingxClient::with_base_url(None, None, Duration::from_secs(5), url).expect("client");
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
        BingxClient::with_base_url(None, None, Duration::from_secs(5), url).expect("client");
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
        Duration::from_secs(1),
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
            &[SWAP, ("quantity", "1")],
            &[
                ("side", "BUY"),
                ("type", "MARKET"),
                ("positionSide", "LONG"),
            ],
        ),
        (
            "place_swap_market_sell_order",
            &[SWAP, ("quantity", "1")],
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
    let client = BingxClient::public(Duration::from_secs(1)).expect("client");
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
