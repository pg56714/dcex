use serde_json::{Map, Number, Value};

use crate::{DcexError, Result};

#[derive(Clone, Debug, Default)]
pub struct BitmexInstrumentInfoParams<'a> {
    pub product_symbol: Option<&'a str>,
    pub filter: Option<&'a str>,
    pub columns: Option<&'a str>,
    pub count: Option<&'a str>,
    pub start: Option<&'a str>,
    pub reverse: Option<&'a str>,
    pub start_time: Option<&'a str>,
    pub end_time: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct BitmexOrderbookParams<'a> {
    pub depth: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct BitmexTableParams<'a> {
    pub product_symbol: Option<&'a str>,
    pub symbol: Option<&'a str>,
    pub filter: Option<&'a str>,
    pub columns: Option<&'a str>,
    pub count: Option<&'a str>,
    pub start: Option<&'a str>,
    pub reverse: Option<&'a str>,
    pub start_time: Option<&'a str>,
    pub end_time: Option<&'a str>,
    pub pool: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct BitmexBucketParams<'a> {
    pub bin_size: Option<&'a str>,
    pub partial: Option<&'a str>,
    pub symbol: Option<&'a str>,
    pub filter: Option<&'a str>,
    pub columns: Option<&'a str>,
    pub count: Option<&'a str>,
    pub start: Option<&'a str>,
    pub reverse: Option<&'a str>,
    pub start_time: Option<&'a str>,
    pub end_time: Option<&'a str>,
    pub pool: Option<&'a str>,
}

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
            .filter(|value| !value.trim().is_empty())
            .ok_or_else(|| DcexError::InvalidInput(format!("missing required parameter: {key}")))
    }

    pub(super) fn only(&self, keys: &[&str]) -> Vec<(String, String)> {
        self.0
            .iter()
            .filter(|(key, _)| keys.contains(&key.as_str()))
            .cloned()
            .collect()
    }

    pub(super) fn ensure_allowed(&self, keys: &[&str]) -> Result<()> {
        if let Some((key, _)) = self.0.iter().find(|(key, _)| !keys.contains(&key.as_str())) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported BitMEX parameter: {key}"
            )));
        }
        Ok(())
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

pub(super) fn validate_enum(params: &BitmexParams, key: &str, allowed: &[&str]) -> Result<()> {
    let Some(value) = params.get(key) else {
        return Ok(());
    };
    if allowed.contains(&value) {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "unsupported BitMEX {key}: {value}"
    )))
}

pub(super) fn validate_comma_separated_enum(
    params: &BitmexParams,
    key: &str,
    allowed: &[&str],
) -> Result<()> {
    let Some(value) = params.get(key) else {
        return Ok(());
    };
    if !value.trim().is_empty()
        && value
            .split(',')
            .map(str::trim)
            .all(|item| allowed.contains(&item))
    {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "unsupported BitMEX {key}: {value}"
    )))
}

pub(super) fn validate_u64_range(
    params: &BitmexParams,
    key: &str,
    minimum: u64,
    maximum: u64,
) -> Result<()> {
    let Some(value) = params.get(key) else {
        return Ok(());
    };
    let parsed = value.parse::<u64>().map_err(|_| {
        DcexError::InvalidInput(format!("BitMEX parameter {key} must be an integer"))
    })?;
    if !(minimum..=maximum).contains(&parsed) {
        return Err(DcexError::InvalidInput(format!(
            "BitMEX parameter {key} must be between {minimum} and {maximum}"
        )));
    }
    Ok(())
}

pub(super) fn validate_number(params: &BitmexParams, key: &str) -> Result<()> {
    let Some(value) = params.get(key) else {
        return Ok(());
    };
    if value.parse::<f64>().is_ok_and(|number| number.is_finite()) {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "BitMEX parameter {key} must be a finite number"
    )))
}

pub(super) fn validate_i64(params: &BitmexParams, key: &str) -> Result<()> {
    let Some(value) = params.get(key) else {
        return Ok(());
    };
    if value.parse::<i64>().is_ok() {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "BitMEX parameter {key} must be an integer"
    )))
}

pub(super) fn validate_bool(params: &BitmexParams, key: &str) -> Result<()> {
    let Some(value) = params.get(key) else {
        return Ok(());
    };
    if matches!(value, "true" | "True" | "false" | "False") {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "BitMEX parameter {key} must be true or false"
    )))
}

pub(super) fn validate_json_object(params: &BitmexParams, key: &str) -> Result<()> {
    let Some(value) = params.get(key) else {
        return Ok(());
    };
    if serde_json::from_str::<Value>(value).is_ok_and(|value| value.is_object()) {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "BitMEX parameter {key} must be a JSON object"
    )))
}

pub(super) fn require_at_most_one(params: &BitmexParams, keys: &[&str]) -> Result<()> {
    let supplied = keys.iter().filter(|key| params.get(key).is_some()).count();
    if supplied <= 1 {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "BitMEX parameters {} are mutually exclusive",
        keys.join(", ")
    )))
}
