use std::sync::Arc;
use std::time::Duration;

use serde_json::{json, Value};

use crate::product_table::ProductTable;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::super::params::{exchange_symbol_fallback, is_canonical_product_symbol};

const PUBLIC_WS_URL: &str = "wss://ws.okx.com:8443/ws/v5/public";

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct OkxWebSocketArg {
    pub channel: String,
    pub inst_id: Option<String>,
}

impl OkxWebSocketArg {
    pub fn new(channel: impl Into<String>, inst_id: Option<String>) -> Result<Self> {
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
}

impl OkxPublicWebSocket {
    pub fn new(timeout: Duration) -> Result<Self> {
        Self::with_url(PUBLIC_WS_URL.to_string(), timeout)
    }

    pub fn with_url(url: impl Into<String>, timeout: Duration) -> Result<Self> {
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
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

    pub async fn subscribe(&mut self, args: Vec<OkxWebSocketArg>) -> Result<()> {
        self.send_subscription("subscribe", args).await
    }

    pub async fn unsubscribe(&mut self, args: Vec<OkxWebSocketArg>) -> Result<()> {
        self.send_subscription("unsubscribe", args).await
    }

    pub async fn subscribe_channel(
        &mut self,
        channel: &str,
        product_symbol: Option<&str>,
    ) -> Result<()> {
        let inst_id = product_symbol
            .map(|symbol| self.exchange_symbol(symbol))
            .transpose()?;
        self.subscribe(vec![OkxWebSocketArg::new(channel, inst_id)?])
            .await
    }

    pub async fn unsubscribe_channel(
        &mut self,
        channel: &str,
        product_symbol: Option<&str>,
    ) -> Result<()> {
        let inst_id = product_symbol
            .map(|symbol| self.exchange_symbol(symbol))
            .transpose()?;
        self.unsubscribe(vec![OkxWebSocketArg::new(channel, inst_id)?])
            .await
    }

    pub async fn subscribe_trades(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_channel("trades", Some(product_symbol)).await
    }

    pub async fn subscribe_ticker(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_channel("tickers", Some(product_symbol))
            .await
    }

    pub async fn subscribe_orderbook(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_channel("books", Some(product_symbol)).await
    }

    pub async fn subscribe_orderbook5(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_channel("books5", Some(product_symbol)).await
    }

    pub async fn subscribe_klines(&mut self, product_symbol: &str, interval: &str) -> Result<()> {
        let channel = format!("candle{}", normalize_interval(interval)?);
        self.subscribe_channel(&channel, Some(product_symbol)).await
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
    if interval.is_empty() {
        return Err(DcexError::InvalidInput(
            "OKX kline interval must not be empty.".to_string(),
        ));
    }
    if !interval
        .chars()
        .all(|character| character.is_ascii_alphanumeric())
    {
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
        let arg = OkxWebSocketArg::new("trades", Some("btc-usdt".to_string())).expect("arg");
        assert_eq!(arg.channel, "trades");
        assert_eq!(arg.inst_id.as_deref(), Some("BTC-USDT"));
        assert_eq!(arg.to_json()["channel"], "trades");
        assert_eq!(arg.to_json()["instId"], "BTC-USDT");
    }

    #[test]
    fn rejects_invalid_channel_and_inst_id() {
        assert!(OkxWebSocketArg::new("bad channel", Some("BTC-USDT".to_string())).is_err());
        assert!(OkxWebSocketArg::new("trades", Some("BTC/USDT".to_string())).is_err());
    }
}
