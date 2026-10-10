use serde_json::{Map, Value};

use crate::{DcexError, Result};

pub(super) struct BitgetParams(Vec<(String, String)>);

impl BitgetParams {
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

    pub(super) fn ensure_allowed(&self, keys: &[&str], allow_product_symbol: bool) -> Result<()> {
        for (key, _) in &self.0 {
            if !(keys.contains(&key.as_str()) || allow_product_symbol && key == "product_symbol") {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Bitget parameter: {key}"
                )));
            }
        }
        Ok(())
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

    pub(super) fn json_required(&self, key: &str) -> Result<Value> {
        serde_json::from_str(self.required(key)?).map_err(|error| {
            DcexError::InvalidInput(format!("invalid JSON parameter {key}: {error}"))
        })
    }

    pub(super) fn json_optional(&self, key: &str) -> Result<Option<Value>> {
        let Some(value) = self.get(key) else {
            return Ok(None);
        };
        serde_json::from_str(value).map(Some).map_err(|error| {
            DcexError::InvalidInput(format!("invalid JSON parameter {key}: {error}"))
        })
    }
}

pub(super) fn exchange_symbol_fallback(product_symbol: &str) -> Result<String> {
    let parts = product_symbol.split('-').collect::<Vec<_>>();
    if parts.len() < 3 {
        return Ok(product_symbol.to_string());
    }
    if parts.iter().any(|part| part.is_empty()) {
        return Err(DcexError::InvalidInput(
            "bitget product symbol must not contain empty components".into(),
        ));
    }
    let symbol = match parts.as_slice() {
        [base, "USD", "SWAP"] => format!("{base}USD_CM"),
        [base, "USDC", "SWAP"] => format!("{base}PERP"),
        [base, quote, "SPOT" | "SWAP"] => format!("{base}{quote}"),
        _ => return Err(DcexError::InvalidInput(
            "cannot safely resolve bitget product symbol; load the product table or pass the official exchange symbol".into(),
        )),
    };
    Ok(symbol.to_ascii_uppercase())
}

pub(super) fn insert_optional_value(
    body: &mut Map<String, Value>,
    key: &str,
    value: Option<Value>,
) {
    if let Some(value) = value {
        body.insert(key.to_string(), value);
    }
}

pub(super) fn require_one_identifier(params: &BitgetParams, keys: &[&str]) -> Result<()> {
    if keys.iter().any(|key| params.get(key).is_some()) {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "Specify {}.",
        keys.join(" or ")
    )))
}

pub(super) fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(message.into())
}

pub(super) fn nonempty<'a>(params: &'a BitgetParams, key: &str) -> Result<&'a str> {
    params
        .get(key)
        .filter(|v| !v.is_empty())
        .ok_or_else(|| invalid(&format!("{key} is required")))
}

pub(super) fn schema_invalid(message: impl std::fmt::Display) -> DcexError {
    DcexError::InvalidInput(format!("Bitget: {message}"))
}

pub(super) fn schema_required<'a>(params: &'a BitgetParams, key: &str) -> Result<&'a str> {
    params
        .get(key)
        .filter(|value| !value.trim().is_empty())
        .ok_or_else(|| schema_invalid(format!("{key} is required")))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn canonical_bitget_symbols_use_exchange_uppercase() {
        assert_eq!(
            exchange_symbol_fallback("rCVCO-USDT-SPOT").unwrap(),
            "RCVCOUSDT"
        );
    }

    #[test]
    fn public_market_symbol_samples() {
        crate::exchanges::symbol_tests::check("bitget", |symbol, _mode| {
            exchange_symbol_fallback(symbol)
        });
    }
}
