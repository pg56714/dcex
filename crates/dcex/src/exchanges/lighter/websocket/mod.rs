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
    let parts = channel.split('/').collect::<Vec<_>>();
    let valid = match parts.as_slice() {
        ["height"] | ["rfq"] => true,
        ["market_stats", "all"] | ["spot_market_stats", "all"] => true,
        [prefix @ ("order_book" | "ticker" | "market_stats" | "trade" | "spot_market_stats"), market_id] => {
            validate_ws_market(market_id, prefix).is_ok()
        }
        [prefix, account_id]
            if matches!(
                *prefix,
                "account_all"
                    | "user_stats"
                    | "account_tx"
                    | "account_all_orders"
                    | "pool_data"
                    | "pool_info"
                    | "notification"
                    | "account_all_trades"
                    | "account_all_positions"
                    | "account_all_assets"
                    | "account_spot_avg_entry_prices"
            ) =>
        {
            validate_ws_account(account_id).is_ok()
        }
        [prefix, market_id, resolution] if matches!(*prefix, "candle" | "mark_price_candle") => {
            validate_ws_market(market_id, prefix).is_ok()
                && normalize_resolution(resolution).is_ok()
        }
        [prefix, market_id, account_id]
            if matches!(*prefix, "account_market" | "account_orders") =>
        {
            validate_ws_market(market_id, prefix).is_ok() && validate_ws_account(account_id).is_ok()
        }
        _ => false,
    };
    if !valid {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Lighter WebSocket channel: {channel}"
        )));
    }
    Ok(channel.to_string())
}

fn validate_ws_market(value: &str, prefix: &str) -> Result<u64> {
    let value = parse_ws_index(value, "market_id")?;
    let valid = match prefix {
        "market_stats" => value <= 254,
        "spot_market_stats" => (2048..=4094).contains(&value),
        _ => value <= 254 || (2048..=4094).contains(&value),
    };
    if !valid {
        return Err(DcexError::InvalidInput(
            "Lighter WebSocket market_id is outside the valid range".to_string(),
        ));
    }
    Ok(value)
}

fn validate_ws_account(value: &str) -> Result<u64> {
    let value = parse_ws_index(value, "account_id")?;
    if value > (1 << 48) - 2 {
        return Err(DcexError::InvalidInput(
            "Lighter WebSocket account_id is outside the valid range".to_string(),
        ));
    }
    Ok(value)
}

fn parse_ws_index(value: &str, name: &str) -> Result<u64> {
    value.parse::<u64>().map_err(|error| {
        DcexError::InvalidInput(format!("invalid Lighter WebSocket {name}: {error}"))
    })
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
    normalize_channel(&format!("{prefix}/{market_id}"))
}

pub(crate) fn account_channel(prefix: &str, account_index: u64) -> Result<String> {
    normalize_channel(&format!("{prefix}/{account_index}"))
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
        for channel in [
            "height",
            "rfq",
            "order_book/0",
            "ticker/2048",
            "market_stats/all",
            "market_stats/254",
            "trade/4094",
            "candle/0/1m",
            "mark_price_candle/2048/1d",
            "account_all/0",
            "account_market/0/1",
            "user_stats/1",
            "account_tx/1",
            "account_all_orders/1",
            "pool_data/1",
            "pool_info/1",
            "notification/1",
            "account_orders/2048/1",
            "account_all_trades/1",
            "account_all_positions/1",
            "spot_market_stats/all",
            "spot_market_stats/2048",
            "account_all_assets/1",
            "account_spot_avg_entry_prices/1",
        ] {
            assert_eq!(normalize_channel(channel).expect(channel), channel);
        }
        for channel in [
            "order_book/255",
            "market_stats/2048",
            "spot_market_stats/254",
            "trade/4095",
            "candle/0/2m",
            "account_all/281474976710655",
            "unknown/0",
            "trade:0",
        ] {
            assert!(normalize_channel(channel).is_err(), "{channel}");
        }
    }
}
