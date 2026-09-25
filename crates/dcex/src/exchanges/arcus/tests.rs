use std::collections::BTreeMap;
use std::io::{Read, Write};
use std::net::TcpListener;
use std::thread;
use std::time::Duration;

use ed25519_dalek::{Signature, SigningKey};
use serde_json::json;

use super::client::{ArcusClient, ArcusSpotClient};
use super::params::{decimal_product_below, exact_units};
use super::signing::legacy_signing_message;
use crate::http::block_on;

#[test]
fn decimal_to_engine_units_is_exact() {
    assert_eq!(exact_units("0.001", "0.0001").unwrap(), 10);
    assert!(exact_units("0.0015", "0.001").is_err());
    assert!(decimal_product_below("100", "0.01", "5").unwrap());
}

#[test]
fn secret_must_match_public_key() {
    let secret = "00".repeat(32);
    assert!(ArcusClient::new(
        Some("ff".repeat(32)),
        Some(secret),
        None,
        0,
        true,
        Duration::from_secs(1)
    )
    .is_err());
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
fn spot_status_wrapper_sets_arcus_venue() {
    let client = ArcusSpotClient::new(None, false, Duration::from_secs(1)).unwrap();
    let request = client.get_status(format!("0x{}", "11".repeat(32)));
    assert_eq!(request.method_name, "get_status");
    assert!(request.params.contains(&("venue".into(), "arcus".into())));
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
