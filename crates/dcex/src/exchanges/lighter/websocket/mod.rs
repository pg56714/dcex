mod private;
mod public;

pub use private::LighterPrivateWebSocket;
pub use public::LighterPublicWebSocket;

use serde_json::{Map, Value};

use crate::{DcexError, Result};

pub(crate) const MAINNET_HTTP_URL: &str = "https://mainnet.zklighter.elliot.ai";
pub(crate) const TESTNET_HTTP_URL: &str = "https://testnet.zklighter.elliot.ai";
pub(crate) const MAINNET_WS_URL: &str = "wss://mainnet.zklighter.elliot.ai/stream";
pub(crate) const TESTNET_WS_URL: &str = "wss://testnet.zklighter.elliot.ai/stream";

pub(crate) fn http_url(testnet: bool) -> &'static str {
    if testnet {
        TESTNET_HTTP_URL
    } else {
        MAINNET_HTTP_URL
    }
}

pub(crate) fn websocket_url(testnet: bool) -> &'static str {
    if testnet {
        TESTNET_WS_URL
    } else {
        MAINNET_WS_URL
    }
}

pub(crate) fn subscription_payload(
    operation: &str,
    channel: &str,
    auth: Option<String>,
) -> Result<Value> {
    let operation = match operation {
        "subscribe" | "unsubscribe" => operation,
        _ => {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Lighter WebSocket operation: {operation}"
            )));
        }
    };
    let channel = normalize_channel(channel)?;
    let mut payload = Map::new();
    payload.insert("type".to_string(), Value::String(operation.to_string()));
    payload.insert("channel".to_string(), Value::String(channel));
    if operation == "subscribe" {
        if let Some(auth) = auth {
            payload.insert("auth".to_string(), Value::String(normalize_auth(&auth)?));
        }
    }
    Ok(Value::Object(payload))
}

pub(crate) fn normalize_channel(channel: &str) -> Result<String> {
    let channel = channel.trim();
    if channel.is_empty() {
        return Err(DcexError::InvalidInput(
            "Lighter WebSocket channel must not be empty.".to_string(),
        ));
    }
    if !channel
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || matches!(character, '_' | '/' | ':'))
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Lighter WebSocket channel: {channel}"
        )));
    }
    Ok(channel.to_string())
}

pub(crate) fn normalize_resolution(resolution: &str) -> Result<String> {
    let resolution = resolution.trim();
    let supported = matches!(
        resolution,
        "1m" | "5m" | "15m" | "30m" | "1h" | "4h" | "12h" | "1d"
    );
    if supported {
        Ok(resolution.to_string())
    } else {
        Err(DcexError::InvalidInput(format!(
            "unsupported Lighter candle resolution: {resolution}"
        )))
    }
}

fn normalize_auth(auth: &str) -> Result<String> {
    let auth = auth.trim();
    if auth.is_empty() {
        return Err(DcexError::InvalidInput(
            "Lighter WebSocket auth token must not be empty.".to_string(),
        ));
    }
    Ok(auth.to_string())
}

pub(crate) fn market_channel(prefix: &str, market_id: u64) -> Result<String> {
    normalize_channel(prefix)?;
    Ok(format!("{prefix}/{market_id}"))
}

pub(crate) fn account_channel(prefix: &str, account_index: u64) -> Result<String> {
    normalize_channel(prefix)?;
    Ok(format!("{prefix}/{account_index}"))
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::*;

    #[test]
    fn builds_public_subscription_payload() {
        let payload = subscription_payload("subscribe", "trade/0", None).expect("payload");
        assert_eq!(payload, json!({"type": "subscribe", "channel": "trade/0"}));
    }

    #[test]
    fn builds_authenticated_subscription_payload() {
        let payload = subscription_payload("subscribe", "account_tx/12", Some("token".to_string()))
            .expect("payload");
        assert_eq!(payload["type"], "subscribe");
        assert_eq!(payload["channel"], "account_tx/12");
        assert_eq!(payload["auth"], "token");
    }

    #[test]
    fn omits_auth_on_unsubscribe() {
        let payload =
            subscription_payload("unsubscribe", "account_tx/12", Some("token".to_string()))
                .expect("payload");
        assert_eq!(
            payload,
            json!({"type": "unsubscribe", "channel": "account_tx/12"})
        );
    }

    #[test]
    fn validates_resolution_and_channel() {
        assert_eq!(normalize_resolution("1m").expect("resolution"), "1m");
        assert!(normalize_resolution("2m").is_err());
        assert!(normalize_channel("bad channel").is_err());
    }
}
