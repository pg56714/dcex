use serde_json::Value;

use crate::http::HttpResponse;
use crate::{DcexError, Result};

pub(super) fn validate_response(response: &HttpResponse) -> Result<Value> {
    let data = response.json()?;
    let code = data
        .as_object()
        .and_then(|object| object.get("code"))
        .map(json_value_string)
        .unwrap_or_else(|| "0".to_string());
    if code != "1000" {
        let message = data
            .as_object()
            .and_then(|object| object.get("msg").or_else(|| object.get("message")))
            .and_then(Value::as_str)
            .unwrap_or("Unknown error");
        return Err(DcexError::HttpStatus {
            status: response.status,
            message: format!("BitMart API Error: [{code}] {message}"),
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

pub(super) fn json_value_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.clone(),
        _ => value.to_string(),
    }
}
