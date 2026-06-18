use serde_json::{Map, Number, Value};

use crate::{DcexError, Result};

pub(super) struct BitmexParams(Vec<(String, String)>);

impl BitmexParams {
    pub(super) fn from_pairs(params: Vec<(String, String)>) -> Self {
        Self(params)
    }

    pub(super) fn get(&self, key: &str) -> Option<&str> {
        self.0
            .iter()
            .find(|(candidate, _)| candidate == key)
            .map(|(_, value)| value.as_str())
    }

    pub(super) fn required(&self, key: &str) -> Result<&str> {
        self.get(key)
            .ok_or_else(|| DcexError::InvalidInput(format!("missing required parameter: {key}")))
    }

    pub(super) fn only(&self, keys: &[&str]) -> Vec<(String, String)> {
        self.0
            .iter()
            .filter(|(key, _)| keys.contains(&key.as_str()))
            .cloned()
            .collect()
    }

    pub(super) fn body(
        &self,
        string_keys: &[&str],
        number_keys: &[&str],
        bool_keys: &[&str],
        json_keys: &[&str],
    ) -> Map<String, Value> {
        let mut body = Map::new();
        for key in string_keys {
            insert_optional_string(&mut body, key, self.get(key));
        }
        for key in number_keys {
            insert_optional_number(&mut body, key, self.get(key));
        }
        for key in bool_keys {
            insert_optional_bool(&mut body, key, self.get(key));
        }
        for key in json_keys {
            insert_optional_json(&mut body, key, self.get(key));
        }
        body
    }
}

pub(super) fn is_canonical_product_symbol(product_symbol: &str) -> bool {
    product_symbol.contains('-')
}

pub(super) fn exchange_symbol_fallback(product_symbol: &str) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) => format!("{base}{quote}"),
        _ => product_symbol.to_string(),
    }
}

pub(super) fn push_optional(params: &mut Vec<(String, String)>, key: &str, value: Option<&str>) {
    if let Some(value) = value {
        params.push((key.to_string(), value.to_string()));
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

pub(super) fn insert_optional_number(
    body: &mut Map<String, Value>,
    key: &str,
    value: Option<&str>,
) {
    if let Some(value) = value {
        body.insert(key.to_string(), number_or_string(value));
    }
}

pub(super) fn insert_optional_bool(body: &mut Map<String, Value>, key: &str, value: Option<&str>) {
    if let Some(value) = value {
        body.insert(key.to_string(), bool_or_string(value));
    }
}

pub(super) fn insert_optional_json(body: &mut Map<String, Value>, key: &str, value: Option<&str>) {
    if let Some(value) = value {
        body.insert(key.to_string(), json_or_string(value));
    }
}

pub(super) fn number_or_string(value: &str) -> Value {
    if let Ok(value) = value.parse::<i64>() {
        return Value::Number(value.into());
    }
    if let Ok(value) = value.parse::<f64>() {
        if let Some(value) = Number::from_f64(value) {
            return Value::Number(value);
        }
    }
    Value::String(value.to_string())
}

pub(super) fn bool_or_string(value: &str) -> Value {
    match value {
        "true" | "True" => Value::Bool(true),
        "false" | "False" => Value::Bool(false),
        _ => Value::String(value.to_string()),
    }
}

pub(super) fn json_or_string(value: &str) -> Value {
    serde_json::from_str(value).unwrap_or_else(|_| Value::String(value.to_string()))
}
