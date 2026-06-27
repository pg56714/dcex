use std::sync::Arc;
use std::time::Duration;

use serde_json::{Map, Value};

use crate::crypto::hmac_sha256_base64;
use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

use super::endpoints::BASE_URL;
use super::params::{exchange_symbol_fallback, is_canonical_product_symbol, OkxParams};
use super::signing::{http_method_name, iso_timestamp, validate_response};

#[derive(Clone)]
pub struct OkxClient {
    transport: AsyncHttpClient,
    base_url: String,
    api_key: Option<String>,
    api_secret: Option<String>,
    passphrase: Option<String>,
    flag: String,
    product_table: Option<Arc<ProductTable>>,
}

impl OkxClient {
    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        passphrase: Option<String>,
        flag: String,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_url(
            api_key,
            api_secret,
            passphrase,
            flag,
            timeout,
            BASE_URL.to_string(),
        )
    }

    pub fn public(timeout: Duration) -> Result<Self> {
        Self::new(None, None, None, "0".to_string(), timeout)
    }

    pub fn with_base_url(
        api_key: Option<String>,
        api_secret: Option<String>,
        passphrase: Option<String>,
        flag: String,
        timeout: Duration,
        base_url: String,
    ) -> Result<Self> {
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            base_url,
            api_key,
            api_secret,
            passphrase,
            flag,
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
        let timestamp = iso_timestamp(unix_timestamp_ms()?);
        let request = self.build_request(method, path, params, body, signed, &timestamp)?;
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

    pub(super) fn build_request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
        timestamp: &str,
    ) -> Result<HttpRequest> {
        if !matches!(method, HttpMethod::Get | HttpMethod::Post) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported OKX HTTP method: {}",
                http_method_name(method)
            )));
        }

        let path = path.into();
        let query = if method == HttpMethod::Get {
            params
                .iter()
                .filter(|(_, value)| !value.is_empty())
                .map(|(key, value)| format!("{key}={value}"))
                .collect::<Vec<_>>()
                .join("&")
        } else {
            String::new()
        };
        let request_path = if query.is_empty() {
            path
        } else {
            format!("{path}?{query}")
        };
        let body = if method == HttpMethod::Post {
            body.unwrap_or_default()
        } else {
            Vec::new()
        };

        let mut request = HttpRequest::new(method, &self.base_url, &request_path)
            .header("Content-Type", "application/json")
            .header("x-simulated-trading", &self.flag);

        if method == HttpMethod::Post {
            request.body = RequestBody::Raw(body.clone());
        }

        if signed {
            let (api_key, api_secret, passphrase) = self.credentials()?;
            let canonical = format!(
                "{timestamp}{}{request_path}{}",
                http_method_name(method),
                String::from_utf8_lossy(&body)
            );
            let signature = hmac_sha256_base64(api_secret.as_bytes(), canonical.as_bytes())?;
            request
                .headers
                .insert("OK-ACCESS-KEY".to_string(), api_key.to_string());
            request
                .headers
                .insert("OK-ACCESS-SIGN".to_string(), signature);
            request
                .headers
                .insert("OK-ACCESS-TIMESTAMP".to_string(), timestamp.to_string());
            request
                .headers
                .insert("OK-ACCESS-PASSPHRASE".to_string(), passphrase.to_string());
        }

        Ok(request)
    }

    pub(super) fn credentials(&self) -> Result<(&str, &str, &str)> {
        match (&self.api_key, &self.api_secret, &self.passphrase) {
            (Some(api_key), Some(api_secret), Some(passphrase)) => {
                Ok((api_key, api_secret, passphrase))
            }
            _ => Err(DcexError::InvalidInput(
                "Signed request requires API Key and Secret and Passphrase.".to_string(),
            )),
        }
    }

    pub(super) async fn get_request(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(HttpMethod::Get, path, params, None, true)
            .await
    }

    pub(super) async fn post_request(&self, path: &str, body: Value) -> Result<ValidatedResponse> {
        let body =
            serde_json::to_vec(&body).map_err(|error| DcexError::Decode(error.to_string()))?;
        self.request(HttpMethod::Post, path, Vec::new(), Some(body), true)
            .await
    }

    pub(super) fn exchange_symbol(&self, product_symbol: &str) -> Result<String> {
        if is_canonical_product_symbol(product_symbol) {
            if let Some(table) = &self.product_table {
                return table.get_exchange_symbol("okx", product_symbol);
            }
        }
        Ok(exchange_symbol_fallback(product_symbol))
    }

    pub(super) fn push_inst_id(
        &self,
        query: &mut Vec<(String, String)>,
        params: &OkxParams,
        key: &str,
    ) -> Result<()> {
        if let Some(product_symbol) = params.get(key) {
            query.push(("instId".to_string(), self.exchange_symbol(product_symbol)?));
        }
        Ok(())
    }

    pub(super) fn push_required_inst_id(
        &self,
        query: &mut Vec<(String, String)>,
        params: &OkxParams,
    ) -> Result<()> {
        query.push((
            "instId".to_string(),
            self.exchange_symbol(params.required("product_symbol")?)?,
        ));
        Ok(())
    }

    pub(super) fn insert_inst_id(
        &self,
        body: &mut Map<String, Value>,
        params: &OkxParams,
        key: &str,
    ) -> Result<()> {
        if let Some(product_symbol) = params.get(key) {
            body.insert(
                "instId".to_string(),
                Value::String(self.exchange_symbol(product_symbol)?),
            );
        }
        Ok(())
    }

    pub(super) fn insert_required_inst_id(
        &self,
        body: &mut Map<String, Value>,
        params: &OkxParams,
    ) -> Result<()> {
        body.insert(
            "instId".to_string(),
            Value::String(self.exchange_symbol(params.required("product_symbol")?)?),
        );
        Ok(())
    }
}
