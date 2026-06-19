#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;
    use std::time::Duration;

    use base64::Engine;
    use serde_json::{json, Value};

    use crate::http::HttpMethod;
    use crate::product_table::{MarketInfo, ProductTable};

    use crate::exchanges::backpack::BackpackClient;

    #[test]
    fn signature_matches_python_vector() {
        let client = BackpackClient::new(
            Some(base64::engine::general_purpose::STANDARD.encode([b'2'; 32])),
            Some(base64::engine::general_purpose::STANDARD.encode([b'1'; 32])),
            5_000,
            Duration::from_secs(1),
        )
        .expect("client");
        let request = client
            .build_request(
                HttpMethod::Get,
                "/api/v1/order",
                vec![
                    ("symbol".to_string(), "BTC_USDC".to_string()),
                    ("orderId".to_string(), "test-order-id".to_string()),
                ],
                None,
                true,
                Some("orderQuery"),
                Some(&[vec![
                    ("symbol".to_string(), "BTC_USDC".to_string()),
                    ("orderId".to_string(), "test-order-id".to_string()),
                ]]),
                BTreeMap::new(),
                "1700000000000",
            )
            .expect("request");

        assert_eq!(
            request.headers.get("X-Signature").map(String::as_str),
            Some(
                "rzPMmBB/3emqFrFFImSTG2B42lnb/wa7k8+/5GEfCbPsnD4Ekp3i54huIhYxkkdH2wqP5nYxvMUEWaDp9l6ZAw=="
            )
        );
        assert_eq!(
            request.path,
            "/api/v1/order?symbol=BTC_USDC&orderId=test-order-id"
        );
    }

    #[test]
    fn product_table_resolves_canonical_symbol() {
        let table = ProductTable::new(vec![MarketInfo {
            exchange: "backpack".to_string(),
            exchange_symbol: "BTC_USDC_PERP".to_string(),
            product_symbol: "BTC-USDC-SWAP".to_string(),
            product_type: "swap".to_string(),
            exchange_type: "PERP".to_string(),
            price_precision: "0.1".to_string(),
            size_precision: "0.001".to_string(),
            min_size: "0.001".to_string(),
            base_currency: "BTC".to_string(),
            quote_currency: "USDC".to_string(),
            min_notional: "0".to_string(),
            size_per_contract: "1".to_string(),
        }]);
        let client = BackpackClient::new(None, None, 5_000, Duration::from_secs(1))
            .expect("client")
            .with_product_table(table);

        assert_eq!(
            client.exchange_symbol("BTC-USDC-SWAP").expect("symbol"),
            "BTC_USDC_PERP"
        );
    }

    #[test]
    fn batch_orders_resolve_product_symbol() {
        let client = BackpackClient::new(
            Some(base64::engine::general_purpose::STANDARD.encode([b'2'; 32])),
            Some(base64::engine::general_purpose::STANDARD.encode([b'1'; 32])),
            5_000,
            Duration::from_secs(1),
        )
        .expect("client");
        let params = vec![(
            "orders".to_string(),
            json!([
                {
                    "product_symbol": "BTC-USDC-SPOT",
                    "side": "Bid",
                    "orderType": "Limit",
                    "quantity": "1",
                    "price": "1"
                }
            ])
            .to_string(),
        )];
        let body = client
            .batch_orders_body(
                &crate::exchanges::backpack::params::BackpackParams::from_pairs(params),
            )
            .expect("batch body");
        let Value::Array(orders) = body else {
            panic!("expected array");
        };
        assert_eq!(
            orders[0].get("symbol"),
            Some(&Value::String("BTC_USDC".to_string()))
        );
        assert!(orders[0].get("product_symbol").is_none());
    }
}
