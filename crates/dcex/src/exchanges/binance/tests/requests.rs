use super::helpers::*;

#[test]
fn raw_auto_identifies_equity_paths() {
    assert_eq!(
        BinanceMarket::from_path("/sapi/v1/equity/order/place").expect("market"),
        BinanceMarket::Equity
    );
}

#[test]
fn raw_auto_identifies_options_paths() {
    assert_eq!(
        BinanceMarket::from_path("/eapi/v1/exchangeInfo").expect("market"),
        BinanceMarket::Options
    );
}

#[test]
fn raw_auto_identifies_coin_futures_paths() {
    assert_eq!(
        BinanceMarket::from_path("/dapi/v1/exchangeInfo").expect("market"),
        BinanceMarket::CoinFutures
    );
}

#[test]
fn futures_orderbook_uses_fapi_base_url() {
    let (futures_base_url, handle) = recording_server();
    let client = BinanceClient::with_base_urls(
        None,
        None,
        Duration::from_secs(10),
        "http://127.0.0.1:9".to_string(),
        futures_base_url,
    )
    .expect("client");
    block_on(async move { client.get_futures_orderbook("BTC-USDT-SWAP").limit(5).await })
        .expect("response");
    assert_eq!(
        handle.join().expect("server"),
        Some("GET /fapi/v1/depth?symbol=BTCUSDT&limit=5 HTTP/1.1".to_string())
    );
}

#[test]
fn coin_futures_market_data_uses_dapi_base_url() {
    let (coin_base_url, handle) = recording_server();
    let client = BinanceClient::public(Duration::from_secs(10))
        .expect("client")
        .with_coin_futures_base_url(coin_base_url);
    block_on(async move {
        client
            .public_request(
                "get_coin_futures_orderbook",
                vec![
                    ("symbol".into(), "BTCUSD_PERP".into()),
                    ("limit".into(), "5".into()),
                ],
            )
            .await
    })
    .expect("response");
    assert_eq!(
        handle.join().expect("server"),
        Some("GET /dapi/v1/depth?symbol=BTCUSD_PERP&limit=5 HTTP/1.1".to_string())
    );
}

#[test]
fn convert_pairs_require_at_least_one_asset() {
    let client = BinanceClient::public(Duration::from_secs(10)).expect("client");
    let error =
        block_on(async move { client.public_request("get_convert_pairs", Vec::new()).await })
            .expect_err("missing filter");
    assert!(error.to_string().contains("fromAsset or toAsset"));
}

#[test]
fn convert_quote_requires_one_amount_before_network() {
    let client = BinanceClient::public(Duration::from_secs(10)).expect("client");
    let error = block_on(async move {
        client
            .private_request(
                "get_convert_quote",
                vec![
                    ("fromAsset".into(), "BTC".into()),
                    ("toAsset".into(), "USDT".into()),
                    ("fromAmount".into(), "1".into()),
                    ("toAmount".into(), "100".into()),
                ],
            )
            .await
    })
    .expect_err("two amounts");
    assert!(error.to_string().contains("exactly one"));
}

#[test]
fn raw_auto_routes_options_paths_to_options_base_url() {
    let (options_base_url, handle) = recording_server();
    let client = BinanceClient::with_all_base_urls(
        None,
        None,
        Duration::from_secs(10),
        "http://127.0.0.1:9".to_string(),
        "http://127.0.0.1:9".to_string(),
        options_base_url,
    )
    .expect("client");

    let response = client
        .request_raw_auto_blocking(HttpMethod::Get, "/eapi/v1/exchangeInfo", Vec::new(), false)
        .expect("response");

    assert_eq!(response.status, 200);
    assert_eq!(
        handle.join().expect("server"),
        Some("GET /eapi/v1/exchangeInfo HTTP/1.1".to_string())
    );
}

#[test]
fn options_market_data_uses_dedicated_path() {
    let (options_base_url, handle) = recording_server();
    let client = BinanceClient::with_all_base_urls(
        None,
        None,
        Duration::from_secs(10),
        "http://127.0.0.1:9".to_string(),
        "http://127.0.0.1:9".to_string(),
        options_base_url,
    )
    .expect("client");

    block_on(async move {
        client
            .public_request(
                "get_options_orderbook",
                vec![
                    (
                        "product_symbol".to_string(),
                        "BTC-260925-100000-C".to_string(),
                    ),
                    ("limit".to_string(), "10".to_string()),
                ],
            )
            .await
    })
    .expect("response");

    assert_eq!(
        handle.join().expect("server"),
        Some("GET /eapi/v1/depth?limit=10&symbol=BTC-260925-100000-C HTTP/1.1".to_string())
    );
}

#[test]
fn options_order_requires_an_order_identifier_for_lookup() {
    let client = BinanceClient::public(Duration::from_secs(10)).expect("client");
    let error = block_on(async move {
        client
            .private_request(
                "get_options_order",
                vec![(
                    "product_symbol".to_string(),
                    "BTC-260925-100000-C".to_string(),
                )],
            )
            .await
    })
    .expect_err("order identifier must be required");
    assert!(error.to_string().contains("orderId, clientOrderId"));
}

