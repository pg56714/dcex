use super::helpers::*;

#[test]
fn product_symbol_selects_expected_market() {
    assert_eq!(
        market_for_product_symbol_fallback("BTC-USDT-SPOT"),
        BinanceMarket::Spot
    );
    assert_eq!(
        market_for_product_symbol_fallback("BTC-USDT-SWAP"),
        BinanceMarket::Futures
    );
    assert_eq!(
        market_for_product_symbol_fallback("AAPL-USDC-EQUITY"),
        BinanceMarket::Equity
    );
    assert_eq!(exchange_symbol_fallback("AAPL-USDC-EQUITY"), "AAPL");
}

#[test]
fn futures_orderbook_rejects_unsupported_limit() {
    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
    let error =
        block_on(async move { client.get_futures_orderbook("BTC-USDT-SWAP").limit(7).await })
            .expect_err("unsupported limit must be rejected before the request");
    assert!(error.to_string().contains("invalid Binance limit: 7"));
}

#[test]
fn raw_auto_rejects_unsupported_path_prefixes() {
    assert_eq!(
        BinanceMarket::from_path("/unknown"),
        Err(DcexError::InvalidInput(
            "unsupported Binance API path: /unknown".to_string()
        ))
    );
}

#[test]
fn product_table_overrides_symbol_fallback() {
    let table = ProductTable::new(vec![crate::product_table::MarketInfo {
        exchange: "binance".to_string(),
        exchange_symbol: "BTCUSDT_250627".to_string(),
        product_symbol: "BTC-USDT-250627".to_string(),
        product_type: "futures".to_string(),
        exchange_type: "delivery".to_string(),
        price_precision: "0.1".to_string(),
        size_precision: "0.001".to_string(),
        min_size: "0.001".to_string(),
        base_currency: "BTC".to_string(),
        quote_currency: "USDT".to_string(),
        min_notional: "0".to_string(),
        size_per_contract: "1".to_string(),
    }]);
    let client = BinanceClient::public(Duration::from_secs(1))
        .expect("client")
        .with_product_table(table);

    assert_eq!(
        client
            .exchange_symbol("BTC-USDT-250627")
            .expect("exchange symbol"),
        "BTCUSDT_250627"
    );
    assert_eq!(
        client
            .market_for_product_symbol("BTC-USDT-250627")
            .expect("market"),
        BinanceMarket::Futures
    );
}

#[test]
fn equity_order_matrix_is_validated_before_requesting() {
    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
    let error = block_on(async move {
        client
            .private_request(
                "place_equity_order",
                vec![
                    ("product_symbol".to_string(), "AAPL-USDC-EQUITY".to_string()),
                    ("side".to_string(), "BUY".to_string()),
                    ("orderType".to_string(), "MARKET".to_string()),
                    ("quantity".to_string(), "1".to_string()),
                ],
            )
            .await
    })
    .expect_err("BUY MARKET quantity must fail");
    assert!(
        error.to_string().contains("require notional"),
        "unexpected error: {error}"
    );

    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
    let error = block_on(async move {
        client
            .private_request(
                "place_equity_order",
                vec![
                    ("product_symbol".to_string(), "AAPL-USDC-EQUITY".to_string()),
                    ("side".to_string(), "BUY".to_string()),
                    ("orderType".to_string(), "LIMIT".to_string()),
                    ("quantity".to_string(), "1".to_string()),
                    ("price".to_string(), "200".to_string()),
                ],
            )
            .await
    })
    .expect_err("LIMIT without session must fail");
    assert!(error.to_string().contains("tradingSession"));
}

#[test]
fn order_side_is_normalized_and_validated() {
    assert_eq!(normalize_order_side("buy").expect("buy side"), "BUY");
    assert_eq!(normalize_order_side("SELL").expect("sell side"), "SELL");
    assert_eq!(
        normalize_order_side("hold"),
        Err(DcexError::InvalidInput(
            "unsupported Binance order side: hold".to_string()
        ))
    );
}

#[test]
fn spot_account_queries_require_a_product_symbol() {
    for method_name in ["get_prevented_matches", "get_allocations"] {
        let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
        let error = block_on(async move { client.private_request(method_name, Vec::new()).await })
            .expect_err("missing product symbol must fail");

        assert_eq!(
            error,
            DcexError::InvalidInput("Binance product_symbol is required.".to_string())
        );
    }
}

#[test]
fn spot_exchange_info_rejects_documented_filter_conflicts() {
    for conflicting_filter in [("permissions", "SPOT"), ("symbolStatus", "TRADING")] {
        let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
        let error = block_on(async move {
            client
                .public_request(
                    "get_spot_exchange_info",
                    vec![
                        ("product_symbol".to_string(), "BTC-USDT-SPOT".to_string()),
                        (
                            conflicting_filter.0.to_string(),
                            conflicting_filter.1.to_string(),
                        ),
                    ],
                )
                .await
        })
        .expect_err("documented filter conflict must fail");

        assert!(matches!(error, DcexError::InvalidInput(_)));
    }
}

