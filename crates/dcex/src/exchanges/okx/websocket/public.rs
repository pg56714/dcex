use std::sync::Arc;
use std::time::Duration;

use serde_json::{json, Value};

use crate::product_table::ProductTable;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::super::params::{exchange_symbol_fallback, is_canonical_product_symbol};

const PUBLIC_WS_URL: &str = "wss://ws.okx.com:8443/ws/v5/public";
const BUSINESS_WS_URL: &str = "wss://ws.okx.com:8443/ws/v5/business";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum OkxWebSocketRoute {
    Public,
    Business,
}

impl OkxWebSocketRoute {
    fn url(self) -> &'static str {
        match self {
            Self::Public => PUBLIC_WS_URL,
            Self::Business => BUSINESS_WS_URL,
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct OkxWebSocketArg {
    pub channel: String,
    pub inst_id: Option<String>,
}

impl OkxWebSocketArg {
    pub fn new(channel: impl Into<String>) -> Result<Self> {
        Self::with_inst_id_optional(channel, None)
    }

    pub fn with_inst_id(channel: impl Into<String>, inst_id: impl Into<String>) -> Result<Self> {
        Self::with_inst_id_optional(channel, Some(inst_id.into()))
    }

    fn with_inst_id_optional(channel: impl Into<String>, inst_id: Option<String>) -> Result<Self> {
        let channel = normalize_channel(&channel.into())?;
        let inst_id = inst_id.map(|value| normalize_inst_id(&value)).transpose()?;
        Ok(Self { channel, inst_id })
    }

    fn to_json(&self) -> Value {
        let mut arg = serde_json::Map::new();
        arg.insert("channel".to_string(), Value::String(self.channel.clone()));
        if let Some(inst_id) = &self.inst_id {
            arg.insert("instId".to_string(), Value::String(inst_id.clone()));
        }
        Value::Object(arg)
    }
}

pub struct OkxPublicWebSocket {
    connection: WebSocketConnection,
    product_table: Option<Arc<ProductTable>>,
    timeout: Duration,
    managed_route: Option<OkxWebSocketRoute>,
    subscription_count: usize,
}

impl OkxPublicWebSocket {
    pub fn new(timeout: Duration) -> Result<Self> {
        Self::with_managed_route(OkxWebSocketRoute::Public, timeout)
    }

    pub fn with_url(url: impl Into<String>, timeout: Duration) -> Result<Self> {
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            product_table: None,
            timeout,
            managed_route: None,
            subscription_count: 0,
        })
    }

    fn with_managed_route(route: OkxWebSocketRoute, timeout: Duration) -> Result<Self> {
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(route.url(), timeout)?),
            product_table: None,
            timeout,
            managed_route: Some(route),
            subscription_count: 0,
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

    pub async fn subscribe(&mut self, args: Vec<OkxWebSocketArg>) -> Result<()> {
        self.prepare_subscription_route(&args).await?;
        let subscription_count = args.len();
        self.send_subscription("subscribe", args).await?;
        self.subscription_count = self.subscription_count.saturating_add(subscription_count);
        Ok(())
    }

    pub async fn unsubscribe(&mut self, args: Vec<OkxWebSocketArg>) -> Result<()> {
        self.validate_subscription_route(&args)?;
        let subscription_count = args.len();
        self.send_subscription("unsubscribe", args).await?;
        self.subscription_count = self.subscription_count.saturating_sub(subscription_count);
        Ok(())
    }

    pub async fn subscribe_channel(&mut self, channel: &str) -> Result<()> {
        self.subscribe(vec![OkxWebSocketArg::new(channel)?]).await
    }

    pub async fn subscribe_channel_for_symbol(
        &mut self,
        channel: &str,
        product_symbol: &str,
    ) -> Result<()> {
        let inst_id = self.exchange_symbol(product_symbol)?;
        self.subscribe(vec![OkxWebSocketArg::with_inst_id(channel, inst_id)?])
            .await
    }

