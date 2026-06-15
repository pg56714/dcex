use std::collections::BTreeMap;
use std::time::Duration;

use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::http::{block_on, AsyncHttpClient, HttpMethod, HttpRequest, HttpResponse, RequestBody};
use crate::{DcexError, Result};

const BASE_URL: &str = "https://mainnet.zklighter.elliot.ai";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum LighterContentType {
    Form,
    Json,
}

#[derive(Clone)]
pub struct LighterClient {
    transport: AsyncHttpClient,
    base_url: String,
}

impl LighterClient {
    pub fn new(timeout: Duration) -> Result<Self> {
        Self::with_base_url(timeout, BASE_URL.to_string())
    }

    pub fn with_base_url(timeout: Duration, base_url: String) -> Result<Self> {
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            base_url,
        })
    }

    #[allow(clippy::too_many_arguments)]
    pub async fn request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Vec<(String, String)>,
        signed: bool,
        headers: BTreeMap<String, String>,
        content_type: LighterContentType,
    ) -> Result<ValidatedResponse> {
        let response = self
            .request_raw(method, path, params, body, signed, headers, content_type)
            .await?;
        let data = validate_response(&response)?;
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
        body: Vec<(String, String)>,
        signed: bool,
        headers: BTreeMap<String, String>,
        content_type: LighterContentType,
    ) -> Result<HttpResponse> {
        let request =
            self.build_request(method, path, params, body, signed, headers, content_type)?;
        self.transport.execute(request).await
    }

    #[allow(clippy::too_many_arguments)]
    pub fn request_raw_blocking(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Vec<(String, String)>,
        signed: bool,
        headers: BTreeMap<String, String>,
        content_type: LighterContentType,
    ) -> Result<HttpResponse> {
        let client = self.clone();
        let path = path.into();
        block_on(async move {
            client
                .request_raw(method, path, params, body, signed, headers, content_type)
                .await
        })
    }

    pub async fn public_request(
        &self,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        headers: BTreeMap<String, String>,
    ) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            path,
            params,
            Vec::new(),
            false,
            headers,
            LighterContentType::Json,
        )
        .await
    }

    #[allow(clippy::too_many_arguments)]
    fn build_request(
        &self,
        method: HttpMethod,
        path: impl Into<String>,
        params: Vec<(String, String)>,
        body: Vec<(String, String)>,
        signed: bool,
        headers: BTreeMap<String, String>,
        content_type: LighterContentType,
    ) -> Result<HttpRequest> {
        if signed {
            return Err(DcexError::InvalidInput(
                "Signed Lighter requests are not implemented yet.".to_string(),
            ));
        }
        if !matches!(method, HttpMethod::Get | HttpMethod::Post) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Lighter HTTP method: {}",
                http_method_name(method)
            )));
        }

        let path = path.into();
        let query = encode_params(&params);
        let request_path = if query.is_empty() {
            path
        } else {
            format!("{path}?{query}")
        };
        let content_type = match content_type {
            LighterContentType::Form => "application/x-www-form-urlencoded",
            LighterContentType::Json => "application/json",
        };
        let mut request = HttpRequest::new(method, &self.base_url, request_path)
            .header("Content-Type", content_type);
        request.headers.extend(headers);
        if method == HttpMethod::Post && !body.is_empty() {
            request.body = RequestBody::Raw(encode_params(&body).into_bytes());
        }
        Ok(request)
    }
}

fn validate_response(response: &HttpResponse) -> Result<Value> {
    response.ensure_success()?;
    let data = response.json()?;
    if let Some(object) = data.as_object() {
        let code = object.get("code");
        if code.is_some_and(|code| !matches!(json_value_string(code).as_str(), "0" | "200")) {
            let message = object
                .get("message")
                .or_else(|| object.get("msg"))
                .map(json_value_string)
                .unwrap_or_else(|| "Unknown error".to_string());
            return Err(DcexError::HttpStatus {
                status: response.status,
                message: format!(
                    "Lighter API Error: [{}] {message}",
                    code.map(json_value_string)
                        .unwrap_or_else(|| "Unknown".to_string())
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

fn json_value_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.clone(),
        _ => value.to_string(),
    }
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
    fn request_matches_python_encoding() {
        let client = LighterClient::new(Duration::from_secs(1)).expect("client");
        let request = client
            .build_request(
                HttpMethod::Post,
                "/api/v1/sendTx",
                vec![("account_index".to_string(), "1".to_string())],
                vec![
                    ("tx_type".to_string(), "14".to_string()),
                    ("tx_info".to_string(), r#"{"Price":100}"#.to_string()),
                ],
                false,
                BTreeMap::new(),
                LighterContentType::Form,
            )
            .expect("request");

        assert_eq!(request.path, "/api/v1/sendTx?account_index=1");
        assert_eq!(
            request.body,
            RequestBody::Raw(b"tx_type=14&tx_info=%7B%22Price%22%3A100%7D".to_vec())
        );
    }
}
