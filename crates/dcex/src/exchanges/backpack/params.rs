use serde_json::{Map, Number, Value};

use crate::{DcexError, Result};

pub(super) struct BackpackParams(Vec<(String, String)>);

impl BackpackParams {
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
        serde_json::from_str(self.required(key)?).map_err(|error| {
            DcexError::InvalidInput(format!("invalid JSON parameter {key}: {error}"))
        })
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

pub(super) fn insert_required_string(body: &mut Map<String, Value>, key: &str, value: &str) {
    body.insert(key.to_string(), Value::String(value.to_string()));
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
    if let Some(value) = value.and_then(bool_value) {
        body.insert(key.to_string(), Value::Bool(value));
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

pub(super) fn signature_payload_from_value(value: &Value) -> Vec<Vec<(String, String)>> {
    match value {
        Value::Array(items) => items
            .iter()
            .map(|item| signature_pairs_from_value(item))
            .collect(),
        Value::Object(_) => vec![signature_pairs_from_value(value)],
        _ => Vec::new(),
    }
}

fn signature_pairs_from_value(value: &Value) -> Vec<(String, String)> {
    let Some(object) = value.as_object() else {
        return Vec::new();
    };
    object
        .iter()
        .filter_map(|(key, value)| {
            if value.is_null() {
                None
            } else {
                Some((key.clone(), json_value_string(value)))
            }
        })
        .collect()
}

fn json_value_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.to_string(),
        Value::Number(value) => value.to_string(),
        Value::Bool(value) => value.to_string(),
        Value::Null => String::new(),
        Value::Array(_) | Value::Object(_) => value.to_string(),
    }
}
