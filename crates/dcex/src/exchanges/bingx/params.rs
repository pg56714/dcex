use serde_json::{Number, Value};

use crate::common::OrderSide;
use crate::{DcexError, Result};

use super::signing::json_value_string;

const BATCH_NUMERIC_FIELDS: &[&str] = &[
    "quantity",
    "quoteOrderQty",
    "price",
    "stopPrice",
    "priceRate",
    "activationPrice",
];

pub(super) struct BingxParams(Vec<(String, String)>);

impl BingxParams {
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
            .map(|(key, value)| (normalize_key(&key).to_string(), value))
            .collect()
    }

    pub(super) fn ensure_allowed(&self, keys: &[&str]) -> Result<()> {
        if let Some((key, _)) = self.0.iter().find(|(key, _)| !keys.contains(&key.as_str())) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported BingX parameter: {key}"
            )));
        }
        Ok(())
    }
}

pub(super) fn normalize_key(key: &str) -> &str {
    match key {
        "type_" => "type",
        _ => key,
    }
}

pub(super) fn is_canonical_product_symbol(product_symbol: &str) -> bool {
    product_symbol.split('-').count() >= 3
}

pub(super) fn exchange_symbol_fallback(product_symbol: &str) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) => format!("{base}-{quote}"),
        _ => product_symbol.to_string(),
    }
}

pub(super) fn push_optional(query: &mut Vec<(String, String)>, key: &str, value: Option<&str>) {
    if let Some(value) = value {
        query.push((key.to_string(), value.to_string()));
    }
}

pub(super) fn push_optional_value<T: ToString>(
    query: &mut Vec<(String, String)>,
    key: &str,
    value: Option<T>,
) {
    if let Some(value) = value {
        query.push((key.to_string(), value.to_string()));
    }
}

pub(super) fn normalize_side(value: &str) -> Result<String> {
    Ok(OrderSide::parse(value)?.to_exchange("bingx")?.to_string())
}

pub(super) fn bool_or_string(value: &str) -> String {
    match value {
        "True" => "true".to_string(),
        "False" => "false".to_string(),
        _ => value.to_string(),
    }
}

pub(super) fn batch_orders_query(value: &str) -> Result<String> {
    let mut value = serde_json::from_str::<Value>(value).map_err(|error| {
        DcexError::InvalidInput(format!("invalid batch order JSON parameter: {error}"))
    })?;
    let Value::Array(orders) = &value else {
        return Err(DcexError::InvalidInput(
            "BingX batch orders must be a JSON array".to_string(),
        ));
    };
    if orders.is_empty() || orders.len() > 5 {
        return Err(DcexError::InvalidInput(
            "BingX batch orders must contain between 1 and 5 orders".to_string(),
        ));
    }
    for order in orders {
        let Value::Object(order) = order else {
            return Err(DcexError::InvalidInput(
                "each BingX batch order must be a JSON object".to_string(),
            ));
        };
        for key in ["symbol", "side", "type"] {
            if !order
                .get(key)
                .and_then(Value::as_str)
                .is_some_and(|value| !value.trim().is_empty())
            {
                return Err(DcexError::InvalidInput(format!(
                    "BingX batch order is missing required field: {key}"
                )));
            }
        }
    }
    normalize_batch_value(&mut value);
    serde_json::to_string(&value).map_err(|error| DcexError::Decode(error.to_string()))
}

pub(super) fn require_one_identifier(params: &BingxParams, keys: &[&str]) -> Result<()> {
    if keys.iter().any(|key| {
        params
            .get(key)
            .is_some_and(|value| !value.trim().is_empty())
    }) {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "one of {} is required",
        keys.join(", ")
    )))
}

pub(super) fn require_pair_or_identifier(
    params: &BingxParams,
    first: &str,
    second: &str,
    identifier: &str,
) -> Result<()> {
    let has_first = params
        .get(first)
        .is_some_and(|value| !value.trim().is_empty());
    let has_second = params
        .get(second)
        .is_some_and(|value| !value.trim().is_empty());
    let has_identifier = params
        .get(identifier)
        .is_some_and(|value| !value.trim().is_empty());
    if has_identifier || (has_first && has_second) {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "BingX requires either {identifier} or both {first} and {second}"
    )))
}

pub(super) fn validate_enum(params: &BingxParams, key: &str, allowed: &[&str]) -> Result<()> {
    let Some(value) = params.get(key) else {
        return Ok(());
    };
    if allowed.contains(&value) {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "unsupported BingX {key}: {value}"
    )))
}

pub(super) fn validate_u64_range(
    params: &BingxParams,
    key: &str,
    minimum: u64,
    maximum: u64,
) -> Result<()> {
    let Some(value) = params.get(key) else {
        return Ok(());
    };
    let parsed = value.parse::<u64>().map_err(|_| {
        DcexError::InvalidInput(format!("BingX parameter {key} must be an integer"))
    })?;
    if !(minimum..=maximum).contains(&parsed) {
        return Err(DcexError::InvalidInput(format!(
            "BingX parameter {key} must be between {minimum} and {maximum}"
        )));
    }
    Ok(())
}

