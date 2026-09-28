//! Affiliate and withdrawal requests from the official endpoint schemas.
use std::collections::BTreeMap;
use std::sync::OnceLock;

use ed25519_dalek::Signer;
use serde::Deserialize;
use serde_json::{Value, json};

use crate::exchange::ValidatedResponse;
use crate::exchanges::arcus::ArcusClient;
use crate::exchanges::arcus::signing::{legacy_signing_message, timestamp_ns};
use crate::http::{HttpMethod, HttpRequest};
use crate::{DcexError, Result};

#[derive(Deserialize)]
struct Endpoint {
    name: String,
    method: String,
    path: String,
    signed: bool,
    schema: Value,
}
static ENDPOINTS: OnceLock<Vec<Endpoint>> = OnceLock::new();
fn endpoint(name: &str) -> Option<&'static Endpoint> {
    ENDPOINTS
        .get_or_init(load_schemas)
        .iter()
        .find(|e| e.name == name)
}
pub(in crate::exchanges::arcus) fn handles(name: &str, public: bool) -> bool {
    endpoint(name).is_some_and(|e| public == (e.method == "GET" && !e.signed))
}
fn invalid(message: impl std::fmt::Display) -> DcexError {
    DcexError::InvalidInput(format!("Arcus: {message}"))
}

impl ArcusClient {
    pub(in crate::exchanges::arcus) async fn field_schema_request(
        &self,
        name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let endpoint = endpoint(name).ok_or_else(|| invalid("unknown schema endpoint"))?;
        let props = endpoint.schema["properties"]
            .as_object()
            .expect("embedded properties");
        let mut body = BTreeMap::new();
        for (key, raw) in params {
            let schema = props
                .get(&key)
                .ok_or_else(|| invalid(format!("unsupported parameter {key}")))?;
            let value = match schema["type"].as_str() {
                Some("integer") => raw
                    .parse::<i64>()
                    .map(Value::from)
                    .map_err(|_| invalid(format!("{key} requires an integer")))?,
                Some("object" | "array") => serde_json::from_str(&raw)
                    .map_err(|_| invalid(format!("{key} requires JSON")))?,
                _ => Value::String(raw),
            };
            if body.insert(key.clone(), value).is_some() {
                return Err(invalid(format!("duplicate parameter {key}")));
            }
        }
        let value = json!(body);
        validate(&value, &endpoint.schema, "request")?;
        if let (Some(start), Some(end)) = (
            value.get("from").and_then(Value::as_i64),
            value.get("to").and_then(Value::as_i64),
        ) && start > end
        {
            return Err(invalid("from must not exceed to"));
        }
        if endpoint.signed && endpoint.path.starts_with("/v1/affiliate/") {
            let address = value["address"]
                .as_str()
                .ok_or_else(|| invalid("address is required"))?;
            let configured = self
                .address
                .as_deref()
                .ok_or_else(|| invalid("configure the API key's master address"))?;
            if !address.eq_ignore_ascii_case(configured) {
                return Err(invalid("address must match the configured master address"));
            }
        }
        if endpoint.path == "/v1/withdraw" {
            let amount = value["amount"].as_str().expect("validated string");
            if !amount.bytes().all(|b| b.is_ascii_digit())
                || !amount.parse::<i64>().is_ok_and(|n| n > 0)
            {
                return Err(invalid(
                    "withdrawal amount must be a positive int64 quantum string",
                ));
            }
            if let Some(asset) = value.get("spotAssetId")
                && asset.as_u64().is_none_or(|n| n > u16::MAX as u64)
            {
                return Err(invalid("spotAssetId must be uint16"));
            }
            if endpoint.signed {
                let configured = self
                    .address
                    .as_deref()
                    .ok_or_else(|| invalid("configure the API key's master address"))?;
                let address = value["ethereumAddress"]
                    .as_str()
                    .expect("validated address");
                if !address.eq_ignore_ascii_case(configured)
                    || value
                        .get("accountIndex")
                        .and_then(Value::as_u64)
                        .unwrap_or(0)
                        != self.account_index as u64
                {
                    return Err(invalid(
                        "API withdrawal must match the configured address and account index",
                    ));
                }
            } else {
                for key in ["r", "s"] {
                    let raw = value["signature"][key]
                        .as_str()
                        .expect("validated signature");
                    let digits = raw.strip_prefix("0x").unwrap_or(raw);
                    if digits.bytes().all(|b| b == b'0') {
                        return Err(invalid("signature r/s must be nonzero"));
                    }
                }
            }
        }
        let method = if endpoint.method == "GET" {
            HttpMethod::Get
        } else {
            HttpMethod::Post
        };
        let mut request = HttpRequest::new(method, &self.base_url, &endpoint.path);
        if endpoint.method == "GET" {
            request.query = body
                .iter()
                .map(|(key, v)| {
                    (
                        key.clone(),
                        v.as_str()
                            .map(str::to_owned)
                            .unwrap_or_else(|| v.to_string()),
                    )
                })
                .collect();
        } else {
            request = request.json(value.clone());
        }
        if endpoint.signed {
            let key = self
                .signing_key
                .as_ref()
                .ok_or_else(|| invalid("API signing key is required"))?;
            let timestamp = timestamp_ns()?;
            let action = endpoint.path.rsplit('/').next().expect("endpoint action");
            let message = if endpoint.method == "GET" {
                // Signed affiliate reads explicitly omit the body and query from
                // the preimage: timestamp + final path segment (no trailing {}).
                format!("{timestamp}{action}").into_bytes()
            } else if endpoint.path == "/v1/withdraw" {
                let typed = BTreeMap::from([
                    (
                        "ad",
                        json!(
                            value["ethereumAddress"]
                                .as_str()
                                .expect("address")
                                .to_ascii_lowercase()
                        ),
                    ),
                    (
                        "ai",
                        json!(
                            value
                                .get("accountIndex")
                                .and_then(Value::as_u64)
                                .unwrap_or(0)
                        ),
                    ),
                    ("ct", json!(timestamp)),
                    ("n", value["nonce"].clone()),
                    ("op", json!(5)),
                    (
                        "q",
                        json!(
                            value["amount"]
                                .as_str()
                                .expect("amount")
                                .parse::<i64>()
                                .expect("validated")
                        ),
                    ),
                    ("v", json!(1)),
                ]);
                serde_json::to_vec(&typed).map_err(invalid)?
            } else {
                legacy_signing_message(timestamp, action, &body)?
            };
            request = request
                .header("X-API-Key", hex::encode(key.verifying_key().to_bytes()))
                .header("X-Timestamp", timestamp.to_string())
                .header("X-Signature", hex::encode(key.sign(&message).to_bytes()));
        }
        self.execute(request).await
    }
}

