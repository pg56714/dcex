use std::time::Duration;

use serde_json::{json, Value};

use crate::exchange::unix_timestamp_ms;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::super::endpoints::WS_URL;
use super::super::signing::{adjusted_timestamp_ms, server_clock_offset_ms, websocket_signature};

pub struct OndoPrivateWebSocket {
    connection: WebSocketConnection,
    api_key_id: Option<String>,
    api_secret: Option<String>,
    timestamp_offset_ms: i64,
    authenticated: bool,
}

impl OndoPrivateWebSocket {
    pub fn new(
        api_key_id: Option<String>,
        api_secret: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_url(api_key_id, api_secret, WS_URL, timeout)
    }

    pub fn with_url(
        api_key_id: Option<String>,
        api_secret: Option<String>,
        url: impl Into<String>,
        timeout: Duration,
    ) -> Result<Self> {
        if api_key_id.is_some() != api_secret.is_some() {
            return Err(DcexError::InvalidInput(
                "Ondo private WebSocket requires API key ID and secret together".to_string(),
            ));
        }
        if api_key_id.is_none() {
            return Err(DcexError::InvalidInput(
                "Ondo private WebSocket requires API key credentials".to_string(),
            ));
        }
        if [api_key_id.as_deref(), api_secret.as_deref()]
            .iter()
            .flatten()
            .any(|value| value.trim().is_empty())
        {
            return Err(DcexError::InvalidInput(
                "Ondo private WebSocket credentials must not be empty".to_string(),
            ));
        }
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            api_key_id,
            api_secret,
            timestamp_offset_ms: 0,
            authenticated: false,
        })
    }

    pub fn is_connected(&self) -> bool {
        self.connection.is_connected()
    }

    pub async fn connect(&mut self) -> Result<()> {
        if self.authenticated && self.connection.is_connected() {
            return Ok(());
        }
        self.connection.connect().await?;
        let key = self.api_key_id.as_deref().expect("validated API key ID");
        let secret = self.api_secret.as_deref().expect("validated API secret");
        for attempt in 0..2 {
            let time = adjusted_timestamp_ms(self.timestamp_offset_ms)?;
            let sign = websocket_signature(secret, &time)?;
            let login = json!({"op": "login", "args": {"key": key, "time": time, "sign": sign}});
            self.connection.send_json(&login).await?;
            let response = self.connection.recv_json().await?;
            if response.get("type").and_then(Value::as_str) == Some("loggedIn") {
                self.authenticated = true;
                return Ok(());
            }
            if attempt == 0 && response.get("type").and_then(Value::as_str) == Some("error") {
                if let Some(offset) = response
                    .get("msg")
                    .and_then(Value::as_str)
                    .and_then(|message| server_clock_offset_ms(message, unix_timestamp_ms().ok()?))
                {
                    self.timestamp_offset_ms = offset;
                    self.connection.close().await?;
                    self.connection.connect().await?;
                    continue;
                }
            }
            self.connection.close().await?;
            return Err(DcexError::Runtime(format!(
                "Ondo WebSocket login failed: {response}"
            )));
        }
        Err(DcexError::Runtime(
            "Ondo WebSocket login failed after timestamp retry".to_string(),
        ))
    }

    pub async fn close(&mut self) -> Result<()> {
        self.authenticated = false;
        self.connection.close().await
    }

    pub async fn ping(&mut self) -> Result<()> {
        self.connection.send_json(&json!({"op": "ping"})).await
    }

    pub async fn subscribe(&mut self, channel: &str, markets: Vec<String>) -> Result<()> {
        if !self.authenticated {
            return Err(DcexError::InvalidInput(
                "Ondo private WebSocket is not authenticated; call connect first".to_string(),
            ));
        }
        if !matches!(
            channel,
            "ordersPerps"
                | "fillsPerps"
                | "positionsPerps"
                | "balancePerps"
                | "liquidationAnnouncementsPerps"
                | "liquidationPerps"
                | "marginTransfersPerps"
                | "ordersSummariesPerps"
                | "fundingPaymentsPerps"
                | "deposits"
                | "withdrawals"
        ) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Ondo private channel: {channel}"
            )));
        }
        if channel == "ordersSummariesPerps" && markets.is_empty() {
            return Err(DcexError::InvalidInput(
                "Ondo ordersSummariesPerps requires at least one market".to_string(),
            ));
        }
        if markets.is_empty() {
            self.connection
                .send_json(&json!({"op": "subscribe", "channel": channel}))
                .await
        } else {
            self.connection
                .send_json(&json!({"op": "subscribe", "channel": channel, "markets": markets}))
                .await
        }
    }

    pub async fn subscribe_orders(&mut self, markets: Vec<String>) -> Result<()> {
        self.subscribe("ordersPerps", markets).await
    }

    pub async fn subscribe_fills(&mut self, markets: Vec<String>) -> Result<()> {
        self.subscribe("fillsPerps", markets).await
    }

    pub async fn subscribe_positions(&mut self) -> Result<()> {
        self.subscribe("positionsPerps", Vec::new()).await
    }

    pub async fn subscribe_balance(&mut self) -> Result<()> {
        self.subscribe("balancePerps", Vec::new()).await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }
}
