use std::time::Duration;

use serde_json::Value;

use crate::product_table::ProductTable;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::Result;

use super::super::client::BackpackClient;
use super::{
    stream_symbol, subscription_payload, validate_depth_speed, validate_kline_interval, WS_URL,
};

pub struct BackpackPublicWebSocket {
    connection: WebSocketConnection,
    client: BackpackClient,
}

impl BackpackPublicWebSocket {
    pub fn new(timeout: Duration) -> Result<Self> {
        Self::with_url(WS_URL.to_string(), timeout)
    }

    pub fn with_url(url: impl Into<String>, timeout: Duration) -> Result<Self> {
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            client: BackpackClient::public(5000, timeout)?,
        })
    }

    pub fn set_product_table(&mut self, product_table: ProductTable) {
        self.client.set_product_table(product_table);
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

    pub async fn subscribe(&mut self, streams: Vec<String>) -> Result<()> {
        let payload = subscription_payload("SUBSCRIBE", streams, None)?;
        self.connection.send_json(&payload).await
    }

    pub async fn unsubscribe(&mut self, streams: Vec<String>) -> Result<()> {
        let payload = subscription_payload("UNSUBSCRIBE", streams, None)?;
        self.connection.send_json(&payload).await
    }

    pub async fn subscribe_book_ticker(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_symbol_stream("bookTicker", product_symbol)
            .await
    }

    pub async fn subscribe_depth(&mut self, product_symbol: &str) -> Result<()> {
        let symbol = self.stream_symbol(product_symbol)?;
        self.subscribe(vec![format!("depth.{symbol}")]).await
    }

    pub async fn subscribe_depth_with_speed(
        &mut self,
        product_symbol: &str,
        speed: &str,
    ) -> Result<()> {
        let symbol = self.stream_symbol(product_symbol)?;
        let stream = format!("depth.{}.{}", validate_depth_speed(speed)?, symbol);
        self.subscribe(vec![stream]).await
    }

    pub async fn subscribe_orderbook(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_depth(product_symbol).await
    }

    pub async fn subscribe_orderbook_with_speed(
        &mut self,
        product_symbol: &str,
        speed: &str,
    ) -> Result<()> {
        self.subscribe_depth_with_speed(product_symbol, speed).await
    }

    pub async fn subscribe_klines(&mut self, product_symbol: &str, interval: &str) -> Result<()> {
        let symbol = self.stream_symbol(product_symbol)?;
        let interval = validate_kline_interval(interval)?;
        self.subscribe(vec![format!("kline.{interval}.{symbol}")])
            .await
    }

    pub async fn subscribe_liquidation(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_symbol_stream("liquidation", product_symbol)
            .await
    }

    pub async fn subscribe_mark_price(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_symbol_stream("markPrice", product_symbol)
            .await
    }

    pub async fn subscribe_ticker(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_symbol_stream("ticker", product_symbol).await
    }

    pub async fn subscribe_open_interest(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_symbol_stream("openInterest", product_symbol)
            .await
    }

    pub async fn subscribe_trades(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_symbol_stream("trade", product_symbol).await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }

    fn stream_symbol(&self, product_symbol: &str) -> Result<String> {
        stream_symbol(self.client.exchange_symbol(product_symbol)?)
    }

    async fn subscribe_symbol_stream(&mut self, prefix: &str, product_symbol: &str) -> Result<()> {
        let symbol = self.stream_symbol(product_symbol)?;
        self.subscribe(vec![format!("{prefix}.{symbol}")]).await
    }
}
