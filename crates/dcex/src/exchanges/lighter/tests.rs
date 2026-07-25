use std::collections::BTreeMap;
use std::io::{ErrorKind, Read, Write};
use std::net::TcpListener;
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

use crate::http::{block_on, HttpMethod, RequestBody};
use crate::product_table::{MarketInfo, ProductTable};

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
fn request_matches_python_encoding() {
    let client = LighterClient::new(Duration::from_secs(1)).expect("client");
    let request = client
        .build_request(
            HttpMethod::Post,
            "/api/v1/sendTx",
            vec![("account_index".to_string(), "1".to_string())],
            vec![
                ("tx_type".to_string(), "14".to_string()),
                ("tx_info".to_string(), r#"{"Price":100}"#.to_string()),
            ],
            false,
            BTreeMap::new(),
            LighterContentType::Form,
        )
        .expect("request");

    assert_eq!(request.path, "/api/v1/sendTx?account_index=1");
    assert_eq!(
        request.body,
        RequestBody::Raw(b"tx_type=14&tx_info=%7B%22Price%22%3A100%7D".to_vec())
    );
}

#[test]
fn product_table_resolves_canonical_symbol_to_market_id() {
    let table = ProductTable::new(vec![MarketInfo {
        exchange: "lighter".to_string(),
        exchange_symbol: "42".to_string(),
        product_symbol: "BTC-USDC-SWAP".to_string(),
        product_type: "swap".to_string(),
        exchange_type: "swap".to_string(),
        price_precision: "0.01".to_string(),
        size_precision: "0.001".to_string(),
        min_size: "0.001".to_string(),
        base_currency: "BTC".to_string(),
        quote_currency: "USDC".to_string(),
        min_notional: "1".to_string(),
        size_per_contract: "1".to_string(),
    }]);
    let client = LighterClient::new(Duration::from_secs(1))
        .expect("client")
        .with_product_table(table);

    assert_eq!(client.market_id("BTC-USDC-SWAP").expect("market id"), "42");
}

#[test]
fn export_sends_resolved_market_id_without_account_index() {
    let (base_url, handle) = recording_server();
    let table = ProductTable::new(vec![MarketInfo {
        exchange: "lighter".to_string(),
        exchange_symbol: "42".to_string(),
        product_symbol: "BTC-USDC-SWAP".to_string(),
        product_type: "swap".to_string(),
        exchange_type: "swap".to_string(),
        price_precision: "0.01".to_string(),
        size_precision: "0.001".to_string(),
        min_size: "0.001".to_string(),
        base_currency: "BTC".to_string(),
        quote_currency: "USDC".to_string(),
        min_notional: "1".to_string(),
        size_per_contract: "1".to_string(),
    }]);
    let client = LighterClient::with_base_url(Duration::from_secs(1), base_url)
        .expect("client")
        .with_product_table(table);

    block_on(async move {
        client
            .private_request(
                "get_export",
                vec![
                    ("product_symbol".to_string(), "BTC-USDC-SWAP".to_string()),
                    ("type_".to_string(), "trade".to_string()),
                    ("authorization".to_string(), "token".to_string()),
                ],
            )
            .await
    })
    .expect("export request");

    let request_line = handle.join().expect("server").expect("request line");
    assert!(request_line.starts_with("GET /api/v1/export?"));
    assert!(request_line.contains("market_id=42"));
    assert!(request_line.contains("type=trade"));
    assert!(!request_line.contains("account_index="));
    assert!(!request_line.contains("product_symbol="));
}

#[test]
fn auth_token_uses_configured_private_key() {
    let client = LighterClient::with_base_url_and_credentials(
        Duration::from_secs(1),
        "https://mainnet.zklighter.elliot.ai".to_string(),
        Some(12),
        Some(3),
        Some("01".to_string() + &"00".repeat(39)),
    )
    .expect("client");

    let token = client
        .create_auth_token_with_deadline_and_api_key_index(600, 3)
        .expect("auth token");
    let parts = token.split(':').collect::<Vec<_>>();

    assert_eq!(parts.len(), 4);
    assert_eq!(parts[1], "12");
    assert_eq!(parts[2], "3");
    assert_eq!(bytes::decode_hex_len(parts[3]), Some(80));
}

mod bytes {
    pub(super) fn decode_hex_len(value: &str) -> Option<usize> {
        hex::decode(value).ok().map(|bytes| bytes.len())
    }
}
