use std::time::Duration;

use serde_json::{json, Value};

use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::{
    decode_event, decode_event_bytes, is_application_ping, is_application_ping_text,
    normalize_data_type, normalize_symbol,
};

const WS_URL: &str = "wss://open-api-ws.bingx.com/market";

pub struct BingxPublicWebSocket {
    connection: WebSocketConnection,
    next_request_id: u64,
}

impl BingxPublicWebSocket {
    pub fn new(timeout: Duration) -> Result<Self> {
        Self::with_url(WS_URL.to_string(), timeout)
    }

    pub fn with_url(url: impl Into<String>, timeout: Duration) -> Result<Self> {
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            next_request_id: 1,
        })
    }

    pub fn is_connected(&self) -> bool {
        self.connection.is_connected()
    }

    pub async fn connect(&mut self) -> Result<()> {
        self.connection
            .connect_with_headers(vec![("Accept-Encoding".to_string(), "gzip".to_string())])
            .await
    }

    pub async fn close(&mut self) -> Result<()> {
        self.connection.close().await
    }

    pub async fn ping(&mut self) -> Result<()> {
        self.connection.send_text("Ping").await
    }

    pub async fn subscribe(&mut self, data_type: &str) -> Result<String> {
        self.send_subscription("sub", data_type).await
    }

    pub async fn unsubscribe(&mut self, data_type: &str) -> Result<String> {
        self.send_subscription("unsub", data_type).await
    }

    pub async fn subscribe_ticker(&mut self, product_symbol: &str) -> Result<String> {
        let symbol = normalize_symbol(product_symbol)?;
        self.subscribe(&format!("{symbol}@ticker")).await
    }

    pub async fn subscribe_trades(&mut self, product_symbol: &str) -> Result<String> {
        let symbol = normalize_symbol(product_symbol)?;
        self.subscribe(&format!("{symbol}@trade")).await
    }

    pub async fn subscribe_orderbook(
        &mut self,
        product_symbol: &str,
        depth: u32,
        speed: &str,
    ) -> Result<String> {
        let symbol = normalize_symbol(product_symbol)?;
        let depth = normalize_orderbook_depth(depth)?;
        let speed = normalize_orderbook_speed(speed)?;
        self.subscribe(&format!("{symbol}@depth{depth}@{speed}"))
            .await
    }

    pub async fn subscribe_klines(
        &mut self,
        product_symbol: &str,
        interval: &str,
    ) -> Result<String> {
        let symbol = normalize_symbol(product_symbol)?;
        let interval = normalize_interval(interval)?;
        self.subscribe(&format!("{symbol}@kline_{interval}")).await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        loop {
            let payload = self.connection.recv_bytes().await?;
            let event = decode_event(payload)?;
            if is_application_ping(&event) {
                self.connection.send_text("Pong").await?;
                continue;
            }
            return Ok(event);
        }
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        loop {
            let payload = self.connection.recv_bytes().await?;
            let body = decode_event_bytes(payload)?;
            if let Ok(text) = std::str::from_utf8(&body) {
                if is_application_ping_text(text) {
                    self.connection.send_text("Pong").await?;
                    continue;
                }
            }
            return Ok(body);
        }
    }

    async fn send_subscription(&mut self, req_type: &str, data_type: &str) -> Result<String> {
        let req_type = match req_type {
            "sub" | "unsub" => req_type,
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported BingX WebSocket reqType: {req_type}"
                )));
            }
        };
        let id = self.next_id();
        let data_type = normalize_data_type(data_type)?;
        self.connection
            .send_json(&json!({
                "id": id,
                "reqType": req_type,
                "dataType": data_type,
            }))
            .await?;
        Ok(id)
    }

    fn next_id(&mut self) -> String {
        let id = self.next_request_id;
        self.next_request_id = self.next_request_id.saturating_add(1).max(1);
        format!("dcex-{id}")
    }
}

fn normalize_orderbook_depth(depth: u32) -> Result<u32> {
    match depth {
        5 => Ok(depth),
        _ => Err(DcexError::InvalidInput(format!(
            "unsupported BingX orderbook depth: {depth}"
        ))),
    }
}

fn normalize_orderbook_speed(speed: &str) -> Result<&'static str> {
    match speed.trim() {
        "500ms" => Ok("500ms"),
        value => Err(DcexError::InvalidInput(format!(
            "unsupported BingX orderbook speed: {value}"
        ))),
    }
}

fn normalize_interval(interval: &str) -> Result<String> {
    let interval = interval.trim();
    if interval.is_empty() {
        return Err(DcexError::InvalidInput(
            "BingX kline interval must not be empty.".to_string(),
        ));
    }
    if !interval
        .chars()
        .all(|character| character.is_ascii_alphanumeric())
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported BingX kline interval: {interval}"
        )));
    }
    Ok(interval.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn maps_public_data_types() {
        assert_eq!(normalize_orderbook_depth(5).expect("depth"), 5);
        assert!(normalize_orderbook_depth(10).is_err());
        assert_eq!(normalize_orderbook_speed("500ms").expect("speed"), "500ms");
        assert!(normalize_orderbook_speed("100ms").is_err());
        assert_eq!(normalize_interval("1m").expect("interval"), "1m");
        assert!(normalize_interval("1 m").is_err());
    }
}
