use crate::exchange::RequestSigner;
use crate::http::{HttpMethod, HttpRequest, block_on};
use std::io::{Read, Write};
use std::net::TcpListener;
use std::thread;
use std::time::Duration;

use super::client::BingxClient;
use super::endpoints::BASE_URL;
use super::signing::BingxSigner;

#[test]
fn signer_uses_unescaped_sorted_payload() {
    let signer = BingxSigner {
        api_key: "api-key".to_string(),
        api_secret: "secret".to_string(),
    };
    let mut request = HttpRequest::new(HttpMethod::Get, BASE_URL, "/test");
    request.query = vec![
        ("symbol".to_string(), "BTC USDT".to_string()),
        ("limit".to_string(), "10".to_string()),
        ("type".to_string(), "LIMIT".to_string()),
    ];

    signer
        .sign(&mut request, 1_700_000_000_000)
        .expect("signature");

    assert_eq!(
        request.query,
        vec![
            ("limit".to_string(), "10".to_string()),
            ("symbol".to_string(), "BTC USDT".to_string()),
            ("timestamp".to_string(), "1700000000000".to_string()),
            ("type".to_string(), "LIMIT".to_string()),
            (
                "signature".to_string(),
                "e75f90a175ff72fbeb9ebc5a4e482bb0f16d7fa4f7cd4f1ac6ffb435249defa6".to_string(),
            ),
        ]
    );
    assert_eq!(
        request.headers.get("X-BX-APIKEY").map(String::as_str),
        Some("api-key")
    );
}

#[test]
fn listen_key_requires_api_key() {
    let client = BingxClient::public(Duration::from_secs(1)).expect("client");
    let error = block_on(async move { client.private_request("get_listen_key", Vec::new()).await })
        .expect_err("missing API key should fail before sending");
    assert_eq!(
        error.to_string(),
        "BingX API key is required for this request."
    );
}

fn recording_server() -> (String, thread::JoinHandle<String>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let url = format!("http://{}", listener.local_addr().expect("address"));
    let handle = thread::spawn(move || {
        let (mut stream, _) = listener.accept().expect("accept");
        stream
            .set_read_timeout(Some(Duration::from_secs(2)))
            .expect("timeout");
        let mut bytes = [0u8; 4096];
        let size = stream.read(&mut bytes).expect("request");
        stream.write_all(
            b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 20\r\nConnection: close\r\n\r\n{\"code\":0,\"data\":{}}",
        ).expect("response");
        String::from_utf8_lossy(&bytes[..size])
            .lines()
            .next()
            .expect("request line")
            .to_string()
    });
    (url, handle)
}

#[test]
fn new_swap_market_routes_use_official_paths() {
    let cases = [
        (
            "get_swap_premium_index",
            "/openApi/swap/v2/quote/premiumIndex",
        ),
        (
            "get_swap_funding_rate",
            "/openApi/swap/v2/quote/fundingRate",
        ),
        ("get_swap_book_ticker", "/openApi/swap/v2/quote/bookTicker"),
        ("get_swap_trading_rules", "/openApi/swap/v1/tradingRules"),
    ];
    for (method, path) in cases {
        let (url, server) = recording_server();
        let client =
            BingxClient::with_base_url(None, None, Duration::from_secs(2), url).expect("client");
        block_on(async move {
            client
                .public_request(
                    method,
                    vec![("product_symbol".into(), "BTC-USDT-SWAP".into())],
                )
                .await
        })
        .expect("request");
        let line = server.join().expect("server");
        assert!(
            line.starts_with(&format!("GET {path}?symbol=BTC-USDT")),
            "{line}"
        );
        if method == "get_swap_trading_rules" {
            assert!(line.contains("&timestamp="), "{line}");
        }
    }
}

#[test]
fn swap_commission_route_is_signed_and_funding_range_is_checked() {
    let (url, server) = recording_server();
    let client = BingxClient::with_base_url(
        Some("api-key".into()),
        Some("secret".into()),
        Duration::from_secs(2),
        url,
    )
    .expect("client");
    block_on(async move {
        client
            .private_request("get_swap_commission_rate", Vec::new())
            .await
    })
    .expect("commission");
    let line = server.join().expect("server");
    assert!(
        line.starts_with("GET /openApi/swap/v2/user/commissionRate?"),
        "{line}"
    );
    assert!(line.contains("signature="), "{line}");
    let client = BingxClient::public(Duration::from_secs(1)).expect("client");
    assert!(
        block_on(async move {
            client
                .public_request(
                    "get_swap_funding_rate",
                    vec![
                        ("start_time".into(), "2000".into()),
                        ("end_time".into(), "1000".into()),
                    ],
                )
                .await
        })
        .is_err()
    );
}
