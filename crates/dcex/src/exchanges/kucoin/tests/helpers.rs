pub(super) use std::time::Duration;
pub(super) use std::{
    io::{Read, Write},
    net::TcpListener,
    thread,
};

pub(super) use crate::http::HttpMethod;

pub(super) use super::super::signing::request_signature;
pub(super) use super::super::*;

pub(super) fn server() -> (String, thread::JoinHandle<String>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let address = listener.local_addr().expect("address");
    let handle = thread::spawn(move || {
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
            let size = stream.read(&mut buffer).expect("read body");
            assert!(size > 0, "request ended before the declared body length");
            request.push_str(&String::from_utf8_lossy(&buffer[..size]));
        }
        stream
            .write_all(
                b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\
Content-Length: 46\r\nConnection: close\r\n\r\n{\"code\":\"200000\",\"data\":{\"bids\":[],\"asks\":[]}}",
            )
            .expect("write");
        request
    });
    (format!("http://{address}"), handle)
}
