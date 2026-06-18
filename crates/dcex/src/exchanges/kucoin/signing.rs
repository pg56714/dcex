use serde_json::Value;

use crate::crypto::hmac_sha256_base64;
use crate::http::{HttpMethod, HttpResponse};
use crate::{DcexError, Result};

pub(super) fn encrypted_passphrase(
    api_secret: Option<&str>,
    passphrase: Option<&str>,
) -> Result<Option<String>> {
    match (api_secret, passphrase) {
        (Some(api_secret), Some(passphrase)) => {
            hmac_sha256_base64(api_secret.as_bytes(), passphrase.as_bytes()).map(Some)
        }
        _ => Ok(None),
    }
}

pub(super) fn request_signature(
    api_secret: &str,
    timestamp: &str,
    method: HttpMethod,
    request_path: &str,
    body: &[u8],
) -> Result<String> {
    let canonical = format!(
        "{timestamp}{}{request_path}{}",
        http_method_name(method),
        String::from_utf8_lossy(body)
    );
    hmac_sha256_base64(api_secret.as_bytes(), canonical.as_bytes())
}

pub(super) fn validate_response(response: &HttpResponse) -> Result<Value> {
    let data = response.json()?;
    if data
        .as_object()
        .and_then(|object| object.get("code"))
        .and_then(Value::as_str)
        != Some("200000")
    {
        let code = data
            .as_object()
            .and_then(|object| object.get("code"))
            .map(json_value_string)
            .unwrap_or_else(|| "Unknown".to_string());
        let message = data
            .as_object()
            .and_then(|object| object.get("msg"))
            .and_then(Value::as_str)
            .unwrap_or("Unknown error");
        return Err(DcexError::HttpStatus {
            status: response.status,
            message: format!("KUCOIN API Error: [{code}] {message}"),
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

fn json_value_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.clone(),
        _ => value.to_string(),
    }
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
