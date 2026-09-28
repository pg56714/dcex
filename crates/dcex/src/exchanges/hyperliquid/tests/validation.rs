use super::helpers::*;

#[test]
fn spot_perp_transfer_rejects_missing_wallet_signature() {
    let client =
        HyperliquidClient::public(false, std::time::Duration::from_secs(1)).expect("client");
    let error = crate::http::block_on(async move {
        client
            .private_request(
                "transfer_usdc_spot_perp",
                vec![
                    ("amount".into(), "1".into()),
                    ("toPerp".into(), "true".into()),
                    ("nonce".into(), "1700000000000".into()),
                    ("signatureChainId".into(), "0xa4b1".into()),
                ],
            )
            .await
    })
    .expect_err("signature required");
    assert!(error.to_string().contains("signature"));
}
