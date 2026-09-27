//! Offline request-building coverage for every Hyperliquid info/exchange route.

use std::io::{ErrorKind, Read, Write};
use std::net::TcpListener;
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

use serde_json::{Value, json};

use super::HyperliquidClient;

const USER: &str = "0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";
const USER_LOWER: &str = "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";
const WALLET: &str = "0x2222222222222222222222222222222222222222";
const CLOID: &str = "0x1234567890ABCDEF1234567890ABCDEF";
const CLOID_LOWER: &str = "0x1234567890abcdef1234567890abcdef";
const ETH: &str = "[\"ETH\",1]";

struct Recorded {
    request_line: String,
    body: Value,
}

/// Serves one request with `response_body` and returns the parsed request.
fn serve_once(response_body: &'static str) -> (String, JoinHandle<Recorded>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    listener.set_nonblocking(true).expect("nonblocking");
    let address = listener.local_addr().expect("address");
    let handle = thread::spawn(move || {
        let deadline = Instant::now() + Duration::from_secs(5);
        let (mut stream, _) = loop {
            match listener.accept() {
                Ok(connection) => break connection,
                Err(error) if error.kind() == ErrorKind::WouldBlock => {
                    assert!(Instant::now() < deadline, "no request received");
                    thread::sleep(Duration::from_millis(5));
                }
                Err(error) => panic!("accept failed: {error}"),
            }
        };
        stream.set_nonblocking(false).expect("blocking stream");
        stream
            .set_read_timeout(Some(Duration::from_secs(2)))
            .expect("read timeout");
        let mut raw = Vec::new();
        let mut buffer = [0u8; 4096];
        loop {
            let size = stream.read(&mut buffer).expect("read");
            assert!(size > 0, "connection closed before body");
            raw.extend_from_slice(&buffer[..size]);
            let text = String::from_utf8_lossy(&raw).into_owned();
            if let Some((head, body)) = text.split_once("\r\n\r\n") {
                let length = head
                    .lines()
                    .find_map(|line| {
                        line.to_ascii_lowercase()
                            .strip_prefix("content-length: ")
                            .and_then(|value| value.trim().parse::<usize>().ok())
                    })
                    .unwrap_or(0);
                if body.len() >= length {
                    break;
                }
            }
        }
        let response = format!(
            "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
            response_body.len(),
            response_body
        );
        stream.write_all(response.as_bytes()).expect("write");
        let text = String::from_utf8_lossy(&raw).into_owned();
        let (head, body) = text.split_once("\r\n\r\n").expect("http request");
        Recorded {
            request_line: head.lines().next().unwrap_or_default().to_string(),
            body: serde_json::from_str(body).expect("json body"),
        }
    });
    (format!("http://{address}"), handle)
}

fn pairs(values: &[(&str, &str)]) -> Vec<(String, String)> {
    values
        .iter()
        .map(|(key, value)| ((*key).to_string(), (*value).to_string()))
        .collect()
}

fn public_payload(method: &'static str, params: &[(&str, &str)]) -> Recorded {
    public_payload_with_response(method, params, "{\"ok\":true}").0
}

fn public_payload_with_response(
    method: &'static str,
    params: &[(&str, &str)],
    response: &'static str,
) -> (Recorded, Value) {
    let (base_url, server) = serve_once(response);
    let client =
        HyperliquidClient::with_endpoint(false, None, None, Duration::from_secs(2), base_url)
            .expect("client");
    let params = pairs(params);
    let data = crate::http::block_on(async move { client.public_request(method, params).await })
        .expect(method)
        .data;
    (server.join().expect("server"), data)
}

fn signing_client(endpoint: String) -> HyperliquidClient {
    HyperliquidClient::with_endpoint(
        false,
        Some(WALLET.to_string()),
        Some(format!("0x{}", "11".repeat(32))),
        Duration::from_secs(2),
        endpoint,
    )
    .expect("client")
}

fn private_payload(method: &'static str, params: &[(&str, &str)]) -> Recorded {
    let (base_url, server) = serve_once("{\"status\":\"ok\",\"response\":{\"type\":\"default\"}}");
    let client = signing_client(base_url);
    let params = pairs(params);
    crate::http::block_on(async move { client.private_request(method, params).await })
        .expect(method);
    let recorded = server.join().expect("server");
    assert!(
        recorded.request_line.starts_with("POST /exchange "),
        "{method}: {}",
        recorded.request_line
    );
    assert!(recorded.body["nonce"].as_u64().is_some(), "{method} nonce");
    let signature = &recorded.body["signature"];
    assert_eq!(signature["r"].as_str().map(str::len), Some(66), "{method}");
    assert_eq!(signature["s"].as_str().map(str::len), Some(66), "{method}");
    assert!(matches!(signature["v"].as_u64(), Some(27 | 28)), "{method}");
    recorded
}