    pub async fn unsubscribe_channel(&mut self, channel: &str) -> Result<()> {
        self.unsubscribe(vec![OkxWebSocketArg::new(channel)?]).await
    }

    pub async fn unsubscribe_channel_for_symbol(
        &mut self,
        channel: &str,
        product_symbol: &str,
    ) -> Result<()> {
        let inst_id = self.exchange_symbol(product_symbol)?;
        self.unsubscribe(vec![OkxWebSocketArg::with_inst_id(channel, inst_id)?])
            .await
    }

    pub async fn subscribe_trades(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_channel_for_symbol("trades", product_symbol)
            .await
    }

    pub async fn subscribe_ticker(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_channel_for_symbol("tickers", product_symbol)
            .await
    }

    pub async fn subscribe_orderbook(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_channel_for_symbol("books", product_symbol)
            .await
    }

    pub async fn subscribe_orderbook5(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_channel_for_symbol("books5", product_symbol)
            .await
    }

    pub async fn subscribe_klines(&mut self, product_symbol: &str, interval: &str) -> Result<()> {
        let channel = format!("candle{}", normalize_interval(interval)?);
        self.subscribe_channel_for_symbol(&channel, product_symbol)
            .await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }

    fn exchange_symbol(&self, product_symbol: &str) -> Result<String> {
        if let Some(table) = &self.product_table {
            if is_canonical_product_symbol(product_symbol) {
                return table.get_exchange_symbol("okx", product_symbol);
            }
        }
        Ok(exchange_symbol_fallback(product_symbol))
    }

    async fn send_subscription(&mut self, op: &str, args: Vec<OkxWebSocketArg>) -> Result<()> {
        if args.is_empty() {
            return Err(DcexError::InvalidInput(
                "at least one OKX WebSocket channel is required.".to_string(),
            ));
        }
        let op = match op {
            "subscribe" | "unsubscribe" => op,
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported OKX WebSocket operation: {op}"
                )));
            }
        };
        let payload = json!({
            "op": op,
            "args": args.iter().map(OkxWebSocketArg::to_json).collect::<Vec<_>>(),
        });
        self.connection.send_json(&payload).await
    }

    async fn prepare_subscription_route(&mut self, args: &[OkxWebSocketArg]) -> Result<()> {
        let target_route = subscription_route(args)?;
        let Some(current_route) = self.managed_route else {
            return Ok(());
        };
        if current_route == target_route {
            return Ok(());
        }
        if self.subscription_count > 0 {
            return Err(DcexError::InvalidInput(
                "OKX public and business channels require separate WebSocket connections."
                    .to_string(),
            ));
        }
        let was_connected = self.connection.is_connected();
        if was_connected {
            self.connection.close().await?;
        }
        self.connection =
            WebSocketConnection::new(WebSocketConfig::new(target_route.url(), self.timeout)?);
        self.managed_route = Some(target_route);
        if was_connected {
            self.connection.connect().await?;
        }
        Ok(())
    }

    fn validate_subscription_route(&self, args: &[OkxWebSocketArg]) -> Result<()> {
        if let Some(current_route) = self.managed_route {
            let target_route = subscription_route(args)?;
            if current_route != target_route {
                return Err(DcexError::InvalidInput(
                    "OKX public and business channels require separate WebSocket connections."
                        .to_string(),
                ));
            }
        }
        Ok(())
    }
}

fn subscription_route(args: &[OkxWebSocketArg]) -> Result<OkxWebSocketRoute> {
    let mut route = None;
    for arg in args {
        let candidate = if arg.channel.starts_with("candle") {
            OkxWebSocketRoute::Business
        } else {
            OkxWebSocketRoute::Public
        };
        if let Some(existing) = route {
            if existing != candidate {
                return Err(DcexError::InvalidInput(
                    "OKX public and business channels require separate WebSocket connections."
                        .to_string(),
                ));
            }
        } else {
            route = Some(candidate);
        }
    }
    Ok(route.unwrap_or(OkxWebSocketRoute::Public))
}

