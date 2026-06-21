use std::time::Duration;

use serde_json::Value;

use crate::exchange::unix_timestamp_ms;
use crate::product_table::ProductTable;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::Result;

use super::super::client::BackpackClient;
use super::{stream_symbol, subscription_payload, WS_URL};

pub struct BackpackPrivateWebSocket {
    connection: WebSocketConnection,
    client: BackpackClient,
}

impl BackpackPrivateWebSocket {
    pub fn new(
        api_key: String,
        api_secret: String,
        window: u64,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_url(api_key, api_secret, window, WS_URL.to_string(), timeout)
    }

    pub fn with_url(
        api_key: String,
        api_secret: String,
        window: u64,
        url: impl Into<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            client: BackpackClient::new(Some(api_key), Some(api_secret), window, timeout)?,
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
        let timestamp = unix_timestamp_ms()?.to_string();
        let signature = self.client.websocket_signature(&timestamp)?;
        let payload = subscription_payload("SUBSCRIBE", streams, Some(signature))?;
        self.connection.send_json(&payload).await
    }

    pub async fn unsubscribe(&mut self, streams: Vec<String>) -> Result<()> {
        let payload = subscription_payload("UNSUBSCRIBE", streams, None)?;
        self.connection.send_json(&payload).await
    }

    pub async fn subscribe_orders(&mut self, product_symbol: Option<&str>) -> Result<()> {
        self.subscribe_account_stream("orderUpdate", product_symbol)
            .await
    }

    pub async fn subscribe_positions(&mut self, product_symbol: Option<&str>) -> Result<()> {
        self.subscribe_account_stream("positionUpdate", product_symbol)
            .await
    }

    pub async fn subscribe_rfq(&mut self, product_symbol: Option<&str>) -> Result<()> {
        self.subscribe_account_stream("rfqUpdate", product_symbol)
            .await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    fn stream_symbol(&self, product_symbol: &str) -> Result<String> {
        stream_symbol(self.client.exchange_symbol(product_symbol)?)
    }

    async fn subscribe_account_stream(
        &mut self,
        suffix: &str,
        product_symbol: Option<&str>,
    ) -> Result<()> {
        let stream = if let Some(product_symbol) = product_symbol {
            format!("account.{suffix}.{}", self.stream_symbol(product_symbol)?)
        } else {
            format!("account.{suffix}")
        };
        self.subscribe(vec![stream]).await
    }
}
