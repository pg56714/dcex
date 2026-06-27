use std::time::Duration;

use serde_json::{json, Value};

use crate::crypto::hmac_sha256_hex;
use crate::exchange::unix_timestamp_ms;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::{normalize_subscription_arg, subscription_arg, validate_credential};

const WS_URL: &str = "wss://www.bitmex.com/realtime";
const AUTH_METHOD: &str = "GET";
const AUTH_PATH: &str = "/realtime";

pub struct BitmexPrivateWebSocket {
    connection: WebSocketConnection,
    api_key: String,
    api_secret: String,
    authenticated: bool,
}

impl BitmexPrivateWebSocket {
    pub fn new(api_key: String, api_secret: String, timeout: Duration) -> Result<Self> {
        Self::with_url(api_key, api_secret, WS_URL.to_string(), timeout)
    }

    pub fn with_url(
        api_key: String,
        api_secret: String,
        url: impl Into<String>,
        timeout: Duration,
    ) -> Result<Self> {
        validate_credential("BitMEX API key", &api_key)?;
        validate_credential("BitMEX API secret", &api_secret)?;
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            api_key,
            api_secret,
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
        let expires = auth_expires(unix_timestamp_ms()?);
        let signature = auth_signature(&self.api_secret, expires)?;
        self.connection
            .connect_with_headers(vec![
                ("api-expires".to_string(), expires.to_string()),
                ("api-signature".to_string(), signature),
                ("api-key".to_string(), self.api_key.clone()),
            ])
            .await?;
        self.authenticated = true;
        Ok(())
    }

    pub async fn login(&mut self) -> Result<()> {
        if !self.connection.is_connected() {
            self.connect().await?;
        }
        self.authenticated = true;
        Ok(())
    }

    pub async fn close(&mut self) -> Result<()> {
        self.authenticated = false;
        self.connection.close().await
    }

    pub async fn ping(&mut self) -> Result<()> {
        self.connection.send_json(&json!({"op": "ping"})).await
    }

    pub async fn subscribe(&mut self, args: Vec<String>) -> Result<()> {
        self.send_operation("subscribe", args).await
    }

    pub async fn unsubscribe(&mut self, args: Vec<String>) -> Result<()> {
        self.send_operation("unsubscribe", args).await
    }

    pub async fn subscribe_orders(&mut self) -> Result<()> {
        self.subscribe(vec![subscription_arg("order", None)?]).await
    }

    pub async fn subscribe_orders_for_symbol(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe(vec![subscription_arg("order", Some(product_symbol))?])
            .await
    }

    pub async fn subscribe_executions(&mut self) -> Result<()> {
        self.subscribe(vec![subscription_arg("execution", None)?])
            .await
    }

    pub async fn subscribe_executions_for_symbol(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe(vec![subscription_arg("execution", Some(product_symbol))?])
            .await
    }

    pub async fn subscribe_positions(&mut self) -> Result<()> {
        self.subscribe(vec![subscription_arg("position", None)?])
            .await
    }

    pub async fn subscribe_positions_for_symbol(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe(vec![subscription_arg("position", Some(product_symbol))?])
            .await
    }

    pub async fn subscribe_margin(&mut self) -> Result<()> {
        self.subscribe(vec![subscription_arg("margin", None)?])
            .await
    }

    pub async fn subscribe_wallet(&mut self) -> Result<()> {
        self.subscribe(vec![subscription_arg("wallet", None)?])
            .await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }

    async fn send_operation(&mut self, op: &str, args: Vec<String>) -> Result<()> {
        if args.is_empty() {
            return Err(DcexError::InvalidInput(
                "at least one BitMEX private WebSocket subscription is required.".to_string(),
            ));
        }
        let op = match op {
            "subscribe" | "unsubscribe" => op,
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported BitMEX private WebSocket operation: {op}"
                )));
            }
        };
        let args = args
            .into_iter()
            .map(|arg| normalize_subscription_arg(&arg))
            .collect::<Result<Vec<_>>>()?;
        self.connection
            .send_json(&json!({
                "op": op,
                "args": args,
            }))
            .await
    }
}

fn auth_signature(api_secret: &str, expires: u64) -> Result<String> {
    let payload = format!("{AUTH_METHOD}{AUTH_PATH}{expires}");
    hmac_sha256_hex(api_secret.as_bytes(), payload.as_bytes())
}

fn auth_expires(timestamp_ms: u64) -> u64 {
    timestamp_ms / 1_000 + 3_600
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn auth_signature_matches_known_payload() {
        assert_eq!(
            auth_signature("secret", 1_700_000_000).expect("signature"),
            "397759ead24da80cb64fac7053e15f4739ad854776f9aad6855262339bff968c"
        );
    }

    #[test]
    fn auth_expires_uses_seconds_plus_one_hour() {
        assert_eq!(auth_expires(1_700_000_000_123), 1_700_003_600);
    }

    #[test]
    fn rejects_empty_credentials() {
        assert!(BitmexPrivateWebSocket::new(
            "".to_string(),
            "secret".to_string(),
            Duration::from_secs(1),
        )
        .is_err());
    }
}
