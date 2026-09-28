use super::helpers::*;

#[tokio::test]
async fn uta_strategy_order_requires_product_symbol() {
    let params =
        BitgetParams::from_pairs(vec![("category".to_string(), "USDT-FUTURES".to_string())]);
    let error = private_client()
        .trade_private_request("place_uta_strategy_order", &params)
        .await
        .expect_err("missing product symbol must fail before sending a request");

    assert!(
        error
            .to_string()
            .contains("Specify product_symbol or symbol.")
    );
}

#[tokio::test]
async fn reality_fills_rejects_out_of_range_limit_before_transport() {
    let params = BitgetParams::from_pairs(vec![
        ("product_symbol".into(), "RAAPLUSDT".into()),
        ("limit".into(), "101".into()),
    ]);
    let error = private_client()
        .account_private_request("get_reality_fills", &params)
        .await
        .expect_err("limit above 100");
    assert!(error.to_string().contains("between 1 and 100"));
}

#[tokio::test]
async fn reality_order_requires_symbol_and_identifier_before_cancel() {
    let empty = BitgetParams::from_pairs(Vec::new());
    let error = private_client()
        .trade_private_request("cancel_reality_order", &empty)
        .await
        .expect_err("missing Reality symbol must fail before sending a request");
    assert!(
        error
            .to_string()
            .contains("Specify product_symbol or symbol.")
    );

    let symbol_only = BitgetParams::from_pairs(vec![(
        "product_symbol".to_string(),
        "RAAPL-USDT-SPOT".to_string(),
    )]);
    let error = private_client()
        .trade_private_request("cancel_reality_order", &symbol_only)
        .await
        .expect_err("missing order identifier must fail before sending a request");
    assert!(error.to_string().contains("Specify orderId or clientOid."));
}
