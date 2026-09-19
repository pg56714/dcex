use std::time::Duration;

use serde_json::{json, Value};

use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::super::endpoints::WS_URL;

pub struct OndoPublicWebSocket {
    connection: WebSocketConnection,
}

impl OndoPublicWebSocket {
    pub fn new(timeout: Duration) -> Result<Self> {
        Self::with_url(WS_URL, timeout)
    }

    pub fn with_url(url: impl Into<String>, timeout: Duration) -> Result<Self> {
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
        self.connection.send_json(&json!({"op": "ping"})).await
    }

    pub async fn subscribe(&mut self, channel: &str, markets: Vec<String>) -> Result<()> {
        self.subscription("subscribe", channel, markets).await
    }

    pub async fn unsubscribe(&mut self, channel: &str, markets: Vec<String>) -> Result<()> {
        self.subscription("unsubscribe", channel, markets).await
    }

    pub async fn subscribe_top_of_book(&mut self, markets: Vec<String>) -> Result<()> {
        self.subscribe("topOfBooksPerps", markets).await
    }

    pub async fn subscribe_depth(&mut self, markets: Vec<String>) -> Result<()> {
        self.subscribe("depthBooksPerps", markets).await
    }

    pub async fn subscribe_trades(&mut self, markets: Vec<String>) -> Result<()> {
        self.subscribe("tradesPerps", markets).await
    }

    pub async fn subscribe_funding_rates(&mut self, markets: Vec<String>) -> Result<()> {
        self.subscribe("fundingRatesPerps", markets).await
    }

    pub async fn subscribe_mark_prices(&mut self, markets: Vec<String>) -> Result<()> {
        self.subscribe("markPricesPerps", markets).await
    }

    pub async fn subscribe_klines(&mut self, market: String, resolution: &str) -> Result<()> {
        if !matches!(resolution, "1" | "5" | "15" | "1H" | "4H" | "1D" | "1W") {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Ondo kline resolution: {resolution}"
            )));
        }
        self.connection
            .send_json(&json!({
                "op": "subscribe",
                "channel": "kLinePerps",
                "markets": [market],
                "resolution": resolution,
            }))
            .await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }

    async fn subscription(&mut self, op: &str, channel: &str, markets: Vec<String>) -> Result<()> {
        if !matches!(
            channel,
            "topOfBooksPerps"
                | "depthBooksPerps"
                | "tradesPerps"
                | "fundingRatesPerps"
                | "markPricesPerps"
        ) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Ondo public channel: {channel}"
            )));
        }
        if markets.is_empty() {
            self.connection
                .send_json(&json!({"op": op, "channel": channel}))
                .await
        } else {
            self.connection
                .send_json(&json!({"op": op, "channel": channel, "markets": markets}))
                .await
        }
    }
}
