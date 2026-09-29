pub(super) use std::sync::{Arc, Mutex};
pub(super) use std::time::Duration;
pub(super) use std::{
    io::{ErrorKind, Read, Write},
    net::TcpListener,
    thread::{self, JoinHandle},
    time::Instant,
};

pub(super) use super::super::client::{BinanceClient, BinanceMarket};
pub(super) use super::super::endpoints::SPOT_BASE_URL;
pub(super) use super::super::params::{
    exchange_symbol_fallback, market_for_product_symbol_fallback, normalize_order_side,
};
pub(super) use super::super::signing::BinanceSigner;
pub(super) use crate::DcexError;
pub(super) use crate::exchange::RequestSigner;
pub(super) use crate::http::{HttpMethod, HttpRequest, block_on};
pub(super) use crate::product_table::ProductTable;

pub(super) fn recording_server() -> (String, JoinHandle<Option<String>>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    listener.set_nonblocking(true).expect("nonblocking");
    let address = listener.local_addr().expect("address");
    let handle = thread::spawn(move || {
        let deadline = Instant::now() + Duration::from_secs(10);
        loop {
            match listener.accept() {
                Ok((mut stream, _)) => {
                    stream.set_nonblocking(false).expect("blocking stream");
                    stream
                        .set_read_timeout(Some(Duration::from_secs(10)))
                        .expect("read timeout");
                    let mut buffer = [0u8; 4096];
                    let size = stream.read(&mut buffer).expect("read");
                    let request = String::from_utf8_lossy(&buffer[..size]).into_owned();
                    stream
                        .write_all(
                            b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\
Content-Length: 11\r\nConnection: close\r\n\r\n{\"ok\":true}",
                        )
                        .expect("write");
                    return request.lines().next().map(str::to_string);
                }
                Err(error) if error.kind() == ErrorKind::WouldBlock => {
                    if Instant::now() >= deadline {
                        return None;
                    }
                    thread::sleep(Duration::from_millis(10));
                }
                Err(error) => panic!("accept failed: {error}"),
            }
        }
    });
    (format!("http://{address}"), handle)
}

pub(super) fn recording_server_after_time_sync() -> (String, JoinHandle<Option<String>>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let address = listener.local_addr().expect("address");
    let handle = thread::spawn(move || {
        let mut signed_request_line = None;
        for request_index in 0..2 {
            let (mut stream, _) = listener.accept().expect("accept");
            stream
                .set_read_timeout(Some(Duration::from_secs(10)))
                .expect("read timeout");
            let mut buffer = [0u8; 4096];
            let size = stream.read(&mut buffer).expect("read");
            let request = String::from_utf8_lossy(&buffer[..size]).into_owned();
            let body = if request_index == 0 {
                r#"{"serverTime":1700000000000}"#
            } else {
                signed_request_line = request.lines().next().map(str::to_string);
                r#"{"ok":true}"#
            };
            let response = format!(
                "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\
                 Content-Length: {}\r\nConnection: close\r\n\r\n{}",
                body.len(),
                body
            );
            stream.write_all(response.as_bytes()).expect("write");
        }
        signed_request_line
    });
    (format!("http://{address}"), handle)
}
