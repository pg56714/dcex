use std::time::Duration;

use serde_json::{json, Value};

use crate::crypto::hmac_sha256_hex;
use crate::exchange::unix_timestamp_ms;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::{decode_event, normalize_symbol, normalize_topic, validate_credential};

const PRIVATE_WS_URL: &str = "wss://ws-manager-compress.bitmart.com/user?protocol=1.1";
const LOGIN_DOMAIN: &str = "bitmart.WebSocket";

pub struct BitmartPrivateWebSocket {
    connection: WebSocketConnection,
    api_key: String,
    api_secret: String,
    memo: String,
    logged_in: bool,
}

impl BitmartPrivateWebSocket {
    pub fn new(
        api_key: String,
        api_secret: String,
        memo: String,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_url(
            api_key,
            api_secret,
            memo,
            PRIVATE_WS_URL.to_string(),
            timeout,
        )
    }

    pub fn with_url(
        api_key: String,
        api_secret: String,
        memo: String,
        url: impl Into<String>,
        timeout: Duration,
    ) -> Result<Self> {
        validate_credential("BitMart API key", &api_key)?;
        validate_credential("BitMart API secret", &api_secret)?;
        validate_credential("BitMart memo", &memo)?;
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            api_key,
            api_secret,
            memo,
            logged_in: false,
        })
    }

    pub fn is_connected(&self) -> bool {
        self.connection.is_connected()
    }

    pub fn is_logged_in(&self) -> bool {
        self.logged_in
    }

    pub async fn connect(&mut self) -> Result<()> {
        self.connection.connect().await?;
        self.login().await
    }

    pub async fn login(&mut self) -> Result<()> {
        self.logged_in = false;
        let timestamp = unix_timestamp_ms()?.to_string();
        let sign = login_signature(&self.api_secret, &self.memo, &timestamp)?;
        let payload = json!({
            "op": "login",
            "args": [self.api_key, timestamp, sign],
        });
        self.connection.send_json(&payload).await?;
        let payload = self.connection.recv_bytes().await?;
        let event = decode_event(payload)?;
        validate_login_ack(&event)?;
        self.logged_in = true;
        Ok(())
    }

    pub async fn close(&mut self) -> Result<()> {
        self.logged_in = false;
        self.connection.close().await
    }

    pub async fn ping(&mut self) -> Result<()> {
        self.connection.send_text("ping").await
    }

    pub async fn subscribe(&mut self, topics: Vec<String>) -> Result<()> {
        self.send_operation("subscribe", topics).await
    }

    pub async fn unsubscribe(&mut self, topics: Vec<String>) -> Result<()> {
        self.send_operation("unsubscribe", topics).await
    }

    pub async fn subscribe_orders(&mut self, product_symbol: Option<&str>) -> Result<()> {
        let topic = match product_symbol {
            Some(product_symbol) => {
                let symbol = normalize_symbol(product_symbol)?;
                format!("spot/user/order:{symbol}")
            }
            None => "spot/user/orders:ALL_SYMBOLS".to_string(),
        };
        self.subscribe(vec![topic]).await
    }

    pub async fn subscribe_balance(&mut self) -> Result<()> {
        self.subscribe(vec!["spot/user/balance:BALANCE_UPDATE".to_string()])
            .await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        let payload = self.connection.recv_bytes().await?;
        decode_event(payload)
    }

    async fn send_operation(&mut self, op: &str, topics: Vec<String>) -> Result<()> {
        if topics.is_empty() {
            return Err(DcexError::InvalidInput(
                "at least one BitMart private WebSocket topic is required.".to_string(),
            ));
        }
        let op = match op {
            "subscribe" | "unsubscribe" => op,
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported BitMart private WebSocket operation: {op}"
                )));
            }
        };
        let topics = topics
            .into_iter()
            .map(|topic| normalize_topic(&topic, "private WebSocket topic"))
            .collect::<Result<Vec<_>>>()?;
        let payload = json!({
            "op": op,
            "args": topics,
        });
        self.connection.send_json(&payload).await
    }
}

fn login_signature(api_secret: &str, memo: &str, timestamp: &str) -> Result<String> {
    let payload = format!("{timestamp}#{memo}#{LOGIN_DOMAIN}");
    hmac_sha256_hex(api_secret.as_bytes(), payload.as_bytes())
}

fn validate_login_ack(event: &Value) -> Result<()> {
    let event_name = event
        .get("event")
        .or_else(|| event.get("op"))
        .and_then(Value::as_str);
    let success = event.get("success").and_then(Value::as_bool);
    let status_codes = ["code", "errorCode", "error_code"]
        .into_iter()
        .filter_map(|field| event.get(field).and_then(value_as_string))
        .collect::<Vec<_>>();
    let codes_are_successful = status_codes
        .iter()
        .all(|code| matches!(code.as_str(), "0" | "1000" | "200"));
    if event_name == Some("login") && success != Some(false) && codes_are_successful {
        Ok(())
    } else {
        Err(DcexError::Runtime(format!(
            "BitMart WebSocket login rejected: {event}"
        )))
    }
}

fn value_as_string(value: &Value) -> Option<String> {
    match value {
        Value::String(value) => Some(value.clone()),
        Value::Number(value) => Some(value.to_string()),
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::*;

    #[test]
    fn login_signature_matches_official_example() {
        assert_eq!(
            login_signature(
                "6c6c98544461bbe71db2bca4c6d7fd0021e0ba9efc215f9c6ad41852df9d9df9",
                "test001",
                "1589267764859",
            )
            .expect("signature"),
            "3ceeb7e1b8cb165a975e28a2e2dfaca4d30b358873c0351c1a071d8c83314556"
        );
    }

    #[test]
    fn rejects_empty_credentials() {
        assert!(BitmartPrivateWebSocket::new(
            "".to_string(),
            "secret".to_string(),
            "memo".to_string(),
            Duration::from_secs(1),
        )
        .is_err());
    }

    #[test]
    fn validates_login_ack() {
        assert!(validate_login_ack(&json!({"event": "login"})).is_ok());
        assert!(validate_login_ack(&json!({"event": "login", "code": 1000})).is_ok());
        assert!(validate_login_ack(&json!({"event": "login", "errorCode": "0"})).is_ok());
        assert!(validate_login_ack(&json!({"event": "login", "errorCode": "30001"})).is_err());
        assert!(validate_login_ack(&json!({"event": "error", "code": 1000})).is_err());
    }
}
