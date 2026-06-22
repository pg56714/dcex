use std::time::Duration;

use serde_json::{json, Value};

use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::{decode_event, decode_event_bytes, normalize_symbol, normalize_topic};

const PUBLIC_WS_URL: &str = "wss://ws-manager-compress.bitmart.com/api?protocol=1.1";

pub struct BitmartPublicWebSocket {
    connection: WebSocketConnection,
}

impl BitmartPublicWebSocket {
    pub fn new(timeout: Duration) -> Result<Self> {
        Self::with_url(PUBLIC_WS_URL.to_string(), timeout)
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
        self.connection.send_text("ping").await
    }

    pub async fn subscribe(&mut self, topics: Vec<String>) -> Result<()> {
        self.send_operation("subscribe", topics).await
    }

    pub async fn unsubscribe(&mut self, topics: Vec<String>) -> Result<()> {
        self.send_operation("unsubscribe", topics).await
    }

    pub async fn request_depth_snapshot(&mut self, product_symbol: &str) -> Result<()> {
        let symbol = normalize_symbol(product_symbol)?;
        self.send_operation("request", vec![format!("spot/depth/increase100:{symbol}")])
            .await
    }

    pub async fn subscribe_ticker(&mut self, product_symbol: &str) -> Result<()> {
        let symbol = normalize_symbol(product_symbol)?;
        self.subscribe(vec![format!("spot/ticker:{symbol}")]).await
    }

    pub async fn subscribe_book_ticker(&mut self, product_symbol: &str) -> Result<()> {
        let symbol = normalize_symbol(product_symbol)?;
        self.subscribe(vec![format!("spot/bookTicker:{symbol}")])
            .await
    }

    pub async fn subscribe_klines(&mut self, product_symbol: &str, interval: &str) -> Result<()> {
        let symbol = normalize_symbol(product_symbol)?;
        let interval = normalize_interval(interval)?;
        self.subscribe(vec![format!("spot/kline{interval}:{symbol}")])
            .await
    }

    pub async fn subscribe_orderbook(&mut self, product_symbol: &str, depth: u32) -> Result<()> {
        let symbol = normalize_symbol(product_symbol)?;
        let channel = orderbook_channel(depth)?;
        self.subscribe(vec![format!("{channel}:{symbol}")]).await
    }

    pub async fn subscribe_depth_increase(&mut self, product_symbol: &str) -> Result<()> {
        let symbol = normalize_symbol(product_symbol)?;
        self.subscribe(vec![format!("spot/depth/increase100:{symbol}")])
            .await
    }

    pub async fn subscribe_trades(&mut self, product_symbol: &str) -> Result<()> {
        let symbol = normalize_symbol(product_symbol)?;
        self.subscribe(vec![format!("spot/trade:{symbol}")]).await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        let payload = self.connection.recv_bytes().await?;
        decode_event(payload)
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        let payload = self.connection.recv_bytes().await?;
        decode_event_bytes(payload)
    }

    async fn send_operation(&mut self, op: &str, topics: Vec<String>) -> Result<()> {
        if topics.is_empty() {
            return Err(DcexError::InvalidInput(
                "at least one BitMart WebSocket topic is required.".to_string(),
            ));
        }
        let op = match op {
            "subscribe" | "unsubscribe" | "request" => op,
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported BitMart WebSocket operation: {op}"
                )));
            }
        };
        let topics = topics
            .into_iter()
            .map(|topic| normalize_topic(&topic, "topic"))
            .collect::<Result<Vec<_>>>()?;
        let payload = json!({
            "op": op,
            "args": topics,
        });
        self.connection.send_json(&payload).await
    }
}

fn orderbook_channel(depth: u32) -> Result<&'static str> {
    match depth {
        5 => Ok("spot/depth5"),
        20 => Ok("spot/depth20"),
        50 => Ok("spot/depth50"),
        _ => Err(DcexError::InvalidInput(format!(
            "unsupported BitMart orderbook depth: {depth}"
        ))),
    }
}

fn normalize_interval(interval: &str) -> Result<&'static str> {
    match interval.trim() {
        "1m" => Ok("1m"),
        "5m" => Ok("5m"),
        "15m" => Ok("15m"),
        "30m" => Ok("30m"),
        "1h" | "1H" => Ok("1H"),
        "2h" | "2H" => Ok("2H"),
        "4h" | "4H" => Ok("4H"),
        "1d" | "1D" => Ok("1D"),
        "1w" | "1W" => Ok("1W"),
        "1M" => Ok("1M"),
        value => Err(DcexError::InvalidInput(format!(
            "unsupported BitMart kline interval: {value}"
        ))),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn maps_intervals_and_orderbook_depth() {
        assert_eq!(normalize_interval("1h").expect("interval"), "1H");
        assert_eq!(normalize_interval("1M").expect("interval"), "1M");
        assert!(normalize_interval("3m").is_err());
        assert_eq!(orderbook_channel(20).expect("depth"), "spot/depth20");
        assert!(orderbook_channel(100).is_err());
    }
}
