use std::time::Duration;

use serde_json::{Value, json};

use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::super::endpoints::WS_URL;

pub struct OndoPublicWebSocket {
    product_table: Option<std::sync::Arc<crate::product_table::ProductTable>>,
    connection: WebSocketConnection,
}

impl OndoPublicWebSocket {
    fn exchange_symbol(&self, symbol: &str, spot: bool) -> Result<String> {
        if let Some(table) = &self.product_table {
            return Ok(table
                .resolve_symbol(
                    "ondo",
                    symbol,
                    Some(if spot { "spot" } else { "swap" }),
                    None,
                )?
                .exchange_symbol
                .clone());
        }
        Ok(if spot {
            symbol.strip_suffix("-SPOT").unwrap_or(symbol)
        } else {
            symbol
        }
        .to_string())
    }

    pub fn set_product_table(&mut self, table: crate::product_table::ProductTable) {
        self.product_table = Some(std::sync::Arc::new(table));
    }

    pub fn new(timeout: Duration) -> Result<Self> {
        Self::with_url(WS_URL, timeout)
    }

    pub fn with_url(url: impl Into<String>, timeout: Duration) -> Result<Self> {
        Ok(Self {
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

    pub async fn subscribe_spot_top_of_book(&mut self, markets: Vec<String>) -> Result<()> {
        self.subscribe("topOfBooksSpot", markets).await
    }

    pub async fn subscribe_spot_depth(&mut self, markets: Vec<String>) -> Result<()> {
        self.subscribe("depthBooksSpot", markets).await
    }

    pub async fn subscribe_spot_trades(&mut self, markets: Vec<String>) -> Result<()> {
        self.subscribe("tradesSpot", markets).await
    }

    pub async fn subscribe_funding_rates(&mut self, markets: Vec<String>) -> Result<()> {
        self.subscribe("fundingRatesPerps", markets).await
    }

    pub async fn subscribe_mark_prices(&mut self, markets: Vec<String>) -> Result<()> {
        self.subscribe("markPricesPerps", markets).await
    }

    pub async fn subscribe_klines(&mut self, market: String, resolution: &str) -> Result<()> {
        let market = self.exchange_symbol(&market, false)?;
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
                | "topOfBooksSpot"
                | "depthBooksSpot"
                | "tradesSpot"
        ) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Ondo public channel: {channel}"
            )));
        }
        let markets = markets
            .into_iter()
            .map(|market| self.exchange_symbol(&market, channel.ends_with("Spot")))
            .collect::<Result<Vec<_>>>()?;
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
