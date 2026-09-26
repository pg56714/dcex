use super::msgpack::{OrderedValue, encode_msgpack};
use super::*;

mod endpoint_coverage;
mod websocket_coverage;

#[test]
fn signature_matches_python_vector() {
    let action = hex::decode("82a474797065a56f72646572a16101").expect("msgpack");
    assert_eq!(
        hyperliquid_signature(&action, 1_700_000_000_000, None, None, false, &[0x11; 32],)
            .expect("signature"),
        HyperliquidSignature {
            r: "0x193f5e88d621ca384beca6146a4c059b8716d5ad3da0404f6cd36f020fc87671".to_string(),
            s: "0x0c3767a2287482caef8a77be7b5c76eac08d9d8fb3080c53033e394bbb35d047".to_string(),
            v: 27,
        }
    );
}

#[test]
fn msgpack_encoder_matches_existing_order_vector() {
    let action = OrderedValue::Object(vec![
        (
            "type".to_string(),
            OrderedValue::String("order".to_string()),
        ),
        ("a".to_string(), OrderedValue::Uint(1)),
    ]);
    assert_eq!(
        hex::encode(encode_msgpack(&action)),
        "82a474797065a56f72646572a16101"
    );
}

#[test]
fn action_json_preserves_signed_field_order() {
    let action = OrderedValue::Object(vec![
        (
            "type".to_string(),
            OrderedValue::String("order".to_string()),
        ),
        (
            "orders".to_string(),
            OrderedValue::Array(vec![OrderedValue::Object(vec![
                ("a".to_string(), OrderedValue::Uint(0)),
                ("b".to_string(), OrderedValue::Bool(true)),
                ("p".to_string(), OrderedValue::String("100".to_string())),
            ])]),
        ),
        (
            "grouping".to_string(),
            OrderedValue::String("na".to_string()),
        ),
    ]);

    let json = serde_json::to_string(&action.to_json()).expect("json");
    let type_index = json.find("\"type\"").expect("type key");
    let orders_index = json.find("\"orders\"").expect("orders key");
    let grouping_index = json.find("\"grouping\"").expect("grouping key");

    assert!(type_index < orders_index);
    assert!(orders_index < grouping_index);
}

#[test]
fn wallet_signed_spot_perp_transfer_preserves_action_and_nonce() {
    use std::{
        io::{Read, Write},
        net::TcpListener,
        thread,
        time::Duration,
    };

    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let address = listener.local_addr().expect("address");
    let server = thread::spawn(move || {
        let (mut stream, _) = listener.accept().expect("accept");
        let mut buffer = [0u8; 4096];
        let size = stream.read(&mut buffer).expect("read");
        let mut request = String::from_utf8_lossy(&buffer[..size]).into_owned();
        let content_length = request
            .lines()
            .find_map(|line| {
                line.to_ascii_lowercase()
                    .strip_prefix("content-length: ")
                    .and_then(|value| value.trim().parse::<usize>().ok())
            })
            .unwrap_or(0);
        while request.split("\r\n\r\n").nth(1).map_or(0, str::len) < content_length {
            let size = stream.read(&mut buffer).expect("body");
            assert!(size > 0);
            request.push_str(&String::from_utf8_lossy(&buffer[..size]));
        }
        let body = r#"{"status":"ok","response":{"type":"default"}}"#;
        let response = format!(
            "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
            body.len(),
            body
        );
        stream.write_all(response.as_bytes()).expect("write");
        request
    });

    let client = HyperliquidClient::with_endpoint(
        false,
        None,
        None,
        Duration::from_secs(2),
        format!("http://{address}"),
    )
    .expect("client");
    let signature = serde_json::json!({
        "r": format!("0x{}", "1".repeat(64)),
        "s": format!("0x{}", "2".repeat(64)),
        "v": 27
    });
    let signature_json = signature.to_string();
    crate::http::block_on(async move {
        client
            .transfer_usdc_spot_perp("1", true, 1_700_000_000_000u64, &signature_json, "0xa4b1")
            .await
    })
    .expect("response");

    let request = server.join().expect("server");
    assert!(request.starts_with("POST /exchange HTTP/1.1"));
    let body: serde_json::Value =
        serde_json::from_str(request.split("\r\n\r\n").nth(1).expect("body")).expect("JSON");
    assert_eq!(body["action"]["type"], "usdClassTransfer");
    assert_eq!(body["action"]["amount"], "1");
    assert_eq!(body["action"]["toPerp"], true);
    assert_eq!(body["action"]["nonce"], 1_700_000_000_000u64);
    assert_eq!(body["nonce"], 1_700_000_000_000u64);
    assert_eq!(body["signature"], signature);
}

#[test]
fn spot_perp_transfer_rejects_missing_wallet_signature() {
    let client =
        HyperliquidClient::public(false, std::time::Duration::from_secs(1)).expect("client");
    let error = crate::http::block_on(async move {
        client
            .private_request(
                "transfer_usdc_spot_perp",
                vec![
                    ("amount".into(), "1".into()),
                    ("toPerp".into(), "true".into()),
                    ("nonce".into(), "1700000000000".into()),
                    ("signatureChainId".into(), "0xa4b1".into()),
                ],
            )
            .await
    })
    .expect_err("signature required");
    assert!(error.to_string().contains("signature"));
}
