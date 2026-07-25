use std::collections::HashSet;

use serde_json::{Map, Number, Value};

use crate::{DcexError, Result};

pub(super) struct BackpackParams(Vec<(String, String)>);

impl BackpackParams {
    pub(super) fn from_pairs(params: Vec<(String, String)>) -> Self {
        Self(params)
    }

    pub(super) fn from_json_object(object: &Map<String, Value>) -> Result<Self> {
        let mut params = Vec::with_capacity(object.len());
        for (key, value) in object {
            let value = match value {
                Value::String(value) => value.clone(),
                Value::Number(value) => value.to_string(),
                Value::Bool(value) => value.to_string(),
                Value::Null | Value::Array(_) | Value::Object(_) => {
                    return Err(DcexError::InvalidInput(format!(
                        "Backpack batch order field {key} must be a scalar"
                    )));
                }
            };
            params.push((key.clone(), value));
        }
        Ok(Self(params))
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
        let value = self
            .get(key)
            .ok_or_else(|| DcexError::InvalidInput(format!("missing required parameter: {key}")))?;
        if value.trim().is_empty() {
            return Err(DcexError::InvalidInput(format!(
                "Backpack parameter {key} must not be empty"
            )));
        }
        Ok(value)
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

    pub(super) fn values<'a>(&'a self, key: &'a str) -> impl Iterator<Item = &'a str> + 'a {
        self.0
            .iter()
            .filter(move |(candidate, _)| candidate == key)
            .map(|(_, value)| value.as_str())
    }

    pub(super) fn ensure_allowed(&self, allowed: &[&str], repeated: &[&str]) -> Result<()> {
        let mut seen = HashSet::new();
        for (key, value) in &self.0 {
            if !allowed.contains(&key.as_str()) {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Backpack parameter: {key}"
                )));
            }
            if value.trim().is_empty() {
                return Err(DcexError::InvalidInput(format!(
                    "Backpack parameter {key} must not be empty"
                )));
            }
            if !repeated.contains(&key.as_str()) && !seen.insert(key.as_str()) {
                return Err(DcexError::InvalidInput(format!(
                    "duplicate Backpack parameter: {key}"
                )));
            }
        }
        Ok(())
    }

    pub(super) fn ensure_exactly_one(&self, keys: &[&str]) -> Result<()> {
        let count = keys.iter().filter(|key| self.get(key).is_some()).count();
        if count != 1 {
            return Err(DcexError::InvalidInput(format!(
                "specify exactly one of {}",
                keys.join(" or ")
            )));
        }
        Ok(())
    }

    pub(super) fn optional_one_of(&self, key: &str, allowed: &[&str]) -> Result<()> {
        if let Some(value) = self.get(key) {
            if !allowed.contains(&value) {
                return Err(DcexError::InvalidInput(format!(
                    "invalid Backpack {key}: {value}; expected one of {}",
                    allowed.join(", ")
                )));
            }
        }
        Ok(())
    }

    pub(super) fn values_one_of(&self, key: &str, allowed: &[&str]) -> Result<()> {
        for value in self.values(key) {
            if !allowed.contains(&value) {
                return Err(DcexError::InvalidInput(format!(
                    "invalid Backpack {key}: {value}; expected one of {}",
                    allowed.join(", ")
                )));
            }
        }
        Ok(())
    }

    pub(super) fn optional_u64_range(&self, key: &str, min: u64, max: u64) -> Result<()> {
        if let Some(value) = self.get(key) {
            let value = value.parse::<u64>().map_err(|error| {
                DcexError::InvalidInput(format!("invalid Backpack {key}: {error}"))
            })?;
            if value < min || value > max {
                return Err(DcexError::InvalidInput(format!(
                    "Backpack parameter {key} must be between {min} and {max}"
                )));
            }
        }
        Ok(())
    }

    pub(super) fn optional_i64(&self, key: &str) -> Result<()> {
        if let Some(value) = self.get(key) {
            value.parse::<i64>().map_err(|error| {
                DcexError::InvalidInput(format!("invalid Backpack {key}: {error}"))
            })?;
        }
        Ok(())
    }

    pub(super) fn optional_i64_range(&self, key: &str, min: i64, max: i64) -> Result<()> {
        if let Some(value) = self.get(key) {
            let value = value.parse::<i64>().map_err(|error| {
                DcexError::InvalidInput(format!("invalid Backpack {key}: {error}"))
            })?;
            if value < min || value > max {
                return Err(DcexError::InvalidInput(format!(
                    "Backpack parameter {key} must be between {min} and {max}"
                )));
            }
        }
        Ok(())
    }

    pub(super) fn optional_bool(&self, key: &str) -> Result<()> {
        if let Some(value) = self.get(key) {
            if bool_value(value).is_none() {
                return Err(DcexError::InvalidInput(format!(
                    "invalid Backpack boolean {key}: {value}"
                )));
            }
        }
        Ok(())
    }

    pub(super) fn bool(&self, key: &str) -> Option<bool> {
        self.get(key).and_then(bool_value)
    }

    pub(super) fn ensure_time_order(&self, start_key: &str, end_key: &str) -> Result<()> {
        self.optional_i64(start_key)?;
        self.optional_i64(end_key)?;
        if let (Some(start), Some(end)) = (self.get(start_key), self.get(end_key)) {
            let start = start.parse::<i64>().expect("validated start");
            let end = end.parse::<i64>().expect("validated end");
            if start > end {
                return Err(DcexError::InvalidInput(format!(
                    "Backpack {start_key} must not be after {end_key}"
                )));
            }
        }
        Ok(())
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
        Value::Array(items) => items.iter().map(signature_pairs_from_value).collect(),
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
