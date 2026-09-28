use super::helpers::*;

#[tokio::test]
async fn advanced_contract_orders_reject_missing_required_fields_before_transport() {
    let empty = params::MexcParams::from_pairs(Vec::new());
    let error = client()
        .trade_private_request("amend_contract_limit_order", &empty)
        .await
        .expect_err("missing order ID");
    assert!(error.to_string().contains("orderId"));

    let tpsl = params::MexcParams::from_pairs(vec![
        ("lossTrend".into(), "1".into()),
        ("profitTrend".into(), "1".into()),
        ("positionId".into(), "7".into()),
        ("vol".into(), "1".into()),
    ]);
    let error = client()
        .trade_private_request("place_contract_position_tpsl", &tpsl)
        .await
        .expect_err("TP/SL price required");
    assert!(error.to_string().contains("stopLossPrice"));
}

#[tokio::test]
async fn multi_asset_mode_rejects_non_boolean_path_value() {
    let params = params::MexcParams::from_pairs(vec![("isMultiAssetMode".into(), "yes".into())]);
    let error = client()
        .account_private_request("change_contract_multi_asset_mode", &params)
        .await
        .expect_err("mode must be true or false");
    assert!(error.to_string().contains("isMultiAssetMode"));
}

#[test]
fn exchange_symbol_uses_product_table_when_available() {
    let table = ProductTable::new(vec![MarketInfo {
        exchange: "mexc".to_string(),
        exchange_symbol: "BTC_USDT".to_string(),
        product_symbol: "BTC-USDT-SWAP".to_string(),
        product_type: "swap".to_string(),
        exchange_type: "linear".to_string(),
        price_precision: "0.1".to_string(),
        size_precision: "1".to_string(),
        min_size: "1".to_string(),
        base_currency: "BTC".to_string(),
        quote_currency: "USDT".to_string(),
        min_notional: "0".to_string(),
        size_per_contract: "1".to_string(),
    }]);
    let client = client().with_product_table(table);

    assert_eq!(
        client.exchange_symbol("BTC-USDT-SWAP", "").expect("symbol"),
        "BTC_USDT"
    );
}
