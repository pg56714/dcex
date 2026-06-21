use serde_json::Value;

use crate::{DcexError, Result};

mod private;
mod public;

pub use private::GateioPrivateWebSocket;
pub use public::GateioPublicWebSocket;

pub(super) fn normalize_channel(channel: &str) -> Result<String> {
    let channel = channel.trim();
    if channel.is_empty() {
        return Err(DcexError::InvalidInput(
            "Gate.io WebSocket channel must not be empty.".to_string(),
        ));
    }
    if !channel
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || matches!(character, '.' | '_'))
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Gate.io WebSocket channel: {channel}"
        )));
    }
    Ok(channel.to_string())
}

pub(super) fn normalize_event(event: &str) -> Result<String> {
    let event = event.trim();
    match event {
        "subscribe" | "unsubscribe" => Ok(event.to_string()),
        _ => Err(DcexError::InvalidInput(format!(
            "unsupported Gate.io WebSocket event: {event}"
        ))),
    }
}

pub(super) fn normalize_symbol(product_symbol: &str) -> Result<String> {
    let product_symbol = product_symbol.trim();
    if product_symbol.is_empty() {
        return Err(DcexError::InvalidInput(
            "Gate.io WebSocket symbol must not be empty.".to_string(),
        ));
    }
    if product_symbol.contains('-') {
        let parts = product_symbol.split('-').collect::<Vec<_>>();
        if parts.len() >= 2 && !parts[0].is_empty() && !parts[1].is_empty() {
            return Ok(format!(
                "{}_{}",
                parts[0].to_ascii_uppercase(),
                parts[1].to_ascii_uppercase()
            ));
        }
    }
    if !product_symbol
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || character == '_')
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Gate.io WebSocket symbol: {product_symbol}"
        )));
    }
    Ok(product_symbol.to_ascii_uppercase())
}

pub(super) fn normalize_payload_value(value: &str) -> Result<String> {
    let value = value.trim();
    if value.is_empty() {
        return Err(DcexError::InvalidInput(
            "Gate.io WebSocket payload value must not be empty.".to_string(),
        ));
    }
    if !value
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || matches!(character, '_' | '.' | '-'))
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Gate.io WebSocket payload value: {value}"
        )));
    }
    Ok(value.to_string())
}

pub(super) fn payload_array(values: Vec<String>) -> Result<Value> {
    let values = values
        .into_iter()
        .map(|value| normalize_payload_value(&value).map(Value::String))
        .collect::<Result<Vec<_>>>()?;
    Ok(Value::Array(values))
}

pub(super) fn validate_credential(label: &str, value: &str) -> Result<()> {
    if value.trim().is_empty() {
        return Err(DcexError::InvalidInput(format!(
            "{label} must not be empty."
        )));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::*;

    #[test]
    fn normalizes_channel_symbol_and_payload() {
        assert_eq!(
            normalize_symbol("BTC-USDT-SPOT").expect("canonical"),
            "BTC_USDT"
        );
        assert_eq!(normalize_symbol("eth_usdt").expect("raw"), "ETH_USDT");
        assert!(normalize_channel("spot.trades").is_ok());
        assert!(normalize_channel("spot trades").is_err());
        assert_eq!(
            payload_array(vec!["BTC_USDT".to_string(), "100ms".to_string()]).expect("payload"),
            json!(["BTC_USDT", "100ms"])
        );
    }
}
