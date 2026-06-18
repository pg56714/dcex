use serde_json::{Map, Number, Value};

use crate::{DcexError, Result};

pub(super) struct KucoinParams(Vec<(String, String)>);

impl KucoinParams {
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

pub(super) fn take_param(params: &mut Vec<(String, String)>, key: &str) -> Option<String> {
    params
        .iter()
        .position(|(param_key, _)| param_key == key)
        .map(|index| params.remove(index).1)
}

pub(super) fn is_canonical_product_symbol(product_symbol: &str) -> bool {
    product_symbol.contains('-')
}

pub(super) fn exchange_symbol_fallback(product_symbol: &str, futures: bool) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) if futures => {
            format!("{}{}M", kucoin_contract_asset(base), quote)
        }
        (Some(base), Some(quote), Some(_kind)) => format!("{base}-{quote}"),
        _ => product_symbol.to_string(),
    }
}

fn kucoin_contract_asset(asset: &str) -> &str {
    match asset {
        "BTC" => "XBT",
        other => other,
    }
}

pub(super) fn normalize_spot_timeframe(params: &mut [(String, String)]) -> Result<()> {
    for (key, value) in params.iter_mut() {
        if key == "timeframe" {
            *key = "type".to_string();
            *value = kucoin_spot_timeframe(value)?;
        }
    }
    Ok(())
}

pub(super) fn normalize_futures_timeframe(params: &mut [(String, String)]) -> Result<()> {
    for (key, value) in params.iter_mut() {
        if key == "timeframe" {
            *key = "granularity".to_string();
            *value = kucoin_futures_granularity(value)?.to_string();
        }
    }
    Ok(())
}

fn kucoin_spot_timeframe(timeframe: &str) -> Result<String> {
    let value = match timeframe {
        "1m" => "1min",
        "3m" => "3min",
        "5m" => "5min",
        "15m" => "15min",
        "30m" => "30min",
        "1h" => "1hour",
        "2h" => "2hour",
        "4h" => "4hour",
        "6h" => "6hour",
        "8h" => "8hour",
        "12h" => "12hour",
        "1d" => "1day",
        "1w" => "1week",
        "1M" => "1month",
        _ => {
            return Err(DcexError::InvalidInput(
                "timeframe not supported".to_string(),
            ))
        }
    };
    Ok(value.to_string())
}

fn kucoin_futures_granularity(timeframe: &str) -> Result<u64> {
    match timeframe {
        "1m" => Ok(60),
        "5m" => Ok(300),
        "15m" => Ok(900),
        "30m" => Ok(1800),
        "1h" => Ok(3600),
        "2h" => Ok(7200),
        "4h" => Ok(14400),
        "8h" => Ok(28800),
        "12h" => Ok(43200),
        "1d" => Ok(86400),
        "1w" => Ok(604800),
        _ => Err(DcexError::InvalidInput(
            "timeframe not supported".to_string(),
        )),
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

pub(super) fn insert_optional_bool(body: &mut Map<String, Value>, key: &str, value: Option<&str>) {
    if let Some(value) = value.and_then(bool_value) {
        body.insert(key.to_string(), Value::Bool(value));
    }
}

pub(super) fn insert_required_string(body: &mut Map<String, Value>, key: &str, value: &str) {
    body.insert(key.to_string(), Value::String(value.to_string()));
}

pub(super) fn insert_required_integer(body: &mut Map<String, Value>, key: &str, value: &str) {
    body.insert(key.to_string(), integer_or_string(value));
}

pub(super) fn insert_truthy_bool(body: &mut Map<String, Value>, key: &str, value: bool) {
    if value {
        body.insert(key.to_string(), Value::Bool(true));
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

pub(super) fn json_value_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.to_string(),
        Value::Number(value) => value.to_string(),
        Value::Bool(value) => value.to_string(),
        Value::Null => String::new(),
        Value::Array(_) | Value::Object(_) => value.to_string(),
    }
}
