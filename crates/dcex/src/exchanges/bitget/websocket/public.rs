use std::sync::Arc;
use std::time::Duration;

use serde_json::{json, Value};

use crate::product_table::ProductTable;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::super::params::{exchange_symbol_fallback, is_canonical_product_symbol};

const PUBLIC_WS_URL: &str = "wss://ws.bitget.com/v2/ws/public";

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct BitgetWebSocketArg {
    pub inst_type: String,
    pub channel: String,
    pub inst_id: String,
}

impl BitgetWebSocketArg {
    pub fn new(
        inst_type: impl Into<String>,
        channel: impl Into<String>,
        inst_id: impl Into<String>,
    ) -> Result<Self> {
        let inst_type = normalize_inst_type(&inst_type.into())?;
        let channel = normalize_channel(&channel.into())?;
        if channel == "auction" && inst_type != "SPOT" {
            return Err(DcexError::InvalidInput(
                "Bitget auction channel only supports SPOT.".to_string(),
            ));
        }
        Ok(Self {
            inst_type,
            channel,
            inst_id: normalize_inst_id(&inst_id.into())?,
        })
    }

    fn to_json(&self) -> Value {
        json!({
            "instType": self.inst_type,
            "channel": self.channel,
            "instId": self.inst_id,
        })
    }
}

pub struct BitgetPublicWebSocket {
    connection: WebSocketConnection,
    default_inst_type: String,
    product_table: Option<Arc<ProductTable>>,
}

impl BitgetPublicWebSocket {
    pub fn new(default_inst_type: impl Into<String>, timeout: Duration) -> Result<Self> {
        Self::with_url(default_inst_type, PUBLIC_WS_URL.to_string(), timeout)
    }

    pub fn with_url(
        default_inst_type: impl Into<String>,
        url: impl Into<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            default_inst_type: normalize_inst_type(&default_inst_type.into())?,
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

    pub fn default_inst_type(&self) -> &str {
        &self.default_inst_type
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

    pub async fn subscribe(&mut self, args: Vec<BitgetWebSocketArg>) -> Result<()> {
        self.send_subscription("subscribe", args).await
    }

    pub async fn unsubscribe(&mut self, args: Vec<BitgetWebSocketArg>) -> Result<()> {
        self.send_subscription("unsubscribe", args).await
    }

    pub async fn ping(&mut self) -> Result<()> {
        self.connection.send_text("ping").await
    }

    pub async fn subscribe_channel(&mut self, channel: &str, product_symbol: &str) -> Result<()> {
        let (inst_type, inst_id) = self.instrument(product_symbol)?;
        self.subscribe(vec![BitgetWebSocketArg::new(inst_type, channel, inst_id)?])
            .await
    }

    pub async fn unsubscribe_channel(&mut self, channel: &str, product_symbol: &str) -> Result<()> {
        let (inst_type, inst_id) = self.instrument(product_symbol)?;
        self.unsubscribe(vec![BitgetWebSocketArg::new(inst_type, channel, inst_id)?])
            .await
    }

    pub async fn subscribe_ticker(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_channel("ticker", product_symbol).await
    }

    pub async fn subscribe_trades(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_channel("trade", product_symbol).await
    }

    pub async fn subscribe_orderbook(&mut self, product_symbol: &str, depth: u32) -> Result<()> {
        let channel = orderbook_channel(depth)?;
        self.subscribe_channel(channel, product_symbol).await
    }

    pub async fn subscribe_klines(&mut self, product_symbol: &str, interval: &str) -> Result<()> {
        let channel = format!("candle{}", normalize_interval(interval)?);
        self.subscribe_channel(&channel, product_symbol).await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }

    fn instrument(&self, product_symbol: &str) -> Result<(String, String)> {
        let inst_id = if let Some(table) = &self.product_table {
            if is_canonical_product_symbol(product_symbol) {
                table.get_exchange_symbol("bitget", product_symbol)?
            } else {
                product_symbol.to_string()
            }
        } else {
            exchange_symbol_fallback(product_symbol)
        };
        Ok((
            self.inst_type_for(product_symbol)?,
            normalize_inst_id(&inst_id)?,
        ))
    }

    fn inst_type_for(&self, product_symbol: &str) -> Result<String> {
        if let Some(table) = &self.product_table {
            if is_canonical_product_symbol(product_symbol) {
                let exchange_type =
                    table.get_exchange_type("bitget", Some(product_symbol), None)?;
                return normalize_inst_type(&exchange_type);
            }
        }
        if product_symbol.ends_with("-SPOT") {
            return Ok("SPOT".to_string());
        }
        if product_symbol.contains("-USDC-") {
            return Ok("USDC-FUTURES".to_string());
        }
        if product_symbol.contains("-USD-") {
            return Ok("COIN-FUTURES".to_string());
        }
        Ok(self.default_inst_type.clone())
    }

    async fn send_subscription(&mut self, op: &str, args: Vec<BitgetWebSocketArg>) -> Result<()> {
        if args.is_empty() {
            return Err(DcexError::InvalidInput(
                "at least one Bitget WebSocket channel is required.".to_string(),
            ));
        }
        let op = match op {
            "subscribe" | "unsubscribe" => op,
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Bitget WebSocket operation: {op}"
                )));
            }
        };
        let payload = json!({
            "op": op,
            "args": args.iter().map(BitgetWebSocketArg::to_json).collect::<Vec<_>>(),
        });
        self.connection.send_json(&payload).await
    }
}

