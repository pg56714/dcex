use std::sync::Arc;
use std::time::Duration;

use serde_json::{Map, Value};
use tokio::sync::Mutex;

use super::endpoints::{BASE_URL, TIME_ENDPOINT};
use super::params::{
    category_for_product_symbol_fallback, exchange_symbol_fallback, is_canonical_product_symbol,
};
use super::signing::{encode_params, extract_server_time_ms, validate_response};
use crate::crypto::hmac_sha256_hex;
use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

#[derive(Clone)]
pub struct BybitClient {
    transport: AsyncHttpClient,
    base_url: String,
    api_key: Option<String>,
    api_secret: Option<String>,
    recv_window: u64,
    sync_server_time: bool,
    timestamp_offset_ms: Arc<Mutex<Option<i64>>>,
    product_table: Option<Arc<ProductTable>>,
}

impl BybitClient {
    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        recv_window: u64,
        sync_server_time: bool,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_url(
            api_key,
            api_secret,
            recv_window,
            sync_server_time,
            timeout,
            BASE_URL.to_string(),
        )
    }

    pub fn public(recv_window: u64, sync_server_time: bool, timeout: Duration) -> Result<Self> {
        Self::new(None, None, recv_window, sync_server_time, timeout)
    }

    pub fn with_base_url(
        api_key: Option<String>,
        api_secret: Option<String>,
        recv_window: u64,
        sync_server_time: bool,
        timeout: Duration,
        base_url: String,
    ) -> Result<Self> {
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            base_url,
            api_key,
            api_secret,
            recv_window,
            sync_server_time,
            timestamp_offset_ms: Arc::new(Mutex::new(None)),
            product_table: None,
        })
    }

    pub fn with_product_table(mut self, product_table: ProductTable) -> Self {
        self.product_table = Some(Arc::new(product_table));
        self
    }

    pub fn set_product_table(&mut self, product_table: ProductTable) {
        self.product_table = Some(Arc::new(product_table));
    }

    pub async fn request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<ValidatedResponse> {
        let response = self.request_raw(method, path, params, body, signed).await?;
        let data = validate_response(&response)?;
        Ok(ValidatedResponse {
            status: response.status,
            headers: response.headers,
            data,
        })
    }

    pub async fn request_raw(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let timestamp = self.timestamp(signed).await?;
        let request = self.build_request(method, path, params, body, signed, timestamp)?;
        self.transport.execute(request).await
    }

    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move { client.request_raw(method, path, params, body, signed).await })
    }
}