#[test]
fn spot_price_rejects_symbol_and_symbols_together() {
    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
    let error = block_on(async move {
        client
            .public_request(
                "get_spot_price",
                vec![
                    ("product_symbol".to_string(), "BTC-USDT-SPOT".to_string()),
                    ("product_symbols".to_string(), "ETH-USDT-SPOT".to_string()),
                ],
            )
            .await
    })
    .expect_err("symbol and symbols must be mutually exclusive");

    assert_eq!(
        error,
        DcexError::InvalidInput(
            "Binance product_symbol and product_symbols cannot be combined.".to_string()
        )
    );
}

#[test]
fn futures_positions_can_be_queried_without_a_symbol() {
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
            .private_request("get_future_position", Vec::new())
            .await
    })
    .expect("response");

    let request_line = handle.join().expect("server").expect("request line");
    assert!(request_line.contains("/fapi/v3/positionRisk?timestamp="));
    assert!(!request_line.contains("symbol="));
}

#[test]
fn margin_borrow_repay_type_is_validated_before_requesting() {
    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
    let error = block_on(async move {
        client
            .private_request(
                "margin_borrow_repay",
                vec![
                    ("asset".to_string(), "USDT".to_string()),
                    ("amount".to_string(), "1".to_string()),
                    ("type".to_string(), "INVALID".to_string()),
                ],
            )
            .await
    })
    .expect_err("transaction type must be validated");

    assert!(error.to_string().contains("BORROW or REPAY"));
}

#[test]
fn portfolio_margin_order_validation_rejects_invalid_requests() {
    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
    let error = block_on(async move {
        client
            .place_pm_um_order("BTCUSDT", "BUY", "LIMIT", "1")
            .await
    })
    .expect_err("LIMIT orders require a price");
    assert!(error.to_string().contains("price"));

    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
    let error = block_on(async move {
        client
            .private_request(
                "cancel_pm_um_order",
                vec![("product_symbol".into(), "BTCUSDT".into())],
            )
            .await
    })
    .expect_err("cancel requires an order identifier");
    assert!(error.to_string().contains("orderId"));
}

#[test]
fn portfolio_margin_algo_rejects_conflicting_close_all_fields() {
    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
    let error = block_on(async move {
        client
            .place_pm_um_algo_order("BTCUSDT", "SELL", "STOP_MARKET")
            .param("triggerPrice", "70000")
            .quantity("0.01")
            .close_position("true")
            .await
    })
    .expect_err("close all cannot include quantity");
    assert!(error.to_string().contains("closePosition"));

    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
    let error = block_on(async move {
        client
            .place_pm_um_algo_order("BTCUSDT", "SELL", "TRAILING_STOP_MARKET")
            .quantity("0.01")
            .callback_rate("11")
            .await
    })
    .expect_err("callback rate out of range");
    assert!(error.to_string().contains("callbackRate"));
}

#[test]
fn portfolio_margin_cm_risk_uses_pair_not_symbol() {
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
    block_on(async move { client.get_pm_cm_position_risk().pair("BTCUSD").await })
        .expect("CM risk");
    let request_line = handle.join().expect("server").expect("request line");
    assert!(request_line.starts_with("GET /papi/v1/cm/positionRisk?"));
    assert!(request_line.contains("pair=BTCUSD"));
    assert!(!request_line.contains("symbol="));
}

#[test]
fn portfolio_margin_leverage_validates_range_and_uses_signed_route() {
    let client = BinanceClient::public(Duration::from_secs(1)).expect("client");
    let error = block_on(async move { client.set_pm_um_leverage("BTCUSDT", 126).await })
        .expect_err("leverage limit");
    assert!(error.to_string().contains("leverage"));

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
    block_on(async move { client.set_pm_cm_leverage("BTCUSD_PERP", 10).await })
        .expect("CM leverage");
    let request_line = handle.join().expect("server").expect("request line");
    assert_eq!(request_line, "POST /papi/v1/cm/leverage HTTP/1.1");
}

#[test]
fn portfolio_margin_cm_conditional_history_accepts_symbol_without_id() {
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
            .get_pm_cm_conditional_order_history("BTCUSD_PERP")
            .await
    })
    .expect("CM history");
    let request_line = handle.join().expect("server").expect("request line");
    assert!(request_line.starts_with("GET /papi/v1/cm/conditional/orderHistory?"));
    assert!(!request_line.contains("strategyId="));
}
