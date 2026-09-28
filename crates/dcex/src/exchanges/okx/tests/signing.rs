use super::helpers::*;

#[test]
fn signature_matches_python_vector() {
    let client = OkxClient::new(
        Some("test_api_key_0000".to_string()),
        Some("test_api_secret_0000".to_string()),
        Some("passphrase".to_string()),
        "0".to_string(),
        Duration::from_secs(1),
    )
    .expect("client");
    let request = client
        .build_request(
            HttpMethod::Get,
            "/api/v5/account/balance",
            Vec::new(),
            None,
            true,
            "1700000000",
        )
        .expect("request");

    assert_eq!(
        request.headers.get("OK-ACCESS-SIGN").map(String::as_str),
        Some("Ls74ct2P5Xi0SXq7smDS5O2D8cy4VmItOq3VDxnTQYE=")
    );
}
