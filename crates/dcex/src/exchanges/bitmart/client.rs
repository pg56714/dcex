use std::sync::Arc;
use std::time::Duration;

use serde_json::Value;

use crate::crypto::hmac_sha256_hex;
use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

use super::endpoints::{FUTURES_BASE_URL, SPOT_BASE_URL};
use super::params::{exchange_symbol_fallback, is_canonical_product_symbol};
use super::signing::validate_response;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum BitmartMarket {
    Futures,
    Spot,
}

impl BitmartMarket {
    pub fn from_path(path: &str) -> Result<Self> {
        if path.starts_with("/contract/")
            || path == super::endpoints::FUTURES_TRANSFER
            || path == super::endpoints::FUTURES_TRANSFER_LIST
        {
            return Ok(Self::Futures);
        }
        if path.starts_with("/spot/") || path.starts_with("/account/") {
            return Ok(Self::Spot);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported BitMart API path: {path}"
        )))
    }
}

#[derive(Clone)]
pub struct BitmartClient {
    transport: AsyncHttpClient,
    spot_base_url: String,
    futures_base_url: String,
    api_key: Option<String>,
    api_secret: Option<String>,
    memo: Option<String>,
    product_table: Option<Arc<ProductTable>>,
}

impl BitmartClient {
    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        memo: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_urls(
            api_key,
            api_secret,
            memo,
            timeout,
            SPOT_BASE_URL.to_string(),
            FUTURES_BASE_URL.to_string(),
        )
    }

    pub fn public(timeout: Duration) -> Result<Self> {
        Self::new(None, None, None, timeout)
    }

    pub fn with_base_urls(
        api_key: Option<String>,
        api_secret: Option<String>,
        memo: Option<String>,
        timeout: Duration,
        spot_base_url: String,
        futures_base_url: String,
    ) -> Result<Self> {
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            spot_base_url,
            futures_base_url,
            api_key,
            api_secret,
            memo,
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
        market: BitmartMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<ValidatedResponse> {
        let response = self
            .request_raw(method, market, path, params, body, signed)
            .await?;
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
        market: BitmartMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let timestamp = unix_timestamp_ms()?;
        let request = self.build_request(method, market, path, params, body, signed, timestamp)?;
        self.transport.execute(request).await
    }

    pub async fn request_raw_auto(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let path = path.into();
        let market = BitmartMarket::from_path(&path)?;
        self.request_raw(method, market, path, params, body, signed)
            .await
    }

    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        market: BitmartMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move {
            client
                .request_raw(method, market, path, params, body, signed)
                .await
        })
    }

    pub fn request_raw_auto_blocking(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move {
            client
                .request_raw_auto(method, path, params, body, signed)
                .await
        })
    }

    pub(super) async fn public_get(
        &self,
        market: BitmartMarket,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Get, market, path, params, None, false)
            .await
    }

    pub(super) async fn get_private(
        &self,
        market: BitmartMarket,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Get, market, path, params, None, true)
            .await
    }

    pub(super) async fn post_private(
        &self,
        market: BitmartMarket,
        path: &str,
        body: Value,
    ) -> Result<ValidatedResponse> {
        let body =
            serde_json::to_vec(&body).map_err(|error| DcexError::Decode(error.to_string()))?;
        self.request(HttpMethod::Post, market, path, Vec::new(), Some(body), true)
            .await
    }

    pub(super) fn build_request(
        &self,
        method: HttpMethod,
        market: BitmartMarket,
        path: impl Into<String>,
        mut params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
        timestamp: u64,
    ) -> Result<HttpRequest> {
        let base_url = match market {
            BitmartMarket::Futures => &self.futures_base_url,
            BitmartMarket::Spot => &self.spot_base_url,
        };
        params.sort_by(|left, right| left.0.cmp(&right.0));
        let path = path.into();
        let path = if matches!(method, HttpMethod::Get) && !params.is_empty() {
            format!(
                "{path}?{}",
                params
                    .iter()
                    .map(|(key, value)| format!("{key}={value}"))
                    .collect::<Vec<_>>()
                    .join("&")
            )
        } else {
            path
        };
        let mut request =
            HttpRequest::new(method, base_url, path).header("Content-Type", "application/json");
        if matches!(method, HttpMethod::Post) {
            request.body = body.clone().map(RequestBody::Raw).unwrap_or_default();
        }
        if signed {
            let (api_key, api_secret, memo) = self.credentials()?;
            let body = String::from_utf8_lossy(body.as_deref().unwrap_or_default());
            let payload = format!("{timestamp}#{memo}#{body}");
            let signature = hmac_sha256_hex(api_secret.as_bytes(), payload.as_bytes())?;
            request
                .headers
                .insert("X-BM-KEY".to_string(), api_key.to_string());
            request.headers.insert("X-BM-SIGN".to_string(), signature);
            request
                .headers
                .insert("X-BM-TIMESTAMP".to_string(), timestamp.to_string());
            request
                .headers
                .insert("X-BM-MEMO".to_string(), memo.to_string());
        }
        Ok(request)
    }

    pub(super) fn credentials(&self) -> Result<(&str, &str, &str)> {
        match (&self.api_key, &self.api_secret, &self.memo) {
            (Some(api_key), Some(api_secret), Some(memo)) => Ok((api_key, api_secret, memo)),
            _ => Err(DcexError::InvalidInput(
                "Signed request requires API Key and Secret and Memo.".to_string(),
            )),
        }
    }

    pub(super) fn exchange_symbol(&self, product_symbol: &str, spot: bool) -> Result<String> {
        if is_canonical_product_symbol(product_symbol) {
            if let Some(table) = &self.product_table {
                return table.get_exchange_symbol("bitmart", product_symbol);
            }
        }
        Ok(exchange_symbol_fallback(product_symbol, spot))
    }
}
