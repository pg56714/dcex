use super::helpers::*;

#[test]
fn secret_must_match_public_key() {
    let secret = "00".repeat(32);
    assert!(
        ArcusClient::new(
            Some("ff".repeat(32)),
            Some(secret),
            None,
            0,
            true,
            Duration::from_secs(1)
        )
        .is_err()
    );
}

#[test]
fn legacy_signing_message_sorts_json_keys() {
    let mut body = BTreeMap::new();
    body.insert("marketId".to_string(), json!(7));
    body.insert("address".to_string(), json!("0xabc"));
    body.insert("accountIndex".to_string(), json!(0));
    assert_eq!(
        legacy_signing_message(123, "cancelAllOrders", &body).unwrap(),
        br#"123cancelAllOrders{"accountIndex":0,"address":"0xabc","marketId":7}"#
    );
}

#[test]
fn modify_order_uses_official_body_and_typed_signature() {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let base_url = format!("http://{}", listener.local_addr().expect("address"));
    let server = thread::spawn(move || {
        let mut captured = String::new();
        for step in 0..2 {
            let (mut stream, _) = listener.accept().expect("accept");
            stream
                .set_read_timeout(Some(Duration::from_secs(2)))
                .expect("timeout");
            let mut raw = Vec::new();
            let header_end = loop {
                let mut chunk = [0u8; 4096];
                let size = stream.read(&mut chunk).expect("read");
                assert!(size > 0, "unexpected EOF");
                raw.extend_from_slice(&chunk[..size]);
                if let Some(end) = raw.windows(4).position(|window| window == b"\r\n\r\n") {
                    break end + 4;
                }
            };
            let headers = String::from_utf8_lossy(&raw[..header_end]);
            let content_length = headers
                .lines()
                .find_map(|line| {
                    line.to_ascii_lowercase()
                        .strip_prefix("content-length: ")
                        .and_then(|value| value.trim().parse::<usize>().ok())
                })
                .unwrap_or(0);
            while raw.len() < header_end + content_length {
                let mut chunk = [0u8; 4096];
                let size = stream.read(&mut chunk).expect("body");
                assert!(size > 0, "unexpected body EOF");
                raw.extend_from_slice(&chunk[..size]);
            }
            if step == 1 {
                captured = String::from_utf8(raw).expect("UTF-8 request");
            }
            let body = if step == 0 {
                r#"{"markets":[{"marketId":7,"marketDisplayName":"BTC-USD","tickSize":"0.1","stepSize":"0.001","minOrderSize":"0.001","maxOrderSize":"100"}]}"#
            } else {
                r#"{"status":"ACK"}"#
            };
            write!(
                stream,
                "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                body.len(), body
            ).expect("response");
        }
        captured
    });
    let key = SigningKey::from_bytes(&[1u8; 32]);
    let address = format!("0x{}", "11".repeat(20));
    let client = ArcusClient::new(
        Some(hex::encode(key.verifying_key().to_bytes())),
        Some(hex::encode(key.to_bytes())),
        Some(address.clone()),
        0,
        true,
        Duration::from_secs(2),
    )
    .expect("client")
    .with_base_url(base_url)
    .expect("base URL");
    let good_til_time = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .expect("time")
        .as_micros() as u64
        + 40 * 86_400 * 1_000_000;
    block_on(async move {
        client
            .private_request(
                "modify_order",
                vec![
                    ("product_symbol".into(), "BTC-USD".into()),
                    ("side".into(), "BUY".into()),
                    ("price".into(), "50000".into()),
                    ("quantity".into(), "0.01".into()),
                    ("good_til_time".into(), good_til_time.to_string()),
                    ("time_in_force".into(), "GTT".into()),
                    ("reduce_only".into(), "false".into()),
                    ("order_id".into(), "abc123".into()),
                ],
            )
            .await
    })
    .expect("modify request");
    let captured = server.join().expect("server");
    assert!(
        captured.starts_with("POST /v1/modifyOrder?address="),
        "{captured}"
    );
    let header_end = captured.find("\r\n\r\n").expect("headers");
    let headers = &captured[..header_end];
    let body: serde_json::Value = serde_json::from_str(&captured[header_end + 4..]).expect("body");
    assert_eq!(body["side"], "BUY");
    assert_eq!(body["orderId"], "abc123");
    assert_eq!(body["goodTilTime"], good_til_time.to_string());
    assert_eq!(body["reduceOnly"], false);
    assert!(body.get("orderType").is_none());
    let timestamp: u64 = headers
        .lines()
        .find_map(|line| {
            line.to_ascii_lowercase()
                .strip_prefix("x-timestamp: ")
                .and_then(|value| value.trim().parse().ok())
        })
        .expect("timestamp");
    let signature = headers
        .lines()
        .find_map(|line| {
            line.to_ascii_lowercase()
                .strip_prefix("x-signature: ")
                .map(str::to_string)
        })
        .expect("signature");
    let bytes: [u8; 64] = hex::decode(signature.trim())
        .expect("signature hex")
        .try_into()
        .expect("signature length");
    let mut canonical = BTreeMap::new();
    canonical.insert("ad", json!(address));
    canonical.insert("ai", json!(0));
    canonical.insert("ct", json!(timestamp));
    canonical.insert("g", json!(good_til_time * 1000));
    canonical.insert("id", json!("abc123"));
    canonical.insert("m", json!(7));
    canonical.insert("op", json!(3));
    canonical.insert("p", json!(500000));
    canonical.insert("q", json!(10));
    canonical.insert("r", json!(0));
    canonical.insert("s", json!(0));
    canonical.insert("t", json!(0));
    canonical.insert("v", json!(1));
    key.verifying_key()
        .verify_strict(
            &serde_json::to_vec(&canonical).expect("canonical"),
            &Signature::from_bytes(&bytes),
        )
        .expect("typed signature");
}

