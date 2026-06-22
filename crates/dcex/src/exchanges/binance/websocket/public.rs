use std::sync::Arc;
use std::time::Duration;

use serde_json::{json, Value};

use crate::product_table::ProductTable;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::super::params::{exchange_symbol_fallback, is_canonical_product_symbol};

const SPOT_PUBLIC_WS_URL: &str = "wss://stream.binance.com:9443/ws";

pub struct BinancePublicWebSocket {
    connection: WebSocketConnection,
    next_request_id: u64,
    product_table: Option<Arc<ProductTable>>,
}

impl BinancePublicWebSocket {
    pub fn new(timeout: Duration) -> Result<Self> {
        Self::with_url(SPOT_PUBLIC_WS_URL.to_string(), timeout)
    }

    pub fn with_url(url: impl Into<String>, timeout: Duration) -> Result<Self> {
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            next_request_id: 1,
            product_table: None,
        })
    }

    pub fn with_product_table(mut self, product_table: ProductTable) -> Self {
        self.product_table = Some(Arc::new(product_table));
        self
    }

    pub fn set_product_table(&mut self, product_table: ProductTable) {
        self.product_table = Some(Arc::new(product_table));
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

    pub async fn subscribe(&mut self, streams: Vec<String>) -> Result<u64> {
        self.send_subscription("SUBSCRIBE", streams).await
    }

    pub async fn unsubscribe(&mut self, streams: Vec<String>) -> Result<u64> {
        self.send_subscription("UNSUBSCRIBE", streams).await
    }

    pub async fn subscribe_trades(&mut self, product_symbol: &str) -> Result<u64> {
        let stream = format!("{}@trade", self.stream_symbol(product_symbol)?);
        self.subscribe(vec![stream]).await
    }

    pub async fn subscribe_agg_trades(&mut self, product_symbol: &str) -> Result<u64> {
        let stream = format!("{}@aggTrade", self.stream_symbol(product_symbol)?);
        self.subscribe(vec![stream]).await
    }

    pub async fn subscribe_orderbook(&mut self, product_symbol: &str) -> Result<u64> {
        let stream = format!("{}@depth", self.stream_symbol(product_symbol)?);
        self.subscribe(vec![stream]).await
    }

    pub async fn subscribe_ticker(&mut self, product_symbol: &str) -> Result<u64> {
        let stream = format!("{}@ticker", self.stream_symbol(product_symbol)?);
        self.subscribe(vec![stream]).await
    }

    pub async fn subscribe_klines(&mut self, product_symbol: &str, interval: &str) -> Result<u64> {
        validate_interval(interval)?;
        let stream = format!("{}@kline_{interval}", self.stream_symbol(product_symbol)?);
        self.subscribe(vec![stream]).await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }

    fn stream_symbol(&self, product_symbol: &str) -> Result<String> {
        let symbol = if let Some(table) = &self.product_table {
            if is_canonical_product_symbol(product_symbol) {
                table.get_exchange_symbol("binance", product_symbol)?
            } else {
                product_symbol.to_string()
            }
        } else {
            exchange_symbol_fallback(product_symbol)
        };
        normalize_stream_symbol(&symbol)
    }

    async fn send_subscription(&mut self, method: &str, streams: Vec<String>) -> Result<u64> {
        if streams.is_empty() {
            return Err(DcexError::InvalidInput(
                "at least one stream is required.".to_string(),
            ));
        }
        let id = self.next_id();
        let payload = subscription_payload(method, streams, id)?;
        self.connection.send_json(&payload).await?;
        Ok(id)
    }

    fn next_id(&mut self) -> u64 {
        let id = self.next_request_id;
        self.next_request_id = self.next_request_id.saturating_add(1).max(1);
        id
    }
}

fn subscription_payload(method: &str, streams: Vec<String>, id: u64) -> Result<Value> {
    let method = match method {
        "SUBSCRIBE" | "UNSUBSCRIBE" => method,
        _ => {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Binance WebSocket method: {method}"
            )));
        }
    };
    let normalized_streams = streams
        .into_iter()
        .map(|stream| {
            let stream = stream.trim();
            if stream.is_empty() {
                return Err(DcexError::InvalidInput(
                    "WebSocket stream name must not be empty.".to_string(),
                ));
            }
            Ok(stream.to_string())
        })
        .collect::<Result<Vec<_>>>()?;
    Ok(json!({
        "method": method,
        "params": normalized_streams,
        "id": id,
    }))
}

fn normalize_stream_symbol(symbol: &str) -> Result<String> {
    let symbol = symbol.trim();
    if symbol.is_empty() {
        return Err(DcexError::InvalidInput(
            "product symbol must not be empty.".to_string(),
        ));
    }
    if !symbol
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || character == '_')
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Binance stream symbol: {symbol}"
        )));
    }
    Ok(symbol.to_ascii_lowercase())
}

fn validate_interval(interval: &str) -> Result<()> {
    let supported = matches!(
        interval,
        "1s" | "1m"
            | "3m"
            | "5m"
            | "15m"
            | "30m"
            | "1h"
            | "2h"
            | "4h"
            | "6h"
            | "8h"
            | "12h"
            | "1d"
            | "3d"
            | "1w"
            | "1M"
    );
    if supported {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(format!(
            "unsupported Binance kline interval: {interval}"
        )))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn normalizes_spot_product_symbol_to_stream_symbol() {
        let client = BinancePublicWebSocket::new(Duration::from_secs(1)).expect("client");
        assert_eq!(
            client.stream_symbol("BTC-USDT-SPOT").expect("symbol"),
            "btcusdt"
        );
        assert_eq!(client.stream_symbol("ETHUSDT").expect("symbol"), "ethusdt");
    }

    #[test]
    fn builds_subscription_payload() {
        let payload = subscription_payload("SUBSCRIBE", vec!["btcusdt@aggTrade".to_string()], 7)
            .expect("json");
        assert_eq!(payload["method"], "SUBSCRIBE");
        assert_eq!(payload["params"][0], "btcusdt@aggTrade");
        assert_eq!(payload["id"], 7);
    }

    #[test]
    fn rejects_invalid_stream_symbol() {
        let client = BinancePublicWebSocket::new(Duration::from_secs(1)).expect("client");
        assert!(client.stream_symbol("BTC/USDT").is_err());
    }
}
