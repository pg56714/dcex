use super::helpers::*;

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
fn query_is_encoded_for_transport_but_not_for_signing() {
    let client = KucoinClient::new(
        Some("key".to_string()),
        Some("secret".to_string()),
        Some("passphrase".to_string()),
        Duration::from_secs(1),
    )
    .expect("client");
    let timestamp = "1700000000000";
    let raw_value = "BTC/USDT+cash value";
    let request = client
        .build_request(
            HttpMethod::Get,
            KucoinMarket::Spot,
            "/api/v1/accounts",
            vec![("currency".to_string(), raw_value.to_string())],
            None,
            true,
            timestamp,
        )
        .expect("request");

    assert_eq!(
        request.path,
        "/api/v1/accounts?currency=BTC%2FUSDT%2Bcash+value"
    );
    let expected = request_signature(
        "secret",
        timestamp,
        HttpMethod::Get,
        "/api/v1/accounts?currency=BTC/USDT+cash value",
        &[],
    )
    .expect("signature");
    assert_eq!(request.headers.get("KC-API-SIGN"), Some(&expected));
}

#[test]
fn delete_batch_cancel_preserves_body_and_signs_exact_bytes() {
    let client = KucoinClient::new(
        Some("key".into()),
        Some("secret".into()),
        Some("passphrase".into()),
        Duration::from_secs(1),
    )
    .expect("client");
    let body = br#"{"orderIdsList":["123","456"]}"#.to_vec();
    let request = client
        .build_request(
            HttpMethod::Delete,
            KucoinMarket::Futures,
            "/api/v1/orders/multi-cancel",
            Vec::new(),
            Some(body.clone()),
            true,
            "1700000000000",
        )
        .expect("request");
    assert_eq!(request.path, "/api/v1/orders/multi-cancel");
    match request.body {
        crate::http::RequestBody::Raw(actual) => assert_eq!(actual, body),
        _ => panic!("DELETE must carry the caller's JSON bytes"),
    }
    // Independently generated with Python hashlib/hmac, including the JSON body.
    assert_eq!(
        request.headers.get("KC-API-SIGN").map(String::as_str),
        Some("nkl3PqCb1JDeDputCiNgxNFASteKlyViBGKdX62mv9k=")
    );
}
