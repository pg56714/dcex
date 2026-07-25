use crate::{DcexError, Result};

use std::collections::HashSet;

use super::msgpack::{parse_ordered_json, OrderedValue};

pub(super) struct HyperliquidParams(pub(super) Vec<(String, String)>);

impl HyperliquidParams {
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
        let value = self
            .get(key)
            .ok_or_else(|| DcexError::InvalidInput(format!("missing required parameter: {key}")))?;
        if value.trim().is_empty() {
            return Err(DcexError::InvalidInput(format!(
                "parameter {key} must not be empty"
            )));
        }
        Ok(value)
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

    pub(super) fn required_i64(&self, key: &str) -> Result<i64> {
        self.required(key)?.parse::<i64>().map_err(|error| {
            DcexError::InvalidInput(format!("invalid integer parameter {key}: {error}"))
        })
    }

    pub(super) fn required_u64(&self, key: &str) -> Result<u64> {
        self.required(key)?.parse::<u64>().map_err(|error| {
            DcexError::InvalidInput(format!("invalid unsigned integer parameter {key}: {error}"))
        })
    }

    pub(super) fn optional_u64(&self, key: &str) -> Result<Option<u64>> {
        self.get(key)
            .map(|value| {
                value.parse::<u64>().map_err(|error| {
                    DcexError::InvalidInput(format!("invalid integer parameter {key}: {error}"))
                })
            })
            .transpose()
    }

    pub(super) fn ordered_json_required(&self, key: &str) -> Result<OrderedValue> {
        parse_ordered_json(self.required(key)?, key)
    }

    pub(super) fn ensure_allowed(&self, keys: &[&str]) -> Result<()> {
        let mut seen = HashSet::new();
        for (key, _) in &self.0 {
            if !keys.contains(&key.as_str()) {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Hyperliquid parameter: {key}"
                )));
            }
            if !seen.insert(key.as_str()) {
                return Err(DcexError::InvalidInput(format!(
                    "duplicate Hyperliquid parameter: {key}"
                )));
            }
        }
        Ok(())
    }

    pub(super) fn required_one_of<'a>(&'a self, key: &str, allowed: &[&str]) -> Result<&'a str> {
        let value = self.required(key)?;
        if !allowed.contains(&value) {
            return Err(DcexError::InvalidInput(format!(
                "invalid Hyperliquid {key}: {value}; expected one of {}",
                allowed.join(", ")
            )));
        }
        Ok(value)
    }

    pub(super) fn address(&self, key: &str) -> Result<String> {
        normalize_address(self.required(key)?, key)
    }

    pub(super) fn optional_address(&self, key: &str) -> Result<Option<String>> {
        self.get(key)
            .map(|value| normalize_address(value, key))
            .transpose()
    }

    pub(super) fn cloid(&self, key: &str) -> Result<String> {
        normalize_cloid(self.required(key)?, key)
    }

    pub(super) fn optional_cloid(&self, key: &str) -> Result<Option<String>> {
        self.get(key)
            .map(|value| normalize_cloid(value, key))
            .transpose()
    }

    pub(super) fn positive_decimal(&self, key: &str) -> Result<&str> {
        let value = self.required(key)?;
        let parsed = value.parse::<f64>().map_err(|error| {
            DcexError::InvalidInput(format!("invalid decimal parameter {key}: {error}"))
        })?;
        if !parsed.is_finite() || parsed <= 0.0 {
            return Err(DcexError::InvalidInput(format!(
                "parameter {key} must be a finite positive decimal"
            )));
        }
        Ok(value)
    }
}

pub(super) fn normalize_address(value: &str, key: &str) -> Result<String> {
    let normalized = value
        .strip_prefix("0x")
        .or_else(|| value.strip_prefix("0X"));
    let Some(hex_value) = normalized else {
        return Err(DcexError::InvalidInput(format!(
            "Hyperliquid {key} must be a 0x-prefixed 20-byte address"
        )));
    };
    if hex_value.len() != 40 || !hex_value.bytes().all(|byte| byte.is_ascii_hexdigit()) {
        return Err(DcexError::InvalidInput(format!(
            "Hyperliquid {key} must be a 0x-prefixed 20-byte address"
        )));
    }
    Ok(format!("0x{}", hex_value.to_ascii_lowercase()))
}

pub(super) fn normalize_cloid(value: &str, key: &str) -> Result<String> {
    let normalized = value
        .strip_prefix("0x")
        .or_else(|| value.strip_prefix("0X"));
    let Some(hex_value) = normalized else {
        return Err(DcexError::InvalidInput(format!(
            "Hyperliquid {key} must be a 0x-prefixed 16-byte hex value"
        )));
    };
    if hex_value.len() != 32 || !hex_value.bytes().all(|byte| byte.is_ascii_hexdigit()) {
        return Err(DcexError::InvalidInput(format!(
            "Hyperliquid {key} must be a 0x-prefixed 16-byte hex value"
        )));
    }
    Ok(format!("0x{}", hex_value.to_ascii_lowercase()))
}

pub(super) fn bool_value(value: &str) -> Option<bool> {
    match value {
        "true" | "True" | "1" => Some(true),
        "false" | "False" | "0" => Some(false),
        _ => None,
    }
}

pub(super) fn is_canonical_product_symbol(product_symbol: &str) -> bool {
    let normalized = product_symbol.to_ascii_uppercase();
    ["-SPOT", "-SWAP", "-FUTURE", "-OPTION"]
        .iter()
        .any(|suffix| normalized.ends_with(suffix))
}

pub(super) fn fallback_coin(product_symbol: &str) -> String {
    if !is_canonical_product_symbol(product_symbol) {
        return product_symbol.to_string();
    }
    product_symbol
        .split('-')
        .next()
        .unwrap_or(product_symbol)
        .to_ascii_uppercase()
}
