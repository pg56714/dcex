use std::collections::BTreeMap;
use std::sync::atomic::{AtomicI64, Ordering};
use std::sync::Arc;
use std::time::Duration;

use serde_json::Value;

use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

use super::endpoints::BASE_URL;
use super::signing::{adjusted_timestamp_ms, rest_signature, server_clock_offset_ms};

#[derive(Clone)]
pub struct OndoClient {
    transport: AsyncHttpClient,
    base_url: String,
    api_key_id: Option<String>,
    api_secret: Option<String>,
    timestamp_offset_ms: Arc<AtomicI64>,
    product_table: Option<Arc<ProductTable>>,
}

impl OndoClient {
    pub fn new(
        api_key_id: Option<String>,
        api_secret: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_url(api_key_id, api_secret, timeout, BASE_URL.to_string())
    }

    pub fn public(timeout: Duration) -> Result<Self> {
        Self::new(None, None, timeout)
    }

    pub fn with_base_url(
        api_key_id: Option<String>,
        api_secret: Option<String>,
        timeout: Duration,
        base_url: String,
    ) -> Result<Self> {
        let (api_key_id, api_secret) = validate_api_credentials(api_key_id, api_secret)?;
        let base_url = validate_base_url(base_url)?;
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            base_url,
            api_key_id,
            api_secret,
            timestamp_offset_ms: Arc::new(AtomicI64::new(0)),
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

    pub fn base_url(&self) -> &str {
        &self.base_url
    }

    pub async fn request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
        extra_headers: BTreeMap<String, String>,
    ) -> Result<ValidatedResponse> {
        let response = self
            .request_raw(method, path, params, body, signed, extra_headers)
            .await?;
        response.ensure_success()?;
        let data = if response
            .headers
            .get("content-type")
            .is_some_and(|content_type| content_type.starts_with("text/csv"))
        {
            Value::String(response.text()?)
        } else {
            response.json()?
        };
        validate_ondo_response(&data)?;
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
        extra_headers: BTreeMap<String, String>,
    ) -> Result<HttpResponse> {
        let path = path.into();
        let timestamp = adjusted_timestamp_ms(self.timestamp_offset_ms.load(Ordering::Relaxed))?;
        let request = self.build_request(
            method,
            &path,
            params.clone(),
            body.clone(),
            signed,
            extra_headers.clone(),
            &timestamp,
        )?;
        let response = self.transport.execute(request).await?;
        if signed {
            if let Some(offset) = timestamp_rejection_offset(&response) {
                self.timestamp_offset_ms.store(offset, Ordering::Relaxed);
                let timestamp = adjusted_timestamp_ms(offset)?;
                let retry = self.build_request(
                    method,
                    path,
                    params,
                    body,
                    true,
                    extra_headers,
                    &timestamp,
                )?;
                return self.transport.execute(retry).await;
            }
        }
        Ok(response)
    }

    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
        extra_headers: BTreeMap<String, String>,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move {
            client
                .request_raw(method, path, params, body, signed, extra_headers)
                .await
        })
    }

    pub(super) async fn public_get(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            path,
            self.normalize_market_query(params)?,
            None,
            false,
            BTreeMap::new(),
        )
        .await
    }

    pub(super) async fn private_get(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            path,
            self.normalize_market_query(params)?,
            None,
            true,
            BTreeMap::new(),
        )
        .await
    }

    pub(super) async fn private_post(&self, path: &str, body: Value) -> Result<ValidatedResponse> {
        self.body_request(HttpMethod::Post, path, body, true).await
    }

    pub(super) async fn private_put(&self, path: &str, body: Value) -> Result<ValidatedResponse> {
        self.body_request(HttpMethod::Put, path, body, true).await
    }

    pub(super) async fn private_delete(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Delete,
            path,
            self.normalize_market_query(params)?,
            None,
            true,
            BTreeMap::new(),
        )
        .await
    }

    pub(super) async fn private_delete_body(
        &self,
        path: &str,
        body: Value,
    ) -> Result<ValidatedResponse> {
        self.body_request(HttpMethod::Delete, path, body, true)
            .await
    }

    async fn body_request(
        &self,
        method: HttpMethod,
        path: &str,
        mut body: Value,
        signed: bool,
    ) -> Result<ValidatedResponse> {
        self.normalize_market_body(&mut body)?;
        let body = serde_json::to_vec(&body)
            .map_err(|error| DcexError::InvalidInput(format!("invalid Ondo JSON body: {error}")))?;
        self.request(
            method,
            path,
            Vec::new(),
            Some(body),
            signed,
            BTreeMap::new(),
        )
        .await
    }

    #[allow(clippy::too_many_arguments)]
    pub(super) fn build_request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
        extra_headers: BTreeMap<String, String>,
        timestamp: &str,
    ) -> Result<HttpRequest> {
        let path = path.into();
        let query = encode_params(&params);
        let request_path = if query.is_empty() {
            path
        } else {
            format!("{path}?{query}")
        };
        let body = body.unwrap_or_default();
        let mut request = HttpRequest::new(method, &self.base_url, request_path.clone())
            .header("Accept", "application/json")
            .header("Content-Type", "application/json");
        request.headers.extend(extra_headers);
        if !body.is_empty() {
            request.body = RequestBody::Raw(body.clone());
        }
        if signed {
            match (self.api_key_id.as_deref(), self.api_secret.as_deref()) {
                (Some(api_key_id), Some(api_secret)) => {
                    request
                        .headers
                        .insert("ONDO-KEY-ID".to_string(), api_key_id.to_string());
                    request
                        .headers
                        .insert("ONDO-TIMESTAMP".to_string(), timestamp.to_string());
                    request.headers.insert(
                        "ONDO-SIGN".to_string(),
                        rest_signature(api_secret, timestamp, method, &request_path, &body)?,
                    );
                }
                _ => {
                    return Err(DcexError::InvalidInput(
                        "Signed Ondo requests require api_key_id and api_secret.".to_string(),
                    ))
                }
            }
        }
        Ok(request)
    }

    pub(super) fn exchange_symbol(&self, product_symbol: &str) -> Result<String> {
        if product_symbol.ends_with(".P") {
            return Ok(product_symbol.to_string());
        }
        if let Some(table) = &self.product_table {
            if let Ok(symbol) = table.get_exchange_symbol("ondo", product_symbol) {
                return Ok(symbol);
            }
        }
        let parts = product_symbol.split('-').collect::<Vec<_>>();
        match parts.as_slice() {
            [base, quote, "SWAP"] if !base.is_empty() && !quote.is_empty() => {
                Ok(format!("{base}-{quote}.P"))
            }
            _ => Err(DcexError::InvalidInput(format!(
                "invalid Ondo product symbol: {product_symbol}"
            ))),
        }
    }

    pub(super) fn normalize_market_query(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<Vec<(String, String)>> {
        params
            .into_iter()
            .map(|(key, value)| {
                if key == "market" {
                    Ok((key, self.exchange_symbol(&value)?))
                } else {
                    Ok((key, value))
                }
            })
            .collect()
    }

    fn normalize_market_body(&self, body: &mut Value) -> Result<()> {
        let Some(object) = body.as_object_mut() else {
            return Ok(());
        };
        if let Some(Value::String(market)) = object.get_mut("market") {
            *market = self.exchange_symbol(market)?;
        }
        if let Some(Value::Array(orders)) = object.get_mut("orders") {
            for order in orders {
                self.normalize_market_body(order)?;
            }
        }
        Ok(())
    }
}

