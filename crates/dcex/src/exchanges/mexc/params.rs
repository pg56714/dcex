use serde_json::{Map, Number, Value};

use crate::{DcexError, Result};

pub(super) struct MexcParams(Vec<(String, String)>);

impl MexcParams {
    pub(super) fn from_pairs(params: Vec<(String, String)>) -> Self {
        Self(params)
    }

    pub(super) fn into_inner(self) -> Vec<(String, String)> {
        self.0
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

    pub(super) fn body(
        &self,
        keys: &[&str],
        number_keys: &[&str],
        bool_keys: &[&str],
    ) -> Map<String, Value> {
        keys.iter()
            .filter_map(|key| {
                self.get(key).map(|value| {
                    (
                        (*key).to_string(),
                        body_value(value, number_keys.contains(key), bool_keys.contains(key)),
                    )
                })
            })
            .collect()
    }

    pub(super) fn json_required(&self, key: &str) -> Result<Value> {
        serde_json::from_str(self.required(key)?).map_err(|error| {
            DcexError::InvalidInput(format!("invalid JSON parameter {key}: {error}"))
        })
    }
}

pub(super) fn is_canonical_product_symbol(product_symbol: &str) -> bool {
    product_symbol.contains('-')
}

pub(super) fn exchange_symbol_fallback(product_symbol: &str, separator: &str) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) => format!("{base}{separator}{quote}"),
        _ => product_symbol.to_string(),
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

pub(super) fn insert_number(body: &mut Map<String, Value>, key: &str, value: i64) {
    body.insert(key.to_string(), Value::Number(Number::from(value)));
}

pub(super) fn require_one_identifier(params: &MexcParams, keys: &[&str]) -> Result<()> {
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

pub(super) fn body_value(value: &str, number: bool, boolean: bool) -> Value {
    if boolean {
        return match value {
            "true" | "True" | "TRUE" | "1" => Value::Bool(true),
            "false" | "False" | "FALSE" | "0" => Value::Bool(false),
            _ => Value::String(value.to_string()),
        };
    }
    if number {
        if let Ok(value) = value.parse::<i64>() {
            return Value::Number(Number::from(value));
        }
        if let Ok(value) = value.parse::<f64>() {
            if let Some(number) = Number::from_f64(value) {
                return Value::Number(number);
            }
        }
    }
    Value::String(value.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn requires_one_cancel_identifier() {
        let empty = MexcParams::from_pairs(Vec::new());
        assert!(require_one_identifier(&empty, &["orderId", "origClientOrderId"]).is_err());

        let order_id = MexcParams::from_pairs(vec![("orderId".to_string(), "1".to_string())]);
        assert!(require_one_identifier(&order_id, &["orderId", "origClientOrderId"]).is_ok());

        let blank = MexcParams::from_pairs(vec![("orderId".to_string(), " ".to_string())]);
        assert!(require_one_identifier(&blank, &["orderId", "origClientOrderId"]).is_err());
    }
}
