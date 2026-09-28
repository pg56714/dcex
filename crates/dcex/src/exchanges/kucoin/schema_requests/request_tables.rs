//! Official affiliate, broker and copy-trading request schemas.
use crate::exchanges::kucoin::{KucoinClient, KucoinMarket, params::KucoinParams};
use crate::{DcexError, Result, exchange::ValidatedResponse, http::HttpMethod};
use serde::Deserialize;
use serde_json::{Map, Value};
use std::sync::OnceLock;

#[derive(Deserialize)]
struct Field {
    name: String,
    required: bool,
    location: String,
    schema: Value,
}
#[derive(Deserialize)]
struct Endpoint {
    name: String,
    method: String,
    path: String,
    market: String,
    fields: Vec<Field>,
    json_body: bool,
    confirm: bool,
}

fn invalid(message: impl std::fmt::Display) -> DcexError {
    DcexError::InvalidInput(format!("KuCoin: {message}"))
}

fn value(field: &Field, raw: &str) -> Result<Value> {
    let value = match field.schema["type"].as_str() {
        Some("integer") => Value::from(
            raw.parse::<i64>()
                .map_err(|_| invalid(format!("{} must be an integer", field.name)))?,
        ),
        Some("number") => {
            if !raw.parse::<f64>().is_ok_and(f64::is_finite) || raw.contains(['e', 'E']) {
                return Err(invalid("use a plain decimal string"));
            }
            Value::String(raw.into())
        }
        Some("boolean") => Value::from(
            raw.parse::<bool>()
                .map_err(|_| invalid("invalid boolean"))?,
        ),
        Some(kind @ ("array" | "object")) => {
            let v: Value =
                serde_json::from_str(raw).map_err(|_| invalid("invalid structured JSON"))?;
            if (kind == "array" && !v.is_array()) || (kind == "object" && !v.is_object()) {
                return Err(invalid("invalid structured field type"));
            }
            v
        }
        _ => Value::String(raw.into()),
    };
    if let Some(n) = value.as_i64()
        && (field.schema["minimum"].as_i64().is_some_and(|min| n < min)
            || field.schema["maximum"].as_i64().is_some_and(|max| n > max))
    {
        return Err(invalid(format!("{} outside documented range", field.name)));
    }
    if let Some(choices) = field.schema["enum"].as_array()
        && !choices.contains(&value)
    {
        return Err(invalid(format!("invalid {}", field.name)));
    }
    Ok(value)
}

impl KucoinClient {
    pub(in crate::exchanges::kucoin) async fn catalog_request(
        &self,
        name: &str,
        params: &KucoinParams,
    ) -> Result<Option<ValidatedResponse>> {
        static ENDPOINTS: OnceLock<Vec<Endpoint>> = OnceLock::new();
        let endpoints = ENDPOINTS.get_or_init(load_schemas);
        let Some(e) = endpoints.iter().find(|e| e.name == name) else {
            return Ok(None);
        };
        let mut allowed: Vec<&str> = e.fields.iter().map(|f| f.name.as_str()).collect();
        if e.confirm {
            allowed.push("confirm");
            if params.get("confirm") != Some("true") {
                return Err(invalid("API key deletion requires confirm=true"));
            }
        }
        params.ensure_allowed(&allowed)?;
        let mut path = e.path.clone();
        let mut query = Vec::new();
        let mut body = Map::new();
        for f in &e.fields {
            let Some(raw) = params.get(&f.name) else {
                if f.required {
                    return Err(invalid(format!("{} is required", f.name)));
                }
                continue;
            };
            let v = value(f, raw)?;
            match f.location.as_str() {
                "path" => {
                    if raw.is_empty()
                        || !raw
                            .bytes()
                            .all(|c| c.is_ascii_alphanumeric() || c == b'-' || c == b'_')
                    {
                        return Err(invalid("invalid path identifier"));
                    }
                    path = path.replace(&format!("{{{}}}", f.name), raw);
                }
                "query" => query.push((f.name.clone(), raw.to_owned())),
                "raw_body" => {
                    body = v
                        .as_object()
                        .ok_or_else(|| invalid("body must be an object"))?
                        .clone()
                }
                _ => {
                    body.insert(f.name.clone(), v);
                }
            }
        }
        if path.contains("copy-trade/futures/")
            && e.method == "POST"
            && (path.ends_with("/orders")
                || path.ends_with("/test")
                || path.ends_with("/st-orders"))
        {
            if body["type"].as_str().unwrap_or("limit") == "limit" && body.get("price").is_none() {
                return Err(invalid("limit orders require price"));
            }
            if body.get("stop").is_some()
                && (body.get("stopPrice").is_none() || body.get("stopPriceType").is_none())
            {
                return Err(invalid("stop requires stopPrice and stopPriceType"));
            }
        }
        if path.ends_with("/proxyClient/submit") {
            let identity = body["identityType"].as_str().unwrap_or("");
            if identity != "bvn" && !body.contains_key("frontPhoto") {
                return Err(invalid("frontPhoto required for this identityType"));
            }
        }
        let method = match e.method.as_str() {
            "GET" => HttpMethod::Get,
            "POST" => HttpMethod::Post,
            "DELETE" => HttpMethod::Delete,
            _ => return Err(invalid("unsupported method")),
        };
        let market = match e.market.as_str() {
            "futures" => KucoinMarket::Futures,
            "broker" => KucoinMarket::Broker,
            _ => KucoinMarket::Spot,
        };
        let body = if e.json_body {
            Some(serde_json::to_vec(&body).map_err(|e| DcexError::Decode(e.to_string()))?)
        } else {
            None
        };
        self.request(method, market, path, query, body, true)
            .await
            .map(Some)
    }
}

fn load_schemas() -> Vec<Endpoint> {
    [
        include_str!("../schemas/account.json"),
        include_str!("../schemas/affiliate.json"),
        include_str!("../schemas/broker.json"),
        include_str!("../schemas/copy_trading.json"),
    ]
    .into_iter()
    .flat_map(|raw| serde_json::from_str::<Vec<Endpoint>>(raw).expect("checked endpoint schemas"))
    .collect()
}