#[test]
fn info_requests_match_official_request_types() {
    let cases: Vec<(&'static str, Vec<(&str, &str)>, Value)> = vec![
        (
            "get_vault_details",
            vec![
                ("vaultAddress", "0xabababababababababababababababababababab"),
                ("user", "0xabababababababababababababababababababab"),
            ],
            json!({"type": "vaultDetails", "vaultAddress": "0xabababababababababababababababababababab", "user": "0xabababababababababababababababababababab"}),
        ),
        (
            "get_delegations",
            vec![("user", "0xabababababababababababababababababababab")],
            json!({"type": "delegations", "user": "0xabababababababababababababababababababab"}),
        ),
        (
            "get_delegator_summary",
            vec![("user", "0xabababababababababababababababababababab")],
            json!({"type": "delegatorSummary", "user": "0xabababababababababababababababababababab"}),
        ),
        (
            "get_delegator_history",
            vec![("user", "0xabababababababababababababababababababab")],
            json!({"type": "delegatorHistory", "user": "0xabababababababababababababababababababab"}),
        ),
        (
            "get_delegator_rewards",
            vec![("user", "0xabababababababababababababababababababab")],
            json!({"type": "delegatorRewards", "user": "0xabababababababababababababababababababab"}),
        ),
        (
            "get_spot_deploy_state",
            vec![("user", "0xabababababababababababababababababababab")],
            json!({"type": "spotDeployState", "user": "0xabababababababababababababababababababab"}),
        ),
        ("get_outcome_meta", vec![], json!({"type": "outcomeMeta"})),
        (
            "get_settled_outcome",
            vec![("outcome", "1")],
            json!({"type": "settledOutcome", "outcome": 1}),
        ),
        (
            "get_outcome_deployer_limits",
            vec![("venue", "test")],
            json!({"type": "outcomeDeployerLimits", "venue": "test"}),
        ),
        (
            "get_perp_deploy_auction_status",
            vec![],
            json!({"type": "perpDeployAuctionStatus"}),
        ),
        (
            "get_spot_pair_deploy_auction_status",
            vec![],
            json!({"type": "spotPairDeployAuctionStatus"}),
        ),
        (
            "get_perps_at_open_interest_cap",
            vec![("dex", "xyz")],
            json!({"type": "perpsAtOpenInterestCap", "dex": "xyz"}),
        ),
        (
            "get_perp_dex_limits",
            vec![("dex", "xyz")],
            json!({"type": "perpDexLimits", "dex": "xyz"}),
        ),
        (
            "get_perp_dex_status",
            vec![("dex", "")],
            json!({"type": "perpDexStatus", "dex": ""}),
        ),
        (
            "get_all_perp_metas",
            vec![],
            json!({"type": "allPerpMetas"}),
        ),
        (
            "get_perp_annotation",
            vec![("product_symbol", "[\"ETH\",1]")],
            json!({"type": "perpAnnotation", "coin": "ETH"}),
        ),
        (
            "get_perp_categories",
            vec![],
            json!({"type": "perpCategories"}),
        ),
        (
            "get_perp_concise_annotations",
            vec![],
            json!({"type": "perpConciseAnnotations"}),
        ),
        (
            "get_token_details",
            vec![("tokenId", "0x00000000000000000000000000000000")],
            json!({"type": "tokenDetails", "tokenId": "0x00000000000000000000000000000000"}),
        ),
        (
            "get_user_dex_abstraction",
            vec![("user", "0xabababababababababababababababababababab")],
            json!({"type": "userDexAbstraction", "user": "0xabababababababababababababababababababab"}),
        ),
        (
            "get_user_abstraction",
            vec![("user", "0xabababababababababababababababababababab")],
            json!({"type": "userAbstraction", "user": "0xabababababababababababababababababababab"}),
        ),
        (
            "get_borrow_lend_user_state",
            vec![("user", "0xabababababababababababababababababababab")],
            json!({"type": "borrowLendUserState", "user": "0xabababababababababababababababababababab"}),
        ),
        (
            "get_borrow_lend_reserve_state",
            vec![("token", "0")],
            json!({"type": "borrowLendReserveState", "token": 0}),
        ),
        (
            "get_all_borrow_lend_reserve_states",
            vec![],
            json!({"type": "allBorrowLendReserveStates"}),
        ),
        (
            "get_predicted_fundings",
            vec![],
            json!({"type":"predictedFundings"}),
        ),
        (
            "frontend_open_orders",
            vec![("user", USER), ("dex", "xyz")],
            json!({"type":"frontendOpenOrders","user":USER_LOWER,"dex":"xyz"}),
        ),
        ("get_meta", vec![], json!({"type": "meta"})),
        (
            "get_meta",
            vec![("dex", "xyz")],
            json!({"type": "meta", "dex": "xyz"}),
        ),
        ("get_spot_meta", vec![], json!({"type": "spotMeta"})),
        (
            "get_spot_meta_and_asset_ctxs",
            vec![],
            json!({"type": "spotMetaAndAssetCtxs"}),
        ),
        (
            "get_meta_and_asset_ctxs",
            vec![],
            json!({"type": "metaAndAssetCtxs"}),
        ),
        (
            "get_l2book",
            vec![("product_symbol", "ETH")],
            json!({"type": "l2Book", "coin": "ETH"}),
        ),
        (
            "get_funding_rate_history",
            vec![
                ("product_symbol", "BTC"),
                ("startTime", "1000"),
                ("endTime", "2000"),
            ],
            json!({"type": "fundingHistory", "coin": "BTC", "startTime": 1000, "endTime": 2000}),
        ),
        (
            "get_funding_rate_history",
            vec![("product_symbol", "BTC-USD-SWAP"), ("startTime", "1000")],
            json!({"type": "fundingHistory", "coin": "BTC", "startTime": 1000}),
        ),
        (
            "get_spot_fee_rates",
            vec![("user", USER)],
            json!({"type": "userFees", "user": USER_LOWER}),
        ),
        (
            "get_futures_fee_rates",
            vec![("user", USER)],
            json!({"type": "userFees", "user": USER_LOWER}),
        ),
        (
            "clearinghouse_state",
            vec![("user", USER)],
            json!({"type": "clearinghouseState", "user": USER_LOWER}),
        ),
        (
            "clearinghouse_state",
            vec![("user", USER), ("dex", "xyz")],
            json!({"type": "clearinghouseState", "user": USER_LOWER, "dex": "xyz"}),
        ),
        (
            "spot_clearinghouse_state",
            vec![("user", USER)],
            json!({"type": "spotClearinghouseState", "user": USER_LOWER}),
        ),
        (
            "open_orders",
            vec![("user", USER)],
            json!({"type": "openOrders", "user": USER_LOWER}),
        ),
        (
            "open_orders",
            vec![("user", USER), ("dex", "xyz")],
            json!({"type": "openOrders", "user": USER_LOWER, "dex": "xyz"}),
        ),
        (
            "user_fills",
            vec![("user", USER)],
            json!({"type": "userFills", "user": USER_LOWER}),
        ),
        (
            "user_fills",
            vec![("user", USER), ("aggregateByTime", "true")],
            json!({"type": "userFills", "user": USER_LOWER, "aggregateByTime": true}),
        ),
        (
            "user_fills",
            vec![("user", USER), ("aggregateByTime", "false")],
            json!({"type": "userFills", "user": USER_LOWER}),
        ),
        (
            "user_fills_by_time",
            vec![("user", USER), ("startTime", "1000")],
            json!({"type": "userFillsByTime", "user": USER_LOWER, "startTime": 1000}),
        ),
        (
            "user_funding",
            vec![("user", USER), ("startTime", "1000"), ("endTime", "2000")],
            json!({"type": "userFunding", "user": USER_LOWER, "startTime": 1000, "endTime": 2000}),
        ),
        (
            "user_non_funding_ledger_updates",
            vec![("user", USER), ("startTime", "1000")],
            json!({"type": "userNonFundingLedgerUpdates", "user": USER_LOWER, "startTime": 1000}),
        ),
        (
            "user_rate_limit",
            vec![("user", USER)],
            json!({"type": "userRateLimit", "user": USER_LOWER}),
        ),
        (
            "order_status",
            vec![("user", USER), ("oid", "42")],
            json!({"type": "orderStatus", "user": USER_LOWER, "oid": 42}),
        ),
        (
            "order_status",
            vec![("user", USER), ("oid", CLOID)],
            json!({"type": "orderStatus", "user": USER_LOWER, "oid": CLOID_LOWER}),
        ),
        (
            "historical_orders",
            vec![("user", USER)],
            json!({"type": "historicalOrders", "user": USER_LOWER}),
        ),
        (
            "subaccounts",
            vec![("user", USER)],
            json!({"type": "subAccounts", "user": USER_LOWER}),
        ),
        (
            "user_role",
            vec![("user", USER)],
            json!({"type": "userRole", "user": USER_LOWER}),
        ),
        (
            "portfolio",
            vec![("user", USER)],
            json!({"type": "portfolio", "user": USER_LOWER}),
        ),
        (
            "user_vault_equities",
            vec![("user", USER)],
            json!({"type": "userVaultEquities", "user": USER_LOWER}),
        ),
    ];
    for (method, params, expected) in cases {
        let recorded = public_payload(method, &params);
        assert!(
            recorded.request_line.starts_with("POST /info "),
            "{method}: {}",
            recorded.request_line
        );
        assert_eq!(recorded.body, expected, "{method} {params:?}");
    }
}

