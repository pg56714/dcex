pub(super) use std::time::Duration;

pub(super) use crate::http::{HttpMethod, RequestBody};

pub(super) use super::super::client::BitgetClient;
pub(super) use super::super::params::BitgetParams;

pub(super) fn private_client() -> BitgetClient {
    BitgetClient::new(
        Some("test_api_key_0000".to_string()),
        Some("test_api_secret_0000".to_string()),
        Some("test-passphrase".to_string()),
        Duration::from_secs(10),
    )
    .expect("client")
}
