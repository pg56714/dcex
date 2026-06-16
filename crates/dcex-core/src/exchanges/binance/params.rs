use super::client::BinanceMarket;
use crate::{DcexError, Result};

pub(super) struct PublicParams(pub(super) Vec<(String, String)>);

impl PublicParams {
    pub(super) fn get(&self, key: &str) -> Option<&str> {
        self.0
            .iter()
            .find(|(candidate, _)| candidate == key)
            .map(|(_, value)| value.as_str())
    }

    pub(super) fn values(&self, key: &str) -> Option<Vec<String>> {
        let values = self
            .0
            .iter()
            .filter(|(candidate, _)| candidate == key)
            .map(|(_, value)| value.clone())
            .collect::<Vec<_>>();
        if values.is_empty() {
            None
        } else {
            Some(values)
        }
    }

    pub(super) fn required(&self, key: &str) -> Result<&str> {
        self.get(key)
            .ok_or_else(|| DcexError::InvalidInput(format!("missing required parameter: {key}")))
    }

    pub(super) fn u64(&self, key: &str) -> Result<Option<u64>> {
        self.get(key)
            .map(|value| {
                value.parse::<u64>().map_err(|error| {
                    DcexError::InvalidInput(format!("invalid integer parameter {key}: {error}"))
                })
            })
            .transpose()
    }

    pub(super) fn without(&self, excluded: &[&str]) -> Vec<(String, String)> {
        self.0
            .iter()
            .filter(|(key, _)| !excluded.contains(&key.as_str()))
            .cloned()
            .collect()
    }
}

pub(super) fn exchange_symbol_fallback(product_symbol: &str) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) => format!("{base}{quote}"),
        _ => product_symbol.to_string(),
    }
}

pub(super) fn is_canonical_product_symbol(product_symbol: &str) -> bool {
    product_symbol.contains('-')
}

pub(super) fn is_spot_product_symbol(product_symbol: &str) -> bool {
    product_symbol.ends_with("-SPOT")
}

pub(super) fn market_for_product_symbol_fallback(product_symbol: &str) -> BinanceMarket {
    if is_spot_product_symbol(product_symbol) {
        BinanceMarket::Spot
    } else {
        BinanceMarket::Futures
    }
}

pub(super) fn market_from_type(market_type: &str) -> BinanceMarket {
    if market_type.eq_ignore_ascii_case("spot") {
        BinanceMarket::Spot
    } else {
        BinanceMarket::Futures
    }
}

pub(super) fn normalize_order_side(side: &str) -> Result<String> {
    if side.eq_ignore_ascii_case("buy") {
        Ok("BUY".to_string())
    } else if side.eq_ignore_ascii_case("sell") {
        Ok("SELL".to_string())
    } else {
        Err(DcexError::InvalidInput(format!(
            "unsupported Binance order side: {side}"
        )))
    }
}

pub(super) fn ensure_futures_listen_key_market(market_type: &str) -> Result<()> {
    if market_type.eq_ignore_ascii_case("spot") {
        Err(DcexError::InvalidInput(
            "Binance Spot user data streams are subscribed through the WebSocket API.".to_string(),
        ))
    } else {
        Ok(())
    }
}

pub(super) fn push_optional(params: &mut Vec<(String, String)>, key: &str, value: Option<&str>) {
    if let Some(value) = value {
        params.push((key.to_string(), value.to_string()));
    }
}

pub(super) fn push_optional_display<T: ToString>(
    params: &mut Vec<(String, String)>,
    key: &str,
    value: Option<T>,
) {
    if let Some(value) = value {
        params.push((key.to_string(), value.to_string()));
    }
}
