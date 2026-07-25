use std::sync::atomic::{AtomicU64, Ordering};

use serde_json::{Map, Value};

use crate::{DcexError, Result};

static CLIENT_OID_SEQUENCE: AtomicU64 = AtomicU64::new(1);

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
            .filter(|value| !value.trim().is_empty())
            .ok_or_else(|| DcexError::InvalidInput(format!("missing required parameter: {key}")))
    }

    pub(super) fn required_any(&self, keys: &[&str]) -> Result<&str> {
        keys.iter()
            .find_map(|key| self.get(key).filter(|value| !value.trim().is_empty()))
            .ok_or_else(|| {
                DcexError::InvalidInput(format!(
                    "missing required parameter: {}",
                    keys.join(" or ")
                ))
            })
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
                "unsupported KuCoin parameter: {key}"
            )));
        }
        Ok(())
    }

    pub(super) fn body(
        &self,
        string_keys: &[&str],
        integer_keys: &[&str],
        bool_keys: &[&str],
    ) -> Result<Map<String, Value>> {
        let mut body = Map::new();
        for key in string_keys {
            insert_optional_string(&mut body, key, self.get(key));
        }
        for key in integer_keys {
            if let Some(value) = self.get(key) {
                let value = value.parse::<i64>().map_err(|_| {
                    DcexError::InvalidInput(format!("KuCoin parameter {key} must be an integer"))
                })?;
                body.insert(key.to_string(), Value::Number(value.into()));
            }
        }
        for key in bool_keys {
            if let Some(value) = self.get(key) {
                let value = bool_value(value).ok_or_else(|| {
                    DcexError::InvalidInput(format!("KuCoin parameter {key} must be true or false"))
                })?;
                body.insert(key.to_string(), Value::Bool(value));
            }
        }
        Ok(body)
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
        } else if key == "type" {
            validate_spot_interval(value)?;
        }
    }
    Ok(())
}

pub(super) fn normalize_futures_timeframe(params: &mut [(String, String)]) -> Result<()> {
    for (key, value) in params.iter_mut() {
        if key == "timeframe" {
            *key = "granularity".to_string();
            *value = kucoin_futures_granularity(value)?.to_string();
        } else if key == "granularity" {
            let granularity = value.parse::<u64>().map_err(|_| {
                DcexError::InvalidInput(
                    "KuCoin futures granularity must be an integer number of minutes".to_string(),
                )
            })?;
            if !matches!(
                granularity,
                1 | 5 | 15 | 30 | 60 | 120 | 240 | 480 | 720 | 1440 | 10080
            ) {
                return Err(DcexError::InvalidInput(
                    "KuCoin futures granularity is not supported".to_string(),
                ));
            }
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

pub(super) fn generate_client_oid() -> String {
    let timestamp = crate::exchange::unix_timestamp_ms().unwrap_or_default();
    let sequence = CLIENT_OID_SEQUENCE.fetch_add(1, Ordering::Relaxed);
    format!("dcex-{timestamp}-{sequence}")
}

fn validate_spot_interval(interval: &str) -> Result<()> {
    if matches!(
        interval,
        "1min"
            | "3min"
            | "5min"
            | "15min"
            | "30min"
            | "1hour"
            | "2hour"
            | "4hour"
            | "6hour"
            | "8hour"
            | "12hour"
            | "1day"
            | "1week"
            | "1month"
    ) {
        return Ok(());
    }
    Err(DcexError::InvalidInput(
        "KuCoin spot kline type is not supported".to_string(),
    ))
}

fn kucoin_futures_granularity(timeframe: &str) -> Result<u64> {
    match timeframe {
        "1m" => Ok(1),
        "5m" => Ok(5),
        "15m" => Ok(15),
        "30m" => Ok(30),
        "1h" => Ok(60),
        "2h" => Ok(120),
        "4h" => Ok(240),
        "8h" => Ok(480),
        "12h" => Ok(720),
        "1d" => Ok(1440),
        "1w" => Ok(10080),
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

pub(super) fn insert_required_string(body: &mut Map<String, Value>, key: &str, value: &str) {
    body.insert(key.to_string(), Value::String(value.to_string()));
}

pub(super) fn insert_truthy_bool(body: &mut Map<String, Value>, key: &str, value: bool) {
    if value {
        body.insert(key.to_string(), Value::Bool(true));
    }
}

pub(super) fn bool_value(value: &str) -> Option<bool> {
    match value {
        "true" | "True" | "1" => Some(true),
        "false" | "False" | "0" => Some(false),
        _ => None,
    }
}

pub(super) fn validate_enum(params: &KucoinParams, key: &str, allowed: &[&str]) -> Result<()> {
    let Some(value) = params.get(key) else {
        return Ok(());
    };
    if allowed.contains(&value) {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "unsupported KuCoin {key}: {value}"
    )))
}

pub(super) fn validate_positive_number(params: &KucoinParams, key: &str) -> Result<()> {
    let Some(value) = params.get(key) else {
        return Ok(());
    };
    if value
        .parse::<f64>()
        .is_ok_and(|number| number.is_finite() && number > 0.0)
    {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "KuCoin parameter {key} must be a positive finite number"
    )))
}

pub(super) fn validate_positive_u64(params: &KucoinParams, key: &str) -> Result<()> {
    let Some(value) = params.get(key) else {
        return Ok(());
    };
    if value.parse::<u64>().is_ok_and(|number| number > 0) {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "KuCoin parameter {key} must be a positive integer"
    )))
}

