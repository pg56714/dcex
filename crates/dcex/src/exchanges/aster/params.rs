use serde_json::Value;

use crate::{DcexError, Result};

#[derive(Clone, Debug, Default)]
pub struct AsterAggTradesParams {
    pub from_id: Option<u64>,
    pub start_time: Option<u64>,
    pub end_time: Option<u64>,
    pub limit: Option<u64>,
}

#[derive(Clone, Debug, Default)]
pub struct AsterExchangeInfoParams<'a> {
    pub product_symbol: Option<&'a str>,
    pub symbols: Option<Vec<String>>,
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

    pub(super) fn values(&self, key: &str) -> Option<Vec<String>> {
        let values = self
            .0
            .iter()
            .filter(|(candidate, _)| candidate == key)
            .map(|(_, value)| value.clone())
            .collect::<Vec<_>>();
        if values.is_empty() {
            None
        } else {
            Some(values)
        }
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

    pub(super) fn u64(&self, key: &str) -> Result<Option<u64>> {
        self.get(key)
            .map(|value| {
                value.parse::<u64>().map_err(|error| {
                    DcexError::InvalidInput(format!("invalid integer parameter {key}: {error}"))
                })
            })
            .transpose()
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
