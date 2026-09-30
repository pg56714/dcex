use super::helpers::*;

#[test]
fn signer_matches_python_implementation() {
    let signer = BinanceSigner {
        api_key: "api-key".to_string(),
        api_secret: "secret".to_string(),
        timestamp_offset_ms: Arc::new(Mutex::new(None)),
    };
    let mut request = HttpRequest::new(HttpMethod::Get, SPOT_BASE_URL, "/api/v3/order");
    request.query = vec![
        ("symbol".to_string(), "BTCUSDT".to_string()),
        ("side".to_string(), "BUY".to_string()),
    ];

    signer
        .sign(&mut request, 1_700_000_000_000)
        .expect("signature");

    assert_eq!(
        request.query,
        vec![
            ("symbol".to_string(), "BTCUSDT".to_string()),
            ("side".to_string(), "BUY".to_string()),
            ("timestamp".to_string(), "1700000000000".to_string()),
            ("recvWindow".to_string(), "5000".to_string()),
            (
                "signature".to_string(),
                "5858226bd5a361c8dd587d4da2c1d479758c21380d4913cea33235d3f32dd987".to_string(),
            ),
        ]
    );
    assert_eq!(
        request.headers.get("X-MBX-APIKEY").map(String::as_str),
        Some("api-key")
    );
}

#[test]
fn signer_applies_timestamp_offset() {
    let signer = BinanceSigner {
        api_key: "api-key".to_string(),
        api_secret: "secret".to_string(),
        timestamp_offset_ms: Arc::new(Mutex::new(Some(-1_500))),
    };
    let mut request = HttpRequest::new(HttpMethod::Get, SPOT_BASE_URL, "/api/v3/order");

    signer
        .sign(&mut request, 1_700_000_000_000)
        .expect("signature");

    assert_eq!(
        request
            .query
            .iter()
            .find(|(key, _)| key == "timestamp")
            .map(|(_, value)| value.as_str()),
        Some("1699999998500")
    );
}

#[test]
fn coin_futures_balance_uses_dapi_signed_route() {
    let (coin_base_url, handle) = recording_server_after_time_sync();
    let client = BinanceClient::new(
        Some("api-key".into()),
        Some("secret".into()),
        Duration::from_secs(2),
    )
    .expect("client")
    .with_coin_futures_base_url(coin_base_url);
    block_on(async move {
        client
            .private_request("get_coin_futures_balance", Vec::new())
            .await
    })
    .expect("response");
    assert!(
        handle
            .join()
            .expect("server")
            .expect("request")
            .starts_with("GET /dapi/v1/balance?")
    );
}

#[test]
fn options_order_uses_dedicated_signed_path() {
    let (options_base_url, handle) = recording_server_after_time_sync();
    let client = BinanceClient::with_all_base_urls(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(10),
        "http://127.0.0.1:9".to_string(),
        "http://127.0.0.1:9".to_string(),
        options_base_url,
    )
    .expect("client");

    block_on(async move {
        client
            .private_request(
                "place_options_order",
                vec![
                    (
                        "product_symbol".to_string(),
                        "BTC-260925-100000-C".to_string(),
                    ),
                    ("side".to_string(), "buy".to_string()),
                    ("type".to_string(), "limit".to_string()),
                    ("quantity".to_string(), "0.01".to_string()),
                    ("price".to_string(), "1".to_string()),
                    ("timeInForce".to_string(), "GTC".to_string()),
                ],
            )
            .await
    })
    .expect("response");

    assert_eq!(
        handle.join().expect("server"),
        Some("POST /eapi/v1/order HTTP/1.1".to_string())
    );
}

