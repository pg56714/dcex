use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::Arc;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

use super::endpoints::{FUTURES_BASE_URL, SPOT_BASE_URL};
use super::params::json_value_string;
use super::signing::{encode_params, http_method_name, parse_private_key, sign_message};

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum AsterMarket {
    Futures,
    Spot,
}

impl AsterMarket {
    pub fn from_path(path: &str) -> Result<Self> {
        if path.starts_with("/fapi/") {
            return Ok(Self::Futures);
        }
        if path.starts_with("/api/") {
            return Ok(Self::Spot);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported Aster API path: {path}"
        )))
    }
}

#[derive(Clone)]
pub struct AsterClient {
    transport: AsyncHttpClient,
    spot_base_url: String,
    futures_base_url: String,
    user_address: Option<String>,
    signer_address: Option<String>,
    private_key: Option<[u8; 32]>,
    last_nonce: Arc<AtomicU64>,
    product_table: Option<Arc<ProductTable>>,
}

impl AsterClient {
    pub fn new(
        user_address: Option<String>,
        signer_address: Option<String>,
        private_key: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_urls(
            user_address,
            signer_address,
            private_key,
            timeout,
            SPOT_BASE_URL.to_string(),
            FUTURES_BASE_URL.to_string(),
        )
    }

    pub fn public(timeout: Duration) -> Result<Self> {
        Self::new(None, None, None, timeout)
    }

    pub fn with_base_urls(
        user_address: Option<String>,
        signer_address: Option<String>,
        private_key: Option<String>,
        timeout: Duration,
        spot_base_url: String,
        futures_base_url: String,
    ) -> Result<Self> {
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            spot_base_url,
            futures_base_url,
            user_address,
            signer_address,
            private_key: private_key.map(|key| parse_private_key(&key)).transpose()?,
            last_nonce: Arc::new(AtomicU64::new(0)),
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
        market: AsterMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
    ) -> Result<ValidatedResponse> {
        let response = self
            .request_raw(method, market, path, params, signed)
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
        market: AsterMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let request = self.build_request(method, market, path, params, signed, None)?;
        self.transport.execute(request).await
    }

    pub async fn request_raw_auto(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let path = path.into();
        let market = AsterMarket::from_path(&path)?;
        self.request_raw(method, market, path, params, signed).await
    }

    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        market: AsterMarket,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move {
            client
                .request_raw(method, market, path, params, signed)
                .await
        })
    }

    pub fn request_raw_auto_blocking(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        signed: bool,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move { client.request_raw_auto(method, path, params, signed).await })
    }

    pub(super) fn build_request(
        &self,
        method: HttpMethod,
        market: AsterMarket,
        path: impl Into<String>,
        mut params: Vec<(String, String)>,
        signed: bool,
        nonce: Option<u64>,
    ) -> Result<HttpRequest> {
        if !matches!(
            method,
            HttpMethod::Get | HttpMethod::Post | HttpMethod::Put | HttpMethod::Delete
        ) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Aster HTTP method: {}",
                http_method_name(method)
            )));
        }
        if signed {
            let signer_address = self.signer_address.as_deref().ok_or_else(|| {
                DcexError::InvalidInput(
                    "Signed Aster requests require signer_address and private_key.".to_string(),
                )
            })?;
            let private_key = self.private_key.as_ref().ok_or_else(|| {
                DcexError::InvalidInput(
                    "Signed Aster requests require signer_address and private_key.".to_string(),
                )
            })?;
            let nonce = match nonce {
                Some(nonce) => nonce,
                None => self.next_nonce()?,
            };
            params.push(("nonce".to_string(), nonce.to_string()));
            if market == AsterMarket::Futures {
                let user_address = self.user_address.as_deref().ok_or_else(|| {
                    DcexError::InvalidInput(
                        "Signed Aster futures requests require user_address.".to_string(),
                    )
                })?;
                params.push(("user".to_string(), user_address.to_string()));
            }
            params.push(("signer".to_string(), signer_address.to_string()));
            let message = encode_params(&params);
            params.push((
                "signature".to_string(),
                sign_message(&message, private_key)?,
            ));
        }

        let base_url = match market {
            AsterMarket::Futures => &self.futures_base_url,
            AsterMarket::Spot => &self.spot_base_url,
        };
        let path = path.into();
        let encoded = encode_params(&params);
        let mut request =
            HttpRequest::new(method, base_url, &path).header("Accept", "application/json");
        if method == HttpMethod::Get {
            if !encoded.is_empty() {
                request.path = format!("{path}?{encoded}");
            }
        } else {
            request.headers.insert(
                "Content-Type".to_string(),
                "application/x-www-form-urlencoded".to_string(),
            );
            if !encoded.is_empty() {
                request.body = RequestBody::Raw(encoded.into_bytes());
            }
        }
        Ok(request)
    }

    fn next_nonce(&self) -> Result<u64> {
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map_err(|error| DcexError::Runtime(error.to_string()))?
            .as_nanos()
            / 1_000;
        let now = u64::try_from(now).unwrap_or(u64::MAX);
        Ok(self
            .last_nonce
            .fetch_update(Ordering::Relaxed, Ordering::Relaxed, |previous| {
                Some(now.max(previous.saturating_add(1)))
            })
            .map(|previous| now.max(previous.saturating_add(1)))
            .unwrap_or(now))
    }

    pub(super) fn exchange_symbol(&self, product_symbol: &str) -> Result<String> {
        if !product_symbol.contains('-') {
            return Ok(product_symbol.to_string());
        }
        if let Some(table) = &self.product_table {
            return table.get_exchange_symbol("aster", product_symbol);
        }
        Ok(exchange_symbol_fallback(product_symbol))
    }
}

fn exchange_symbol_fallback(product_symbol: &str) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) => format!("{base}{quote}"),
        _ => product_symbol.to_string(),
    }
}

pub(super) fn validate_response(response: &HttpResponse) -> Result<Value> {
    let data = response.json()?;
    response.ensure_success()?;
    if let Some(object) = data.as_object() {
        let code = object.get("code");
        if code.is_some_and(|code| !matches!(json_value_string(code).as_str(), "0" | "200")) {
            let message = object
                .get("msg")
                .or_else(|| object.get("message"))
                .and_then(Value::as_str)
                .unwrap_or("Unknown error");
            return Err(DcexError::HttpStatus {
                status: response.status,
                message: format!(
                    "Aster API error [{}]: {message}",
                    code.map(json_value_string)
                        .unwrap_or_else(|| "null".to_string())
                ),
                headers: response
                    .headers
                    .iter()
                    .map(|(key, value)| (key.clone(), value.clone()))
                    .collect(),
            });
        }
    }
    Ok(data)
}