pub(super) fn validate_time_range(
    params: &BingxParams,
    start_key: &str,
    end_key: &str,
    maximum_span_ms: Option<u64>,
) -> Result<()> {
    validate_u64_range(params, start_key, 0, u64::MAX)?;
    validate_u64_range(params, end_key, 0, u64::MAX)?;
    let (Some(start), Some(end)) = (params.get(start_key), params.get(end_key)) else {
        return Ok(());
    };
    let start = start.parse::<u64>().map_err(|_| {
        DcexError::InvalidInput(format!("BingX parameter {start_key} must be an integer"))
    })?;
    let end = end.parse::<u64>().map_err(|_| {
        DcexError::InvalidInput(format!("BingX parameter {end_key} must be an integer"))
    })?;
    if end < start {
        return Err(DcexError::InvalidInput(format!(
            "BingX parameter {end_key} must be greater than or equal to {start_key}"
        )));
    }
    if maximum_span_ms.is_some_and(|maximum| end - start > maximum) {
        return Err(DcexError::InvalidInput(format!(
            "BingX time range between {start_key} and {end_key} is too large"
        )));
    }
    Ok(())
}

pub(super) fn validate_page_window(
    params: &BingxParams,
    page_key: &str,
    size_key: &str,
    default_page: u64,
    default_size: u64,
    maximum_offset: u64,
) -> Result<()> {
    let page = params
        .get(page_key)
        .map(str::parse::<u64>)
        .transpose()
        .map_err(|_| {
            DcexError::InvalidInput(format!("BingX parameter {page_key} must be an integer"))
        })?
        .unwrap_or(default_page);
    let size = params
        .get(size_key)
        .map(str::parse::<u64>)
        .transpose()
        .map_err(|_| {
            DcexError::InvalidInput(format!("BingX parameter {size_key} must be an integer"))
        })?
        .unwrap_or(default_size);
    if page.saturating_mul(size) > maximum_offset {
        return Err(DcexError::InvalidInput(format!(
            "BingX requires {page_key} * {size_key} <= {maximum_offset}"
        )));
    }
    Ok(())
}

pub(super) fn validate_positive_number(params: &BingxParams, key: &str) -> Result<()> {
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
        "BingX parameter {key} must be a positive finite number"
    )))
}

pub(super) fn validate_bool(params: &BingxParams, key: &str) -> Result<()> {
    let Some(value) = params.get(key) else {
        return Ok(());
    };
    if matches!(value, "true" | "True" | "false" | "False") {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "BingX parameter {key} must be true or false"
    )))
}

pub(super) fn validate_client_id(
    params: &BingxParams,
    key: &str,
    restricted_charset: bool,
) -> Result<()> {
    let Some(value) = params.get(key) else {
        return Ok(());
    };
    let valid_charset = !restricted_charset
        || value
            .chars()
            .all(|character| character.is_ascii_alphanumeric() || character == '_');
    if (1..=40).contains(&value.chars().count()) && valid_charset {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "BingX parameter {key} must be 1-40 characters{}",
        if restricted_charset {
            " using only letters, numbers, and underscore"
        } else {
            ""
        }
    )))
}

pub(super) fn validate_json_object(params: &BingxParams, key: &str) -> Result<()> {
    let Some(value) = params.get(key) else {
        return Ok(());
    };
    if serde_json::from_str::<Value>(value).is_ok_and(|value| value.is_object()) {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "BingX parameter {key} must be a JSON object"
    )))
}

fn normalize_batch_value(value: &mut Value) {
    let Value::Array(orders) = value else {
        return;
    };
    for order in orders {
        let Value::Object(order) = order else {
            continue;
        };
        for field in BATCH_NUMERIC_FIELDS {
            if let Some(Value::String(raw)) = order.get(*field) {
                if let Ok(number) = raw.parse::<f64>() {
                    if let Some(number) = Number::from_f64(number) {
                        order.insert((*field).to_string(), Value::Number(number));
                    }
                }
            }
        }
    }
}

pub(super) fn comma_list(value: &str) -> String {
    if let Ok(Value::Array(values)) = serde_json::from_str::<Value>(value) {
        return values
            .iter()
            .map(json_value_string)
            .collect::<Vec<_>>()
            .join(",");
    }
    value.to_string()
}

pub(super) fn python_list_string(value: &str) -> String {
    if let Ok(Value::Array(values)) = serde_json::from_str::<Value>(value) {
        let values = values
            .iter()
            .map(json_value_string)
            .collect::<Vec<_>>()
            .join(",");
        return format!("[{values}]");
    }
    value.replace(['\'', ' '], "")
}