#[test]
fn subaccounts_null_response_is_normalized_to_empty_list() {
    let (_, data) = public_payload_with_response("subaccounts", &[("user", USER)], "null");
    assert_eq!(data, json!([]));
}

#[test]
fn info_requests_reject_invalid_parameters_before_network() {
    let client = HyperliquidClient::with_endpoint(
        false,
        None,
        None,
        Duration::from_secs(1),
        "http://127.0.0.1:1".to_string(),
    )
    .expect("client");
    for (method, params) in [
        ("get_spot_meta", vec![("dex", "xyz")]),
        (
            "get_funding_rate_history",
            vec![
                ("product_symbol", "BTC"),
                ("startTime", "2000"),
                ("endTime", "1000"),
            ],
        ),
        ("order_status", vec![("user", USER), ("oid", "abc")]),
        ("user_role", vec![("user", "0x1234")]),
        ("user_funding", vec![("user", USER)]),
        ("unknown_info_method", vec![]),
    ] {
        let client = client.clone();
        let params = pairs(&params);
        let result =
            crate::http::block_on(async move { client.public_request(method, params).await });
        assert!(result.is_err(), "{method} should be rejected");
    }
}

#[test]
fn exchange_actions_match_official_wire_format() {
    let cases: Vec<(&'static str, Vec<(&str, &str)>, Value)> = vec![
        (
            "cancel_order",
            vec![("product_symbol", ETH), ("oid", "77")],
            json!({"type": "cancel", "cancels": [{"a": 1, "o": 77}]}),
        ),
        (
            "cancel_order_by_cloid",
            vec![("product_symbol", ETH), ("cloid", CLOID)],
            json!({"type": "cancelByCloid", "cancels": [{"asset": 1, "cloid": CLOID_LOWER}]}),
        ),
        (
            "modify_order",
            vec![
                ("oid", "77"),
                ("product_symbol", ETH),
                ("isBuy", "false"),
                ("price", "2500.5"),
                ("size", "0.2"),
                ("reduceOnly", "true"),
                ("tif", "Alo"),
                ("cloid", CLOID),
            ],
            json!({
                "type": "modify",
                "oid": 77,
                "order": {
                    "a": 1, "b": false, "p": "2500.5", "s": "0.2", "r": true,
                    "t": {"limit": {"tif": "Alo"}},
                    "c": CLOID_LOWER
                }
            }),
        ),
        (
            "modify_order",
            vec![
                ("oid", CLOID),
                ("product_symbol", ETH),
                ("isBuy", "true"),
                ("price", "2400"),
                ("size", "0.2"),
                ("reduceOnly", "false"),
                ("tif", "Gtc"),
            ],
            json!({
                "type": "modify",
                "oid": CLOID_LOWER,
                "order": {
                    "a": 1, "b": true, "p": "2400", "s": "0.2", "r": false,
                    "t": {"limit": {"tif": "Gtc"}}
                }
            }),
        ),
        (
            "update_leverage",
            vec![
                ("product_symbol", ETH),
                ("isCross", "false"),
                ("leverage", "5"),
            ],
            json!({"type": "updateLeverage", "asset": 1, "isCross": false, "leverage": 5}),
        ),
        (
            "update_isolate_margin",
            vec![
                ("product_symbol", ETH),
                ("isBuy", "true"),
                ("ntli", "-1000000"),
            ],
            json!({"type": "updateIsolatedMargin", "asset": 1, "isBuy": true, "ntli": -1000000}),
        ),
        (
            "place_twap_order",
            vec![
                ("product_symbol", ETH),
                ("isBuy", "true"),
                ("size", "1.5"),
                ("reduceOnly", "false"),
                ("minutes", "30"),
                ("randomize", "true"),
            ],
            json!({
                "type": "twapOrder",
                "twap": {"a": 1, "b": true, "s": "1.5", "r": false, "m": 30, "t": true}
            }),
        ),
        (
            "cancel_twap_order",
            vec![("product_symbol", ETH), ("twap_id", "9")],
            json!({"type": "twapCancel", "a": 1, "t": 9}),
        ),
        (
            "place_future_limit_order",
            vec![
                ("product_symbol", ETH),
                ("isBuy", "true"),
                ("price", "2000"),
                ("size", "0.1"),
                ("tif", "Gtc"),
            ],
            json!({
                "type": "order",
                "orders": [{"a": 1, "b": true, "p": "2000", "s": "0.1", "r": false,
                            "t": {"limit": {"tif": "Gtc"}}}],
                "grouping": "na"
            }),
        ),
        (
            "place_future_limit_buy_order",
            vec![
                ("product_symbol", ETH),
                ("price", "2000"),
                ("size", "0.1"),
                ("tif", "Ioc"),
            ],
            json!({
                "type": "order",
                "orders": [{"a": 1, "b": true, "p": "2000", "s": "0.1", "r": false,
                            "t": {"limit": {"tif": "Ioc"}}}],
                "grouping": "na"
            }),
        ),
        (
            "place_future_limit_sell_order",
            vec![
                ("product_symbol", ETH),
                ("price", "2100"),
                ("size", "0.1"),
                ("tif", "Alo"),
                ("cloid", CLOID),
            ],
            json!({
                "type": "order",
                "orders": [{"a": 1, "b": false, "p": "2100", "s": "0.1", "r": false,
                            "t": {"limit": {"tif": "Alo"}}, "c": CLOID_LOWER}],
                "grouping": "na"
            }),
        ),
        (
            "place_order",
            vec![
                ("product_symbol", ETH),
                ("isBuy", "false"),
                ("price", "1800"),
                ("size", "0.1"),
                ("reduceOnly", "true"),
                ("triggerPx", "1850"),
                ("tpsl", "sl"),
                ("isMarket", "true"),
                ("grouping", "positionTpsl"),
            ],
            json!({
                "type": "order",
                "orders": [{"a": 1, "b": false, "p": "1800", "s": "0.1", "r": true,
                            "t": {"trigger": {"isMarket": true, "triggerPx": "1850", "tpsl": "sl"}}}],
                "grouping": "positionTpsl"
            }),
        ),
    ];
    for (method, params, expected) in cases {
        let recorded = private_payload(method, &params);
        assert_eq!(recorded.body["action"], expected, "{method} {params:?}");
        assert!(recorded.body.get("vaultAddress").is_none(), "{method}");
    }
}

