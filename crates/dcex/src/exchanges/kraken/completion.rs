//! RFQ, affiliate, and funding endpoints with their documented parameter locations.
use std::sync::OnceLock;

use serde::Deserialize;
use serde_json::{Map, Value};

use super::{KrakenAuth, KrakenClient, params::KrakenParams};
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

#[derive(Deserialize)]
struct Field {
    name: String,
    location: String,
    required: bool,
    schema: Value,
}
#[derive(Deserialize)]
struct Endpoint {
    name: String,
    method: String,
    path: String,
    auth: String,
    fields: Vec<Field>,
}
static ENDPOINTS: OnceLock<Vec<Endpoint>> = OnceLock::new();
fn invalid(message: impl std::fmt::Display) -> DcexError {
    DcexError::InvalidInput(format!("Kraken: {message}"))
}

impl KrakenClient {
    pub(super) async fn completion_private_request(
        &self,
        name: &str,
        params: &KrakenParams,
    ) -> Result<Option<ValidatedResponse>> {
        let endpoints = ENDPOINTS.get_or_init(|| {
            serde_json::from_str(include_str!("completion_endpoints.json"))
                .expect("embedded Kraken schema")
        });
        let Some(e) = endpoints.iter().find(|e| e.name == name) else {
            return Ok(None);
        };
        let keys: Vec<_> = e.fields.iter().map(|f| f.name.as_str()).collect();
        params.ensure_allowed(&keys)?;
        let mut fields = Map::new();
        let mut query = Vec::new();
        let mut body = None;
        let mut body_fields = Map::new();
        let mut path = e.path.clone();
        for f in &e.fields {
            let Some(raw) = params.get(&f.name) else {
                if f.required {
                    return Err(invalid(format!("{} is required", f.name)));
                }
                continue;
            };
            if raw.is_empty() {
                return Err(invalid(format!("{} cannot be empty", f.name)));
            }
            let json = matches!(
                f.schema["type"].as_str(),
                Some("object" | "array" | "boolean" | "integer" | "number")
            ) || f.schema.get("oneOf").is_some()
                || f.schema.get("allOf").is_some();
            let value: Value = if json {
                serde_json::from_str(raw)
                    .map_err(|_| invalid(format!("invalid {} JSON value", f.name)))?
            } else {
                raw.into()
            };
            validate(&value, &f.schema, &f.name)?;
            match f.location.as_str() {
                "path" => {
                    if !raw
                        .bytes()
                        .all(|b| b.is_ascii_alphanumeric() || b"_-".contains(&b))
                    {
                        return Err(invalid("invalid path identifier"));
                    }
                    path = path.replace(&format!("{{{}}}", f.name), raw);
                }
                "body" => body = Some(value.clone()),
                "body_field" => {
                    body_fields.insert(f.name.clone(), value.clone());
                }
                "query" => {
                    if e.auth == "header" {
                        nested_query(&f.name, &value, &mut query)?;
                    } else {
                        query.push((f.name.clone(), raw.to_owned()));
                    }
                }
                "header" => {}
                _ => return Err(invalid("unknown embedded parameter location")),
            }
            fields.insert(f.name.clone(), value);
        }
        validate_endpoint(name, &fields)?;
        let method = match e.method.as_str() {
            "GET" => HttpMethod::Get,
            "POST" => HttpMethod::Post,
            "PUT" => HttpMethod::Put,
            "DELETE" => HttpMethod::Delete,
            _ => return Err(invalid("unknown HTTP verb")),
        };
        if e.auth == "header" {
            return self
                .request_header_nonce(method, path, query, body, params.get("otp"))
                .await
                .map(Some);
        }
        if e.auth == "spot" {
            let body = serde_json::to_vec(&Value::Object(body_fields)).map_err(invalid)?;
            return self
                .request(method, KrakenAuth::Spot, path, Vec::new(), Some(body), true)
                .await
                .map(Some);
        }
        self.request(method, KrakenAuth::Futures, path, query, None, true)
            .await
            .map(Some)
    }
}

