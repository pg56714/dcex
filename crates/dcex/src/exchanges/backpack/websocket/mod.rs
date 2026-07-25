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
    for prefix in [
        "account.orderUpdate",
        "account.positionUpdate",
        "account.rfqUpdate",
    ] {
        if stream == prefix {
            return Ok(stream.to_string());
        }
        if let Some(symbol) = stream.strip_prefix(&format!("{prefix}.")) {
            return Ok(format!("{prefix}.{}", stream_symbol(symbol.to_string())?));
        }
    }
    if let Some(remainder) = stream.strip_prefix("kline.") {
        let (interval, symbol) = remainder.split_once('.').ok_or_else(|| {
            DcexError::InvalidInput(format!("unsupported Backpack WebSocket stream: {stream}"))
        })?;
        return Ok(format!(
            "kline.{}.{}",
            validate_kline_interval(interval)?,
            stream_symbol(symbol.to_string())?
        ));
    }
    if let Some(remainder) = stream.strip_prefix("depth.") {
        if let Some((speed, symbol)) = remainder.split_once('.') {
            if matches!(speed, "200ms" | "600ms" | "1000ms") {
                return Ok(format!(
                    "depth.{}.{}",
                    validate_depth_speed(speed)?,
                    stream_symbol(symbol.to_string())?
                ));
            }
            if speed.strip_suffix("ms").is_some_and(|millis| {
                !millis.is_empty() && millis.chars().all(|character| character.is_ascii_digit())
            }) {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Backpack depth speed: {speed}"
                )));
            }
        }
        return Ok(format!("depth.{}", stream_symbol(remainder.to_string())?));
    }
    for prefix in [
        "bookTicker",
        "liquidation",
        "markPrice",
        "ticker",
        "openInterest",
        "trade",
    ] {
        if let Some(symbol) = stream.strip_prefix(&format!("{prefix}.")) {
            return Ok(format!("{prefix}.{}", stream_symbol(symbol.to_string())?));
        }
    }
    Err(DcexError::InvalidInput(format!(
        "unsupported Backpack WebSocket stream: {stream}"
    )))
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
        .all(|character| character.is_ascii_alphanumeric() || matches!(character, '_' | '.'))
        || symbol.starts_with('.')
        || symbol.ends_with('.')
        || !symbol.contains('_')
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Backpack stream symbol: {symbol}"
        )));
    }
    Ok(symbol.to_ascii_uppercase())
}

pub(crate) fn validate_kline_interval(interval: &str) -> Result<String> {
    let interval = interval.trim();
    if matches!(
        interval,
        "1s" | "1m"
            | "3m"
            | "5m"
            | "15m"
            | "30m"
            | "1h"
            | "2h"
            | "4h"
            | "6h"
            | "8h"
            | "12h"
            | "1d"
            | "3d"
            | "1w"
            | "1month"
    ) {
        Ok(interval.to_string())
    } else {
        Err(DcexError::InvalidInput(format!(
            "unsupported Backpack K-line interval: {interval}"
        )))
    }
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
        assert_eq!(
            normalize_stream("trade.MU.US_USDC").expect("stock stream"),
            "trade.MU.US_USDC"
        );
        assert!(normalize_stream("liquidation").is_err());
        assert!(normalize_stream("liquidation.SOL_USDC_PERP").is_ok());
        assert!(normalize_stream("depth.500ms.SOL_USDC").is_err());
        assert!(normalize_stream("kline.7m.SOL_USDC").is_err());
        assert!(normalize_stream("account.unknown").is_err());
        assert!(normalize_stream("bad stream").is_err());
        assert!(validate_depth_speed("200ms").is_ok());
        assert!(validate_depth_speed("500ms").is_err());
    }
}
