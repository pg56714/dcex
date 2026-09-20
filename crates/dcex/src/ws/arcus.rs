//! Arcus WebSocket subscriptions. Account streams are publicly readable by
//! address; API keys authorize writes, not subscriptions.

use std::time::Duration;

use serde_json::{json, Value};

use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

pub struct ArcusWebSocket {
    connection: WebSocketConnection,
}

impl ArcusWebSocket {
    pub fn new(testnet: bool, timeout: Duration) -> Result<Self> {
        let url = if testnet {
            "wss://api.testnet.arcus.xyz/v1/ws"
        } else {
            "wss://api.arcus.xyz/v1/ws"
        };
        Self::with_url(url.to_string(), timeout)
    }

    pub fn with_url(url: String, timeout: Duration) -> Result<Self> {
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
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
        self.connection.send_ping(Vec::new()).await
    }

    pub async fn subscribe(&mut self, channel: &str, id: Option<&str>) -> Result<()> {
        self.send_subscription("subscribe", channel, id).await
    }

    pub async fn unsubscribe(&mut self, channel: &str, id: Option<&str>) -> Result<()> {
        self.send_subscription("unsubscribe", channel, id).await
    }

    async fn send_subscription(
        &mut self,
        action: &str,
        channel: &str,
        id: Option<&str>,
    ) -> Result<()> {
        let required_id = match channel {
            "l2Orderbook"
            | "l2OrderbookUpdates"
            | "trades"
            | "bbo"
            | "predictedFunding"
            | "candles"
            | "account"
            | "positions"
            | "spotPositions"
            | "orders"
            | "userFills"
            | "spotFills"
            | "funding"
            | "accountAttributeUpdates"
            | "accountTransferUpdates" => true,
            "markets"
            | "oraclePrices"
            | "exchangeAttributeUpdates"
            | "marketAttributes"
            | "lendingRates" => false,
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unknown Arcus WS channel: {channel}"
                )))
            }
        };
        if required_id && id.is_none_or(str::is_empty) {
            return Err(DcexError::InvalidInput(format!(
                "Arcus {channel} subscription requires an id"
            )));
        }
        if !required_id && id.is_some() && channel != "oraclePrices" {
            return Err(DcexError::InvalidInput(format!(
                "Arcus {channel} does not use an id"
            )));
        }
        let mut payload = json!({"type": action, "channel": channel});
        if let Some(id) = id {
            payload["id"] = Value::String(id.to_string());
        }
        self.connection.send_json(&payload).await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn invalid_subscription_is_rejected_without_network() {
        let mut client = ArcusWebSocket::new(false, Duration::from_secs(1)).unwrap();
        assert!(client.subscribe("orders", None).await.is_err());
        assert!(client.subscribe("unknown", Some("BTC-USD")).await.is_err());
    }
}
