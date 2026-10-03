use super::helpers::*;

#[test]
fn query_encoding_uses_uri_percent_encoding() {
    assert_eq!(
        encode_params(&[("greeting".to_string(), "hello world".to_string())]),
        "greeting=hello%20world"
    );
}

#[test]
fn product_table_asset_class_drives_xstock_orders() {
    let table = ProductTable::new(vec![MarketInfo {
        exchange: "kraken".to_string(),
        exchange_symbol: "AAPLxUSD".to_string(),
        product_symbol: "APPLE-USD-SPOT".to_string(),
        product_type: "spot".to_string(),
        exchange_type: "tokenized_asset".to_string(),
        price_precision: "0.01".to_string(),
        size_precision: "0.00000001".to_string(),
        min_size: "0.00000001".to_string(),
        base_currency: "AAPLx".to_string(),
        quote_currency: "USD".to_string(),
        min_notional: "0.5".to_string(),
        size_per_contract: "1".to_string(),
        ..MarketInfo::default()
    }]);
    let client = KrakenClient::public(Duration::from_secs(10))
        .expect("client")
        .with_product_table(table);

    assert_eq!(
        client
            .spot_asset_class("APPLE-USD-SPOT")
            .expect("asset class"),
        Some("tokenized_asset".to_string())
    );
}

#[test]
fn amend_and_edit_orders_use_documented_routes() {
    use std::io::{Read, Write};
    use std::net::TcpListener;
    use std::thread;

    for (method, params, path, spot) in [
        (
            "amend_spot_order",
            vec![
                ("txid".into(), "abc".into()),
                ("order_qty".into(), "1.25".into()),
            ],
            "/0/private/AmendOrder",
            true,
        ),
        (
            "edit_futures_order",
            vec![
                ("orderId".into(), "xyz".into()),
                ("limitPrice".into(), "7200".into()),
            ],
            "/derivatives/api/v3/editorder",
            false,
        ),
    ] {
        let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
        let url = format!("http://{}", listener.local_addr().expect("address"));
        let server = thread::spawn(move || {
            let (mut stream, _) = listener.accept().expect("accept");
            let mut buffer = [0u8; 4096];
            let size = stream.read(&mut buffer).expect("read");
            let request = String::from_utf8_lossy(&buffer[..size]).into_owned();
            let body = if spot {
                r#"{"error":[],"result":{}}"#
            } else {
                r#"{"result":"success"}"#
            };
            write!(stream,"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",body.len(),body).expect("write");
            request
        });
        let client = KrakenClient::with_base_urls(
            Some("spot-key".into()),
            Some(SECRET.into()),
            Some("futures-key".into()),
            Some(SECRET.into()),
            Duration::from_secs(10),
            url.clone(),
            url,
        )
        .expect("client");
        crate::http::block_on(async move { client.private_request(method, params).await })
            .expect("request");
        let request = server.join().expect("server");
        assert!(
            request.starts_with(&format!("POST {path} HTTP/1.1")),
            "{request}"
        );
        assert!(
            request
                .to_ascii_lowercase()
                .contains(if spot { "api-sign:" } else { "authent:" })
        );
    }
}
