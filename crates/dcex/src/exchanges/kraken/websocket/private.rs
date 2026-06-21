use std::time::Duration;

use serde_json::{json, Value};

use crate::exchanges::kraken::{KrakenAuth, KrakenClient};
use crate::http::HttpMethod;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

const PRIVATE_WS_URL: &str = "wss://ws-auth.kraken.com/v2";
const SPOT_HTTP_BASE_URL: &str = "https://api.kraken.com";
const TOKEN_PATH: &str = "/0/private/GetWebSocketsToken";

pub struct KrakenPrivateWebSocket {
    connection: WebSocketConnection,
    client: KrakenClient,
    token: Option<String>,
    next_request_id: u64,
}

impl KrakenPrivateWebSocket {
    pub fn new(api_key: String, api_secret: String, timeout: Duration) -> Result<Self> {
        Self::with_urls(
            api_key,
            api_secret,
            timeout,
            SPOT_HTTP_BASE_URL.to_string(),
            PRIVATE_WS_URL.to_string(),
        )
    }

    pub fn with_urls(
        api_key: String,
        api_secret: String,
        timeout: Duration,
        spot_http_base_url: impl Into<String>,
        ws_base_url: impl Into<String>,
    ) -> Result<Self> {
        validate_credential("Kraken API key", &api_key)?;
        validate_credential("Kraken API secret", &api_secret)?;
        let client = KrakenClient::with_base_urls(
            Some(api_key),
            Some(api_secret),
            None,
            None,
            timeout,
            spot_http_base_url.into(),
            "https://futures.kraken.com".to_string(),
        )?;
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(ws_base_url, timeout)?),
            client,
            token: None,
            next_request_id: 1,
        })
    }

    pub fn is_connected(&self) -> bool {
        self.connection.is_connected()
    }

    pub fn token(&self) -> Option<&str> {
        self.token.as_deref()
    }

    pub async fn connect(&mut self) -> Result<String> {
        let token = self.fetch_token().await?;
        self.connection.connect().await?;
        Ok(token)
    }

    pub async fn fetch_token(&mut self) -> Result<String> {
        let response = self
            .client
            .request(
                HttpMethod::Post,
                KrakenAuth::Spot,
                TOKEN_PATH,
                Vec::new(),
                None,
                true,
            )
            .await?;
        let token = extract_token(&response.data)?;
        self.token = Some(token.clone());
        Ok(token)
    }

    pub async fn close(&mut self) -> Result<()> {
        self.connection.close().await
    }

    pub async fn ping(&mut self) -> Result<u64> {
        let request_id = self.next_request_id();
        let payload = json!({
            "method": "ping",
            "req_id": request_id,
        });
        self.connection.send_json(&payload).await?;
        Ok(request_id)
    }

    pub async fn subscribe_balances(&mut self) -> Result<u64> {
        self.send_private_subscription("subscribe", "balances", None)
            .await
    }

    pub async fn unsubscribe_balances(&mut self) -> Result<u64> {
        self.send_private_subscription("unsubscribe", "balances", None)
            .await
    }

    pub async fn subscribe_executions(
        &mut self,
        snap_orders: bool,
        snap_trades: bool,
    ) -> Result<u64> {
        let mut extra = serde_json::Map::new();
        extra.insert("snap_orders".to_string(), Value::Bool(snap_orders));
        extra.insert("snap_trades".to_string(), Value::Bool(snap_trades));
        self.send_private_subscription("subscribe", "executions", Some(extra))
            .await
    }

    pub async fn unsubscribe_executions(&mut self) -> Result<u64> {
        self.send_private_subscription("unsubscribe", "executions", None)
            .await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    async fn send_private_subscription(
        &mut self,
        method: &str,
        channel: &str,
        extra_params: Option<serde_json::Map<String, Value>>,
    ) -> Result<u64> {
        let method = normalize_method(method)?;
        let channel = normalize_channel(channel)?;
        let token = self
            .token
            .as_ref()
            .ok_or_else(|| {
                DcexError::InvalidInput("Kraken WebSocket token is missing.".to_string())
            })?
            .clone();
        let request_id = self.next_request_id();
        let mut params = serde_json::Map::new();
        params.insert("channel".to_string(), Value::String(channel));
        params.insert("token".to_string(), Value::String(token));
        params.insert("req_id".to_string(), Value::from(request_id));
        if let Some(extra_params) = extra_params {
            params.extend(extra_params);
        }
        let payload = json!({
            "method": method,
            "params": params,
        });
        self.connection.send_json(&payload).await?;
        Ok(request_id)
    }

    fn next_request_id(&mut self) -> u64 {
        let id = self.next_request_id;
        self.next_request_id = self.next_request_id.saturating_add(1).max(1);
        id
    }
}

fn extract_token(data: &Value) -> Result<String> {
    data.get("result")
        .and_then(|result| result.get("token"))
        .and_then(Value::as_str)
        .filter(|token| !token.trim().is_empty())
        .map(ToString::to_string)
        .ok_or_else(|| DcexError::Decode("Kraken WebSocket token missing.".to_string()))
}

fn normalize_method(method: &str) -> Result<&'static str> {
    match method.trim() {
        "subscribe" => Ok("subscribe"),
        "unsubscribe" => Ok("unsubscribe"),
        method => Err(DcexError::InvalidInput(format!(
            "unsupported Kraken WebSocket method: {method}"
        ))),
    }
}

fn normalize_channel(channel: &str) -> Result<String> {
    let channel = channel.trim();
    if channel.is_empty() {
        return Err(DcexError::InvalidInput(
            "Kraken private WebSocket channel must not be empty.".to_string(),
        ));
    }
    if !channel
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || character == '_')
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Kraken private WebSocket channel: {channel}"
        )));
    }
    Ok(channel.to_string())
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
    fn extracts_websocket_token() {
        let data = json!({
            "error": [],
            "result": {"token": "token-value", "expires": 900}
        });
        assert_eq!(extract_token(&data).expect("token"), "token-value");
    }

    #[test]
    fn rejects_missing_token() {
        let data = json!({"error": [], "result": {}});
        assert!(extract_token(&data).is_err());
    }
}
