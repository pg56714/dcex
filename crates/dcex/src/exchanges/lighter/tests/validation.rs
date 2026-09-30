use super::helpers::*;

#[test]
fn product_table_resolves_canonical_symbol_to_market_id() {
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
    }]);
    let client = LighterClient::new(Duration::from_secs(1))
        .expect("client")
        .with_product_table(table);

    assert_eq!(client.market_id("BTC-USDC-SWAP").expect("market id"), "42");
}

#[test]
fn new_lighter_queries_reject_invalid_parameters_before_network() {
    let client = LighterClient::with_base_url(Duration::from_secs(10), "http://127.0.0.1:1".into())
        .expect("client");
    assert!(
        block_on({
            let client = client.clone();
            async move {
                client
                    .public_request("get_synthetic_spot_info", vec![])
                    .await
            }
        })
        .is_err()
    );
    assert!(
        block_on({
            let client = client.clone();
            async move {
                client
                    .public_request(
                        "get_market_price_charts",
                        vec![("market_ids".into(), "-1".into())],
                    )
                    .await
            }
        })
        .is_err()
    );
    assert!(
        block_on({
            let client = client.clone();
            async move {
                client
                    .public_request(
                        "get_mark_price_candles",
                        vec![
                            ("market_id".into(), "1".into()),
                            ("resolution".into(), "1w".into()),
                            ("start_timestamp".into(), "1".into()),
                            ("end_timestamp".into(), "2".into()),
                            ("count_back".into(), "1".into()),
                        ],
                    )
                    .await
            }
        })
        .is_err()
    );
    assert!(
        block_on(async move {
            client
                .private_request(
                    "get_account_orders",
                    vec![
                        ("account_index".into(), "12".into()),
                        ("client_order_indexes".into(), "1,".into()),
                        ("authorization".into(), "token".into()),
                    ],
                )
                .await
        })
        .is_err()
    );
}

#[test]
fn known_endpoint_rejects_a_mismatched_signing_chain() {
    let result = LighterClient::with_base_url_credentials_and_chain_id(
        Duration::from_secs(10),
        "https://api.rh.lighter.xyz".to_string(),
        304,
        None,
        None,
        None,
    );

    assert!(result.is_err());
}

#[test]
fn rfq_routes_validate_requests_and_keep_maker_response_out_of_scope() {
    for (method, params, route) in [
        (
            "create_rfq",
            vec![
                ("market_index".into(), "1".into()),
                ("direction".into(), "0".into()),
                ("base_amount".into(), "0.1".into()),
                ("authorization".into(), "token".into()),
            ],
            "POST /api/v1/rfq/create HTTP/1.1",
        ),
        (
            "get_rfq",
            vec![
                ("rfq_id".into(), "10".into()),
                ("authorization".into(), "token".into()),
            ],
            "GET /api/v1/rfq/get?rfq_id=10 HTTP/1.1",
        ),
        (
            "list_rfqs",
            vec![
                ("limit".into(), "20".into()),
                ("authorization".into(), "token".into()),
            ],
            "GET /api/v1/rfq/list?limit=20 HTTP/1.1",
        ),
        (
            "update_rfq",
            vec![
                ("rfq_id".into(), "10".into()),
                ("status".into(), "CANCELED".into()),
                ("authorization".into(), "token".into()),
            ],
            "POST /api/v1/rfq/update HTTP/1.1",
        ),
    ] {
        let (base_url, server) = recording_server();
        let client =
            LighterClient::with_base_url(Duration::from_secs(10), base_url).expect("client");
        block_on(async move { client.private_request(method, params).await }).expect(method);
        assert_eq!(server.join().expect("server"), Some(route.to_string()));
    }
    let client = LighterClient::new(Duration::from_secs(10)).expect("client");
    assert!(
        block_on(async move {
            client
                .private_request(
                    "create_rfq",
                    vec![
                        ("market_index".into(), "1".into()),
                        ("direction".into(), "0".into()),
                        ("authorization".into(), "token".into()),
                    ],
                )
                .await
        })
        .is_err()
    );
}
