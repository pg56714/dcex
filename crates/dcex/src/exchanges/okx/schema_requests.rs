//! Schema-driven request validation, encoding and dispatch.
use super::{client::OkxClient, params::OkxParams};
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};
use serde_json::Value;
use std::collections::HashMap;
use std::sync::{Arc, Mutex, OnceLock};

mod sbe;
mod schema_cache;
mod validation;
use schema_cache::cached_schema;
use validation::*;

#[path = "generated/schema_tables.rs"]
mod endpoints;
struct RiskEndpoint {
    path: &'static str,
    post: bool,
    public: bool,
    keys: &'static [&'static str],
    required: &'static [&'static str],
    bools: &'static [&'static str],
    schema: Option<&'static str>,
}
impl OkxClient {
    pub(super) async fn table_request(
        &self,
        name: &str,
        p: &OkxParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        let Some(e) = endpoints::endpoint(name) else {
            return Ok(None);
        };
        if public != e.public {
            return Ok(None);
        }
        let schema = e.schema.map(cached_schema).transpose()?;
        let pairs = p.without(&[]);
        crate::exchanges::input_contracts::pairs("okx", name, &pairs)?;
        let mut seen = std::collections::HashSet::new();
        for (key, value) in &pairs {
            if !e.keys.contains(&key.as_str())
                || !seen.insert(key)
                || (value.trim().is_empty()
                    && !schema
                        .as_ref()
                        .is_some_and(|sc| sc["properties"][key]["x-allow-empty"] == true))
            {
                return Err(invalid("unknown, duplicate or empty parameter"));
            }
        }
        for key in e.required {
            if *key == "instId" {
                p.get("product_symbol")
                    .or(p.get("instId"))
                    .ok_or_else(|| invalid("instId is required"))?;
            } else {
                p.required(key)?;
            }
        }
        if p.get("product_symbol").is_some() && p.get("instId").is_some() {
            return Err(invalid("provide only one instrument parameter"));
        }
        let mut query = p.only(
            &e.keys
                .iter()
                .copied()
                .filter(|k| *k != "product_symbol")
                .collect::<Vec<_>>(),
        );
        if let Some(product) = p.get("product_symbol") {
            query.push(("instId".into(), self.exchange_symbol(product)?));
        }
        for key in e.bools {
            if let Some((_, value)) = query.iter_mut().find(|(k, _)| k == key) {
                *value = match value.as_str() {
                    "true" | "True" => "true",
                    "false" | "False" => "false",
                    _ => return Err(invalid("boolean must be true or false")),
                }
                .into();
            }
        }
        validate(name, p)?;
        if let Some(schema) = &schema {
            validate_additional(name, p, schema)?;
        }
        let response = if e.post {
            let body = query
                .into_iter()
                .map(|(key, value)| {
                    let value = if e.bools.contains(&key.as_str()) {
                        Value::Bool(value == "true")
                    } else if ["ccyList", "repayCcyList"].contains(&key.as_str())
                        || schema.as_ref().is_some_and(|s| {
                            matches!(
                                s["properties"][&key]["type"].as_str(),
                                Some("array" | "object" | "integer")
                            )
                        })
                    {
                        serde_json::from_str(&value)
                            .map_err(|_| invalid("invalid currency list JSON"))?
                    } else {
                        Value::String(value)
                    };
                    Ok((key, value))
                })
                .collect::<Result<serde_json::Map<String, Value>>>()?;
            let body = if schema.as_ref().is_some_and(|sc| sc["x-body-array"] == true) {
                body.get("orders")
                    .cloned()
                    .ok_or_else(|| invalid("orders are required"))?
            } else {
                Value::Object(body)
            };
            let body = serde_json::to_vec(&body).map_err(|error| invalid(&error.to_string()))?;
            self.request(HttpMethod::Post, e.path, Vec::new(), Some(body), !public)
                .await
        } else {
            self.request(HttpMethod::Get, e.path, query, None, !public)
                .await
        };
        response.map(Some)
    }
}
fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(format!("OKX: {message}"))
}
