use std::io::Read;

use flate2::read::GzDecoder;
use serde_json::Value;

use crate::{DcexError, Result};

mod private;
mod public;

pub use private::BingxPrivateWebSocket;
pub use public::BingxPublicWebSocket;

pub(super) fn decode_event(payload: Vec<u8>) -> Result<Value> {
    let text = decode_event_text(&payload)?;
    parse_event_text(&text)
}

pub(super) fn decode_event_bytes(payload: Vec<u8>) -> Result<Vec<u8>> {
    let text = decode_event_text(&payload)?;
    let trimmed = text.trim();
    if matches!(trimmed, "Pong" | "pong") {
        serde_json::to_vec(trimmed)
            .map_err(|error| DcexError::Decode(format!("failed to encode BingX pong: {error}")))
    } else {
        Ok(text.into_bytes())
    }
}

pub(super) fn is_application_ping(value: &Value) -> bool {
    value
        .as_str()
        .map(|text| text.eq_ignore_ascii_case("ping"))
        .unwrap_or(false)
}

pub(super) fn is_application_ping_text(text: &str) -> bool {
    text.trim().eq_ignore_ascii_case("ping")
}

fn decode_event_text(payload: &[u8]) -> Result<String> {
    let text_error = match std::str::from_utf8(payload) {
        Ok(text) => return Ok(text.to_string()),
        Err(error) => Some(DcexError::Decode(format!(
            "failed to decode BingX WebSocket text payload: {error}"
        ))),
    };
    gunzip(payload).map_err(|error| text_error.unwrap_or(error))
}

fn parse_event_text(text: &str) -> Result<Value> {
    let text = text.trim();
    if matches!(text, "Ping" | "ping" | "Pong" | "pong") {
        return Ok(Value::String(text.to_string()));
    }
    serde_json::from_str(text).map_err(|error| {
        DcexError::Decode(format!("failed to decode BingX WebSocket JSON: {error}"))
    })
}

fn gunzip(payload: &[u8]) -> Result<String> {
    let mut decoder = GzDecoder::new(payload);
    let mut output = Vec::new();
    decoder.read_to_end(&mut output).map_err(|error| {
        DcexError::Decode(format!(
            "failed to inflate BingX WebSocket payload: {error}"
        ))
    })?;
    String::from_utf8(output).map_err(|error| {
        DcexError::Decode(format!(
            "failed to decode BingX WebSocket inflated payload: {error}"
        ))
    })
}

pub(super) fn normalize_symbol(product_symbol: &str) -> Result<String> {
    let product_symbol = product_symbol.trim();
    if product_symbol.is_empty() {
        return Err(DcexError::InvalidInput(
            "BingX WebSocket symbol must not be empty.".to_string(),
        ));
    }
    if product_symbol.contains('-') {
        let parts = product_symbol.split('-').collect::<Vec<_>>();
        if parts.len() >= 2 && !parts[0].is_empty() && !parts[1].is_empty() {
            return Ok(format!(
                "{}-{}",
                parts[0].to_ascii_uppercase(),
                parts[1].to_ascii_uppercase()
            ));
        }
    }
    if !product_symbol
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || character == '-')
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported BingX WebSocket symbol: {product_symbol}"
        )));
    }
    Ok(product_symbol.to_ascii_uppercase())
}

pub(super) fn normalize_data_type(data_type: &str) -> Result<String> {
    let data_type = data_type.trim();
    if data_type.is_empty() {
        return Err(DcexError::InvalidInput(
            "BingX WebSocket dataType must not be empty.".to_string(),
        ));
    }
    if !data_type.chars().all(|character| {
        character.is_ascii_alphanumeric() || matches!(character, '-' | '_' | '@' | '.')
    }) {
        return Err(DcexError::InvalidInput(format!(
            "unsupported BingX WebSocket dataType: {data_type}"
        )));
    }
    Ok(data_type.to_string())
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

    use flate2::write::GzEncoder;
    use flate2::Compression;
    use serde_json::json;

    use super::*;

    #[test]
    fn decodes_text_gzip_and_ping() {
        assert_eq!(
            decode_event(br#"{"code":0,"dataType":"BTC-USDT@trade"}"#.to_vec()).expect("json"),
            json!({"code": 0, "dataType": "BTC-USDT@trade"})
        );
        assert_eq!(
            decode_event(b"Ping".to_vec()).expect("ping"),
            Value::String("Ping".to_string())
        );

        let mut encoder = GzEncoder::new(Vec::new(), Compression::default());
        encoder
            .write_all(br#"{"code":0,"dataType":"BTC-USDT@kline_1m"}"#)
            .expect("write");
        let compressed = encoder.finish().expect("finish");
        assert_eq!(
            decode_event(compressed).expect("gzip"),
            json!({"code": 0, "dataType": "BTC-USDT@kline_1m"})
        );
    }

    #[test]
    fn normalizes_symbols_and_data_types() {
        assert_eq!(
            normalize_symbol("BTC-USDT-SPOT").expect("canonical"),
            "BTC-USDT"
        );
        assert_eq!(normalize_symbol("eth-usdt").expect("raw"), "ETH-USDT");
        assert!(normalize_data_type("BTC-USDT@kline_1m").is_ok());
        assert!(normalize_data_type("BTC USDT@trade").is_err());
    }
}
