use std::time::Duration;

use crate::http::{HttpMethod, RequestBody};
use crate::product_table::{MarketInfo, ProductTable};

use super::*;

fn client() -> MexcClient {
    MexcClient::new(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(1),
    )
    .expect("client")
}

#[test]
fn spot_signature_matches_python_protocol() {
    let request = client()
        .build_request(
            HttpMethod::Get,
            MexcApi::Spot,
            "/api/v3/order",
            vec![("symbol".to_string(), "BTCUSDT".to_string())],
            None,
            true,
            1_700_000_000_000,
        )
        .expect("request");

    assert_eq!(
        request.query,
        vec![
            ("symbol".to_string(), "BTCUSDT".to_string()),
            ("timestamp".to_string(), "1700000000000".to_string()),
            (
                "signature".to_string(),
                "6244d11c958f45ac56733152cb3cb1831d23a2b3709b3a88b8b42a072aceb410".to_string(),
            ),
        ]
    );
}

#[test]
fn contract_signature_uses_exact_json_body() {
    let request = client()
        .build_request(
            HttpMethod::Post,
            MexcApi::Contract,
            "/api/v1/private/order/cancel",
            Vec::new(),
            Some(br#"[{"orderId":"1"},{"orderId":"2"}]"#.to_vec()),
            true,
            1_700_000_000_000,
        )
        .expect("request");

    assert_eq!(
        request.headers.get("Signature").map(String::as_str),
        Some("5767f5e6ba9a1f7bf0e35db1de5ecf52d00218b3f2bc2939b4d5ed5758bb0944")
    );
    assert_eq!(
        request.body,
        RequestBody::Raw(br#"[{"orderId":"1"},{"orderId":"2"}]"#.to_vec())
    );
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
