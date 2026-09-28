//! Offline route coverage for every Bybit REST dispatch name.
//!
//! Each case sends one request through `public_request`/`private_request`
//! against a local single-shot HTTP server and asserts the HTTP verb, the
//! official V5 path, and whether the request carried a Bybit signature.

pub(super) use std::collections::BTreeSet;
pub(super) use std::io::{Read, Write};
pub(super) use std::net::{SocketAddr, TcpListener, TcpStream};
pub(super) use std::thread;
pub(super) use std::time::Duration;

pub(super) use super::super::client::BybitClient;

pub(super) use super::route_cases::*;

pub(super) fn single_shot_server() -> (SocketAddr, thread::JoinHandle<String>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let address = listener.local_addr().expect("address");
    let handle = thread::spawn(move || {
        let (mut stream, _) = listener.accept().expect("accept");
        let mut buffer = [0u8; 8192];
        let mut request = Vec::new();
        loop {
            let size = stream.read(&mut buffer).expect("read");
            if size == 0 {
                return String::new();
            }
            request.extend_from_slice(&buffer[..size]);
            let text = String::from_utf8_lossy(&request);
            if let Some((head, body)) = text.split_once("\r\n\r\n") {
                let content_length = head
                    .lines()
                    .find_map(|line| {
                        line.to_ascii_lowercase()
                            .strip_prefix("content-length:")
                            .and_then(|value| value.trim().parse::<usize>().ok())
                    })
                    .unwrap_or(0);
                if body.len() >= content_length {
                    break;
                }
            }
        }
        let body = r#"{"retCode":0,"retMsg":"OK","result":{}}"#;
        let response = format!(
            "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
            body.len(),
            body
        );
        stream.write_all(response.as_bytes()).expect("write");
        String::from_utf8_lossy(&request).into_owned()
    });
    (address, handle)
}

pub(super) fn client(base_url: String) -> BybitClient {
    BybitClient::with_base_url(
        Some("api-key".to_string()),
        Some("api-secret".to_string()),
        5_000,
        false,
        Duration::from_secs(5),
        base_url,
    )
    .expect("client")
}

pub(super) fn params(case: &RouteCase) -> Vec<(String, String)> {
    case.params
        .iter()
        .map(|(key, value)| ((*key).to_string(), (*value).to_string()))
        .collect()
}
