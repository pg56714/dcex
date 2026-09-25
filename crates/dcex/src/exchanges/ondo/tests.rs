use std::collections::BTreeMap;
use std::time::Duration;

use super::OndoClient;
use crate::http::{HttpMethod, RequestBody};

#[test]
fn rejects_partial_api_credentials() {
    assert!(OndoClient::new(Some("key".to_string()), None, Duration::from_secs(5)).is_err());
}

#[test]
fn signed_request_uses_exact_encoded_path_and_raw_body() {
    let client = OndoClient::new(
        Some("key".to_string()),
        Some("ondoApiSecret_SECRET".to_string()),
        Duration::from_secs(5),
    )
    .expect("client");
    let body = br#"{"market":"AAPL-USD.P","side":"buy"}"#.to_vec();
    let request = client
        .build_request(
            HttpMethod::Post,
            "/v1/perps/orders",
            vec![("note".to_string(), "a b".to_string())],
            Some(body.clone()),
            true,
            BTreeMap::new(),
            "1741170600000",
        )
        .expect("request");
    assert_eq!(request.path, "/v1/perps/orders?note=a+b");
    assert_eq!(request.body, RequestBody::Raw(body.clone()));
    assert_eq!(
        request.headers.get("ONDO-KEY-ID").map(String::as_str),
        Some("key")
    );
    assert_eq!(
        request.headers.get("ONDO-TIMESTAMP").map(String::as_str),
        Some("1741170600000")
    );
    assert_eq!(
        request.headers.get("ONDO-SIGN").map(String::as_str),
        Some(
            super::signing::rest_signature(
                "ondoApiSecret_SECRET",
                "1741170600000",
                HttpMethod::Post,
                &request.path,
                &body,
            )
            .expect("signature")
            .as_str()
        ),
    );
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
    use super::websocket::{OndoPrivateWebSocket, OndoPublicWebSocket};

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

    for method in ["withdraw", "sandbox_withdrawal"] {
        let error = client
            .private_request(method, Vec::new())
            .await
            .expect_err("external withdrawal creation is outside project scope");
        assert!(
            error
                .to_string()
                .contains("unsupported Ondo private method")
        );
    }

    let error = client
        .private_request("get_withdrawal_status", Vec::new())
        .await
        .expect_err("one withdrawal identifier is required");
    assert!(error.to_string().contains("requires exactly one"));

    let error = client
        .private_request(
            "create_api_key",
            vec![
                ("name".to_string(), "test".to_string()),
                ("scopes".to_string(), r#"["admin"]"#.to_string()),
            ],
        )
        .await
        .expect_err("invalid API-key scope");
    assert!(error.to_string().contains("trade or transfer"));

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

    let error = client
        .private_request(
            "set_api_key_ip_whitelist",
            vec![
                ("apiKeyID".to_string(), "key-id".to_string()),
                ("ip".to_string(), "not-an-ip".to_string()),
            ],
        )
        .await
        .expect_err("invalid IP address");
    assert!(error.to_string().contains("IPv4"));
}