fn normalize_inst_type(inst_type: &str) -> Result<String> {
    let inst_type = inst_type.trim().to_ascii_uppercase();
    match inst_type.as_str() {
        "SPOT" | "USDT-FUTURES" | "COIN-FUTURES" | "USDC-FUTURES" => Ok(inst_type),
        "MIX" | "SWAP" | "FUTURES" => Ok("USDT-FUTURES".to_string()),
        _ => Err(DcexError::InvalidInput(format!(
            "unsupported Bitget WebSocket instrument type: {inst_type}"
        ))),
    }
}

fn normalize_channel(channel: &str) -> Result<String> {
    let channel = channel.trim();
    match channel {
        "ticker" | "trade" | "books" | "books1" | "books5" | "books15" | "auction" => {
            Ok(channel.to_string())
        }
        _ if channel
            .strip_prefix("candle")
            .is_some_and(|interval| normalize_interval(interval).is_ok()) =>
        {
            Ok(channel.to_string())
        }
        _ => Err(DcexError::InvalidInput(format!(
            "unsupported Bitget WebSocket channel: {channel}"
        ))),
    }
}

fn normalize_inst_id(inst_id: &str) -> Result<String> {
    let inst_id = inst_id.trim();
    if inst_id.is_empty() {
        return Err(DcexError::InvalidInput(
            "Bitget instrument ID must not be empty.".to_string(),
        ));
    }
    if !inst_id
        .chars()
        .all(|character| character.is_ascii_alphanumeric())
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Bitget instrument ID: {inst_id}"
        )));
    }
    Ok(inst_id.to_ascii_uppercase())
}

fn orderbook_channel(depth: u32) -> Result<&'static str> {
    match depth {
        0 => Err(DcexError::InvalidInput(
            "Bitget orderbook depth must be greater than zero.".to_string(),
        )),
        1 => Ok("books1"),
        5 => Ok("books5"),
        15 => Ok("books15"),
        _ => Ok("books"),
    }
}

fn normalize_interval(interval: &str) -> Result<String> {
    let interval = interval.trim();
    match interval {
        "1m" | "5m" | "15m" | "30m" | "1H" | "4H" | "6H" | "12H" | "1D" | "3D" | "1W" | "1M"
        | "6Hutc" | "12Hutc" | "1Dutc" | "3Dutc" | "1Wutc" | "1Mutc" => Ok(interval.to_string()),
        _ => Err(DcexError::InvalidInput(format!(
            "unsupported Bitget kline interval: {interval}"
        ))),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn normalizes_instrument_type_aliases() {
        assert_eq!(
            normalize_inst_type("usdt-futures").expect("inst_type"),
            "USDT-FUTURES"
        );
        assert_eq!(normalize_inst_type("swap").expect("alias"), "USDT-FUTURES");
        assert!(normalize_inst_type("bad").is_err());
    }

    #[test]
    fn builds_channel_arg() {
        let arg = BitgetWebSocketArg::new("spot", "trade", "btcusdt").expect("arg");
        assert_eq!(arg.inst_type, "SPOT");
        assert_eq!(arg.channel, "trade");
        assert_eq!(arg.inst_id, "BTCUSDT");
        assert_eq!(arg.to_json()["instType"], "SPOT");
        assert!(BitgetWebSocketArg::new("spot", "bad", "btcusdt").is_err());
        assert!(BitgetWebSocketArg::new("USDT-FUTURES", "auction", "btcusdt").is_err());
    }

    #[test]
    fn infers_inst_type_from_product_symbol() {
        let client =
            BitgetPublicWebSocket::new("USDT-FUTURES", Duration::from_secs(1)).expect("client");
        assert_eq!(client.instrument("BTC-USDT-SPOT").expect("spot").0, "SPOT");
        assert_eq!(
            client.instrument("BTC-USD-SWAP").expect("coin futures").0,
            "COIN-FUTURES"
        );
    }

    #[test]
    fn maps_orderbook_depth_to_channel() {
        assert_eq!(orderbook_channel(1).expect("books1"), "books1");
        assert_eq!(orderbook_channel(5).expect("books5"), "books5");
        assert_eq!(orderbook_channel(15).expect("books15"), "books15");
        assert_eq!(orderbook_channel(100).expect("books"), "books");
        assert!(orderbook_channel(0).is_err());
    }
}
