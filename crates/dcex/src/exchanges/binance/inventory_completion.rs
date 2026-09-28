//! Additional documented SDK operations; Alpha has its own host and Fiat uses JSON.
use super::{BinanceClient, params::PublicParams};
use crate::{DcexError, Result, exchange::ValidatedResponse, http::HttpMethod};
use serde::Deserialize;
use serde_json::{Map, Value};
use std::sync::OnceLock;
#[derive(Deserialize)]
struct Field {
    wire: String,
    kind: String,
    required: bool,
}
#[derive(Deserialize)]
struct Endpoint {
    name: String,
    method: String,
    path: String,
    public: bool,
    json_body: bool,
    fields: Vec<Field>,
}
fn invalid(message: impl std::fmt::Display) -> DcexError {
    DcexError::InvalidInput(format!("Binance: {message}"))
}
impl BinanceClient {
    pub(super) async fn inventory_request(
        &self,
        name: &str,
        p: &PublicParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        static ENDPOINTS: OnceLock<Vec<Endpoint>> = OnceLock::new();
        let endpoints = ENDPOINTS.get_or_init(|| {
            serde_json::from_str(include_str!("inventory_completion.json"))
                .expect("checked Binance schemas")
        });
        let Some(e) = endpoints
            .iter()
            .find(|e| e.name == name && e.public == public)
        else {
            return Ok(None);
        };
        let allowed: Vec<&str> = e.fields.iter().map(|f| f.wire.as_str()).collect();
        p.ensure_allowed(&allowed)?;
        let mut fields = Map::new();
        for f in &e.fields {
            let Some(raw) = p.get(&f.wire) else {
                if f.required {
                    return Err(invalid(format!("{} is required", f.wire)));
                }
                continue;
            };
            let value = match f.kind.as_str() {
                "int" => Value::from(
                    raw.parse::<i64>()
                        .map_err(|_| invalid(format!("invalid integer {}", f.wire)))?,
                ),
                "bool" => Value::from(
                    raw.parse::<bool>()
                        .map_err(|_| invalid("invalid boolean"))?,
                ),
                "array" | "object" => {
                    let v: Value = serde_json::from_str(raw)
                        .map_err(|_| invalid("invalid structured parameter"))?;
                    if (f.kind == "array" && !v.is_array())
                        || (f.kind == "object" && !v.is_object())
                    {
                        return Err(invalid("invalid JSON type"));
                    }
                    v
                }
                "decimal" => {
                    if !crate::common::is_positive_plain_decimal(raw) {
                        return Err(invalid("decimal must be a positive plain string"));
                    }
                    Value::String(raw.into())
                }
                _ => Value::String(raw.into()),
            };
            fields.insert(f.wire.clone(), value);
        }
        let method = match e.method.as_str() {
            "GET" => HttpMethod::Get,
            "POST" => HttpMethod::Post,
            "DELETE" => HttpMethod::Delete,
            "PUT" => HttpMethod::Put,
            _ => return Err(invalid("unsupported verb")),
        };
        let mut query = Vec::new();
        let body = if e.json_body {
            if let Some(v) = fields.remove("recvWindow") {
                query.push(("recvWindow".into(), v.to_string()));
            }
            Some(Value::Object(fields))
        } else {
            for (key, value) in fields {
                if key == "cancelInfoList" {
                    for (index, item) in value
                        .as_array()
                        .ok_or_else(|| invalid("cancelInfoList must be an array"))?
                        .iter()
                        .enumerate()
                    {
                        let object = item
                            .as_object()
                            .ok_or_else(|| invalid("cancelInfoList entries must be objects"))?;
                        for (field, value) in object {
                            query.push((
                                format!("{key}[{index}].{field}"),
                                super::signing::json_value_string(value),
                            ));
                        }
                    }
                } else if let Some(items) = value.as_array() {
                    for item in items {
                        query.push((key.clone(), super::signing::json_value_string(item)));
                    }
                } else {
                    query.push((key, super::signing::json_value_string(&value)));
                }
            }
            None
        };
        self.inventory_transport(method, &e.path, query, body, !public)
            .await
            .map(Some)
    }
}
