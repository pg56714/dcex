use super::helpers::*;

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
            super::super::signing::rest_signature(
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
async fn websocket_deadman_sends_authenticated_timeout_message() {
    use futures_util::{SinkExt, StreamExt};
    use tokio_tungstenite::accept_async;
    use tokio_tungstenite::tungstenite::Message;

    let listener = tokio::net::TcpListener::bind("127.0.0.1:0")
        .await
        .expect("bind");
    let url = format!("ws://{}", listener.local_addr().expect("address"));
    let server = tokio::spawn(async move {
        let (stream, _) = listener.accept().await.expect("accept");
        let mut socket = accept_async(stream).await.expect("WebSocket");
        let login = socket.next().await.expect("login").expect("message");
        let login: serde_json::Value = serde_json::from_str(login.to_text().unwrap()).unwrap();
        assert_eq!(login["op"], "login");
        socket
            .send(Message::Text(r#"{"type":"loggedIn"}"#.into()))
            .await
            .expect("login acknowledgement");
        let subscription = socket.next().await.expect("subscription").expect("message");
        serde_json::from_str::<serde_json::Value>(subscription.to_text().unwrap())
            .expect("subscription JSON")
    });
    let mut client = super::super::websocket::OndoPrivateWebSocket::with_url(
        Some("key".into()),
        Some("ondoApiSecret_SECRET".into()),
        url,
        Duration::from_secs(10),
    )
    .expect("client");
    assert!(client.subscribe_cancel_all_orders_after(30).await.is_err());
    client.connect().await.expect("login");
    assert!(client.subscribe_cancel_all_orders_after(0).await.is_err());
    client
        .subscribe_cancel_all_orders_after(30)
        .await
        .expect("arm dead-man switch");
    let request = server.await.expect("server");
    assert_eq!(
        request,
        serde_json::json!({
            "op": "subscribe",
            "channel": "cancelAllOrdersAfterPerps",
            "timeout_seconds": 30,
        })
    );
}