fn nested_query(key: &str, value: &Value, out: &mut Vec<(String, String)>) -> Result<()> {
    match value {
        Value::Object(object) => {
            for (child, value) in object {
                nested_query(&format!("{key}[{child}]"), value, out)?;
            }
        }
        Value::Array(values) => {
            // Matches the official guide's Python _nested_query helper. The
            // status.list array representation is not independently confirmed.
            let mut items = Vec::new();
            for item in values {
                items.push(format!(
                    "'{}'",
                    item.as_str()
                        .ok_or_else(|| invalid("query list requires strings"))?
                ));
            }
            out.push((key.into(), format!("[{}]", items.join(", "))));
        }
        Value::Null => {}
        Value::String(s) => out.push((key.into(), s.clone())),
        _ => out.push((key.into(), value.to_string())),
    }
    Ok(())
}

fn validate_endpoint(name: &str, fields: &Map<String, Value>) -> Result<()> {
    let has = |key: &str| fields.contains_key(key);
    match name {
        "accept_rfq_offer" if has("bidAccepted") == has("askAccepted") => {
            return Err(invalid(
                "exactly one of bidAccepted or askAccepted is required",
            ));
        }
        "place_rfq_offer" => {
            let flat = has("bid") || has("ask");
            let legs = has("bidSide") || has("askSide");
            if flat == legs {
                return Err(invalid(
                    "supply bid/ask or per-leg bidSide/askSide exclusively",
                ));
            }
            for key in ["bidSide", "askSide"] {
                if let Some(raw) = fields.get(key).and_then(Value::as_str) {
                    let values: Vec<Value> = serde_json::from_str(raw)
                        .map_err(|_| invalid("side pricing must be a JSON array"))?;
                    if values.is_empty()
                        || values.iter().any(|v| {
                            v["tradeable"].as_str().is_none_or(|s| s.is_empty())
                                || !v["price"].is_number()
                        })
                    {
                        return Err(invalid("side pricing requires tradeable and numeric price"));
                    }
                }
            }
        }
        "create_user_rfq" => {
            let legs = fields["json"]["legs"]
                .as_array()
                .ok_or_else(|| invalid("RFQ legs must be an array"))?;
            let mut seen = std::collections::HashSet::new();
            if legs.is_empty()
                || legs.iter().any(|leg| {
                    !seen.insert(leg["tradeable"].as_str().unwrap_or(""))
                        || leg["size"].as_f64() == Some(0.0)
                })
            {
                return Err(invalid("RFQ legs must be nonempty, unique and nonzero"));
            }
        }
        "add_assignment_program" => {
            if has("baseCurrency") != has("quoteCurrency") {
                return Err(invalid(
                    "baseCurrency and quoteCurrency are required together",
                ));
            }
            if fields["contractType"] == "flex" && !has("contract") && !has("baseCurrency") {
                return Err(invalid(
                    "flex assignment requires contract or base/quote currencies",
                ));
            }
        }
        "update_rfq_assignment_max_leverage" => {
            if !fields["maxLeverage"].as_f64().is_some_and(|n| n > 0.0) {
                return Err(invalid("maxLeverage must be positive"));
            }
        }
        "create_spot_withdrawal" => {
            if !fields["amount"]
                .as_str()
                .is_some_and(crate::common::is_positive_plain_decimal)
            {
                return Err(invalid("amount must be a positive plain decimal string"));
            }
        }
        "get_affiliate_daily_activity" => {
            if has("activity_date") {
                if has("iiban") || has("start_date") || has("end_date") {
                    return Err(invalid(
                        "activity_date and history parameters are mutually exclusive",
                    ));
                }
            } else {
                if !has("iiban") || !has("start_date") || !has("end_date") {
                    return Err(invalid("history requires iiban, start_date and end_date"));
                }
                if fields.get("all_users") == Some(&Value::Bool(true)) {
                    return Err(invalid("all_users is only available for daily activity"));
                }
                if fields["start_date"].as_str() > fields["end_date"].as_str() {
                    return Err(invalid("start_date must not exceed end_date"));
                }
                let ids: Vec<_> = fields["iiban"]
                    .as_str()
                    .expect("validated string")
                    .split(',')
                    .collect();
                let unique: std::collections::HashSet<_> = ids.iter().collect();
                if ids.len() > 10 || unique.len() != ids.len() || ids.iter().any(|s| s.is_empty()) {
                    return Err(invalid("iiban requires 1..10 distinct identifiers"));
                }
            }
        }
        "claim_funding_deposit_address" => {
            if fields["body"]["method_id"]
                .as_str()
                .is_none_or(|s| s.is_empty())
            {
                return Err(invalid("body.method_id is required"));
            }
        }
        "update_funding_address" => {
            if fields["body"]["name"].as_str().is_none_or(|s| s.is_empty()) {
                return Err(invalid("body.name is required"));
            }
        }
        _ => {}
    }
    Ok(())
}

