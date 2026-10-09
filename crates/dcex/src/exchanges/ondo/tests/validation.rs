use super::helpers::*;

#[test]
fn rejects_partial_api_credentials() {
    assert!(OndoClient::new(Some("key".to_string()), None, Duration::from_secs(5)).is_err());
}

#[tokio::test]
async fn invalid_order_is_rejected_before_transport() {
    let client = OndoClient::public(Duration::from_secs(5)).expect("client");
    assert!(
        client
            .private_request(
                "place_order",
                vec![
                    ("market".to_string(), "AAPL-USD.P".to_string()),
                    ("side".to_string(), "buy".to_string()),
                    ("type".to_string(), "market".to_string()),
                    ("price".to_string(), "200".to_string()),
                    ("size".to_string(), "1".to_string()),
                ]
            )
            .await
            .is_err()
    );
}

#[test]
fn only_canonical_swap_symbols_map_to_ondo_perps() {
    let client = OndoClient::public(Duration::from_secs(5)).expect("client");
    assert_eq!(
        client.exchange_symbol("BTC-USD-SWAP").expect("symbol"),
        "BTC-USD.P"
    );
    assert!(client.exchange_symbol("BTC-USD-SPOT").is_err());
    assert_eq!(
        client
            .normalize_market_query(vec![("market".to_string(), "BTC-USD-SWAP".to_string())])
            .expect("query"),
        vec![("market".to_string(), "BTC-USD.P".to_string())]
    );
}

#[test]
fn a_loaded_ondo_table_never_falls_back_to_a_guessed_market() {
    let client = OndoClient::public(Duration::from_secs(5))
        .expect("client")
        .with_product_table(crate::product_table::ProductTable::new(vec![]));
    assert!(client.exchange_symbol("UNLISTED-USD-SWAP").is_err());
    assert!(client.exchange_symbol("BTC-USD.P").is_err());
}

#[tokio::test]
async fn raw_json_orders_cannot_bypass_validation() {
    let client = OndoClient::public(Duration::from_secs(5)).expect("client");
    let error = client
        .private_request(
            "place_order",
            vec![(
                "body".to_string(),
                r#"{"market":"BTC-USD.P","side":"wrong","size":"1","price":"100"}"#.to_string(),
            )],
        )
        .await
        .expect_err("invalid side");
    assert!(error.to_string().contains("side must be buy or sell"));
    let error = client
        .private_request(
            "place_batch_orders",
            vec![(
                "orders".to_string(),
                r#"[{"market":"BTC-USD.P","side":"buy"}]"#.to_string(),
            )],
        )
        .await
        .expect_err("missing limit price");
    assert!(
        error
            .to_string()
            .contains("limit order requires price and size")
    );
}

#[tokio::test]
async fn websocket_rejects_invalid_private_credentials_and_channels() {
    use super::super::websocket::{OndoPrivateWebSocket, OndoPublicWebSocket};

    assert!(
        OndoPrivateWebSocket::new(Some("key".to_string()), None, Duration::from_secs(5)).is_err()
    );
    let mut public = OndoPublicWebSocket::new(Duration::from_secs(5)).expect("public ws");
    assert!(public.subscribe("invalid", Vec::new()).await.is_err());
    let mut private = OndoPrivateWebSocket::new(
        Some("key".to_string()),
        Some("ondoApiSecret_SECRET".to_string()),
        Duration::from_secs(5),
    )
    .expect("private ws");
    assert!(private.subscribe("ordersPerps", Vec::new()).await.is_err());
}

#[tokio::test]
async fn stateful_account_requests_are_validated_before_transport() {
    let client = OndoClient::public(Duration::from_secs(5)).expect("client");

    for method in ["create_withdrawal", "sandbox_withdrawal"] {
        let error = client
            .private_request(method, Vec::new())
            .await
            .expect_err("withdrawal fields must be validated before transport");
        assert!(
            error
                .to_string()
                .contains("missing required parameter: customer_withdrawal_id")
        );
    }

    let error = client
        .private_request("get_withdrawal_status", Vec::new())
        .await
        .expect_err("one withdrawal identifier is required");
    assert!(error.to_string().contains("requires exactly one"));
    let error = client
        .private_request(
            "sandbox_deposit",
            vec![
                ("amount".to_string(), "1".to_string()),
                ("symbol".to_string(), "USDC".to_string()),
                (
                    "deposit_destination".to_string(),
                    r#"{"id":"account","wallet":"invalid"}"#.to_string(),
                ),
                ("chain_id".to_string(), "eth-sepolia".to_string()),
            ],
        )
        .await
        .expect_err("invalid wallet kind");
    assert!(error.to_string().contains("main or margin"));
}

