use std::time::Duration;

use serde_json::{json, Value};

use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::{normalize_subscription_arg, subscription_arg};

const WS_URL: &str = "wss://ws.bitmex.com/realtime";

pub struct BitmexPublicWebSocket {
    connection: WebSocketConnection,
}

impl BitmexPublicWebSocket {
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
        self.connection.send_ping(Vec::new()).await
    }

    pub async fn subscribe(&mut self, args: Vec<String>) -> Result<()> {
        self.send_operation("subscribe", args).await
    }

    pub async fn unsubscribe(&mut self, args: Vec<String>) -> Result<()> {
        self.send_operation("unsubscribe", args).await
    }

    pub async fn subscribe_table(&mut self, table: &str) -> Result<()> {
        self.subscribe(vec![subscription_arg(table, None)?]).await
    }

    pub async fn subscribe_table_for_symbol(
        &mut self,
        table: &str,
        product_symbol: &str,
    ) -> Result<()> {
        self.subscribe(vec![subscription_arg(table, Some(product_symbol))?])
            .await
    }

    pub async fn unsubscribe_table(&mut self, table: &str) -> Result<()> {
        self.unsubscribe(vec![subscription_arg(table, None)?]).await
    }

    pub async fn unsubscribe_table_for_symbol(
        &mut self,
        table: &str,
        product_symbol: &str,
    ) -> Result<()> {
        self.unsubscribe(vec![subscription_arg(table, Some(product_symbol))?])
            .await
    }

    pub async fn subscribe_instrument(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_table_for_symbol("instrument", product_symbol)
            .await
    }

    pub async fn subscribe_trades(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_table_for_symbol("trade", product_symbol)
            .await
    }

    pub async fn subscribe_quotes(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_table_for_symbol("quote", product_symbol)
            .await
    }

    pub async fn subscribe_orderbook(&mut self, product_symbol: &str, depth: u32) -> Result<()> {
        let table = orderbook_table(depth)?;
        self.subscribe_table_for_symbol(table, product_symbol).await
    }

    pub async fn subscribe_klines(&mut self, product_symbol: &str, bin_size: &str) -> Result<()> {
        let table = trade_bin_table(bin_size)?;
        self.subscribe_table_for_symbol(table, product_symbol).await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }

    async fn send_operation(&mut self, op: &str, args: Vec<String>) -> Result<()> {
        if args.is_empty() {
            return Err(DcexError::InvalidInput(
                "at least one BitMEX WebSocket subscription is required.".to_string(),
            ));
        }
        let op = match op {
            "subscribe" | "unsubscribe" => op,
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported BitMEX WebSocket operation: {op}"
                )));
            }
        };
        let args = args
            .into_iter()
            .map(|arg| normalize_subscription_arg(&arg))
            .collect::<Result<Vec<_>>>()?;
        self.connection
            .send_json(&json!({
                "op": op,
                "args": args,
            }))
            .await
    }
}

fn orderbook_table(depth: u32) -> Result<&'static str> {
    match depth {
        0 => Ok("orderBookL2"),
        10 => Ok("orderBook10"),
        25 => Ok("orderBookL2_25"),
        _ => Err(DcexError::InvalidInput(format!(
            "unsupported BitMEX orderbook depth: {depth}"
        ))),
    }
}

fn trade_bin_table(bin_size: &str) -> Result<&'static str> {
    match bin_size.trim() {
        "1m" => Ok("tradeBin1m"),
        "5m" => Ok("tradeBin5m"),
        "1h" => Ok("tradeBin1h"),
        "1d" => Ok("tradeBin1d"),
        value => Err(DcexError::InvalidInput(format!(
            "unsupported BitMEX trade bin size: {value}"
        ))),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn maps_orderbook_depth_and_trade_bins() {
        assert_eq!(orderbook_table(0).expect("full depth"), "orderBookL2");
        assert_eq!(orderbook_table(10).expect("top 10"), "orderBook10");
        assert_eq!(orderbook_table(25).expect("top 25"), "orderBookL2_25");
        assert_eq!(trade_bin_table("1m").expect("bin"), "tradeBin1m");
        assert!(trade_bin_table("15m").is_err());
    }
}
