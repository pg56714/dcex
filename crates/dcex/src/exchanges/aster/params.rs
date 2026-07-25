use std::collections::HashSet;

use serde_json::{Map, Value};

use crate::{DcexError, Result};

#[derive(Clone, Debug, Default)]
pub struct AsterAggTradesParams {
    pub from_id: Option<u64>,
    pub start_time: Option<u64>,
    pub end_time: Option<u64>,
    pub limit: Option<u64>,
}

#[derive(Clone, Debug, Default)]
pub struct AsterFundingRateParams<'a> {
    pub product_symbol: Option<&'a str>,
    pub start_time: Option<u64>,
    pub end_time: Option<u64>,
    pub limit: Option<u64>,
}

#[derive(Clone, Debug, Default)]
pub struct AsterHistoricalTradesParams {
    pub limit: Option<u64>,
    pub from_id: Option<u64>,
}

#[derive(Clone, Debug, Default)]
pub struct AsterIndexPriceKlinesParams {
    pub start_time: Option<u64>,
    pub end_time: Option<u64>,
    pub limit: Option<u64>,
}

#[derive(Clone, Debug, Default)]
pub struct AsterKlinesParams {
    pub start_time: Option<u64>,
    pub end_time: Option<u64>,
    pub limit: Option<u64>,
}

#[derive(Clone, Debug, Default)]
pub struct AsterLimitParams {
    pub limit: Option<u64>,
}

#[derive(Clone, Debug, Default)]
pub struct AsterOptionalSymbolParams<'a> {
    pub product_symbol: Option<&'a str>,
}

pub(super) struct AsterParams(Vec<(String, String)>);

impl AsterParams {
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

    pub(super) fn from_json_object(object: &Map<String, Value>) -> Result<Self> {
        let mut params = Vec::with_capacity(object.len());
        for (key, value) in object {
            let value = match value {
                Value::String(value) => value.clone(),
                Value::Number(value) => value.to_string(),
                Value::Bool(value) => value.to_string(),
                Value::Null | Value::Array(_) | Value::Object(_) => {
                    return Err(DcexError::InvalidInput(format!(
                        "Aster order field {key} must be a scalar"
                    )));
                }
            };
            params.push((key.clone(), value));
        }
        Ok(Self(params))
    }

    pub(super) fn required(&self, key: &str) -> Result<&str> {
        let value = self
            .get(key)
            .ok_or_else(|| DcexError::InvalidInput(format!("missing required parameter: {key}")))?;
        if value.trim().is_empty() {
            return Err(DcexError::InvalidInput(format!(
                "Aster parameter {key} must not be empty"
            )));
        }
        Ok(value)
    }

    pub(super) fn required_any(&self, keys: &[&str]) -> Result<&str> {
        let value = self.get_any(keys).ok_or_else(|| {
            DcexError::InvalidInput(format!("missing required parameter: {}", keys.join(" or ")))
        })?;
        if value.trim().is_empty() {
            return Err(DcexError::InvalidInput(format!(
                "Aster parameter {} must not be empty",
                keys.join(" or ")
            )));
        }
        Ok(value)
    }

    pub(super) fn u64(&self, key: &str) -> Result<Option<u64>> {
        self.get(key)
            .map(|value| {
                value.parse::<u64>().map_err(|error| {
                    DcexError::InvalidInput(format!("invalid integer parameter {key}: {error}"))
                })
            })
            .transpose()
    }

