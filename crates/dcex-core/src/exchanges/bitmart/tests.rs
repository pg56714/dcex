use std::time::Duration;

use serde_json::{json, Value};

use crate::http::{HttpMethod, RequestBody};

use super::*;

#[test]
fn signed_post_uses_exact_body() {
    let client = BitmartClient::new(
        Some("api-key".to_string()),
        Some("test_api_secret_0000".to_string()),
        Some("test_memo".to_string()),
        Duration::from_secs(1),
    )
    .expect("client");
    let body = br#"{"symbol":"BTCUSDT"}"#.to_vec();
    let request = client
        .build_request(
            HttpMethod::Post,
            BitmartMarket::Spot,
            "/spot/v2/submit_order",
            Vec::new(),
            Some(body.clone()),
            true,
            1_700_000_000_000,
        )
        .expect("request");

    assert_eq!(
        request.headers.get("X-BM-SIGN").map(String::as_str),
        Some("a5a38bab707890a577d96959ca82a1b7a4c0db7ffd9b40ba17b20ad57932a542")
    );
    assert_eq!(request.body, RequestBody::Raw(body));
}

#[test]
fn contract_modify_limit_order_keeps_numeric_payload_types() {
    let client = BitmartClient::new(
        Some("api-key".to_string()),
        Some("test_api_secret_0000".to_string()),
        Some("test_memo".to_string()),
        Duration::from_secs(1),
    )
    .expect("client");
    let params = params::BitmartParams::from_pairs(vec![
        ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
        ("order_id".to_string(), "123456".to_string()),
        ("price".to_string(), "100.1".to_string()),
        ("size".to_string(), "1".to_string()),
    ]);
    let mut body = serde_json::Map::new();
    client
        .insert_required_symbol(&mut body, &params, false)
        .expect("symbol");
    params::insert_optional_integer(&mut body, "order_id", params.get("order_id"));
    params::insert_optional_string(&mut body, "price", params.get("price"));
    params::insert_optional_integer(&mut body, "size", params.get("size"));

    assert_eq!(
        Value::Object(body),
        json!({
            "symbol": "BTCUSDT",
            "order_id": 123456,
            "price": "100.1",
            "size": 1
        })
    );
}

#[test]
fn spot_limit_buy_shortcut_does_not_require_side_param() {
    let client = BitmartClient::new(None, None, None, Duration::from_secs(1)).expect("client");
    let params = params::BitmartParams::from_pairs(vec![
        ("product_symbol".to_string(), "BTC-USDT-SPOT".to_string()),
        ("size".to_string(), "1".to_string()),
        ("price".to_string(), "100".to_string()),
    ]);
    let body = client
        .spot_order_body_from_params(&params, Some("buy"), Some("limit"))
        .expect("body");

    assert_eq!(
        Value::Object(body),
        json!({
            "symbol": "BTC_USDT",
            "side": "buy",
            "type": "limit",
            "size": "1",
            "price": "100"
        })
    );
}

#[test]
fn contract_cancel_order_keeps_order_id_as_string() {
    let client = BitmartClient::new(None, None, None, Duration::from_secs(1)).expect("client");
    let params = params::BitmartParams::from_pairs(vec![
        ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
        ("order_id".to_string(), "3000378272670421".to_string()),
    ]);
    let body = client
        .contract_cancel_order_body_from_params(&params)
        .expect("body");

    assert_eq!(
        Value::Object(body),
        json!({
            "symbol": "BTCUSDT",
            "order_id": "3000378272670421"
        })
    );
}