fn validate(value: &Value, schema: &Value, field: &str) -> Result<()> {
    if let Some(choices) = schema["enum"].as_array()
        && !choices.contains(value)
    {
        return Err(invalid(format!("invalid {field}")));
    }
    match schema["type"].as_str() {
        Some("object") => {
            let object = value
                .as_object()
                .ok_or_else(|| invalid(format!("{field} must be an object")))?;
            let props = schema["properties"]
                .as_object()
                .ok_or_else(|| invalid("invalid embedded schema"))?;
            for required in schema["required"]
                .as_array()
                .into_iter()
                .flatten()
                .filter_map(Value::as_str)
            {
                if !object.contains_key(required) {
                    return Err(invalid(format!("{field}.{required} is required")));
                }
            }
            for (key, v) in object {
                validate(
                    v,
                    props
                        .get(key)
                        .ok_or_else(|| invalid(format!("unknown {field}.{key}")))?,
                    &format!("{field}.{key}"),
                )?;
            }
        }
        Some("string") => {
            let text = value
                .as_str()
                .ok_or_else(|| invalid(format!("{field} requires a string")))?;
            if schema["minLength"]
                .as_u64()
                .is_some_and(|n| text.chars().count() < (n as usize))
                || schema["maxLength"]
                    .as_u64()
                    .is_some_and(|n| text.chars().count() > (n as usize))
            {
                return Err(invalid(format!("invalid {field} length")));
            }
            if let Some(pattern) = schema["pattern"].as_str() {
                // Nonzero signature scalars are checked separately above; Rust
                // regex intentionally does not support the OpenAPI lookahead.
                let pattern = pattern.replace("(?=.*[1-9a-fA-F])", "");
                let regex =
                    regex::Regex::new(&pattern).map_err(|_| invalid("invalid embedded pattern"))?;
                if !regex.is_match(text) {
                    return Err(invalid(format!("invalid {field} format")));
                }
            }
        }
        Some("integer") => {
            let n = value
                .as_i64()
                .ok_or_else(|| invalid(format!("{field} requires an integer")))?;
            if schema["minimum"].as_i64().is_some_and(|min| n < min)
                || schema["maximum"].as_i64().is_some_and(|max| n > max)
            {
                return Err(invalid(format!("{field} is outside documented limits")));
            }
        }
        _ => return Err(invalid("unsupported embedded field type")),
    }
    Ok(())
}

fn load_schemas() -> Vec<Endpoint> {
    [
        include_str!("../schemas/withdrawals.json"),
        include_str!("../schemas/account.json"),
        include_str!("../schemas/affiliate.json"),
    ]
    .into_iter()
    .flat_map(|raw| serde_json::from_str::<Vec<Endpoint>>(raw).expect("checked endpoint schemas"))
    .collect()
}
