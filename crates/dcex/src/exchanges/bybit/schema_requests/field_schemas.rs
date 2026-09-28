//! Additional V5 endpoints, keyed by reviewed official request schemas.
use crate::exchange::ValidatedResponse;
use crate::exchanges::bybit::{client::BybitClient, params::BybitParams};
use crate::http::HttpMethod;
use crate::{DcexError, Result};
use serde::Deserialize;
use serde_json::{Map, Value};
use std::collections::{HashMap, HashSet};
use std::sync::OnceLock;

#[derive(Deserialize)]
struct Field {
    name: String,
    #[serde(rename = "type")]
    kind: String,
    required: bool,
}

#[derive(Deserialize)]
struct Endpoint {
    name: String,
    method: String,
    path: String,
    public: bool,
    fields: Vec<Field>,
}

fn endpoints() -> &'static HashMap<String, Endpoint> {
    static CACHE: OnceLock<HashMap<String, Endpoint>> = OnceLock::new();
    CACHE.get_or_init(|| {
        let items: Vec<Endpoint> = load_schemas();
        items.into_iter().map(|e| (e.name.clone(), e)).collect()
    })
}

impl BybitClient {
    pub(in crate::exchanges::bybit) async fn field_schema_request(
        &self,
        name: &str,
        params: &BybitParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        let Some(endpoint) = endpoints().get(name).filter(|e| e.public == public) else {
            return Ok(None);
        };
        let pairs = params.without(&[]);
        let mut seen = HashSet::new();
        let mut body = Map::new();
        for (key, raw) in &pairs {
            let field = endpoint
                .fields
                .iter()
                .find(|f| &f.name == key)
                .ok_or_else(|| invalid(format!("unknown parameter: {key}")))?;
            if !seen.insert(key) || (field.required && raw.trim().is_empty()) {
                return Err(invalid(format!("duplicate or empty parameter: {key}")));
            }
            let value = match field.kind.as_str() {
                "integer" | "int" | "int64" | "long" => Value::from(
                    raw.parse::<i64>()
                        .map_err(|_| invalid(format!("{key} requires an integer")))?,
                ),
                "boolean" => Value::Bool(
                    raw.parse::<bool>()
                        .map_err(|_| invalid(format!("{key} requires a boolean")))?,
                ),
                kind if kind.starts_with("array") || kind == "object" => {
                    let value: Value = serde_json::from_str(raw)
                        .map_err(|_| invalid(format!("{key} requires valid JSON")))?;
                    if (kind.starts_with("array") && !value.is_array())
                        || (kind == "object" && !value.is_object())
                    {
                        return Err(invalid(format!("{key} has the wrong JSON type")));
                    }
                    value
                }
                "string" => Value::String(raw.clone()),
                _ => return Err(invalid("unsupported schema type")),
            };
            body.insert(key.clone(), value);
        }
        for field in &endpoint.fields {
            if field.required && !body.contains_key(&field.name) {
                return Err(invalid(format!("{} is required", field.name)));
            }
        }
        validate_conditions(&endpoint.path, &body)?;
        let result = if endpoint.method == "GET" {
            self.request(HttpMethod::Get, &endpoint.path, pairs, None, !public)
                .await?
        } else {
            let bytes = serde_json::to_vec(&body).map_err(|e| DcexError::Decode(e.to_string()))?;
            self.request(
                HttpMethod::Post,
                &endpoint.path,
                vec![],
                Some(bytes),
                !public,
            )
            .await?
        };
        Ok(Some(result))
    }
}

fn validate_conditions(path: &str, body: &Map<String, Value>) -> Result<()> {
    let text = |key: &str| body.get(key).and_then(Value::as_str);
    let require = |key: &str| {
        if body.contains_key(key) {
            Ok(())
        } else {
            Err(invalid(format!("{key} is required")))
        }
    };
    if path == "/v5/asset/withdraw/create" {
        if body.get("forceChain").and_then(Value::as_i64) != Some(2) {
            require("chain")?;
        }
        if !text("amount").is_some_and(crate::common::is_positive_plain_decimal) {
            return Err(invalid("amount requires a positive plain decimal string"));
        }
    }
    if path == "/v5/rwa/stocks/order" {
        if body.contains_key("qty") && body.contains_key("notional") {
            return Err(invalid("qty and notional are mutually exclusive"));
        }
        if text("side") == Some("SELL") || text("type") != Some("MARKET") {
            require("qty")?;
            if body.contains_key("notional") {
                return Err(invalid("notional requires a market buy"));
            }
        } else if !body.contains_key("qty") {
            require("notional")?;
        }
        if matches!(text("type"), Some("LIMIT" | "STOP_LIMIT")) {
            require("limitPrice")?;
        }
        if matches!(text("type"), Some("STOP" | "STOP_LIMIT")) {
            require("stopPrice")?;
        }
        if text("tradingSession") == Some("24H") && text("type") != Some("LIMIT") {
            return Err(invalid("24H trading requires a limit order"));
        }
        if text("side") == Some("SELL") && text("timeInForce") == Some("IOC") {
            return Err(invalid("SELL does not support IOC"));
        }
    }
    Ok(())
}

fn invalid(message: impl Into<String>) -> DcexError {
    DcexError::InvalidInput(format!("Bybit: {}", message.into()))
}

fn load_schemas() -> Vec<Endpoint> {
    [
        include_str!("../schemas/trading.json"),
        include_str!("../schemas/account.json"),
        include_str!("../schemas/affiliate.json"),
        include_str!("../schemas/alpha.json"),
        include_str!("../schemas/fiat.json"),
        include_str!("../schemas/withdrawals.json"),
        include_str!("../schemas/bots.json"),
        include_str!("../schemas/broker.json"),
        include_str!("../schemas/card.json"),
        include_str!("../schemas/event.json"),
        include_str!("../schemas/file_upload.json"),
        include_str!("../schemas/pwm.json"),
        include_str!("../schemas/leveraged_tokens.json"),
        include_str!("../schemas/loan.json"),
        include_str!("../schemas/convert.json"),
        include_str!("../schemas/stocks.json"),
        include_str!("../schemas/compliance.json"),
        include_str!("../schemas/referral.json"),
        include_str!("../schemas/subaccount.json"),
    ]
    .into_iter()
    .flat_map(|raw| serde_json::from_str::<Vec<Endpoint>>(raw).expect("checked endpoint schemas"))
    .collect()
}
