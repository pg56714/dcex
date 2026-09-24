use std::time::Duration;

use crate::http::{HttpMethod, RequestBody};

use super::client::BitgetClient;
use super::params::BitgetParams;

#[test]
fn signed_batch_uses_exact_body() {
    let client = BitgetClient::new(
        Some("test_api_key_0000".to_string()),
        Some("test_api_secret_0000".to_string()),
        Some("test-passphrase".to_string()),
        Duration::from_secs(1),
    )
    .expect("client");
    let body = br#"[{"category":"SPOT","symbol":"BTCUSDT","qty":"0.001"}]"#.to_vec();
    let request = client
        .build_request(
            HttpMethod::Post,
            "/api/v3/trade/place-batch",
            Vec::new(),
            Some(body.clone()),
            true,
            1_700_000_000_000,
        )
        .expect("request");

    assert_eq!(
        request.headers.get("ACCESS-SIGN").map(String::as_str),
        Some("R/bWef7Dwp6wughM4S1AulQN6C10+sQmcP55rWFxRoc=")
    );
    assert_eq!(request.body, RequestBody::Raw(body));
}

fn private_client() -> BitgetClient {
    BitgetClient::new(
        Some("test_api_key_0000".to_string()),
        Some("test_api_secret_0000".to_string()),
        Some("test-passphrase".to_string()),
        Duration::from_secs(1),
    )
    .expect("client")
}

#[tokio::test]
async fn uta_strategy_order_requires_product_symbol() {
    let params =
        BitgetParams::from_pairs(vec![("category".to_string(), "USDT-FUTURES".to_string())]);
    let error = private_client()
        .trade_private_request("place_uta_strategy_order", &params)
        .await
        .expect_err("missing product symbol must fail before sending a request");

    assert!(error
        .to_string()
        .contains("Specify product_symbol or symbol."));
}

#[tokio::test]
async fn uta_strategy_modification_requires_order_id_and_quantity() {
    let empty = BitgetParams::from_pairs(Vec::new());
    let error = private_client()
        .trade_private_request("modify_uta_strategy_order", &empty)
        .await
        .expect_err("missing order ID must fail before sending a request");
    assert!(error
        .to_string()
        .contains("missing required parameter: orderId"));

    let order_id_only = BitgetParams::from_pairs(vec![("orderId".to_string(), "1".to_string())]);
    let error = private_client()
        .trade_private_request("modify_uta_strategy_order", &order_id_only)
        .await
        .expect_err("missing quantity must fail before sending a request");
    assert!(error
        .to_string()
        .contains("missing required parameter: qty"));
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
    assert!(error
        .to_string()
        .contains("Specify product_symbol or symbol."));

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
