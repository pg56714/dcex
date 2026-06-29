use std::sync::Arc;
use std::time::Duration;

use serde_json::Value;

use crate::exchange::{ExchangeHttpClient, ValidatedResponse};
use crate::http::{block_on, HttpMethod, HttpRequest, HttpResponse};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

use super::endpoints::BASE_URL;
use super::params::{exchange_symbol_fallback, is_canonical_product_symbol};
use super::signing::{BingxResponseValidator, BingxSigner};

#[derive(Clone)]
pub struct BingxClient {
    inner: ExchangeHttpClient,
    base_url: String,
    api_key: Option<String>,
    product_table: Option<Arc<ProductTable>>,
}

impl BingxClient {
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
        let mut inner =
            ExchangeHttpClient::new(timeout)?.with_validator(Arc::new(BingxResponseValidator));
        if let (Some(api_key), Some(api_secret)) = (api_key.clone(), api_secret) {
            inner = inner.with_signer(Arc::new(BingxSigner {
                api_key,
                api_secret,
            }));
        }
        Ok(Self {
            inner,
            base_url,
            api_key,
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
        signed: bool,
        headers: Vec<(String, String)>,
        json_body: Option<Value>,
    ) -> Result<ValidatedResponse> {
        self.inner
            .execute(
                self.build_request(method, path, params, signed, headers, json_body),
                signed,
            )
            .await
    }

    pub async fn request_raw(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
        headers: Vec<(String, String)>,
        json_body: Option<Value>,
    ) -> Result<HttpResponse> {
        self.inner
            .execute_raw(
                self.build_request(method, path, params, signed, headers, json_body),
                signed,
            )
            .await
    }

    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
        headers: Vec<(String, String)>,
        json_body: Option<Value>,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move {
            client
                .request_raw(method, path, params, signed, headers, json_body)
                .await
        })
    }

    pub(super) async fn private_get(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Get, path, params, true, Vec::new(), None)
            .await
    }

    pub(super) async fn private_post(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Post, path, params, true, Vec::new(), None)
            .await
    }

    pub(super) async fn private_delete(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Delete, path, params, true, Vec::new(), None)
            .await
    }

    pub(super) async fn private_put(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Put, path, params, true, Vec::new(), None)
            .await
    }

    pub(super) async fn unsigned_post_with_api_key(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let api_key = self.api_key.as_deref().ok_or_else(|| {
            DcexError::InvalidInput("BingX API key is required for this request.".to_string())
        })?;
        let headers = vec![("X-BX-APIKEY".to_string(), api_key.to_string())];
        self.request(HttpMethod::Post, path, params, false, headers, None)
            .await
    }

    pub(super) async fn public_get(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            path,
            params,
            false,
            vec![("Content-Type".to_string(), "application/json".to_string())],
            None,
        )
        .await
    }

    pub(super) fn build_request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        mut params: Vec<(String, String)>,
        signed: bool,
        headers: Vec<(String, String)>,
        json_body: Option<Value>,
    ) -> HttpRequest {
        params.sort_by(|left, right| left.0.cmp(&right.0));
        let mut request = HttpRequest::new(method, &self.base_url, path);
        request.headers.extend(headers);
        if signed || matches!(method, HttpMethod::Get | HttpMethod::Delete) {
            request.query = params;
        } else if let Some(json_body) = json_body {
            request = request.json(json_body);
        } else {
            request.query = params;
        }
        request
    }

    pub(super) fn exchange_symbol(&self, product_symbol: &str) -> Result<String> {
        if is_canonical_product_symbol(product_symbol) {
            if let Some(table) = &self.product_table {
                return table.get_exchange_symbol("bingx", product_symbol);
            }
        }
        Ok(exchange_symbol_fallback(product_symbol))
    }

    pub(super) fn push_required_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &super::params::BingxParams,
    ) -> Result<()> {
        let product_symbol = params.required_any(&["product_symbol", "symbol"])?;
        query.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        Ok(())
    }

    pub(super) fn push_optional_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &super::params::BingxParams,
    ) -> Result<()> {
        if let Some(product_symbol) = params
            .get("product_symbol")
            .or_else(|| params.get("symbol"))
        {
            query.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        }
        Ok(())
    }
}
