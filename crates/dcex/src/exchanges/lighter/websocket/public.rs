use std::time::Duration;

use serde_json::Value;

use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::Result;

use super::{market_channel, normalize_resolution, subscription_payload, websocket_url};

pub struct LighterPublicWebSocket {
    connection: WebSocketConnection,
}

impl LighterPublicWebSocket {
    pub fn new(testnet: bool, timeout: Duration) -> Result<Self> {
        Self::with_url(websocket_url(testnet).to_string(), timeout)
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
        self.connection.send_ping(Vec::new()).await
    }

    pub async fn subscribe(&mut self, channel: &str) -> Result<()> {
        let payload = subscription_payload("subscribe", channel, None)?;
        self.connection.send_json(&payload).await
    }

    pub async fn unsubscribe(&mut self, channel: &str) -> Result<()> {
        let payload = subscription_payload("unsubscribe", channel, None)?;
        self.connection.send_json(&payload).await
    }

    pub async fn subscribe_orderbook(&mut self, market_id: u64) -> Result<()> {
        self.subscribe(&market_channel("order_book", market_id)?)
            .await
    }

    pub async fn subscribe_ticker(&mut self, market_id: u64) -> Result<()> {
        self.subscribe(&market_channel("ticker", market_id)?).await
    }

    pub async fn subscribe_market_stats(&mut self, market_id: u64) -> Result<()> {
        self.subscribe(&market_channel("market_stats", market_id)?)
            .await
    }

    pub async fn subscribe_all_market_stats(&mut self) -> Result<()> {
        self.subscribe("market_stats/all").await
    }

    pub async fn subscribe_trades(&mut self, market_id: u64) -> Result<()> {
        self.subscribe(&market_channel("trade", market_id)?).await
    }

    pub async fn subscribe_klines(&mut self, market_id: u64, resolution: &str) -> Result<()> {
        let resolution = normalize_resolution(resolution)?;
        self.subscribe(&format!("candle/{market_id}/{resolution}"))
            .await
    }

    pub async fn subscribe_mark_price_klines(
        &mut self,
        market_id: u64,
        resolution: &str,
    ) -> Result<()> {
        let resolution = normalize_resolution(resolution)?;
        self.subscribe(&format!("mark_price_candle/{market_id}/{resolution}"))
            .await
    }

    pub async fn subscribe_spot_market_stats(&mut self, market_id: u64) -> Result<()> {
        self.subscribe(&market_channel("spot_market_stats", market_id)?)
            .await
    }

    pub async fn subscribe_all_spot_market_stats(&mut self) -> Result<()> {
        self.subscribe("spot_market_stats/all").await
    }

    pub async fn subscribe_height(&mut self) -> Result<()> {
        self.subscribe("height").await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }
}
