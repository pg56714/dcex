use std::collections::{BTreeSet, HashSet};

use crate::{DcexError, Result};

pub(super) struct LighterParams(Vec<(String, String)>);

impl LighterParams {
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
            .filter(|value| !value.trim().is_empty())
            .ok_or_else(|| DcexError::InvalidInput(format!("missing required parameter: {key}")))
    }

    pub(super) fn required_i64(&self, key: &str) -> Result<i64> {
        parse_i64(self.required(key)?, key)
    }

    pub(super) fn optional_i64(&self, key: &str) -> Result<Option<i64>> {
        self.get(key).map(|value| parse_i64(value, key)).transpose()
    }

    pub(super) fn optional_u64(&self, key: &str) -> Result<Option<u64>> {
        self.get(key).map(|value| parse_u64(value, key)).transpose()
    }

    pub(super) fn required_u64(&self, key: &str) -> Result<u64> {
        parse_u64(self.required(key)?, key)
    }

    pub(super) fn required_bool(&self, key: &str) -> Result<bool> {
        bool_value(self.required(key)?)
            .ok_or_else(|| DcexError::InvalidInput(format!("invalid boolean parameter: {key}")))
    }

    pub(super) fn optional_bool(&self, key: &str) -> Result<Option<bool>> {
        self.get(key)
            .map(|value| {
                bool_value(value).ok_or_else(|| {
                    DcexError::InvalidInput(format!("invalid boolean parameter: {key}"))
                })
            })
            .transpose()
    }

    pub(super) fn query(&self, keys: &[&str]) -> Vec<(String, String)> {
        self.query_renamed(&keys.iter().map(|key| (*key, *key)).collect::<Vec<_>>())
    }

    pub(super) fn query_renamed(&self, keys: &[(&str, &str)]) -> Vec<(String, String)> {
        let wanted = keys
            .iter()
            .map(|(source, _)| *source)
            .collect::<BTreeSet<_>>();
        let mut values = Vec::new();
        for (key, value) in &self.0 {
            if !wanted.contains(key.as_str()) {
                continue;
            }
            let target = keys
                .iter()
                .find(|(source, _)| source == key)
                .map(|(_, target)| *target)
                .unwrap_or(key);
            values.push((target.to_string(), value.clone()));
        }
        values
    }

    pub(super) fn ensure_allowed(&self, keys: &[&str]) -> Result<()> {
        self.ensure_allowed_with_repeated(keys, &[])
    }

    pub(super) fn ensure_allowed_with_repeated(
        &self,
        keys: &[&str],
        repeated: &[&str],
    ) -> Result<()> {
        let mut seen = HashSet::new();
        for (key, _) in &self.0 {
            if !keys.contains(&key.as_str()) {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Lighter parameter: {key}"
                )));
            }
            if !seen.insert(key.as_str()) && !repeated.contains(&key.as_str()) {
                return Err(DcexError::InvalidInput(format!(
                    "duplicate Lighter parameter: {key}"
                )));
            }
        }
        Ok(())
    }

    pub(super) fn values<'a>(&'a self, key: &'a str) -> impl Iterator<Item = &'a str> + 'a {
        self.0
            .iter()
            .filter(move |(candidate, _)| candidate == key)
            .map(|(_, value)| value.as_str())
    }

    pub(super) fn required_one_of<'a>(&'a self, key: &str, allowed: &[&str]) -> Result<&'a str> {
        let value = self.required(key)?;
        if !allowed.contains(&value) {
            return Err(DcexError::InvalidInput(format!(
                "invalid Lighter {key}: {value}; expected one of {}",
                allowed.join(", ")
            )));
        }
        Ok(value)
    }

    pub(super) fn optional_one_of<'a>(
        &'a self,
        key: &str,
        allowed: &[&str],
    ) -> Result<Option<&'a str>> {
        self.get(key)
            .map(|_| self.required_one_of(key, allowed))
            .transpose()
    }

    pub(super) fn required_u64_range(&self, key: &str, min: u64, max: u64) -> Result<u64> {
        let value = self.required_u64(key)?;
        ensure_u64_range(key, value, min, max)?;
        Ok(value)
    }

    pub(super) fn optional_u64_range(&self, key: &str, min: u64, max: u64) -> Result<Option<u64>> {
        let value = self.optional_u64(key)?;
        if let Some(value) = value {
            ensure_u64_range(key, value, min, max)?;
        }
        Ok(value)
    }

    pub(super) fn ensure_time_order(&self, start_key: &str, end_key: &str) -> Result<()> {
        let start = self.optional_u64(start_key)?;
        let end = self.optional_u64(end_key)?;
        if matches!((start, end), (Some(start), Some(end)) if start > end) {
            return Err(DcexError::InvalidInput(format!(
                "Lighter {start_key} must not be greater than {end_key}"
            )));
        }
        Ok(())
    }
}

pub(super) fn bool_value(value: &str) -> Option<bool> {
    match value {
        "true" | "True" | "1" => Some(true),
        "false" | "False" | "0" => Some(false),
        _ => None,
    }
}

pub(super) fn insert_optional_pair(
    values: &mut Vec<(String, String)>,
    key: &str,
    value: Option<impl ToString>,
) {
    if let Some(value) = value {
        values.push((key.to_string(), value.to_string()));
    }
}

pub(super) fn parse_i64(value: &str, key: &str) -> Result<i64> {
    value.parse::<i64>().map_err(|error| {
        DcexError::InvalidInput(format!("invalid integer parameter {key}: {error}"))
    })
}

pub(super) fn parse_u64(value: &str, key: &str) -> Result<u64> {
    value.parse::<u64>().map_err(|error| {
        DcexError::InvalidInput(format!("invalid integer parameter {key}: {error}"))
    })
}

fn ensure_u64_range(key: &str, value: u64, min: u64, max: u64) -> Result<()> {
    if value < min || value > max {
        return Err(DcexError::InvalidInput(format!(
            "Lighter parameter {key} must be between {min} and {max}"
        )));
    }
    Ok(())
}
