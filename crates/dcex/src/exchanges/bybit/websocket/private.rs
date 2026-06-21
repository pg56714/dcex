use std::time::Duration;

use serde_json::{json, Value};

use crate::crypto::hmac_sha256_hex;
use crate::exchange::unix_timestamp_ms;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

const PRIVATE_WS_URL: &str = "wss://stream.bybit.com/v5/private";
const AUTH_PAYLOAD_PREFIX: &str = "GET/realtime";

pub struct BybitPrivateWebSocket {
    connection: WebSocketConnection,
    api_key: String,
    api_secret: String,
    next_request_id: u64,
    authenticated: bool,
}

impl BybitPrivateWebSocket {
    pub fn new(api_key: String, api_secret: String, timeout: Duration) -> Result<Self> {
        Self::with_url(api_key, api_secret, PRIVATE_WS_URL.to_string(), timeout)
    }

    pub fn with_url(
        api_key: String,
        api_secret: String,
        url: impl Into<String>,
        timeout: Duration,
    ) -> Result<Self> {
        validate_credential("Bybit API key", &api_key)?;
        validate_credential("Bybit API secret", &api_secret)?;
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            api_key,
            api_secret,
            next_request_id: 1,
            authenticated: false,
        })
    }

    pub fn is_connected(&self) -> bool {
        self.connection.is_connected()
    }

    pub fn is_authenticated(&self) -> bool {
        self.authenticated
    }

    pub async fn connect(&mut self) -> Result<()> {
        self.connection.connect().await?;
        self.auth().await
    }

    pub async fn auth(&mut self) -> Result<()> {
        let expires = auth_expires_ms(unix_timestamp_ms()?);
        let signature = auth_signature(&self.api_secret, expires)?;
        let request_id = self.next_request_id();
        let payload = json!({
            "req_id": request_id,
            "op": "auth",
            "args": [self.api_key, expires, signature],
        });
        self.connection.send_json(&payload).await?;
        self.authenticated = true;
        Ok(())
    }

    pub async fn close(&mut self) -> Result<()> {
        self.authenticated = false;
        self.connection.close().await
    }

    pub async fn ping(&mut self) -> Result<String> {
        let request_id = self.next_request_id();
        let payload = json!({
            "req_id": request_id,
            "op": "ping",
        });
        self.connection.send_json(&payload).await?;
        Ok(request_id)
    }

    pub async fn subscribe(&mut self, topics: Vec<String>) -> Result<String> {
        self.send_topics("subscribe", topics).await
    }

    pub async fn unsubscribe(&mut self, topics: Vec<String>) -> Result<String> {
        self.send_topics("unsubscribe", topics).await
    }

    pub async fn subscribe_orders(&mut self) -> Result<String> {
        self.subscribe(vec!["order".to_string()]).await
    }

    pub async fn subscribe_executions(&mut self) -> Result<String> {
        self.subscribe(vec!["execution".to_string()]).await
    }

    pub async fn subscribe_positions(&mut self) -> Result<String> {
        self.subscribe(vec!["position".to_string()]).await
    }

    pub async fn subscribe_wallet(&mut self) -> Result<String> {
        self.subscribe(vec!["wallet".to_string()]).await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    async fn send_topics(&mut self, op: &str, topics: Vec<String>) -> Result<String> {
        if topics.is_empty() {
            return Err(DcexError::InvalidInput(
                "at least one Bybit private WebSocket topic is required.".to_string(),
            ));
        }
        let op = match op {
            "subscribe" | "unsubscribe" => op,
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Bybit WebSocket operation: {op}"
                )));
            }
        };
        let topics = topics
            .into_iter()
            .map(|topic| normalize_topic(&topic))
            .collect::<Result<Vec<_>>>()?;
        let request_id = self.next_request_id();
        let payload = json!({
            "req_id": request_id,
            "op": op,
            "args": topics,
        });
        self.connection.send_json(&payload).await?;
        Ok(request_id)
    }

    fn next_request_id(&mut self) -> String {
        let id = self.next_request_id;
        self.next_request_id = self.next_request_id.saturating_add(1).max(1);
        id.to_string()
    }
}

fn auth_expires_ms(timestamp_ms: u64) -> u64 {
    timestamp_ms + 1_000
}

fn auth_signature(api_secret: &str, expires_ms: u64) -> Result<String> {
    let payload = format!("{AUTH_PAYLOAD_PREFIX}{expires_ms}");
    hmac_sha256_hex(api_secret.as_bytes(), payload.as_bytes())
}

fn normalize_topic(topic: &str) -> Result<String> {
    let topic = topic.trim();
    if topic.is_empty() {
        return Err(DcexError::InvalidInput(
            "Bybit private WebSocket topic must not be empty.".to_string(),
        ));
    }
    if !topic
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || character == '.')
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Bybit private WebSocket topic: {topic}"
        )));
    }
    Ok(topic.to_string())
}

fn validate_credential(label: &str, value: &str) -> Result<()> {
    if value.trim().is_empty() {
        return Err(DcexError::InvalidInput(format!(
            "{label} must not be empty."
        )));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn auth_expires_adds_one_second() {
        assert_eq!(auth_expires_ms(1_700_000_000_000), 1_700_000_001_000);
    }

    #[test]
    fn auth_signature_matches_known_payload() {
        assert_eq!(
            auth_signature("secret", 1_700_000_001_000).expect("signature"),
            "23eb87122b2f700b742777602b09bfd81decc9559bac752cc879747252c1544c"
        );
    }

    #[test]
    fn rejects_invalid_topic() {
        assert!(normalize_topic("order").is_ok());
        assert!(normalize_topic("bad/topic").is_err());
    }
}