    pub(super) fn ensure_allowed(&self, allowed: &[&str], repeated: &[&str]) -> Result<()> {
        let mut seen = HashSet::new();
        for (key, value) in &self.0 {
            if !allowed.contains(&key.as_str()) {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Aster parameter: {key}"
                )));
            }
            if value.trim().is_empty() {
                return Err(DcexError::InvalidInput(format!(
                    "Aster parameter {key} must not be empty"
                )));
            }
            if !repeated.contains(&key.as_str()) && !seen.insert(key.as_str()) {
                return Err(DcexError::InvalidInput(format!(
                    "duplicate Aster parameter: {key}"
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
                    "invalid Aster {key}: {value}; expected one of {}",
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
            if !matches!(value.to_ascii_lowercase().as_str(), "true" | "false") {
                return Err(DcexError::InvalidInput(format!(
                    "invalid Aster boolean {key}: {value}"
                )));
            }
        }
        Ok(())
    }

    pub(super) fn optional_u64_range(&self, key: &str, min: u64, max: u64) -> Result<()> {
        if let Some(value) = self.u64(key)? {
            if value < min || value > max {
                return Err(DcexError::InvalidInput(format!(
                    "Aster parameter {key} must be between {min} and {max}"
                )));
            }
        }
        Ok(())
    }

    pub(super) fn required_u64_range(&self, key: &str, min: u64, max: u64) -> Result<()> {
        self.required(key)?;
        self.optional_u64_range(key, min, max)
    }

    pub(super) fn optional_decimal(&self, key: &str) -> Result<()> {
        if let Some(value) = self.get(key) {
            validate_decimal(key, value)?;
        }
        Ok(())
    }

    pub(super) fn optional_non_negative_decimal(&self, key: &str) -> Result<()> {
        if let Some(value) = self.get(key) {
            validate_decimal(key, value)?;
            if value.starts_with('-') {
                return Err(DcexError::InvalidInput(format!(
                    "Aster parameter {key} must not be negative"
                )));
            }
        }
        Ok(())
    }

    pub(super) fn required_positive_decimal(&self, key: &str) -> Result<()> {
        let value = self.required(key)?;
        validate_decimal(key, value)?;
        let parsed = value.parse::<f64>().map_err(|error| {
            DcexError::InvalidInput(format!("invalid Aster decimal {key}: {error}"))
        })?;
        if !parsed.is_finite() || parsed <= 0.0 {
            return Err(DcexError::InvalidInput(format!(
                "Aster parameter {key} must be greater than zero"
            )));
        }
        Ok(())
    }

    pub(super) fn optional_decimal_range(&self, key: &str, min: f64, max: f64) -> Result<()> {
        if let Some(value) = self.get(key) {
            validate_decimal(key, value)?;
            let parsed = value.parse::<f64>().map_err(|error| {
                DcexError::InvalidInput(format!("invalid Aster decimal {key}: {error}"))
            })?;
            if !parsed.is_finite() || parsed < min || parsed > max {
                return Err(DcexError::InvalidInput(format!(
                    "Aster parameter {key} must be between {min} and {max}"
                )));
            }
        }
        Ok(())
    }

    pub(super) fn ensure_time_order(&self, start_key: &str, end_key: &str) -> Result<()> {
        let start = self.u64(start_key)?;
        let end = self.u64(end_key)?;
        if start.zip(end).is_some_and(|(start, end)| start > end) {
            return Err(DcexError::InvalidInput(format!(
                "Aster {start_key} must not be after {end_key}"
            )));
        }
        Ok(())
    }

    pub(super) fn ensure_max_time_span(
        &self,
        start_key: &str,
        end_key: &str,
        max_millis: u64,
    ) -> Result<()> {
        self.ensure_time_order(start_key, end_key)?;
        if let (Some(start), Some(end)) = (self.u64(start_key)?, self.u64(end_key)?) {
            if end - start > max_millis {
                return Err(DcexError::InvalidInput(format!(
                    "Aster {start_key}/{end_key} range exceeds {max_millis} milliseconds"
                )));
            }
        }
        Ok(())
    }

    pub(super) fn ensure_absent_with(&self, key: &str, other_keys: &[&str]) -> Result<()> {
        if self.get(key).is_some() && other_keys.iter().any(|other| self.get(other).is_some()) {
            return Err(DcexError::InvalidInput(format!(
                "Aster parameter {key} cannot be combined with {}",
                other_keys.join(" or ")
            )));
        }
        Ok(())
    }

    pub(super) fn only(&self, keys: &[&str]) -> Vec<(String, String)> {
        self.0
            .iter()
            .filter(|(key, _)| keys.contains(&key.as_str()))
            .cloned()
            .collect()
    }

    pub(super) fn json_required(&self, key: &str) -> Result<Value> {
        serde_json::from_str(self.required(key)?).map_err(|error| {
            DcexError::InvalidInput(format!("invalid JSON parameter {key}: {error}"))
        })
    }
}

fn validate_decimal(key: &str, value: &str) -> Result<()> {
    let value = value.trim();
    let value = value
        .strip_prefix('+')
        .or_else(|| value.strip_prefix('-'))
        .unwrap_or(value);
    let mut parts = value.split('.');
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
            "invalid Aster decimal {key}: {value}"
        )));
    }
    Ok(())
}

pub(super) fn push_optional_display<T: ToString>(
    params: &mut Vec<(String, String)>,
    key: &str,
    value: Option<T>,
) {
    if let Some(value) = value {
        params.push((key.to_string(), value.to_string()));
    }
}

pub(super) fn json_value_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.clone(),
        _ => value.to_string(),
    }
}
