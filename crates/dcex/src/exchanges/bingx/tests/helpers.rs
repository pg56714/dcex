pub(super) use crate::exchange::RequestSigner;
pub(super) use crate::http::{HttpMethod, HttpRequest, block_on};
pub(super) use std::io::{Read, Write};
pub(super) use std::net::TcpListener;
pub(super) use std::thread;
pub(super) use std::time::Duration;

pub(super) use super::super::client::BingxClient;
pub(super) use super::super::endpoints::BASE_URL;
pub(super) use super::super::signing::BingxSigner;

pub(super) fn recording_server() -> (String, thread::JoinHandle<String>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let url = format!("http://{}", listener.local_addr().expect("address"));
    let handle = thread::spawn(move || {
        let (mut stream, _) = listener.accept().expect("accept");
        stream
            .set_read_timeout(Some(Duration::from_secs(2)))
            .expect("timeout");
        let mut bytes = [0u8; 4096];
        let size = stream.read(&mut bytes).expect("request");
        stream.write_all(
            b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: 20\r\nConnection: close\r\n\r\n{\"code\":0,\"data\":{}}",
        ).expect("response");
        String::from_utf8_lossy(&bytes[..size])
            .lines()
            .next()
            .expect("request line")
            .to_string()
    });
    (url, handle)
}
