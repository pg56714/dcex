use super::helpers::*;

#[test]
fn futures_symbol_fallback_matches_kucoin_contract_format() {
    let client = KucoinClient::public(Duration::from_secs(1)).expect("client");

    assert_eq!(
        client
            .exchange_symbol("BTC-USDT-SWAP", true)
            .expect("symbol"),
        "XBTUSDTM"
    );
    assert_eq!(
        client
            .exchange_symbol("ETH-USDT-SWAP", true)
            .expect("symbol"),
        "ETHUSDTM"
    );
}

#[tokio::test]
async fn spot_batch_order_never_leaks_internal_product_symbol() {
    let (base_url, handle) = server();
    let client = KucoinClient::with_base_urls(
        Some("key".to_string()),
        Some("secret".to_string()),
        Some("passphrase".to_string()),
        Duration::from_secs(10),
        base_url,
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");
    let orders = serde_json::json!([{
        "symbol": "BTC-USDT",
        "product_symbol": "SHOULD-NOT-BE-SENT-SPOT",
        "side": "buy",
        "type": "limit",
        "size": "1",
        "price": "100000"
    }]);

    client
        .private_request(
            "place_spot_batch_orders",
            vec![("orders".to_string(), orders.to_string())],
        )
        .await
        .expect("response");

    let request = handle.join().expect("server");
    let body = request.split("\r\n\r\n").nth(1).expect("body");
    let body: serde_json::Value = serde_json::from_str(body).expect("json body");
    assert_eq!(body["orderList"][0]["symbol"], "BTC-USDT");
    assert!(body["orderList"][0].get("product_symbol").is_none());
}

#[tokio::test]
async fn current_required_and_conditional_fields_are_rejected_before_transport() {
    let client = KucoinClient::with_base_urls(
        Some("key".to_string()),
        Some("secret".to_string()),
        Some("passphrase".to_string()),
        Duration::from_secs(10),
        "http://127.0.0.1:9".to_string(),
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");

    for (method, params, expected) in [
        (
            "get_spot_open_orders",
            vec![],
            "missing required parameter: product_symbol or symbol",
        ),
        (
            "cancel_futures_order_by_client_oid",
            vec![("clientOid".to_string(), "client-1".to_string())],
            "missing required parameter: product_symbol or symbol",
        ),
        (
            "get_futures_open_order_value",
            vec![],
            "missing required parameter: product_symbol or symbol",
        ),
        (
            "place_futures_market_order",
            vec![
                ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
                ("side".to_string(), "buy".to_string()),
                ("size".to_string(), "1".to_string()),
                ("qty".to_string(), "0.001".to_string()),
            ],
            "requires exactly one of size, qty, valueQty",
        ),
        (
            "place_spot_batch_orders",
            vec![("orders".to_string(), "[]".to_string())],
            "between 1 and 20 orders",
        ),
        (
            "flex_transfer",
            vec![
                ("transfer_type".to_string(), "PARENT_TO_SUB".to_string()),
                ("currency".to_string(), "USDT".to_string()),
                ("amount".to_string(), "1".to_string()),
                ("fromAccountType".to_string(), "MARGIN_V2".to_string()),
                ("toAccountType".to_string(), "TRADE".to_string()),
                ("toUserId".to_string(), "sub-user".to_string()),
            ],
            "cannot use a V2 margin account type",
        ),
        (
            "get_structured_earn_orders",
            vec![],
            "missing required parameter: categories",
        ),
    ] {
        let error = client
            .private_request(method, params)
            .await
            .expect_err("validation error");
        assert!(error.to_string().contains(expected), "{error}");
    }

    let error = client
        .public_request(
            "get_futures_open_interest",
            vec![
                (
                    "product_symbol".to_string(),
                    "BTC-USDT-SWAP,ETH-USDT-SWAP".to_string(),
                ),
                ("interval".to_string(), "5min".to_string()),
            ],
        )
        .await
        .expect_err("validation error");
    assert!(
        error
            .to_string()
            .contains("historical open interest requires exactly one symbol")
    );
}

#[tokio::test]
async fn margin_borrow_uses_v3_endpoint_and_normalizes_symbol() {
    let (base_url, handle) = server();
    let client = KucoinClient::with_base_urls(
        Some("key".to_string()),
        Some("secret".to_string()),
        Some("passphrase".to_string()),
        Duration::from_secs(10),
        base_url,
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");

    client
        .private_request(
            "borrow_margin",
            vec![
                ("currency".to_string(), "USDT".to_string()),
                ("size".to_string(), "1".to_string()),
                ("isIsolated".to_string(), "true".to_string()),
                ("product_symbol".to_string(), "BTC-USDT-SPOT".to_string()),
            ],
        )
        .await
        .expect("response");

    let request = handle.join().expect("server");
    assert!(request.starts_with("POST /api/v3/margin/borrow HTTP/1.1"));
    let body = request.split("\r\n\r\n").nth(1).expect("body");
    let body: serde_json::Value = serde_json::from_str(body).expect("json body");
    assert_eq!(body["currency"], "USDT");
    assert_eq!(body["size"], "1");
    assert_eq!(body["isIsolated"], true);
    assert_eq!(body["symbol"], "BTC-USDT");
}

#[tokio::test]
async fn margin_history_normalizes_canonical_product_symbol() {
    let (base_url, handle) = server();
    let client = KucoinClient::with_base_urls(
        Some("key".to_string()),
        Some("secret".to_string()),
        Some("passphrase".to_string()),
        Duration::from_secs(10),
        base_url,
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");

    client
        .private_request(
            "get_margin_borrow_history",
            vec![
                ("product_symbol".to_string(), "BTC-USDT-SPOT".to_string()),
                ("pageSize".to_string(), "20".to_string()),
            ],
        )
        .await
        .expect("response");

    let request = handle.join().expect("server");
    assert!(request.starts_with("GET /api/v3/margin/borrow?symbol=BTC-USDT&pageSize=20 HTTP/1.1"));
}

#[tokio::test]
async fn dcp_uses_spot_dead_cancel_all_routes_and_symbols_string() {
    let (base_url, server_handle) = server();
    let client = KucoinClient::with_base_urls(
        Some("key".into()),
        Some("secret".into()),
        Some("passphrase".into()),
        Duration::from_secs(10),
        base_url,
        "http://127.0.0.1:9".into(),
    )
    .expect("client");
    client
        .private_request(
            "set_dcp",
            vec![
                ("timeout".into(), "10".into()),
                ("symbols".into(), r#"["BTC-USDT","ETH-USDT"]"#.into()),
            ],
        )
        .await
        .expect("set DCP");
    let request = server_handle.join().expect("server");
    assert!(request.starts_with("POST /api/v1/hf/orders/dead-cancel-all HTTP/1.1"));
    let body: serde_json::Value =
        serde_json::from_str(request.split("\r\n\r\n").nth(1).expect("body")).expect("JSON");
    assert_eq!(
        body,
        serde_json::json!({"timeout": 10, "symbols": "BTC-USDT,ETH-USDT"})
    );

    let (base_url, server_handle) = server();
    let client = KucoinClient::with_base_urls(
        Some("key".into()),
        Some("secret".into()),
        Some("passphrase".into()),
        Duration::from_secs(10),
        base_url,
        "http://127.0.0.1:9".into(),
    )
    .expect("client");
    client
        .private_request("get_dcp", Vec::new())
        .await
        .expect("get DCP");
    let request = server_handle.join().expect("server");
    assert!(request.starts_with("GET /api/v1/hf/orders/dead-cancel-all/query HTTP/1.1"));
}

#[tokio::test]
async fn test_orders_reuse_live_order_validation_and_use_test_routes() {
    for (method, route, symbol) in [
        ("test_spot_order", "/api/v1/hf/orders/test", "BTC-USDT-SPOT"),
        ("test_futures_order", "/api/v1/orders/test", "XBT-USDT-SWAP"),
    ] {
        let (base_url, server_handle) = server();
        let client = KucoinClient::with_base_urls(
            Some("key".into()),
            Some("secret".into()),
            Some("passphrase".into()),
            Duration::from_secs(10),
            base_url.clone(),
            base_url,
        )
        .expect("client");
        client
            .private_request(
                method,
                vec![
                    ("product_symbol".into(), symbol.into()),
                    ("side".into(), "buy".into()),
                    ("type".into(), "limit".into()),
                    ("size".into(), "1".into()),
                    ("price".into(), "100".into()),
                ],
            )
            .await
            .expect("test order");
        let request = server_handle.join().expect("server");
        assert!(
            request.starts_with(&format!("POST {route} HTTP/1.1")),
            "{request}"
        );
        let body: serde_json::Value =
            serde_json::from_str(request.split("\r\n\r\n").nth(1).expect("body")).expect("JSON");
        assert_eq!(body["side"], "buy");
        assert_eq!(body["price"], "100");
    }
}

#[tokio::test]
async fn alter_spot_order_uses_validated_json_body() {
    let (base_url, server_handle) = server();
    let client = KucoinClient::with_base_urls(
        Some("key".into()),
        Some("secret".into()),
        Some("passphrase".into()),
        Duration::from_secs(10),
        base_url,
        "http://127.0.0.1:9".into(),
    )
    .expect("client");
    client
        .private_request(
            "alter_spot_order",
            vec![
                ("product_symbol".into(), "BTC-USDT-SPOT".into()),
                ("orderId".into(), "123".into()),
                ("newPrice".into(), "30000".into()),
            ],
        )
        .await
        .expect("alter order");
    let request = server_handle.join().expect("server");
    assert!(request.starts_with("POST /api/v1/hf/orders/alter HTTP/1.1"));
    let body: serde_json::Value =
        serde_json::from_str(request.split("\r\n\r\n").nth(1).expect("body")).expect("JSON");
    assert_eq!(body["symbol"], "BTC-USDT");
    assert_eq!(body["orderId"], "123");
    assert_eq!(body["newPrice"], "30000");
}

#[tokio::test]
async fn uta_v2_order_uses_signed_unified_route_and_normalized_symbol() {
    let (base_url, handle) = server();
    let client = KucoinClient::with_base_urls(
        Some("key".into()),
        Some("secret".into()),
        Some("passphrase".into()),
        Duration::from_secs(10),
        base_url,
        "http://127.0.0.1:9".into(),
    )
    .expect("client");

    client
        .place_uta_order("FUTURES", "BTC-USDT-SWAP", "BUY", "LIMIT", "1", "UNIT")
        .price("30000")
        .await
        .expect("response");

    let request = handle.join().expect("server");
    assert!(request.starts_with("POST /api/ua/v2/unified/order/place HTTP/1.1"));
    assert!(request.to_ascii_lowercase().contains("kc-api-sign:"));
    let body: serde_json::Value =
        serde_json::from_str(request.split("\r\n\r\n").nth(1).expect("body")).expect("JSON");
    assert_eq!(body["tradeType"], "FUTURES");
    assert_eq!(body["symbol"], "XBTUSDTM");
    assert_eq!(body["price"], "30000");
    assert_eq!(body["size"], "1");
    assert_eq!(body["sizeUnit"], "UNIT");
    assert!(body["clientOid"].as_str().is_some());
}

#[tokio::test]
async fn uta_v2_order_identifier_is_required_before_network() {
    let client = KucoinClient::public(Duration::from_secs(1)).expect("client");
    let error = client
        .cancel_uta_order("SPOT", "BTC-USDT")
        .await
        .expect_err("order id is required");
    assert!(error.to_string().contains("orderId"));
}
