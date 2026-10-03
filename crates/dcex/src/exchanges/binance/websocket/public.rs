use std::collections::HashSet;
use std::sync::Arc;
use std::time::Duration;

use serde_json::{Value, json};

use crate::product_table::ProductTable;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::super::params::{
    exchange_symbol_fallback, is_canonical_product_symbol, is_spot_product_symbol,
};

const SPOT_PUBLIC_WS_URL: &str = "wss://stream.binance.com:9443/ws";

pub struct BinancePublicWebSocket {
    connection: WebSocketConnection,
    next_request_id: u64,
    product_table: Option<Arc<ProductTable>>,
    subscriptions: HashSet<String>,
    profile: String,
}

impl BinancePublicWebSocket {
    pub fn new(timeout: Duration) -> Result<Self> {
        Self::with_url(SPOT_PUBLIC_WS_URL.to_string(), timeout)
    }

    pub fn with_url(url: impl Into<String>, timeout: Duration) -> Result<Self> {
        Self::with_profile_url("spot", Some(url.into()), timeout)
    }

    /// Profiles: spot, futures_public, futures_market, coin_futures,
    /// options_public, options_market, alpha. Split futures/options connections by feed.
    pub fn with_profile(profile: &str, timeout: Duration) -> Result<Self> {
        Self::with_profile_url(profile, None, timeout)
    }

    pub fn with_profile_url(profile: &str, url: Option<String>, timeout: Duration) -> Result<Self> {
        let default_url = match profile {
            "spot" => SPOT_PUBLIC_WS_URL,
            "alpha" => "wss://nbstream.binance.com/w3w/wsa/stream/stream",
            "futures_public" | "options_public" => "wss://fstream.binance.com/public/ws",
            "futures_market" | "options_market" => "wss://fstream.binance.com/market/ws",
            "coin_futures" => "wss://dstream.binance.com/ws",
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Binance public stream profile: {profile}"
                )));
            }
        };
        let url = url.unwrap_or_else(|| default_url.to_string());
        Ok(Self {
            profile: profile.to_string(),
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            next_request_id: 1,
            product_table: None,
            subscriptions: HashSet::new(),
        })
    }

    pub fn url(&self) -> &str {
        &self.connection.config().url
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
        self.connection.connect().await?;
        self.subscriptions.clear();
        Ok(())
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
        if self.product_table.is_none()
            && self.profile == "spot"
            && is_canonical_product_symbol(product_symbol)
            && !is_spot_product_symbol(product_symbol)
        {
            return Err(DcexError::InvalidInput(format!(
                "Binance Spot WebSocket does not support non-Spot product: {product_symbol}"
            )));
        }

        let symbol = if let Some(table) = &self.product_table {
            let market = if self.profile == "spot" {
                super::super::BinanceMarket::Spot
            } else if self.profile == "coin_futures" {
                super::super::BinanceMarket::CoinFutures
            } else if self.profile.starts_with("options_") {
                super::super::BinanceMarket::Options
            } else if self.profile == "equity" {
                super::super::BinanceMarket::Equity
            } else {
                super::super::BinanceMarket::Futures
            };
            table
                .resolve_symbol_in(market.table_exchange(), product_symbol, |row| {
                    market.accepts(row)
                })?
                .exchange_symbol
                .clone()
        } else {
            exchange_symbol_fallback(product_symbol)?
        };
        if self.profile.starts_with("options_") {
            let symbol = symbol.trim();
            if symbol.is_empty()
                || !symbol
                    .chars()
                    .all(|c| c.is_ascii_alphanumeric() || matches!(c, '-' | '_' | '.'))
            {
                return Err(DcexError::InvalidInput(
                    "invalid Binance option stream symbol".into(),
                ));
            }
            return Ok(symbol.to_ascii_lowercase());
        }
        if self.product_table.is_none()
            && self.profile != "spot"
            && is_spot_product_symbol(product_symbol)
        {
            return Err(DcexError::InvalidInput(
                "Spot product requires the spot WebSocket profile".into(),
            ));
        }
        normalize_stream_symbol(&symbol)
    }

    async fn send_subscription(&mut self, method: &str, streams: Vec<String>) -> Result<u64> {
        if streams.is_empty() {
            return Err(DcexError::InvalidInput(
                "at least one stream is required.".to_string(),
            ));
        }
        let streams = normalize_streams(streams)?;
        if self.profile.starts_with("futures_") {
            for stream in &streams {
                let public = stream.contains("@depth")
                    || stream.contains("@rpiDepth")
                    || stream.contains("bookTicker");
                if public != (self.profile == "futures_public") {
                    return Err(DcexError::InvalidInput(format!(
                        "stream {stream} requires the futures_{} profile",
                        if public { "public" } else { "market" }
                    )));
                }
            }
        }
        if method == "SUBSCRIBE" {
            let mut subscriptions = self.subscriptions.clone();
            subscriptions.extend(streams.iter().cloned());
            let limit = if self.profile.starts_with("options_") {
                200
            } else {
                1_024
            };
            if subscriptions.len() > limit {
                return Err(DcexError::InvalidInput(format!(
                    "Binance {} WebSocket supports at most {limit} streams.",
                    self.profile
                )));
            }
        }
        let id = self.next_id();
        let payload = subscription_payload(method, &streams, id)?;
        self.connection.send_json(&payload).await?;
        if method == "SUBSCRIBE" {
            self.subscriptions.extend(streams);
        } else {
            for stream in streams {
                self.subscriptions.remove(&stream);
            }
        }
        Ok(id)
    }

    fn next_id(&mut self) -> u64 {
        let id = self.next_request_id;
        self.next_request_id = self.next_request_id.saturating_add(1).max(1);
        id
    }
}

