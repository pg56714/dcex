use std::time::Duration;

use serde_json::{json, Value};

use crate::http::HttpMethod;

use super::*;

#[test]
fn signature_includes_encoded_query_path() {
    let client = BitmexClient::new(
        Some("api-key".to_string()),
        Some("test_api_secret_0000".to_string()),
        Duration::from_secs(1),
    )
    .expect("client");
    let request = client
        .build_request(
            HttpMethod::Get,
            "/api/v1/order",
            vec![("symbol".to_string(), "XBT USD".to_string())],
            None,
            true,
            1_700_000_005,
        )
        .expect("request");

    assert_eq!(
        request.headers.get("api-signature").map(String::as_str),
        Some("905e6a49c2961c68bc44ba85b3357543b65aaac1e032d40531df86ecae67feeb")
    );
}

#[test]
fn limit_buy_shortcut_builds_order_body_without_side_param() {
    let client = BitmexClient::new(None, None, Duration::from_secs(1)).expect("client");
    let params = params::BitmexParams::from_pairs(vec![
        ("product_symbol".to_string(), "XBT-USD-SWAP".to_string()),
        ("orderQty".to_string(), "100".to_string()),
        ("price".to_string(), "1.5".to_string()),
    ]);
    let body = client
        .order_body_from_params(
            &params,
            Some("Buy"),
            Some("Limit"),
            Some(("timeInForce", "GoodTillCancel")),
        )
        .expect("body");

    assert_eq!(
        Value::Object(body),
        json!({
            "symbol": "XBTUSD",
            "side": "Buy",
            "ordType": "Limit",
            "orderQty": 100,
            "price": 1.5,
            "timeInForce": "GoodTillCancel"
        })
    );
}

#[test]
fn amend_order_requires_order_identifier() {
    let client = BitmexClient::new(None, None, Duration::from_secs(1)).expect("client");
    let params = params::BitmexParams::from_pairs(vec![
        ("product_symbol".to_string(), "XBT-USD-SWAP".to_string()),
        ("price".to_string(), "1.5".to_string()),
    ]);

    assert!(client.amend_order_body_from_params(&params).is_err());
}

#[test]
fn cancel_order_accepts_array_identifiers() {
    let client = BitmexClient::new(None, None, Duration::from_secs(1)).expect("client");
    let params = params::BitmexParams::from_pairs(vec![
        (
            "orderID".to_string(),
            "[\"order-a\",\"order-b\"]".to_string(),
        ),
        ("text".to_string(), "cancel".to_string()),
    ]);
    let body = client.cancel_order_body_from_params(&params);

    assert_eq!(
        Value::Object(body),
        json!({
            "orderID": ["order-a", "order-b"],
            "text": "cancel"
        })
    );
}
