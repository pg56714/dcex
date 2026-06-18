use serde_json::Value;
use url::form_urlencoded;

use crate::crypto::hmac_sha256_base64;
use crate::http::{HttpMethod, HttpResponse};
use crate::{DcexError, Result};

pub(super) fn validate_response(response: &HttpResponse) -> Result<Value> {
    let data = response.json()?;
    let code = data
        .as_object()
        .and_then(|object| object.get("code"))
        .map(json_value_string)
        .unwrap_or_default();
    if code != "00000" {
        let message = data
            .as_object()
            .and_then(|object| object.get("msg").or_else(|| object.get("message")))
            .and_then(Value::as_str)
            .unwrap_or("Unknown error");
        return Err(DcexError::HttpStatus {
            status: response.status,
            message: format!("Bitget API Error: [{code}] {message}"),
            headers: response
                .headers
                .iter()
                .map(|(key, value)| (key.clone(), value.clone()))
                .collect(),
        });
    }
    response.ensure_success()?;
    Ok(data)
}

pub(super) fn sign(
    timestamp: u64,
    method: HttpMethod,
    path: &str,
    query_string: &str,
    body: &[u8],
    api_secret: &str,
) -> Result<String> {
    let request_path = if query_string.is_empty() {
        path.to_string()
    } else {
        format!("{path}?{query_string}")
    };
    let payload = format!(
        "{timestamp}{}{request_path}{}",
        http_method_name(method),
        String::from_utf8_lossy(body)
    );
    hmac_sha256_base64(api_secret.as_bytes(), payload.as_bytes())
}

pub(super) fn encode_params(params: &[(String, String)]) -> String {
    let mut serializer = form_urlencoded::Serializer::new(String::new());
    serializer.extend_pairs(
        params
            .iter()
            .map(|(key, value)| (key.as_str(), value.as_str())),
    );
    serializer.finish()
}

pub(super) const fn http_method_name(method: HttpMethod) -> &'static str {
    match method {
        HttpMethod::Delete => "DELETE",
        HttpMethod::Get => "GET",
        HttpMethod::Patch => "PATCH",
        HttpMethod::Post => "POST",
        HttpMethod::Put => "PUT",
    }
}

fn json_value_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.clone(),
        _ => value.to_string(),
    }
}