fn subscription_payload(method: &str, streams: &[String], id: u64) -> Result<Value> {
    let method = match method {
        "SUBSCRIBE" | "UNSUBSCRIBE" => method,
        _ => {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Binance WebSocket method: {method}"
            )));
        }
    };
    Ok(json!({
        "method": method,
        "params": streams,
        "id": id,
    }))
}

fn normalize_streams(streams: Vec<String>) -> Result<Vec<String>> {
    streams
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
        .collect()
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
    fn option_stream_preserves_fractional_strikes_and_resolved_names() {
        let mut client =
            BinancePublicWebSocket::with_profile("options_public", Duration::from_secs(1)).unwrap();
        assert_eq!(
            client.stream_symbol("XRP-261030-2.2-C").unwrap(),
            "xrp-261030-2.2-c"
        );
        client.set_product_table(ProductTable::new(vec![crate::product_table::MarketInfo {
            exchange: "binance".into(),
            product_symbol: "XRP-USDT-261030-2.2-C-OPTION".into(),
            exchange_symbol: "XRP-261030-2.2-C".into(),
            product_type: "option".into(),
            ..Default::default()
        }]));
        assert_eq!(
            client
                .stream_symbol("XRP-USDT-261030-2.2-C-OPTION")
                .unwrap(),
            "xrp-261030-2.2-c"
        );
    }

    #[test]
    fn coin_stream_uses_the_coin_margined_namespace() {
        let client = BinancePublicWebSocket::with_profile("coin_futures", Duration::from_secs(1))
            .unwrap()
            .with_product_table(ProductTable::new(vec![crate::product_table::MarketInfo {
                exchange: "binance_coinm".into(),
                product_symbol: "BTC-USD-SWAP".into(),
                exchange_symbol: "BTCUSD_PERP".into(),
                product_type: "swap".into(),
                ..Default::default()
            }]));
        assert_eq!(client.stream_symbol("BTC-USD-SWAP").unwrap(), "btcusd_perp");
    }

    #[test]
    fn normalizes_spot_product_symbol_to_stream_symbol() {
        let client = BinancePublicWebSocket::new(Duration::from_secs(1)).expect("client");
        assert_eq!(
            client.stream_symbol("BTC-USDT-SPOT").expect("symbol"),
            "btcusdt"
        );
        assert_eq!(client.stream_symbol("ETHUSDT").expect("symbol"), "ethusdt");
        assert!(client.stream_symbol("BTC-USDT-SWAP").is_err());
    }

    #[test]
    fn builds_subscription_payload() {
        let streams = vec!["btcusdt@aggTrade".to_string()];
        let payload = subscription_payload("SUBSCRIBE", &streams, 7).expect("json");
        assert_eq!(payload["method"], "SUBSCRIBE");
        assert_eq!(payload["params"][0], "btcusdt@aggTrade");
        assert_eq!(payload["id"], 7);
    }

    #[test]
    fn rejects_invalid_stream_symbol() {
        let client = BinancePublicWebSocket::new(Duration::from_secs(1)).expect("client");
        assert!(client.stream_symbol("BTC/USDT").is_err());
    }

    #[tokio::test]
    async fn rejects_more_than_1024_streams_before_transport() {
        let mut client = BinancePublicWebSocket::new(Duration::from_secs(1)).expect("client");
        client.subscriptions = (0..1_024).map(|index| format!("stream{index}")).collect();
        assert!(
            client
                .subscribe(vec!["stream1024".to_string()])
                .await
                .is_err()
        );
    }
}
