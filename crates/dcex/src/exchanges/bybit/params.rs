use std::sync::atomic::{AtomicU64, Ordering};

use serde_json::{Map, Value};

use crate::exchange::unix_timestamp_ms;
use crate::{DcexError, Result};

static TRANSFER_COUNTER: AtomicU64 = AtomicU64::new(0);

pub(super) struct BybitParams(Vec<(String, String)>);

impl BybitParams {
    pub(super) fn from_pairs(pairs: Vec<(String, String)>) -> Self {
        Self(pairs)
    }

    pub(super) fn pairs(&self) -> &[(String, String)] {
        &self.0
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

    pub(super) fn i64_required(&self, key: &str) -> Result<i64> {
        self.required(key)?.parse::<i64>().map_err(|error| {
            DcexError::InvalidInput(format!("invalid integer parameter {key}: {error}"))
        })
    }

    pub(super) fn json_required(&self, key: &str) -> Result<Value> {
        serde_json::from_str(self.required(key)?).map_err(|error| {
            DcexError::InvalidInput(format!("invalid JSON parameter {key}: {error}"))
        })
    }

    /// Rejects any parameter outside `keys` instead of silently dropping it.
    pub(super) fn ensure_allowed(&self, keys: &[&str]) -> Result<()> {
        match self.0.iter().find(|(key, _)| !keys.contains(&key.as_str())) {
            Some((key, _)) => Err(DcexError::InvalidInput(format!(
                "unsupported Bybit parameter: {key}"
            ))),
            None => Ok(()),
        }
    }

    pub(super) fn only(&self, keys: &[&str]) -> Vec<(String, String)> {
        self.0
            .iter()
            .filter(|(key, _)| keys.contains(&key.as_str()))
            .cloned()
            .collect()
    }

    pub(super) fn without(&self, excluded: &[&str]) -> Vec<(String, String)> {
        self.0
            .iter()
            .filter(|(key, _)| !excluded.contains(&key.as_str()))
            .cloned()
            .collect()
    }
}

pub(super) fn exchange_symbol_fallback(product_symbol: &str) -> Result<String> {
    let parts = product_symbol.split('-').collect::<Vec<_>>();
    if parts.len() < 3
        || matches!(
            parts.as_slice(),
            [_, _, _, "C" | "P"] | [_, _, _, "C" | "P", "USDT" | "USDC"]
        )
    {
        return Ok(product_symbol.to_string());
    }
    if parts.iter().any(|part| part.is_empty()) {
        return Err(DcexError::InvalidInput(
            "bybit product symbol must not contain empty components".into(),
        ));
    }
    let symbol = match parts.as_slice() {
        [base, "USDC", "SWAP"] => format!("{base}PERP"),
        [base, quote, "SPOT" | "SWAP"] => format!("{base}{quote}"),
        _ => return Err(DcexError::InvalidInput(
            "cannot safely resolve bybit product symbol; load the product table or pass the official exchange symbol".into(),
        )),
    };
    Ok(symbol)
}

/// Category implied by a unified product symbol that the no-table fallback can map.
pub(super) fn canonical_category_fallback(product_symbol: &str) -> Option<&'static str> {
    match product_symbol.split('-').collect::<Vec<_>>().as_slice() {
        [_, _, "SPOT"] => Some("spot"),
        [_, "USD", "SWAP"] => Some("inverse"),
        [_, _, "SWAP"] => Some("linear"),
        _ => None,
    }
}

pub(super) fn bybit_timeframe(timeframe: &str) -> Result<&'static str> {
    match timeframe {
        "1m" => Ok("1"),
        "3m" => Ok("3"),
        "5m" => Ok("5"),
        "15m" => Ok("15"),
        "30m" => Ok("30"),
        "1h" => Ok("60"),
        "2h" => Ok("120"),
        "4h" => Ok("240"),
        "6h" => Ok("360"),
        "12h" => Ok("720"),
        "1d" => Ok("D"),
        "1w" => Ok("W"),
        "1M" => Ok("M"),
        _ => Err(DcexError::InvalidInput(
            "timeframe not supported".to_string(),
        )),
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

pub(super) fn insert_optional_i64(
    body: &mut Map<String, Value>,
    key: &str,
    value: Option<&str>,
) -> Result<()> {
    if let Some(value) = value {
        let parsed = value.parse::<i64>().map_err(|error| {
            DcexError::InvalidInput(format!("invalid integer parameter {key}: {error}"))
        })?;
        body.insert(key.to_string(), Value::Number(parsed.into()));
    }
    Ok(())
}

pub(super) fn insert_optional_bool(
    body: &mut Map<String, Value>,
    key: &str,
    value: Option<&str>,
) -> Result<()> {
    if let Some(value) = value {
        let parsed = match value.to_ascii_lowercase().as_str() {
            "true" => true,
            "false" => false,
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "invalid boolean parameter {key}: {value}"
                )));
            }
        };
        body.insert(key.to_string(), Value::Bool(parsed));
    }
    Ok(())
}

pub(super) fn require_one_identifier(params: &BybitParams, keys: &[&str]) -> Result<()> {
    if keys.iter().any(|key| params.get(key).is_some()) {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "one of {} is required",
        keys.join(", ")
    )))
}

pub(super) fn string_body(pairs: &[(&str, &str)]) -> Map<String, Value> {
    pairs
        .iter()
        .map(|(key, value)| (key.to_string(), Value::String(value.to_string())))
        .collect()
}

pub(super) fn generate_transfer_id() -> String {
    let now = unix_timestamp_ms().unwrap_or(0) as u128;
    let counter = TRANSFER_COUNTER.fetch_add(1, Ordering::Relaxed) as u128;
    let value = (now << 64) | counter;
    let hex = format!("{value:032x}");
    format!(
        "{}-{}-4{}-a{}-{}",
        &hex[0..8],
        &hex[8..12],
        &hex[13..16],
        &hex[17..20],
        &hex[20..32]
    )
}

pub(in crate::exchanges::bybit) fn invalid(message: impl std::fmt::Display) -> crate::DcexError {
    crate::DcexError::InvalidInput(format!("Bybit: {message}"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn order_lookup_requires_one_identifier() {
        let empty = BybitParams::from_pairs(Vec::new());
        assert!(require_one_identifier(&empty, &["orderId", "orderLinkId"]).is_err());

        let linked = BybitParams::from_pairs(vec![(
            "orderLinkId".to_string(),
            "client-order".to_string(),
        )]);
        assert!(require_one_identifier(&linked, &["orderId", "orderLinkId"]).is_ok());
    }

    #[test]
    fn exchange_symbol_fallback_requires_metadata_for_dated_futures() {
        assert_eq!(
            exchange_symbol_fallback("BTC-USDT-SWAP").expect("symbol"),
            "BTCUSDT"
        );
        assert!(exchange_symbol_fallback("BTC-USDT-250221-FUTURES").is_err());
        assert!(exchange_symbol_fallback("BTC-USD-230331-FUTURES").is_err());
    }
}

#[cfg(test)]
#[test]
fn public_market_symbol_samples() {
    crate::exchanges::symbol_tests::check("bybit", |symbol, _mode| {
        exchange_symbol_fallback(symbol)
    });
}
