use std::sync::Arc;
use std::time::Duration;

use serde_json::Value;

use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

use super::endpoints::{FUTURES_BASE_URL, SPOT_BASE_URL};
use super::params::{exchange_symbol_fallback, is_canonical_product_symbol, KucoinParams};
use super::signing::{
    encrypted_passphrase, http_method_name, request_signature, validate_response,
};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum KucoinMarket {
    Futures,
    Spot,
}

#[derive(Clone)]
pub struct KucoinClient {
    transport: AsyncHttpClient,
    spot_base_url: String,
    futures_base_url: String,
    api_key: Option<String>,
    api_secret: Option<String>,
    encrypted_passphrase: Option<String>,
    product_table: Option<Arc<ProductTable>>,
}

impl KucoinClient {
    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        passphrase: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_urls(
            api_key,
            api_secret,
            passphrase,
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
        passphrase: Option<String>,
        timeout: Duration,
        spot_base_url: String,
        futures_base_url: String,
    ) -> Result<Self> {
        let encrypted_passphrase =
            encrypted_passphrase(api_secret.as_deref(), passphrase.as_deref())?;
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            spot_base_url,
            futures_base_url,
            api_key,
            api_secret,
            encrypted_passphrase,
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
        market: KucoinMarket,
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
        market: KucoinMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let timestamp = unix_timestamp_ms()?.to_string();
        let request = self.build_request(method, market, path, params, body, signed, &timestamp)?;
        self.transport.execute(request).await
    }

    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        market: KucoinMarket,
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

    pub(super) async fn private_get(
        &self,
        market: KucoinMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Get, market, path, params, None, true)
            .await
    }

    pub(super) async fn private_post(
        &self,
        market: KucoinMarket,
        path: impl Into<String>,
        body: Value,
    ) -> Result<ValidatedResponse> {
        let body = serde_json::to_vec(&body).map_err(|error| {
            DcexError::InvalidInput(format!("invalid KuCoin JSON body: {error}"))
        })?;
        self.request(HttpMethod::Post, market, path, Vec::new(), Some(body), true)
            .await
    }

    pub(super) async fn private_delete(
        &self,
        market: KucoinMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Delete, market, path, params, None, true)
            .await
    }

    pub(super) fn build_request(
        &self,
        method: HttpMethod,
        market: KucoinMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
        timestamp: &str,
    ) -> Result<HttpRequest> {
        if !matches!(
            method,
            HttpMethod::Get | HttpMethod::Post | HttpMethod::Put | HttpMethod::Delete
        ) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported KuCoin HTTP method: {}",
                http_method_name(method)
            )));
        }

        let path = path.into();
        let query = if matches!(method, HttpMethod::Get | HttpMethod::Delete) {
            url::form_urlencoded::Serializer::new(String::new())
                .extend_pairs(params)
                .finish()
        } else {
            String::new()
        };
        let request_path = if query.is_empty() {
            path
        } else {
            format!("{path}?{query}")
        };
        let body = if matches!(method, HttpMethod::Post | HttpMethod::Put) {
            body.unwrap_or_default()
        } else {
            Vec::new()
        };
        let base_url = match market {
            KucoinMarket::Futures => &self.futures_base_url,
            KucoinMarket::Spot => &self.spot_base_url,
        };
        let mut request = HttpRequest::new(method, base_url, &request_path)
            .header("Content-Type", "application/json");
        if matches!(method, HttpMethod::Post | HttpMethod::Put) && !body.is_empty() {
            request.body = RequestBody::Raw(body.clone());
        }

        if signed {
            let (api_key, api_secret, encrypted_passphrase) = self.credentials()?;
            let signature = request_signature(api_secret, timestamp, method, &request_path, &body)?;
            request
                .headers
                .insert("KC-API-KEY".to_string(), api_key.to_string());
            request.headers.insert("KC-API-SIGN".to_string(), signature);
            request
                .headers
                .insert("KC-API-TIMESTAMP".to_string(), timestamp.to_string());
            request.headers.insert(
                "KC-API-PASSPHRASE".to_string(),
                encrypted_passphrase.to_string(),
            );
            request
                .headers
                .insert("KC-API-KEY-VERSION".to_string(), "2".to_string());
        }

        Ok(request)
    }

    fn credentials(&self) -> Result<(&str, &str, &str)> {
        match (&self.api_key, &self.api_secret, &self.encrypted_passphrase) {
            (Some(api_key), Some(api_secret), Some(encrypted_passphrase)) => {
                Ok((api_key, api_secret, encrypted_passphrase))
            }
            _ => Err(DcexError::InvalidInput(
                "Signed request requires API Key, Secret, and Passphrase.".to_string(),
            )),
        }
    }

    pub(super) fn exchange_symbol(&self, product_symbol: &str, futures: bool) -> Result<String> {
        if is_canonical_product_symbol(product_symbol) {
            if let Some(table) = &self.product_table {
                return table.get_exchange_symbol("kucoin", product_symbol);
            }
        }
        Ok(exchange_symbol_fallback(product_symbol, futures))
    }

    pub(super) fn push_required_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &KucoinParams,
        futures: bool,
    ) -> Result<()> {
        let product_symbol = params.required_any(&["product_symbol", "symbol"])?;
        query.push((
            "symbol".to_string(),
            self.exchange_symbol(product_symbol, futures)?,
        ));
        Ok(())
    }

    pub(super) fn push_optional_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &KucoinParams,
        futures: bool,
    ) -> Result<()> {
        if let Some(product_symbol) = params.get_any(&["product_symbol", "symbol"]) {
            query.push((
                "symbol".to_string(),
                self.exchange_symbol(product_symbol, futures)?,
            ));
        }
        Ok(())
    }
}
