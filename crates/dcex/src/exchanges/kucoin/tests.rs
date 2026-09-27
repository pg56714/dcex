use std::time::Duration;
use std::{
    io::{Read, Write},
    net::TcpListener,
    thread,
};

use crate::http::HttpMethod;

use super::signing::request_signature;
use super::*;

#[test]
fn signature_and_passphrase_match_python_vectors() {
    let client = KucoinClient::new(
        Some("test_api_key_0000".to_string()),
        Some("test_api_secret_0000".to_string()),
        Some("passphrase".to_string()),
        Duration::from_secs(1),
    )
    .expect("client");
    let request = client
        .build_request(
            HttpMethod::Get,
            KucoinMarket::Spot,
            "/api/v1/accounts",
            vec![
                ("currency".to_string(), "BTC-USDT".to_string()),
                ("type".to_string(), "trade".to_string()),
            ],
            None,
            true,
            "1700000000000",
        )
        .expect("request");

    assert_eq!(
        request.headers.get("KC-API-SIGN").map(String::as_str),
        Some("U7HJOAA1P91EHj3Qgp0soO+BbskRIYBAUVt+Lrmrbvk=")
    );
    assert_eq!(
        request.headers.get("KC-API-PASSPHRASE").map(String::as_str),
        Some("BiepdEOmmFVpiE0m2qjSxvqjTlOfQ1XzmhElRgdHLwI=")
    );
}

#[test]
fn query_is_encoded_for_transport_but_not_for_signing() {
    let client = KucoinClient::new(
        Some("key".to_string()),
        Some("secret".to_string()),
        Some("passphrase".to_string()),
        Duration::from_secs(1),
    )
    .expect("client");
    let timestamp = "1700000000000";
    let raw_value = "BTC/USDT+cash value";
    let request = client
        .build_request(
            HttpMethod::Get,
            KucoinMarket::Spot,
            "/api/v1/accounts",
            vec![("currency".to_string(), raw_value.to_string())],
            None,
            true,
            timestamp,
        )
        .expect("request");

    assert_eq!(
        request.path,
        "/api/v1/accounts?currency=BTC%2FUSDT%2Bcash+value"
    );
    let expected = request_signature(
        "secret",
        timestamp,
        HttpMethod::Get,
        "/api/v1/accounts?currency=BTC/USDT+cash value",
        &[],
    )
    .expect("signature");
    assert_eq!(request.headers.get("KC-API-SIGN"), Some(&expected));
}

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
async fn spot_batch_order_never_leaks_internal_product_symbol() {
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
        Duration::from_secs(1),
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
            .err()
            .expect("validation error");
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
        .err()
        .expect("validation error");
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
        Duration::from_secs(2),
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
        Duration::from_secs(2),
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
async fn dcp_uses_spot_dead_cancel_all_routes_and_symbols_string() {
    let (base_url, server_handle) = server();
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
        Duration::from_secs(2),
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
            Duration::from_secs(2),
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
        Duration::from_secs(2),
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

fn server() -> (String, thread::JoinHandle<String>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let address = listener.local_addr().expect("address");
    let handle = thread::spawn(move || {
        let (mut stream, _) = listener.accept().expect("accept");
        let mut buffer = [0u8; 4096];
        let size = stream.read(&mut buffer).expect("read");
        let mut request = String::from_utf8_lossy(&buffer[..size]).into_owned();
        let content_length = request
            .lines()
            .find_map(|line| {
                line.to_ascii_lowercase()
                    .strip_prefix("content-length: ")
                    .and_then(|value| value.trim().parse::<usize>().ok())
            })
            .unwrap_or(0);
        while request.split("\r\n\r\n").nth(1).map_or(0, str::len) < content_length {
            let size = stream.read(&mut buffer).expect("read body");
            assert!(size > 0, "request ended before the declared body length");
            request.push_str(&String::from_utf8_lossy(&buffer[..size]));
        }
        stream
            .write_all(
                b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\
Content-Length: 46\r\nConnection: close\r\n\r\n{\"code\":\"200000\",\"data\":{\"bids\":[],\"asks\":[]}}",
            )
            .expect("write");
        request
    });
    (format!("http://{address}"), handle)
}

#[tokio::test]
async fn uta_v2_order_uses_signed_unified_route_and_normalized_symbol() {
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

#[tokio::test]
async fn uta_v2_order_identifier_is_required_before_network() {
    let client = KucoinClient::public(Duration::from_secs(1)).expect("client");
    let error = client
        .cancel_uta_order("SPOT", "BTC-USDT")
        .await
        .expect_err("order id is required");
    assert!(error.to_string().contains("orderId"));
}

mod endpoint_coverage;

#[test]
fn delete_batch_cancel_preserves_body_and_signs_exact_bytes() {
    let client = KucoinClient::new(
        Some("key".into()),
        Some("secret".into()),
        Some("passphrase".into()),
        Duration::from_secs(1),
    )
    .expect("client");
    let body = br#"{"orderIdsList":["123","456"]}"#.to_vec();
    let request = client
        .build_request(
            HttpMethod::Delete,
            KucoinMarket::Futures,
            "/api/v1/orders/multi-cancel",
            Vec::new(),
            Some(body.clone()),
            true,
            "1700000000000",
        )
        .expect("request");
    assert_eq!(request.path, "/api/v1/orders/multi-cancel");
    match request.body {
        crate::http::RequestBody::Raw(actual) => assert_eq!(actual, body),
        _ => panic!("DELETE must carry the caller's JSON bytes"),
    }
    // Independently generated with Python hashlib/hmac, including the JSON body.
    assert_eq!(
        request.headers.get("KC-API-SIGN").map(String::as_str),
        Some("nkl3PqCb1JDeDputCiNgxNFASteKlyViBGKdX62mv9k=")
    );
}
