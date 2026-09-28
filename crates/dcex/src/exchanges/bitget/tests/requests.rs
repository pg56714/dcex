use super::helpers::*;

#[tokio::test]
async fn uta_strategy_modification_requires_order_id_and_quantity() {
    let empty = BitgetParams::from_pairs(Vec::new());
    let error = private_client()
        .trade_private_request("modify_uta_strategy_order", &empty)
        .await
        .expect_err("missing order ID must fail before sending a request");
    assert!(
        error
            .to_string()
            .contains("missing required parameter: orderId")
    );

    let order_id_only = BitgetParams::from_pairs(vec![("orderId".to_string(), "1".to_string())]);
    let error = private_client()
        .trade_private_request("modify_uta_strategy_order", &order_id_only)
        .await
        .expect_err("missing quantity must fail before sending a request");
    assert!(
        error
            .to_string()
            .contains("missing required parameter: qty")
    );
}
