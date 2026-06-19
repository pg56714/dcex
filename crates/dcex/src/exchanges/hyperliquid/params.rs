use crate::{DcexError, Result};

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
        self.get(key)
            .ok_or_else(|| DcexError::InvalidInput(format!("missing required parameter: {key}")))
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

    pub(super) fn optional_i64(&self, key: &str) -> Result<Option<i64>> {
        self.get(key)
            .map(|value| {
                value.parse::<i64>().map_err(|error| {
                    DcexError::InvalidInput(format!("invalid integer parameter {key}: {error}"))
                })
            })
            .transpose()
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
}

pub(super) fn bool_value(value: &str) -> Option<bool> {
    match value {
        "true" | "True" | "1" => Some(true),
        "false" | "False" | "0" => Some(false),
        _ => None,
    }
}

pub(super) fn is_canonical_product_symbol(product_symbol: &str) -> bool {
    product_symbol.contains('-')
}

pub(super) fn fallback_coin(product_symbol: &str) -> String {
    product_symbol
        .split('-')
        .next()
        .unwrap_or(product_symbol)
        .to_string()
}
