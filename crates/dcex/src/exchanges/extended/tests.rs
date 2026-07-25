use std::time::Duration;
use std::{
    io::{Read, Write},
    net::TcpListener,
    thread,
};

use super::client::signing_domain_for_base_url;
use super::ExtendedClient;

#[test]
fn testnet_base_url_uses_sepolia_signing_domain() {
    assert_eq!(
        signing_domain_for_base_url("https://api.starknet.sepolia.extended.exchange").chain_id,
        "SN_SEPOLIA"
    );
    assert_eq!(
        signing_domain_for_base_url("https://api.starknet.extended.exchange").chain_id,
        "SN_MAIN"
    );
}

#[tokio::test]
async fn market_methods_use_documented_paths() {
    assert_request_line(
        public_request(
            "get_market_statistics",
            vec![("market".to_string(), "BTC-USD".to_string())],
        )
        .await,
        "GET /api/v1/info/markets/BTC-USD/stats HTTP/1.1",
    );
    assert_request_line(
        public_request(
            "get_order_book",
            vec![("market".to_string(), "BTC-USD".to_string())],
        )
        .await,
        "GET /api/v1/info/markets/BTC-USD/orderbook HTTP/1.1",
    );
    assert_request_line(
        public_request(
            "get_assets",
            vec![
                ("asset".to_string(), "BTC".to_string()),
                ("type".to_string(), "SPOT".to_string()),
                ("collateral".to_string(), "false".to_string()),
            ],
        )
        .await,
        "GET /api/v1/info/assets?asset=BTC&type=SPOT&collateral=false HTTP/1.1",
    );
    assert_request_line(
        public_request(
            "get_trades",
            vec![("market".to_string(), "BTC-USD".to_string())],
        )
        .await,
        "GET /api/v1/info/markets/BTC-USD/trades HTTP/1.1",
    );
    assert_request_line(
        public_request(
            "get_candles",
            vec![
                ("market".to_string(), "BTC-USD".to_string()),
                ("candleType".to_string(), "mark-prices".to_string()),
                ("interval".to_string(), "PT1M".to_string()),
                ("limit".to_string(), "50".to_string()),
                ("endTime".to_string(), "123".to_string()),
            ],
        )
        .await,
        "GET /api/v1/info/candles/BTC-USD/mark-prices?interval=PT1M&limit=50&endTime=123 HTTP/1.1",
    );
    assert_request_line(
        public_request(
            "get_funding",
            vec![
                ("market".to_string(), "BTC-USD".to_string()),
                ("startTime".to_string(), "100".to_string()),
                ("endTime".to_string(), "200".to_string()),
                ("limit".to_string(), "10".to_string()),
            ],
        )
        .await,
        "GET /api/v1/info/BTC-USD/funding?startTime=100&endTime=200&limit=10 HTTP/1.1",
    );
    assert_request_line(
        public_request(
            "get_open_interest",
            vec![
                ("market".to_string(), "BTC-USD".to_string()),
                ("interval".to_string(), "P1H".to_string()),
                ("startTime".to_string(), "100".to_string()),
                ("endTime".to_string(), "200".to_string()),
                ("limit".to_string(), "10".to_string()),
            ],
        )
        .await,
        "GET /api/v1/info/BTC-USD/open-interests?interval=P1H&startTime=100&endTime=200&limit=10 HTTP/1.1",
    );
}

#[tokio::test]
async fn get_candles_requires_interval_and_limit() {
    let client = ExtendedClient::with_base_url(
        None,
        Duration::from_secs(2),
        "http://127.0.0.1:1".to_string(),
        "dcex-test".to_string(),
    )
    .expect("client");

    let missing_interval = client
        .public_request(
            "get_candles",
            vec![
                ("market".to_string(), "BTC-USD".to_string()),
                ("limit".to_string(), "50".to_string()),
            ],
        )
        .await
        .expect_err("interval must be required");
    assert!(missing_interval
        .to_string()
        .contains("missing required parameter: interval"));

    let missing_limit = client
        .public_request(
            "get_candles",
            vec![
                ("market".to_string(), "BTC-USD".to_string()),
                ("interval".to_string(), "PT1M".to_string()),
            ],
        )
        .await
        .expect_err("limit must be required");
    assert!(missing_limit
        .to_string()
        .contains("missing required parameter: limit"));
}

#[tokio::test]
async fn get_order_uses_plural_order_path() {
    let request = private_request("get_order", vec![("id".to_string(), "123".to_string())]).await;
    assert_request_line(request.as_str(), "GET /api/v1/user/orders/123 HTTP/1.1");
    assert!(request
        .to_ascii_lowercase()
        .contains("x-api-key: extended-key"));
}

