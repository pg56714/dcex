use super::helpers::*;

#[test]
fn signature_matches_python_vector() {
    let client = BackpackClient::new(
        Some(base64::engine::general_purpose::STANDARD.encode([b'2'; 32])),
        Some(base64::engine::general_purpose::STANDARD.encode([b'1'; 32])),
        5_000,
        Duration::from_secs(1),
    )
    .expect("client");
    let request = client
        .build_request(
            HttpMethod::Get,
            "/api/v1/order",
            vec![
                ("symbol".to_string(), "BTC_USDC".to_string()),
                ("orderId".to_string(), "test-order-id".to_string()),
            ],
            None,
            true,
            Some("orderQuery"),
            Some(&[vec![
                ("symbol".to_string(), "BTC_USDC".to_string()),
                ("orderId".to_string(), "test-order-id".to_string()),
            ]]),
            BTreeMap::new(),
            "1700000000000",
        )
        .expect("request");

    assert_eq!(
        request.headers.get("X-Signature").map(String::as_str),
        Some(
            "rzPMmBB/3emqFrFFImSTG2B42lnb/wa7k8+/5GEfCbPsnD4Ekp3i54huIhYxkkdH2wqP5nYxvMUEWaDp9l6ZAw=="
        )
    );
    assert_eq!(
        request.path,
        "/api/v1/order?symbol=BTC_USDC&orderId=test-order-id"
    );
}
