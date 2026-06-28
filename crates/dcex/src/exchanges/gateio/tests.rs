use std::time::Duration;

use crate::http::HttpMethod;

use super::client::GateioClient;
use super::params::{normalize_side, signed_size};

#[test]
fn signature_matches_python_vector() {
    let client = GateioClient::new(
        Some("test_api_key_0000".to_string()),
        Some("test_api_secret_0000".to_string()),
        Duration::from_secs(1),
    )
    .expect("client");
    let request = client
        .build_request(
            HttpMethod::Post,
            "/api/v4/spot/orders",
            vec![("a".to_string(), "1".to_string())],
            Some(br#"{"b":"2"}"#.to_vec()),
            true,
            1_700_000_000,
        )
        .expect("request");
    assert_eq!(
        request.headers.get("SIGN").map(String::as_str),
        Some(
            "3a314366c1367344b6abbad3a7f0b0519a5f1f606acde4c269a8cada67d7ddbd\
33504564f284bd0f8f7be971075a6ef0f8a47f95f310cad579fdb483f0330b7a"
        )
    );
}

#[test]
fn normalizes_side_and_contract_size() {
    assert_eq!(normalize_side("BUY").expect("buy"), "buy");
    assert_eq!(normalize_side("sell").expect("sell"), "sell");
    assert_eq!(signed_size("-3", true).expect("positive"), 3);
    assert_eq!(signed_size("3", false).expect("negative"), -3);
}