#[test]
fn equity_order_uses_dedicated_signed_path() {
    let (spot_base_url, handle) = recording_server_after_time_sync();
    let client = BinanceClient::with_base_urls(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(10),
        spot_base_url,
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");

    block_on(async move {
        client
            .private_request(
                "place_equity_order",
                vec![
                    ("product_symbol".to_string(), "AAPL-USDC-EQUITY".to_string()),
                    ("side".to_string(), "SELL".to_string()),
                    ("orderType".to_string(), "MARKET".to_string()),
                    ("quantity".to_string(), "0.5".to_string()),
                ],
            )
            .await
    })
    .expect("response");

    assert_eq!(
        handle.join().expect("server"),
        Some("POST /sapi/v1/equity/order/place HTTP/1.1".to_string())
    );
}

#[test]
fn signer_preserves_a_custom_recv_window() {
    let signer = BinanceSigner {
        api_key: "api-key".to_string(),
        api_secret: "secret".to_string(),
        timestamp_offset_ms: Arc::new(Mutex::new(None)),
    };
    let mut request = HttpRequest::new(
        HttpMethod::Post,
        SPOT_BASE_URL,
        "/sapi/v1/equity/order/place",
    )
    .form(vec![("recvWindow".to_string(), "9000".to_string())]);

    signer
        .sign(&mut request, 1_700_000_000_000)
        .expect("signature");

    let crate::http::RequestBody::Form(params) = request.body else {
        panic!("expected form body");
    };
    assert_eq!(
        params
            .iter()
            .filter(|(key, _)| key == "recvWindow")
            .collect::<Vec<_>>(),
        vec![&("recvWindow".to_string(), "9000".to_string())]
    );
}

#[test]
fn margin_market_data_uses_spot_base_url_and_api_key() {
    let (spot_base_url, handle) = recording_server();
    let client = BinanceClient::with_base_urls(
        Some("api-key".to_string()),
        None,
        Duration::from_secs(10),
        spot_base_url,
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");

    block_on(async move {
        client
            .private_request(
                "get_margin_price_index",
                vec![("product_symbol".to_string(), "BTC-USDT-SPOT".to_string())],
            )
            .await
    })
    .expect("response");

    assert_eq!(
        handle.join().expect("server"),
        Some("GET /sapi/v1/margin/priceIndex?symbol=BTCUSDT HTTP/1.1".to_string())
    );
}

#[test]
fn futures_listen_key_keepalive_and_close_send_no_parameters() {
    for (name, method) in [
        ("keep_alive_futures_listen_key", "PUT"),
        ("close_futures_listen_key", "DELETE"),
    ] {
        let (futures_base_url, handle) = recording_server();
        let client = BinanceClient::with_base_urls(
            Some("api-key".to_string()),
            None,
            Duration::from_secs(10),
            "http://127.0.0.1:9".to_string(),
            futures_base_url,
        )
        .expect("client");

        block_on(async move {
            client
                .private_request(name, vec![("listenKey".to_string(), "k".to_string())])
                .await
        })
        .expect("response");

        assert_eq!(
            handle.join().expect("server"),
            Some(format!("{method} /fapi/v1/listenKey HTTP/1.1"))
        );
    }
}

#[test]
fn margin_order_uses_signed_margin_path() {
    let (spot_base_url, handle) = recording_server_after_time_sync();
    let client = BinanceClient::with_base_urls(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(10),
        spot_base_url,
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");

    block_on(async move {
        client
            .private_request(
                "place_margin_order",
                vec![
                    ("product_symbol".to_string(), "BTC-USDT-SPOT".to_string()),
                    ("side".to_string(), "buy".to_string()),
                    ("type".to_string(), "limit".to_string()),
                    ("quantity".to_string(), "0.001".to_string()),
                    ("price".to_string(), "1".to_string()),
                    ("timeInForce".to_string(), "GTC".to_string()),
                    (
                        "sideEffectType".to_string(),
                        "auto_borrow_repay".to_string(),
                    ),
                    ("isIsolated".to_string(), "true".to_string()),
                ],
            )
            .await
    })
    .expect("response");

    assert_eq!(
        handle.join().expect("server"),
        Some("POST /sapi/v1/margin/order HTTP/1.1".to_string())
    );
}

#[test]
fn simple_earn_products_use_signed_spot_path() {
    let (spot_base_url, handle) = recording_server_after_time_sync();
    let client = BinanceClient::with_base_urls(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(10),
        spot_base_url,
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");

    block_on(async move {
        client
            .private_request(
                "get_flexible_earn_products",
                vec![
                    ("asset".to_string(), "USDT".to_string()),
                    ("size".to_string(), "10".to_string()),
                ],
            )
            .await
    })
    .expect("response");

    let request_line = handle.join().expect("server").expect("request line");
    assert!(request_line.contains("/sapi/v1/simple-earn/flexible/list?"));
    assert!(request_line.contains("asset=USDT"));
    assert!(request_line.contains("size=10"));
}

#[test]
fn flexible_loan_assets_use_signed_v2_path() {
    let (spot_base_url, handle) = recording_server_after_time_sync();
    let client = BinanceClient::with_base_urls(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(10),
        spot_base_url,
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");

    block_on(async move {
        client
            .private_request(
                "get_flexible_loan_assets",
                vec![("loanCoin".to_string(), "USDT".to_string())],
            )
            .await
    })
    .expect("response");

    let request_line = handle.join().expect("server").expect("request line");
    assert!(request_line.contains("/sapi/v2/loan/flexible/loanable/data?"));
    assert!(request_line.contains("loanCoin=USDT"));
}

#[test]
fn eth_staking_account_uses_current_signed_path() {
    let (spot_base_url, handle) = recording_server_after_time_sync();
    let client = BinanceClient::with_base_urls(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(10),
        spot_base_url,
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");

    block_on(async move {
        client
            .private_request("get_eth_staking_account", Vec::new())
            .await
    })
    .expect("response");

    let request_line = handle.join().expect("server").expect("request line");
    assert!(request_line.contains("/sapi/v2/eth-staking/account?timestamp="));
}

#[test]
fn subaccount_list_uses_signed_spot_path() {
    let (spot_base_url, handle) = recording_server_after_time_sync();
    let client = BinanceClient::with_base_urls(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(10),
        spot_base_url,
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");

    block_on(async move {
        client
            .private_request(
                "get_subaccounts",
                vec![("limit".to_string(), "10".to_string())],
            )
            .await
    })
    .expect("response");

    let request_line = handle.join().expect("server").expect("request line");
    assert!(request_line.contains("/sapi/v1/sub-account/list?"));
    assert!(request_line.contains("limit=10"));
}

#[test]
fn portfolio_margin_routes_signed_account_and_risk_queries() {
    let (spot_base_url, handle) = recording_server_after_time_sync();
    let client = BinanceClient::with_base_urls(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(10),
        spot_base_url.clone(),
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client")
    .with_portfolio_margin_base_url(spot_base_url);

    block_on(async move { client.get_pm_account().await }).expect("PM account response");

    let request_line = handle.join().expect("server").expect("request line");
    assert!(request_line.starts_with("GET /papi/v1/account?"));
    assert!(request_line.contains("timestamp="));
    assert!(request_line.contains("signature="));
}

#[test]
fn portfolio_margin_algo_order_uses_current_signed_route() {
    let (spot_base_url, handle) = recording_server_after_time_sync();
    let client = BinanceClient::with_base_urls(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(10),
        spot_base_url.clone(),
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client")
    .with_portfolio_margin_base_url(spot_base_url);

    block_on(async move {
        client
            .place_pm_um_algo_order("BTCUSDT", "SELL", "STOP_MARKET")
            .quantity("0.01")
            .param("triggerPrice", "70000")
            .await
    })
    .expect("algo response");
    let request_line = handle.join().expect("server").expect("request line");
    assert_eq!(request_line, "POST /papi/v1/um/algo/order HTTP/1.1");
}

#[test]
fn portfolio_margin_borrow_uses_signed_loan_route() {
    let (spot_base_url, handle) = recording_server_after_time_sync();
    let client = BinanceClient::with_base_urls(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(10),
        spot_base_url.clone(),
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client")
    .with_portfolio_margin_base_url(spot_base_url);
    block_on(async move { client.borrow_pm_margin("USDT", "100").await }).expect("borrow");
    let request_line = handle.join().expect("server").expect("request line");
    assert_eq!(request_line, "POST /papi/v1/marginLoan HTTP/1.1");
}

#[test]
fn portfolio_margin_position_mode_uses_signed_get_route() {
    let (spot_base_url, handle) = recording_server_after_time_sync();
    let client = BinanceClient::with_base_urls(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(10),
        spot_base_url.clone(),
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client")
    .with_portfolio_margin_base_url(spot_base_url);
    block_on(async move { client.get_pm_um_position_mode().await }).expect("position mode");
    let request_line = handle.join().expect("server").expect("request line");
    assert!(request_line.starts_with("GET /papi/v1/um/positionSide/dual?"));
}

#[test]
fn portfolio_margin_repay_debt_uses_signed_route() {
    let (spot_base_url, handle) = recording_server_after_time_sync();
    let client = BinanceClient::with_base_urls(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(10),
        spot_base_url.clone(),
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client")
    .with_portfolio_margin_base_url(spot_base_url);
    block_on(async move {
        client
            .repay_pm_margin_debt("USDT")
            .param("amount", "1")
            .await
    })
    .expect("repay debt");
    let request_line = handle.join().expect("server").expect("request line");
    assert_eq!(request_line, "POST /papi/v1/margin/repay-debt HTTP/1.1");
}

#[test]
fn portfolio_margin_order_amendments_use_signed_route() {
    let (spot_base_url, handle) = recording_server_after_time_sync();
    let client = BinanceClient::with_base_urls(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(10),
        spot_base_url.clone(),
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client")
    .with_portfolio_margin_base_url(spot_base_url);
    block_on(async move { client.get_pm_um_order_amendments("BTCUSDT", "123").await })
        .expect("amendment history");
    let request_line = handle.join().expect("server").expect("request line");
    assert!(request_line.starts_with("GET /papi/v1/um/orderAmendment?"));
    assert!(request_line.contains("orderId=123"));
}
