use super::helpers::*;

#[test]
fn borrow_liquidation_estimate_uses_encoded_payload() {
    use std::io::{Read, Write};
    use std::net::TcpListener;
    use std::thread;

    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let base_url = format!("http://{}", listener.local_addr().expect("address"));
    let server = thread::spawn(move || {
        let (mut stream, _) = listener.accept().expect("accept");
        let mut buffer = [0u8; 4096];
        let size = stream.read(&mut buffer).expect("read");
        let request = String::from_utf8_lossy(&buffer[..size]).into_owned();
        let response = r#"{"liquidationPrice":"50000","markPrice":"60000"}"#;
        write!(
            stream,
            "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
            response.len(), response
        )
        .expect("write");
        request
    });
    let encoded = base64::engine::general_purpose::STANDARD
        .encode(br#"{"quantity":"1","side":"Borrow","symbol":"BTC"}"#);
    let client =
        BackpackClient::with_base_url(None, None, 5_000, Duration::from_secs(10), base_url)
            .expect("client");
    let result = crate::http::block_on(async move {
        client
            .public_request(
                "get_borrow_lend_liquidation_price",
                vec![
                    ("borrow".into(), encoded),
                    ("subaccountId".into(), "7".into()),
                ],
            )
            .await
    })
    .expect("estimate");
    assert_eq!(result.data["liquidationPrice"], "50000");
    let request = server.join().expect("server");
    assert!(request.starts_with("GET /api/v1/borrowLend/position/liquidationPrice?borrow="));
    assert!(request.contains("subaccountId=7 HTTP/1.1"));
}

#[test]
fn rfq_submit_omits_default_execution_mode() {
    let client = BackpackClient::public(5_000, Duration::from_secs(10)).expect("client");
    let error = crate::http::block_on(async move {
        client
            .submit_rfq("BTC-USDC-SPOT", "Bid")
            .quantity("0.5")
            .await
    })
    .expect_err("valid RFQ should reach credential validation");

    assert!(
        error
            .to_string()
            .contains("Signed Backpack requests require api_key and api_secret")
    );
}

#[test]
fn immediate_rfq_requires_price() {
    let client = BackpackClient::public(5_000, Duration::from_secs(10)).expect("client");
    let error = crate::http::block_on(async move {
        client
            .submit_rfq_with_execution_mode("BTC-USDC-SPOT", "Bid", "Immediate")
            .quantity("0.5")
            .await
    })
    .expect_err("Immediate RFQ without price must fail");

    assert!(error.to_string().contains("requires price"));
}

#[test]
fn rfq_actions_accept_client_id_identifiers() {
    let accept_client = BackpackClient::public(5_000, Duration::from_secs(10)).expect("client");
    let accept_error = crate::http::block_on(async move {
        accept_client
            .accept_rfq_quote_by_client_id(42, "quote-id")
            .await
    })
    .expect_err("valid clientId accept should reach credential validation");
    assert!(
        accept_error
            .to_string()
            .contains("Signed Backpack requests require api_key and api_secret")
    );

    let cancel_client = BackpackClient::public(5_000, Duration::from_secs(10)).expect("client");
    let cancel_error =
        crate::http::block_on(async move { cancel_client.cancel_rfq_by_client_id(42).await })
            .expect_err("valid clientId cancel should reach credential validation");
    assert!(
        cancel_error
            .to_string()
            .contains("Signed Backpack requests require api_key and api_secret")
    );
}