#[test]
fn risk_controls_use_official_paths_and_legacy_signatures() {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let base_url = format!("http://{}", listener.local_addr().expect("address"));
    let server = thread::spawn(move || {
        let mut requests = Vec::new();
        for _ in 0..4 {
            let (mut stream, _) = listener.accept().expect("accept");
            stream
                .set_read_timeout(Some(Duration::from_secs(2)))
                .expect("timeout");
            let mut raw = Vec::new();
            let header_end = loop {
                let mut chunk = [0u8; 4096];
                let size = stream.read(&mut chunk).expect("read");
                assert!(size > 0, "unexpected EOF");
                raw.extend_from_slice(&chunk[..size]);
                if let Some(end) = raw.windows(4).position(|window| window == b"\r\n\r\n") {
                    break end + 4;
                }
            };
            let headers = String::from_utf8_lossy(&raw[..header_end]);
            let content_length = headers
                .lines()
                .find_map(|line| {
                    line.to_ascii_lowercase()
                        .strip_prefix("content-length: ")
                        .and_then(|value| value.trim().parse::<usize>().ok())
                })
                .unwrap_or(0);
            while raw.len() < header_end + content_length {
                let mut chunk = [0u8; 4096];
                let size = stream.read(&mut chunk).expect("body");
                assert!(size > 0, "unexpected body EOF");
                raw.extend_from_slice(&chunk[..size]);
            }
            let request = String::from_utf8(raw).expect("UTF-8 request");
            let response = if request.starts_with("GET ") {
                r#"{"markets":[{"marketId":7,"marketDisplayName":"BTC-USD"}]}"#
            } else {
                r#"{"status":"ACK"}"#
            };
            write!(
                stream,
                "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                response.len(), response
            )
            .expect("response");
            requests.push(request);
        }
        requests
    });
    let key = SigningKey::from_bytes(&[2u8; 32]);
    let address = format!("0x{}", "22".repeat(20));
    let client = ArcusClient::new(
        Some(hex::encode(key.verifying_key().to_bytes())),
        Some(hex::encode(key.to_bytes())),
        Some(address.clone()),
        0,
        true,
        Duration::from_secs(2),
    )
    .expect("client")
    .with_base_url(base_url)
    .expect("base URL");
    let deadline = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .expect("time")
        .as_micros() as u64
        + 60_000_000;
    block_on(async move {
        client
            .private_request(
                "schedule_cancel",
                vec![("time".into(), deadline.to_string())],
            )
            .await
            .expect("arm");
        client
            .private_request("disarm_scheduled_cancel", vec![])
            .await
            .expect("disarm");
        client
            .private_request(
                "adjust_isolated_margin",
                vec![
                    ("product_symbol".into(), "BTC-USD".into()),
                    ("amount".into(), "-40.5".into()),
                ],
            )
            .await
            .expect("margin");
        Ok(())
    })
    .expect("risk requests");
    let requests = server.join().expect("server");
    let posted: Vec<_> = requests
        .iter()
        .filter(|request| request.starts_with("POST "))
        .collect();
    assert_eq!(posted.len(), 3);
    for (request, path, action) in [
        (posted[0], "/v1/scheduleCancel", "scheduleCancel"),
        (posted[1], "/v1/scheduleCancel", "scheduleCancel"),
        (
            posted[2],
            "/v1/adjustIsolatedMargin",
            "adjustIsolatedMargin",
        ),
    ] {
        assert!(request.starts_with(&format!("POST {path}?address=")));
        let header_end = request.find("\r\n\r\n").expect("headers");
        let headers = &request[..header_end];
        let body: BTreeMap<String, Value> =
            serde_json::from_str(&request[header_end + 4..]).expect("body");
        assert_eq!(body["address"], address);
        assert_eq!(body["accountIndex"], 0);
        let timestamp: u64 = headers
            .lines()
            .find_map(|line| {
                line.to_ascii_lowercase()
                    .strip_prefix("x-timestamp: ")
                    .and_then(|value| value.trim().parse().ok())
            })
            .expect("timestamp");
        let signature = headers
            .lines()
            .find_map(|line| {
                line.to_ascii_lowercase()
                    .strip_prefix("x-signature: ")
                    .map(str::to_string)
            })
            .expect("signature");
        let bytes: [u8; 64] = hex::decode(signature.trim())
            .expect("signature hex")
            .try_into()
            .expect("signature length");
        key.verifying_key()
            .verify_strict(
                &legacy_signing_message(timestamp, action, &body).expect("message"),
                &Signature::from_bytes(&bytes),
            )
            .expect("valid signature");
    }
    let arm_body: Value =
        serde_json::from_str(posted[0].split("\r\n\r\n").nth(1).unwrap()).unwrap();
    let disarm_body: Value =
        serde_json::from_str(posted[1].split("\r\n\r\n").nth(1).unwrap()).unwrap();
    let margin_body: Value =
        serde_json::from_str(posted[2].split("\r\n\r\n").nth(1).unwrap()).unwrap();
    assert_eq!(arm_body["time"], deadline);
    assert!(disarm_body.get("time").is_none());
    assert_eq!(margin_body["marketId"], 7);
    assert_eq!(margin_body["amount"], "-40.5");
}

