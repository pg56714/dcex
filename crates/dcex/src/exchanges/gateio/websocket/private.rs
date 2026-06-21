use std::time::Duration;

use serde_json::{json, Value};

use crate::crypto::hmac_sha512_hex;
use crate::exchange::unix_timestamp_ms;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::{
    normalize_channel, normalize_event, normalize_symbol, payload_array, validate_credential,
};

const WS_URL: &str = "wss://api.gateio.ws/ws/v4/";

pub struct GateioPrivateWebSocket {
    connection: WebSocketConnection,
    api_key: String,
    api_secret: String,
}

impl GateioPrivateWebSocket {
    pub fn new(api_key: String, api_secret: String, timeout: Duration) -> Result<Self> {
        Self::with_url(api_key, api_secret, WS_URL.to_string(), timeout)
    }

    pub fn with_url(
        api_key: String,
        api_secret: String,
        url: impl Into<String>,
        timeout: Duration,
    ) -> Result<Self> {
        validate_credential("Gate.io API key", &api_key)?;
        validate_credential("Gate.io API secret", &api_secret)?;
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            api_key,
            api_secret,
        })
    }

    pub fn is_connected(&self) -> bool {
        self.connection.is_connected()
    }

    pub async fn connect(&mut self) -> Result<()> {
        self.connection.connect().await
    }

    pub async fn close(&mut self) -> Result<()> {
        self.connection.close().await
    }

    pub async fn ping(&mut self) -> Result<()> {
        let time = unix_timestamp_ms()? / 1_000;
        self.connection
            .send_json(&json!({
                "time": time,
                "channel": "spot.ping",
            }))
            .await
    }

    pub async fn subscribe(&mut self, channel: &str, payload: Vec<String>) -> Result<()> {
        self.send_channel_event(channel, "subscribe", payload).await
    }

    pub async fn unsubscribe(&mut self, channel: &str, payload: Vec<String>) -> Result<()> {
        self.send_channel_event(channel, "unsubscribe", payload)
            .await
    }

    pub async fn subscribe_orders(&mut self, product_symbols: Vec<String>) -> Result<()> {
        let payload = normalize_symbols(product_symbols)?;
        self.subscribe("spot.orders", payload).await
    }

    pub async fn subscribe_user_trades(&mut self, product_symbols: Vec<String>) -> Result<()> {
        let payload = normalize_symbols(product_symbols)?;
        self.subscribe("spot.usertrades", payload).await
    }

    pub async fn subscribe_balances(&mut self) -> Result<()> {
        self.send_request("spot.balances", "subscribe", json!({}))
            .await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    async fn send_channel_event(
        &mut self,
        channel: &str,
        event: &str,
        payload: Vec<String>,
    ) -> Result<()> {
        let payload = payload_array(payload)?;
        self.send_request(channel, event, payload).await
    }

    async fn send_request(&mut self, channel: &str, event: &str, payload: Value) -> Result<()> {
        let channel = normalize_channel(channel)?;
        let event = normalize_event(event)?;
        let time = unix_timestamp_ms()? / 1_000;
        let sign = auth_signature(&self.api_secret, &channel, &event, time)?;
        self.connection
            .send_json(&json!({
                "time": time,
                "channel": channel,
                "event": event,
                "payload": payload,
                "auth": {
                    "method": "api_key",
                    "KEY": self.api_key,
                    "SIGN": sign,
                },
            }))
            .await
    }
}

fn normalize_symbols(product_symbols: Vec<String>) -> Result<Vec<String>> {
    if product_symbols.is_empty() {
        return Err(DcexError::InvalidInput(
            "at least one Gate.io symbol is required.".to_string(),
        ));
    }
    product_symbols
        .into_iter()
        .map(|symbol| normalize_symbol(&symbol))
        .collect()
}

fn auth_signature(api_secret: &str, channel: &str, event: &str, time: u64) -> Result<String> {
    let payload = format!("channel={channel}&event={event}&time={time}");
    hmac_sha512_hex(api_secret.as_bytes(), payload.as_bytes())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn auth_signature_matches_known_payload() {
        assert_eq!(
            auth_signature("secret", "spot.orders", "subscribe", 1_700_000_000)
                .expect("signature"),
            "0dc17b76097b2726573e30bde2a792ce238bbd452f414d949a5f71d5bf1dd50e8e8166a762af6614f0228360882c6e35df2ac39ed0eba1be8b02d9ca1ec9c6c9"
        );
    }

    #[test]
    fn rejects_empty_credentials_and_symbols() {
        assert!(GateioPrivateWebSocket::new(
            "".to_string(),
            "secret".to_string(),
            Duration::from_secs(1),
        )
        .is_err());
        assert!(normalize_symbols(Vec::new()).is_err());
    }
}
