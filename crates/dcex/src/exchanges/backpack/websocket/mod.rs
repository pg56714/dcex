mod private;
mod public;

pub use private::BackpackPrivateWebSocket;
pub use public::BackpackPublicWebSocket;

use serde_json::{json, Value};

use crate::{DcexError, Result};

pub(crate) const WS_URL: &str = "wss://ws.backpack.exchange";

pub(crate) fn subscription_payload(
    method: &str,
    streams: Vec<String>,
    signature: Option<[String; 4]>,
) -> Result<Value> {
    let method = match method {
        "SUBSCRIBE" | "UNSUBSCRIBE" => method,
        _ => {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Backpack WebSocket method: {method}"
            )));
        }
    };
    let streams = streams
        .into_iter()
        .map(|stream| normalize_stream(&stream))
        .collect::<Result<Vec<_>>>()?;
    if streams.is_empty() {
        return Err(DcexError::InvalidInput(
            "at least one Backpack WebSocket stream is required.".to_string(),
        ));
    }
    let mut payload = json!({
        "method": method,
        "params": streams,
    });
    if method == "SUBSCRIBE" {
        if let Some(signature) = signature {
            payload["signature"] = json!(signature);
        }
    }
    Ok(payload)
}

pub(crate) fn normalize_stream(stream: &str) -> Result<String> {
    let stream = stream.trim();
    if stream.is_empty() {
        return Err(DcexError::InvalidInput(
            "Backpack WebSocket stream must not be empty.".to_string(),
        ));
    }
    if !stream
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || matches!(character, '.' | '_' | '-'))
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Backpack WebSocket stream: {stream}"
        )));
    }
    Ok(stream.to_string())
}

pub(crate) fn stream_symbol(symbol: String) -> Result<String> {
    let symbol = symbol.trim();
    if symbol.is_empty() {
        return Err(DcexError::InvalidInput(
            "Backpack stream symbol must not be empty.".to_string(),
        ));
    }
    if !symbol
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || character == '_')
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Backpack stream symbol: {symbol}"
        )));
    }
    Ok(symbol.to_ascii_uppercase())
}

pub(crate) fn validate_depth_speed(speed: &str) -> Result<String> {
    let speed = speed.trim();
    if matches!(speed, "200ms" | "600ms" | "1000ms") {
        Ok(speed.to_string())
    } else {
        Err(DcexError::InvalidInput(format!(
            "unsupported Backpack depth speed: {speed}"
        )))
    }
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::*;

    #[test]
    fn builds_public_subscription_payload() {
        let payload = subscription_payload(
            "SUBSCRIBE",
            vec!["trade.SOL_USDC".to_string(), "depth.SOL_USDC".to_string()],
            None,
        )
        .expect("payload");
        assert_eq!(
            payload,
            json!({"method": "SUBSCRIBE", "params": ["trade.SOL_USDC", "depth.SOL_USDC"]})
        );
    }

    #[test]
    fn builds_private_subscription_payload() {
        let payload = subscription_payload(
            "SUBSCRIBE",
            vec!["account.orderUpdate".to_string()],
            Some([
                "key".to_string(),
                "sig".to_string(),
                "123".to_string(),
                "5000".to_string(),
            ]),
        )
        .expect("payload");
        assert_eq!(payload["signature"], json!(["key", "sig", "123", "5000"]));
    }

    #[test]
    fn omits_signature_on_unsubscribe() {
        let payload = subscription_payload(
            "UNSUBSCRIBE",
            vec!["account.orderUpdate".to_string()],
            Some([
                "key".to_string(),
                "sig".to_string(),
                "123".to_string(),
                "5000".to_string(),
            ]),
        )
        .expect("payload");
        assert!(payload.get("signature").is_none());
    }

    #[test]
    fn validates_stream_and_speed() {
        assert!(normalize_stream("trade.SOL_USDC").is_ok());
        assert!(normalize_stream("bad stream").is_err());
        assert!(validate_depth_speed("200ms").is_ok());
        assert!(validate_depth_speed("500ms").is_err());
    }
}
