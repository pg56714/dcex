use serde_json::{Map, Number, Value};

use crate::common::OrderSide;
use crate::{DcexError, Result};

pub(super) struct GateioParams(Vec<(String, String)>);

impl GateioParams {
    pub(super) fn from_pairs(params: Vec<(String, String)>) -> Self {
        Self(params)
    }

    pub(super) fn get(&self, key: &str) -> Option<&str> {
        self.0
            .iter()
            .find(|(candidate, _)| candidate == key)
            .map(|(_, value)| value.as_str())
    }

    pub(super) fn get_any(&self, keys: &[&str]) -> Option<&str> {
        keys.iter().find_map(|key| self.get(key))
    }

    pub(super) fn required(&self, key: &str) -> Result<&str> {
        self.get(key)
            .ok_or_else(|| DcexError::InvalidInput(format!("missing required parameter: {key}")))
    }

    pub(super) fn required_any(&self, keys: &[&str]) -> Result<&str> {
        self.get_any(keys).ok_or_else(|| {
            DcexError::InvalidInput(format!("missing required parameter: {}", keys.join(" or ")))
        })
    }

    pub(super) fn settle(&self) -> &str {
        self.get("settle")
            .or_else(|| self.get("ccy"))
            .unwrap_or("usdt")
    }

    pub(super) fn market_path(&self) -> Result<&str> {
        let market_path = self.get("path").unwrap_or("futures");
        match market_path {
            "futures" | "delivery" => Ok(market_path),
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported Gate.io market path: {market_path}"
            ))),
        }
    }

    pub(super) fn only(&self, keys: &[&str]) -> Vec<(String, String)> {
        self.0
            .iter()
            .filter(|(key, _)| keys.contains(&key.as_str()))
            .cloned()
            .collect()
    }

    pub(super) fn only_renamed(&self, mappings: &[(&str, &str)]) -> Vec<(String, String)> {
        mappings
            .iter()
            .filter_map(|(source, target)| {
                self.get(source)
                    .map(|value| ((*target).to_string(), value.to_string()))
            })
            .collect()
    }

    pub(super) fn body(
        &self,
        string_keys: &[&str],
        integer_keys: &[&str],
        bool_keys: &[&str],
    ) -> Map<String, Value> {
        let mut body = Map::new();
        for key in string_keys {
            insert_optional_string(&mut body, key, self.get(key));
        }
        for key in integer_keys {
            insert_optional_integer(&mut body, key, self.get(key));
        }
        for key in bool_keys {
            insert_optional_bool(&mut body, key, self.get(key));
        }
        body
    }

    pub(super) fn json_required(&self, key: &str) -> Result<Value> {
        let value = self.required(key)?;
        serde_json::from_str(value).map_err(|error| {
            DcexError::InvalidInput(format!("invalid JSON parameter {key}: {error}"))
        })
    }
}

pub(super) fn is_canonical_product_symbol(product_symbol: &str) -> bool {
    product_symbol.contains('-')
}

pub(super) fn exchange_symbol_fallback(product_symbol: &str) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) => format!("{base}_{quote}"),
        _ => product_symbol.to_string(),
    }
}

pub(super) fn insert_optional_string(
    body: &mut Map<String, Value>,
    key: &str,
    value: Option<&str>,
) {
    if let Some(value) = value {
        body.insert(key.to_string(), Value::String(value.to_string()));
    }
}

pub(super) fn insert_optional_integer(
    body: &mut Map<String, Value>,
    key: &str,
    value: Option<&str>,
) {
    if let Some(value) = value {
        body.insert(key.to_string(), integer_or_string(value));
    }
}

pub(super) fn insert_optional_bool(body: &mut Map<String, Value>, key: &str, value: Option<&str>) {
    if let Some(value) = value {
        if let Some(value) = bool_value(value) {
            body.insert(key.to_string(), Value::Bool(value));
        }
    }
}

pub(super) fn insert_truthy_bool(body: &mut Map<String, Value>, key: &str, value: Option<&str>) {
    if value.and_then(bool_value).unwrap_or(false) {
        body.insert(key.to_string(), Value::Bool(true));
    }
}

pub(super) fn integer_or_string(value: &str) -> Value {
    value
        .parse::<i64>()
        .ok()
        .map(Number::from)
        .map(Value::Number)
        .unwrap_or_else(|| Value::String(value.to_string()))
}

pub(super) fn bool_value(value: &str) -> Option<bool> {
    match value {
        "true" | "True" | "1" => Some(true),
        "false" | "False" | "0" => Some(false),
        _ => None,
    }
}

pub(super) fn normalize_side(value: &str) -> Result<String> {
    Ok(OrderSide::parse(value)?.to_exchange("gateio")?.to_string())
}

pub(super) fn signed_size(value: &str, positive: bool) -> Result<String> {
    let size = value.parse::<i64>().map_err(|error| {
        DcexError::InvalidInput(format!("invalid Gate.io contract size {value:?}: {error}"))
    })?;
    let size = if positive { size.abs() } else { -size.abs() };
    Ok(size.to_string())
}

pub(super) fn json_value_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.to_string(),
        Value::Number(value) => value.to_string(),
        Value::Bool(value) => value.to_string(),
        Value::Null => String::new(),
        Value::Array(_) | Value::Object(_) => value.to_string(),
    }
}
