use std::sync::Arc;
use std::time::Duration;

use serde_json::{Map, Value};

use crate::crypto::hmac_sha256_hex;
use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

use super::endpoints::BASE_URL;
use super::params::{
    exchange_symbol_fallback, insert_optional_string, is_canonical_product_symbol, BitmexParams,
};
use super::signing::{encode_params, http_method_name, validate_response};

#[derive(Clone)]
pub struct BitmexClient {
    transport: AsyncHttpClient,
    base_url: String,
    api_key: Option<String>,
    api_secret: Option<String>,
    product_table: Option<Arc<ProductTable>>,
}

impl BitmexClient {
    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_url(api_key, api_secret, timeout, BASE_URL.to_string())
    }

    pub fn public(timeout: Duration) -> Result<Self> {
        Self::new(None, None, timeout)
    }

    pub fn with_base_url(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: Duration,
        base_url: String,
    ) -> Result<Self> {
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            base_url,
            api_key,
            api_secret,
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
        let expires = unix_timestamp_ms()? / 1000 + 5;
        let request = self.build_request(method, path, params, body, signed, expires)?;
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

    pub(super) async fn public_get(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Get, path, params, None, false)
            .await
    }

    pub(super) async fn get_private(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Get, path, params, None, true)
            .await
    }

    pub(super) async fn private_json(
        &self,
        method: HttpMethod,
        path: &str,
        body: Value,
    ) -> Result<ValidatedResponse> {
        let body =
            serde_json::to_vec(&body).map_err(|error| DcexError::Decode(error.to_string()))?;
        self.request(method, path, Vec::new(), Some(body), true)
            .await
    }

    pub(super) fn build_request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
        expires: u64,
    ) -> Result<HttpRequest> {
        let path = path.into();
        let mut request = HttpRequest::new(method, &self.base_url, &path)
            .header("Accept", "application/json")
            .header("Content-Type", "application/json");
        let full_path = if matches!(method, HttpMethod::Get) && !params.is_empty() {
            request.query = params;
            format!("{path}?{}", encode_params(&request.query))
        } else {
            path
        };
        if !matches!(method, HttpMethod::Get) {
            request.body = body.clone().map(RequestBody::Raw).unwrap_or_default();
        }
        if signed {
            if let (Some(api_key), Some(api_secret)) = (&self.api_key, &self.api_secret) {
                let body = String::from_utf8_lossy(body.as_deref().unwrap_or_default());
                let payload = format!("{}{full_path}{expires}{body}", http_method_name(method));
                let signature = hmac_sha256_hex(api_secret.as_bytes(), payload.as_bytes())?;
                request
                    .headers
                    .insert("api-key".to_string(), api_key.clone());
                request
                    .headers
                    .insert("api-signature".to_string(), signature);
                request
                    .headers
                    .insert("api-expires".to_string(), expires.to_string());
            }
        }
        Ok(request)
    }

    pub(super) fn exchange_symbol(&self, product_symbol: &str) -> Result<String> {
        if is_canonical_product_symbol(product_symbol) {
            if let Some(table) = &self.product_table {
                return table.get_exchange_symbol("bitmex", product_symbol);
            }
        }
        Ok(exchange_symbol_fallback(product_symbol))
    }

    pub(super) fn push_product_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &BitmexParams,
    ) -> Result<()> {
        if let Some(symbol) = params.get("symbol") {
            query.push(("symbol".to_string(), self.exchange_symbol(symbol)?));
        } else if let Some(product_symbol) = params.get("product_symbol") {
            query.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        }
        Ok(())
    }

    pub(super) fn insert_product_symbol(
        &self,
        body: &mut Map<String, Value>,
        params: &BitmexParams,
    ) -> Result<()> {
        if let Some(symbol) = params.get("symbol") {
            let symbol = self.exchange_symbol(symbol)?;
            insert_optional_string(body, "symbol", Some(&symbol));
        } else if let Some(product_symbol) = params.get("product_symbol") {
            let symbol = self.exchange_symbol(product_symbol)?;
            insert_optional_string(body, "symbol", Some(&symbol));
        }
        Ok(())
    }

    pub(super) fn insert_required_product_symbol(
        &self,
        body: &mut Map<String, Value>,
        params: &BitmexParams,
    ) -> Result<()> {
        let symbol = if let Some(symbol) = params.get("symbol") {
            self.exchange_symbol(symbol)?
        } else {
            self.exchange_symbol(params.required("product_symbol")?)?
        };
        body.insert("symbol".to_string(), Value::String(symbol));
        Ok(())
    }
}
