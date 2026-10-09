use super::helpers::*;

#[test]
fn request_matches_python_encoding() {
    let client = LighterClient::new(Duration::from_secs(10)).expect("client");
    let request = client
        .build_request(
            HttpMethod::Post,
            "/api/v1/sendTx",
            vec![("account_index".to_string(), "1".to_string())],
            vec![
                ("tx_type".to_string(), "14".to_string()),
                ("tx_info".to_string(), r#"{"Price":100}"#.to_string()),
            ],
            false,
            BTreeMap::new(),
            LighterContentType::Form,
        )
        .expect("request");

    assert_eq!(request.path, "/api/v1/sendTx?account_index=1");
    assert_eq!(
        request.body,
        RequestBody::Raw(b"tx_type=14&tx_info=%7B%22Price%22%3A100%7D".to_vec())
    );
}

#[test]
fn robinhood_uses_its_own_market_ids() {
    let mainnet = MarketInfo {
        exchange: "lighter".to_string(),
        exchange_symbol: "42".to_string(),
        product_symbol: "BTC-USDC-SWAP".to_string(),
        product_type: "swap".to_string(),
        exchange_type: "swap".to_string(),
        price_precision: "0.01".to_string(),
        size_precision: "0.001".to_string(),
        min_size: "0.001".to_string(),
        base_currency: "BTC".to_string(),
        quote_currency: "USDC".to_string(),
        min_notional: "1".to_string(),
        size_per_contract: "1".to_string(),
        ..MarketInfo::default()
    };
    let mut robinhood = mainnet.clone();
    robinhood.exchange = "lighter_robinhood".to_string();
    robinhood.exchange_symbol = "77".to_string();
    let table = ProductTable::new(vec![mainnet, robinhood]);
    let client = LighterClient::with_network(Duration::from_secs(10), LighterNetwork::Robinhood)
        .expect("Robinhood client")
        .with_product_table(table);
    assert_eq!(
        client.market_id("BTC-USDC-SWAP").expect("Robinhood market"),
        "77"
    );
}

#[test]
fn export_sends_resolved_market_id_with_configured_account_index() {
    let (base_url, handle) = recording_server();
    let table = ProductTable::new(vec![MarketInfo {
        exchange: "lighter".to_string(),
        exchange_symbol: "42".to_string(),
        product_symbol: "BTC-USDC-SWAP".to_string(),
        product_type: "swap".to_string(),
        exchange_type: "swap".to_string(),
        price_precision: "0.01".to_string(),
        size_precision: "0.001".to_string(),
        min_size: "0.001".to_string(),
        base_currency: "BTC".to_string(),
        quote_currency: "USDC".to_string(),
        min_notional: "1".to_string(),
        size_per_contract: "1".to_string(),
        ..MarketInfo::default()
    }]);
    let client = LighterClient::with_base_url_and_credentials(
        Duration::from_secs(10),
        base_url,
        Some(12),
        None,
        None,
    )
    .expect("client")
    .with_product_table(table);

    block_on(async move {
        client
            .private_request(
                "get_export",
                vec![
                    ("product_symbol".to_string(), "BTC-USDC-SWAP".to_string()),
                    ("type".to_string(), "trade".to_string()),
                    ("aggregate".to_string(), "true".to_string()),
                    ("authorization".to_string(), "token".to_string()),
                ],
            )
            .await
    })
    .expect("export request");

    let request_line = handle.join().expect("server").expect("request line");
    assert!(request_line.starts_with("GET /api/v1/export?"));
    assert!(request_line.contains("market_id=42"));
    assert!(request_line.contains("type=trade"));
    assert!(request_line.contains("account_index=12"));
    assert!(request_line.contains("aggregate=true"));
    assert!(!request_line.contains("product_symbol="));
}

#[test]
fn new_market_queries_follow_official_paths() {
    let cases = [
        (
            "get_mark_price_candles",
            vec![
                ("market_id", "1"),
                ("resolution", "1h"),
                ("start_timestamp", "1000"),
                ("end_timestamp", "2000"),
                ("count_back", "10"),
            ],
            "/api/v1/markPriceCandles?",
        ),
        (
            "get_market_price_charts",
            vec![("market_ids", "1"), ("market_ids", "2")],
            "/api/v1/marketPriceCharts?market_ids=1&market_ids=2",
        ),
        (
            "get_synthetic_spot_info",
            vec![("symbol", "AAPL")],
            "/api/v1/syntheticSpotInfo?symbol=AAPL",
        ),
    ];
    for (method, params, expected) in cases {
        let (base_url, handle) = recording_server();
        let client =
            LighterClient::with_base_url(Duration::from_secs(10), base_url).expect("client");
        let params = params
            .into_iter()
            .map(|(key, value)| (key.to_string(), value.to_string()))
            .collect();
        block_on(async move { client.public_request(method, params).await }).expect("request");
        let line = handle.join().expect("server").expect("request line");
        assert!(line.starts_with(&format!("GET {expected}")), "{line}");
    }
}

#[test]
fn robinhood_client_uses_explicit_profile() {
    let client = LighterClient::with_network(Duration::from_secs(10), LighterNetwork::Robinhood)
        .expect("client");

    assert_eq!(client.network(), Some(LighterNetwork::Robinhood));
    assert_eq!(client.base_url(), "https://api.rh.lighter.xyz");
    assert_eq!(client.chain_id(), Some(466_324));
}