pub(super) fn validate_u64_range(
    params: &KucoinParams,
    key: &str,
    minimum: u64,
    maximum: u64,
) -> Result<()> {
    let Some(value) = params.get(key) else {
        return Ok(());
    };
    let parsed = value.parse::<u64>().map_err(|_| {
        DcexError::InvalidInput(format!("KuCoin parameter {key} must be an integer"))
    })?;
    if !(minimum..=maximum).contains(&parsed) {
        return Err(DcexError::InvalidInput(format!(
            "KuCoin parameter {key} must be between {minimum} and {maximum}"
        )));
    }
    Ok(())
}

pub(super) fn validate_time_range(
    params: &KucoinParams,
    start_key: &str,
    end_key: &str,
    maximum_span_ms: Option<u64>,
) -> Result<()> {
    let start = params
        .get(start_key)
        .map(str::parse::<u64>)
        .transpose()
        .map_err(|_| {
            DcexError::InvalidInput(format!("KuCoin parameter {start_key} must be an integer"))
        })?;
    let end = params
        .get(end_key)
        .map(str::parse::<u64>)
        .transpose()
        .map_err(|_| {
            DcexError::InvalidInput(format!("KuCoin parameter {end_key} must be an integer"))
        })?;
    let (Some(start), Some(end)) = (start, end) else {
        return Ok(());
    };
    if end < start {
        return Err(DcexError::InvalidInput(format!(
            "KuCoin parameter {end_key} must be greater than or equal to {start_key}"
        )));
    }
    if maximum_span_ms.is_some_and(|maximum| end - start > maximum) {
        return Err(DcexError::InvalidInput(format!(
            "KuCoin time range between {start_key} and {end_key} is too large"
        )));
    }
    Ok(())
}

pub(super) fn validate_client_oid(params: &KucoinParams, key: &str) -> Result<()> {
    let Some(value) = params.get(key) else {
        return Ok(());
    };
    if (1..=40).contains(&value.len())
        && value
            .chars()
            .all(|character| character.is_ascii_alphanumeric() || matches!(character, '_' | '-'))
    {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "KuCoin parameter {key} must be 1-40 ASCII letters, numbers, underscores, or hyphens"
    )))
}

pub(super) fn validate_text_length(
    params: &KucoinParams,
    key: &str,
    maximum: usize,
    ascii_only: bool,
) -> Result<()> {
    let Some(value) = params.get(key) else {
        return Ok(());
    };
    let valid_charset = !ascii_only || value.is_ascii();
    if !value.is_empty() && value.chars().count() <= maximum && valid_charset {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "KuCoin parameter {key} must contain 1-{maximum} {}characters",
        if ascii_only { "ASCII " } else { "" }
    )))
}

pub(super) fn require_exactly_one(params: &KucoinParams, keys: &[&str]) -> Result<()> {
    let supplied = keys
        .iter()
        .filter(|key| {
            params
                .get(key)
                .is_some_and(|value| !value.trim().is_empty())
        })
        .count();
    if supplied == 1 {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "KuCoin requires exactly one of {}",
        keys.join(", ")
    )))
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
