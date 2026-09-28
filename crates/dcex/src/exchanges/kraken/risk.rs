//! Authenticated depth, account history and transfers within an account family.
use super::client::{KrakenAuth, KrakenClient};
use super::params::KrakenParams;
use super::risk_endpoints::ENDPOINTS;
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

pub(super) struct Field {
    pub key: &'static str,
    pub kind: &'static str,
    pub required: bool,
    pub values: &'static [&'static str],
    pub minimum: u64,
}
pub(super) struct Endpoint {
    pub name: &'static str,
    pub path: &'static str,
    pub method: HttpMethod,
    pub auth: KrakenAuth,
    pub public: bool,
    pub allowed: &'static [&'static str],
    pub fields: &'static [Field],
    pub symbol_key: Option<&'static str>,
}
fn invalid(message: impl std::fmt::Display) -> DcexError {
    DcexError::InvalidInput(format!("Kraken: {message}"))
}
impl KrakenClient {
    pub(super) async fn risk_request(
        &self,
        name: &str,
        params: &KrakenParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        let Some(endpoint) = ENDPOINTS
            .iter()
            .find(|e| e.name == name && e.public == public)
        else {
            return Ok(None);
        };
        params.ensure_allowed(endpoint.allowed)?;
        let mut query = Vec::new();
        let mut path = endpoint.path.to_string();
        for field in endpoint.fields {
            let canonical = if endpoint.symbol_key == Some(field.key) {
                params.get("product_symbol")
            } else {
                None
            };
            if canonical.is_some() && params.get(field.key).is_some() {
                return Err(invalid("use product_symbol or native symbol, exclusively"));
            }
            let value = canonical.or_else(|| params.get(field.key));
            let Some(value) = value else {
                if field.required {
                    return Err(invalid(format!("{} is required", field.key)));
                }
                continue;
            };
            if value.trim().is_empty() {
                return Err(invalid(format!("{} cannot be empty", field.key)));
            }
            if !field.values.is_empty() && field.kind != "array" && !field.values.contains(&value) {
                return Err(invalid(format!("invalid {}", field.key)));
            }
            match field.kind {
                "signed_integer" => {
                    value
                        .parse::<i32>()
                        .map_err(|_| invalid("userref must be an int32"))?;
                }
                "positive" => {
                    if !value.parse::<f64>().is_ok_and(|v| v.is_finite() && v > 0.0) {
                        return Err(invalid(format!("{} must be positive", field.key)));
                    }
                }
                "integer" => {
                    if !value.parse::<u64>().is_ok_and(|v| v >= field.minimum) {
                        return Err(invalid(format!("invalid {} integer", field.key)));
                    }
                }
                "boolean" => {
                    value
                        .parse::<bool>()
                        .map_err(|_| invalid(format!("{} must be true or false", field.key)))?;
                }
                "array" => {
                    let values: Vec<String> = serde_json::from_str(value)
                        .map_err(|_| invalid("array filters must be JSON string arrays"))?;
                    if values.is_empty() {
                        return Err(invalid("filter arrays cannot be empty"));
                    }
                    for value in values {
                        if value.is_empty()
                            || !field.values.is_empty() && !field.values.contains(&value.as_str())
                        {
                            return Err(invalid(format!("invalid {} filter", field.key)));
                        }
                        // OpenAPI form/explode query arrays use repeated keys.
                        query.push((field.key.to_string(), value));
                    }
                    continue;
                }
                _ => {}
            }
            let value = if canonical.is_some() {
                self.exchange_symbol(
                    value,
                    if endpoint.auth == KrakenAuth::Futures {
                        "PF_"
                    } else {
                        ""
                    },
                )?
            } else {
                value.into()
            };
            let placeholder = format!("{{{}}}", field.key);
            if path.contains(&placeholder) {
                if !value
                    .bytes()
                    .all(|b| b.is_ascii_alphanumeric() || b == b'_' || b == b'.' || b == b'-')
                {
                    return Err(invalid("invalid path identifier"));
                }
                path = path.replace(&placeholder, &value);
            } else {
                query.push((field.key.to_string(), value));
            }
        }
        if name == "edit_spot_order" && params.required("txid")?.contains(',') {
            return Err(invalid("EditOrder requires one order identifier"));
        }
        if let Some(ids) = params.get("txid") {
            let ids: Vec<_> = ids.split(',').collect();
            if ids.len() > 20 || ids.iter().any(|v| v.trim().is_empty()) {
                return Err(invalid("txid requires 1..=20 transaction identifiers"));
            }
        }
        if name == "get_spot_ledger_entries" {
            let ids: Vec<_> = params.required("id")?.split(',').collect();
            if ids.len() > 20 || ids.iter().any(|id| id.trim().is_empty()) {
                return Err(invalid("id requires 1..=20 ledger identifiers"));
            }
        }
        if let Some(amount) = params.get("amount")
            && !amount
                .parse::<f64>()
                .is_ok_and(|v| v.is_finite() && v > 0.0)
        {
            return Err(invalid("amount must be positive"));
        }
        if name == "get_spot_deposit_addresses"
            && params.get("method") == Some("Bitcoin Lightning")
            && params.get("amount").is_none()
        {
            return Err(invalid("Bitcoin Lightning requires amount"));
        }
        for (start, end) in [("since", "before"), ("from", "to")] {
            if name.starts_with("get_futures_")
                && let (Some(a), Some(b)) = (params.get(start), params.get(end))
                && a.parse::<u64>().map_err(invalid)? > b.parse::<u64>().map_err(invalid)?
            {
                return Err(invalid(format!("{start} must not exceed {end}")));
            }
        }
        if name == "simulate_futures_portfolio" {
            let body: serde_json::Value = serde_json::from_str(params.required("json")?)
                .map_err(|_| invalid("portfolio must be valid JSON"))?;
            if body.as_object().is_none_or(|o| o.len() != 1) {
                return Err(invalid("portfolio must contain only positions"));
            }
            let positions = body["positions"]
                .as_array()
                .filter(|v| v.len() <= 500)
                .ok_or_else(|| invalid("positions must be an array of at most 500 entries"))?;
            for position in positions {
                if position.as_object().is_none_or(|o| o.len() != 3)
                    || position["instrument"].as_str().is_none_or(|v| v.is_empty())
                    || !position["size"].as_f64().is_some_and(f64::is_finite)
                    || !position["entryPrice"]
                        .as_f64()
                        .is_some_and(|v| v.is_finite() && v >= 0.0)
                {
                    return Err(invalid("invalid portfolio position"));
                }
            }
        }
        if let (Some(start), Some(end)) = (params.get("starttm"), params.get("endtm"))
            && start.parse::<u64>().map_err(invalid)? > end.parse::<u64>().map_err(invalid)?
        {
            return Err(invalid("starttm must not exceed endtm"));
        }
        if name == "get_spot_post_trade_data"
            && params
                .get("count")
                .is_some_and(|v| v.parse::<u64>().is_ok_and(|n| n > 1000))
        {
            return Err(invalid("count must not exceed 1000"));
        }
        let result = if name == "get_futures_account_log_csv" {
            let response = self
                .request_raw(endpoint.method, endpoint.auth, path, query, None, true)
                .await?;
            response.ensure_success()?;
            // Preserve CSV verbatim, while exposing the usual status/header envelope.
            let text = response.text()?;
            if text.trim_start().starts_with('{') {
                super::signing::validate_response(&response)?;
            }
            let data = serde_json::Value::String(text);
            ValidatedResponse {
                status: response.status,
                headers: response.headers,
                data,
            }
        } else {
            self.request(endpoint.method, endpoint.auth, path, query, None, !public)
                .await?
        };
        Ok(Some(result))
    }
}

impl KrakenClient {
    /// Download a completed Spot export as ZIP bytes, validating JSON error responses.
    pub async fn retrieve_spot_export(&self, id: impl Into<String>) -> Result<Vec<u8>> {
        let id = id.into();
        if id.trim().is_empty() {
            return Err(invalid("report id is required"));
        }
        let response = self
            .request_raw(
                HttpMethod::Post,
                KrakenAuth::Spot,
                "/0/private/RetrieveExport",
                vec![("id".into(), id)],
                None,
                true,
            )
            .await?;
        response.ensure_success()?;
        if response
            .headers
            .iter()
            .any(|(k, v)| k.eq_ignore_ascii_case("content-type") && v.contains("json"))
            || response.body.iter().find(|b| !b.is_ascii_whitespace()) == Some(&b'{')
        {
            super::signing::validate_response(&response)?;
            return Err(crate::DcexError::Decode(
                "Kraken export returned JSON instead of ZIP bytes".into(),
            ));
        }
        if !response.body.starts_with(b"PK") {
            return Err(crate::DcexError::Decode(
                "Kraken export did not return a ZIP archive".into(),
            ));
        }
        Ok(response.body)
    }
}
