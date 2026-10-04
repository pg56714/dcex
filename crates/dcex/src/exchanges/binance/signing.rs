use std::sync::{Arc, Mutex};

use serde_json::Value;

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
        let literal_brackets = request.path == "/sapi/v1/w3w/wallet/prediction/trade/batch-cancel";
        let params = match &mut request.body {
            RequestBody::Empty => &mut request.query,
            RequestBody::Json(_)
                if matches!(
                    request.path.as_str(),
                    "/sapi/v1/fiat/deposit" | "/sapi/v2/fiat/withdraw"
                ) =>
            {
                &mut request.query
            }
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
        let encoded = crate::exchanges::schema::form(params, literal_brackets);
        let signature = hmac_sha256_hex(self.api_secret.as_bytes(), encoded.as_bytes())?;
        params.push(("signature".to_string(), signature));
        if literal_brackets {
            let body = crate::exchanges::schema::form(params, true).into_bytes();
            request.body = RequestBody::Raw(body);
            request.headers.insert(
                "Content-Type".into(),
                "application/x-www-form-urlencoded".into(),
            );
        }
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
        if let Some(object) = data.as_object()
            && let Some(code) = object.get("code")
            && json_value_string(code) != "200"
        {
            let message = object.get("msg").and_then(Value::as_str).unwrap_or("");
            let code = json_value_string(code);
            let message =
                crate::http::api_error_message("Binance", response.status, Some(&code), message);
            let headers = response.header_pairs();
            if let Some(outcomes) = object
                .get("data")
                .filter(|v| v.get("cancelResult").is_some() || v.get("newOrderResult").is_some())
            {
                return Err(DcexError::ExchangeResponse {
                    status: response.status,
                    message,
                    headers,
                    data: outcomes.clone(),
                });
            }
            return Err(DcexError::HttpStatus {
                status: response.status,
                message,
                headers,
            });
        }
        response.ensure_success("Binance")?;
        Ok(data)
    }
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

#[cfg(test)]
mod partial_order_tests {
    use super::*;
    #[test]
    fn cancel_replace_partial_failure_retains_both_results() {
        let outcomes = serde_json::json!({"cancelResult":"SUCCESS","newOrderResult":"FAILURE","cancelResponse":{"orderId":123,"status":"CANCELED"},"newOrderResponse":{"code":-2010,"msg":"insufficient balance"}});
        let response=HttpResponse{status:409,headers:std::collections::BTreeMap::from([("x-mbx-used-weight-1m".into(),"12".into())]),body:serde_json::to_vec(&serde_json::json!({"code":-2021,"msg":"Order cancel-replace partially failed.","data":outcomes})).unwrap()};
        let error = BinanceResponseValidator.validate(&response).unwrap_err();
        let DcexError::ExchangeResponse {
            status,
            headers,
            data,
            ..
        } = error
        else {
            panic!("expected exchange error");
        };
        assert_eq!(status, 409);
        assert_eq!(data, outcomes);
        assert!(
            headers
                .iter()
                .any(|(key, value)| key == "x-mbx-used-weight-1m" && value == "12")
        );
    }
}