#[test]
fn raw_auto_routes_spot_paths_to_spot_base_url() {
    let (spot_base_url, handle) = recording_server();
    let client = BinanceClient::with_base_urls(
        None,
        None,
        Duration::from_secs(10),
        spot_base_url,
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");

    let response = client
        .request_raw_auto_blocking(
            HttpMethod::Get,
            "/api/v3/exchangeInfo",
            vec![("symbol".to_string(), "BTCUSDT".to_string())],
            false,
        )
        .expect("response");

    assert_eq!(response.status, 200);
    assert_eq!(
        handle.join().expect("server"),
        Some("GET /api/v3/exchangeInfo?symbol=BTCUSDT HTTP/1.1".to_string())
    );
}

#[test]
fn raw_auto_routes_futures_paths_to_futures_base_url() {
    let (futures_base_url, handle) = recording_server();
    let client = BinanceClient::with_base_urls(
        None,
        None,
        Duration::from_secs(10),
        "http://127.0.0.1:9".to_string(),
        futures_base_url,
    )
    .expect("client");

    let response = client
        .request_raw_auto_blocking(HttpMethod::Get, "/fapi/v1/exchangeInfo", Vec::new(), false)
        .expect("response");

    assert_eq!(response.status, 200);
    assert_eq!(
        handle.join().expect("server"),
        Some("GET /fapi/v1/exchangeInfo HTTP/1.1".to_string())
    );
}

#[test]
fn product_table_selects_equity_market() {
    let table = ProductTable::new(vec![crate::product_table::MarketInfo {
        exchange: "binance".to_string(),
        exchange_symbol: "AAPL".to_string(),
        product_symbol: "AAPL-USDC-EQUITY".to_string(),
        product_type: "equity".to_string(),
        exchange_type: "equity".to_string(),
        price_precision: "0.01".to_string(),
        size_precision: "0.0001".to_string(),
        min_size: "0.0001".to_string(),
        base_currency: "AAPL".to_string(),
        quote_currency: "USDC".to_string(),
        min_notional: "1".to_string(),
        size_per_contract: "1".to_string(),
        ..Default::default()
    }]);
    let client = BinanceClient::public(Duration::from_secs(10))
        .expect("client")
        .with_product_table(table);

    assert_eq!(
        client
            .market_for_product_symbol("AAPL-USDC-EQUITY")
            .expect("market"),
        BinanceMarket::Equity
    );
    assert_eq!(
        client.exchange_symbol("AAPL-USDC-EQUITY").expect("symbol"),
        "AAPL"
    );
}

#[test]
fn equity_market_data_uses_dedicated_path() {
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
            .public_request(
                "get_equity_quote",
                vec![("product_symbol".to_string(), "AAPL-USDC-EQUITY".to_string())],
            )
            .await
    })
    .expect("response");

    assert_eq!(
        handle.join().expect("server"),
        Some("GET /sapi/v1/equity/market/quote?symbol=AAPL HTTP/1.1".to_string())
    );
}

#[test]
fn futures_algo_lookup_requires_an_identifier_before_requesting() {
    let client = BinanceClient::new(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(10),
    )
    .expect("client");

    let error = block_on(async move {
        client
            .private_request("cancel_futures_algo_order", Vec::new())
            .await
    })
    .expect_err("missing algo identifier must fail");

    assert_eq!(
        error,
        DcexError::InvalidInput("Either algoId or clientAlgoId is required.".to_string())
    );
}

#[test]
fn order_lookup_requires_an_identifier_before_requesting() {
    for method_name in ["cancel_order", "get_order"] {
        let client = BinanceClient::new(
            Some("api-key".to_string()),
            Some("secret".to_string()),
            Duration::from_secs(10),
        )
        .expect("client");
        let error = block_on(async move {
            client
                .private_request(
                    method_name,
                    vec![("product_symbol".to_string(), "BTC-USDT-SPOT".to_string())],
                )
                .await
        })
        .expect_err("missing order identifier must fail");

        assert_eq!(
            error,
            DcexError::InvalidInput("Either orderId or origClientOrderId is required.".to_string())
        );
    }
}

#[test]
fn current_spot_exchange_info_fields_reach_the_wire() {
    let (spot_base_url, handle) = recording_server();
    let client = BinanceClient::with_base_urls(
        None,
        None,
        Duration::from_secs(10),
        spot_base_url,
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");

    block_on(async move {
        client
            .public_request(
                "get_spot_exchange_info",
                vec![
                    ("permissions".to_string(), "SPOT".to_string()),
                    ("permissions".to_string(), "MARGIN".to_string()),
                    ("showPermissionSets".to_string(), "false".to_string()),
                    ("symbolStatus".to_string(), "TRADING".to_string()),
                ],
            )
            .await
    })
    .expect("response");

    let request_line = handle.join().expect("server").expect("request line");
    assert!(request_line.contains("permissions=%5B%22SPOT%22%2C%22MARGIN%22%5D"));
    assert!(request_line.contains("showPermissionSets=false"));
    assert!(request_line.contains("symbolStatus=TRADING"));
}

#[test]
fn current_spot_kline_fields_reach_the_wire() {
    let (spot_base_url, handle) = recording_server();
    let client = BinanceClient::with_base_urls(
        None,
        None,
        Duration::from_secs(10),
        spot_base_url,
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");

    block_on(async move {
        client
            .public_request(
                "get_klines",
                vec![
                    ("product_symbol".to_string(), "BTC-USDT-SPOT".to_string()),
                    ("interval".to_string(), "1m".to_string()),
                    ("start_time".to_string(), "1".to_string()),
                    ("end_time".to_string(), "2".to_string()),
                    ("time_zone".to_string(), "8".to_string()),
                ],
            )
            .await
    })
    .expect("response");

    let request_line = handle.join().expect("server").expect("request line");
    assert!(request_line.contains("startTime=1"));
    assert!(request_line.contains("endTime=2"));
    assert!(request_line.contains("timeZone=8"));
}

#[test]
fn spot_account_omit_zero_balances_reaches_the_wire() {
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
                "get_account_balance",
                vec![
                    ("market_type".to_string(), "spot".to_string()),
                    ("omitZeroBalances".to_string(), "true".to_string()),
                ],
            )
            .await
    })
    .expect("response");

    let request_line = handle.join().expect("server").expect("request line");
    assert!(request_line.contains("omitZeroBalances=true"));
}

