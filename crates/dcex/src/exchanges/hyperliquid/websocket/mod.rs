mod private;
mod public;

pub use private::HyperliquidPrivateWebSocket;
pub use public::HyperliquidPublicWebSocket;

use serde_json::{Map, Value};

use crate::{DcexError, Result};

use super::params::{fallback_coin, is_canonical_product_symbol};

pub(crate) const MAINNET_WS_URL: &str = "wss://api.hyperliquid.xyz/ws";
pub(crate) const TESTNET_WS_URL: &str = "wss://api.hyperliquid-testnet.xyz/ws";

pub(crate) fn websocket_url(testnet: bool) -> &'static str {
    if testnet {
        TESTNET_WS_URL
    } else {
        MAINNET_WS_URL
    }
}

pub(crate) fn subscription_payload(method: &str, subscription: Value) -> Result<Value> {
    let method = match method {
        "subscribe" | "unsubscribe" => method,
        _ => {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Hyperliquid WebSocket method: {method}"
            )));
        }
    };
    let subscription = normalize_subscription(subscription)?;
    let mut payload = Map::new();
    payload.insert("method".to_string(), Value::String(method.to_string()));
    payload.insert("subscription".to_string(), Value::Object(subscription));
    Ok(Value::Object(payload))
}

pub(crate) fn normalize_subscription(subscription: Value) -> Result<Map<String, Value>> {
    let Value::Object(subscription) = subscription else {
        return Err(DcexError::InvalidInput(
            "Hyperliquid WebSocket subscription must be a JSON object.".to_string(),
        ));
    };
    let subscription_type = subscription
        .get("type")
        .and_then(Value::as_str)
        .map(str::trim)
        .filter(|value| !value.is_empty())
        .ok_or_else(|| {
            DcexError::InvalidInput(
                "Hyperliquid WebSocket subscription requires a non-empty type.".to_string(),
            )
        })?;
    validate_token(subscription_type, "subscription type")?;
    Ok(subscription)
}

pub(crate) fn coin_subscription(subscription_type: &str, coin: String) -> Result<Value> {
    validate_token(subscription_type, "subscription type")?;
    let coin = normalize_coin(&coin)?;
    Ok(serde_json::json!({
        "type": subscription_type,
        "coin": coin,
    }))
}

pub(crate) fn user_subscription(
    subscription_type: &str,
    user: &str,
    dex: Option<&str>,
) -> Result<Value> {
    validate_token(subscription_type, "subscription type")?;
    let user = normalize_user(user)?;
    let mut subscription = Map::new();
    subscription.insert(
        "type".to_string(),
        Value::String(subscription_type.to_string()),
    );
    subscription.insert("user".to_string(), Value::String(user));
    if let Some(dex) = dex {
        subscription.insert("dex".to_string(), Value::String(normalize_dex(dex)?));
    }
    Ok(Value::Object(subscription))
}

pub(crate) fn all_mids_subscription(dex: Option<&str>) -> Result<Value> {
    let mut subscription = Map::new();
    subscription.insert("type".to_string(), Value::String("allMids".to_string()));
    if let Some(dex) = dex {
        subscription.insert("dex".to_string(), Value::String(normalize_dex(dex)?));
    }
    Ok(Value::Object(subscription))
}

pub(crate) fn candle_subscription(coin: String, interval: &str) -> Result<Value> {
    let interval = normalize_interval(interval)?;
    let mut subscription = coin_subscription("candle", coin)?
        .as_object()
        .expect("coin subscription object")
        .clone();
    subscription.insert("interval".to_string(), Value::String(interval));
    Ok(Value::Object(subscription))
}

pub(crate) fn l2_book_subscription(
    coin: String,
    n_sig_figs: Option<u64>,
    mantissa: Option<u64>,
) -> Result<Value> {
    validate_l2_book_precision(n_sig_figs, mantissa)?;
    let mut subscription = coin_subscription("l2Book", coin)?
        .as_object()
        .expect("coin subscription object")
        .clone();
    if let Some(n_sig_figs) = n_sig_figs {
        subscription.insert(
            "nSigFigs".to_string(),
            Value::Number(serde_json::Number::from(n_sig_figs)),
        );
    }
    if let Some(mantissa) = mantissa {
        subscription.insert(
            "mantissa".to_string(),
            Value::Number(serde_json::Number::from(mantissa)),
        );
    }
    Ok(Value::Object(subscription))
}

fn validate_l2_book_precision(n_sig_figs: Option<u64>, mantissa: Option<u64>) -> Result<()> {
    if let Some(n_sig_figs) = n_sig_figs {
        if !matches!(n_sig_figs, 2 | 3 | 4 | 5) {
            return Err(DcexError::InvalidInput(format!(
                "Hyperliquid l2Book nSigFigs must be one of 2, 3, 4, or 5; got {n_sig_figs}."
            )));
        }
    }
    if let Some(mantissa) = mantissa {
        if n_sig_figs != Some(5) {
            return Err(DcexError::InvalidInput(
                "Hyperliquid l2Book mantissa requires nSigFigs to be 5.".to_string(),
            ));
        }
        if !matches!(mantissa, 1 | 2 | 5) {
            return Err(DcexError::InvalidInput(format!(
                "Hyperliquid l2Book mantissa must be one of 1, 2, or 5; got {mantissa}."
            )));
        }
    }
    Ok(())
}

