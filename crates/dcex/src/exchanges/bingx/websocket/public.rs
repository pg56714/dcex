use std::time::Duration;

use serde_json::{json, Value};

use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::{
    decode_event, decode_event_bytes, is_application_ping, is_application_ping_text,
    normalize_data_type,
};

const SPOT_WS_URL: &str = "wss://open-api-ws.bingx.com/market";
const SWAP_WS_URL: &str = "wss://open-api-swap.bingx.com/swap-market";

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
enum BingxPublicMarket {
    Spot,
    Swap,
}

pub struct BingxPublicWebSocket {
    connection: WebSocketConnection,
    next_request_id: u64,
    market: BingxPublicMarket,
}

impl BingxPublicWebSocket {
    pub fn new(timeout: Duration) -> Result<Self> {
        Self::with_url(SPOT_WS_URL.to_string(), timeout)
    }

    pub fn new_swap(timeout: Duration) -> Result<Self> {
        Self::with_url(SWAP_WS_URL.to_string(), timeout)
    }

    pub fn with_url(url: impl Into<String>, timeout: Duration) -> Result<Self> {
        let url = url.into();
        let market = market_for_url(&url);
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            next_request_id: 1,
            market,
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
        let symbol = self.symbol_for_connection(product_symbol)?;
        self.subscribe(&format!("{symbol}@ticker")).await
    }

    pub async fn subscribe_trades(&mut self, product_symbol: &str) -> Result<String> {
        let symbol = self.symbol_for_connection(product_symbol)?;
        self.subscribe(&format!("{symbol}@trade")).await
    }

    pub async fn subscribe_orderbook(
        &mut self,
        product_symbol: &str,
        depth: u32,
        speed: &str,
    ) -> Result<String> {
        let symbol = self.symbol_for_connection(product_symbol)?;
        let depth = normalize_orderbook_depth(depth)?;
        match self.market {
            BingxPublicMarket::Spot => self.subscribe(&format!("{symbol}@depth{depth}")).await,
            BingxPublicMarket::Swap => {
                let speed = normalize_orderbook_speed(speed)?;
                self.subscribe(&format!("{symbol}@depth{depth}@{speed}"))
                    .await
            }
        }
    }

    pub async fn subscribe_klines(
        &mut self,
        product_symbol: &str,
        interval: &str,
    ) -> Result<String> {
        let symbol = self.symbol_for_connection(product_symbol)?;
        let interval = normalize_interval(interval, self.market)?;
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

    fn symbol_for_connection(&self, product_symbol: &str) -> Result<String> {
        let (symbol, market) = normalize_product_symbol(product_symbol)?;
        if let Some(market) = market {
            if market != self.market {
                return Err(DcexError::InvalidInput(format!(
                    "BingX {market:?} WebSocket symbol requires the matching public WebSocket URL"
                )));
            }
        }
        Ok(symbol)
    }
}

fn normalize_orderbook_depth(depth: u32) -> Result<u32> {
    match depth {
        5 | 10 | 20 | 50 | 100 => Ok(depth),
        _ => Err(DcexError::InvalidInput(format!(
            "unsupported BingX orderbook depth: {depth}"
        ))),
    }
}

fn normalize_orderbook_speed(speed: &str) -> Result<&'static str> {
    match speed.trim() {
        "200ms" => Ok("200ms"),
        "500ms" => Ok("500ms"),
        value => Err(DcexError::InvalidInput(format!(
            "unsupported BingX orderbook speed: {value}"
        ))),
    }
}

fn normalize_interval(interval: &str, market: BingxPublicMarket) -> Result<String> {
    let interval = interval.trim();
    if interval.is_empty() {
        return Err(DcexError::InvalidInput(
            "BingX kline interval must not be empty.".to_string(),
        ));
    }
    let normalized = match (market, interval) {
        (BingxPublicMarket::Spot, "1m") => "1min".to_string(),
        (BingxPublicMarket::Spot, "3m") => "3min".to_string(),
        (BingxPublicMarket::Spot, "5m") => "5min".to_string(),
        (BingxPublicMarket::Spot, "15m") => "15min".to_string(),
        (BingxPublicMarket::Spot, "30m") => "30min".to_string(),
        _ => interval.to_string(),
    };
    if !normalized
        .chars()
        .all(|character| character.is_ascii_alphanumeric())
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported BingX kline interval: {interval}"
        )));
    }
    Ok(normalized)
}

fn normalize_product_symbol(product_symbol: &str) -> Result<(String, Option<BingxPublicMarket>)> {
    let product_symbol = product_symbol.trim();
    if product_symbol.is_empty() {
        return Err(DcexError::InvalidInput(
            "BingX WebSocket symbol must not be empty.".to_string(),
        ));
    }
    if product_symbol.contains('-') {
        let parts = product_symbol.split('-').collect::<Vec<_>>();
        if parts.len() >= 2 && !parts[0].is_empty() && !parts[1].is_empty() {
            let market = match parts.get(2).map(|value| value.to_ascii_uppercase()) {
                Some(kind) if kind == "SPOT" => Some(BingxPublicMarket::Spot),
                Some(kind) if kind == "SWAP" => Some(BingxPublicMarket::Swap),
                _ => None,
            };
            return Ok((
                format!(
                    "{}-{}",
                    parts[0].to_ascii_uppercase(),
                    parts[1].to_ascii_uppercase()
                ),
                market,
            ));
        }
    }
    if !product_symbol
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || character == '-')
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported BingX WebSocket symbol: {product_symbol}"
        )));
    }
    Ok((product_symbol.to_ascii_uppercase(), None))
}

fn market_for_url(url: &str) -> BingxPublicMarket {
    if url.contains("swap-market") {
        BingxPublicMarket::Swap
    } else {
        BingxPublicMarket::Spot
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn maps_public_data_types() {
        assert_eq!(normalize_orderbook_depth(5).expect("depth"), 5);
        assert_eq!(normalize_orderbook_depth(100).expect("depth"), 100);
        assert_eq!(normalize_orderbook_speed("500ms").expect("speed"), "500ms");
        assert_eq!(normalize_orderbook_speed("200ms").expect("speed"), "200ms");
        assert!(normalize_orderbook_speed("100ms").is_err());
        assert_eq!(
            normalize_interval("1m", BingxPublicMarket::Spot).expect("interval"),
            "1min"
        );
        assert_eq!(
            normalize_interval("1m", BingxPublicMarket::Swap).expect("interval"),
            "1m"
        );
        assert!(normalize_interval("1 m", BingxPublicMarket::Spot).is_err());
        assert_eq!(
            normalize_product_symbol("BTC-USDT-SWAP").expect("symbol"),
            ("BTC-USDT".to_string(), Some(BingxPublicMarket::Swap))
        );
    }
}
