pub(super) use std::{
    io::{ErrorKind, Read, Write},
    net::TcpListener,
    thread::{self, JoinHandle},
    time::{Duration, Instant},
};

pub(super) use serde_json::{Value, json};

pub(super) use crate::http::HttpMethod;
pub(super) use crate::product_table::{MarketInfo, ProductTable};

pub(super) use super::super::{AsterClient, AsterMarket, sign_message};
pub(super) use crate::DcexError;
pub(super) use crate::exchanges::aster::params::AsterParams;

pub(super) fn recording_server() -> (String, JoinHandle<Option<String>>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    listener.set_nonblocking(true).expect("nonblocking");
    let address = listener.local_addr().expect("address");
    let handle = thread::spawn(move || {
        let deadline = Instant::now() + Duration::from_secs(2);
        loop {
            match listener.accept() {
                Ok((mut stream, _)) => {
                    stream.set_nonblocking(false).expect("blocking stream");
                    stream
                        .set_read_timeout(Some(Duration::from_secs(2)))
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
