pub(super) use std::time::Duration;
pub(super) use std::time::{SystemTime, UNIX_EPOCH};
pub(super) use std::{
    io::{Read, Write},
    net::TcpListener,
    thread,
};

pub(super) use super::super::ExtendedClient;
pub(super) use super::super::client::signing_domain_for_base_url;
pub(super) use serde_json::json;

pub(super) async fn public_request(method: &str, params: Vec<(String, String)>) -> String {
    let (base_url, handle) = server();
    let client = ExtendedClient::with_base_url(
        None,
        Duration::from_secs(10),
        base_url,
        "dcex-test".to_string(),
    )
    .expect("client");

    client
        .public_request(method, params)
        .await
        .expect("response");
    handle.join().expect("server")
}

pub(super) async fn private_request(method: &str, params: Vec<(String, String)>) -> String {
    let (base_url, handle) = server();
    let client = ExtendedClient::with_base_url(
        Some("extended-key".to_string()),
        Duration::from_secs(10),
        base_url,
        "dcex-test".to_string(),
    )
    .expect("client");

    client
        .private_request(method, params)
        .await
        .expect("response");
    handle.join().expect("server")
}

pub(super) fn assert_request_line(request: impl AsRef<str>, expected: &str) {
    let first_line = request.as_ref().lines().next().expect("request line");
    assert_eq!(first_line, expected);
}

pub(super) fn server() -> (String, thread::JoinHandle<String>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let address = listener.local_addr().expect("address");
    let handle = thread::spawn(move || {
        let (mut stream, _) = listener.accept().expect("accept");
        let mut buffer = [0u8; 4096];
        let size = stream.read(&mut buffer).expect("read");
        let request = String::from_utf8_lossy(&buffer[..size]).into_owned();
        stream
            .write_all(
                b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\
Content-Length: 15\r\nConnection: close\r\n\r\n{\"status\":\"OK\"}",
            )
            .expect("write");
        request
    });
    (format!("http://{address}"), handle)
}