impl BybitClient {
    pub(super) async fn get_request(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Get, path, params, None, true)
            .await
    }

    pub(super) async fn post_request(
        &self,
        path: &str,
        body: Map<String, Value>,
    ) -> Result<ValidatedResponse> {
        let body = serde_json::to_vec(&Value::Object(body))
            .map_err(|error| DcexError::Decode(error.to_string()))?;
        self.request(HttpMethod::Post, path, Vec::new(), Some(body), true)
            .await
    }

    pub(super) fn exchange_symbol(&self, product_symbol: &str) -> Result<String> {
        if is_canonical_product_symbol(product_symbol) {
            if let Some(table) = &self.product_table {
                return table.get_exchange_symbol("bybit", product_symbol);
            }
        }
        Ok(exchange_symbol_fallback(product_symbol))
    }

    pub(super) fn category_for_product_symbol(
        &self,
        product_symbol: &str,
        default_category: &str,
    ) -> Result<String> {
        if is_canonical_product_symbol(product_symbol) {
            if let Some(table) = &self.product_table {
                return table.get_exchange_type("bybit", Some(product_symbol), None);
            }
        }
        Ok(category_for_product_symbol_fallback(
            product_symbol,
            default_category,
        ))
    }

    pub(super) fn push_symbol_category(
        &self,
        params: &mut Vec<(String, String)>,
        product_symbol: &str,
        include_category: bool,
    ) -> Result<()> {
        params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        if include_category {
            params.push((
                "category".to_string(),
                self.category_for_product_symbol(product_symbol, "linear")?,
            ));
        }
        Ok(())
    }

    pub(super) fn insert_symbol_category(
        &self,
        body: &mut Map<String, Value>,
        product_symbol: &str,
    ) -> Result<()> {
        body.insert(
            "category".to_string(),
            Value::String(self.category_for_product_symbol(product_symbol, "linear")?),
        );
        body.insert(
            "symbol".to_string(),
            Value::String(self.exchange_symbol(product_symbol)?),
        );
        Ok(())
    }

    async fn timestamp(&self, signed: bool) -> Result<u64> {
        if !signed || !self.sync_server_time {
            return unix_timestamp_ms();
        }
        let mut offset = self.timestamp_offset_ms.lock().await;
        if offset.is_none() {
            let local_start = unix_timestamp_ms()?;
            let response = self
                .transport
                .execute(HttpRequest::new(
                    HttpMethod::Get,
                    &self.base_url,
                    TIME_ENDPOINT,
                ))
                .await;
            let local_end = unix_timestamp_ms()?;
            let calculated = response
                .ok()
                .and_then(|response| response.json().ok())
                .and_then(|data| extract_server_time_ms(&data))
                .map(|server_time| server_time as i64 - ((local_start + local_end) / 2) as i64)
                .unwrap_or(0);
            *offset = Some(calculated);
        }
        let local = unix_timestamp_ms()? as i64;
        let adjusted = local + offset.unwrap_or(0);
        u64::try_from(adjusted).map_err(|error| DcexError::Runtime(error.to_string()))
    }

    fn build_request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        mut params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
        timestamp: u64,
    ) -> Result<HttpRequest> {
        let path = path.into();
        params.sort_by(|left, right| left.0.cmp(&right.0));
        let payload = if matches!(method, HttpMethod::Get) {
            encode_params(&params)
        } else {
            String::from_utf8_lossy(body.as_deref().unwrap_or_default()).into_owned()
        };
        let mut request = HttpRequest::new(method, &self.base_url, path)
            .header("Content-Type", "application/json");
        if matches!(method, HttpMethod::Get) {
            request.query = params;
        } else {
            request.body = body.map(RequestBody::Raw).unwrap_or_default();
        }
        if signed {
            let (api_key, api_secret) = self.credentials()?;
            let signature_payload = format!("{timestamp}{api_key}{}{payload}", self.recv_window);
            let signature = hmac_sha256_hex(api_secret.as_bytes(), signature_payload.as_bytes())?;
            request
                .headers
                .insert("X-BAPI-API-KEY".to_string(), api_key.to_string());
            request.headers.insert("X-BAPI-SIGN".to_string(), signature);
            request
                .headers
                .insert("X-BAPI-SIGN-TYPE".to_string(), "2".to_string());
            request
                .headers
                .insert("X-BAPI-TIMESTAMP".to_string(), timestamp.to_string());
            request.headers.insert(
                "X-BAPI-RECV-WINDOW".to_string(),
                self.recv_window.to_string(),
            );
        }
        Ok(request)
    }

    fn credentials(&self) -> Result<(&str, &str)> {
        match (&self.api_key, &self.api_secret) {
            (Some(api_key), Some(api_secret)) => Ok((api_key, api_secret)),
            _ => Err(DcexError::InvalidInput(
                "Signed request requires API Key and Secret.".to_string(),
            )),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::super::signing::extract_server_time_ms;
    use super::*;

    #[test]
    fn auth_matches_python_vector() {
        let client = BybitClient::new(
            Some("test_api_key_0000".to_string()),
            Some("test_api_secret_0000".to_string()),
            5_000,
            false,
            Duration::from_secs(1),
        )
        .expect("client");
        let request = client
            .build_request(
                HttpMethod::Get,
                "/v5/order/realtime",
                vec![
                    ("symbol".to_string(), "BTCUSDT".to_string()),
                    ("category".to_string(), "linear".to_string()),
                ],
                None,
                true,
                1_700_000_000_000,
            )
            .expect("request");

        assert_eq!(
            request.headers.get("X-BAPI-SIGN").map(String::as_str),
            Some("ef8980e55f6ba1d32ab182ddbdad9c8182df87123b035c969965698c9dcd8713")
        );
    }

    #[test]
    fn auth_signs_encoded_get_query_payload() {
        let client = BybitClient::new(
            Some("test_api_key_0000".to_string()),
            Some("test_api_secret_0000".to_string()),
            5_000,
            false,
            Duration::from_secs(1),
        )
        .expect("client");
        let request = client
            .build_request(
                HttpMethod::Get,
                "/v5/account/withdrawal",
                vec![("coinName".to_string(), "BTC,ETH".to_string())],
                None,
                true,
                1_700_000_000_000,
            )
            .expect("request");

        assert_eq!(
            request.headers.get("X-BAPI-SIGN").map(String::as_str),
            Some("debcb4f8de9897ee9b0f8ff0c4f6c4ee2e98b96ee3e418617f23da70801fe587")
        );
    }

    #[test]
    fn extracts_supported_server_time_shapes() {
        assert_eq!(
            extract_server_time_ms(&serde_json::json!({"time": "1700000000000"})),
            Some(1_700_000_000_000)
        );
        assert_eq!(
            extract_server_time_ms(
                &serde_json::json!({"result": {"timeNano": "1700000000000000000"}})
            ),
            Some(1_700_000_000_000)
        );
    }
}
