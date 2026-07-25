use std::time::{SystemTime, UNIX_EPOCH};

use base64::Engine;
use serde_json::Value;

use crate::crypto::{hmac_sha512_base64, sha256};
use crate::http::{HttpMethod, HttpResponse};
use crate::{DcexError, Result};

pub(super) fn validate_response(response: &HttpResponse) -> Result<Value> {
    response.ensure_success()?;
    let data = response.json()?;
    if let Some(message) = kraken_error_message(&data) {
        return Err(DcexError::HttpStatus {
            status: response.status,
            message,
            headers: response
                .headers
                .iter()
                .map(|(key, value)| (key.clone(), value.clone()))
                .collect(),
        });
    }
    Ok(data)
}

fn kraken_error_message(data: &Value) -> Option<String> {
    let object = data.as_object()?;
    match object.get("error") {
        Some(Value::Array(errors)) if !errors.is_empty() => {
            return Some(
                errors
                    .iter()
                    .map(json_value_string)
                    .collect::<Vec<_>>()
                    .join(", "),
            );
        }
        Some(Value::String(error)) if !error.is_empty() => return Some(error.clone()),
        _ => {}
    }
    if object.get("result").and_then(Value::as_str) == Some("error") {
        let message = object
            .get("errors")
            .or_else(|| object.get("error"))
            .map(json_value_string)
            .unwrap_or_else(|| "Kraken API error".to_string());
        return Some(message);
    }
    None
}

fn json_value_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.clone(),
        Value::Array(values) => values
            .iter()
            .map(json_value_string)
            .collect::<Vec<_>>()
            .join(", "),
        _ => value.to_string(),
    }
}

pub(super) fn encode_params(params: &[(String, String)]) -> String {
    url::form_urlencoded::Serializer::new(String::new())
        .extend_pairs(
            params
                .iter()
                .map(|(key, value)| (key.as_str(), value.as_str())),
        )
        .finish()
        .replace('+', "%20")
}

fn decode_secret(api_secret: &str) -> Result<Vec<u8>> {
    base64::engine::general_purpose::STANDARD
        .decode(api_secret)
        .map_err(|error| DcexError::InvalidInput(format!("invalid Kraken API secret: {error}")))
}

pub(super) fn spot_signature(
    path: &str,
    nonce: &str,
    encoded_payload: &str,
    api_secret: &str,
) -> Result<String> {
    let digest = sha256(format!("{nonce}{encoded_payload}").as_bytes());
    let mut message = Vec::with_capacity(path.len() + digest.len());
    message.extend_from_slice(path.as_bytes());
    message.extend_from_slice(&digest);
    hmac_sha512_base64(&decode_secret(api_secret)?, &message)
}

pub(super) fn futures_signature(
    path: &str,
    post_data: &str,
    nonce: &str,
    api_secret: &str,
) -> Result<String> {
    let auth_path = path.strip_prefix("/derivatives").unwrap_or(path);
    let digest = sha256(format!("{post_data}{nonce}{auth_path}").as_bytes());
    hmac_sha512_base64(&decode_secret(api_secret)?, &digest)
}

pub(super) fn unix_timestamp_ns() -> Result<u128> {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|duration| duration.as_nanos())
        .map_err(|error| DcexError::Runtime(error.to_string()))
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
