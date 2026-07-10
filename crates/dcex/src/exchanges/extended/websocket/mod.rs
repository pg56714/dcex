mod private;
mod public;

pub use private::ExtendedPrivateWebSocket;
pub use public::ExtendedPublicWebSocket;

use crate::{DcexError, Result};

pub(super) const WS_URL: &str = "wss://api.starknet.extended.exchange";
pub(super) const USER_AGENT: &str = "dcex-rust/0.1";
const STREAM_PREFIX: &str = "stream.extended.exchange/v1";

pub(super) fn stream_url(base_url: &str, path: &str) -> Result<String> {
    let base_url = base_url.trim_end_matches('/');
    if !(base_url.starts_with("ws://") || base_url.starts_with("wss://")) {
        return Err(DcexError::InvalidInput(
            "Extended WebSocket base URL must use ws:// or wss://.".to_string(),
        ));
    }
    Ok(format!(
        "{base_url}/{STREAM_PREFIX}/{}",
        path.trim_start_matches('/')
    ))
}

pub(super) fn optional_market_path(prefix: &str, market: Option<&str>) -> Result<String> {
    match market {
        Some(market) => Ok(format!("{prefix}/{}", normalize_market(market)?)),
        None => Ok(prefix.to_string()),
    }
}

pub(super) fn normalize_market(market: &str) -> Result<&str> {
    let market = market.trim();
    if market.is_empty()
        || !market.chars().all(|character| {
            character.is_ascii_alphanumeric() || character == '-' || character == '_'
        })
    {
        return Err(DcexError::InvalidInput(format!(
            "invalid Extended WebSocket market: {market}"
        )));
    }
    Ok(market)
}

pub(super) fn normalize_candle_type(candle_type: &str) -> Result<&str> {
    match candle_type.trim() {
        "trades" => Ok("trades"),
        "mark-prices" => Ok("mark-prices"),
        "index-prices" => Ok("index-prices"),
        value => Err(DcexError::InvalidInput(format!(
            "unsupported Extended candle type: {value}"
        ))),
    }
}

pub(super) fn normalize_candle_interval(interval: &str) -> Result<&str> {
    match interval.trim() {
        "P30D" | "P7D" | "PT24H" | "PT12H" | "PT8H" | "PT4H" | "PT2H" | "PT1H" | "PT30M"
        | "PT15M" | "PT5M" | "PT1M" => Ok(interval.trim()),
        value => Err(DcexError::InvalidInput(format!(
            "unsupported Extended candle interval: {value}"
        ))),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn builds_documented_stream_urls() {
        assert_eq!(
            stream_url(WS_URL, "orderbooks/BTC-USD").unwrap(),
            "wss://api.starknet.extended.exchange/stream.extended.exchange/v1/orderbooks/BTC-USD"
        );
        assert_eq!(
            optional_market_path("prices/mark", None).unwrap(),
            "prices/mark"
        );
        assert!(normalize_market("BTC/USD").is_err());
        assert!(normalize_candle_interval("1m").is_err());
    }
}
