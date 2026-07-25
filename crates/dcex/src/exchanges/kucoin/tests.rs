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
    assert!(body["clientOid"]
        .as_str()
        .is_some_and(|value| value.starts_with("dcex-")));
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
    assert!(error
        .to_string()
        .contains("historical open interest requires exactly one symbol"));
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
Content-Length: 46\r\nConnection: close\r\n\r\n{\"code\":\"200000\",\"data\":{\"bids\":[],\"asks\":[]}}",
            )
            .expect("write");
        request
    });
    (format!("http://{address}"), handle)
}