fn timestamp_rejection_offset(response: &HttpResponse) -> Option<i64> {
    if response.status != 401 {
        return None;
    }
    let data: Value = serde_json::from_slice(&response.body).ok()?;
    if data.get("error_code")?.as_str()? != "timestamp_too_far" {
        return None;
    }
    server_clock_offset_ms(data.get("error")?.as_str()?, unix_timestamp_ms().ok()?)
}

fn validate_api_credentials(
    api_key_id: Option<String>,
    api_secret: Option<String>,
) -> Result<(Option<String>, Option<String>)> {
    let api_key_id = non_empty_optional(api_key_id, "Ondo API key ID")?;
    let api_secret = non_empty_optional(api_secret, "Ondo API secret")?;
    if api_key_id.is_some() != api_secret.is_some() {
        return Err(DcexError::InvalidInput(
            "Ondo api_key_id and api_secret must be provided together.".to_string(),
        ));
    }
    Ok((api_key_id, api_secret))
}

fn non_empty_optional(value: Option<String>, name: &str) -> Result<Option<String>> {
    value
        .map(|value| {
            let value = value.trim().to_string();
            if value.is_empty() {
                Err(DcexError::InvalidInput(format!("{name} must not be empty")))
            } else {
                Ok(value)
            }
        })
        .transpose()
}

fn validate_base_url(base_url: String) -> Result<String> {
    let base_url = base_url.trim().trim_end_matches('/').to_string();
    if base_url.is_empty() || !(base_url.starts_with("https://") || base_url.starts_with("http://"))
    {
        return Err(DcexError::InvalidInput(
            "Ondo REST base URL must use http:// or https://".to_string(),
        ));
    }
    Ok(base_url)
}

fn encode_params(params: &[(String, String)]) -> String {
    url::form_urlencoded::Serializer::new(String::new())
        .extend_pairs(
            params
                .iter()
                .map(|(key, value)| (key.as_str(), value.as_str())),
        )
        .finish()
}

fn validate_ondo_response(data: &Value) -> Result<()> {
    if data.get("success").and_then(Value::as_bool) != Some(false) {
        return Ok(());
    }
    let code = data
        .get("error_code")
        .and_then(Value::as_str)
        .unwrap_or("unknown_error");
    let message = data
        .get("error")
        .and_then(Value::as_str)
        .unwrap_or("Ondo request failed");
    Err(DcexError::Runtime(format!("Ondo {code}: {message}")))
}

#[cfg(test)]
mod timestamp_tests {
    use super::*;

    #[test]
    fn retries_only_explicit_timestamp_rejections() {
        let response = |status, body: &str| HttpResponse {
            status,
            headers: BTreeMap::new(),
            body: body.as_bytes().to_vec(),
        };
        let message = r#"{"error_code":"timestamp_too_far","error":"timestamp too far in the future. current time unixMilli 1789810892725, timestamp 1789810894652"}"#;
        assert!(timestamp_rejection_offset(&response(401, message)).is_some());
        assert!(timestamp_rejection_offset(&response(400, message)).is_none());
        assert!(timestamp_rejection_offset(&response(
            401,
            r#"{"error_code":"signature_mismatch"}"#
        ))
        .is_none());
    }
}
