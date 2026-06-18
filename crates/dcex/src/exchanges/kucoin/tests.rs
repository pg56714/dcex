use std::time::Duration;

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
    let client = KucoinClient::new(None, None, None, Duration::from_secs(1)).expect("client");

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
