use std::time::Duration;

use serde_json::Value;

use crate::Result;
use crate::ws::{WebSocketConfig, WebSocketConnection};

use super::super::chains::LighterNetwork;
use super::{legacy_network, market_channel, normalize_resolution, subscription_payload};

pub struct LighterPublicWebSocket {
    network: Option<LighterNetwork>,
    product_table: Option<std::sync::Arc<crate::product_table::ProductTable>>,
    connection: WebSocketConnection,
}

impl LighterPublicWebSocket {
    pub fn resolve_market_symbol(&self, symbol: &str) -> Result<u64> {
        let native = if let Some(table) = &self.product_table {
            table
                .resolve_symbol(
                    self.network
                        .map_or("lighter", LighterNetwork::product_table_exchange),
                    symbol,
                    None,
                    None,
                )?
                .exchange_symbol
                .as_str()
        } else {
            symbol
        };
        native.parse().map_err(|_| {
            crate::DcexError::InvalidInput(
                "Lighter market requires a numeric ID or a loaded product table".into(),
            )
        })
    }

    pub fn set_product_table(&mut self, table: crate::product_table::ProductTable) {
        self.product_table = Some(std::sync::Arc::new(table));
    }

    pub fn with_product_table(mut self, table: crate::product_table::ProductTable) -> Self {
        self.set_product_table(table);
        self
    }

    pub fn new(testnet: bool, timeout: Duration) -> Result<Self> {
        Self::with_network(legacy_network(testnet), timeout)
    }

    pub fn with_network(network: LighterNetwork, timeout: Duration) -> Result<Self> {
        Self::with_network_and_url(network, network.profile().ws_url, timeout)
    }

    /// Connect to `url`; a known network URL selects that network's product-table markets.
    pub fn with_url(url: impl Into<String>, timeout: Duration) -> Result<Self> {
        let url = url.into();
        let network = LighterNetwork::ALL
            .into_iter()
            .find(|network| network.profile().ws_url == url.trim_end_matches('/'));
        Self::with_optional_network(network, url, timeout)
    }

    /// Connect to a custom `url` that serves `network`'s markets.
    pub fn with_network_and_url(
        network: LighterNetwork,
        url: impl Into<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_optional_network(Some(network), url.into(), timeout)
    }

    fn with_optional_network(
        network: Option<LighterNetwork>,
        url: String,
        timeout: Duration,
    ) -> Result<Self> {
        Ok(Self {
            network,
            product_table: None,
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

    pub async fn subscribe_orderbook(&mut self, market_id: impl ToString) -> Result<()> {
        let market_id = self.resolve_market_symbol(&market_id.to_string())?;
        self.subscribe(&market_channel("order_book", market_id)?)
            .await
    }

    pub async fn subscribe_ticker(&mut self, market_id: impl ToString) -> Result<()> {
        let market_id = self.resolve_market_symbol(&market_id.to_string())?;
        self.subscribe(&market_channel("ticker", market_id)?).await
    }

    pub async fn subscribe_market_stats(&mut self, market_id: impl ToString) -> Result<()> {
        let market_id = self.resolve_market_symbol(&market_id.to_string())?;
        self.subscribe(&market_channel("market_stats", market_id)?)
            .await
    }

    pub async fn subscribe_all_market_stats(&mut self) -> Result<()> {
        self.subscribe("market_stats/all").await
    }

    pub async fn subscribe_trades(&mut self, market_id: impl ToString) -> Result<()> {
        let market_id = self.resolve_market_symbol(&market_id.to_string())?;
        self.subscribe(&market_channel("trade", market_id)?).await
    }

    pub async fn subscribe_klines(
        &mut self,
        market_id: impl ToString,
        resolution: &str,
    ) -> Result<()> {
        let market_id = self.resolve_market_symbol(&market_id.to_string())?;
        let resolution = normalize_resolution(resolution)?;
        self.subscribe(&format!("candle/{market_id}/{resolution}"))
            .await
    }

    pub async fn subscribe_mark_price_klines(
        &mut self,
        market_id: impl ToString,
        resolution: &str,
    ) -> Result<()> {
        let market_id = self.resolve_market_symbol(&market_id.to_string())?;
        let resolution = normalize_resolution(resolution)?;
        self.subscribe(&format!("mark_price_candle/{market_id}/{resolution}"))
            .await
    }

    pub async fn subscribe_spot_market_stats(&mut self, market_id: impl ToString) -> Result<()> {
        let market_id = self.resolve_market_symbol(&market_id.to_string())?;
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
