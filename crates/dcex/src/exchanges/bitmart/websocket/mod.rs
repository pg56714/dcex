use std::io::Read;

use flate2::read::DeflateDecoder;
use serde_json::Value;

use crate::{DcexError, Result};

mod private;
mod public;

pub use private::BitmartPrivateWebSocket;
pub use public::BitmartPublicWebSocket;

pub(super) fn decode_event(payload: Vec<u8>) -> Result<Value> {
    let text = decode_event_text(&payload)?;
    parse_event_text(&text)
}

pub(super) fn decode_event_bytes(payload: Vec<u8>) -> Result<Vec<u8>> {
    let text = decode_event_text(&payload)?;
    let text = text.trim();
    if matches!(text, "ping" | "pong") {
        serde_json::to_vec(text)
            .map_err(|error| DcexError::Decode(format!("failed to encode BitMart ping: {error}")))
    } else {
        Ok(text.as_bytes().to_vec())
    }
}

fn parse_event_text(text: &str) -> Result<Value> {
    let text = text.trim();
    if matches!(text, "ping" | "pong") {
        return Ok(Value::String(text.to_string()));
    }
    serde_json::from_str(text).map_err(|error| {
        DcexError::Decode(format!("failed to decode BitMart WebSocket JSON: {error}"))
    })
}

fn decode_event_text(payload: &[u8]) -> Result<String> {
    let text_error = match std::str::from_utf8(payload) {
        Ok(text) => return Ok(text.to_string()),
        Err(error) => Some(DcexError::Decode(format!(
            "failed to decode BitMart WebSocket text payload: {error}"
        ))),
    };
    inflate_raw(payload).map_err(|error| text_error.unwrap_or(error))
}

fn inflate_raw(payload: &[u8]) -> Result<String> {
    let mut decoder = DeflateDecoder::new(payload);
    let mut output = Vec::new();
    decoder.read_to_end(&mut output).map_err(|error| {
        DcexError::Decode(format!(
            "failed to inflate BitMart WebSocket payload: {error}"
        ))
    })?;
    String::from_utf8(output).map_err(|error| {
        DcexError::Decode(format!(
            "failed to decode BitMart WebSocket inflated payload: {error}"
        ))
    })
}

pub(super) fn normalize_topic(topic: &str, label: &str) -> Result<String> {
    let topic = topic.trim();
    if topic.is_empty() {
        return Err(DcexError::InvalidInput(format!(
            "BitMart {label} must not be empty."
        )));
    }
    if !topic
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || matches!(character, '/' | ':' | '_'))
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported BitMart {label}: {topic}"
        )));
    }
    Ok(topic.to_string())
}

pub(super) fn normalize_symbol(product_symbol: &str) -> Result<String> {
    let product_symbol = product_symbol.trim();
    if product_symbol.is_empty() {
        return Err(DcexError::InvalidInput(
            "BitMart WebSocket symbol must not be empty.".to_string(),
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
            "unsupported BitMart WebSocket symbol: {product_symbol}"
        )));
    }
    Ok(product_symbol.to_ascii_uppercase())
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
    use std::io::Write;

    use flate2::write::DeflateEncoder;
    use flate2::Compression;
    use serde_json::json;

    use super::*;

    #[test]
    fn decodes_json_text_and_pong() {
        assert_eq!(
            decode_event(br#"{"event":"subscribe"}"#.to_vec()).expect("json"),
            json!({"event": "subscribe"})
        );
        assert_eq!(
            decode_event(b"pong".to_vec()).expect("pong"),
            Value::String("pong".to_string())
        );
    }

    #[test]
    fn decodes_raw_deflate_json() {
        let mut encoder = DeflateEncoder::new(Vec::new(), Compression::default());
        encoder
            .write_all(br#"{"table":"spot/trade"}"#)
            .expect("write");
        let compressed = encoder.finish().expect("finish");
        assert_eq!(
            decode_event(compressed).expect("compressed"),
            json!({"table": "spot/trade"})
        );
    }

    #[test]
    fn normalizes_symbols_and_topics() {
        assert_eq!(
            normalize_symbol("BTC-USDT-SPOT").expect("canonical"),
            "BTC_USDT"
        );
        assert_eq!(normalize_symbol("btc_usdt").expect("raw"), "BTC_USDT");
        assert!(normalize_topic("spot/trade:BTC_USDT", "topic").is_ok());
        assert!(normalize_topic("spot trade", "topic").is_err());
    }
}
