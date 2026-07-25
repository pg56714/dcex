use std::collections::HashSet;

use serde_json::{Map, Value};

use crate::{DcexError, Result};

#[derive(Clone)]
pub(super) struct ExtendedParams(Vec<(String, String)>);

impl ExtendedParams {
    pub(super) fn from_pairs(params: Vec<(String, String)>) -> Self {
        Self(params)
    }

    pub(super) fn get(&self, key: &str) -> Option<&str> {
        self.0
            .iter()
            .find(|(candidate, _)| candidate == key)
            .map(|(_, value)| value.as_str())
    }

    pub(super) fn first(&self, keys: &[&str]) -> Option<&str> {
        keys.iter().find_map(|key| self.get(key))
    }

    pub(super) fn first_required(&self, keys: &[&str]) -> Result<&str> {
        let value = self.first(keys).ok_or_else(|| {
            DcexError::InvalidInput(format!("missing required parameter: {}", keys.join(" or ")))
        })?;
        if value.trim().is_empty() {
            return Err(DcexError::InvalidInput(format!(
                "Extended parameter {} must not be empty",
                keys.join(" or ")
            )));
        }
        Ok(value)
    }

    pub(super) fn required(&self, key: &str) -> Result<&str> {
        let value = self
            .get(key)
            .ok_or_else(|| DcexError::InvalidInput(format!("missing required parameter: {key}")))?;
        if value.trim().is_empty() {
            return Err(DcexError::InvalidInput(format!(
                "Extended parameter {key} must not be empty"
            )));
        }
        Ok(value)
    }

    pub(super) fn ensure_allowed(&self, allowed: &[&str], repeated: &[&str]) -> Result<()> {
        let mut seen = HashSet::new();
        for (key, value) in &self.0 {
            if !allowed.contains(&key.as_str()) {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Extended parameter: {key}"
                )));
            }
            if value.trim().is_empty() {
                return Err(DcexError::InvalidInput(format!(
                    "Extended parameter {key} must not be empty"
                )));
            }
            if !repeated.contains(&key.as_str()) && !seen.insert(key.as_str()) {
                return Err(DcexError::InvalidInput(format!(
                    "duplicate Extended parameter: {key}"
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

    pub(super) fn ensure_at_most_one(&self, keys: &[&str]) -> Result<()> {
        let count = keys.iter().filter(|key| self.get(key).is_some()).count();
        if count > 1 {
            return Err(DcexError::InvalidInput(format!(
                "specify at most one of {}",
                keys.join(" or ")
            )));
        }
        Ok(())
    }

    pub(super) fn optional_one_of(&self, key: &str, allowed: &[&str]) -> Result<()> {
        if let Some(value) = self.get(key) {
            if !allowed.contains(&value) {
                return Err(DcexError::InvalidInput(format!(
                    "invalid Extended {key}: {value}; expected one of {}",
                    allowed.join(", ")
                )));
            }
        }
        Ok(())
    }

    pub(super) fn repeated_one_of(&self, key: &str, allowed: &[&str]) -> Result<()> {
        for (_, value) in self.0.iter().filter(|(candidate, _)| candidate == key) {
            if !allowed.contains(&value.as_str()) {
                return Err(DcexError::InvalidInput(format!(
                    "invalid Extended {key}: {value}; expected one of {}",
                    allowed.join(", ")
                )));
            }
        }
        Ok(())
    }

    pub(super) fn required_one_of(&self, key: &str, allowed: &[&str]) -> Result<()> {
        self.required(key)?;
        self.optional_one_of(key, allowed)
    }

    pub(super) fn optional_bool(&self, key: &str) -> Result<()> {
        if let Some(value) = self.get(key) {
            if !matches!(value, "true" | "false") {
                return Err(DcexError::InvalidInput(format!(
                    "invalid Extended boolean {key}: {value}"
                )));
            }
        }
        Ok(())
    }

    pub(super) fn u64(&self, key: &str) -> Result<Option<u64>> {
        self.get(key)
            .map(|value| {
                value.parse::<u64>().map_err(|error| {
                    DcexError::InvalidInput(format!("invalid Extended integer {key}: {error}"))
                })
            })
            .transpose()
    }

    pub(super) fn optional_u64_range(&self, key: &str, min: u64, max: u64) -> Result<()> {
        if let Some(value) = self.u64(key)? {
            if value < min || value > max {
                return Err(DcexError::InvalidInput(format!(
                    "Extended parameter {key} must be between {min} and {max}"
                )));
            }
        }
        Ok(())
    }

    pub(super) fn repeated_u64_range(&self, key: &str, min: u64, max: u64) -> Result<()> {
        for (_, value) in self.0.iter().filter(|(candidate, _)| candidate == key) {
            let value = value.parse::<u64>().map_err(|error| {
                DcexError::InvalidInput(format!("invalid Extended integer {key}: {error}"))
            })?;
            if value < min || value > max {
                return Err(DcexError::InvalidInput(format!(
                    "Extended parameter {key} must be between {min} and {max}"
                )));
            }
        }
        Ok(())
    }

    pub(super) fn required_u64_range(&self, key: &str, min: u64, max: u64) -> Result<()> {
        self.required(key)?;
        self.optional_u64_range(key, min, max)
    }

    pub(super) fn required_positive_decimal(&self, key: &str) -> Result<()> {
        validate_positive_decimal(key, self.required(key)?)
    }

    pub(super) fn ensure_time_order(&self, start_key: &str, end_key: &str) -> Result<()> {
        let start = self.u64(start_key)?;
        let end = self.u64(end_key)?;
        if start.zip(end).is_some_and(|(start, end)| start > end) {
            return Err(DcexError::InvalidInput(format!(
                "Extended {start_key} must not be after {end_key}"
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
        }) {
            return Err(DcexError::InvalidInput(format!(
                "invalid Extended path parameter {key}: {value}"
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

    pub(super) fn with(&self, key: impl Into<String>, value: impl Into<String>) -> Self {
        let mut pairs = self.0.clone();
        pairs.push((key.into(), value.into()));
        Self(pairs)
    }

    pub(super) fn body_required(&self) -> Result<Value> {
        self.body_optional()?.ok_or_else(|| {
            DcexError::InvalidInput("missing required parameter: body or order JSON".to_string())
        })
    }

    pub(super) fn body_optional(&self) -> Result<Option<Value>> {
        self.ensure_at_most_one(&["body", "order"])?;
        let Some(body) = self.get("body").or_else(|| self.get("order")) else {
            return Ok(None);
        };
        serde_json::from_str(body)
            .map(Some)
            .map_err(|error| DcexError::InvalidInput(format!("invalid JSON body: {error}")))
    }
}

pub(super) fn body_object<'a>(body: &'a Value, field: &str) -> Result<&'a Map<String, Value>> {
    body.as_object()
        .ok_or_else(|| DcexError::InvalidInput(format!("Extended {field} must be a JSON object")))
}

pub(super) fn object_allowed(object: &Map<String, Value>, allowed: &[&str]) -> Result<()> {
    for key in object.keys() {
        if !allowed.contains(&key.as_str()) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Extended JSON field: {key}"
            )));
        }
    }
    Ok(())
}

pub(super) fn object_required<'a>(object: &'a Map<String, Value>, key: &str) -> Result<&'a Value> {
    let value = object
        .get(key)
        .ok_or_else(|| DcexError::InvalidInput(format!("missing required JSON field: {key}")))?;
    if value.as_str().is_some_and(|value| value.trim().is_empty()) || value.is_null() {
        return Err(DcexError::InvalidInput(format!(
            "Extended JSON field {key} must not be empty"
        )));
    }
    Ok(value)
}

pub(super) fn json_string<'a>(
    object: &'a Map<String, Value>,
    key: &str,
    required: bool,
) -> Result<Option<&'a str>> {
    let Some(value) = object.get(key) else {
        if required {
            object_required(object, key)?;
        }
        return Ok(None);
    };
    let value = value.as_str().ok_or_else(|| {
        DcexError::InvalidInput(format!("Extended JSON field {key} must be a string"))
    })?;
    if value.trim().is_empty() {
        return Err(DcexError::InvalidInput(format!(
            "Extended JSON field {key} must not be empty"
        )));
    }
    Ok(Some(value))
}