#[tokio::test]
async fn order_and_body_fields_are_rejected_before_transport() {
    let client = OndoClient::public(Duration::from_secs(5)).expect("client");
    let order = |extra: serde_json::Value| {
        let mut body = serde_json::json!({"market": "AAPL-USD.P", "side": "buy", "type": "limit",
                                          "price": "200", "size": "1"});
        for (key, value) in extra.as_object().unwrap() {
            if value.is_null() {
                body.as_object_mut().unwrap().remove(key);
            } else {
                body[key] = value.clone();
            }
        }
        body
    };
    let body = |value: serde_json::Value| vec![("body", value.to_string())];
    let twap = |value: serde_json::Value| body(value);
    let pairs = |items: &[(&'static str, &'static str)]| {
        items
            .iter()
            .map(|(key, value)| (*key, value.to_string()))
            .collect::<Vec<_>>()
    };
    let base_twap = serde_json::json!({"market": "AAPL-USD.P", "side": "buy", "size": "1",
                                       "runningTime": 60, "frequency": 30});
    let mut twap_bad_bool = base_twap.clone();
    twap_bad_bool["reduceOnly"] = "yes".into();
    let mut twap_bad_int = base_twap.clone();
    twap_bad_int["frequency"] = "30".into();
    let mut twap_missing = base_twap.clone();
    twap_missing["market"] = " ".into();
    type Case<'a> = (&'a str, Vec<(&'a str, String)>, &'a str);
    let cases: Vec<Case> = vec![
        (
            "place_order",
            pairs(&[
                ("market", "AAPL-USD.P"),
                ("side", "buy"),
                ("price", "1"),
                ("size", "1"),
                ("quoteSize", "1"),
            ]),
            "limit orders cannot include quoteSize",
        ),
        (
            "place_order",
            pairs(&[
                ("market", "AAPL-USD.P"),
                ("side", "buy"),
                ("type", "market"),
            ]),
            "exactly one of size or quoteSize",
        ),
        (
            "place_order",
            pairs(&[
                ("market", "AAPL-USD.P"),
                ("side", "buy"),
                ("market", "MSFT-USD.P"),
            ]),
            "duplicate Ondo parameter: market",
        ),
        (
            "place_order",
            pairs(&[
                ("market", "AAPL-USD.P"),
                ("side", "buy"),
                ("postOnly", "yes"),
            ]),
            "invalid Ondo boolean postOnly",
        ),
        (
            "place_order",
            body(order(serde_json::json!({"leverage": "2"}))),
            "unsupported Ondo body field: leverage",
        ),
        (
            "place_order",
            body(order(serde_json::json!({"market": " "}))),
            "market must be a nonempty string",
        ),
        (
            "place_order",
            body(order(serde_json::json!({"type": "stop"}))),
            "order type must be limit or market",
        ),
        (
            "place_order",
            body(order(serde_json::json!({"timeInForce": "FOK"}))),
            "timeInForce must be GTC or IOC",
        ),
        (
            "place_order",
            body(order(serde_json::json!({"reduceOnly": "true"}))),
            "reduceOnly must be boolean",
        ),
        (
            "place_order",
            body(order(serde_json::json!({"size": null}))),
            "requires price and size",
        ),
        (
            "place_order",
            body(order(serde_json::json!({"type": "market"}))),
            "invalid Ondo market order fields",
        ),
        (
            "place_batch_orders",
            body(serde_json::json!({"orders": [order(serde_json::json!({"side": "short"}))]})),
            "side must be buy or sell",
        ),
        (
            "place_twap_order",
            twap(twap_bad_bool),
            "reduceOnly must be boolean",
        ),
        (
            "place_twap_order",
            twap(twap_bad_int),
            "frequency must be an unsigned integer",
        ),
        (
            "place_twap_order",
            twap(twap_missing),
            "missing required Ondo body field: market",
        ),
        (
            "get_orders",
            pairs(&[("startTime", "x")]),
            "invalid Ondo integer startTime",
        ),
        (
            "get_orders",
            pairs(&[("startTime", "1"), ("endTime", "y")]),
            "invalid Ondo integer endTime",
        ),
        ("get_orders", pairs(&[("market", " ")]), "must not be empty"),
    ];
    for (method, params, expected) in cases {
        let params = params
            .into_iter()
            .map(|(key, value)| (key.to_string(), value))
            .collect();
        let error = client
            .private_request(method, params)
            .await
            .expect_err(expected)
            .to_string();
        assert!(error.contains(expected), "{method} {expected}: {error}");
    }
}
