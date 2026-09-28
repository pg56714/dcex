use super::helpers::*;

#[test]
fn eip712_signature_matches_python_vector() {
    let message = "symbol=BTCUSDT&side=BUY&type=MARKET&quantity=0.001\
&nonce=1700000000000000&signer=0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a";
    assert_eq!(
        sign_message(message, &[0x11; 32]).expect("signature"),
        "0x3ca64e9c82501b8f15cd31348beaaf1aa6636cbba5fb2bc8d1bccf8ee2ffd310\
1a3724dfa8fd2f36de42d3a641b95599d0d4dee5ffb9010eb33b44784d3f60191c"
    );
}

#[test]
fn signed_futures_request_includes_user_before_signer() {
    let client = AsterClient::new(
        Some("0x0000000000000000000000000000000000000001".to_string()),
        Some("0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a".to_string()),
        Some(format!("0x{}", "11".repeat(32))),
        Duration::from_secs(1),
    )
    .expect("client");
    let nonce = client.reserve_nonce().unwrap();
    let request = client
        .build_request(
            HttpMethod::Get,
            AsterMarket::Futures,
            "/fapi/v3/balance",
            Vec::new(),
            true,
            Some(nonce),
        )
        .expect("request");

    assert_eq!(
        request.headers.get("Accept").map(String::as_str),
        Some("application/json")
    );
    assert!(request.path.contains(&format!("nonce={nonce}")));
    assert!(
        request
            .path
            .contains("user=0x0000000000000000000000000000000000000001")
    );
    assert!(
        request
            .path
            .contains("signer=0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a")
    );
    assert!(request.path.contains("signature=0x"));
}
