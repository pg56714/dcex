use std::time::Duration;

use serde_json::{json, Value};

use crate::exchange::unix_timestamp_ms;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::{normalize_channel, normalize_event, normalize_symbol, payload_array};

const WS_URL: &str = "wss://api.gateio.ws/ws/v4/";

pub struct GateioPublicWebSocket {
    connection: WebSocketConnection,
}

impl GateioPublicWebSocket {
    pub fn new(timeout: Duration) -> Result<Self> {
        Self::with_url(WS_URL.to_string(), timeout)
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
        let time = unix_timestamp_ms()? / 1_000;
        self.connection
            .send_json(&json!({
                "time": time,
                "channel": "spot.ping",
            }))
            .await
    }

    pub async fn subscribe(&mut self, channel: &str, payload: Vec<String>) -> Result<()> {
        self.send_channel_event(channel, "subscribe", payload).await
    }

    pub async fn unsubscribe(&mut self, channel: &str, payload: Vec<String>) -> Result<()> {
        self.send_channel_event(channel, "unsubscribe", payload)
            .await
    }

    pub async fn subscribe_ticker(&mut self, product_symbol: &str) -> Result<()> {
        let symbol = normalize_symbol(product_symbol)?;
        self.subscribe("spot.tickers", vec![symbol]).await
    }

    pub async fn subscribe_trades(&mut self, product_symbol: &str) -> Result<()> {
        let symbol = normalize_symbol(product_symbol)?;
        self.subscribe("spot.trades", vec![symbol]).await
    }

    pub async fn subscribe_candlesticks(
        &mut self,
        product_symbol: &str,
        interval: &str,
    ) -> Result<()> {
        let symbol = normalize_symbol(product_symbol)?;
        let interval = normalize_candlestick_interval(interval)?;
        self.subscribe("spot.candlesticks", vec![interval.to_string(), symbol])
            .await
    }

    pub async fn subscribe_book_ticker(&mut self, product_symbol: &str) -> Result<()> {
        let symbol = normalize_symbol(product_symbol)?;
        self.subscribe("spot.book_ticker", vec![symbol]).await
    }

    pub async fn subscribe_orderbook(&mut self, product_symbol: &str, speed: &str) -> Result<()> {
        let symbol = normalize_symbol(product_symbol)?;
        let speed = normalize_orderbook_speed(speed)?;
        self.subscribe("spot.order_book_update", vec![symbol, speed.to_string()])
            .await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }

    async fn send_channel_event(
        &mut self,
        channel: &str,
        event: &str,
        payload: Vec<String>,
    ) -> Result<()> {
        let payload = payload_array(payload)?;
        self.send_request(channel, event, payload).await
    }

    async fn send_request(&mut self, channel: &str, event: &str, payload: Value) -> Result<()> {
        let channel = normalize_channel(channel)?;
        let event = normalize_event(event)?;
        let time = unix_timestamp_ms()? / 1_000;
        self.connection
            .send_json(&json!({
                "time": time,
                "channel": channel,
                "event": event,
                "payload": payload,
            }))
            .await
    }
}

fn normalize_candlestick_interval(interval: &str) -> Result<&'static str> {
    match interval.trim() {
        "10s" => Ok("10s"),
        "1m" => Ok("1m"),
        "5m" => Ok("5m"),
        "15m" => Ok("15m"),
        "30m" => Ok("30m"),
        "1h" => Ok("1h"),
        "4h" => Ok("4h"),
        "8h" => Ok("8h"),
        "1d" => Ok("1d"),
        "7d" => Ok("7d"),
        value => Err(DcexError::InvalidInput(format!(
            "unsupported Gate.io candlestick interval: {value}"
        ))),
    }
}

fn normalize_orderbook_speed(speed: &str) -> Result<&'static str> {
    match speed.trim() {
        "100ms" => Ok("100ms"),
        value => Err(DcexError::InvalidInput(format!(
            "unsupported Gate.io orderbook update speed: {value}"
        ))),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn validates_public_helpers() {
        assert_eq!(
            normalize_candlestick_interval("1m").expect("interval"),
            "1m"
        );
        assert!(normalize_candlestick_interval("2m").is_err());
        assert_eq!(normalize_orderbook_speed("100ms").expect("speed"), "100ms");
        assert!(normalize_orderbook_speed("1000ms").is_err());
    }
}
