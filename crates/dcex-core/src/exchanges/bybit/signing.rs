use serde_json::Value;
use url::form_urlencoded;

use crate::http::HttpResponse;
use crate::{DcexError, Result};

pub(super) fn encode_params(params: &[(String, String)]) -> String {
    let mut serializer = form_urlencoded::Serializer::new(String::new());
    serializer.extend_pairs(
        params
            .iter()
            .map(|(key, value)| (key.as_str(), value.as_str())),
    );
    serializer.finish()
}

pub(super) fn extract_server_time_ms(data: &Value) -> Option<u64> {
    if let Some(value) = data.get("time").and_then(json_u64) {
        return Some(value);
    }
    let result = data.get("result")?.as_object()?;
    if let Some(value) = result.get("timeNano").and_then(json_u64) {
        return Some(value / 1_000_000);
    }
    result
        .get("timeSecond")
        .and_then(json_u64)
        .map(|value| value * 1_000)
}

fn json_u64(value: &Value) -> Option<u64> {
    value
        .as_u64()
        .or_else(|| value.as_str().and_then(|value| value.parse().ok()))
}

pub(super) fn validate_response(response: &HttpResponse) -> Result<Value> {
    let data = response.json()?;
    let code = data
        .as_object()
        .and_then(|object| object.get("retCode"))
        .map(json_value_string)
        .unwrap_or_else(|| "0".to_string());
    if code != "0" {
        let message = data
            .as_object()
            .and_then(|object| object.get("retMsg"))
            .and_then(Value::as_str)
            .unwrap_or("Unknown error");
        return Err(DcexError::HttpStatus {
            status: response.status,
            message: format!("Bybit API Error: [{code}] {message}"),
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