pub(super) fn json_u64(
    object: &Map<String, Value>,
    key: &str,
    required: bool,
) -> Result<Option<u64>> {
    let Some(value) = object.get(key) else {
        if required {
            object_required(object, key)?;
        }
        return Ok(None);
    };
    let parsed = match value {
        Value::Number(value) => value.as_u64(),
        Value::String(value) => value.parse::<u64>().ok(),
        _ => None,
    }
    .ok_or_else(|| {
        DcexError::InvalidInput(format!(
            "Extended JSON field {key} must be a non-negative integer"
        ))
    })?;
    Ok(Some(parsed))
}

pub(super) fn json_bool(object: &Map<String, Value>, key: &str) -> Result<Option<bool>> {
    object
        .get(key)
        .map(|value| {
            value.as_bool().ok_or_else(|| {
                DcexError::InvalidInput(format!("Extended JSON field {key} must be a boolean"))
            })
        })
        .transpose()
}

pub(super) fn validate_positive_decimal(key: &str, value: &str) -> Result<()> {
    validate_decimal(key, value)?;
    let parsed = value.parse::<f64>().map_err(|error| {
        DcexError::InvalidInput(format!("invalid Extended decimal {key}: {error}"))
    })?;
    if !parsed.is_finite() || parsed <= 0.0 {
        return Err(DcexError::InvalidInput(format!(
            "Extended parameter {key} must be greater than zero"
        )));
    }
    Ok(())
}

pub(super) fn validate_non_negative_decimal(key: &str, value: &str) -> Result<()> {
    validate_decimal(key, value)?;
    let parsed = value.parse::<f64>().map_err(|error| {
        DcexError::InvalidInput(format!("invalid Extended decimal {key}: {error}"))
    })?;
    if !parsed.is_finite() || parsed < 0.0 {
        return Err(DcexError::InvalidInput(format!(
            "Extended parameter {key} must not be negative"
        )));
    }
    Ok(())
}

fn validate_decimal(key: &str, value: &str) -> Result<()> {
    let value = value.trim();
    let unsigned = value
        .strip_prefix('+')
        .or_else(|| value.strip_prefix('-'))
        .unwrap_or(value);
    let mut parts = unsigned.split('.');
    let integer = parts.next().unwrap_or_default();
    let fraction = parts.next();
    let valid = parts.next().is_none()
        && (!integer.is_empty() || fraction.is_some_and(|part| !part.is_empty()))
        && integer.chars().all(|character| character.is_ascii_digit())
        && fraction.is_none_or(|part| {
            !part.is_empty() && part.chars().all(|character| character.is_ascii_digit())
        });
    if !valid {
        return Err(DcexError::InvalidInput(format!(
            "invalid Extended decimal {key}: {value}"
        )));
    }
    Ok(())
}

pub(super) fn path_with_id(base: &str, id: &str) -> String {
    format!("{}/{}", base.trim_end_matches('/'), id)
}
