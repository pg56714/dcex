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
            let value = crate::exchanges::schema::encode(
                &key,
                &raw,
                schema["type"].as_str().unwrap_or("string"),
            )?;
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
            self.validate_withdrawal(&value, endpoint.signed)?;
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
                super::super::withdrawals::withdrawal_message(&value, timestamp)?
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
    crate::exchanges::schema::validate_with(value, schema, field, true, false)
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
