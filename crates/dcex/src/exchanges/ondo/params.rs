use std::collections::HashSet;

use serde_json::{Map, Number, Value};

use crate::{DcexError, Result};

#[derive(Clone)]
pub(super) struct OndoParams(Vec<(String, String)>);

impl OndoParams {
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
        let value = self
            .get(key)
            .ok_or_else(|| DcexError::InvalidInput(format!("missing required parameter: {key}")))?;
        if value.trim().is_empty() {
            return Err(DcexError::InvalidInput(format!(
                "Ondo parameter {key} must not be empty"
            )));
        }
        Ok(value)
    }

    pub(super) fn ensure_allowed(&self, allowed: &[&str]) -> Result<()> {
        let mut seen = HashSet::new();
        for (key, value) in &self.0 {
            if !allowed.contains(&key.as_str()) {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Ondo parameter: {key}"
                )));
            }
            if value.trim().is_empty() {
                return Err(DcexError::InvalidInput(format!(
                    "Ondo parameter {key} must not be empty"
                )));
            }
            if !seen.insert(key.as_str()) {
                return Err(DcexError::InvalidInput(format!(
                    "duplicate Ondo parameter: {key}"
                )));
            }
        }
        Ok(())
    }

    pub(super) fn ensure_required(&self, required: &[&str]) -> Result<()> {
        for key in required {
            self.required(key)?;
        }
        Ok(())
    }

    pub(super) fn optional_one_of(&self, key: &str, allowed: &[&str]) -> Result<()> {
        if let Some(value) = self.get(key) {
            if !allowed.contains(&value) {
                return Err(DcexError::InvalidInput(format!(
                    "invalid Ondo {key}: {value}; expected one of {}",
                    allowed.join(", ")
                )));
            }
        }
        Ok(())
    }

    pub(super) fn optional_bool(&self, key: &str) -> Result<()> {
        if let Some(value) = self.get(key) {
            if !matches!(value, "true" | "false") {
                return Err(DcexError::InvalidInput(format!(
                    "invalid Ondo boolean {key}: {value}"
                )));
            }
        }
        Ok(())
    }

    pub(super) fn optional_u64(&self, key: &str) -> Result<()> {
        if let Some(value) = self.get(key) {
            value.parse::<u64>().map_err(|error| {
                DcexError::InvalidInput(format!("invalid Ondo integer {key}: {error}"))
            })?;
        }
        Ok(())
    }

    pub(super) fn ensure_time_order(&self, start: &str, end: &str) -> Result<()> {
        let start_value = self
            .get(start)
            .map(str::parse::<u64>)
            .transpose()
            .map_err(|error| {
                DcexError::InvalidInput(format!("invalid Ondo integer {start}: {error}"))
            })?;
        let end_value = self
            .get(end)
            .map(str::parse::<u64>)
            .transpose()
            .map_err(|error| {
                DcexError::InvalidInput(format!("invalid Ondo integer {end}: {error}"))
            })?;
        if start_value
            .zip(end_value)
            .is_some_and(|(start, end)| start > end)
        {
            return Err(DcexError::InvalidInput(format!(
                "Ondo {start} must not be after {end}"
            )));
        }
        Ok(())
    }

    pub(super) fn path_segment(&self, key: &str) -> Result<&str> {
        let value = self.required(key)?;
        if !value.chars().all(|character| {
            character.is_ascii_alphanumeric()
                || character == '-'
                || character == '_'
                || character == '.'
                || character == ':'
        }) {
            return Err(DcexError::InvalidInput(format!(
                "invalid Ondo path parameter {key}: {value}"
            )));
        }
        Ok(value)
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
        allowed: &[&str],
        required: &[&str],
        bools: &[&str],
        integers: &[&str],
        json: &[&str],
    ) -> Result<Value> {
        if let Some(body) = self.get("body") {
            self.ensure_allowed(&["body"])?;
            let value: Value = serde_json::from_str(body).map_err(|error| {
                DcexError::InvalidInput(format!("invalid Ondo JSON body: {error}"))
            })?;
            let object = value.as_object().ok_or_else(|| {
                DcexError::InvalidInput("Ondo JSON body must be an object".to_string())
            })?;
            for key in object.keys() {
                if !allowed.contains(&key.as_str()) {
                    return Err(DcexError::InvalidInput(format!(
                        "unsupported Ondo body field: {key}"
                    )));
                }
            }
            for key in required {
                if !object.get(*key).is_some_and(|value| {
                    !value.is_null() && !value.as_str().is_some_and(|value| value.trim().is_empty())
                }) {
                    return Err(DcexError::InvalidInput(format!(
                        "missing required Ondo body field: {key}"
                    )));
                }
            }
            for key in bools {
                if object.get(*key).is_some_and(|value| !value.is_boolean()) {
                    return Err(DcexError::InvalidInput(format!(
                        "Ondo body field {key} must be boolean"
                    )));
                }
            }
            for key in integers {
                if object.get(*key).is_some_and(|value| !value.is_u64()) {
                    return Err(DcexError::InvalidInput(format!(
                        "Ondo body field {key} must be an unsigned integer"
                    )));
                }
            }
            return Ok(value);
        }
        self.ensure_allowed(allowed)?;
        self.ensure_required(required)?;
        let mut body = Map::new();
        for (key, value) in &self.0 {
            let value = if bools.contains(&key.as_str()) {
                Value::Bool(value.parse::<bool>().map_err(|error| {
                    DcexError::InvalidInput(format!("invalid Ondo boolean {key}: {error}"))
                })?)
            } else if integers.contains(&key.as_str()) {
                Value::Number(Number::from(value.parse::<u64>().map_err(|error| {
                    DcexError::InvalidInput(format!("invalid Ondo integer {key}: {error}"))
                })?))
            } else if json.contains(&key.as_str()) {
                serde_json::from_str(value).map_err(|error| {
                    DcexError::InvalidInput(format!("invalid Ondo JSON field {key}: {error}"))
                })?
            } else {
                Value::String(value.clone())
            };
            body.insert(key.clone(), value);
        }
        Ok(Value::Object(body))
    }
}

pub(super) fn path_with_id(base: &str, id: &str) -> String {
    format!("{}/{}", base.trim_end_matches('/'), id)
}
