use std::time::Duration;

use serde_json::json;

use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

const PUBLIC_WS_URL: &str = "wss://wbs-api.mexc.com/ws";

pub struct MexcPublicWebSocket {
    connection: WebSocketConnection,
}

impl MexcPublicWebSocket {
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
        self.connection.send_json(&json!({"method": "PING"})).await
    }

    pub async fn subscribe(&mut self, channels: Vec<String>) -> Result<()> {
        self.send_subscription("SUBSCRIPTION", channels).await
    }

    pub async fn unsubscribe(&mut self, channels: Vec<String>) -> Result<()> {
        self.send_subscription("UNSUBSCRIPTION", channels).await
    }

    pub async fn subscribe_trades(&mut self, product_symbol: &str) -> Result<()> {
        let symbol = normalize_symbol(product_symbol)?;
        self.subscribe(vec![format!(
            "spot@public.aggre.deals.v3.api.pb@100ms@{symbol}"
        )])
        .await
    }

    pub async fn subscribe_orderbook(&mut self, product_symbol: &str, speed: &str) -> Result<()> {
        let symbol = normalize_symbol(product_symbol)?;
        let speed = normalize_speed(speed)?;
        self.subscribe(vec![format!(
            "spot@public.aggre.depth.v3.api.pb@{speed}@{symbol}"
        )])
        .await
    }

    pub async fn subscribe_partial_orderbook(
        &mut self,
        product_symbol: &str,
        levels: u32,
    ) -> Result<()> {
        let symbol = normalize_symbol(product_symbol)?;
        let levels = normalize_levels(levels)?;
        self.subscribe(vec![format!(
            "spot@public.limit.depth.v3.api.pb@{symbol}@{levels}"
        )])
        .await
    }

    pub async fn subscribe_book_ticker(&mut self, product_symbol: &str) -> Result<()> {
        let symbol = normalize_symbol(product_symbol)?;
        self.subscribe(vec![format!(
            "spot@public.aggre.bookTicker.v3.api.pb@100ms@{symbol}"
        )])
        .await
    }

    pub async fn subscribe_klines(&mut self, product_symbol: &str, interval: &str) -> Result<()> {
        let symbol = normalize_symbol(product_symbol)?;
        let interval = normalize_interval(interval)?;
        self.subscribe(vec![format!(
            "spot@public.kline.v3.api.pb@{symbol}@{interval}"
        )])
        .await
    }

    pub async fn recv(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }

    async fn send_subscription(&mut self, method: &str, channels: Vec<String>) -> Result<()> {
        if channels.is_empty() {
            return Err(DcexError::InvalidInput(
                "at least one MEXC WebSocket channel is required.".to_string(),
            ));
        }
        let method = match method {
            "SUBSCRIPTION" | "UNSUBSCRIPTION" => method,
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported MEXC WebSocket method: {method}"
                )));
            }
        };
        let channels = channels
            .into_iter()
            .map(|channel| normalize_channel(&channel))
            .collect::<Result<Vec<_>>>()?;
        let payload = json!({
            "method": method,
            "params": channels,
        });
        self.connection.send_json(&payload).await
    }
}

fn normalize_channel(channel: &str) -> Result<String> {
    let channel = channel.trim();
    if channel.is_empty() {
        return Err(DcexError::InvalidInput(
            "MEXC WebSocket channel must not be empty.".to_string(),
        ));
    }
    if !channel
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || matches!(character, '@' | '.'))
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported MEXC WebSocket channel: {channel}"
        )));
    }
    Ok(channel.to_string())
}

fn normalize_symbol(product_symbol: &str) -> Result<String> {
    let product_symbol = product_symbol.trim();
    if product_symbol.is_empty() {
        return Err(DcexError::InvalidInput(
            "MEXC WebSocket symbol must not be empty.".to_string(),
        ));
    }
    if product_symbol.contains('-') {
        let mut parts = product_symbol.split('-');
        if let (Some(base), Some(quote), Some(_kind), None) =
            (parts.next(), parts.next(), parts.next(), parts.next())
        {
            return Ok(format!(
                "{}{}",
                base.to_ascii_uppercase(),
                quote.to_ascii_uppercase()
            ));
        }
    }
    if !product_symbol
        .chars()
        .all(|character| character.is_ascii_alphanumeric())
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported MEXC WebSocket symbol: {product_symbol}"
        )));
    }
    Ok(product_symbol.to_ascii_uppercase())
}

fn normalize_speed(speed: &str) -> Result<&'static str> {
    match speed.trim() {
        "100ms" => Ok("100ms"),
        "10ms" => Ok("10ms"),
        speed => Err(DcexError::InvalidInput(format!(
            "unsupported MEXC WebSocket speed: {speed}"
        ))),
    }
}

fn normalize_levels(levels: u32) -> Result<u32> {
    match levels {
        5 | 10 | 20 => Ok(levels),
        _ => Err(DcexError::InvalidInput(format!(
            "unsupported MEXC partial orderbook levels: {levels}"
        ))),
    }
}

fn normalize_interval(interval: &str) -> Result<String> {
    let interval = interval.trim();
    if interval.is_empty() {
        return Err(DcexError::InvalidInput(
            "MEXC kline interval must not be empty.".to_string(),
        ));
    }
    if !interval
        .chars()
        .all(|character| character.is_ascii_alphanumeric())
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported MEXC kline interval: {interval}"
        )));
    }
    Ok(match interval {
        "1m" => "Min1".to_string(),
        "5m" => "Min5".to_string(),
        "15m" => "Min15".to_string(),
        "30m" => "Min30".to_string(),
        "1h" => "Min60".to_string(),
        "4h" => "Hour4".to_string(),
        "8h" => "Hour8".to_string(),
        "1d" => "Day1".to_string(),
        "1w" => "Week1".to_string(),
        "1M" => "Month1".to_string(),
        value => value.to_string(),
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn normalizes_symbol_and_interval() {
        assert_eq!(
            normalize_symbol("BTC-USDT-SPOT").expect("symbol"),
            "BTCUSDT"
        );
        assert_eq!(normalize_symbol("mxusdt").expect("symbol"), "MXUSDT");
        assert_eq!(normalize_interval("1m").expect("interval"), "Min1");
        assert_eq!(normalize_interval("Min15").expect("interval"), "Min15");
    }

    #[test]
    fn validates_speed_and_levels() {
        assert_eq!(normalize_speed("100ms").expect("speed"), "100ms");
        assert!(normalize_speed("1s").is_err());
        assert_eq!(normalize_levels(20).expect("levels"), 20);
        assert!(normalize_levels(50).is_err());
    }
}