pub(crate) fn normalize_coin(product_symbol: &str) -> Result<String> {
    let is_canonical_product_symbol = is_canonical_product_symbol(product_symbol);
    let coin = fallback_coin(product_symbol);
    let coin = coin.trim();
    if coin.is_empty() {
        return Err(DcexError::InvalidInput(
            "Hyperliquid coin must not be empty.".to_string(),
        ));
    }
    if !coin.chars().all(|character| {
        character.is_ascii_alphanumeric() || matches!(character, '-' | '_' | '/' | ':' | '#' | '@')
    }) {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Hyperliquid coin: {coin}"
        )));
    }
    if is_canonical_product_symbol {
        if product_symbol.to_ascii_uppercase().ends_with("-SPOT") {
            return Err(DcexError::InvalidInput(format!(
                "cannot safely resolve Hyperliquid spot coin for {product_symbol}; load a product table or pass the official raw coin"
            )));
        }
        Ok(coin.to_ascii_uppercase())
    } else {
        Ok(coin.to_string())
    }
}

pub(crate) fn normalize_user(user: &str) -> Result<String> {
    let user = user.trim();
    if user.len() != 42 || !user.starts_with("0x") {
        return Err(DcexError::InvalidInput(
            "Hyperliquid user address must be a 0x-prefixed 20-byte address.".to_string(),
        ));
    }
    if !user[2..]
        .chars()
        .all(|character| character.is_ascii_hexdigit())
    {
        return Err(DcexError::InvalidInput(
            "Hyperliquid user address must contain only hex digits.".to_string(),
        ));
    }
    Ok(user.to_ascii_lowercase())
}

pub(crate) fn normalize_dex(dex: &str) -> Result<String> {
    let dex = dex.trim();
    if dex.is_empty() {
        return Err(DcexError::InvalidInput(
            "Hyperliquid dex must not be empty.".to_string(),
        ));
    }
    validate_token(dex, "dex")?;
    Ok(dex.to_string())
}

pub(crate) fn normalize_interval(interval: &str) -> Result<String> {
    let interval = interval.trim();
    let supported = matches!(
        interval,
        "1m" | "3m"
            | "5m"
            | "15m"
            | "30m"
            | "1h"
            | "2h"
            | "4h"
            | "8h"
            | "12h"
            | "1d"
            | "3d"
            | "1w"
            | "1M"
    );
    if supported {
        Ok(interval.to_string())
    } else {
        Err(DcexError::InvalidInput(format!(
            "unsupported Hyperliquid candle interval: {interval}"
        )))
    }
}

fn validate_token(value: &str, label: &str) -> Result<()> {
    if value.trim().is_empty() {
        return Err(DcexError::InvalidInput(format!(
            "Hyperliquid {label} must not be empty."
        )));
    }
    if !value
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || matches!(character, '-' | '_'))
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Hyperliquid {label}: {value}"
        )));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::*;

    #[test]
    fn builds_subscription_payload() {
        let payload = subscription_payload("subscribe", json!({"type": "trades", "coin": "BTC"}))
            .expect("payload");
        assert_eq!(payload["method"], "subscribe");
        assert_eq!(payload["subscription"]["type"], "trades");
        assert_eq!(payload["subscription"]["coin"], "BTC");
    }

    #[test]
    fn rejects_invalid_subscription() {
        assert!(subscription_payload("subscribe", json!("bad")).is_err());
        assert!(subscription_payload("subscribe", json!({})).is_err());
        assert!(subscription_payload("bad", json!({"type": "trades"})).is_err());
    }

    #[test]
    fn normalizes_coin_from_canonical_symbol() {
        assert_eq!(normalize_coin("btc-usdc-swap").expect("coin"), "BTC");
        assert_eq!(normalize_coin("ETH").expect("coin"), "ETH");
    }

    #[test]
    fn preserves_raw_hyperliquid_coin_symbols() {
        assert_eq!(normalize_coin("kPEPE").expect("coin"), "kPEPE");
        assert_eq!(normalize_coin("test:ABC").expect("coin"), "test:ABC");
        assert_eq!(normalize_coin("test:ABC-1").expect("coin"), "test:ABC-1");
        assert_eq!(normalize_coin("@107").expect("coin"), "@107");
        assert_eq!(normalize_coin("#10").expect("coin"), "#10");
        assert!(normalize_coin("HYPE-USDC-SPOT").is_err());
    }

    #[test]
    fn validates_user_address() {
        let user = normalize_user("0x000000000000000000000000000000000000000A").expect("user");
        assert_eq!(user, "0x000000000000000000000000000000000000000a");
        assert!(normalize_user("not-an-address").is_err());
    }

    #[test]
    fn validates_l2_book_precision() {
        assert!(l2_book_subscription("BTC".to_string(), Some(5), Some(2)).is_ok());
        assert!(l2_book_subscription("BTC".to_string(), Some(1), None).is_err());
        assert!(l2_book_subscription("BTC".to_string(), Some(4), Some(2)).is_err());
        assert!(l2_book_subscription("BTC".to_string(), Some(5), Some(3)).is_err());
    }
}
