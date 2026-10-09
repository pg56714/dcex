use serde_json::Value;
use url::Url;

use crate::{DcexError, Result};

mod pro;
pub use pro::KucoinProWebSocket;
mod private;
#[cfg(test)]
mod private_tests;
mod public;
#[cfg(test)]
mod public_tests;

pub use private::KucoinPrivateWebSocket;
pub use public::KucoinPublicWebSocket;

#[derive(Clone, Debug, PartialEq, Eq)]
pub(super) struct KucoinBulletToken {
    pub(super) token: String,
    pub(super) endpoint: String,
}

pub(super) fn extract_bullet_token(data: &Value) -> Result<KucoinBulletToken> {
    let payload = data.get("data").unwrap_or(data);
    let token = payload
        .get("token")
        .and_then(Value::as_str)
        .filter(|value| !value.trim().is_empty())
        .map(ToString::to_string)
        .ok_or_else(|| DcexError::Decode("KuCoin bullet token missing.".to_string()))?;
    let endpoint = payload
        .get("instanceServers")
        .and_then(Value::as_array)
        .and_then(|servers| servers.first())
        .and_then(|server| server.get("endpoint"))
        .and_then(Value::as_str)
        .filter(|value| !value.trim().is_empty())
        .map(ToString::to_string)
        .ok_or_else(|| DcexError::Decode("KuCoin WebSocket endpoint missing.".to_string()))?;
    Ok(KucoinBulletToken { token, endpoint })
}

pub(super) fn websocket_url(endpoint: &str, token: &str, connect_id: &str) -> Result<String> {
    let endpoint = endpoint.trim();
    validate_token("KuCoin WebSocket endpoint", endpoint)?;
    validate_token("KuCoin bullet token", token)?;
    validate_token("KuCoin connect id", connect_id)?;

    let mut url = Url::parse(endpoint)
        .map_err(|error| DcexError::InvalidInput(format!("invalid KuCoin endpoint: {error}")))?;
    url.query_pairs_mut()
        .clear()
        .append_pair("token", token)
        .append_pair("connectId", connect_id);
    Ok(url.into())
}

pub(super) fn normalize_symbol(product_symbol: &str, futures: bool) -> Result<String> {
    let product_symbol = product_symbol.trim().to_ascii_uppercase();
    if product_symbol.is_empty()
        || !product_symbol
            .chars()
            .all(|c| c.is_ascii_alphanumeric() || c == '-')
    {
        return Err(DcexError::InvalidInput(
            "unsupported KuCoin WebSocket symbol".into(),
        ));
    }
    if futures && product_symbol.split('-').count() == 2 {
        return Err(DcexError::InvalidInput(
            "KuCoin futures symbol requires a product table or an official contract symbol".into(),
        ));
    }
    super::params::exchange_symbol_fallback(&product_symbol, futures)
}

pub(super) fn normalize_topic(topic: &str) -> Result<String> {
    let topic = topic.trim();
    if topic.is_empty() {
        return Err(DcexError::InvalidInput(
            "KuCoin WebSocket topic must not be empty.".to_string(),
        ));
    }
    if !topic.chars().all(|character| {
        character.is_ascii_alphanumeric() || matches!(character, '/' | ':' | ',' | '-' | '_')
    }) {
        return Err(DcexError::InvalidInput(format!(
            "unsupported KuCoin WebSocket topic: {topic}"
        )));
    }
    Ok(topic.to_string())
}

pub(super) fn validate_credential(label: &str, value: &str) -> Result<()> {
    if value.trim().is_empty() {
        return Err(DcexError::InvalidInput(format!(
            "{label} must not be empty."
        )));
    }
    Ok(())
}

fn validate_token(label: &str, value: &str) -> Result<()> {
    if value.trim().is_empty() {
        return Err(DcexError::InvalidInput(format!(
            "{label} must not be empty."
        )));
    }
    if value.contains(char::is_whitespace) {
        return Err(DcexError::InvalidInput(format!(
            "{label} must not contain whitespace."
        )));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::*;

    #[test]
    fn extracts_bullet_token_and_endpoint() {
        let token = extract_bullet_token(&json!({
            "code": "200000",
            "data": {
                "token": "abc",
                "instanceServers": [{"endpoint": "wss://ws-api-spot.kucoin.com/"}]
            }
        }))
        .expect("token");
        assert_eq!(token.token, "abc");
        assert_eq!(token.endpoint, "wss://ws-api-spot.kucoin.com/");
        assert!(extract_bullet_token(&json!({"data": {}})).is_err());
    }

    #[test]
    fn normalizes_symbol_topic_and_url() {
        assert_eq!(
            normalize_symbol("BTC-USDT-SPOT", false).expect("spot"),
            "BTC-USDT"
        );
        assert_eq!(
            normalize_symbol("BTC-USDT-SWAP", true).expect("futures"),
            "XBTUSDTM"
        );
        assert!(normalize_symbol("BTC-USDT-SPOT", true).is_err());
        assert!(normalize_symbol("BTC-USDT-SWAP", false).is_err());
        assert!(normalize_topic("/market/ticker:BTC-USDT").is_ok());
        assert!(normalize_topic("/market ticker:BTC-USDT").is_err());
        assert_eq!(
            websocket_url("wss://example.test/", "token=value", "dcex-1").expect("url"),
            "wss://example.test/?token=token%3Dvalue&connectId=dcex-1"
        );
    }
}
