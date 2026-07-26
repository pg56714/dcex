use std::sync::{Arc, Mutex};

use serde_json::Value;
use url::form_urlencoded;

use crate::crypto::hmac_sha256_hex;
use crate::exchange::{RequestSigner, ResponseValidator};
use crate::http::{HttpRequest, HttpResponse, RequestBody};
use crate::{DcexError, Result};

#[derive(Clone)]
pub(super) struct BinanceSigner {
    pub(super) api_key: String,
    pub(super) api_secret: String,
    pub(super) timestamp_offset_ms: Arc<Mutex<Option<i64>>>,
}

impl RequestSigner for BinanceSigner {
    fn sign(&self, request: &mut HttpRequest, timestamp_ms: u64) -> Result<()> {
        let timestamp_ms = self.adjust_timestamp(timestamp_ms)?;
        let params = match &mut request.body {
            RequestBody::Empty => &mut request.query,
            RequestBody::Form(params) => params,
            _ => {
                return Err(DcexError::InvalidInput(
                    "Binance signed requests require query or form parameters.".to_string(),
                ));
            }
        };
        if !params.iter().any(|(key, _)| key == "timestamp") {
            params.push(("timestamp".to_string(), timestamp_ms.to_string()));
        }
        if !params.iter().any(|(key, _)| key == "recvWindow") {
            params.push(("recvWindow".to_string(), "5000".to_string()));
        }
        let encoded = encode_params(params);
        let signature = hmac_sha256_hex(self.api_secret.as_bytes(), encoded.as_bytes())?;
        params.push(("signature".to_string(), signature));
        request
            .headers
            .insert("X-MBX-APIKEY".to_string(), self.api_key.clone());
        Ok(())
    }
}

impl BinanceSigner {
    fn adjust_timestamp(&self, timestamp_ms: u64) -> Result<u64> {
        let offset = self.timestamp_offset_ms.lock().map_err(|error| {
            DcexError::Runtime(format!("Binance timestamp offset lock poisoned: {error}"))
        })?;
        let Some(offset) = *offset else {
            return Ok(timestamp_ms);
        };
        Ok((timestamp_ms as i64 + offset).max(0) as u64)
    }
}

pub(super) struct BinanceResponseValidator;

impl ResponseValidator for BinanceResponseValidator {
    fn validate(&self, response: &HttpResponse) -> Result<Value> {
        let data = response.json()?;
        if let Some(object) = data.as_object() {
            if let Some(code) = object.get("code") {
                if json_value_string(code) != "200" {
                    let message = object
                        .get("msg")
                        .and_then(Value::as_str)
                        .unwrap_or("Unknown error");
                    return Err(DcexError::HttpStatus {
                        status: response.status,
                        message: format!(
                            "BINANCE API Error: [{}] {message}",
                            json_value_string(code)
                        ),
                        headers: response
                            .headers
                            .iter()
                            .map(|(key, value)| (key.clone(), value.clone()))
                            .collect(),
                    });
                }
            }
        }
        response.ensure_success()?;
        Ok(data)
    }
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

pub(super) fn json_value_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.clone(),
        _ => value.to_string(),
    }
}

pub(super) fn extract_server_time_ms(data: &Value) -> Option<u64> {
    data.as_object()
        .and_then(|object| object.get("serverTime"))
        .and_then(|value| match value {
            Value::Number(value) => value.as_u64(),
            Value::String(value) => value.parse().ok(),
            _ => None,
        })
}