fn normalize_channel(channel: &str) -> Result<String> {
    let channel = channel.trim();
    if channel.is_empty() {
        return Err(DcexError::InvalidInput(
            "OKX WebSocket channel must not be empty.".to_string(),
        ));
    }
    if !channel
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || matches!(character, '-' | '_'))
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported OKX WebSocket channel: {channel}"
        )));
    }
    Ok(channel.to_string())
}

fn normalize_inst_id(inst_id: &str) -> Result<String> {
    let inst_id = inst_id.trim();
    if inst_id.is_empty() {
        return Err(DcexError::InvalidInput(
            "OKX instrument ID must not be empty.".to_string(),
        ));
    }
    if !inst_id
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || character == '-')
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported OKX instrument ID: {inst_id}"
        )));
    }
    Ok(inst_id.to_ascii_uppercase())
}

fn normalize_interval(interval: &str) -> Result<String> {
    let interval = interval.trim();
    let supported = matches!(
        interval,
        "1s" | "1m"
            | "3m"
            | "5m"
            | "15m"
            | "30m"
            | "1H"
            | "2H"
            | "4H"
            | "6H"
            | "12H"
            | "1D"
            | "2D"
            | "3D"
            | "5D"
            | "1W"
            | "1M"
            | "3M"
            | "6Hutc"
            | "12Hutc"
            | "1Dutc"
            | "2Dutc"
            | "3Dutc"
            | "5Dutc"
            | "1Wutc"
            | "1Mutc"
            | "3Mutc"
    );
    if !supported {
        return Err(DcexError::InvalidInput(format!(
            "unsupported OKX kline interval: {interval}"
        )));
    }
    Ok(interval.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn normalizes_product_symbol_to_inst_id() {
        let client = OkxPublicWebSocket::new(Duration::from_secs(1)).expect("client");
        assert_eq!(
            client.exchange_symbol("BTC-USDT-SPOT").expect("spot"),
            "BTC-USDT"
        );
        assert_eq!(
            client.exchange_symbol("BTC-USDT-SWAP").expect("swap"),
            "BTC-USDT-SWAP"
        );
    }

    #[test]
    fn builds_channel_arg() {
        let arg = OkxWebSocketArg::with_inst_id("trades", "btc-usdt").expect("arg");
        assert_eq!(arg.channel, "trades");
        assert_eq!(arg.inst_id.as_deref(), Some("BTC-USDT"));
        assert_eq!(arg.to_json()["channel"], "trades");
        assert_eq!(arg.to_json()["instId"], "BTC-USDT");
    }

    #[test]
    fn rejects_invalid_channel_and_inst_id() {
        assert!(OkxWebSocketArg::with_inst_id("bad channel", "BTC-USDT").is_err());
        assert!(OkxWebSocketArg::with_inst_id("trades", "BTC/USDT").is_err());
    }

    #[test]
    fn routes_candles_to_the_business_websocket() {
        let candle = OkxWebSocketArg::new("candle1m").expect("candle");
        let trades = OkxWebSocketArg::new("trades").expect("trades");
        assert_eq!(
            subscription_route(&[candle.clone()]).expect("route"),
            OkxWebSocketRoute::Business
        );
        assert_eq!(
            subscription_route(&[trades.clone()]).expect("route"),
            OkxWebSocketRoute::Public
        );
        assert!(subscription_route(&[candle, trades]).is_err());
    }

    #[test]
    fn accepts_only_official_candle_intervals() {
        assert_eq!(normalize_interval("1m").expect("interval"), "1m");
        assert_eq!(normalize_interval("1H").expect("interval"), "1H");
        assert_eq!(normalize_interval("1Dutc").expect("interval"), "1Dutc");
        assert!(normalize_interval("1h").is_err());
        assert!(normalize_interval("2s").is_err());
    }
}
