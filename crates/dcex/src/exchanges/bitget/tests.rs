use std::time::Duration;

use crate::http::{HttpMethod, RequestBody};

use super::client::BitgetClient;

#[test]
fn signed_batch_uses_exact_body() {
    let client = BitgetClient::new(
        Some("test_api_key_0000".to_string()),
        Some("test_api_secret_0000".to_string()),
        Some("test-passphrase".to_string()),
        Duration::from_secs(1),
    )
    .expect("client");
    let body = br#"[{"category":"SPOT","symbol":"BTCUSDT","qty":"0.001"}]"#.to_vec();
    let request = client
        .build_request(
            HttpMethod::Post,
            "/api/v3/trade/place-batch",
            Vec::new(),
            Some(body.clone()),
            true,
            1_700_000_000_000,
        )
        .expect("request");

    assert_eq!(
        request.headers.get("ACCESS-SIGN").map(String::as_str),
        Some("R/bWef7Dwp6wughM4S1AulQN6C10+sQmcP55rWFxRoc=")
    );
    assert_eq!(request.body, RequestBody::Raw(body));
}
