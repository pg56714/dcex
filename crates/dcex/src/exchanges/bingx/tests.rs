use crate::exchange::RequestSigner;
use crate::http::{block_on, HttpMethod, HttpRequest};
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
            (
                "signature".to_string(),
                "19a79f275d914021036bb65476f48319ed590bc5f26de3e0f8e6b3aa6bb31e1f".to_string(),
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
