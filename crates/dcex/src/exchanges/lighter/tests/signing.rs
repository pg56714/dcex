use super::helpers::*;

#[test]
fn account_orders_uses_client_indexes_and_auth_header() {
    let (base_url, handle) = recording_server();
    let client = LighterClient::with_base_url_and_credentials(
        Duration::from_secs(10),
        base_url,
        Some(12),
        None,
        None,
    )
    .expect("client");
    block_on(async move {
        client
            .private_request(
                "get_account_orders",
                vec![
                    ("client_order_indexes".into(), "123,456".into()),
                    ("authorization".into(), "test-token".into()),
                ],
            )
            .await
    })
    .expect("request");
    let line = handle.join().expect("server").expect("request line");
    assert!(line.starts_with("GET /api/v1/accountOrders?"), "{line}");
    assert!(line.contains("account_index=12"), "{line}");
    assert!(line.contains("client_order_indexes=123%2C456"), "{line}");
}

#[test]
fn auth_token_uses_configured_private_key() {
    let client = LighterClient::with_base_url_and_credentials(
        Duration::from_secs(10),
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

#[test]
fn custom_url_does_not_guess_a_signing_chain() {
    let client =
        LighterClient::with_base_url(Duration::from_secs(10), "http://localhost:8000".to_string())
            .expect("client");

    assert_eq!(client.network(), None);
    assert_eq!(client.chain_id(), None);
    assert!(client.signing_chain_id().is_err());
}

#[test]
fn custom_url_accepts_an_explicit_signing_chain() {
    let client = LighterClient::with_base_url_credentials_and_chain_id(
        Duration::from_secs(10),
        "http://localhost:8000".to_string(),
        466_324,
        None,
        None,
        None,
    )
    .expect("client");

    assert_eq!(client.network(), None);
    assert_eq!(client.chain_id(), Some(466_324));
}
