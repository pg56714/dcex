use std::collections::BTreeSet;

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
