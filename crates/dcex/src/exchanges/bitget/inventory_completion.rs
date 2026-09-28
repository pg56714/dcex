//! Additional operations extracted from Bitget's published OpenAPI documentation.
use super::{client::BitgetClient, params::BitgetParams};
use crate::{DcexError, Result, exchange::ValidatedResponse, http::HttpMethod};
use serde::Deserialize;
use serde_json::{Map, Value};
use std::sync::OnceLock;

#[derive(Deserialize)]
struct Field {
    wire: String,
    required: bool,
    schema: Value,
    location: String,
}
#[derive(Deserialize)]
struct Endpoint {
    name: String,
    method: String,
    path: String,
    public: bool,
    confirm: bool,
    fields: Vec<Field>,
}

fn invalid(message: impl std::fmt::Display) -> DcexError {
    DcexError::InvalidInput(format!("Bitget: {message}"))
}

fn validate(value: &Value, schema: &Value, key: &str) -> Result<()> {
    let valid = match schema["type"].as_str() {
        Some("string") => value.is_string(),
        Some("integer") => value.is_i64() || value.is_u64(),
        Some("number") => value.is_number(),
        Some("boolean") => value.is_boolean(),
        Some("array") => value.is_array(),
        Some("object") => value.is_object(),
        _ => true,
    };
    if !valid {
        return Err(invalid(format!("invalid type for {key}")));
    }
    if let Some(choices) = schema["enum"].as_array()
        && !choices.contains(value)
    {
        return Err(invalid(format!("invalid {key}")));
    }
    if let Some(number) = value.as_f64()
        && (schema["minimum"]
            .as_f64()
            .is_some_and(|minimum| number < minimum)
            || schema["maximum"]
                .as_f64()
                .is_some_and(|maximum| number > maximum))
    {
        return Err(invalid(format!("{key} is outside the documented range")));
    }
    if let Some(items) = value.as_array() {
        for item in items {
            validate(item, &schema["items"], key)?;
        }
    }
    if let Some(object) = value.as_object() {
        if let Some(required) = schema["required"].as_array() {
            for field in required.iter().filter_map(Value::as_str) {
                if !object.contains_key(field) {
                    return Err(invalid(format!("missing {key}.{field}")));
                }
            }
        }
        for (field, item) in object {
            validate(item, &schema["properties"][field], field)?;
        }
    }
    Ok(())
}

impl BitgetClient {
    pub(super) async fn inventory_request(
        &self,
        name: &str,
        p: &BitgetParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        static ENDPOINTS: OnceLock<Vec<Endpoint>> = OnceLock::new();
        let endpoints = ENDPOINTS.get_or_init(|| {
            serde_json::from_str(include_str!("inventory_completion.json"))
                .expect("validated endpoint schemas")
        });
        let Some(endpoint) = endpoints
            .iter()
            .find(|e| e.name == name && e.public == public)
        else {
            return Ok(None);
        };
        let mut allowed: Vec<&str> = endpoint.fields.iter().map(|f| f.wire.as_str()).collect();
        if endpoint.confirm {
            allowed.push("confirm");
            if p.get("confirm") != Some("true") {
                return Err(invalid("confirm=true is required"));
            }
        }
        p.ensure_allowed(&allowed, false)?;
        let mut query = Vec::new();
        let mut body = Map::new();
        for field in &endpoint.fields {
            let Some(raw) = p.get(&field.wire) else {
                if field.required {
                    return Err(invalid(format!("missing {}", field.wire)));
                }
                continue;
            };
            let value = if field.schema["type"].as_str().unwrap_or("string") == "string" {
                Value::String(raw.into())
            } else {
                serde_json::from_str(raw)
                    .map_err(|_| invalid(format!("invalid JSON for {}", field.wire)))?
            };
            validate(&value, &field.schema, &field.wire)?;
            if field.location == "query" {
                query.push((field.wire.clone(), raw.into()));
            } else {
                body.insert(field.wire.clone(), value);
            }
        }
        let response = if endpoint.method == "GET" {
            if public {
                self.public_get(&endpoint.path, query).await?
            } else {
                self.get_private(&endpoint.path, query).await?
            }
        } else {
            let path = if query.is_empty() {
                endpoint.path.clone()
            } else {
                format!(
                    "{}?{}",
                    endpoint.path,
                    super::signing::encode_params(&query)
                )
            };
            let body = if endpoint.fields.iter().any(|f| f.location == "body") {
                Some(serde_json::to_vec(&Value::Object(body)).map_err(|e| invalid(e.to_string()))?)
            } else {
                None
            };
            self.request(HttpMethod::Post, path, vec![], body, !public)
                .await?
        };
        Ok(Some(response))
    }
}
