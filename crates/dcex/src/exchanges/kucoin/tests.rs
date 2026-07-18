use std::time::Duration;
use std::{
    io::{Read, Write},
    net::TcpListener,
    thread,
};

use crate::http::HttpMethod;

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
