use super::helpers::*;

#[test]
fn public_market_symbol_samples_resolve_ids_from_metadata() {
    let fixture: Value = serde_json::from_str(include_str!(
        "../../../../tests/fixtures/symbol_fallback.json"
    ))
    .expect("public fixture");
    let sample = fixture["cases"]
        .as_array()
        .unwrap()
        .iter()
        .find(|row| row["exchange"] == "arcus")
        .unwrap()["sample"]
        .clone();
    for selector in ["BTC-USD", "BTC-USD-SWAP", "1", "UNKNOWN-USD-SWAP"] {
        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        let base_url = format!("http://{}", listener.local_addr().unwrap());
        let body = json!({"markets": [sample.clone()]}).to_string();
        let server = thread::spawn(move || {
            let (mut stream, _) = listener.accept().unwrap();
            stream
                .set_read_timeout(Some(Duration::from_secs(2)))
                .unwrap();
            let mut bytes = [0; 2048];
            let size = stream.read(&mut bytes).unwrap();
            assert!(String::from_utf8_lossy(&bytes[..size]).starts_with("GET /v1/markets "));
            write!(stream, "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{body}", body.len()).unwrap();
        });
        let client = ArcusClient::public(Duration::from_secs(2))
            .unwrap()
            .with_base_url(base_url)
            .unwrap();
        let result = block_on(async move { client.market_info(selector).await });
        server.join().unwrap();
        if selector.starts_with("UNKNOWN") {
            assert!(result.is_err());
        } else {
            assert_eq!(result.unwrap()["marketId"], sample["marketId"]);
        }
    }
}

#[test]
fn spot_status_wrapper_sets_arcus_venue() {
    let client = ArcusSpotClient::new(None, false, Duration::from_secs(10)).unwrap();
    let request = client.get_status(format!("0x{}", "11".repeat(32)));
    assert_eq!(request.method_name, "get_status");
    assert!(request.params.contains(&("venue".into(), "arcus".into())));
}
