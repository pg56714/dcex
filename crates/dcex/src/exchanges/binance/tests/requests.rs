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
        Duration::from_secs(2),
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
    let client = BinanceClient::public(Duration::from_secs(2))
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
    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
    let error =
        block_on(async move { client.public_request("get_convert_pairs", Vec::new()).await })
            .expect_err("missing filter");
    assert!(error.to_string().contains("fromAsset or toAsset"));
}

#[test]
fn convert_quote_requires_one_amount_before_network() {
    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
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
        Duration::from_secs(2),
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
        Duration::from_secs(2),
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
    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
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
        Duration::from_secs(2),
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
        Duration::from_secs(2),
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
    }]);
    let client = BinanceClient::public(Duration::from_secs(1))
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
        Duration::from_secs(2),
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
        Duration::from_secs(1),
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
            Duration::from_secs(1),
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
        Duration::from_secs(2),
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
        Duration::from_secs(2),
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
        Duration::from_secs(2),
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
        Duration::from_secs(2),
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
        Duration::from_secs(2),
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
    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
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
    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
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
    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
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
    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
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
    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
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
        Duration::from_secs(2),
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
        Duration::from_secs(2),
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
    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
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
        Duration::from_secs(2),
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
    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
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
        Duration::from_secs(2),
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
        Duration::from_secs(2),
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
        Duration::from_secs(2),
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
    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
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
