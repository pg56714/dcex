use super::helpers::*;

#[tokio::test]
async fn public_spot_orderbook_uses_public_endpoint() {
    let (base_url, handle) = server();
    let client = KucoinClient::with_base_urls(
        None,
        None,
        None,
        Duration::from_secs(2),
        base_url,
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");

    let response = client
        .public_request(
            "get_spot_orderbook",
            vec![("product_symbol".to_string(), "BTC-USDT-SPOT".to_string())],
        )
        .await
        .expect("response");

    assert_eq!(response.data["code"], "200000");
    let request = handle.join().expect("server");
    assert!(request.starts_with("GET /api/v1/market/orderbook/level2_20?symbol=BTC-USDT HTTP/1.1"));
    let request = request.to_ascii_lowercase();
    assert!(!request.contains("kc-api-key:"));
    assert!(!request.contains("kc-api-sign:"));
    assert!(!request.contains("kc-api-timestamp:"));
    assert!(!request.contains("kc-api-passphrase:"));
}

#[tokio::test]
async fn spot_open_orders_uses_current_paginated_endpoint() {
    let (base_url, handle) = server();
    let client = KucoinClient::with_base_urls(
        Some("key".to_string()),
        Some("secret".to_string()),
        Some("passphrase".to_string()),
        Duration::from_secs(2),
        base_url,
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");

    client
        .private_request(
            "get_spot_open_orders",
            vec![
                ("product_symbol".to_string(), "BTC-USDT-SPOT".to_string()),
                ("pageNum".to_string(), "2".to_string()),
                ("pageSize".to_string(), "50".to_string()),
            ],
        )
        .await
        .expect("response");

    let request = handle.join().expect("server");
    assert!(request.starts_with(
        "GET /api/v1/hf/orders/active/page?pageNum=2&pageSize=50&symbol=BTC-USDT HTTP/1.1"
    ));
}

#[tokio::test]
async fn futures_position_uses_v2_endpoint() {
    let (base_url, handle) = server();
    let client = KucoinClient::with_base_urls(
        Some("key".to_string()),
        Some("secret".to_string()),
        Some("passphrase".to_string()),
        Duration::from_secs(2),
        "http://127.0.0.1:9".to_string(),
        base_url,
    )
    .expect("client");

    client
        .private_request(
            "get_futures_position",
            vec![("product_symbol".to_string(), "BTC-USDT-SWAP".to_string())],
        )
        .await
        .expect("response");

    let request = handle.join().expect("server");
    assert!(request.starts_with("GET /api/v2/position?symbol=XBTUSDTM HTTP/1.1"));
}

#[tokio::test]
async fn futures_kline_uses_minutes_for_granularity() {
    let (base_url, handle) = server();
    let client = KucoinClient::with_base_urls(
        None,
        None,
        None,
        Duration::from_secs(2),
        "http://127.0.0.1:9".to_string(),
        base_url,
    )
    .expect("client");

    client
        .public_request(
            "get_futures_kline",
            vec![
                ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
                ("timeframe".to_string(), "1m".to_string()),
            ],
        )
        .await
        .expect("response");

    let request = handle.join().expect("server");
    assert!(request.starts_with("GET /api/v1/kline/query?symbol=XBTUSDTM&granularity=1 HTTP/1.1"));
}

#[tokio::test]
async fn futures_order_serializes_current_quantity_and_force_hold_fields() {
    let (base_url, handle) = server();
    let client = KucoinClient::with_base_urls(
        Some("key".to_string()),
        Some("secret".to_string()),
        Some("passphrase".to_string()),
        Duration::from_secs(2),
        "http://127.0.0.1:9".to_string(),
        base_url,
    )
    .expect("client");

    client
        .private_request(
            "place_futures_order",
            vec![
                ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
                ("side".to_string(), "buy".to_string()),
                ("type".to_string(), "limit".to_string()),
                ("qty".to_string(), "0.001".to_string()),
                ("price".to_string(), "100000".to_string()),
                ("forceHold".to_string(), "true".to_string()),
            ],
        )
        .await
        .expect("response");

    let request = handle.join().expect("server");
    assert!(request.starts_with("POST /api/v1/orders HTTP/1.1"));
    let body = request.split("\r\n\r\n").nth(1).expect("body");
    let body: serde_json::Value = serde_json::from_str(body).expect("json body");
    assert_eq!(body["symbol"], "XBTUSDTM");
    assert_eq!(body["qty"], "0.001");
    assert_eq!(body["forceHold"], true);
    assert!(body.get("size").is_none());
    assert!(
        body["clientOid"]
            .as_str()
            .is_some_and(|value| value.starts_with("dcex-"))
    );
}

#[tokio::test]
async fn earn_purchase_uses_json_body_and_endpoint() {
    let (base_url, handle) = server();
    let client = KucoinClient::with_base_urls(
        Some("key".to_string()),
        Some("secret".to_string()),
        Some("passphrase".to_string()),
        Duration::from_secs(2),
        base_url,
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");

    client
        .private_request(
            "purchase_earn",
            vec![
                ("productId".to_string(), "2611".to_string()),
                ("amount".to_string(), "1".to_string()),
                ("accountType".to_string(), "TRADE".to_string()),
            ],
        )
        .await
        .expect("response");

    let request = handle.join().expect("server");
    assert!(request.starts_with("POST /api/v1/earn/orders HTTP/1.1"));
    let body = request.split("\r\n\r\n").nth(1).expect("body");
    let body: serde_json::Value = serde_json::from_str(body).expect("json body");
    assert_eq!(body["productId"], "2611");
    assert_eq!(body["amount"], "1");
    assert_eq!(body["accountType"], "TRADE");
}

#[tokio::test]
async fn subaccount_balance_uses_path_and_query() {
    let (base_url, handle) = server();
    let client = KucoinClient::with_base_urls(
        Some("key".to_string()),
        Some("secret".to_string()),
        Some("passphrase".to_string()),
        Duration::from_secs(2),
        base_url,
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");

    client
        .private_request(
            "get_subaccount_balance",
            vec![
                ("subUserId".to_string(), "sub-user".to_string()),
                ("includeBaseAmount".to_string(), "true".to_string()),
                ("baseCurrency".to_string(), "USDT".to_string()),
            ],
        )
        .await
        .expect("response");

    let request = handle.join().expect("server");
    assert!(request.starts_with(
        "GET /api/v1/sub-accounts/sub-user?includeBaseAmount=true&baseCurrency=USDT HTTP/1.1"
    ));
}

#[tokio::test]
async fn uta_v2_positions_and_risk_overview_use_documented_paths() {
    for (method, path) in [
        ("get_uta_positions", "/api/ua/v2/unified/position/open-list"),
        (
            "get_uta_account_overview",
            "/api/ua/v2/unified/account/overview",
        ),
    ] {
        let (base_url, handle) = server();
        let client = KucoinClient::with_base_urls(
            Some("key".into()),
            Some("secret".into()),
            Some("passphrase".into()),
            Duration::from_secs(2),
            base_url,
            "http://127.0.0.1:9".into(),
        )
        .expect("client");
        client
            .private_request(method, Vec::new())
            .await
            .expect("response");
        let request = handle.join().expect("server");
        assert!(request.starts_with(&format!("GET {path} HTTP/1.1")));
    }
}
