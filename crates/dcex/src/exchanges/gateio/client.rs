use std::sync::Arc;
use std::time::Duration;

use serde_json::Value;

use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

use super::endpoints::{api_path, BASE_URL};
use super::params::{exchange_symbol_fallback, is_canonical_product_symbol};
use super::signing::{gateio_signature, validated};

#[derive(Clone)]
pub struct GateioClient {
    transport: AsyncHttpClient,
    base_url: String,
    api_key: Option<String>,
    api_secret: Option<String>,
    product_table: Option<Arc<ProductTable>>,
}

impl GateioClient {
    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_url(api_key, api_secret, timeout, BASE_URL.to_string())
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
        validated(response)
    }

    pub async fn request_raw(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let timestamp = unix_timestamp_ms()? / 1000;
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

    pub(super) async fn private_get(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Get, api_path(path), params, None, true)
            .await
    }

    pub(super) async fn private_delete(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Delete, api_path(path), params, None, true)
            .await
    }

    pub(super) async fn private_post_query(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Post, api_path(path), params, None, true)
            .await
    }

    pub(super) async fn private_post_json(
        &self,
        path: &str,
        body: Value,
    ) -> Result<ValidatedResponse> {
        let body =
            serde_json::to_vec(&body).map_err(|error| DcexError::Decode(error.to_string()))?;
        self.request(
            HttpMethod::Post,
            api_path(path),
            Vec::new(),
            Some(body),
            true,
        )
        .await
    }

    pub(super) async fn private_put_json(
        &self,
        path: &str,
        body: Value,
    ) -> Result<ValidatedResponse> {
        let body =
            serde_json::to_vec(&body).map_err(|error| DcexError::Decode(error.to_string()))?;
        self.request(
            HttpMethod::Put,
            api_path(path),
            Vec::new(),
            Some(body),
            true,
        )
        .await
    }

    pub(super) async fn private_patch_json(
        &self,
        path: &str,
        body: Value,
    ) -> Result<ValidatedResponse> {
        let body =
            serde_json::to_vec(&body).map_err(|error| DcexError::Decode(error.to_string()))?;
        self.request(
            HttpMethod::Patch,
            api_path(path),
            Vec::new(),
            Some(body),
            true,
        )
        .await
    }

    pub(super) fn build_request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
        timestamp: u64,
    ) -> Result<HttpRequest> {
        let path = path.into();
        let query = params
            .iter()
            .map(|(key, value)| format!("{key}={value}"))
            .collect::<Vec<_>>()
            .join("&");
        let request_path = if query.is_empty() {
            path.clone()
        } else {
            format!("{path}?{query}")
        };
        let mut request = HttpRequest::new(method, &self.base_url, request_path)
            .header("Accept", "application/json")
            .header("Content-Type", "application/json");
        if matches!(
            method,
            HttpMethod::Post | HttpMethod::Put | HttpMethod::Patch
        ) {
            request.body = body.clone().map(RequestBody::Raw).unwrap_or_default();
        }
        if signed {
            let (api_key, api_secret) = self.credentials()?;
            let signature = gateio_signature(
                method,
                &path,
                &query,
                body.as_deref().unwrap_or_default(),
                timestamp,
                api_secret,
            )?;
            request
                .headers
                .insert("KEY".to_string(), api_key.to_string());
            request
                .headers
                .insert("Timestamp".to_string(), timestamp.to_string());
            request.headers.insert("SIGN".to_string(), signature);
        }
        Ok(request)
    }

    pub(super) fn credentials(&self) -> Result<(&str, &str)> {
        match (&self.api_key, &self.api_secret) {
            (Some(api_key), Some(api_secret)) => Ok((api_key, api_secret)),
            _ => Err(DcexError::InvalidInput(
                "Signed request requires API Key and Secret.".to_string(),
            )),
        }
    }

    pub(super) fn exchange_symbol(&self, product_symbol: &str) -> Result<String> {
        if is_canonical_product_symbol(product_symbol) {
            if let Some(table) = &self.product_table {
                return table.get_exchange_symbol("gateio", product_symbol);
            }
        }
        Ok(exchange_symbol_fallback(product_symbol))
    }

    pub(super) fn normalize_contract_query(&self, params: &mut [(String, String)]) -> Result<()> {
        for (key, value) in params.iter_mut() {
            if key == "product_symbol" {
                *key = "contract".to_string();
                *value = self.exchange_symbol(value)?;
            } else if key == "contract" {
                *value = self.exchange_symbol(value)?;
            }
        }
        Ok(())
    }

    pub(super) fn normalize_currency_pair_query(
        &self,
        params: &mut [(String, String)],
    ) -> Result<()> {
        for (key, value) in params.iter_mut() {
            if key == "product_symbol" || key == "symbol" {
                *key = "currency_pair".to_string();
                *value = self.exchange_symbol(value)?;
            } else if key == "currency_pair" {
                *value = self.exchange_symbol(value)?;
            }
        }
        Ok(())
    }
}