#[test]
fn spot_cancel_fields_reach_the_wire() {
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
                "cancel_order",
                vec![
                    ("product_symbol".to_string(), "BTC-USDT-SPOT".to_string()),
                    ("orderId".to_string(), "1".to_string()),
                    ("newClientOrderId".to_string(), "cancel-1".to_string()),
                    ("cancelRestrictions".to_string(), "ONLY_NEW".to_string()),
                ],
            )
            .await
    })
    .expect("response");

    let request_line = handle.join().expect("server").expect("request line");
    assert!(request_line.contains("newClientOrderId=cancel-1"));
    assert!(request_line.contains("cancelRestrictions=ONLY_NEW"));
}

#[test]
fn futures_account_trade_order_id_reaches_the_wire() {
    let (futures_base_url, handle) = recording_server_after_time_sync();
    let client = BinanceClient::with_base_urls(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(10),
        "http://127.0.0.1:9".to_string(),
        futures_base_url,
    )
    .expect("client");

    block_on(async move {
        client
            .private_request(
                "get_account_trades",
                vec![
                    ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
                    ("orderId".to_string(), "2".to_string()),
                ],
            )
            .await
    })
    .expect("response");

    let request_line = handle.join().expect("server").expect("request line");
    assert!(request_line.contains("/fapi/v1/userTrades?symbol=BTCUSDT&orderId=2"));
}

#[test]
fn margin_order_lookup_requires_an_identifier() {
    let client = BinanceClient::public(Duration::from_secs(10)).expect("client");
    let error = block_on(async move {
        client
            .private_request(
                "get_margin_order",
                vec![("product_symbol".to_string(), "BTC-USDT-SPOT".to_string())],
            )
            .await
    })
    .expect_err("order identifier must be required");

    assert!(error.to_string().contains("orderId or origClientOrderId"));
}

#[test]
fn flexible_earn_partial_redemption_requires_amount() {
    let client = BinanceClient::public(Duration::from_secs(10)).expect("client");
    let error = block_on(async move {
        client
            .private_request(
                "redeem_flexible_earn",
                vec![
                    ("productId".to_string(), "USDT001".to_string()),
                    ("redeemAll".to_string(), "false".to_string()),
                ],
            )
            .await
    })
    .expect_err("partial redemption must require amount");

    assert!(error.to_string().contains("requires amount"));
}

#[test]
fn flexible_loan_borrow_requires_an_amount() {
    let client = BinanceClient::public(Duration::from_secs(10)).expect("client");
    let error = block_on(async move {
        client
            .private_request(
                "borrow_flexible_loan",
                vec![
                    ("loanCoin".to_string(), "USDT".to_string()),
                    ("collateralCoin".to_string(), "BTC".to_string()),
                ],
            )
            .await
    })
    .expect_err("an amount must be required");

    assert!(error.to_string().contains("loanAmount or collateralAmount"));
}

#[test]
fn staking_mutations_require_documented_identifiers() {
    let client = BinanceClient::public(Duration::from_secs(10)).expect("client");
    let error = block_on(async move {
        client
            .private_request("subscribe_onchain_yields", Vec::new())
            .await
    })
    .expect_err("project and amount must be required");

    assert!(error.to_string().contains("projectId"));
}

#[test]
fn subaccount_transfer_requires_internal_account_fields() {
    let client = BinanceClient::public(Duration::from_secs(10)).expect("client");
    let error = block_on(async move {
        client
            .private_request(
                "transfer_between_subaccounts",
                vec![
                    ("fromAccountType".to_string(), "SPOT".to_string()),
                    ("toAccountType".to_string(), "SPOT".to_string()),
                ],
            )
            .await
    })
    .expect_err("asset and amount must be required");

    assert!(error.to_string().contains("asset"));
}

#[test]
fn portfolio_margin_algo_lookup_needs_only_algo_id() {
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
    block_on(async move { client.get_pm_um_algo_order("2146760").await }).expect("algo lookup");
    let request_line = handle.join().expect("server").expect("request line");
    assert!(request_line.starts_with("GET /papi/v1/um/algo/algoOrder?"));
    assert!(request_line.contains("algoId=2146760"));
    assert!(!request_line.contains("symbol="));
}

#[test]
fn portfolio_margin_cm_order_uses_papi_route() {
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
            .place_pm_cm_order("BTCUSD_PERP", "BUY", "LIMIT", "1")
            .price("40000")
            .time_in_force("GTC")
            .await
    })
    .expect("CM order");
    let request_line = handle.join().expect("server").expect("request line");
    assert_eq!(request_line, "POST /papi/v1/cm/order HTTP/1.1");
}

#[test]
fn portfolio_margin_margin_order_requires_price_and_time_in_force() {
    let client = BinanceClient::public(Duration::from_secs(10)).expect("client");
    let error = block_on(async move {
        client
            .place_pm_margin_order("BTCUSDT", "BUY", "LIMIT", "1")
            .await
    })
    .expect_err("LIMIT price required");
    assert!(error.to_string().contains("price"));
}

#[test]
fn portfolio_margin_modify_order_uses_put_route() {
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
            .modify_pm_um_order("BTCUSDT", "BUY", "123", "0.02", "40000")
            .await
    })
    .expect("modify order");
    let request_line = handle.join().expect("server").expect("request line");
    assert_eq!(request_line, "PUT /papi/v1/um/order HTTP/1.1");
}

