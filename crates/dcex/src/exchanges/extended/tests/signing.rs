use super::helpers::*;

#[test]
fn testnet_base_url_uses_sepolia_signing_domain() {
    assert_eq!(
        signing_domain_for_base_url("https://api.starknet.sepolia.extended.exchange").chain_id,
        "SN_SEPOLIA"
    );
    assert_eq!(
        signing_domain_for_base_url("https://api.starknet.extended.exchange").chain_id,
        "SN_MAIN"
    );
}

#[tokio::test]
async fn signed_internal_transfer_uses_user_transfer_route() {
    let body = serde_json::json!({
        "fromAccount": 3004,
        "toAccount": 7349,
        "amount": "1000",
        "transferredAsset": "USD",
        "settlement": {
            "amount": 1000000000,
            "assetId": "0x1",
            "expirationTimestamp": 478932,
            "nonce": 758978120,
            "receiverPositionId": 104350,
            "receiverPublicKey": "0x2",
            "senderPositionId": 100005,
            "senderPublicKey": "0x2",
            "signature": {"r": "abc", "s": "def"}
        }
    });
    let request = private_request(
        "submit_internal_transfer",
        vec![("body".into(), body.to_string())],
    )
    .await;
    assert_request_line(&request, "POST /api/v1/user/transfer HTTP/1.1");
    let sent: serde_json::Value =
        serde_json::from_str(request.split("\r\n\r\n").nth(1).expect("body")).expect("JSON");
    assert_eq!(sent, body);
}
