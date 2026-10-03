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

    pub(super) fn ensure_allowed(&self, keys: &[&str]) -> Result<()> {
        if let Some((key, _)) = self.0.iter().find(|(key, _)| !keys.contains(&key.as_str())) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Kraken parameter: {key}"
            )));
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

pub(super) fn exchange_symbol_fallback(
    product_symbol: &str,
    futures_prefix: &str,
) -> Result<String> {
    let parts = product_symbol.split('-').collect::<Vec<_>>();
    if parts.len() < 3 {
        return Ok(product_symbol.to_string());
    }
    if parts.iter().any(|part| part.is_empty()) {
        return Err(DcexError::InvalidInput(
            "kraken product symbol must not contain empty components".into(),
        ));
    }
    let symbol = match parts.as_slice() {
        [base, quote, "SPOT"] if futures_prefix.is_empty() => {
            let base = if *base == "DOGE" { "XDG" } else { kraken_asset(base) };
            format!("{base}{}", kraken_asset(quote))
        },
        [base, quote, "SWAP"] if futures_prefix == "PF_" => format!("PF_{}{}", kraken_asset(base), kraken_asset(quote)),
        _ => return Err(DcexError::InvalidInput(
            "cannot safely resolve kraken product symbol; load the product table or pass the official exchange symbol".into(),
        )),
    };
    Ok(if futures_prefix.is_empty() {
        symbol
    } else {
        symbol.to_ascii_uppercase()
    })
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
    let count = keys.iter().filter(|key| params.get(key).is_some()).count();
    if count == 1 {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "Specify exactly one of {}.",
        keys.join(", "),
    )))
}

pub(in crate::exchanges::kraken) fn invalid(message: impl std::fmt::Display) -> crate::DcexError {
    crate::DcexError::InvalidInput(format!("Kraken: {message}"))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn canonical_kraken_futures_use_exchange_uppercase() {
        assert_eq!(
            exchange_symbol_fallback("AAPLx-USD-SWAP", "PF_").unwrap(),
            "PF_AAPLXUSD"
        );
        assert_eq!(
            exchange_symbol_fallback("AAPLx-USD-SPOT", "").unwrap(),
            "AAPLxUSD"
        );
    }

    #[test]
    fn public_market_symbol_samples() {
        crate::exchanges::symbol_tests::check("kraken", |symbol, mode| {
            exchange_symbol_fallback(symbol, if mode == "spot" { "" } else { "PF_" })
        });
    }
}