#[test]
fn exchange_actions_forward_vault_and_expiry() {
    let recorded = private_payload(
        "cancel_order",
        &[
            ("product_symbol", "[\"BTC\",0]"),
            ("oid", "1"),
            ("vaultAddress", "0xBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB"),
            ("expiresAfter", "1700000001000"),
        ],
    );
    assert_eq!(
        recorded.body["vaultAddress"],
        "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    );
    assert_eq!(recorded.body["expiresAfter"], 1_700_000_001_000u64);
}

#[test]
fn transfer_between_dexes_uses_agent_send_asset_with_matching_nonce() {
    let recorded = private_payload(
        "transfer_between_dexes",
        &[
            ("sourceDex", ""),
            ("destinationDex", "xyz"),
            ("token", "USDC"),
            ("amount", "12.5"),
        ],
    );
    let action = &recorded.body["action"];
    assert_eq!(action["type"], "agentSendAsset");
    assert_eq!(action["destination"], WALLET);
    assert_eq!(action["sourceDex"], "");
    assert_eq!(action["destinationDex"], "xyz");
    assert_eq!(action["token"], "USDC");
    assert_eq!(action["amount"], "12.5");
    assert_eq!(action["fromSubAccount"], "");
    assert_eq!(action["nonce"], recorded.body["nonce"]);
}

#[test]
fn exchange_actions_reject_invalid_parameters_before_network() {
    let client = signing_client("http://127.0.0.1:1".to_string());
    for (method, params) in [
        (
            "update_leverage",
            vec![
                ("product_symbol", ETH),
                ("isCross", "true"),
                ("leverage", "0"),
            ],
        ),
        (
            "place_twap_order",
            vec![
                ("product_symbol", ETH),
                ("isBuy", "true"),
                ("size", "1"),
                ("reduceOnly", "false"),
                ("minutes", "0"),
                ("randomize", "false"),
            ],
        ),
        (
            "cancel_order_by_cloid",
            vec![("product_symbol", ETH), ("cloid", "0x12")],
        ),
        (
            "cancel_order",
            vec![("product_symbol", ETH), ("oid", "1"), ("unexpected", "1")],
        ),
        (
            "place_order",
            vec![
                ("product_symbol", ETH),
                ("isBuy", "true"),
                ("price", "1"),
                ("size", "1"),
                ("reduceOnly", "false"),
                ("tif", "Gtc"),
                ("grouping", "bad"),
            ],
        ),
        (
            "place_order",
            vec![
                ("product_symbol", ETH),
                ("isBuy", "true"),
                ("price", "1"),
                ("size", "1"),
                ("reduceOnly", "false"),
                ("tif", "Gtc"),
                ("builder_address", WALLET),
            ],
        ),
        (
            "transfer_between_dexes",
            vec![
                ("sourceDex", "xyz"),
                ("destinationDex", "xyz"),
                ("token", "USDC"),
                ("amount", "1"),
            ],
        ),
        ("schedule_cancel", vec![("time", "1")]),
        ("unknown_exchange_method", vec![]),
    ] {
        let client = client.clone();
        let params = pairs(&params);
        let result =
            crate::http::block_on(async move { client.private_request(method, params).await });
        assert!(result.is_err(), "{method} should be rejected");
    }
}

#[test]
fn signed_actions_require_credentials() {
    let client = HyperliquidClient::public(false, Duration::from_secs(1)).expect("client");
    let result = crate::http::block_on(async move {
        client
            .private_request(
                "cancel_order",
                pairs(&[("product_symbol", "[\"BTC\",0]"), ("oid", "1")]),
            )
            .await
    });
    assert!(result.is_err());
}

/// Serves one response per request, in order, and returns the parsed requests.
fn serve_sequence(responses: Vec<&'static str>) -> (String, JoinHandle<Vec<Recorded>>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    listener.set_nonblocking(true).expect("nonblocking");
    let address = listener.local_addr().expect("address");
    let handle = thread::spawn(move || {
        let mut recorded = Vec::new();
        for response_body in responses {
            let deadline = Instant::now() + Duration::from_secs(5);
            let (mut stream, _) = loop {
                match listener.accept() {
                    Ok(connection) => break connection,
                    Err(error) if error.kind() == ErrorKind::WouldBlock => {
                        assert!(Instant::now() < deadline, "no request received");
                        thread::sleep(Duration::from_millis(5));
                    }
                    Err(error) => panic!("accept failed: {error}"),
                }
            };
            stream.set_nonblocking(false).expect("blocking stream");
            stream
                .set_read_timeout(Some(Duration::from_secs(2)))
                .expect("read timeout");
            let mut raw = Vec::new();
            let mut buffer = [0u8; 4096];
            loop {
                let size = stream.read(&mut buffer).expect("read");
                assert!(size > 0, "connection closed before body");
                raw.extend_from_slice(&buffer[..size]);
                let text = String::from_utf8_lossy(&raw).into_owned();
                if let Some((head, body)) = text.split_once("\r\n\r\n") {
                    let length = head
                        .lines()
                        .find_map(|line| {
                            line.to_ascii_lowercase()
                                .strip_prefix("content-length: ")
                                .and_then(|value| value.trim().parse::<usize>().ok())
                        })
                        .unwrap_or(0);
                    if body.len() >= length {
                        break;
                    }
                }
            }
            let response = format!(
                "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                response_body.len(),
                response_body
            );
            stream.write_all(response.as_bytes()).expect("write");
            let text = String::from_utf8_lossy(&raw).into_owned();
            let (head, body) = text.split_once("\r\n\r\n").expect("http request");
            recorded.push(Recorded {
                request_line: head.lines().next().unwrap_or_default().to_string(),
                body: serde_json::from_str(body).expect("json body"),
            });
        }
        recorded
    });
    (format!("http://{address}"), handle)
}

fn market_order_requests(
    method: &'static str,
    params: &[(&str, &str)],
    meta_response: &'static str,
) -> Vec<Recorded> {
    let (base_url, server) = serve_sequence(vec![
        meta_response,
        "{\"status\":\"ok\",\"response\":{\"type\":\"order\"}}",
    ]);
    let client = signing_client(base_url);
    let params = pairs(params);
    crate::http::block_on(async move { client.private_request(method, params).await })
        .expect(method);
    server.join().expect("server")
}

const BTC_META: &str =
    "[{\"universe\":[{\"name\":\"BTC\",\"szDecimals\":5}]},[{\"midPx\":\"100.0\"}]]";

#[test]
fn additional_info_requests_match_official_request_types() {
    let cases: Vec<(&'static str, Vec<(&str, &str)>, Value)> = vec![
        ("get_perp_dexs", vec![], json!({"type": "perpDexs"})),
        (
            "get_meta_and_asset_ctxs",
            vec![("dex", "xyz")],
            json!({"type": "metaAndAssetCtxs", "dex": "xyz"}),
        ),
        (
            "get_l2book",
            vec![
                ("product_symbol", "ETH"),
                ("nSigFigs", "5"),
                ("mantissa", "2"),
            ],
            json!({"type": "l2Book", "coin": "ETH", "nSigFigs": 5, "mantissa": 2}),
        ),
        (
            "get_l2book",
            vec![("product_symbol", "@107"), ("nSigFigs", "3")],
            json!({"type": "l2Book", "coin": "@107", "nSigFigs": 3}),
        ),
        (
            "get_candle_snapshot",
            vec![
                ("product_symbol", "BTC"),
                ("interval", "15m"),
                ("startTime", "1000"),
                ("endTime", "2000"),
            ],
            json!({
                "type": "candleSnapshot",
                "req": {"coin": "BTC", "interval": "15m", "startTime": 1000, "endTime": 2000}
            }),
        ),
        (
            "get_candle_snapshot",
            vec![
                ("product_symbol", "xyz:ABC"),
                ("interval", "1M"),
                ("startTime", "1000"),
                ("endTime", "1000"),
            ],
            json!({
                "type": "candleSnapshot",
                "req": {"coin": "xyz:ABC", "interval": "1M", "startTime": 1000, "endTime": 1000}
            }),
        ),
        (
            "user_fills_by_time",
            vec![
                ("user", USER),
                ("startTime", "1000"),
                ("endTime", "2000"),
                ("aggregateByTime", "true"),
            ],
            json!({
                "type": "userFillsByTime", "user": USER_LOWER,
                "startTime": 1000, "endTime": 2000, "aggregateByTime": true
            }),
        ),
        (
            "user_non_funding_ledger_updates",
            vec![("user", USER), ("startTime", "1000"), ("endTime", "2000")],
            json!({
                "type": "userNonFundingLedgerUpdates", "user": USER_LOWER,
                "startTime": 1000, "endTime": 2000
            }),
        ),
    ];
    for (method, params, expected) in cases {
        let recorded = public_payload(method, &params);
        assert!(recorded.request_line.starts_with("POST /info "), "{method}");
        assert_eq!(recorded.body, expected, "{method} {params:?}");
    }
}

#[test]
fn additional_info_requests_reject_invalid_parameters_before_network() {
    let client = HyperliquidClient::with_endpoint(
        false,
        None,
        None,
        Duration::from_secs(1),
        "http://127.0.0.1:1".to_string(),
    )
    .expect("client");
    for (method, params) in [
        (
            "get_l2book",
            vec![("product_symbol", "BTC"), ("nSigFigs", "1")],
        ),
        (
            "get_l2book",
            vec![
                ("product_symbol", "BTC"),
                ("nSigFigs", "4"),
                ("mantissa", "2"),
            ],
        ),
        (
            "get_l2book",
            vec![
                ("product_symbol", "BTC"),
                ("nSigFigs", "5"),
                ("mantissa", "3"),
            ],
        ),
        (
            "get_candle_snapshot",
            vec![
                ("product_symbol", "BTC"),
                ("interval", "2d"),
                ("startTime", "1"),
                ("endTime", "2"),
            ],
        ),
        (
            "get_candle_snapshot",
            vec![
                ("product_symbol", "BTC"),
                ("interval", "1h"),
                ("startTime", "2"),
                ("endTime", "1"),
            ],
        ),
        (
            "get_candle_snapshot",
            vec![
                ("product_symbol", "BTC"),
                ("interval", "1h"),
                ("startTime", "1"),
            ],
        ),
        ("get_perp_dexs", vec![("dex", "xyz")]),
        ("clearinghouse_state", vec![("user", USER), ("dex", "")]),
        ("get_l2book", vec![("product_symbol", "BTC-USDC-SPOT")]),
    ] {
        let client = client.clone();
        let params = pairs(&params);
        let result =
            crate::http::block_on(async move { client.public_request(method, params).await });
        assert!(result.is_err(), "{method} should be rejected");
    }
}

#[test]
fn schedule_cancel_and_batch_modify_match_official_wire_format() {
    let recorded = private_payload("noop", &[("nonce", "1700000000123")]);
    assert_eq!(recorded.body["action"], json!({"type":"noop"}));
    assert_eq!(recorded.body["nonce"], 1700000000123_u64);
    let recorded = private_payload("schedule_cancel", &[]);
    assert_eq!(recorded.body["action"], json!({"type": "scheduleCancel"}));

    let time = crate::exchange::unix_timestamp_ms().expect("now") + 60_000;
    let time_text = time.to_string();
    let recorded = private_payload("schedule_cancel", &[("time", time_text.as_str())]);
    assert_eq!(
        recorded.body["action"],
        json!({"type": "scheduleCancel", "time": time})
    );

    let modifies = json!([
        {
            "oid": 42,
            "order": {"a": 1, "b": true, "p": "2000", "s": "0.1", "r": false,
                      "t": {"limit": {"tif": "Gtc"}}, "c": CLOID}
        },
        {
            "order": {"t": {"trigger": {"tpsl": "tp", "triggerPx": "2600", "isMarket": false}},
                      "r": true, "s": "0.1", "p": "2600", "b": false, "a": 1},
            "oid": CLOID
        }
    ])
    .to_string();
    let recorded = private_payload("modify_batch_orders", &[("modifies", modifies.as_str())]);
    assert_eq!(
        recorded.body["action"],
        json!({
            "type": "batchModify",
            "modifies": [
                {"oid": 42, "order": {"a": 1, "b": true, "p": "2000", "s": "0.1", "r": false,
                                      "t": {"limit": {"tif": "Gtc"}}, "c": CLOID_LOWER}},
                {"oid": CLOID_LOWER, "order": {"a": 1, "b": false, "p": "2600", "s": "0.1",
                                               "r": true, "t": {"trigger": {
                                                   "isMarket": false, "triggerPx": "2600",
                                                   "tpsl": "tp"}}}}
            ]
        })
    );
}

#[test]
fn batch_modify_rejects_malformed_modifies_before_network() {
    let client = signing_client("http://127.0.0.1:1".to_string());
    let limit = r#"{"limit":{"tif":"Gtc"}}"#;
    let valid_order = format!(r#"{{"a":1,"b":true,"p":"1","s":"1","r":false,"t":{limit}}}"#);
    let cases = vec![
        "[]".to_string(),
        "{}".to_string(),
        r#"[{"oid":1}]"#.to_string(),
        r#"[{"oid":1,"order":{"a":1,"b":true,"p":"1","s":"1","r":false}}]"#.to_string(),
        format!(
            r#"[{{"oid":1,"order":{}}}]"#,
            valid_order.replace(r#""p":"1""#, r#""p":"0""#)
        ),
        format!(
            r#"[{{"oid":1,"order":{}}}]"#,
            valid_order.replace("Gtc", "Fok")
        ),
        format!(r#"[{{"oid":-1,"order":{valid_order}}}]"#),
        format!(r#"[{{"oid":1,"extra":1,"order":{valid_order}}}]"#),
    ];
    for modifies in cases {
        let client = client.clone();
        let params = pairs(&[("modifies", modifies.as_str())]);
        let result = crate::http::block_on(async move {
            client.private_request("modify_batch_orders", params).await
        });
        assert!(result.is_err(), "{modifies} should be rejected");
    }
}

#[test]
fn orders_forward_builder_vault_and_trigger_fields() {
    let recorded = private_payload(
        "place_order",
        &[
            ("product_symbol", ETH),
            ("isBuy", "true"),
            ("price", "2000"),
            ("size", "0.5"),
            ("reduceOnly", "false"),
            ("tif", "Gtc"),
            ("cloid", CLOID),
            ("grouping", "normalTpsl"),
            ("builder_address", USER),
            ("fee_ten_bp", "25"),
            ("vaultAddress", USER),
            ("expiresAfter", "1700000001000"),
        ],
    );
    assert_eq!(
        recorded.body["action"],
        json!({
            "type": "order",
            "orders": [{"a": 1, "b": true, "p": "2000", "s": "0.5", "r": false,
                        "t": {"limit": {"tif": "Gtc"}}, "c": CLOID_LOWER}],
            "grouping": "normalTpsl",
            "builder": {"b": USER_LOWER, "f": 25}
        })
    );
    assert_eq!(recorded.body["vaultAddress"], USER_LOWER);
    assert_eq!(recorded.body["expiresAfter"], 1_700_000_001_000u64);

    let recorded = private_payload(
        "modify_order",
        &[
            ("oid", "5"),
            ("product_symbol", ETH),
            ("isBuy", "true"),
            ("price", "2100"),
            ("size", "0.5"),
            ("reduceOnly", "true"),
            ("triggerPx", "2050"),
            ("tpsl", "tp"),
        ],
    );
    assert_eq!(
        recorded.body["action"]["order"]["t"],
        json!({"trigger": {"isMarket": false, "triggerPx": "2050", "tpsl": "tp"}})
    );
}

#[test]
fn market_orders_price_from_mid_with_slippage_and_ioc() {
    for (method, params, expected_price, expected_buy, expected_reduce) in [
        (
            "place_future_market_buy_order",
            vec![("product_symbol", "[\"BTC\",0]"), ("size", "0.01")],
            "105",
            true,
            false,
        ),
        (
            "place_future_market_sell_order",
            vec![("product_symbol", "[\"BTC\",0]"), ("size", "0.01")],
            "95",
            false,
            false,
        ),
        (
            "place_future_market_order",
            vec![
                ("product_symbol", "[\"BTC\",0]"),
                ("isBuy", "false"),
                ("size", "0.01"),
                ("slippage", "0.01"),
                ("reduceOnly", "true"),
                ("cloid", CLOID),
            ],
            "99",
            false,
            true,
        ),
    ] {
        let recorded = market_order_requests(method, &params, BTC_META);
        assert!(
            recorded[0].request_line.starts_with("POST /info "),
            "{method}"
        );
        assert_eq!(
            recorded[0].body,
            json!({"type": "metaAndAssetCtxs"}),
            "{method}"
        );
        assert!(
            recorded[1].request_line.starts_with("POST /exchange "),
            "{method}"
        );
        let order = &recorded[1].body["action"]["orders"][0];
        assert_eq!(order["a"], 0, "{method}");
        assert_eq!(order["b"], expected_buy, "{method}");
        assert_eq!(order["p"], expected_price, "{method}");
        assert_eq!(order["s"], "0.01", "{method}");
        assert_eq!(order["r"], expected_reduce, "{method}");
        assert_eq!(order["t"], json!({"limit": {"tif": "Ioc"}}), "{method}");
        assert_eq!(recorded[1].body["action"]["grouping"], "na", "{method}");
    }
}

#[test]
fn market_trigger_orders_use_market_trigger_type() {
    let recorded = market_order_requests(
        "place_future_market_sell_order",
        &[
            ("product_symbol", "[\"BTC\",0]"),
            ("size", "0.01"),
            ("triggerPx", "90"),
            ("tpsl", "sl"),
            ("reduceOnly", "true"),
        ],
        BTC_META,
    );
    let order = &recorded[1].body["action"]["orders"][0];
    assert_eq!(
        order["t"],
        json!({"trigger": {"isMarket": true, "triggerPx": "90", "tpsl": "sl"}})
    );
    assert_eq!(order["p"], "95");
    assert_eq!(order["r"], true);
}

#[test]
fn builder_dex_market_orders_query_the_matching_dex() {
    let recorded = market_order_requests(
        "place_future_market_buy_order",
        &[("product_symbol", "[\"xyz:ABC\",110000]"), ("size", "1")],
        "[{\"universe\":[{\"name\":\"xyz:ABC\",\"szDecimals\":2}]},[{\"midPx\":\"12.3456\"}]]",
    );
    assert_eq!(
        recorded[0].body,
        json!({"type": "metaAndAssetCtxs", "dex": "xyz"})
    );
    let order = &recorded[1].body["action"]["orders"][0];
    assert_eq!(order["a"], 110000);
    // 12.3456 * 1.05 = 12.96288 -> rounded up to 5 significant figures, max 4 decimals.
    assert_eq!(order["p"], "12.963");
}

#[test]
fn market_orders_reject_invalid_slippage_before_network() {
    let client = signing_client("http://127.0.0.1:1".to_string());
    for slippage in ["1", "-0.1", "nan", "abc"] {
        let client = client.clone();
        let params = pairs(&[
            ("product_symbol", "[\"BTC\",0]"),
            ("size", "1"),
            ("slippage", slippage),
        ]);
        let result = crate::http::block_on(async move {
            client
                .private_request("place_future_market_buy_order", params)
                .await
        });
        assert!(result.is_err(), "slippage {slippage} should be rejected");
    }
}

#[test]
fn batch_orders_send_every_order_in_one_action_with_grouping() {
    // hyperliquid-python-sdk bulk_orders: {"type":"order","orders":[...],"grouping":g}.
    let orders = json!([
        {"product_symbol": ETH, "isBuy": true, "price": "2500", "size": "0.1", "tif": "Gtc", "cloid": CLOID},
        {"product_symbol": ETH, "isBuy": false, "price": "2700", "size": "0.1", "reduceOnly": true,
         "triggerPx": "2700", "tpsl": "tp", "isMarket": true},
        {"product_symbol": ETH, "isBuy": false, "price": "2300", "size": "0.1", "reduceOnly": true,
         "triggerPx": "2300", "tpsl": "sl", "isMarket": true, "cloid": null}
    ])
    .to_string();
    let recorded = private_payload(
        "place_batch_orders",
        &[
            ("orders", &orders),
            ("grouping", "normalTpsl"),
            ("builder_address", WALLET),
            ("fee_ten_bp", "10"),
            ("expiresAfter", "1900000000000"),
        ],
    );
    assert_eq!(
        recorded.body["action"],
        json!({
            "type": "order",
            "orders": [
                {"a": 1, "b": true, "p": "2500", "s": "0.1", "r": false,
                 "t": {"limit": {"tif": "Gtc"}}, "c": CLOID_LOWER},
                {"a": 1, "b": false, "p": "2700", "s": "0.1", "r": true,
                 "t": {"trigger": {"isMarket": true, "triggerPx": "2700", "tpsl": "tp"}}},
                {"a": 1, "b": false, "p": "2300", "s": "0.1", "r": true,
                 "t": {"trigger": {"isMarket": true, "triggerPx": "2300", "tpsl": "sl"}}}
            ],
            "grouping": "normalTpsl",
            "builder": {"b": WALLET, "f": 10}
        })
    );
    assert_eq!(recorded.body["expiresAfter"], 1_900_000_000_000_u64);

    let orders = json!([
        {"product_symbol": "[\"BTC\",0]", "isBuy": true, "price": "100", "size": "1", "tif": "Ioc"}
    ])
    .to_string();
    let recorded = private_payload("place_batch_orders", &[("orders", &orders)]);
    assert_eq!(recorded.body["action"]["grouping"], "na");
    assert_eq!(recorded.body["action"]["orders"][0]["a"], 0);
}

#[test]
fn batch_cancels_send_every_cancel_in_one_action() {
    // SDK bulk_cancel / bulk_cancel_by_cloid wire formats.
    let cancels = json!([
        {"product_symbol": ETH, "oid": 77},
        {"product_symbol": "[\"BTC\",0]", "oid": "78"}
    ])
    .to_string();
    let recorded = private_payload(
        "cancel_batch_orders",
        &[("cancels", &cancels), ("vaultAddress", USER)],
    );
    assert_eq!(
        recorded.body["action"],
        json!({"type": "cancel", "cancels": [{"a": 1, "o": 77}, {"a": 0, "o": 78}]})
    );
    assert_eq!(recorded.body["vaultAddress"], USER_LOWER);

    let cancels = json!([
        {"product_symbol": ETH, "cloid": CLOID},
        {"product_symbol": "[\"@107\",10107]", "cloid": CLOID_LOWER}
    ])
    .to_string();
    let recorded = private_payload("cancel_batch_orders_by_cloid", &[("cancels", &cancels)]);
    assert_eq!(
        recorded.body["action"],
        json!({"type": "cancelByCloid", "cancels": [
            {"asset": 1, "cloid": CLOID_LOWER},
            {"asset": 10107, "cloid": CLOID_LOWER}
        ]})
    );
}

#[test]
fn batch_actions_reject_malformed_items_before_network() {
    let client = signing_client("http://127.0.0.1:1".to_string());
    let order = |extra: Value| {
        let mut order =
            json!({"product_symbol": ETH, "isBuy": true, "price": "1", "size": "1", "tif": "Gtc"});
        for (key, value) in extra.as_object().expect("object") {
            order[key] = value.clone();
        }
        json!([order]).to_string()
    };
    for (method, params) in [
        ("place_batch_orders", vec![("orders", "[]".to_string())]),
        ("place_batch_orders", vec![("orders", "{}".to_string())]),
        ("place_batch_orders", vec![("orders", "[1]".to_string())]),
        (
            "place_batch_orders",
            vec![("orders", order(json!({"price": 1.5})))],
        ),
        (
            "place_batch_orders",
            vec![("orders", order(json!({"grouping": "na"})))],
        ),
        (
            "place_batch_orders",
            vec![("orders", order(json!({"tif": null})))],
        ),
        (
            "place_batch_orders",
            vec![("orders", order(json!({})))]
                .into_iter()
                .chain([("grouping", "bad".to_string())])
                .collect(),
        ),
        (
            "place_batch_orders",
            vec![
                ("orders", order(json!({}))),
                ("fee_ten_bp", "1".to_string()),
            ],
        ),
        ("cancel_batch_orders", vec![("cancels", "[]".to_string())]),
        (
            "cancel_batch_orders",
            vec![("cancels", json!([{"product_symbol": ETH}]).to_string())],
        ),
        (
            "cancel_batch_orders",
            vec![(
                "cancels",
                json!([{"product_symbol": ETH, "oid": 1, "cloid": CLOID}]).to_string(),
            )],
        ),
        (
            "cancel_batch_orders_by_cloid",
            vec![(
                "cancels",
                json!([{"product_symbol": ETH, "cloid": "0x12"}]).to_string(),
            )],
        ),
    ] {
        let client = client.clone();
        let params = params
            .into_iter()
            .map(|(key, value)| (key.to_string(), value))
            .collect::<Vec<_>>();
        let result =
            crate::http::block_on(async move { client.private_request(method, params).await });
        assert!(result.is_err(), "{method} should be rejected");
    }
}

#[test]
fn update_isolated_margin_alias_matches_legacy_name() {
    let params = [
        ("product_symbol", ETH),
        ("isBuy", "true"),
        ("ntli", "-5000000"),
    ];
    let expected =
        json!({"type": "updateIsolatedMargin", "asset": 1, "isBuy": true, "ntli": -5000000});
    assert_eq!(
        private_payload("update_isolated_margin", &params).body["action"],
        expected
    );
    assert_eq!(
        private_payload("update_isolate_margin", &params).body["action"],
        expected
    );
}

const SPOT_META: &str = "[{\"tokens\":[{\"name\":\"USDC\",\"szDecimals\":8,\"index\":0},{\"name\":\"PURR\",\"szDecimals\":0,\"index\":1},{\"name\":\"HYPE\",\"szDecimals\":2,\"index\":150}],\"universe\":[{\"name\":\"PURR/USDC\",\"tokens\":[1,0],\"index\":0},{\"name\":\"@107\",\"tokens\":[150,0],\"index\":107}]},[{\"coin\":\"PURR/USDC\",\"midPx\":\"0.209265\"},{\"coin\":\"@107\",\"midPx\":\"0.0012345\"}]]";

#[test]
fn spot_market_orders_price_from_spot_mids() {
    // SDK _slippage_price: spot rounds to 5 significant figures and 8 - szDecimals decimals.
    let recorded = market_order_requests(
        "place_future_market_buy_order",
        &[("product_symbol", "[\"@107\",10107]"), ("size", "1")],
        SPOT_META,
    );
    assert_eq!(recorded[0].body, json!({"type": "spotMetaAndAssetCtxs"}));
    let order = &recorded[1].body["action"]["orders"][0];
    assert_eq!(order["a"], 10107);
    // 0.0012345 * 1.05 = 0.00129622 -> 5 sig figs capped at 8 - 2 = 6 decimals (perp rule would give 4).
    assert_eq!(order["p"], "0.001297");
    assert_eq!(order["t"], json!({"limit": {"tif": "Ioc"}}));

    let recorded = market_order_requests(
        "place_future_market_sell_order",
        &[("product_symbol", "[\"PURR/USDC\",10000]"), ("size", "10")],
        SPOT_META,
    );
    assert_eq!(recorded[0].body, json!({"type": "spotMetaAndAssetCtxs"}));
    let order = &recorded[1].body["action"]["orders"][0];
    assert_eq!(order["a"], 10000);
    // 0.209265 * 0.95 = 0.19880175 -> 5 significant figures (spot allows 8 decimals), down.
    assert_eq!(order["p"], "0.1988");
}

#[test]
fn abstraction_queries_preserve_scalar_results() {
    for (method, response, expected) in [
        ("get_user_dex_abstraction", "true", json!(true)),
        (
            "get_user_abstraction",
            "\"portfolioMargin\"",
            json!("portfolioMargin"),
        ),
    ] {
        let (_, data) = public_payload_with_response(method, &[("user", USER)], response);
        assert_eq!(data, expected);
    }
}

#[test]
fn account_actions_preserve_wallet_signature_and_exact_payloads() {
    let reserve = private_payload("reserve_request_weight", &[("weight", "100")]);
    assert_eq!(
        reserve.body["action"],
        json!({"type":"reserveRequestWeight","weight":100})
    );
    let agent = private_payload("set_agent_abstraction", &[("abstraction", "p")]);
    assert_eq!(
        agent.body["action"],
        json!({"type":"agentSetAbstraction","abstraction":"p"})
    );
    let signature =
        json!({"r":format!("0x{}","11".repeat(32)),"s":format!("0x{}","22".repeat(32)),"v":28});
    let signature_text = signature.to_string();
    let user = private_payload(
        "set_user_abstraction",
        &[
            ("user", USER),
            ("abstraction", "portfolioMargin"),
            ("nonce", "1700000000000"),
            ("signature", &signature_text),
            ("signatureChainId", "0xa4b1"),
        ],
    );
    assert_eq!(
        user.body,
        json!({"action":{"type":"userSetAbstraction","hyperliquidChain":"Mainnet","signatureChainId":"0xa4b1","user":USER_LOWER,"abstraction":"portfolioMargin","nonce":1700000000000_u64},"nonce":1700000000000_u64,"signature":signature})
    );
}

#[test]
fn account_risk_queries_and_actions_reject_invalid_parameters() {
    for (public, name, params) in [
        (true, "get_token_details", vec![("tokenId", "0x1234")]),
        (true, "get_borrow_lend_reserve_state", vec![("token", "-1")]),
        (true, "get_user_abstraction", vec![("user", "0x1234")]),
        (false, "reserve_request_weight", vec![("weight", "0")]),
        (
            false,
            "reserve_request_weight",
            vec![("weight", "1"), ("destination", USER)],
        ),
        (
            false,
            "set_agent_abstraction",
            vec![("abstraction", "portfolioMargin")],
        ),
        (
            false,
            "set_agent_abstraction",
            vec![("abstraction", "p"), ("vaultAddress", USER)],
        ),
        (
            false,
            "set_user_abstraction",
            vec![
                ("user", USER),
                ("abstraction", "portfolioMargin"),
                ("nonce", "1"),
                ("signature", "{}"),
                ("signatureChainId", "0xa4b1"),
            ],
        ),
    ] {
        let client = signing_client("http://127.0.0.1:1".into());
        let params = pairs(&params);
        let error = crate::http::block_on(async move {
            if public {
                client.public_request(name, params).await
            } else {
                client.private_request(name, params).await
            }
        })
        .unwrap_err();
        assert!(
            matches!(error, crate::DcexError::InvalidInput(_)),
            "{name}: {error}"
        );
    }
}

#[test]
fn vault_staking_and_abstraction_actions() {
    let body = private_payload(
        "transfer_vault_usd",
        &[
            ("targetVault", "0xabababababababababababababababababababab"),
            ("isDeposit", "true"),
            ("usd", "100"),
        ],
    );
    assert_eq!(body.body["action"]["type"], "vaultTransfer");
    assert!(body.body.get("vaultAddress").is_none());
    let body = private_payload("enable_agent_dex_abstraction", &[]);
    assert_eq!(body.body["action"]["type"], "agentEnableDexAbstraction");
    let body = private_payload(
        "transfer_hip3_liquidator",
        &[("dex", "xyz"), ("ntl", "100"), ("isDeposit", "true")],
    );
    assert_eq!(body.body["action"]["type"], "hip3LiquidatorTransfer");
    let body = private_payload(
        "deposit_staking_signed",
        &[
            ("wei", "100"),
            ("nonce", "100"),
            (
                "signature",
                "{\"r\":\"0x1111111111111111111111111111111111111111111111111111111111111111\",\"s\":\"0x2222222222222222222222222222222222222222222222222222222222222222\",\"v\":27}",
            ),
            ("signatureChainId", "0xa4b1"),
        ],
    );
    assert_eq!(body.body["action"]["type"], "cDeposit");
    let body = private_payload(
        "withdraw_staking_signed",
        &[
            ("wei", "100"),
            ("nonce", "100"),
            (
                "signature",
                "{\"r\":\"0x1111111111111111111111111111111111111111111111111111111111111111\",\"s\":\"0x2222222222222222222222222222222222222222222222222222222222222222\",\"v\":27}",
            ),
            ("signatureChainId", "0xa4b1"),
        ],
    );
    assert_eq!(body.body["action"]["type"], "cWithdraw");
    let body = private_payload(
        "delegate_tokens_signed",
        &[
            ("validator", "0xabababababababababababababababababababab"),
            ("wei", "100"),
            ("isUndelegate", "true"),
            ("nonce", "100"),
            (
                "signature",
                "{\"r\":\"0x1111111111111111111111111111111111111111111111111111111111111111\",\"s\":\"0x2222222222222222222222222222222222222222222222222222222222222222\",\"v\":27}",
            ),
            ("signatureChainId", "0xa4b1"),
        ],
    );
    assert_eq!(body.body["action"]["type"], "tokenDelegate");
    let body = private_payload(
        "set_user_dex_abstraction_signed",
        &[
            ("user", "0xabababababababababababababababababababab"),
            ("enabled", "true"),
            ("nonce", "100"),
            (
                "signature",
                "{\"r\":\"0x1111111111111111111111111111111111111111111111111111111111111111\",\"s\":\"0x2222222222222222222222222222222222222222222222222222222222222222\",\"v\":27}",
            ),
            ("signatureChainId", "0xa4b1"),
        ],
    );
    assert_eq!(body.body["action"]["type"], "userDexAbstraction");
}

#[test]
fn subaccount_actions_use_master_signer() {
    let r = private_payload("create_sub_account", &[("name", "desk")]);
    assert_eq!(r.body["action"]["type"], "createSubAccount");
    assert!(r.body.get("vaultAddress").is_none());
    let r = private_payload(
        "transfer_sub_account_usd",
        &[
            (
                "subAccountUser",
                "0xabababababababababababababababababababab",
            ),
            ("isDeposit", "true"),
            ("usd", "100"),
        ],
    );
    assert_eq!(r.body["action"]["type"], "subAccountTransfer");
    assert!(r.body.get("vaultAddress").is_none());
    let r = private_payload(
        "transfer_sub_account_spot",
        &[
            (
                "subAccountUser",
                "0xabababababababababababababababababababab",
            ),
            ("isDeposit", "true"),
            ("token", "USDC"),
            ("amount", "1"),
        ],
    );
    assert_eq!(r.body["action"]["type"], "subAccountSpotTransfer");
    assert!(r.body.get("vaultAddress").is_none());
}

#[test]
fn agent_approval_preserves_wallet_signature() {
    let body = private_payload(
        "approve_agent_signed",
        &[
            ("agentAddress", "0xabababababababababababababababababababab"),
            ("nonce", "100"),
            (
                "signature",
                "{\"r\":\"0x1111111111111111111111111111111111111111111111111111111111111111\",\"s\":\"0x2222222222222222222222222222222222222222222222222222222222222222\",\"v\":27}",
            ),
            ("signatureChainId", "0xa4b1"),
        ],
    );
    assert_eq!(body.body["action"]["type"], "approveAgent");
    assert!(body.body["action"].get("agentName").is_none());
}

#[test]
fn info_queries_are_independent_of_websocket_subscriptions() {
    let r = public_payload("get_all_mids", &[("dex", "")]);
    assert_eq!(r.body, json!({"type":"allMids","dex":""}));
    let r = public_payload(
        "get_active_asset_data",
        &[("user", USER), ("product_symbol", "BTC-USDC-SWAP")],
    );
    assert_eq!(
        r.body,
        json!({"type":"activeAssetData","user":USER_LOWER,"coin":"BTC"})
    );
    let r = public_payload("get_user_twap_slice_fills", &[("user", USER)]);
    assert_eq!(
        r.body,
        json!({"type":"userTwapSliceFills","user":USER_LOWER})
    );
}
