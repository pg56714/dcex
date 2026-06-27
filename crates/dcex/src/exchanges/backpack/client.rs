use std::collections::BTreeMap;
use std::sync::Arc;
use std::time::Duration;

use ed25519_dalek::SigningKey;
use serde_json::Value;

use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::product_table::ProductTable;
use crate::{DcexError, Result};

use super::endpoints::BASE_URL;
use super::params::signature_payload_from_value;
use super::signing::{decode_signing_key, encode_params, http_method_name, signature_header};

pub type SignaturePayload = Vec<Vec<(String, String)>>;

#[derive(Clone)]
pub struct BackpackClient {
    transport: AsyncHttpClient,
    base_url: String,
    api_key: Option<String>,
    signing_key: Option<SigningKey>,
    window: u64,
    product_table: Option<Arc<ProductTable>>,
}

impl BackpackClient {
    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        window: u64,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_url(api_key, api_secret, window, timeout, BASE_URL.to_string())
    }

    pub fn public(window: u64, timeout: Duration) -> Result<Self> {
        Self::new(None, None, window, timeout)
    }

    pub fn with_base_url(
        api_key: Option<String>,
        api_secret: Option<String>,
        window: u64,
        timeout: Duration,
        base_url: String,
    ) -> Result<Self> {
        let signing_key = api_secret
            .map(|secret| decode_signing_key(&secret))
            .transpose()?;
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            base_url,
            api_key,
            signing_key,
            window,
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

    #[allow(clippy::too_many_arguments)]
    pub async fn request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
        instruction: Option<String>,
        signature_payload: Option<SignaturePayload>,
        extra_headers: BTreeMap<String, String>,
    ) -> Result<ValidatedResponse> {
        let response = self
            .request_raw(
                method,
                path,
                params,
                body,
                signed,
                instruction,
                signature_payload,
                extra_headers,
            )
            .await?;
        response.ensure_success()?;
        let data = match response.json() {
            Ok(data) => data,
            Err(DcexError::Decode(_)) => Value::String(response.text()?),
            Err(error) => return Err(error),
        };
        Ok(ValidatedResponse {
            status: response.status,
            headers: response.headers,
            data,
        })
    }

    #[allow(clippy::too_many_arguments)]
    pub async fn request_raw(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
        instruction: Option<String>,
        signature_payload: Option<SignaturePayload>,
        extra_headers: BTreeMap<String, String>,
    ) -> Result<HttpResponse> {
        let timestamp = unix_timestamp_ms()?.to_string();
        let request = self.build_request(
            method,
            path,
            params,
            body,
            signed,
            instruction.as_deref(),
            signature_payload.as_deref(),
            extra_headers,
            &timestamp,
        )?;
        self.transport.execute(request).await
    }

    #[allow(clippy::too_many_arguments)]
    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Option<Vec<u8>>,
        signed: bool,
        instruction: Option<String>,
        signature_payload: Option<SignaturePayload>,
        extra_headers: BTreeMap<String, String>,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move {
            client
                .request_raw(
                    method,
                    path,
                    params,
                    body,
                    signed,
                    instruction,
                    signature_payload,
                    extra_headers,
                )
                .await
        })
    }

    pub async fn public_path_request(
        &self,
        path: impl Into<String>,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            path,
            params,
            None,
            false,
            None,
            None,
            BTreeMap::new(),
        )
        .await
    }

    pub(super) async fn public_get(
        &self,
        path: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.public_path_request(path, params).await
    }

    pub(super) async fn private_get(
        &self,
        path: &str,
        params: Vec<(String, String)>,
        instruction: &str,
    ) -> Result<ValidatedResponse> {
        let signature_payload = if params.is_empty() {
            None
        } else {
            Some(vec![params.clone()])
        };
        self.request(
            HttpMethod::Get,
            path,
            params,
            None,
            true,
            Some(instruction.to_string()),
            signature_payload,
            BTreeMap::new(),
        )
        .await
    }

    pub(super) async fn private_post_value(
        &self,
        path: &str,
        body: Value,
        instruction: &str,
    ) -> Result<ValidatedResponse> {
        self.private_body_request(HttpMethod::Post, path, body, instruction)
            .await
    }

    pub(super) async fn private_delete_value(
        &self,
        path: &str,
        body: Value,
        instruction: &str,
    ) -> Result<ValidatedResponse> {
        self.private_body_request(HttpMethod::Delete, path, body, instruction)
            .await
    }

    async fn private_body_request(
        &self,
        method: HttpMethod,
        path: &str,
        body: Value,
        instruction: &str,
    ) -> Result<ValidatedResponse> {
        let signature_payload = signature_payload_from_value(&body);
        let body = serde_json::to_vec(&body)
            .map_err(|error| DcexError::InvalidInput(format!("invalid JSON body: {error}")))?;
        self.request(
            method,
            path,
            Vec::new(),
            Some(body),
            true,
            Some(instruction.to_string()),
            Some(signature_payload),
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
        instruction: Option<&str>,
        signature_payload: Option<&[Vec<(String, String)>]>,
        extra_headers: BTreeMap<String, String>,
        timestamp: &str,
    ) -> Result<HttpRequest> {
        if !matches!(
            method,
            HttpMethod::Get | HttpMethod::Post | HttpMethod::Patch | HttpMethod::Delete
        ) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Backpack HTTP method: {}",
                http_method_name(method)
            )));
        }

        let path = path.into();
        let query = if method == HttpMethod::Get {
            encode_params(&params)
        } else {
            String::new()
        };
        let request_path = if query.is_empty() {
            path
        } else {
            format!("{path}?{query}")
        };
        let mut request = HttpRequest::new(method, &self.base_url, request_path)
            .header("Accept", "application/json")
            .header("Content-Type", "application/json");
        request.headers.extend(extra_headers);
        if matches!(
            method,
            HttpMethod::Post | HttpMethod::Patch | HttpMethod::Delete
        ) {
            if let Some(body) = body {
                request.body = RequestBody::Raw(body);
            }
        }

        if signed {
            let api_key = self.api_key.as_deref().ok_or_else(|| {
                DcexError::InvalidInput(
                    "Signed Backpack requests require api_key and api_secret.".to_string(),
                )
            })?;
            let signing_key = self.signing_key.as_ref().ok_or_else(|| {
                DcexError::InvalidInput(
                    "Signed Backpack requests require api_key and api_secret.".to_string(),
                )
            })?;
            let instruction = instruction.ok_or_else(|| {
                DcexError::InvalidInput(
                    "Signed Backpack requests require an instruction.".to_string(),
                )
            })?;
            let signature_payload = signature_payload.unwrap_or_default().to_vec();
            request
                .headers
                .insert("X-API-Key".to_string(), api_key.to_string());
            request.headers.insert(
                "X-Signature".to_string(),
                signature_header(
                    signing_key,
                    instruction,
                    &signature_payload,
                    timestamp,
                    self.window,
                ),
            );
            request
                .headers
                .insert("X-Timestamp".to_string(), timestamp.to_string());
            request
                .headers
                .insert("X-Window".to_string(), self.window.to_string());
        }
        Ok(request)
    }

    pub(super) fn exchange_symbol(&self, product_symbol: &str) -> Result<String> {
        if product_symbol.contains('_') {
            return Ok(product_symbol.to_string());
        }
        if product_symbol.contains('-') {
            if let Some(table) = &self.product_table {
                return table.get_exchange_symbol("backpack", product_symbol);
            }
            return Ok(exchange_symbol_fallback(product_symbol));
        }
        Ok(product_symbol.to_string())
    }

    pub(super) fn websocket_signature(&self, timestamp: &str) -> Result<[String; 4]> {
        let api_key = self.api_key.as_deref().ok_or_else(|| {
            DcexError::InvalidInput(
                "Backpack private WebSocket subscriptions require api_key and api_secret."
                    .to_string(),
            )
        })?;
        let signing_key = self.signing_key.as_ref().ok_or_else(|| {
            DcexError::InvalidInput(
                "Backpack private WebSocket subscriptions require api_key and api_secret."
                    .to_string(),
            )
        })?;
        Ok([
            api_key.to_string(),
            signature_header(
                signing_key,
                "subscribe",
                &Vec::new(),
                timestamp,
                self.window,
            ),
            timestamp.to_string(),
            self.window.to_string(),
        ])
    }
}

fn exchange_symbol_fallback(product_symbol: &str) -> String {
    let parts = product_symbol.split('-').collect::<Vec<_>>();
    match parts.as_slice() {
        [base, quote, "SPOT"] => format!("{base}_{quote}"),
        [base, quote, ..] => format!("{base}_{quote}_PERP"),
        _ => product_symbol.to_string(),
    }
}