#[test]
fn portfolio_margin_cm_conditional_requires_trigger_and_uses_route() {
    let client = BinanceClient::public(Duration::from_secs(10)).expect("client");
    let error = block_on(async move {
        client
            .place_pm_cm_conditional_order("BTCUSD_PERP", "SELL", "STOP_MARKET")
            .await
    })
    .expect_err("stop price required");
    assert!(error.to_string().contains("stopPrice"));

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
            .place_pm_cm_conditional_order("BTCUSD_PERP", "SELL", "STOP_MARKET")
            .param("stopPrice", "40000")
            .quantity("1")
            .await
    })
    .expect("CM conditional order");
    let request_line = handle.join().expect("server").expect("request line");
    assert_eq!(request_line, "POST /papi/v1/cm/conditional/order HTTP/1.1");
}

#[test]
fn portfolio_margin_oco_uses_margin_order_oco_route() {
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
            .place_pm_margin_oco("LTCBTC", "SELL", "1", "100", "90")
            .await
    })
    .expect("OCO order");
    let request_line = handle.join().expect("server").expect("request line");
    assert_eq!(request_line, "POST /papi/v1/margin/order/oco HTTP/1.1");
}

#[test]
fn portfolio_margin_cm_conditional_lookup_uses_open_order_route() {
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
            .get_pm_cm_conditional_order("BTCUSD_PERP", "456")
            .await
    })
    .expect("CM conditional order");
    let request_line = handle.join().expect("server").expect("request line");
    assert!(request_line.starts_with("GET /papi/v1/cm/conditional/openOrder?"));
    assert!(request_line.contains("strategyId=456"));
}

#[test]
fn portfolio_margin_cm_trailing_callback_rate_uses_official_range() {
    let client = BinanceClient::public(Duration::from_secs(10)).expect("client");
    let error = block_on(async move {
        client
            .place_pm_cm_conditional_order("BTCUSD_PERP", "SELL", "TRAILING_STOP_MARKET")
            .param("callbackRate", "6")
            .quantity("1")
            .await
    })
    .expect_err("callback above official maximum");
    assert!(error.to_string().contains("callbackRate"));
}

#[test]
fn all_open_orders_market_type_narrows_shared_native_symbol() {
    let row = |product_symbol: &str, product_type: &str| crate::product_table::MarketInfo {
        exchange: "binance".to_string(),
        exchange_symbol: "BTCUSDT".to_string(),
        product_symbol: product_symbol.to_string(),
        product_type: product_type.to_string(),
        ..Default::default()
    };
    let table = ProductTable::new(vec![
        row("BTC-USDT-SPOT", "spot"),
        row("BTC-USDT-SWAP", "swap"),
    ]);
    let (futures_base_url, handle) = recording_server_after_time_sync();
    let client = BinanceClient::with_base_urls(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(10),
        "http://127.0.0.1:9".to_string(),
        futures_base_url,
    )
    .expect("client")
    .with_product_table(table);

    let ambiguous = client.clone();
    let error = block_on(async move {
        ambiguous
            .private_request(
                "get_all_open_orders",
                vec![("product_symbol".to_string(), "BTCUSDT".to_string())],
            )
            .await
    })
    .expect_err("native symbol without market_type is ambiguous");
    assert!(error.to_string().contains("candidates"), "{error}");

    block_on(async move {
        client
            .private_request(
                "get_all_open_orders",
                vec![
                    ("product_symbol".to_string(), "BTCUSDT".to_string()),
                    ("market_type".to_string(), "swap".to_string()),
                ],
            )
            .await
    })
    .expect("response");
    let request_line = handle.join().expect("server").expect("request line");
    assert!(request_line.contains("/fapi/v1/openOrders?symbol=BTCUSDT"));
}

