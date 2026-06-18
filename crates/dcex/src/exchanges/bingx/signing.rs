use serde_json::{json, Value};

use crate::crypto::hmac_sha256_hex;
use crate::exchange::{RequestSigner, ResponseValidator};
use crate::http::{HttpRequest, HttpResponse};
use crate::{DcexError, Result};

#[derive(Clone)]
pub(super) struct BingxSigner {
    pub(super) api_key: String,
    pub(super) api_secret: String,
}

impl RequestSigner for BingxSigner {
    fn sign(&self, request: &mut HttpRequest, timestamp_ms: u64) -> Result<()> {
        request.query.sort_by(|left, right| left.0.cmp(&right.0));
        request
            .query
            .push(("timestamp".to_string(), timestamp_ms.to_string()));
        let payload = request
            .query
            .iter()
            .map(|(key, value)| format!("{key}={value}"))
            .collect::<Vec<_>>()
            .join("&");
        let signature = hmac_sha256_hex(self.api_secret.as_bytes(), payload.as_bytes())?;
        request.query.push(("signature".to_string(), signature));
        request
            .headers
            .insert("X-BX-APIKEY".to_string(), self.api_key.clone());
        Ok(())
    }
}

pub(super) struct BingxResponseValidator;

impl ResponseValidator for BingxResponseValidator {
    fn validate(&self, response: &HttpResponse) -> Result<Value> {
        let data = if response.body.is_empty() {
            json!({"code": 0})
        } else {
            response.json()?
        };
        let code = data
            .as_object()
            .and_then(|object| object.get("code"))
            .map(json_value_string)
            .unwrap_or_else(|| "0".to_string());
        if code != "0" {
            let message = data
                .as_object()
                .and_then(|object| object.get("msg"))
                .and_then(Value::as_str)
                .unwrap_or("Unknown error");
            return Err(DcexError::HttpStatus {
                status: response.status,
                message: format!("BingX API Error: [{code}] {message}"),
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
}

pub(super) fn json_value_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.clone(),
        Value::Number(value) => value.to_string(),
        Value::Bool(value) => value.to_string(),
        Value::Null => String::new(),
        Value::Array(_) | Value::Object(_) => value.to_string(),
    }
}
