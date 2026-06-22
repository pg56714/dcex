use std::sync::Arc;
use std::time::Duration;

use serde_json::{json, Value};

use crate::product_table::ProductTable;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::super::params::{
    bybit_timeframe, exchange_symbol_fallback, is_canonical_product_symbol,
};

const PUBLIC_SPOT_WS_URL: &str = "wss://stream.bybit.com/v5/public/spot";
const PUBLIC_LINEAR_WS_URL: &str = "wss://stream.bybit.com/v5/public/linear";
const PUBLIC_INVERSE_WS_URL: &str = "wss://stream.bybit.com/v5/public/inverse";
const PUBLIC_OPTION_WS_URL: &str = "wss://stream.bybit.com/v5/public/option";

pub struct BybitPublicWebSocket {
    connection: WebSocketConnection,
    category: String,
    next_request_id: u64,
    product_table: Option<Arc<ProductTable>>,
}

impl BybitPublicWebSocket {
    pub fn new(category: impl Into<String>, timeout: Duration) -> Result<Self> {
        let category = normalize_category(&category.into())?;
        Self::with_url(
            category.clone(),
            category_url(&category).to_string(),
            timeout,
        )
    }

    pub fn with_url(
        category: impl Into<String>,
        url: impl Into<String>,
        timeout: Duration,
    ) -> Result<Self> {
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            category: normalize_category(&category.into())?,
            next_request_id: 1,
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

    pub fn category(&self) -> &str {
        &self.category
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

    pub async fn subscribe(&mut self, topics: Vec<String>) -> Result<String> {
        self.send_topics("subscribe", topics).await
    }

    pub async fn unsubscribe(&mut self, topics: Vec<String>) -> Result<String> {
        self.send_topics("unsubscribe", topics).await
    }

    pub async fn ping(&mut self) -> Result<String> {
        let request_id = self.next_request_id();
        let payload = json!({
            "req_id": request_id,
            "op": "ping",
        });
        self.connection.send_json(&payload).await?;
        Ok(request_id)
    }

    pub async fn subscribe_trades(&mut self, product_symbol: &str) -> Result<String> {
        let topic = format!("publicTrade.{}", self.exchange_symbol(product_symbol)?);
        self.subscribe(vec![topic]).await
    }

    pub async fn subscribe_ticker(&mut self, product_symbol: &str) -> Result<String> {
        let topic = format!("tickers.{}", self.exchange_symbol(product_symbol)?);
        self.subscribe(vec![topic]).await
    }

    pub async fn subscribe_orderbook(
        &mut self,
        product_symbol: &str,
        depth: u32,
    ) -> Result<String> {
        validate_orderbook_depth(depth)?;
        let topic = format!(
            "orderbook.{depth}.{}",
            self.exchange_symbol(product_symbol)?
        );
        self.subscribe(vec![topic]).await
    }

    pub async fn subscribe_klines(
        &mut self,
        product_symbol: &str,
        interval: &str,
    ) -> Result<String> {
        let topic = format!(
            "kline.{}.{}",
            bybit_timeframe(interval)?,
            self.exchange_symbol(product_symbol)?
        );
        self.subscribe(vec![topic]).await
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
                return table.get_exchange_symbol("bybit", product_symbol);
            }
        }
        normalize_symbol(&exchange_symbol_fallback(product_symbol))
    }

    async fn send_topics(&mut self, op: &str, topics: Vec<String>) -> Result<String> {
        if topics.is_empty() {
            return Err(DcexError::InvalidInput(
                "at least one Bybit WebSocket topic is required.".to_string(),
            ));
        }
        let op = match op {
            "subscribe" | "unsubscribe" => op,
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Bybit WebSocket operation: {op}"
                )));
            }
        };
        let topics = topics
            .into_iter()
            .map(|topic| normalize_topic(&topic))
            .collect::<Result<Vec<_>>>()?;
        let request_id = self.next_request_id();
        let payload = json!({
            "req_id": request_id,
            "op": op,
            "args": topics,
        });
        self.connection.send_json(&payload).await?;
        Ok(request_id)
    }

    fn next_request_id(&mut self) -> String {
        let id = self.next_request_id;
        self.next_request_id = self.next_request_id.saturating_add(1).max(1);
        id.to_string()
    }
}

fn category_url(category: &str) -> &'static str {
    match category {
        "spot" => PUBLIC_SPOT_WS_URL,
        "linear" => PUBLIC_LINEAR_WS_URL,
        "inverse" => PUBLIC_INVERSE_WS_URL,
        "option" => PUBLIC_OPTION_WS_URL,
        _ => PUBLIC_LINEAR_WS_URL,
    }
}

fn normalize_category(category: &str) -> Result<String> {
    let category = category.trim().to_ascii_lowercase();
    match category.as_str() {
        "spot" | "linear" | "inverse" | "option" => Ok(category),
        _ => Err(DcexError::InvalidInput(format!(
            "unsupported Bybit WebSocket category: {category}"
        ))),
    }
}

fn normalize_symbol(symbol: &str) -> Result<String> {
    let symbol = symbol.trim();
    if symbol.is_empty() {
        return Err(DcexError::InvalidInput(
            "Bybit symbol must not be empty.".to_string(),
        ));
    }
    if !symbol
        .chars()
        .all(|character| character.is_ascii_alphanumeric())
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Bybit symbol: {symbol}"
        )));
    }
    Ok(symbol.to_ascii_uppercase())
}

fn normalize_topic(topic: &str) -> Result<String> {
    let topic = topic.trim();
    if topic.is_empty() {
        return Err(DcexError::InvalidInput(
            "Bybit WebSocket topic must not be empty.".to_string(),
        ));
    }
    if !topic
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || character == '.')
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Bybit WebSocket topic: {topic}"
        )));
    }
    Ok(topic.to_string())
}

fn validate_orderbook_depth(depth: u32) -> Result<()> {
    if depth == 0 {
        return Err(DcexError::InvalidInput(
            "Bybit orderbook depth must be greater than zero.".to_string(),
        ));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn normalizes_category() {
        assert_eq!(normalize_category("LINEAR").expect("category"), "linear");
        assert!(normalize_category("bad").is_err());
    }

    #[test]
    fn normalizes_product_symbol_to_topic_symbol() {
        let client = BybitPublicWebSocket::new("spot", Duration::from_secs(1)).expect("client");
        assert_eq!(
            client.exchange_symbol("BTC-USDT-SPOT").expect("symbol"),
            "BTCUSDT"
        );
    }

    #[test]
    fn rejects_invalid_symbol_and_topic() {
        assert!(normalize_symbol("BTC-USDT").is_err());
        assert!(normalize_topic("publicTrade/BTCUSDT").is_err());
    }
}