#[test]
fn batch_cancel_signs_each_element_with_shared_timestamp() {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let base_url = format!("http://{}", listener.local_addr().expect("address"));
    let server = thread::spawn(move || {
        let mut posted = None;
        for _ in 0..3 {
            let (mut stream, _) = listener.accept().expect("accept");
            stream
                .set_read_timeout(Some(Duration::from_secs(2)))
                .expect("timeout");
            let mut raw = Vec::new();
            let header_end = loop {
                let mut chunk = [0u8; 4096];
                let size = stream.read(&mut chunk).expect("read");
                assert!(size > 0, "unexpected EOF");
                raw.extend_from_slice(&chunk[..size]);
                if let Some(end) = raw.windows(4).position(|window| window == b"\r\n\r\n") {
                    break end + 4;
                }
            };
            let headers = String::from_utf8_lossy(&raw[..header_end]);
            let content_length = headers
                .lines()
                .find_map(|line| {
                    line.to_ascii_lowercase()
                        .strip_prefix("content-length: ")
                        .and_then(|value| value.trim().parse::<usize>().ok())
                })
                .unwrap_or(0);
            while raw.len() < header_end + content_length {
                let mut chunk = [0u8; 4096];
                let size = stream.read(&mut chunk).expect("body");
                assert!(size > 0, "unexpected body EOF");
                raw.extend_from_slice(&chunk[..size]);
            }
            let request = String::from_utf8(raw).expect("request");
            let response = if request.starts_with("GET ") {
                r#"{"markets":[{"marketId":7,"marketDisplayName":"BTC-USD"}]}"#
            } else {
                posted = Some(request);
                r#"{"responses":[]}"#
            };
            write!(
                stream,
                "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
                response.len(), response
            )
            .expect("response");
        }
        posted.expect("batch POST")
    });
    let key = SigningKey::from_bytes(&[3u8; 32]);
    let address = format!("0x{}", "33".repeat(20));
    let client = ArcusClient::new(
        Some(hex::encode(key.verifying_key().to_bytes())),
        Some(hex::encode(key.to_bytes())),
        Some(address.clone()),
        0,
        true,
        Duration::from_secs(2),
    )
    .expect("client")
    .with_base_url(base_url)
    .expect("base URL");
    block_on(async move {
        client
            .private_request(
                "batch_cancel_orders",
                vec![(
                    "cancels".into(),
                    r#"[{"product_symbol":"BTC-USD","order_id":"one"},{"product_symbol":"BTC-USD","order_id":"two"}]"#.into(),
                )],
            )
            .await
    })
    .expect("batch cancel");
    let request = server.join().expect("server");
    assert!(request.starts_with("POST /v1/batchCancelOrders?address="));
    let (headers, body) = request.split_once("\r\n\r\n").expect("body");
    let body: Value = serde_json::from_str(body).expect("JSON");
    let cancels = body["cancels"].as_array().expect("cancels");
    assert_eq!(cancels.len(), 2);
    let timestamp: u64 = headers
        .lines()
        .find_map(|line| {
            line.to_ascii_lowercase()
                .strip_prefix("x-timestamp: ")
                .and_then(|value| value.trim().parse().ok())
        })
        .expect("timestamp");
    let header_signature = headers
        .lines()
        .find_map(|line| {
            line.to_ascii_lowercase()
                .strip_prefix("x-signature: ")
                .map(str::to_string)
        })
        .expect("header signature");
    assert_eq!(cancels[0]["signature"], header_signature.trim());
    for (index, item) in cancels.iter().enumerate() {
        assert_eq!(item["orderId"], ["one", "two"][index]);
        assert_eq!(item["timestamp"], timestamp);
        let signature: [u8; 64] = hex::decode(item["signature"].as_str().unwrap())
            .expect("hex")
            .try_into()
            .expect("signature length");
        let mut canonical = BTreeMap::new();
        canonical.insert("ad", json!(address));
        canonical.insert("ai", json!(0));
        canonical.insert("ct", json!(timestamp));
        canonical.insert("id", json!(["one", "two"][index]));
        canonical.insert("m", json!(7));
        canonical.insert("op", json!(2));
        canonical.insert("v", json!(1));
        key.verifying_key()
            .verify_strict(
                &serde_json::to_vec(&canonical).expect("canonical"),
                &Signature::from_bytes(&signature),
            )
            .expect("element signature");
    }
}