#[test]
fn all_open_orders_rejects_unified_symbol_for_another_market() {
    let client = BinanceClient::with_base_urls(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(10),
        "http://127.0.0.1:9".to_string(),
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");
    let error = block_on(async move {
        client
            .private_request(
                "get_all_open_orders",
                vec![
                    ("product_symbol".to_string(), "BTC-USDT-SPOT".to_string()),
                    ("market_type".to_string(), "swap".to_string()),
                ],
            )
            .await
    })
    .expect_err("conflicting market_type");
    assert!(error.to_string().contains("market_type"), "{error}");
}

#[tokio::test]
async fn every_typed_wrapper_reaches_dispatch() {
    // The typed Rust methods must reach the same dispatch Python calls by name.
    let url = crate::exchanges::wrapper_dispatch::instant_server();
    let client = BinanceClient::with_all_base_urls(
        Some("api-key".into()),
        Some("secret".into()),
        Duration::from_secs(10),
        url.clone(),
        url.clone(),
        url.clone(),
    )
    .expect("client")
    .with_alpha_base_url(url.clone())
    .with_portfolio_margin_base_url(url.clone())
    .with_coin_futures_base_url(url.clone());
    crate::exchanges::wrapper_dispatch::assert_dispatch(
        "binance",
        "BinanceClient",
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

#[tokio::test]
async fn every_typed_request_reaches_dispatch() {
    // Hand-written typed requests (outside the wrapper macro) must reach dispatch too.
    use crate::exchanges::wrapper_dispatch::note_typed_call as note;
    let url = crate::exchanges::wrapper_dispatch::instant_server();
    let client = BinanceClient::with_all_base_urls(
        Some("api-key".into()),
        Some("secret".into()),
        Duration::from_secs(10),
        url.clone(),
        url.clone(),
        url.clone(),
    )
    .expect("client")
    .with_alpha_base_url(url.clone())
    .with_portfolio_margin_base_url(url.clone())
    .with_coin_futures_base_url(url.clone());
    let (mut called, mut failures) = (Vec::new(), Vec::new());
    note(
        &mut called,
        &mut failures,
        "get_income_history",
        client.get_income_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_wallet_balance",
        client.get_wallet_balance().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_funding_wallet",
        client.get_funding_wallet().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "place_options_batch_orders",
        client.place_options_batch_orders("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_options_batch_orders",
        client.cancel_options_batch_orders("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_coin_futures_exchange_info",
        client.get_coin_futures_exchange_info().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_coin_futures_orderbook",
        client.get_coin_futures_orderbook("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_coin_futures_balance",
        client.get_coin_futures_balance().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_coin_futures_positions",
        client.get_coin_futures_positions().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_coin_futures_trades",
        client.get_coin_futures_trades("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_coin_futures_klines",
        client.get_coin_futures_klines("BTCUSDT", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_coin_futures_ticker",
        client.get_coin_futures_ticker().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_coin_futures_mark_price",
        client.get_coin_futures_mark_price().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_coin_futures_funding_rate",
        client.get_coin_futures_funding_rate("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_coin_futures_account",
        client.get_coin_futures_account().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_coin_futures_open_orders",
        client.get_coin_futures_open_orders().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_coin_futures_order",
        client.get_coin_futures_order("BTCUSDT", 1).send().await,
    );
    note(
        &mut called,
        &mut failures,
        "place_coin_futures_order",
        client
            .place_coin_futures_order("BTCUSDT", "BUY", "1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_coin_futures_order",
        client.cancel_coin_futures_order("BTCUSDT", 1).send().await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_all_coin_futures_orders",
        client
            .cancel_all_coin_futures_orders("BTCUSDT")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "place_coin_futures_limit_order",
        client
            .place_coin_futures_limit_order("BTCUSDT", "BUY", "1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "get_convert_pairs",
        client.get_convert_pairs().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_convert_asset_info",
        client.get_convert_asset_info().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_convert_quote",
        client.get_convert_quote("1", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "accept_convert_quote",
        client.accept_convert_quote("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_convert_order_status",
        client.get_convert_order_status("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_convert_trade_history",
        client.get_convert_trade_history(1, 1).send().await,
    );
    note(
        &mut called,
        &mut failures,
        "place_convert_limit_order",
        client
            .place_convert_limit_order("1", "1", "1", "BUY", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_convert_limit_order",
        client.cancel_convert_limit_order(1).send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_open_convert_limit_orders",
        client.get_open_convert_limit_orders().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_simple_earn_account",
        client.get_simple_earn_account().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_flexible_earn_products",
        client.get_flexible_earn_products().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_locked_earn_products",
        client.get_locked_earn_products().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_flexible_earn_positions",
        client.get_flexible_earn_positions().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_locked_earn_positions",
        client.get_locked_earn_positions().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "subscribe_flexible_earn",
        client.subscribe_flexible_earn("1", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "subscribe_locked_earn",
        client.subscribe_locked_earn("1", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "redeem_flexible_earn",
        client.redeem_flexible_earn("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "redeem_locked_earn",
        client.redeem_locked_earn("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_flexible_earn_subscription_history",
        client.get_flexible_earn_subscription_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_locked_earn_subscription_history",
        client.get_locked_earn_subscription_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_flexible_earn_redemption_history",
        client.get_flexible_earn_redemption_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_locked_earn_redemption_history",
        client.get_locked_earn_redemption_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_flexible_earn_rewards_history",
        client.get_flexible_earn_rewards_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_locked_earn_rewards_history",
        client.get_locked_earn_rewards_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_equity_exchange_info",
        client.get_equity_exchange_info().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_equity_tokenized_assets",
        client.get_equity_tokenized_assets().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_equity_quote",
        client.get_equity_quote("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "place_equity_order",
        client
            .place_equity_order("BTCUSDT", "BUY", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_equity_order",
        client.cancel_equity_order("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_all_equity_orders",
        client.cancel_all_equity_orders().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_open_equity_orders",
        client.get_open_equity_orders().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_equity_order_history",
        client.get_equity_order_history(1, 1).send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_equity_order_detail",
        client.get_equity_order_detail("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_equity_trade_history",
        client.get_equity_trade_history(1, 1).send().await,
    );
    note(
        &mut called,
        &mut failures,
        "mint_equity_token",
        client.mint_equity_token("1", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "redeem_equity_token",
        client.redeem_equity_token("1", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_equity_convert_status",
        client.get_equity_convert_status("1", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_equity_convert_history",
        client.get_equity_convert_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "sign_equity_disclaimer",
        client.sign_equity_disclaimer().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "create_or_renew_equity_listen_key",
        client.create_or_renew_equity_listen_key().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "check_flexible_loan_collateral_repay_rate",
        client
            .check_flexible_loan_collateral_repay_rate("1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "adjust_flexible_loan_ltv",
        client
            .adjust_flexible_loan_ltv("1", "1", "1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "borrow_flexible_loan",
        client.borrow_flexible_loan("1", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "repay_flexible_loan",
        client.repay_flexible_loan("1", "1", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_flexible_loan_assets",
        client.get_flexible_loan_assets().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_flexible_loan_borrow_history",
        client.get_flexible_loan_borrow_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_flexible_loan_collateral_assets",
        client.get_flexible_loan_collateral_assets().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_flexible_loan_interest_rate_history",
        client
            .get_flexible_loan_interest_rate_history("1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "get_flexible_loan_liquidation_history",
        client.get_flexible_loan_liquidation_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_flexible_loan_ltv_adjustment_history",
        client
            .get_flexible_loan_ltv_adjustment_history()
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "get_flexible_loan_ongoing_orders",
        client.get_flexible_loan_ongoing_orders().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_flexible_loan_repayment_history",
        client.get_flexible_loan_repayment_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_crypto_loan_income_history",
        client.get_crypto_loan_income_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_stable_loan_borrow_history",
        client.get_stable_loan_borrow_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_stable_loan_ltv_adjustment_history",
        client.get_stable_loan_ltv_adjustment_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_stable_loan_repayment_history",
        client.get_stable_loan_repayment_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_all_margin_assets",
        client.get_all_margin_assets().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_all_cross_margin_pairs",
        client.get_all_cross_margin_pairs().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_all_isolated_margin_symbols",
        client.get_all_isolated_margin_symbols().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_margin_price_index",
        client.get_margin_price_index("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_cross_margin_account",
        client.get_cross_margin_account().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_isolated_margin_account",
        client.get_isolated_margin_account().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "margin_borrow_repay",
        client.margin_borrow_repay("1", "1", "1", true).send().await,
    );
    note(
        &mut called,
        &mut failures,
        "borrow_margin_asset",
        client.borrow_margin_asset("1", "1", true).send().await,
    );
    note(
        &mut called,
        &mut failures,
        "repay_margin_asset",
        client.repay_margin_asset("1", "1", true).send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_margin_borrow_repay_records",
        client.get_margin_borrow_repay_records("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_margin_interest_history",
        client.get_margin_interest_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_margin_max_borrowable",
        client.get_margin_max_borrowable("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_margin_max_transferable",
        client.get_margin_max_transferable("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "place_margin_order",
        client
            .place_margin_order("BTCUSDT", "BUY", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_margin_order",
        client.cancel_margin_order("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_margin_order",
        client.get_margin_order("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_open_margin_orders",
        client.get_open_margin_orders().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_all_open_margin_orders",
        client.cancel_all_open_margin_orders("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_all_margin_orders",
        client.get_all_margin_orders("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_margin_account_trades",
        client.get_margin_account_trades("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_spot_exchange_info",
        client.get_spot_exchange_info().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_spot_orderbook",
        client.get_spot_orderbook("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_spot_trades",
        client.get_spot_trades("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_spot_price",
        client.get_spot_price().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_klines",
        client.get_klines("BTCUSDT", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_futures_orderbook",
        client.get_futures_orderbook("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_futures_ticker",
        client.get_futures_ticker().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_futures_premium_index",
        client.get_futures_premium_index().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_futures_funding_rate",
        client.get_futures_funding_rate().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_futures_open_interest_history",
        client
            .get_futures_open_interest_history("BTCUSDT", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "get_futures_global_long_short_account_ratio",
        client
            .get_futures_global_long_short_account_ratio("BTCUSDT", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "get_futures_top_long_short_account_ratio",
        client
            .get_futures_top_long_short_account_ratio("BTCUSDT", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "get_futures_top_long_short_position_ratio",
        client
            .get_futures_top_long_short_position_ratio("BTCUSDT", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "get_futures_taker_buy_sell_volume",
        client
            .get_futures_taker_buy_sell_volume("BTCUSDT", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "get_futures_basis",
        client.get_futures_basis("BTCUSDT", "1", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_options_exchange_info",
        client.get_options_exchange_info().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_options_index_price",
        client.get_options_index_price("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_options_exercise_history",
        client.get_options_exercise_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_options_klines",
        client.get_options_klines("BTCUSDT", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_options_open_interest",
        client.get_options_open_interest("1", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_options_mark_price",
        client.get_options_mark_price().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_options_orderbook",
        client.get_options_orderbook("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_options_block_trades",
        client.get_options_block_trades().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_options_trades",
        client.get_options_trades("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "ping_options",
        client.ping_options().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_options_ticker",
        client.get_options_ticker().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "place_options_order",
        client
            .place_options_order("BTCUSDT", "BUY", "1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "get_options_account_bill",
        client.get_options_account_bill("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_options_margin_account",
        client.get_options_margin_account().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_options_account_trades",
        client.get_options_account_trades("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_all_options_orders_by_underlying",
        client
            .cancel_all_options_orders_by_underlying("1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_all_options_orders",
        client.cancel_all_options_orders("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_options_order",
        client.get_options_order("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_options_order",
        client.cancel_options_order("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_options_positions",
        client.get_options_positions().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_open_options_orders",
        client.get_open_options_orders().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_options_order_history",
        client.get_options_order_history("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_options_commission",
        client.get_options_commission().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_options_exercise_records",
        client.get_options_exercise_records().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "create_options_listen_key",
        client.create_options_listen_key().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "keep_alive_options_listen_key",
        client.keep_alive_options_listen_key().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "close_options_listen_key",
        client.close_options_listen_key().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_account",
        client.get_pm_account().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_um_account",
        client.get_pm_um_account().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_um_position_risk",
        client.get_pm_um_position_risk().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_um_open_orders",
        client.get_pm_um_open_orders().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_um_order",
        client.get_pm_um_order("BTCUSDT", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_pm_um_order",
        client.cancel_pm_um_order("BTCUSDT", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_all_pm_um_orders",
        client.cancel_all_pm_um_orders("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "place_pm_um_order",
        client
            .place_pm_um_order("BTCUSDT", "BUY", "1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "place_pm_um_algo_order",
        client
            .place_pm_um_algo_order("BTCUSDT", "BUY", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_um_algo_order",
        client.get_pm_um_algo_order("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_um_algo_order_by_client_id",
        client.get_pm_um_algo_order_by_client_id("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_pm_um_algo_order",
        client.cancel_pm_um_algo_order("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_pm_um_algo_order_by_client_id",
        client
            .cancel_pm_um_algo_order_by_client_id("1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_all_pm_um_algo_orders",
        client.cancel_all_pm_um_algo_orders("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_um_open_algo_orders",
        client.get_pm_um_open_algo_orders().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_um_algo_order_history",
        client.get_pm_um_algo_order_history("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_cm_account",
        client.get_pm_cm_account().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_cm_position_risk",
        client.get_pm_cm_position_risk().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_um_account_config",
        client.get_pm_um_account_config().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_um_symbol_config",
        client.get_pm_um_symbol_config().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_um_leverage_bracket",
        client.get_pm_um_leverage_bracket().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_um_api_trading_status",
        client.get_pm_um_api_trading_status().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_cm_adl_quantile",
        client.get_pm_cm_adl_quantile("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_margin_max_borrowable",
        client.get_pm_margin_max_borrowable("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_um_force_orders",
        client.get_pm_um_force_orders().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_cm_force_orders",
        client.get_pm_cm_force_orders().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_margin_force_orders",
        client.get_pm_margin_force_orders().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_um_all_orders",
        client.get_pm_um_all_orders("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_um_user_trades",
        client.get_pm_um_user_trades("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_cm_open_orders",
        client.get_pm_cm_open_orders().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_cm_all_orders",
        client.get_pm_cm_all_orders("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_cm_user_trades",
        client.get_pm_cm_user_trades("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_margin_open_orders",
        client.get_pm_margin_open_orders().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_margin_all_orders",
        client.get_pm_margin_all_orders("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_margin_trades",
        client.get_pm_margin_trades("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "place_pm_cm_order",
        client
            .place_pm_cm_order("BTCUSDT", "BUY", "1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "place_pm_margin_order",
        client
            .place_pm_margin_order("BTCUSDT", "BUY", "1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_cm_order",
        client.get_pm_cm_order("BTCUSDT", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_pm_cm_order",
        client.cancel_pm_cm_order("BTCUSDT", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_margin_order",
        client.get_pm_margin_order("BTCUSDT", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_pm_margin_order",
        client.cancel_pm_margin_order("BTCUSDT", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_all_pm_cm_orders",
        client.cancel_all_pm_cm_orders("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_all_pm_margin_orders",
        client.cancel_all_pm_margin_orders("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "modify_pm_um_order",
        client
            .modify_pm_um_order("BTCUSDT", "BUY", "1", "1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "modify_pm_cm_order",
        client
            .modify_pm_cm_order("BTCUSDT", "BUY", "1", "1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "borrow_pm_margin",
        client.borrow_pm_margin("1", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "repay_pm_margin",
        client.repay_pm_margin("1", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "place_pm_cm_conditional_order",
        client
            .place_pm_cm_conditional_order("BTCUSDT", "BUY", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_pm_cm_conditional_order",
        client
            .cancel_pm_cm_conditional_order("BTCUSDT", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_all_pm_cm_conditional_orders",
        client
            .cancel_all_pm_cm_conditional_orders("BTCUSDT")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_cm_conditional_order",
        client
            .get_pm_cm_conditional_order("BTCUSDT", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_cm_conditional_order_history",
        client
            .get_pm_cm_conditional_order_history("BTCUSDT")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_cm_open_conditional_orders",
        client.get_pm_cm_open_conditional_orders().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_cm_all_conditional_orders",
        client.get_pm_cm_all_conditional_orders().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "place_pm_margin_oco",
        client
            .place_pm_margin_oco("BTCUSDT", "BUY", "1", "1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_margin_oco",
        client.get_pm_margin_oco("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_pm_margin_oco",
        client.cancel_pm_margin_oco("BTCUSDT", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_margin_open_oco",
        client.get_pm_margin_open_oco().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_margin_all_oco",
        client.get_pm_margin_all_oco().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_balance",
        client.get_pm_balance().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_cm_leverage_bracket",
        client.get_pm_cm_leverage_bracket().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "set_pm_um_leverage",
        client.set_pm_um_leverage("BTCUSDT", 1).send().await,
    );
    note(
        &mut called,
        &mut failures,
        "set_pm_cm_leverage",
        client.set_pm_cm_leverage("BTCUSDT", 1).send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_um_position_mode",
        client.get_pm_um_position_mode().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_cm_position_mode",
        client.get_pm_cm_position_mode().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "set_pm_um_position_mode",
        client.set_pm_um_position_mode(true).send().await,
    );
    note(
        &mut called,
        &mut failures,
        "set_pm_cm_position_mode",
        client.set_pm_cm_position_mode(true).send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_um_adl_quantile",
        client.get_pm_um_adl_quantile().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "repay_pm_margin_debt",
        client.repay_pm_margin_debt("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_um_order_amendments",
        client
            .get_pm_um_order_amendments("BTCUSDT", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "get_pm_cm_order_amendments",
        client
            .get_pm_cm_order_amendments("BTCUSDT", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "create_oco_order",
        client.create_oco_order("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "create_oto_order",
        client.create_oto_order("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "create_otoco_order",
        client.create_otoco_order("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_prevented_matches",
        client.get_prevented_matches("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_allocations",
        client.get_allocations("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_order_rate_limit",
        client.get_order_rate_limit().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "redeem_eth_staking",
        client.redeem_eth_staking("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "subscribe_eth_staking",
        client.subscribe_eth_staking("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "wrap_beth",
        client.wrap_beth("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_onchain_yields_personal_quota",
        client.get_onchain_yields_personal_quota("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "preview_onchain_yields_subscription",
        client
            .preview_onchain_yields_subscription("1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "subscribe_onchain_yields",
        client.subscribe_onchain_yields("1", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "redeem_onchain_yields",
        client.redeem_onchain_yields("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "set_onchain_yields_auto_subscribe",
        client
            .set_onchain_yields_auto_subscribe("1", true)
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "set_onchain_yields_redeem_option",
        client
            .set_onchain_yields_redeem_option("1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "set_soft_staking",
        client.set_soft_staking(true).send().await,
    );
    note(
        &mut called,
        &mut failures,
        "subscribe_sol_staking",
        client.subscribe_sol_staking("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "redeem_sol_staking",
        client.redeem_sol_staking("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_eth_staking_account",
        client.get_eth_staking_account().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_eth_staking_quota",
        client.get_eth_staking_quota().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_eth_redemption_history",
        client.get_eth_redemption_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_eth_staking_history",
        client.get_eth_staking_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_wbeth_rate_history",
        client.get_wbeth_rate_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_wbeth_rewards_history",
        client.get_wbeth_rewards_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_wbeth_unwrap_history",
        client.get_wbeth_unwrap_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_wbeth_wrap_history",
        client.get_wbeth_wrap_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_onchain_yields_products",
        client.get_onchain_yields_products().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_onchain_yields_positions",
        client.get_onchain_yields_positions().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_onchain_yields_redemption_history",
        client.get_onchain_yields_redemption_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_onchain_yields_rewards_history",
        client.get_onchain_yields_rewards_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_onchain_yields_subscription_history",
        client
            .get_onchain_yields_subscription_history()
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "get_onchain_yields_account",
        client.get_onchain_yields_account().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_soft_staking_products",
        client.get_soft_staking_products().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_soft_staking_rewards_history",
        client.get_soft_staking_rewards_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_sol_staking_account",
        client.get_sol_staking_account().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_sol_staking_quota",
        client.get_sol_staking_quota().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_bnsol_rate_history",
        client.get_bnsol_rate_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_bnsol_rewards_history",
        client.get_bnsol_rewards_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_sol_boost_rewards_history",
        client.get_sol_boost_rewards_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_sol_redemption_history",
        client.get_sol_redemption_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_sol_staking_history",
        client.get_sol_staking_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_sol_unclaimed_rewards",
        client.get_sol_unclaimed_rewards().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "claim_sol_boost_rewards",
        client.claim_sol_boost_rewards().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_subaccounts",
        client.get_subaccounts().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_subaccount_status",
        client.get_subaccount_status().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_subaccount_transaction_statistics",
        client.get_subaccount_transaction_statistics().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_subaccount_futures_position_risk",
        client.get_subaccount_futures_position_risk().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_subaccount_futures_account",
        client.get_subaccount_futures_account().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_subaccount_margin_account",
        client.get_subaccount_margin_account().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_subaccount_futures_summary",
        client.get_subaccount_futures_summary().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_subaccount_margin_summary",
        client.get_subaccount_margin_summary().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_subaccount_assets",
        client.get_subaccount_assets().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_subaccount_spot_summary",
        client.get_subaccount_spot_summary().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_subaccount_futures_transfer_history",
        client
            .get_subaccount_futures_transfer_history()
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "get_subaccount_spot_transfer_history",
        client.get_subaccount_spot_transfer_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_subaccount_universal_transfer_history",
        client
            .get_subaccount_universal_transfer_history()
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "get_subaccount_transfer_history",
        client.get_subaccount_transfer_history().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "place_order",
        client.place_order("BTCUSDT", "BUY", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "test_order",
        client.test_order("BTCUSDT", "BUY", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "place_futures_algo_order",
        client
            .place_futures_algo_order("BTCUSDT", "BUY", "1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_futures_algo_order",
        client.cancel_futures_algo_order().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_futures_algo_order",
        client.get_futures_algo_order().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_all_open_futures_algo_orders",
        client.get_all_open_futures_algo_orders().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_all_futures_algo_orders",
        client.get_all_futures_algo_orders("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "place_market_order",
        client
            .place_market_order("BTCUSDT", "BUY", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "place_market_buy_order",
        client.place_market_buy_order("BTCUSDT", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "place_market_sell_order",
        client.place_market_sell_order("BTCUSDT", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "place_limit_order",
        client
            .place_limit_order("BTCUSDT", "BUY", "1", "1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "place_limit_buy_order",
        client
            .place_limit_buy_order("BTCUSDT", "1", "1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "place_limit_sell_order",
        client
            .place_limit_sell_order("BTCUSDT", "1", "1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "place_post_only_limit_order",
        client
            .place_post_only_limit_order("BTCUSDT", "BUY", "1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "place_post_only_limit_buy_order",
        client
            .place_post_only_limit_buy_order("BTCUSDT", "1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "place_post_only_limit_sell_order",
        client
            .place_post_only_limit_sell_order("BTCUSDT", "1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "cancel_order",
        client.cancel_order("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_order",
        client.get_order("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_open_orders",
        client.get_open_orders("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_all_open_orders",
        client.get_all_open_orders().send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_future_all_order",
        client.get_future_all_order("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_all_orders",
        client.get_all_orders("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_account_trades",
        client.get_account_trades("BTCUSDT").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "create_universal_transfer",
        client.create_universal_transfer("1", "1", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "get_universal_transfer_history",
        client.get_universal_transfer_history("1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "transfer_subaccount_futures",
        client
            .transfer_subaccount_futures("1", "1", "1", 1)
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "transfer_subaccount_margin",
        client
            .transfer_subaccount_margin("1", "1", "1", 1)
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "transfer_between_subaccount_futures",
        client
            .transfer_between_subaccount_futures("1", "1", 1, "1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "transfer_subaccount_to_master",
        client.transfer_subaccount_to_master("1", "1").send().await,
    );
    note(
        &mut called,
        &mut failures,
        "transfer_subaccount_to_subaccount",
        client
            .transfer_subaccount_to_subaccount("1", "1", "1")
            .send()
            .await,
    );
    note(
        &mut called,
        &mut failures,
        "transfer_between_subaccounts",
        client
            .transfer_between_subaccounts("1", "1", "1", "1")
            .send()
            .await,
    );
    crate::exchanges::wrapper_dispatch::assert_typed_requests("binance", called, failures);
}
