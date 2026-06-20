use std::sync::{Arc, Mutex};
use std::time::Duration;
use std::{
    io::{ErrorKind, Read, Write},
    net::TcpListener,
    thread::{self, JoinHandle},
    time::Instant,
};

use super::client::{BinanceClient, BinanceMarket};
use super::endpoints::SPOT_BASE_URL;
use super::params::{market_for_product_symbol_fallback, normalize_order_side};
use super::signing::BinanceSigner;
use crate::exchange::RequestSigner;
use crate::http::{block_on, HttpMethod, HttpRequest};
use crate::product_table::ProductTable;
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
fn signer_matches_python_implementation() {
    let signer = BinanceSigner {
        api_key: "api-key".to_string(),
        api_secret: "secret".to_string(),
        timestamp_offset_ms: Arc::new(Mutex::new(None)),
    };
    let mut request = HttpRequest::new(HttpMethod::Get, SPOT_BASE_URL, "/api/v3/order");
    request.query = vec![
        ("symbol".to_string(), "BTCUSDT".to_string()),
        ("side".to_string(), "BUY".to_string()),
    ];

    signer
        .sign(&mut request, 1_700_000_000_000)
        .expect("signature");

    assert_eq!(
        request.query,
        vec![
            ("symbol".to_string(), "BTCUSDT".to_string()),
            ("side".to_string(), "BUY".to_string()),
            ("timestamp".to_string(), "1700000000000".to_string()),
            ("recvWindow".to_string(), "5000".to_string()),
            (
                "signature".to_string(),
                "5858226bd5a361c8dd587d4da2c1d479758c21380d4913cea33235d3f32dd987".to_string(),
            ),
        ]
    );
    assert_eq!(
        request.headers.get("X-MBX-APIKEY").map(String::as_str),
        Some("api-key")
    );
}

#[test]
fn signer_applies_timestamp_offset() {
    let signer = BinanceSigner {
        api_key: "api-key".to_string(),
        api_secret: "secret".to_string(),
        timestamp_offset_ms: Arc::new(Mutex::new(Some(-1_500))),
    };
    let mut request = HttpRequest::new(HttpMethod::Get, SPOT_BASE_URL, "/api/v3/order");

    signer
        .sign(&mut request, 1_700_000_000_000)
        .expect("signature");

    assert_eq!(
        request
            .query
            .iter()
            .find(|(key, _)| key == "timestamp")
            .map(|(_, value)| value.as_str()),
        Some("1699999998500")
    );
}

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
}

#[test]
fn raw_auto_routes_spot_paths_to_spot_base_url() {
    let (spot_base_url, handle) = recording_server();
    let client = BinanceClient::with_base_urls(
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
            "/api/v3/exchangeInfo",
            vec![("symbol".to_string(), "BTCUSDT".to_string())],
            false,
        )
        .expect("response");

    assert_eq!(response.status, 200);
    assert_eq!(
        handle.join().expect("server"),
        Some("GET /api/v3/exchangeInfo?symbol=BTCUSDT HTTP/1.1".to_string())
    );
}

#[test]
fn raw_auto_routes_futures_paths_to_futures_base_url() {
    let (futures_base_url, handle) = recording_server();
    let client = BinanceClient::with_base_urls(
        None,
        None,
        Duration::from_secs(2),
        "http://127.0.0.1:9".to_string(),
        futures_base_url,
    )
    .expect("client");

    let response = client
        .request_raw_auto_blocking(HttpMethod::Get, "/fapi/v1/exchangeInfo", Vec::new(), false)
        .expect("response");

    assert_eq!(response.status, 200);
    assert_eq!(
        handle.join().expect("server"),
        Some("GET /fapi/v1/exchangeInfo HTTP/1.1".to_string())
    );
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
    let client = BinanceClient::new(None, None, Duration::from_secs(1))
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
fn futures_algo_lookup_requires_an_identifier_before_requesting() {
    let client = BinanceClient::new(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(1),
    )
    .expect("client");

    let error = block_on(async move {
        client
            .private_request("cancel_futures_algo_order", Vec::new())
            .await
    })
    .expect_err("missing algo identifier must fail");

    assert_eq!(
        error,
        DcexError::InvalidInput("Either algoId or clientAlgoId is required.".to_string())
    );
}
