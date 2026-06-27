use std::{
    io::{ErrorKind, Read, Write},
    net::TcpListener,
    thread::{self, JoinHandle},
    time::{Duration, Instant},
};

use serde_json::{json, Value};

use crate::http::HttpMethod;
use crate::product_table::{MarketInfo, ProductTable};

use super::{sign_message, AsterClient, AsterMarket};
use crate::exchanges::aster::params::AsterParams;
use crate::DcexError;

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
Content-Length: 11\r\nConnection: close\r\n\r\n{\"ok\":true}",
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
fn eip712_signature_matches_python_vector() {
    let message = "symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001\
&nonce=1700000000000000&signer=0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a";
    assert_eq!(
        sign_message(message, &[0x11; 32]).expect("signature"),
        "0x3ca64e9c82501b8f15cd31348beaaf1aa6636cbba5fb2bc8d1bccf8ee2ffd310\
1a3724dfa8fd2f36de42d3a641b95599d0d4dee5ffb9010eb33b44784d3f60191c"
    );
}

#[test]
fn signed_futures_request_includes_user_before_signer() {
    let client = AsterClient::new(
        Some("0x0000000000000000000000000000000000000001".to_string()),
        Some("0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a".to_string()),
        Some(format!("0x{}", "11".repeat(32))),
        Duration::from_secs(1),
    )
    .expect("client");
    let request = client
        .build_request(
            HttpMethod::Get,
            AsterMarket::Futures,
            "/fapi/v3/balance",
            Vec::new(),
            true,
            Some(1_700_000_000_000_000),
        )
        .expect("request");

    assert_eq!(
        request.headers.get("Accept").map(String::as_str),
        Some("application/json")
    );
    assert!(request.path.contains("nonce=1700000000000000"));
    assert!(request
        .path
        .contains("user=0x0000000000000000000000000000000000000001"));
    assert!(request
        .path
        .contains("signer=0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a"));
    assert!(request.path.contains("signature=0x"));
}

#[test]
fn raw_auto_routes_spot_paths_to_spot_base_url() {
    let (spot_base_url, handle) = recording_server();
    let client = AsterClient::with_base_urls(
        None,
        None,
        None,
        Duration::from_secs(2),
        spot_base_url,
        "http://127.0.0.1:9".to_string(),
    )
    .expect("client");

    let response = client
        .request_raw_auto_blocking(HttpMethod::Get, "/api/v3/time", Vec::new(), false)
        .expect("response");

    assert_eq!(response.status, 200);
    assert_eq!(
        handle.join().expect("server"),
        Some("GET /api/v3/time HTTP/1.1".to_string())
    );
}

#[test]
fn raw_auto_routes_futures_paths_to_futures_base_url() {
    let (futures_base_url, handle) = recording_server();
    let client = AsterClient::with_base_urls(
        None,
        None,
        None,
        Duration::from_secs(2),
        "http://127.0.0.1:9".to_string(),
        futures_base_url,
    )
    .expect("client");

    let response = client
        .request_raw_auto_blocking(HttpMethod::Get, "/fapi/v3/time", Vec::new(), false)
        .expect("response");

    assert_eq!(response.status, 200);
    assert_eq!(
        handle.join().expect("server"),
        Some("GET /fapi/v3/time HTTP/1.1".to_string())
    );
}

#[test]
fn raw_auto_rejects_unsupported_path_prefixes() {
    assert_eq!(
        AsterMarket::from_path("/unknown"),
        Err(DcexError::InvalidInput(
            "unsupported Aster API path: /unknown".to_string()
        ))
    );
}

#[test]
fn product_table_resolves_canonical_symbol() {
    let table = ProductTable::new(vec![MarketInfo {
        exchange: "aster".to_string(),
        exchange_symbol: "ASTERUSDT".to_string(),
        product_symbol: "ASTER-USDT-SWAP".to_string(),
        product_type: "swap".to_string(),
        exchange_type: "PERP".to_string(),
        price_precision: "0.0001".to_string(),
        size_precision: "0.1".to_string(),
        min_size: "0.1".to_string(),
        base_currency: "ASTER".to_string(),
        quote_currency: "USDT".to_string(),
        min_notional: "5".to_string(),
        size_per_contract: "1".to_string(),
    }]);
    let client = AsterClient::public(Duration::from_secs(1))
        .expect("client")
        .with_product_table(table);

    assert_eq!(
        client.exchange_symbol("ASTER-USDT-SWAP").expect("symbol"),
        "ASTERUSDT"
    );
}

#[test]
fn batch_orders_resolve_product_symbol_and_side() {
    let client = AsterClient::public(Duration::from_secs(1)).expect("client");
    let params = AsterParams::from_pairs(vec![(
        "batchOrders".to_string(),
        json!([
            {
                "product_symbol": "ASTER-USDT-SWAP",
                "side": "buy",
                "type": "LIMIT",
                "quantity": "1",
                "price": "1"
            }
        ])
        .to_string(),
    )]);
    let body = client
        .resolve_order_array(&params, "batchOrders")
        .expect("batch orders");
    let Value::Array(items) = serde_json::from_str(&body).expect("json") else {
        panic!("expected array");
    };
    assert_eq!(
        items[0].get("symbol"),
        Some(&Value::String("ASTERUSDT".to_string()))
    );
    assert_eq!(
        items[0].get("side"),
        Some(&Value::String("BUY".to_string()))
    );
    assert!(items[0].get("product_symbol").is_none());
}
