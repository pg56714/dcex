use serde_json::{Map, Number, Value};

use crate::{DcexError, Result};

#[derive(Clone, Debug, Default)]
pub struct BitmartContractsDetailsParams<'a> {
    pub product_symbol: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct BitmartFundingRateHistoryParams<'a> {
    pub limit: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct BitmartSpotKlineParams<'a> {
    pub before: Option<&'a str>,
    pub after: Option<&'a str>,
    pub limit: Option<&'a str>,
}

pub(super) struct BitmartParams(Vec<(String, String)>);

impl BitmartParams {
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

    pub(super) fn body(&self, keys: &[&str]) -> Map<String, Value> {
        keys.iter()
            .filter_map(|key| {
                self.get(key)
                    .map(|value| ((*key).to_string(), Value::String(value.to_string())))
            })
            .collect()
    }
}

pub(super) fn is_canonical_product_symbol(product_symbol: &str) -> bool {
    product_symbol.contains('-')
}

pub(super) fn exchange_symbol_fallback(product_symbol: &str, spot: bool) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) if spot => format!("{base}_{quote}"),
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

pub(super) fn insert_optional_integer(
    body: &mut Map<String, Value>,
    key: &str,
    value: Option<&str>,
) {
    if let Some(value) = value {
        body.insert(key.to_string(), integer_or_string(value));
    }
}

pub(super) fn boolean_or_string(value: &str) -> Value {
    match value {
        "true" | "True" => Value::Bool(true),
        "false" | "False" => Value::Bool(false),
        _ => Value::String(value.to_string()),
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

pub(super) fn bitmart_timeframe(timeframe: &str) -> Result<u32> {
    match timeframe {
        "1m" => Ok(1),
        "5m" => Ok(5),
        "15m" => Ok(15),
        "30m" => Ok(30),
        "1h" => Ok(60),
        "2h" => Ok(120),
        "4h" => Ok(240),
        "1d" => Ok(1440),
        "1w" => Ok(10080),
        "1M" => Ok(43200),
        _ => Err(DcexError::InvalidInput(
            "timeframe not supported".to_string(),
        )),
    }
}
