pub(super) use std::io::{Read, Write};
pub(super) use std::net::TcpListener;
pub(super) use std::thread;
pub(super) use std::time::Duration;

pub(super) use crate::http::{HttpMethod, RequestBody};
pub(super) use crate::product_table::{MarketInfo, ProductTable};

pub(super) use super::super::endpoints::CONTRACT_DETAIL;
pub(super) use super::super::*;

pub(super) fn client() -> MexcClient {
    MexcClient::new(
        Some("api-key".to_string()),
        Some("secret".to_string()),
        Duration::from_secs(1),
    )
    .expect("client")
}
