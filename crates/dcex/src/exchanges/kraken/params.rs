use crate::{DcexError, Result};

pub(super) struct KrakenParams(Vec<(String, String)>);

impl KrakenParams {
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

pub(super) fn exchange_symbol_fallback(product_symbol: &str, futures_prefix: &str) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) => {
            let base = kraken_asset(base);
            let quote = kraken_asset(quote);
            format!("{futures_prefix}{base}{quote}")
        }
        _ => product_symbol.to_string(),
    }
}

pub(super) fn kraken_asset(asset: &str) -> &str {
    match asset {
        "BTC" => "XBT",
        other => other,
    }
}

pub(super) fn push_optional(params: &mut Vec<(String, String)>, key: &str, value: Option<&str>) {
    if let Some(value) = value {
        params.push((key.to_string(), value.to_string()));
    }
}

pub(super) fn require_one_identifier(params: &KrakenParams, keys: &[&str]) -> Result<()> {
    if keys.iter().any(|key| params.get(key).is_some()) {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "Specify {}.",
        keys.join(", ")
    )))
}