#[tokio::test]
async fn private_methods_use_documented_paths_and_params() {
    assert_request_line(
        private_request(
            "get_spot_balances",
            vec![("accountId".to_string(), "100".to_string())],
        )
        .await,
        "GET /api/v1/user/spot/balances?accountId=100 HTTP/1.1",
    );
    assert_request_line(
        private_request(
            "get_fees",
            vec![
                ("market".to_string(), "BTC-USD".to_string()),
                ("builderId".to_string(), "2017".to_string()),
            ],
        )
        .await,
        "GET /api/v1/user/fees?market=BTC-USD&builderId=2017 HTTP/1.1",
    );
    assert_request_line(
        private_request(
            "get_asset_operations",
            vec![
                ("type".to_string(), "TRANSFER".to_string()),
                ("status".to_string(), "COMPLETED".to_string()),
                ("cursor".to_string(), "123".to_string()),
                ("limit".to_string(), "50".to_string()),
            ],
        )
        .await,
        "GET /api/v1/user/assetOperations?type=TRANSFER&status=COMPLETED&cursor=123&limit=50 HTTP/1.1",
    );
    assert_request_line(
        private_request("get_rebates", vec![]).await,
        "GET /api/v1/user/rebates/stats HTTP/1.1",
    );
    assert_request_line(
        private_request("get_builder_dashboard", vec![]).await,
        "GET /api/v1/info/builder/dashboard HTTP/1.1",
    );
    assert_request_line(
        private_request(
            "get_builder_trades",
            vec![
                ("cursor".to_string(), "123".to_string()),
                ("limit".to_string(), "100".to_string()),
            ],
        )
        .await,
        "GET /api/v1/builder/trades?cursor=123&limit=100 HTTP/1.1",
    );
    assert_request_line(
        private_request("get_bridge_config", vec![]).await,
        "GET /api/v1/user/bridge/config HTTP/1.1",
    );
    assert_request_line(
        private_request(
            "get_bridge_quote",
            vec![
                ("chainIn".to_string(), "ARB".to_string()),
                ("chainOut".to_string(), "STRK".to_string()),
                ("amount".to_string(), "100".to_string()),
                ("asset".to_string(), "USD".to_string()),
            ],
        )
        .await,
        "GET /api/v1/user/bridge/quote?chainIn=ARB&chainOut=STRK&amount=100&asset=USD HTTP/1.1",
    );
    assert_request_line(
        private_request(
            "get_order_by_external_id",
            vec![("externalId".to_string(), "client-123".to_string())],
        )
        .await,
        "GET /api/v1/user/orders/external/client-123 HTTP/1.1",
    );

    let deadman_request = private_request(
        "set_deadmanswitch",
        vec![("countdownTime".to_string(), "60".to_string())],
    )
    .await;
    assert_request_line(
        deadman_request.as_str(),
        "POST /api/v1/user/deadmanswitch?countdownTime=60 HTTP/1.1",
    );
    assert!(deadman_request.ends_with("\r\n\r\n"));
}

async fn public_request(method: &str, params: Vec<(String, String)>) -> String {
    let (base_url, handle) = server();
    let client = ExtendedClient::with_base_url(
        None,
        Duration::from_secs(2),
        base_url,
        "dcex-test".to_string(),
    )
    .expect("client");

    client
        .public_request(method, params)
        .await
        .expect("response");
    handle.join().expect("server")
}

async fn private_request(method: &str, params: Vec<(String, String)>) -> String {
    let (base_url, handle) = server();
    let client = ExtendedClient::with_base_url(
        Some("extended-key".to_string()),
        Duration::from_secs(2),
        base_url,
        "dcex-test".to_string(),
    )
    .expect("client");

    client
        .private_request(method, params)
        .await
        .expect("response");
    handle.join().expect("server")
}

fn assert_request_line(request: impl AsRef<str>, expected: &str) {
    let first_line = request.as_ref().lines().next().expect("request line");
    assert_eq!(first_line, expected);
}

fn server() -> (String, thread::JoinHandle<String>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let address = listener.local_addr().expect("address");
    let handle = thread::spawn(move || {
        let (mut stream, _) = listener.accept().expect("accept");
        let mut buffer = [0u8; 4096];
        let size = stream.read(&mut buffer).expect("read");
        let request = String::from_utf8_lossy(&buffer[..size]).into_owned();
        stream
            .write_all(
                b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\
Content-Length: 15\r\nConnection: close\r\n\r\n{\"status\":\"OK\"}",
            )
            .expect("write");
        request
    });
    (format!("http://{address}"), handle)
}
