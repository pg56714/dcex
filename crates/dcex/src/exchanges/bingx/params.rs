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
            .ok_or_else(|| DcexError::InvalidInput(format!("missing required parameter: {key}")))
    }

    pub(super) fn required_any(&self, keys: &[&str]) -> Result<&str> {
        keys.iter().find_map(|key| self.get(key)).ok_or_else(|| {
            DcexError::InvalidInput(format!("missing required parameter: {}", keys.join(" or ")))
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
    normalize_batch_value(&mut value);
    serde_json::to_string(&value).map_err(|error| DcexError::Decode(error.to_string()))
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
