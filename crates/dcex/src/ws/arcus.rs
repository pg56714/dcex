//! Arcus WebSocket subscriptions and trading RPC. Account streams are publicly
//! readable by address; API keys authorize writes, not subscriptions.

use std::time::Duration;

use serde_json::{Value, json};

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

    /// Sends a read-only RPC. Responses are correlated by the caller's numeric id.
    pub async fn get_request(&mut self, id: u64, method: &str, payload: Value) -> Result<()> {
        if ![
            "l2orderbook",
            "bbo",
            "mids",
            "account",
            "fills",
            "interest",
            "orders",
            "markets",
            "spotAssets",
            "prices",
            "positions",
            "spotPositions",
            "spotFills",
            "leverages",
            "ratelimit",
        ]
        .contains(&method)
            || !payload.is_object()
        {
            return Err(DcexError::InvalidInput(
                "Arcus invalid read-only RPC method or payload".into(),
            ));
        }
        self.connection
            .send_json(&json!({"type":"get","id":id,"request":{"type":method,"payload":payload}}))
            .await
    }

    /// Sends a frame produced by `ArcusClient::sign_websocket_request` unchanged.
    /// Read the 202 acknowledgement and order/fill updates separately; do not retry blindly.
    pub async fn post_request(&mut self, frame: Value) -> Result<()> {
        validate_signed_frame(&frame)?;
        self.connection.send_json(&frame).await
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
            | "settleLoanResults"
            | "accountTransferUpdates" => true,
            "markets"
            | "oraclePrices"
            | "exchangeAttributeUpdates"
            | "marketAttributes"
            | "lendingRates" => false,
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unknown Arcus WS channel: {channel}"
                )));
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

fn validate_signed_frame(frame: &Value) -> Result<()> {
    let invalid =
        || DcexError::InvalidInput("Arcus requires a complete signed trading RPC frame".into());
    let object = frame.as_object().ok_or_else(invalid)?;
    if object.len() != 3 || frame["type"] != "post" || frame["id"].as_u64().is_none() {
        return Err(invalid());
    }
    let request = frame["request"].as_object().ok_or_else(invalid)?;
    if request
        .keys()
        .any(|k| !["type", "payload", "apiKey", "timestamp", "signature"].contains(&k.as_str()))
    {
        return Err(invalid());
    }
    if !request
        .get("type")
        .and_then(Value::as_str)
        .is_some_and(|m| {
            [
                "placeOrder",
                "cancelOrder",
                "cancelAllOrders",
                "scheduleCancel",
                "modifyOrder",
                "batchPlaceOrders",
                "batchCancelOrders",
                "batchModifyOrders",
                "setLeverage",
                "adjustIsolatedMargin",
            ]
            .contains(&m)
        })
    {
        return Err(invalid());
    }
    let payload = request
        .get("payload")
        .and_then(Value::as_object)
        .ok_or_else(invalid)?;
    let address = payload
        .get("address")
        .and_then(Value::as_str)
        .ok_or_else(invalid)?;
    if address.len() != 42
        || !address.starts_with("0x")
        || !address[2..].bytes().all(|b| b.is_ascii_hexdigit())
    {
        return Err(invalid());
    }
    for (field, size) in [("apiKey", 64), ("signature", 128)] {
        if !request
            .get(field)
            .and_then(Value::as_str)
            .is_some_and(|s| s.len() == size && s.bytes().all(|b| b.is_ascii_hexdigit()))
        {
            return Err(invalid());
        }
    }
    let timestamp = request
        .get("timestamp")
        .and_then(Value::as_str)
        .and_then(|s| s.parse::<u64>().ok())
        .ok_or_else(invalid)?;
    if payload
        .get("timestamp")
        .is_some_and(|t| t.as_u64() != Some(timestamp))
    {
        return Err(DcexError::InvalidInput(
            "Arcus payload timestamp differs from signed envelope".into(),
        ));
    }
    if payload
        .get("clientTime")
        .is_some_and(|t| t.as_str().and_then(|s| s.parse::<u64>().ok()) != Some(timestamp))
    {
        return Err(DcexError::InvalidInput(
            "Arcus clientTime differs from signed envelope".into(),
        ));
    }
    for key in ["orders", "cancels", "modifies"] {
        if let Some(items) = payload.get(key) {
            let items = items
                .as_array()
                .filter(|items| !items.is_empty())
                .ok_or_else(invalid)?;
            for item in items {
                if item.get("timestamp").and_then(Value::as_u64).or_else(|| {
                    item.get("clientTime")
                        .and_then(Value::as_str)
                        .and_then(|v| v.parse::<u64>().ok())
                }) != Some(timestamp)
                    || !item["signature"]
                        .as_str()
                        .is_some_and(|s| s.len() == 128 && s.bytes().all(|b| b.is_ascii_hexdigit()))
                {
                    return Err(invalid());
                }
            }
        }
    }
    Ok(())
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
