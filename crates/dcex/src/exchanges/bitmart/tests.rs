use std::{
    io::{ErrorKind, Read, Write},
    net::TcpListener,
    thread::{self, JoinHandle},
    time::{Duration, Instant},
};

use serde_json::{json, Value};

use crate::http::{HttpMethod, RequestBody};
use crate::DcexError;

use super::*;

fn recording_server() -> (String, JoinHandle<Option<String>>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    listener.set_nonblocking(true).expect("nonblocking");
    let address = listener.local_addr().expect("address");
    let handle = thread::spawn(move || {
        let deadline = Instant::now() + Duration::from_secs(2);
        loop {
            match listener.accept() {
                Ok((mut stream, _)) => {
                    stream.set_nonblocking(false).expect("blocking stream");
                    stream
                        .set_read_timeout(Some(Duration::from_secs(2)))
                        .expect("read timeout");
                    let mut buffer = [0u8; 4096];
                    let size = stream.read(&mut buffer).expect("read");
                    let request = String::from_utf8_lossy(&buffer[..size]).into_owned();
                    stream
                        .write_all(
                            b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\
Content-Length: 13\r\nConnection: close\r\n\r\n{\"code\":1000}",
                        )
                        .expect("write");
                    return request.lines().next().map(str::to_string);
                }
                Err(error) if error.kind() == ErrorKind::WouldBlock => {
                    if Instant::now() >= deadline {
                        return None;
                    }
                    thread::sleep(Duration::from_millis(10));
                }
                Err(error) => panic!("accept failed: {error}"),
            }
        }
    });
    (format!("http://{address}"), handle)
}

#[test]
fn signed_post_uses_exact_body() {
    let client = BitmartClient::new(
        Some("api-key".to_string()),
        Some("test_api_secret_0000".to_string()),
        Some("test_memo".to_string()),
        Duration::from_secs(1),
    )
    .expect("client");
    let body = br#"{"symbol":"BTCUSDT"}"#.to_vec();
    let request = client
        .build_request(
            HttpMethod::Post,
            BitmartMarket::Spot,
            "/spot/v2/submit_order",
            Vec::new(),
            Some(body.clone()),
            true,
            1_700_000_000_000,
        )
        .expect("request");

    assert_eq!(
        request.headers.get("X-BM-SIGN").map(String::as_str),
        Some("a5a38bab707890a577d96959ca82a1b7a4c0db7ffd9b40ba17b20ad57932a542")
    );
    assert_eq!(request.body, RequestBody::Raw(body));
}

#[test]
fn raw_auto_routes_spot_paths_to_spot_base_url() {
    let (spot_base_url, handle) = recording_server();
    let client = BitmartClient::with_base_urls(
        None,
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
            "/spot/quotation/v3/ticker",
            vec![("symbol".to_string(), "BTC_USDT".to_string())],
            None,
            false,
        )
        .expect("response");

    assert_eq!(response.status, 200);
    assert_eq!(
        handle.join().expect("server"),
        Some("GET /spot/quotation/v3/ticker?symbol=BTC_USDT HTTP/1.1".to_string())
    );
}

#[test]
fn raw_auto_routes_contract_paths_to_futures_base_url() {
    let (futures_base_url, handle) = recording_server();
    let client = BitmartClient::with_base_urls(
        None,
        None,
        None,
        Duration::from_secs(2),
        "http://127.0.0.1:9".to_string(),
        futures_base_url,
    )
    .expect("client");

    let response = client
        .request_raw_auto_blocking(
            HttpMethod::Get,
            "/contract/public/details",
            vec![("symbol".to_string(), "BTCUSDT".to_string())],
            None,
            false,
        )
        .expect("response");

    assert_eq!(response.status, 200);
    assert_eq!(
        handle.join().expect("server"),
        Some("GET /contract/public/details?symbol=BTCUSDT HTTP/1.1".to_string())
    );
}

#[test]
fn raw_auto_routes_transfer_contract_paths_to_futures_base_url() {
    let (futures_base_url, handle) = recording_server();
    let client = BitmartClient::with_base_urls(
        None,
        None,
        None,
        Duration::from_secs(2),
        "http://127.0.0.1:9".to_string(),
        futures_base_url,
    )
    .expect("client");

    let response = client
        .request_raw_auto_blocking(
            HttpMethod::Get,
            "/account/v1/transfer-contract",
            Vec::new(),
            None,
            false,
        )
        .expect("response");

    assert_eq!(response.status, 200);
    assert_eq!(
        handle.join().expect("server"),
        Some("GET /account/v1/transfer-contract HTTP/1.1".to_string())
    );
}

#[test]
fn raw_auto_rejects_unsupported_path_prefixes() {
    assert_eq!(
        BitmartMarket::from_path("/unknown"),
        Err(DcexError::InvalidInput(
            "unsupported BitMart API path: /unknown".to_string()
        ))
    );
}

#[test]
fn contract_modify_limit_order_keeps_numeric_payload_types() {
    let client = BitmartClient::new(
        Some("api-key".to_string()),
        Some("test_api_secret_0000".to_string()),
        Some("test_memo".to_string()),
        Duration::from_secs(1),
    )
    .expect("client");
    let params = params::BitmartParams::from_pairs(vec![
        ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
        ("order_id".to_string(), "123456".to_string()),
        ("price".to_string(), "100.1".to_string()),
        ("size".to_string(), "1".to_string()),
    ]);
    let mut body = serde_json::Map::new();
    client
        .insert_required_symbol(&mut body, &params, false)
        .expect("symbol");
    params::insert_optional_integer(&mut body, "order_id", params.get("order_id"));
    params::insert_optional_string(&mut body, "price", params.get("price"));
    params::insert_optional_integer(&mut body, "size", params.get("size"));

    assert_eq!(
        Value::Object(body),
        json!({
            "symbol": "BTCUSDT",
            "order_id": 123456,
            "price": "100.1",
            "size": 1
        })
    );
}

#[test]
fn spot_limit_buy_shortcut_does_not_require_side_param() {
    let client = BitmartClient::public(Duration::from_secs(1)).expect("client");
    let params = params::BitmartParams::from_pairs(vec![
        ("product_symbol".to_string(), "BTC-USDT-SPOT".to_string()),
        ("size".to_string(), "1".to_string()),
        ("price".to_string(), "100".to_string()),
    ]);
    let body = client
        .spot_order_body_from_params(&params, Some("buy"), Some("limit"))
        .expect("body");

    assert_eq!(
        Value::Object(body),
        json!({
            "symbol": "BTC_USDT",
            "side": "buy",
            "type": "limit",
            "size": "1",
            "price": "100"
        })
    );
}

#[test]
fn contract_cancel_order_keeps_order_id_as_string() {
    let client = BitmartClient::public(Duration::from_secs(1)).expect("client");
    let params = params::BitmartParams::from_pairs(vec![
        ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
        ("order_id".to_string(), "3000378272670421".to_string()),
    ]);
    let body = client
        .contract_cancel_order_body_from_params(&params)
        .expect("body");

    assert_eq!(
        Value::Object(body),
        json!({
            "symbol": "BTCUSDT",
            "order_id": "3000378272670421"
        })
    );
}
