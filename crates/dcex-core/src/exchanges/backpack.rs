use std::collections::BTreeMap;
use std::time::Duration;

use base64::Engine;
use ed25519_dalek::{Signer, SigningKey};

use crate::exchange::{unix_timestamp_ms, ValidatedResponse};
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::{DcexError, Result};

const BASE_URL: &str = "https://api.backpack.exchange";

pub type SignaturePayload = Vec<Vec<(String, String)>>;

#[derive(Clone)]
pub struct BackpackClient {
    transport: AsyncHttpClient,
    base_url: String,
    api_key: Option<String>,
    signing_key: Option<SigningKey>,
    window: u64,
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
        })
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
        let data = response.json()?;
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

    pub async fn public_request(
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

    #[allow(clippy::too_many_arguments)]
    fn build_request(
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
            let message = signature_message(
                instruction,
                signature_payload.unwrap_or_default(),
                timestamp,
                self.window,
            );
            let signature = signing_key.sign(message.as_bytes());
            request
                .headers
                .insert("X-API-Key".to_string(), api_key.to_string());
            request.headers.insert(
                "X-Signature".to_string(),
                base64::engine::general_purpose::STANDARD.encode(signature.to_bytes()),
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
}

fn decode_signing_key(api_secret: &str) -> Result<SigningKey> {
    let seed = base64::engine::general_purpose::STANDARD
        .decode(api_secret)
        .map_err(|error| {
            DcexError::InvalidInput(format!("invalid Backpack API secret: {error}"))
        })?;
    let seed: [u8; 32] = seed.try_into().map_err(|seed: Vec<u8>| {
        DcexError::InvalidInput(format!(
            "Backpack API secret must decode to 32 bytes, got {}",
            seed.len()
        ))
    })?;
    Ok(SigningKey::from_bytes(&seed))
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

fn signature_message(
    instruction: &str,
    payload: &[Vec<(String, String)>],
    timestamp: &str,
    window: u64,
) -> String {
    let chunks = if payload.is_empty() {
        vec![format!("instruction={instruction}")]
    } else {
        payload
            .iter()
            .map(|item| {
                let mut sorted = item.clone();
                sorted.sort_by(|left, right| left.0.cmp(&right.0));
                let query = encode_params(&sorted);
                if query.is_empty() {
                    format!("instruction={instruction}")
                } else {
                    format!("instruction={instruction}&{query}")
                }
            })
            .collect()
    };
    format!("{}&timestamp={timestamp}&window={window}", chunks.join("&"))
}

const fn http_method_name(method: HttpMethod) -> &'static str {
    match method {
        HttpMethod::Delete => "DELETE",
        HttpMethod::Get => "GET",
        HttpMethod::Patch => "PATCH",
        HttpMethod::Post => "POST",
        HttpMethod::Put => "PUT",
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn signature_matches_python_vector() {
        let client = BackpackClient::new(
            Some(base64::engine::general_purpose::STANDARD.encode([b'2'; 32])),
            Some(base64::engine::general_purpose::STANDARD.encode([b'1'; 32])),
            5_000,
            Duration::from_secs(1),
        )
        .expect("client");
        let request = client
            .build_request(
                HttpMethod::Get,
                "/api/v1/order",
                vec![
                    ("symbol".to_string(), "BTC_USDC".to_string()),
                    ("orderId".to_string(), "test-order-id".to_string()),
                ],
                None,
                true,
                Some("orderQuery"),
                Some(&[vec![
                    ("symbol".to_string(), "BTC_USDC".to_string()),
                    ("orderId".to_string(), "test-order-id".to_string()),
                ]]),
                BTreeMap::new(),
                "1700000000000",
            )
            .expect("request");

        assert_eq!(
            request.headers.get("X-Signature").map(String::as_str),
            Some(
                "rzPMmBB/3emqFrFFImSTG2B42lnb/wa7k8+/5GEfCbPsnD4Ekp3i54huIhYxkkdH2wqP5nYxvMUEWaDp9l6ZAw=="
            )
        );
        assert_eq!(
            request.path,
            "/api/v1/order?symbol=BTC_USDC&orderId=test-order-id"
        );
    }
}