fn validate(value: &Value, schema: &Value, field: &str) -> Result<()> {
    if let Some(branches) = schema["allOf"].as_array() {
        for branch in branches {
            validate(value, branch, field)?;
        }
    }
    if let Some(branches) = schema["oneOf"].as_array() {
        let selected: Vec<_> = branches
            .iter()
            .filter(|branch| {
                branch["properties"]
                    .as_object()
                    .is_none_or(|props| props.keys().any(|k| value.get(k).is_some()))
            })
            .collect();
        if selected.len() != 1 {
            return Err(invalid(format!(
                "{field} requires exactly one documented variant"
            )));
        }
        validate(value, selected[0], field)?;
    }
    if let Some(choices) = schema["enum"].as_array()
        && !choices.contains(value)
    {
        return Err(invalid(format!("invalid {field}")));
    }
    match schema["type"].as_str() {
        Some("object") => {
            let obj = value
                .as_object()
                .ok_or_else(|| invalid(format!("{field} requires an object")))?;
            for key in schema["required"]
                .as_array()
                .into_iter()
                .flatten()
                .filter_map(Value::as_str)
            {
                if !obj.contains_key(key) {
                    return Err(invalid(format!("{field}.{key} is required")));
                }
            }
            if let Some(props) = schema["properties"].as_object() {
                for (key, child) in props {
                    if let Some(v) = obj.get(key) {
                        validate(v, child, &format!("{field}.{key}"))?;
                    }
                }
            }
        }
        Some("array") => {
            let items = value
                .as_array()
                .ok_or_else(|| invalid(format!("{field} requires an array")))?;
            if schema["minItems"]
                .as_u64()
                .is_some_and(|n| items.len() < n as usize)
                || schema["maxItems"]
                    .as_u64()
                    .is_some_and(|n| items.len() > n as usize)
            {
                return Err(invalid(format!("invalid {field} length")));
            }
            for v in items {
                validate(v, &schema["items"], field)?;
            }
        }
        Some("string") => {
            let raw = value
                .as_str()
                .ok_or_else(|| invalid(format!("{field} requires a string")))?;
            if schema["minLength"]
                .as_u64()
                .is_some_and(|n| raw.chars().count() < n as usize)
                || schema["maxLength"]
                    .as_u64()
                    .is_some_and(|n| raw.chars().count() > n as usize)
            {
                return Err(invalid(format!("invalid {field} length")));
            }
            if let Some(pattern) = schema["pattern"].as_str()
                && !regex::Regex::new(pattern)
                    .map_err(|_| invalid("invalid embedded pattern"))?
                    .is_match(raw)
            {
                return Err(invalid(format!("invalid {field} format")));
            }
            if schema["format"] == "uuid"
                && !(raw.len() == 36
                    && raw.bytes().enumerate().all(|(i, b)| {
                        if [8, 13, 18, 23].contains(&i) {
                            b == b'-'
                        } else {
                            b.is_ascii_hexdigit()
                        }
                    }))
            {
                return Err(invalid(format!("{field} requires a UUID")));
            }
        }
        Some("boolean") if !value.is_boolean() => {
            return Err(invalid(format!("{field} requires boolean")));
        }
        Some("integer") if value.as_i64().is_none() => {
            return Err(invalid(format!("{field} requires integer")));
        }
        Some("number") if !value.is_number() => {
            return Err(invalid(format!("{field} requires number")));
        }
        _ => {}
    }
    if let Some(n) = value.as_f64()
        && (schema["minimum"]
            .as_f64()
            .is_some_and(|min| n < min || n == min && schema["exclusiveMinimum"] == true)
            || schema["maximum"].as_f64().is_some_and(|max| n > max))
    {
        return Err(invalid(format!("{field} is outside documented limits")));
    }
    Ok(())
}
