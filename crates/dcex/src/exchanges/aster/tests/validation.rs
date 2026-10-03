use super::helpers::*;

#[test]
fn raw_auto_rejects_unsupported_path_prefixes() {
    assert_eq!(
        AsterMarket::from_path("/unknown"),
        Err(DcexError::InvalidInput(
            "unsupported Aster API path: /unknown".to_string()
        ))
    );
}

#[test]
fn product_table_resolves_canonical_symbol() {
    let table = ProductTable::new(vec![MarketInfo {
        exchange: "aster".to_string(),
        exchange_symbol: "ASTERUSDT".to_string(),
        product_symbol: "ASTER-USDT-SWAP".to_string(),
        product_type: "swap".to_string(),
        exchange_type: "PERP".to_string(),
        price_precision: "0.0001".to_string(),
        size_precision: "0.1".to_string(),
        min_size: "0.1".to_string(),
        base_currency: "ASTER".to_string(),
        quote_currency: "USDT".to_string(),
        min_notional: "5".to_string(),
        size_per_contract: "1".to_string(),
        ..MarketInfo::default()
    }]);
    let client = AsterClient::public(Duration::from_secs(1))
        .expect("client")
        .with_product_table(table);

    assert_eq!(
        client.exchange_symbol("ASTER-USDT-SWAP").expect("symbol"),
        "ASTERUSDT"
    );
}

#[test]
fn batch_orders_resolve_product_symbol_and_side() {
    let client = AsterClient::public(Duration::from_secs(1)).expect("client");
    let params = AsterParams::from_pairs(vec![(
        "batchOrders".to_string(),
        json!([
            {
                "product_symbol": "ASTER-USDT-SWAP",
                "side": "buy",
                "type": "LIMIT",
                "timeInForce": "GTC",
                "quantity": "1",
                "price": "1"
            }
        ])
        .to_string(),
    )]);
    let body = client.resolve_batch_orders(&params).expect("batch orders");
    let Value::Array(items) = serde_json::from_str(&body).expect("json") else {
        panic!("expected array");
    };
    assert_eq!(
        items[0].get("symbol"),
        Some(&Value::String("ASTERUSDT".to_string()))
    );
    assert_eq!(
        items[0].get("side"),
        Some(&Value::String("BUY".to_string()))
    );
    assert!(items[0].get("product_symbol").is_none());
}

#[test]
fn credentials_must_be_paired_and_addresses_are_validated() {
    assert!(
        AsterClient::new(
            None,
            Some("0x19e7e376e7c213b7e7e7e46cc70a5dd086daff2a".to_string()),
            None,
            Duration::from_secs(1),
        )
        .is_err()
    );
    assert!(
        AsterClient::new(
            Some("not-an-address".to_string()),
            None,
            None,
            Duration::from_secs(1),
        )
        .is_err()
    );
}

#[tokio::test]
async fn remaining_openable_notional_is_public_and_validates_leverage() {
    let (base_url, handle) = recording_server();
    let client = AsterClient::with_base_urls(
        None,
        None,
        None,
        Duration::from_secs(10),
        "http://127.0.0.1:9".into(),
        base_url,
    )
    .expect("client");
    client
        .public_request(
            "get_futures_remaining_openable_notional",
            vec![
                ("product_symbol".into(), "ASTER-USDT-SWAP".into()),
                ("leverage".into(), "5".into()),
            ],
        )
        .await
        .expect("public request");
    let line = handle.join().expect("server").expect("request");
    assert!(
        line.starts_with(
            "GET /fapi/v3/remainingOpenableNotionalValue?symbol=ASTERUSDT&leverage=5 HTTP/1.1"
        ),
        "{line}"
    );

    let client = AsterClient::public(Duration::from_secs(10)).expect("client");
    assert!(
        client
            .public_request(
                "get_futures_remaining_openable_notional",
                vec![
                    ("product_symbol".into(), "ASTER-USDT-SWAP".into()),
                    ("leverage".into(), "0".into()),
                ]
            )
            .await
            .is_err()
    );
}

#[test]
fn batch_amendments_normalize_symbols_and_validate_each_order() {
    let client = AsterClient::public(Duration::from_secs(1)).expect("client");
    let params = AsterParams::from_pairs(vec![("batchOrders".into(), json!([
        {"product_symbol":"ASTER-USDT-SWAP", "orderId":123, "side":"buy", "quantity":"2", "price":"1.2"},
        {"symbol":"BTCUSDT", "origClientOrderId":"mine", "quantity":"3", "price":"2.1"}
    ]).to_string())]);
    let resolved = client
        .resolve_batch_amendments(&params)
        .expect("batch amendments");
    let orders: Value = serde_json::from_str(&resolved).expect("JSON");
    assert_eq!(orders[0]["symbol"], "ASTERUSDT");
    assert_eq!(orders[0]["side"], "BUY");
    assert!(orders[0].get("product_symbol").is_none());
    assert_eq!(orders[1]["origClientOrderId"], "mine");

    let bad = AsterParams::from_pairs(vec![(
        "batchOrders".into(),
        json!([
            {"symbol":"BTCUSDT", "orderId":123, "quantity":"0", "price":"2"}
        ])
        .to_string(),
    )]);
    assert!(client.resolve_batch_amendments(&bad).is_err());
}
