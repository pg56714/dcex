//! Offline request-building coverage for every Lighter REST route and signed transaction.

use std::collections::BTreeMap;
use std::io::{ErrorKind, Read, Write};
use std::net::TcpListener;
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

use serde_json::{Value, json};

use crate::Result;
use crate::http::block_on;
use crate::product_table::{MarketInfo, ProductTable};

use super::helpers::LighterClient;

const ACCOUNT: u64 = 12;
const API_KEY: u64 = 3;
const CHAIN_ID: u64 = 304;
const TOKEN: &str = "test-token";

#[derive(Debug)]
struct Recorded {
    method: String,
    path: String,
    query: Vec<(String, String)>,
    headers: BTreeMap<String, String>,
    body: String,
}

impl Recorded {
    fn form(&self) -> Vec<(String, String)> {
        url::form_urlencoded::parse(self.body.as_bytes())
            .into_owned()
            .collect()
    }

    fn form_value(&self, key: &str) -> Option<String> {
        self.form()
            .into_iter()
            .find_map(|(candidate, value)| (candidate == key).then_some(value))
    }
}

/// Serves `responses.len()` sequential requests and records each one.
fn serve(responses: Vec<&'static str>) -> (String, JoinHandle<Vec<Recorded>>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    listener.set_nonblocking(true).expect("nonblocking");
    let address = listener.local_addr().expect("address");
    let handle = thread::spawn(move || {
        let mut recorded = Vec::new();
        for response_body in responses {
            let deadline = Instant::now() + Duration::from_secs(10);
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
                .set_read_timeout(Some(Duration::from_secs(10)))
                .expect("read timeout");
            let mut raw = Vec::new();
            let mut buffer = [0u8; 8192];
            loop {
                let size = stream.read(&mut buffer).expect("read");
                assert!(size > 0, "connection closed early");
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
            let mut lines = head.lines();
            let request_line = lines.next().unwrap_or_default();
            let mut parts = request_line.split_whitespace();
            let method = parts.next().unwrap_or_default().to_string();
            let target = parts.next().unwrap_or_default();
            let (path, query) = target.split_once('?').unwrap_or((target, ""));
            let headers = lines
                .filter_map(|line| line.split_once(':'))
                .map(|(key, value)| (key.trim().to_ascii_lowercase(), value.trim().to_string()))
                .collect();
            recorded.push(Recorded {
                method,
                path: path.to_string(),
                query: url::form_urlencoded::parse(query.as_bytes())
                    .into_owned()
                    .collect(),
                headers,
                body: body.to_string(),
            });
        }
        recorded
    });
    (format!("http://{address}"), handle)
}

fn pairs(values: &[(&str, &str)]) -> Vec<(String, String)> {
    values
        .iter()
        .map(|(key, value)| ((*key).to_string(), (*value).to_string()))
        .collect()
}

fn owned(values: &[(&str, &str)]) -> Vec<(String, String)> {
    pairs(values)
}

fn public_client(base_url: String) -> LighterClient {
    LighterClient::with_base_url(Duration::from_secs(10), base_url).expect("client")
}

fn account_client(base_url: String) -> LighterClient {
    LighterClient::with_base_url_and_credentials(
        Duration::from_secs(10),
        base_url,
        Some(ACCOUNT),
        None,
        None,
    )
    .expect("client")
}

fn signing_client(base_url: String) -> LighterClient {
    LighterClient::with_base_url_credentials_and_chain_id(
        Duration::from_secs(10),
        base_url,
        CHAIN_ID,
        Some(ACCOUNT),
        Some(API_KEY),
        Some("01".to_string() + &"00".repeat(39)),
    )
    .expect("client")
}

fn record_public(method: &'static str, params: &[(&str, &str)]) -> Recorded {
    let (base_url, server) = serve(vec!["{\"code\":200}"]);
    let client = public_client(base_url);
    let params = pairs(params);
    block_on(async move { client.public_request(method, params).await }).expect(method);
    server.join().expect("server").pop().expect("request")
}

fn record_private(method: &'static str, params: &[(&str, &str)]) -> Recorded {
    let (base_url, server) = serve(vec!["{\"code\":200}"]);
    let client = account_client(base_url);
    let params = pairs(params);
    block_on(async move { client.private_request(method, params).await }).expect(method);
    server.join().expect("server").pop().expect("request")
}

#[test]
fn public_routes_follow_official_paths_and_query_names() {
    let cases: Vec<(&'static str, Vec<(&str, &str)>, &str, Vec<(&str, &str)>)> = vec![
        ("get_status", vec![], "/", vec![]),
        ("get_info", vec![], "/info", vec![]),
        ("get_announcement", vec![], "/api/v1/announcement", vec![]),
        ("get_system_config", vec![], "/api/v1/systemConfig", vec![]),
        (
            "get_layer1_basic_info",
            vec![],
            "/api/v1/layer1BasicInfo",
            vec![],
        ),
        ("get_funding_rates", vec![], "/api/v1/funding-rates", vec![]),
        (
            "get_exchange_stats",
            vec![],
            "/api/v1/exchangeStats",
            vec![],
        ),
        (
            "get_deposit_networks",
            vec![],
            "/api/v1/deposit/networks",
            vec![],
        ),
        (
            "get_fastbridge_info",
            vec![],
            "/api/v1/fastbridge/info",
            vec![],
        ),
        ("get_lease_options", vec![], "/api/v1/leaseOptions", vec![]),
        (
            "get_withdrawal_delay",
            vec![],
            "/api/v1/withdrawalDelay",
            vec![],
        ),
        ("get_token_list", vec![], "/api/v1/tokenlist", vec![]),
        ("get_asset_details", vec![], "/api/v1/assetDetails", vec![]),
        (
            "get_asset_details",
            vec![("asset_id", "3")],
            "/api/v1/assetDetails",
            vec![("asset_id", "3")],
        ),
        (
            "get_order_book_details",
            vec![("market_id", "1"), ("filter", "perp")],
            "/api/v1/orderBookDetails",
            vec![("market_id", "1"), ("filter", "perp")],
        ),
        (
            "get_order_books",
            vec![("filter", "spot")],
            "/api/v1/orderBooks",
            vec![("filter", "spot")],
        ),
        (
            "get_order_book_orders",
            vec![("market_id", "1"), ("limit", "250")],
            "/api/v1/orderBookOrders",
            vec![("market_id", "1"), ("limit", "250")],
        ),
        (
            "get_recent_trades",
            vec![("market_id", "2"), ("limit", "100")],
            "/api/v1/recentTrades",
            vec![("market_id", "2"), ("limit", "100")],
        ),
        (
            "get_trades",
            vec![
                ("sort_by", "timestamp"),
                ("limit", "10"),
                ("market_id", "1"),
                ("from_", "1700000000000"),
                ("type_", "liquidation"),
                ("role", "maker"),
                ("aggregate", "true"),
            ],
            "/api/v1/trades",
            vec![
                ("market_id", "1"),
                ("sort_by", "timestamp"),
                ("from", "1700000000000"),
                ("role", "maker"),
                ("type", "liquidation"),
                ("limit", "10"),
                ("aggregate", "true"),
            ],
        ),
        (
            "get_candles",
            vec![
                ("market_id", "1"),
                ("resolution", "1w"),
                ("start_timestamp", "1000"),
                ("end_timestamp", "2000"),
                ("count_back", "5"),
                ("set_timestamp_to_end", "true"),
            ],
            "/api/v1/candles",
            vec![
                ("market_id", "1"),
                ("resolution", "1w"),
                ("start_timestamp", "1000"),
                ("end_timestamp", "2000"),
                ("count_back", "5"),
                ("set_timestamp_to_end", "true"),
            ],
        ),
        (
            "get_fundings",
            vec![
                ("market_id", "1"),
                ("resolution", "1h"),
                ("start_timestamp", "1000"),
                ("end_timestamp", "2000"),
                ("count_back", "5"),
            ],
            "/api/v1/fundings",
            vec![
                ("market_id", "1"),
                ("resolution", "1h"),
                ("start_timestamp", "1000"),
                ("end_timestamp", "2000"),
                ("count_back", "5"),
            ],
        ),
        (
            "get_execute_stats",
            vec![("period", "w")],
            "/api/v1/executeStats",
            vec![("period", "w")],
        ),
        (
            "get_exchange_metrics",
            vec![
                ("period", "d"),
                ("kind", "volume"),
                ("filter", "byMarket"),
                ("value", "1"),
            ],
            "/api/v1/exchangeMetrics",
            vec![
                ("period", "d"),
                ("kind", "volume"),
                ("filter", "byMarket"),
                ("value", "1"),
            ],
        ),
        (
            "get_account",
            vec![("by", "index"), ("value", "12"), ("active_only", "true")],
            "/api/v1/account",
            vec![("by", "index"), ("value", "12"), ("active_only", "true")],
        ),
        (
            "get_accounts_by_l1_address",
            vec![("l1_address", "0xabc")],
            "/api/v1/accountsByL1Address",
            vec![("l1_address", "0xabc")],
        ),
        (
            "get_api_keys",
            vec![("account_index", "12"), ("api_key_index", "3")],
            "/api/v1/apikeys",
            vec![("account_index", "12"), ("api_key_index", "3")],
        ),
    ];
    for (method, params, path, expected_query) in cases {
        let recorded = record_public(method, &params);
        assert_eq!(recorded.method, "GET", "{method}");
        assert_eq!(recorded.path, path, "{method}");
        let mut actual = recorded.query.clone();
        actual.sort();
        let mut expected = owned(&expected_query);
        expected.sort();
        assert_eq!(actual, expected, "{method}");
        assert!(!recorded.headers.contains_key("authorization"), "{method}");
    }
}

#[test]
fn public_routes_forward_optional_authorization_header() {
    let cases: Vec<(&'static str, Vec<(&str, &str)>, &str)> = vec![
        (
            "get_account_metadata",
            vec![("by", "index"), ("value", "12"), ("authorization", TOKEN)],
            "/api/v1/accountMetadata",
        ),
        (
            "get_public_pools_metadata",
            vec![
                ("index", "0"),
                ("limit", "10"),
                ("filter", "all"),
                ("authorization", TOKEN),
            ],
            "/api/v1/publicPoolsMetadata",
        ),
        (
            "get_pnl",
            vec![
                ("by", "index"),
                ("value", "12"),
                ("resolution", "1h"),
                ("start_timestamp", "1000"),
                ("end_timestamp", "2000"),
                ("count_back", "5"),
                ("ignore_transfers", "true"),
                ("authorization", TOKEN),
            ],
            "/api/v1/pnl",
        ),
        (
            "get_tokens",
            vec![("account_index", "12"), ("authorization", TOKEN)],
            "/api/v1/tokens",
        ),
        (
            "get_trades",
            vec![
                ("sort_by", "trade_id"),
                ("limit", "5"),
                ("account_index", "12"),
                ("authorization", TOKEN),
            ],
            "/api/v1/trades",
        ),
    ];
    for (method, params, path) in cases {
        let recorded = record_public(method, &params);
        assert_eq!(recorded.path, path, "{method}");
        assert_eq!(
            recorded.headers.get("authorization").map(String::as_str),
            Some(TOKEN),
            "{method}"
        );
        assert!(
            !recorded.query.iter().any(|(key, _)| key == "authorization"),
            "{method} must not leak authorization into the query"
        );
    }
}

#[test]
fn private_routes_follow_official_paths_and_attach_auth() {
    let auth = ("authorization", TOKEN);
    let cases: Vec<(&'static str, Vec<(&str, &str)>, &str, Vec<(&str, &str)>)> = vec![
        (
            "get_account_limits",
            vec![auth],
            "/api/v1/accountLimits",
            vec![("account_index", "12")],
        ),
        (
            "get_account_active_orders",
            vec![("market_id", "1"), auth],
            "/api/v1/accountActiveOrders",
            vec![("market_id", "1"), ("account_index", "12")],
        ),
        (
            "get_account_inactive_orders",
            vec![
                ("limit", "50"),
                ("market_id", "1"),
                ("ask_filter", "1"),
                auth,
            ],
            "/api/v1/accountInactiveOrders",
            vec![
                ("market_id", "1"),
                ("ask_filter", "1"),
                ("limit", "50"),
                ("account_index", "12"),
            ],
        ),
        (
            "get_deposit_history",
            vec![("l1_address", "0xabc"), ("filter", "pending"), auth],
            "/api/v1/deposit/history",
            vec![
                ("l1_address", "0xabc"),
                ("filter", "pending"),
                ("account_index", "12"),
            ],
        ),
        (
            "get_fastwithdraw_info",
            vec![auth],
            "/api/v1/fastwithdraw/info",
            vec![("account_index", "12")],
        ),
        (
            "get_l1_metadata",
            vec![("l1_address", "0xabc"), auth],
            "/api/v1/l1Metadata",
            vec![("l1_address", "0xabc")],
        ),
        (
            "get_liquidations",
            vec![("limit", "10"), auth],
            "/api/v1/liquidations",
            vec![("limit", "10"), ("account_index", "12")],
        ),
        (
            "get_referral_points",
            vec![auth],
            "/api/v1/referral/points",
            vec![("account_index", "12")],
        ),
        (
            "get_referral_user_referrals",
            vec![("l1_address", "0xabc"), ("limit", "300"), auth],
            "/api/v1/referral/userReferrals",
            vec![("l1_address", "0xabc"), ("limit", "300")],
        ),
        (
            "get_transfer_history",
            vec![("type_", "L2Transfer"), ("type_", "L2MintShares"), auth],
            "/api/v1/transfer/history",
            vec![
                ("type", "L2Transfer"),
                ("type", "L2MintShares"),
                ("account_index", "12"),
            ],
        ),
        (
            "get_transfer_fee_info",
            vec![("to_account_index", "13"), auth],
            "/api/v1/transferFeeInfo",
            vec![("to_account_index", "13"), ("account_index", "12")],
        ),
        (
            "get_withdraw_history",
            vec![("filter", "claimable"), auth],
            "/api/v1/withdraw/history",
            vec![("filter", "claimable"), ("account_index", "12")],
        ),
        (
            "get_position_funding",
            vec![("limit", "10"), ("side", "long"), auth],
            "/api/v1/positionFunding",
            vec![("limit", "10"), ("side", "long"), ("account_index", "12")],
        ),
        (
            "get_leases",
            vec![("limit", "10"), auth],
            "/api/v1/leases",
            vec![("limit", "10"), ("account_index", "12")],
        ),
        (
            "get_maker_only_api_keys",
            vec![auth],
            "/api/v1/getMakerOnlyApiKeys",
            vec![("account_index", "12")],
        ),
    ];
    for (method, params, path, expected_query) in cases {
        let recorded = record_private(method, &params);
        assert_eq!(recorded.method, "GET", "{method}");
        assert_eq!(recorded.path, path, "{method}");
        let mut actual = recorded.query.clone();
        actual.sort();
        let mut expected = owned(&expected_query);
        expected.sort();
        assert_eq!(actual, expected, "{method}");
        assert_eq!(
            recorded.headers.get("authorization").map(String::as_str),
            Some(TOKEN),
            "{method}"
        );
    }
}

#[test]
fn partner_stats_and_next_nonce_use_configured_indexes_without_auth() {
    let recorded = record_private(
        "get_partner_stats",
        &[("start_timestamp", "1000"), ("end_timestamp", "2000")],
    );
    assert_eq!(recorded.path, "/api/v1/partnerStats");
    assert!(
        recorded
            .query
            .contains(&("account_index".into(), "12".into()))
    );
    assert!(!recorded.headers.contains_key("authorization"));

    let (base_url, server) = serve(vec!["{\"code\":200,\"nonce\":7}"]);
    let client = signing_client(base_url);
    block_on(async move { client.private_request("get_next_nonce", Vec::new()).await })
        .expect("next nonce");
    let recorded = server.join().expect("server").pop().expect("request");
    assert_eq!(recorded.path, "/api/v1/nextNonce");
    assert_eq!(
        recorded.query,
        owned(&[("account_index", "12"), ("api_key_index", "3")])
    );
}

#[test]
fn send_tx_routes_post_form_bodies() {
    let (base_url, server) = serve(vec!["{\"code\":200}", "{\"code\":200}"]);
    let client = public_client(base_url);
    block_on(async move {
        client
            .private_request(
                "send_tx",
                pairs(&[
                    ("tx_type", "14"),
                    ("tx_info", "{\"Nonce\":1}"),
                    ("price_protection", "false"),
                ]),
            )
            .await?;
        client
            .private_request(
                "send_tx_batch",
                pairs(&[("tx_types", "[14,15]"), ("tx_infos", "[{},{}]")]),
            )
            .await
    })
    .expect("send tx");
    let recorded = server.join().expect("server");
    assert_eq!(recorded[0].method, "POST");
    assert_eq!(recorded[0].path, "/api/v1/sendTx");
    assert_eq!(
        recorded[0].form(),
        owned(&[
            ("tx_type", "14"),
            ("tx_info", "{\"Nonce\":1}"),
            ("price_protection", "false"),
        ])
    );
    assert!(
        recorded[0]
            .headers
            .get("content-type")
            .is_some_and(|value| value.starts_with("application/x-www-form-urlencoded"))
    );
    assert_eq!(recorded[1].path, "/api/v1/sendTxBatch");
    assert_eq!(
        recorded[1].form(),
        owned(&[("tx_types", "[14,15]"), ("tx_infos", "[{},{}]")])
    );
}

fn submitted_tx(method: &'static str, params: &[(&str, &str)]) -> (u64, Value, Recorded) {
    let (base_url, server) = serve(vec!["{\"code\":200}"]);
    let client = signing_client(base_url);
    let params = pairs(params);
    block_on(async move { client.private_request(method, params).await }).expect(method);
    let recorded = server.join().expect("server").pop().expect("request");
    assert_eq!(recorded.method, "POST", "{method}");
    assert_eq!(recorded.path, "/api/v1/sendTx", "{method}");
    let tx_type = recorded
        .form_value("tx_type")
        .expect("tx_type")
        .parse::<u64>()
        .expect("numeric tx_type");
    let tx_info: Value =
        serde_json::from_str(&recorded.form_value("tx_info").expect("tx_info")).expect("json");
    assert_eq!(tx_info["AccountIndex"], ACCOUNT, "{method}");
    assert_eq!(tx_info["ApiKeyIndex"], API_KEY, "{method}");
    assert_eq!(tx_info["Nonce"], 55, "{method}");
    assert!(tx_info["ExpiredAt"].as_u64().is_some(), "{method}");
    assert!(
        tx_info["Sig"].as_str().is_some_and(|sig| !sig.is_empty()),
        "{method}"
    );
    (tx_type, tx_info, recorded)
}

#[test]
fn signed_transactions_use_official_tx_types_and_fields() {
    let (tx_type, info, recorded) = submitted_tx(
        "create_order",
        &[
            ("market_index", "1"),
            ("client_order_index", "42"),
            ("base_amount", "1000"),
            ("price", "250000"),
            ("is_ask", "true"),
            ("order_type", "0"),
            ("time_in_force", "1"),
            ("order_expiry", "1900000000000"),
            ("nonce", "55"),
            ("price_protection", "true"),
        ],
    );
    assert_eq!(tx_type, 14);
    assert_eq!(info["MarketIndex"], 1);
    assert_eq!(info["ClientOrderIndex"], 42);
    assert_eq!(info["BaseAmount"], 1000);
    assert_eq!(info["Price"], 250000);
    assert_eq!(info["IsAsk"], 1);
    assert_eq!(info["Type"], 0);
    assert_eq!(info["TimeInForce"], 1);
    assert_eq!(info["ReduceOnly"], 0);
    assert_eq!(info["TriggerPrice"], 0);
    assert_eq!(info["OrderExpiry"], 1_900_000_000_000_u64);
    assert!(info["L2TxAttributes"].is_null());
    assert_eq!(
        recorded.form_value("price_protection").as_deref(),
        Some("true")
    );

    let (tx_type, info, _) = submitted_tx(
        "create_order",
        &[
            ("market_index", "0"),
            ("client_order_index", "1"),
            ("base_amount", "10"),
            ("price", "100"),
            ("is_ask", "false"),
            ("order_type", "1"),
            ("time_in_force", "0"),
            ("order_expiry", "0"),
            ("reduce_only", "true"),
            ("nonce", "55"),
        ],
    );
    assert_eq!(tx_type, 14);
    assert_eq!(info["Type"], 1);
    assert_eq!(info["TimeInForce"], 0);
    assert_eq!(info["OrderExpiry"], 0);
    assert_eq!(info["ReduceOnly"], 1);

    let (tx_type, info, _) = submitted_tx(
        "create_order",
        &[
            ("market_index", "1"),
            ("client_order_index", "2"),
            ("base_amount", "10"),
            ("price", "90"),
            ("is_ask", "true"),
            ("order_type", "2"),
            ("time_in_force", "0"),
            ("trigger_price", "95"),
            ("order_expiry", "1900000000000"),
            ("reduce_only", "true"),
            ("nonce", "55"),
            ("self_trade_behavior_mode", "1"),
        ],
    );
    assert_eq!(tx_type, 14);
    assert_eq!(info["Type"], 2);
    assert_eq!(info["TriggerPrice"], 95);
    assert_eq!(info["L2TxAttributes"]["6"], 1);

    let (tx_type, info, _) = submitted_tx(
        "cancel_order",
        &[
            ("market_index", "1"),
            ("order_index", "99"),
            ("nonce", "55"),
        ],
    );
    assert_eq!(tx_type, 15);
    assert_eq!(info["MarketIndex"], 1);
    assert_eq!(info["Index"], 99);

    let (tx_type, info, _) = submitted_tx(
        "modify_order",
        &[
            ("market_index", "1"),
            ("order_index", "99"),
            ("base_amount", "20"),
            ("price", "101"),
            ("nonce", "55"),
        ],
    );
    assert_eq!(tx_type, 17);
    assert_eq!(info["Index"], 99);
    assert_eq!(info["BaseAmount"], 20);
    assert_eq!(info["Price"], 101);
    assert_eq!(info["TriggerPrice"], 0);

    let (tx_type, info, _) = submitted_tx(
        "cancel_all_orders",
        &[
            ("time_in_force", "1"),
            ("timestamp_ms", "1900000000000"),
            ("nonce", "55"),
        ],
    );
    assert_eq!(tx_type, 16);
    assert_eq!(info["TimeInForce"], 1);
    assert_eq!(info["Time"], 1_900_000_000_000_u64);

    let (tx_type, info, _) = submitted_tx(
        "cancel_all_orders",
        &[
            ("time_in_force", "0"),
            ("timestamp_ms", "0"),
            ("cancel_all_market_index", "7"),
            ("nonce", "55"),
        ],
    );
    assert_eq!(tx_type, 16);
    assert_eq!(info["L2TxAttributes"]["5"], 7);

    let (tx_type, info, _) = submitted_tx(
        "update_leverage",
        &[
            ("market_index", "1"),
            ("fraction", "500"),
            ("margin_mode", "1"),
            ("nonce", "55"),
        ],
    );
    assert_eq!(tx_type, 20);
    assert_eq!(info["InitialMarginFraction"], 500);
    assert_eq!(info["MarginMode"], 1);

    let (tx_type, info, _) = submitted_tx(
        "update_margin",
        &[
            ("market_index", "1"),
            ("usdc_amount", "-1500000"),
            ("direction", "0"),
            ("nonce", "55"),
        ],
    );
    assert_eq!(tx_type, 29);
    assert_eq!(info["USDCAmount"], -1_500_000);
    assert_eq!(info["Direction"], 0);
}

#[test]
fn signed_transactions_fetch_next_nonce_when_not_supplied() {
    let (base_url, server) = serve(vec!["{\"code\":200,\"nonce\":\"77\"}", "{\"code\":200}"]);
    let client = signing_client(base_url);
    block_on(async move {
        client
            .private_request(
                "cancel_order",
                pairs(&[("market_index", "1"), ("order_index", "5")]),
            )
            .await
    })
    .expect("cancel");
    let recorded = server.join().expect("server");
    assert_eq!(recorded[0].path, "/api/v1/nextNonce");
    assert_eq!(
        recorded[0].query,
        owned(&[("account_index", "12"), ("api_key_index", "3")])
    );
    assert_eq!(recorded[1].path, "/api/v1/sendTx");
    let info: Value =
        serde_json::from_str(&recorded[1].form_value("tx_info").expect("tx_info")).expect("json");
    assert_eq!(info["Nonce"], 77);
}

#[test]
fn sign_only_methods_return_signed_transactions_without_network() {
    let client = signing_client("http://127.0.0.1:1".to_string());
    for (method, params, tx_type) in [
        (
            "sign_create_order",
            vec![
                ("market_index", "1"),
                ("client_order_index", "1"),
                ("base_amount", "1"),
                ("price", "1"),
                ("is_ask", "false"),
                ("order_type", "0"),
                ("time_in_force", "2"),
                ("nonce", "1"),
            ],
            14,
        ),
        (
            "sign_cancel_order",
            vec![("market_index", "1"), ("order_index", "1"), ("nonce", "1")],
            15,
        ),
        (
            "sign_modify_order",
            vec![
                ("market_index", "1"),
                ("order_index", "1"),
                ("base_amount", "1"),
                ("price", "1"),
                ("nonce", "1"),
            ],
            17,
        ),
        (
            "sign_cancel_all_orders",
            vec![
                ("time_in_force", "2"),
                ("timestamp_ms", "0"),
                ("nonce", "1"),
            ],
            16,
        ),
        (
            "sign_update_leverage",
            vec![
                ("market_index", "1"),
                ("fraction", "1000"),
                ("margin_mode", "0"),
                ("nonce", "1"),
            ],
            20,
        ),
        (
            "sign_update_margin",
            vec![
                ("market_index", "1"),
                ("usdc_amount", "1"),
                ("direction", "1"),
                ("nonce", "1"),
            ],
            29,
        ),
    ] {
        let client = client.clone();
        let params = pairs(&params);
        let signed = block_on(async move { client.sign_request(method, params).await })
            .unwrap_or_else(|error| panic!("{method}: {error}"));
        assert_eq!(signed.tx_type, tx_type, "{method}");
        assert_eq!(signed.tx_hash.len(), 80, "{method}");
        let info: Value = serde_json::from_str(&signed.tx_info).expect("tx_info json");
        assert_eq!(info["Nonce"], 1, "{method}");
        assert!(info["Sig"].as_str().is_some(), "{method}");
    }
}

#[test]
fn signed_transactions_reject_invalid_parameters_before_network() {
    let client = signing_client("http://127.0.0.1:1".to_string());
    let order = |extra: &[(&'static str, &'static str)]| {
        let mut params = vec![
            ("market_index", "1"),
            ("client_order_index", "1"),
            ("base_amount", "1"),
            ("price", "1"),
            ("is_ask", "false"),
            ("order_type", "0"),
            ("time_in_force", "1"),
            ("nonce", "1"),
        ];
        for &(key, value) in extra {
            if let Some(existing) = params.iter_mut().find(|(candidate, _)| *candidate == key) {
                existing.1 = value;
            } else {
                params.push((key, value));
            }
        }
        params
    };
    for (method, params) in [
        // Market orders must be IOC with a zero expiry; an explicit non-zero expiry is rejected.
        (
            "create_order",
            order(&[
                ("order_type", "1"),
                ("time_in_force", "0"),
                ("order_expiry", "1900000000000"),
            ]),
        ),
        ("create_order", order(&[("market_index", "255")])),
        ("create_order", order(&[("market_index", "32768")])),
        ("create_order", order(&[("market_index", "-1")])),
        ("create_order", order(&[("price", "0")])),
        ("create_order", order(&[("base_amount", "0")])),
        ("create_order", order(&[("time_in_force", "3")])),
        ("create_order", order(&[("order_type", "2")])),
        ("create_order", order(&[("nonce", "-1")])),
        ("create_order", order(&[("product_symbol", "1")])),
        ("create_order", order(&[("unexpected", "1")])),
        ("create_order", order(&[("integrator_taker_fee", "10")])),
        (
            "cancel_order",
            vec![
                ("market_index", "255"),
                ("order_index", "1"),
                ("nonce", "1"),
            ],
        ),
        (
            "cancel_all_orders",
            vec![
                ("time_in_force", "0"),
                ("timestamp_ms", "0"),
                ("cancel_all_market_index", "32768"),
                ("nonce", "1"),
            ],
        ),
        (
            "cancel_order",
            vec![("market_index", "1"), ("order_index", "0"), ("nonce", "1")],
        ),
        (
            "cancel_all_orders",
            vec![
                ("time_in_force", "1"),
                ("timestamp_ms", "0"),
                ("nonce", "1"),
            ],
        ),
        (
            "cancel_all_orders",
            vec![
                ("time_in_force", "1"),
                ("timestamp_ms", "1"),
                ("cancel_all_market_index", "1"),
                ("nonce", "1"),
            ],
        ),
        (
            "update_leverage",
            vec![
                ("market_index", "1"),
                ("fraction", "0"),
                ("margin_mode", "0"),
                ("nonce", "1"),
            ],
        ),
        (
            "update_leverage",
            vec![
                ("market_index", "1"),
                ("fraction", "100"),
                ("margin_mode", "2"),
                ("nonce", "1"),
            ],
        ),
        (
            "update_margin",
            vec![
                ("market_index", "1"),
                ("usdc_amount", "0"),
                ("direction", "0"),
                ("nonce", "1"),
            ],
        ),
        (
            "update_margin",
            vec![
                ("market_index", "1"),
                ("usdc_amount", "1"),
                ("direction", "2"),
                ("nonce", "1"),
            ],
        ),
        ("send_tx", vec![("tx_type", "256"), ("tx_info", "{}")]),
        ("send_tx", vec![("tx_type", "14")]),
        ("send_tx_batch", vec![("tx_types", "[14]")]),
        ("unknown_private_method", vec![]),
    ] {
        let client = client.clone();
        let params = pairs(&params);
        let result = block_on(async move { client.private_request(method, params).await });
        assert!(result.is_err(), "{method} should be rejected");
    }
}

#[test]
fn signed_transactions_require_credentials_and_chain() {
    let client = account_client("http://127.0.0.1:1".to_string());
    let result = block_on(async move {
        client
            .private_request(
                "cancel_order",
                pairs(&[("market_index", "1"), ("order_index", "1"), ("nonce", "1")]),
            )
            .await
    });
    assert!(result.is_err());

    let client = LighterClient::with_base_url_and_credentials(
        Duration::from_secs(10),
        "http://127.0.0.1:1".to_string(),
        Some(ACCOUNT),
        Some(API_KEY),
        Some("01".to_string() + &"00".repeat(39)),
    )
    .expect("client");
    let result = block_on(async move {
        client
            .private_request(
                "cancel_order",
                pairs(&[("market_index", "1"), ("order_index", "1"), ("nonce", "1")]),
            )
            .await
    });
    assert!(result.is_err(), "custom URL without chain id must not sign");
}

#[test]
fn market_and_account_queries_reject_invalid_parameters_before_network() {
    let client = account_client("http://127.0.0.1:1".to_string());
    for (public, method, params) in [
        (true, "get_status", vec![("unexpected", "1")]),
        (true, "get_order_book_orders", vec![("market_id", "1")]),
        (
            true,
            "get_order_book_orders",
            vec![("market_id", "1"), ("limit", "251")],
        ),
        (
            true,
            "get_recent_trades",
            vec![("market_id", "1"), ("limit", "101")],
        ),
        (
            true,
            "get_trades",
            vec![("sort_by", "price"), ("limit", "1")],
        ),
        (
            true,
            "get_candles",
            vec![
                ("market_id", "1"),
                ("resolution", "2m"),
                ("start_timestamp", "1"),
                ("end_timestamp", "2"),
                ("count_back", "1"),
            ],
        ),
        (
            true,
            "get_fundings",
            vec![
                ("market_id", "1"),
                ("resolution", "1h"),
                ("start_timestamp", "3"),
                ("end_timestamp", "2"),
                ("count_back", "1"),
            ],
        ),
        (true, "get_execute_stats", vec![("period", "x")]),
        (true, "get_account", vec![("by", "name"), ("value", "1")]),
        (
            true,
            "get_order_books",
            vec![("market_id", "1"), ("product_symbol", "1")],
        ),
        (true, "unknown_public_method", vec![]),
        (false, "get_account_inactive_orders", vec![("limit", "0")]),
        (false, "get_deposit_history", vec![("filter", "all")]),
        (false, "get_export", vec![("type_", "orders")]),
        (false, "get_transfer_history", vec![("type_", "L2Withdraw")]),
        (false, "get_liquidations", vec![("limit", "101")]),
        (false, "get_next_nonce", vec![("api_key_index", "255")]),
    ] {
        let client = client.clone();
        let params = pairs(&params);
        let result = block_on(async move {
            if public {
                client.public_request(method, params).await
            } else {
                client.private_request(method, params).await
            }
        });
        assert!(result.is_err(), "{method} should be rejected");
    }
}

fn sign(client: &LighterClient, method: &'static str, params: &[(&str, &str)]) -> Result<Value> {
    let client = client.clone();
    let params = pairs(params);
    let signed = block_on(async move { client.sign_request(method, params).await })?;
    Ok(serde_json::from_str(&signed.tx_info).expect("tx_info json"))
}

fn lighter_row(market_id: &str, product_symbol: &str, product_type: &str) -> MarketInfo {
    MarketInfo {
        exchange: "lighter".to_string(),
        exchange_symbol: market_id.to_string(),
        product_symbol: product_symbol.to_string(),
        product_type: product_type.to_string(),
        exchange_type: product_type.to_string(),
        price_precision: "0.01".to_string(),
        size_precision: "0.001".to_string(),
        min_size: "0.001".to_string(),
        base_currency: "X".to_string(),
        quote_currency: "USDC".to_string(),
        min_notional: "1".to_string(),
        size_per_contract: "1".to_string(),
        ..MarketInfo::default()
    }
}

const LIMIT_ORDER: &[(&str, &str)] = &[
    ("client_order_index", "1"),
    ("base_amount", "1"),
    ("price", "1"),
    ("is_ask", "false"),
    ("order_type", "0"),
    ("time_in_force", "1"),
    ("nonce", "1"),
];

fn with(
    base: &[(&'static str, &'static str)],
    extra: &[(&'static str, &'static str)],
) -> Vec<(&'static str, &'static str)> {
    let mut params = base.to_vec();
    for &(key, value) in extra {
        if let Some(existing) = params.iter_mut().find(|(candidate, _)| *candidate == key) {
            existing.1 = value;
        } else {
            params.push((key, value));
        }
    }
    params
}

#[test]
fn market_ids_follow_lighter_go_bounds_not_legacy_ranges() {
    // lighter-go txtypes: MaxMarketIndex = 32767, NilMarketIndex = 255; 4095 is live perp STONK.
    let client = signing_client("http://127.0.0.1:1".to_string());
    for market in ["0", "254", "256", "2047", "2048", "4095", "32767"] {
        let info = sign(
            &client,
            "sign_create_order",
            &with(LIMIT_ORDER, &[("market_index", market)]),
        )
        .unwrap_or_else(|error| panic!("create {market}: {error}"));
        assert_eq!(info["MarketIndex"].to_string(), market);
        // Without metadata the market type is unknown, so reduce-only is not blocked.
        sign(
            &client,
            "sign_create_order",
            &with(
                LIMIT_ORDER,
                &[("market_index", market), ("reduce_only", "true")],
            ),
        )
        .unwrap_or_else(|error| panic!("reduce-only {market}: {error}"));
        sign(
            &client,
            "sign_cancel_order",
            &[
                ("market_index", market),
                ("order_index", "1"),
                ("nonce", "1"),
            ],
        )
        .unwrap_or_else(|error| panic!("cancel {market}: {error}"));
        sign(
            &client,
            "sign_modify_order",
            &[
                ("market_index", market),
                ("order_index", "1"),
                ("base_amount", "1"),
                ("price", "1"),
                ("nonce", "1"),
            ],
        )
        .unwrap_or_else(|error| panic!("modify {market}: {error}"));
        sign(
            &client,
            "sign_update_leverage",
            &[
                ("market_index", market),
                ("fraction", "1000"),
                ("margin_mode", "0"),
                ("nonce", "1"),
            ],
        )
        .unwrap_or_else(|error| panic!("leverage {market}: {error}"));
        sign(
            &client,
            "sign_update_margin",
            &[
                ("market_index", market),
                ("usdc_amount", "1"),
                ("direction", "1"),
                ("nonce", "1"),
            ],
        )
        .unwrap_or_else(|error| panic!("margin {market}: {error}"));
    }
    let info = sign(
        &client,
        "sign_cancel_all_orders",
        &[
            ("time_in_force", "0"),
            ("timestamp_ms", "0"),
            ("cancel_all_market_index", "4095"),
            ("nonce", "1"),
        ],
    )
    .expect("cancel all 4095");
    assert_eq!(info["L2TxAttributes"]["5"], 4095);
    for market in ["255", "32768", "-1"] {
        assert!(
            sign(
                &client,
                "sign_create_order",
                &with(LIMIT_ORDER, &[("market_index", market)]),
            )
            .is_err(),
            "{market}"
        );
    }
}

#[test]
fn spot_restrictions_use_market_metadata() {
    // 4095 is a perp even though it sits in the legacy spot range; 7 is a spot market.
    let table = ProductTable::new(vec![
        lighter_row("4095", "STONK-USDC-SWAP", "swap"),
        lighter_row("7", "ABC-USDC-SPOT", "spot"),
    ]);
    let client = signing_client("http://127.0.0.1:1".to_string()).with_product_table(table);
    let info = sign(
        &client,
        "sign_create_order",
        &with(
            LIMIT_ORDER,
            &[
                ("product_symbol", "STONK-USDC-SWAP"),
                ("reduce_only", "true"),
            ],
        ),
    )
    .expect("perp reduce-only");
    assert_eq!(info["MarketIndex"], 4095);
    sign(
        &client,
        "sign_create_order",
        &with(LIMIT_ORDER, &[("market_index", "7")]),
    )
    .expect("spot limit");
    for params in [
        with(
            LIMIT_ORDER,
            &[("market_index", "7"), ("reduce_only", "true")],
        ),
        with(
            LIMIT_ORDER,
            &[
                ("product_symbol", "ABC-USDC-SPOT"),
                ("order_type", "2"),
                ("time_in_force", "0"),
                ("trigger_price", "1"),
            ],
        ),
    ] {
        assert!(
            sign(&client, "sign_create_order", &params).is_err(),
            "{params:?}"
        );
    }
    for (method, params) in [
        (
            "sign_update_leverage",
            [
                ("market_index", "7"),
                ("fraction", "1000"),
                ("margin_mode", "0"),
                ("nonce", "1"),
            ],
        ),
        (
            "sign_update_margin",
            [
                ("market_index", "7"),
                ("usdc_amount", "1"),
                ("direction", "1"),
                ("nonce", "1"),
            ],
        ),
    ] {
        assert!(sign(&client, method, &params).is_err(), "{method}");
    }
}

#[test]
fn default_order_expiry_matches_order_type_and_time_in_force() {
    let client = signing_client("http://127.0.0.1:1".to_string());
    // Market and IOC limit orders default to expiry 0 (lighter-python DEFAULT_IOC_EXPIRY).
    for extra in [
        vec![("order_type", "1"), ("time_in_force", "0")],
        vec![
            ("order_type", "1"),
            ("time_in_force", "0"),
            ("order_expiry", "-1"),
        ],
        vec![("order_type", "0"), ("time_in_force", "0")],
    ] {
        let mut extra = extra;
        extra.push(("market_index", "1"));
        let info = sign(&client, "sign_create_order", &with(LIMIT_ORDER, &extra))
            .unwrap_or_else(|error| panic!("{extra:?}: {error}"));
        assert_eq!(info["OrderExpiry"], 0, "{extra:?}");
    }
    // Resting, trigger and TWAP orders default to the 28-day expiry.
    for extra in [
        vec![("order_type", "0"), ("time_in_force", "1")],
        vec![("order_type", "0"), ("time_in_force", "2")],
        vec![
            ("order_type", "2"),
            ("time_in_force", "0"),
            ("trigger_price", "1"),
        ],
        vec![("order_type", "6"), ("time_in_force", "1")],
    ] {
        let mut extra = extra;
        extra.push(("market_index", "1"));
        let info = sign(&client, "sign_create_order", &with(LIMIT_ORDER, &extra))
            .unwrap_or_else(|error| panic!("{extra:?}: {error}"));
        assert!(
            info["OrderExpiry"]
                .as_i64()
                .is_some_and(|value| value > 1_700_000_000_000),
            "{extra:?}"
        );
    }
}

#[test]
fn grouped_orders_sign_and_submit_one_transaction() {
    for grouping in [1, 2, 3] {
        let sl = serde_json::json!({"market_index":1,"client_order_index":11,"base_amount":if grouping==2 {1000} else {0},"price":240000,"is_ask":true,"order_type":2,"time_in_force":0,"reduce_only":true,"trigger_price":240000,"order_expiry":1900000000000_i64});
        let mut tp = sl.clone();
        tp["client_order_index"] = 12.into();
        tp["order_type"] = 4.into();
        tp["trigger_price"] = 260000.into();
        let parent = serde_json::json!({"market_index":1,"client_order_index":10,"base_amount":1000,"price":250000,"is_ask":false,"order_type":1,"time_in_force":0,"order_expiry":0});
        let orders = match grouping {
            1 => serde_json::json!([parent, sl]),
            2 => serde_json::json!([sl, tp]),
            _ => serde_json::json!([parent, sl, tp]),
        };
        let (base, server) = serve(vec!["{\"code\":200}"]);
        let client = signing_client(base);
        block_on(async move {
            client
                .private_request(
                    "create_grouped_orders",
                    vec![
                        ("grouping_type".into(), grouping.to_string()),
                        ("orders".into(), orders.to_string()),
                        ("nonce".into(), "5".into()),
                    ],
                )
                .await
        })
        .expect("grouped transaction");
        let records = server.join().unwrap();
        assert_eq!(records.len(), 1);
        assert_eq!(records[0].path, "/api/v1/sendTx");
        assert_eq!(records[0].form_value("tx_type").as_deref(), Some("28"));
        let tx: Value = serde_json::from_str(&records[0].form_value("tx_info").unwrap()).unwrap();
        assert_eq!(tx["GroupingType"], grouping);
        assert_eq!(tx["Nonce"], 5);
        assert!(tx["Sig"].is_string());
        assert_eq!(
            tx["Orders"].as_array().unwrap().len(),
            if grouping == 3 { 3 } else { 2 }
        );
    }
}

#[test]
fn grouped_orders_validate_relationships_before_nonce_lookup() {
    let valid = serde_json::json!({"market_index":1,"client_order_index":11,"base_amount":1000,"price":240000,"is_ask":true,"order_type":2,"time_in_force":0,"reduce_only":true,"trigger_price":240000,"order_expiry":1900000000000_i64});
    let mut second = valid.clone();
    second["client_order_index"] = 12.into();
    second["order_type"] = 4.into();
    let client = signing_client("http://127.0.0.1:9".into());
    for (field, value) in [
        ("client_order_index", 11.into()),
        ("market_index", 2.into()),
        ("reduce_only", false.into()),
        ("order_expiry", 1800000000000_i64.into()),
        ("order_type", 2.into()),
        ("is_ask", false.into()),
    ] {
        let mut bad = second.clone();
        bad[field] = value;
        let orders = serde_json::json!([valid, bad]);
        let error = block_on({
            let client = client.clone();
            async move {
                client
                    .sign_request(
                        "sign_create_grouped_orders",
                        vec![
                            ("grouping_type".into(), "2".into()),
                            ("orders".into(), orders.to_string()),
                        ],
                    )
                    .await
            }
        })
        .unwrap_err();
        assert!(
            matches!(error, crate::DcexError::InvalidInput(_)),
            "{field}: {error}"
        );
    }
}

#[test]
fn account_config_transactions_have_correct_types_and_signed_fields() {
    for (method, params, tx_type, expected) in [
        (
            "update_account_config",
            vec![("account_trading_mode", "1"), ("nonce", "5")],
            41,
            json!({"AccountTradingMode":1}),
        ),
        (
            "update_account_asset_config",
            vec![
                ("asset_index", "62"),
                ("asset_margin_mode", "0"),
                ("nonce", "5"),
            ],
            42,
            json!({"AssetIndex":62,"AssetMarginMode":0}),
        ),
    ] {
        let (base, server) = serve(vec!["{\"code\":200}"]);
        let client = signing_client(base);
        let params = pairs(&params);
        block_on(async move { client.private_request(method, params).await }).expect(method);
        let requests = server.join().unwrap();
        assert_eq!(requests.len(), 1);
        assert_eq!(requests[0].form_value("tx_type"), Some(tx_type.to_string()));
        let tx: Value = serde_json::from_str(&requests[0].form_value("tx_info").unwrap()).unwrap();
        for (key, value) in expected.as_object().unwrap() {
            assert_eq!(&tx[key], value);
        }
        assert_eq!(tx["Nonce"], 5);
        assert!(tx["Sig"].as_str().is_some_and(|s| !s.is_empty()));
    }
}

#[test]
fn account_config_rejects_invalid_modes_before_nonce_lookup() {
    let client = signing_client("http://127.0.0.1:1".into());
    for (method, params) in [
        (
            "sign_update_account_config",
            vec![("account_trading_mode", "2")],
        ),
        (
            "sign_update_account_config",
            vec![("account_trading_mode", "-1")],
        ),
        (
            "sign_update_account_asset_config",
            vec![("asset_index", "0"), ("asset_margin_mode", "1")],
        ),
        (
            "sign_update_account_asset_config",
            vec![("asset_index", "63"), ("asset_margin_mode", "1")],
        ),
        (
            "sign_update_account_asset_config",
            vec![("asset_index", "1"), ("asset_margin_mode", "2")],
        ),
    ] {
        let error = sign(&client, method, &params).unwrap_err();
        assert!(
            matches!(error, crate::DcexError::InvalidInput(_)),
            "{method}: {error}"
        );
    }
}

#[test]
fn additional_account_and_deposit_routes_preserve_form_and_authorization() {
    let cases: &[(&str, bool, &str, &str, &[(&str, &str)])] = &[
        (
            "set_maker_only_api_keys",
            false,
            "POST",
            "/api/v1/setMakerOnlyApiKeys",
            &[
                ("account_index", "12"),
                ("api_key_indexes", "[]"),
                ("authorization", "test-token"),
            ],
        ),
        (
            "change_account_tier",
            false,
            "POST",
            "/api/v1/changeAccountTier",
            &[
                ("account_index", "12"),
                ("new_tier", "premium"),
                ("authorization", "test-token"),
            ],
        ),
        (
            "create_read_only_token",
            false,
            "POST",
            "/api/v1/tokens/create",
            &[
                ("name", "reporting"),
                ("account_index", "12"),
                ("expiry", "1800000000"),
                ("sub_account_access", "false"),
                ("authorization", "test-token"),
            ],
        ),
        (
            "revoke_read_only_token",
            false,
            "POST",
            "/api/v1/tokens/revoke",
            &[
                ("token_id", "1"),
                ("account_index", "12"),
                ("authorization", "test-token"),
            ],
        ),
        (
            "get_transaction",
            true,
            "GET",
            "/api/v1/tx",
            &[("by", "hash"), ("value", "abc")],
        ),
        (
            "get_transaction_by_l1_hash",
            true,
            "GET",
            "/api/v1/txFromL1TxHash",
            &[(
                "hash",
                "0x1111111111111111111111111111111111111111111111111111111111111111",
            )],
        ),
        (
            "acknowledge_notification",
            false,
            "POST",
            "/api/v1/notification/ack",
            &[
                ("notif_id", "notification-1"),
                ("account_index", "12"),
                ("authorization", "test-token"),
            ],
        ),
        (
            "create_deposit_intent_address",
            true,
            "POST",
            "/api/v1/createIntentAddress",
            &[
                ("chain_id", "42161"),
                ("from_addr", "0x2222222222222222222222222222222222222222"),
                ("amount", "1"),
            ],
        ),
        (
            "get_latest_deposit",
            true,
            "GET",
            "/api/v1/deposit/latest",
            &[("l1_address", "0x2222222222222222222222222222222222222222")],
        ),
    ];
    for (name, public, method, path, params) in cases {
        let (url, server) = serve(vec!["{\"code\":200}"]);
        let client = account_client(url);
        block_on(async move {
            if *public {
                client.public_request(name, pairs(params)).await
            } else {
                client.private_request(name, pairs(params)).await
            }
        })
        .expect(name);
        let request = server.join().expect("server").pop().expect("request");
        assert_eq!(request.method, *method);
        assert_eq!(request.path, *path);
        let actual = if *method == "POST" {
            request.form()
        } else {
            request.query.clone()
        };
        let expected: Vec<_> = params
            .iter()
            .filter(|(k, _)| *k != "authorization")
            .map(|(k, v)| ((*k).to_string(), (*v).to_string()))
            .collect();
        assert_eq!(actual, expected);
        assert_eq!(
            request.headers.get("authorization").map(String::as_str),
            if *public { None } else { Some(TOKEN) }
        );
    }
}

#[test]
fn pool_transactions_have_official_types_and_fields() {
    for (method, params, tx_type, expected) in [
        (
            "create_public_pool",
            vec![
                ("operator_fee", "1"),
                ("initial_total_shares", "1"),
                ("min_operator_share_rate", "1"),
                ("nonce", "5"),
            ],
            10,
            json!({"OperatorFee": 1, "InitialTotalShares": 1, "MinOperatorShareRate": 1}),
        ),
        (
            "update_public_pool",
            vec![
                ("public_pool_index", "1"),
                ("status", "1"),
                ("operator_fee", "1"),
                ("min_operator_share_rate", "1"),
                ("nonce", "5"),
            ],
            11,
            json!({"PublicPoolIndex": 1, "Status": 1, "OperatorFee": 1, "MinOperatorShareRate": 1}),
        ),
        (
            "mint_shares",
            vec![
                ("public_pool_index", "140737488355328"),
                ("share_amount", "1"),
                ("nonce", "5"),
            ],
            18,
            json!({"PublicPoolIndex": 140737488355328_u64, "ShareAmount": 1}),
        ),
        (
            "burn_shares",
            vec![
                ("public_pool_index", "140737488355328"),
                ("share_amount", "1"),
                ("nonce", "5"),
            ],
            19,
            json!({"PublicPoolIndex": 140737488355328_u64, "ShareAmount": 1}),
        ),
        (
            "stake_assets",
            vec![
                ("staking_pool_index", "140737488355328"),
                ("share_amount", "1"),
                ("nonce", "5"),
            ],
            35,
            json!({"StakingPoolIndex": 140737488355328_u64, "ShareAmount": 1}),
        ),
        (
            "unstake_assets",
            vec![
                ("staking_pool_index", "140737488355328"),
                ("share_amount", "1"),
                ("nonce", "5"),
            ],
            36,
            json!({"StakingPoolIndex": 140737488355328_u64, "ShareAmount": 1}),
        ),
    ] {
        let (base, server) = serve(vec!["{\"code\":200}"]);
        let client = signing_client(base);
        let params = pairs(&params);
        block_on(async move { client.private_request(method, params).await }).expect(method);
        let requests = server.join().unwrap();
        assert_eq!(requests.len(), 1);
        assert_eq!(requests[0].form_value("tx_type"), Some(tx_type.to_string()));
        let tx: Value = serde_json::from_str(&requests[0].form_value("tx_info").unwrap()).unwrap();
        for (key, value) in expected.as_object().unwrap() {
            assert_eq!(&tx[key], value);
        }
        assert_eq!(tx["Nonce"], 5);
        assert!(tx["Sig"].as_str().is_some_and(|s| !s.is_empty()));
    }
}

#[test]
fn explorer_uses_separate_origin_and_official_paths() {
    for (name, private, path, params) in [
        (
            "get_pnl_leaderboard",
            false,
            "/api/v1/pnlLeaderboard",
            vec![
                ("time_window", "24h"),
                ("sort_by", "pnl"),
                ("sort_dir", "asc"),
                ("limit", "10"),
                ("offset", "0"),
            ],
        ),
        (
            "export_historical_trades",
            true,
            "/api/v1/export/historicalTrades",
            vec![
                ("l1_address", "0x1111111111111111111111111111111111111111"),
                ("date", "2026-09-01"),
                ("authorization", "test-token"),
            ],
        ),
        (
            "get_explorer_account_logs",
            false,
            "/accounts/1/logs",
            vec![("param", "1"), ("limit", "1"), ("offset", "1")],
        ),
        (
            "get_explorer_account_positions",
            false,
            "/accounts/1/positions",
            vec![("param", "1")],
        ),
        (
            "get_explorer_account_assets",
            false,
            "/accounts/1/assets",
            vec![("param", "1")],
        ),
        ("get_explorer_batches", false, "/batches", vec![]),
        (
            "get_explorer_batch",
            false,
            "/batches/1",
            vec![("batchId", "1")],
        ),
        ("get_explorer_blocks", false, "/blocks", vec![]),
        (
            "get_explorer_block",
            false,
            "/blocks/1",
            vec![("blockId", "1")],
        ),
        ("get_explorer_log", false, "/logs/1", vec![("hash", "1")]),
        ("get_explorer_markets", false, "/markets", vec![]),
        (
            "get_explorer_market_logs",
            false,
            "/markets/1/logs",
            vec![("symbol", "1")],
        ),
        ("search_explorer", false, "/search", vec![("q", "1")]),
        (
            "get_explorer_transaction_stats",
            false,
            "/stats/tx",
            vec![("aggregation_period", "1")],
        ),
        ("get_explorer_total", false, "/total", vec![]),
    ] {
        let (url, server) = serve(vec!["{\"code\":200}"]);
        let client = account_client(if name.contains("explorer") {
            "http://127.0.0.1:1".into()
        } else {
            url.clone()
        })
        .with_explorer_base_url(url)
        .expect("explorer URL");
        block_on(async move {
            if private {
                client.private_request(name, pairs(&params)).await
            } else {
                client.public_request(name, pairs(&params)).await
            }
        })
        .expect(name);
        let request = server.join().expect("server").pop().expect("request");
        assert_eq!(request.path, path);
        assert_eq!(request.method, "GET");
        assert!(!request.query.iter().any(|(key, _)| matches!(
            key.as_str(),
            "authorization" | "param" | "batchId" | "blockId" | "hash" | "symbol"
        )));
    }
}

#[test]
fn same_master_transfer_has_no_external_wallet_signature() {
    let client = signing_client("http://127.0.0.1:1".into());
    let tx = block_on(async move {
        client
            .sign_transfer_l2_account(pairs(&[
                ("to_account_index", "13"),
                ("asset_index", "3"),
                ("from_route_type", "0"),
                ("to_route_type", "1"),
                ("amount", "4294967297"),
                ("nonce", "5"),
            ]))
            .await
    })
    .expect("sign");
    assert_eq!(tx.tx_type, 12);
    let info: Value = serde_json::from_str(&tx.tx_info).expect("JSON");
    assert_eq!(info["FromAccountIndex"], 12);
    assert_eq!(info["ToAccountIndex"], 13);
    assert_eq!(info["L1Sig"], "");
    assert_eq!(info["Memo"], json!([0; 32].to_vec()));
    assert_eq!(info["Amount"], 4294967297_u64);
}

#[tokio::test]
async fn every_typed_wrapper_reaches_dispatch() {
    // The typed Rust methods must reach the same dispatch Python calls by name.
    let url = crate::exchanges::wrapper_dispatch::instant_server();
    let client = signing_client(url.clone());
    crate::exchanges::wrapper_dispatch::assert_dispatch(
        "lighter",
        "LighterClient",
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
