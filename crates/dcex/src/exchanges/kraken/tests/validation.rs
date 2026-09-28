use super::helpers::*;

#[test]
fn futures_dead_mans_switch_rejects_invalid_timeout_before_network() {
    let client = KrakenClient::public(Duration::from_secs(1)).expect("client");
    let error = crate::http::block_on(async move {
        client
            .private_request(
                "cancel_futures_all_orders_after",
                vec![("timeout".into(), "-1".into())],
            )
            .await
    })
    .expect_err("negative timeout");
    assert!(error.to_string().contains("non-negative"));
}

#[test]
fn xstock_symbol_infers_tokenized_asset_class() {
    let client = KrakenClient::public(Duration::from_secs(1)).expect("client");
    assert_eq!(
        client
            .spot_asset_class("AAPLx-USD-SPOT")
            .expect("asset class"),
        Some("tokenized_asset".to_string())
    );
    assert_eq!(
        client
            .spot_asset_class("BTC-USD-SPOT")
            .expect("asset class"),
        None
    );
}
