use super::helpers::*;

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

#[test]
fn unsigned_post_json_does_not_duplicate_fields_in_query() {
    let client = BingxClient::public(Duration::from_secs(1)).expect("client");
    let body = serde_json::json!({"symbol": "BTCUSDT", "limit": 1});
    let request = client.build_request(
        HttpMethod::Post,
        "/test",
        vec![
            ("symbol".into(), "BTCUSDT".into()),
            ("limit".into(), "1".into()),
        ],
        false,
        Vec::new(),
        Some(body.clone()),
    );
    assert!(request.query.is_empty());
    assert!(!request.headers.contains_key("X-BX-APIKEY"));
    match request.body {
        crate::http::RequestBody::Json(actual) => assert_eq!(actual, body),
        _ => panic!("unsigned POST must preserve its JSON body"),
    }
}
