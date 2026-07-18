use std::io::{Read, Write};
use std::net::TcpListener;
use std::thread;
use std::time::Duration;

use crate::http::{HttpMethod, RequestBody};
use crate::product_table::{MarketInfo, ProductTable};

use super::*;

fn client() -> MexcClient {
    MexcClient::new(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(1),
    )
    .expect("client")
}

#[test]
fn spot_signature_matches_python_protocol() {
    let request = client()
        .build_request(
            HttpMethod::Get,
            MexcApi::Spot,
            "/api/v3/order",
            vec![("symbol".to_string(), "BTCUSDT".to_string())],
            None,
            true,
            1_700_000_000_000,
        )
        .expect("request");

    assert_eq!(
        request.query,
        vec![
            ("symbol".to_string(), "BTCUSDT".to_string()),
            ("timestamp".to_string(), "1700000000000".to_string()),
            (
                "signature".to_string(),
                "6244d11c958f45ac56733152cb3cb1831d23a2b3709b3a88b8b42a072aceb410".to_string(),
            ),
        ]
    );
}

#[test]
fn contract_signature_uses_exact_json_body() {
    let request = client()
        .build_request(
            HttpMethod::Post,
            MexcApi::Contract,
            "/api/v1/private/order/cancel",
            Vec::new(),
            Some(br#"[{"orderId":"1"},{"orderId":"2"}]"#.to_vec()),
            true,
            1_700_000_000_000,
        )
        .expect("request");

    assert_eq!(
        request.headers.get("Signature").map(String::as_str),
        Some("5767f5e6ba9a1f7bf0e35db1de5ecf52d00218b3f2bc2939b4d5ed5758bb0944")
    );
    assert_eq!(
        request.body,
        RequestBody::Raw(br#"[{"orderId":"1"},{"orderId":"2"}]"#.to_vec())
    );
}

#[test]
fn exchange_symbol_uses_product_table_when_available() {
    let table = ProductTable::new(vec![MarketInfo {
        exchange: "mexc".to_string(),
        exchange_symbol: "BTC_USDT".to_string(),
        product_symbol: "BTC-USDT-SWAP".to_string(),
        product_type: "swap".to_string(),
        exchange_type: "linear".to_string(),
        price_precision: "0.1".to_string(),
        size_precision: "1".to_string(),
        min_size: "1".to_string(),
        base_currency: "BTC".to_string(),
        quote_currency: "USDT".to_string(),
        min_notional: "0".to_string(),
        size_per_contract: "1".to_string(),
    }]);
    let client = client().with_product_table(table);

    assert_eq!(
        client.exchange_symbol("BTC-USDT-SWAP", "").expect("symbol"),
        "BTC_USDT"
    );
}

#[tokio::test]
async fn signed_spot_request_uses_synchronized_server_time() {
    const SERVER_TIME: u64 = 1_700_000_000_000;
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let address = listener.local_addr().expect("address");
    let handle = thread::spawn(move || {
        let mut requests = Vec::new();
        for body in [
            format!(r#"{{"serverTime":{SERVER_TIME}}}"#),
            "{}".to_string(),
        ] {
            let (mut stream, _) = listener.accept().expect("accept");
            let mut buffer = [0u8; 4096];
            let size = stream.read(&mut buffer).expect("read");
            requests.push(String::from_utf8_lossy(&buffer[..size]).into_owned());
            let response = format!(
                "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{body}",
                body.len()
            );
            stream.write_all(response.as_bytes()).expect("write");
        }
        requests
    });
    let base_url = format!("http://{address}");
    let client = MexcClient::with_base_urls(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(2),
        base_url.clone(),
        base_url,
    )
    .expect("client");

    client
        .request_raw(
            HttpMethod::Get,
            MexcApi::Spot,
            "/api/v3/openOrders",
            Vec::new(),
            None,
            true,
        )
        .await
        .expect("request");

    let requests = handle.join().expect("server");
    assert!(requests[0].starts_with("GET /api/v3/time HTTP/1.1"));
    let timestamp = requests[1]
        .split_whitespace()
        .nth(1)
        .and_then(|path| path.split("timestamp=").nth(1))
        .and_then(|query| query.split('&').next())
        .and_then(|value| value.parse::<u64>().ok())
        .expect("timestamp");
    assert!(timestamp >= SERVER_TIME);
    assert!(timestamp - SERVER_TIME < 1_000);
}
