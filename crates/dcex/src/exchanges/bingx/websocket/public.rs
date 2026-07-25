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
        Self::with_spot_url(SPOT_WS_URL.to_string(), timeout)
    }

    pub fn new_swap(timeout: Duration) -> Result<Self> {
        Self::with_swap_url(SWAP_WS_URL.to_string(), timeout)
    }

    pub fn with_url(url: impl Into<String>, timeout: Duration) -> Result<Self> {
        let url = url.into();
        let market = market_for_url(&url);
        Self::with_url_and_market(url, timeout, market)
    }

    pub fn with_spot_url(url: impl Into<String>, timeout: Duration) -> Result<Self> {
        Self::with_url_and_market(url.into(), timeout, BingxPublicMarket::Spot)
    }

    pub fn with_swap_url(url: impl Into<String>, timeout: Duration) -> Result<Self> {
        Self::with_url_and_market(url.into(), timeout, BingxPublicMarket::Swap)
    }

    fn with_url_and_market(
        url: String,
        timeout: Duration,
        market: BingxPublicMarket,
    ) -> Result<Self> {
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
                if speed == "200ms" && !matches!(symbol.as_str(), "BTC-USDT" | "ETH-USDT") {
                    return Err(DcexError::InvalidInput(
                        "BingX 200ms swap depth is only available for BTC-USDT and ETH-USDT"
                            .to_string(),
                    ));
                }
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
    let supported = match market {
        BingxPublicMarket::Spot => [
            "1min", "3min", "5min", "15min", "30min", "1h", "2h", "4h", "6h", "8h", "12h", "1d",
            "3d", "1w", "1M",
        ]
        .contains(&normalized.as_str()),
        BingxPublicMarket::Swap => [
            "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w",
            "1M",
        ]
        .contains(&normalized.as_str()),
    };
    if !supported {
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
    let parts = product_symbol.split('-').collect::<Vec<_>>();
    let market = match parts.as_slice() {
        [base, quote] if !base.is_empty() && !quote.is_empty() => None,
        [base, quote, kind]
            if !base.is_empty() && !quote.is_empty() && kind.eq_ignore_ascii_case("SPOT") =>
        {
            Some(BingxPublicMarket::Spot)
        }
        [base, quote, kind]
            if !base.is_empty() && !quote.is_empty() && kind.eq_ignore_ascii_case("SWAP") =>
        {
            Some(BingxPublicMarket::Swap)
        }
        _ => {
            return Err(DcexError::InvalidInput(format!(
                "unsupported BingX WebSocket symbol: {product_symbol}"
            )));
        }
    };
    if !parts[0]
        .chars()
        .all(|character| character.is_ascii_alphanumeric())
        || !parts[1]
            .chars()
            .all(|character| character.is_ascii_alphanumeric())
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported BingX WebSocket symbol: {product_symbol}"
        )));
    }
    Ok((
        format!(
            "{}-{}",
            parts[0].to_ascii_uppercase(),
            parts[1].to_ascii_uppercase()
        ),
        market,
    ))
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
    use crate::http::block_on;

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
        assert!(normalize_interval("2m", BingxPublicMarket::Swap).is_err());
        assert!(normalize_product_symbol("BTCUSDT").is_err());
        assert_eq!(
            normalize_product_symbol("BTC-USDT-SWAP").expect("symbol"),
            ("BTC-USDT".to_string(), Some(BingxPublicMarket::Swap))
        );
    }

    #[test]
    fn explicit_swap_market_survives_custom_url() {
        let mut websocket = BingxPublicWebSocket::with_swap_url(
            "wss://proxy.example.test/ws",
            Duration::from_secs(1),
        )
        .expect("client");
        let error = block_on(async move {
            websocket
                .subscribe_orderbook("SOL-USDT-SWAP", 20, "200ms")
                .await
        })
        .expect_err("SOL swap should reject the BTC/ETH-only 200ms speed");
        assert_eq!(
            error.to_string(),
            "BingX 200ms swap depth is only available for BTC-USDT and ETH-USDT"
        );
    }
}
