#[cfg(test)]
#[allow(clippy::module_inception)]
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
        let client = BackpackClient::public(5_000, Duration::from_secs(1))
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

    #[test]
    fn rejects_window_above_official_maximum() {
        let error = BackpackClient::public(60_001, Duration::from_secs(1))
            .err()
            .expect("window must be rejected");

        assert!(error.to_string().contains("60000"));
    }

    #[test]
    fn rejects_partial_credentials() {
        let error = BackpackClient::new(
            Some(base64::engine::general_purpose::STANDARD.encode([b'2'; 32])),
            None,
            5_000,
            Duration::from_secs(1),
        )
        .err()
        .expect("partial credentials must be rejected");

        assert!(error.to_string().contains("provided together"));
    }

    #[test]
    fn rfq_symbol_fallback_uses_the_stock_rfq_suffix() {
        let client = BackpackClient::public(5_000, Duration::from_secs(1)).expect("client");
        assert_eq!(
            client.exchange_symbol("AAPL.US-USDC-RFQ").expect("symbol"),
            "AAPL.US_USDC_RFQ"
        );
    }

    #[test]
    fn rfq_submit_body_resolves_symbol_and_scalar_types() {
        let client = BackpackClient::public(5_000, Duration::from_secs(1)).expect("client");
        let params = crate::exchanges::backpack::params::BackpackParams::from_pairs(vec![
            ("product_symbol".to_string(), "AAPL.US-USDC-RFQ".to_string()),
            ("side".to_string(), "Bid".to_string()),
            ("executionMode".to_string(), "AwaitAccept".to_string()),
            ("quantity".to_string(), "0.5".to_string()),
            ("autoLend".to_string(), "true".to_string()),
        ]);

        let body = client.rfq_submit_body(&params).expect("body");
        assert_eq!(body.get("symbol"), Some(&json!("AAPL.US_USDC_RFQ")));
        assert_eq!(body.get("quantity"), Some(&json!("0.5")));
        assert_eq!(body.get("autoLend"), Some(&json!(true)));
    }

    #[test]
    fn stock_rfq_rejects_quote_quantity() {
        let client = BackpackClient::public(5_000, Duration::from_secs(1)).expect("client");
        let error = crate::http::block_on(async move {
            client
                .private_request(
                    "submit_rfq",
                    vec![
                        ("product_symbol".to_string(), "AAPL.US-USDC-RFQ".to_string()),
                        ("side".to_string(), "Bid".to_string()),
                        ("executionMode".to_string(), "AwaitAccept".to_string()),
                        ("quoteQuantity".to_string(), "100".to_string()),
                    ],
                )
                .await
        })
        .expect_err("stock RFQ quoteQuantity must fail");

        assert!(error.to_string().contains("require quantity"));
    }
}
