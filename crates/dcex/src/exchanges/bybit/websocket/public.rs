use std::collections::HashSet;
use std::sync::Arc;
use std::time::Duration;

use serde_json::{Value, json};

use crate::product_table::ProductTable;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::super::params::{bybit_timeframe, exchange_symbol_fallback};

const PUBLIC_SPOT_WS_URL: &str = "wss://stream.bybit.com/v5/public/spot";
const PUBLIC_LINEAR_WS_URL: &str = "wss://stream.bybit.com/v5/public/linear";
const PUBLIC_INVERSE_WS_URL: &str = "wss://stream.bybit.com/v5/public/inverse";
const PUBLIC_OPTION_WS_URL: &str = "wss://stream.bybit.com/v5/public/option";
const PUBLIC_RFQ_WS_URL: &str = "wss://stream.bybit.com/v5/public/rfq";
const PUBLIC_SPREAD_WS_URL: &str = "wss://stream.bybit.com/v5/public/spread";

pub struct BybitPublicWebSocket {
    connection: WebSocketConnection,
    category: String,
    next_request_id: u64,
    product_table: Option<Arc<ProductTable>>,
    subscriptions: HashSet<String>,
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
            subscriptions: HashSet::new(),
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
        self.connection.connect().await?;
        self.subscriptions.clear();
        Ok(())
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
        let topic = format!("publicTrade.{}", self.trade_topic_symbol(product_symbol)?);
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
        validate_orderbook_depth(&self.category, depth)?;
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
        if self.category == "spread" {
            return Err(DcexError::InvalidInput(
                "Bybit spread WebSocket does not provide kline streams.".to_string(),
            ));
        }
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
            return Ok(table
                .resolve_symbol("bybit", product_symbol, None, Some(&self.category))?
                .exchange_symbol
                .clone());
        }
        let canonical = product_symbol.to_ascii_uppercase();
        let canonical_type = canonical.rsplit('-').next().unwrap_or("");
        let type_matches = match canonical_type {
            "SPOT" => self.category == "spot",
            "SWAP" | "FUTURES" => matches!(self.category.as_str(), "linear" | "inverse"),
            "OPTION" | "OPTIONS" => self.category == "option",
            _ => true,
        };
        if !type_matches {
            return Err(DcexError::InvalidInput(
                "Bybit product type does not match WebSocket category".into(),
            ));
        }
        if self.category == "spread" {
            return normalize_spread_symbol(product_symbol);
        }
        if matches!(canonical_type, "SWAP" | "FUTURES") {
            let quote = canonical.split('-').nth(1).unwrap_or("");
            let matches = match self.category.as_str() {
                "linear" => matches!(quote, "USDT" | "USDC"),
                "inverse" => quote == "USD",
                _ => false,
            };
            if !matches {
                return Err(DcexError::InvalidInput(
                    "Bybit settlement currency does not match WebSocket category; load the product table for other currencies".into(),
                ));
            }
        }
        let symbol = exchange_symbol_fallback(&canonical)?;
        if matches!(self.category.as_str(), "option" | "linear") {
            normalize_option_symbol(&symbol)
        } else {
            normalize_symbol(&symbol)
        }
    }

    fn trade_topic_symbol(&self, product_symbol: &str) -> Result<String> {
        let symbol = self.exchange_symbol(product_symbol)?;
        if self.category == "option" {
            normalize_symbol(symbol.split('-').next().unwrap_or(&symbol))
        } else {
            Ok(symbol)
        }
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
            .map(|topic| normalize_topic(&self.category, &topic))
            .collect::<Result<Vec<_>>>()?;
        if json!(&topics).to_string().len() > 21_000 {
            return Err(DcexError::InvalidInput(
                "Bybit WebSocket subscription args must not exceed 21,000 characters.".to_string(),
            ));
        }
        if op == "subscribe" && self.category == "spot" && topics.len() > 10 {
            return Err(DcexError::InvalidInput(
                "Bybit Spot WebSocket subscription requests support at most 10 topics.".to_string(),
            ));
        }
        if op == "subscribe" && self.category == "option" {
            let mut subscriptions = self.subscriptions.clone();
            subscriptions.extend(topics.iter().cloned());
            if subscriptions.len() > 2_000 {
                return Err(DcexError::InvalidInput(
                    "Bybit Options WebSocket connections support at most 2000 topics.".to_string(),
                ));
            }
        }
        let request_id = self.next_request_id();
        let payload = json!({
            "req_id": request_id,
            "op": op,
            "args": &topics,
        });
        self.connection.send_json(&payload).await?;
        if op == "subscribe" {
            self.subscriptions.extend(topics);
        } else {
            for topic in topics {
                self.subscriptions.remove(&topic);
            }
        }
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
        "rfq" => PUBLIC_RFQ_WS_URL,
        "spread" => PUBLIC_SPREAD_WS_URL,
        _ => PUBLIC_LINEAR_WS_URL,
    }
}

fn normalize_category(category: &str) -> Result<String> {
    let category = category.trim().to_ascii_lowercase();
    match category.as_str() {
        "spot" | "linear" | "inverse" | "option" | "rfq" | "spread" => Ok(category),
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

fn normalize_option_symbol(symbol: &str) -> Result<String> {
    let symbol = symbol.trim();
    if symbol.is_empty()
        || !symbol
            .chars()
            .all(|character| character.is_ascii_alphanumeric() || matches!(character, '-' | '.'))
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Bybit option symbol: {symbol}"
        )));
    }
    Ok(symbol.to_ascii_uppercase())
}

/// Spread symbols combine two legs, e.g. `SOLUSDT_SOL/USDT`.
fn is_spread_symbol_char(character: char) -> bool {
    character.is_ascii_alphanumeric() || matches!(character, '-' | '_' | '/')
}

fn normalize_spread_symbol(symbol: &str) -> Result<String> {
    let symbol = symbol.trim();
    if symbol.is_empty() || !symbol.chars().all(is_spread_symbol_char) {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Bybit spread symbol: {symbol}"
        )));
    }
    Ok(symbol.to_ascii_uppercase())
}

fn normalize_topic(category: &str, topic: &str) -> Result<String> {
    let topic = topic.trim();
    if topic.is_empty() {
        return Err(DcexError::InvalidInput(
            "Bybit WebSocket topic must not be empty.".to_string(),
        ));
    }
    let is_spread = category == "spread";
    if !topic.chars().all(|character| {
        character.is_ascii_alphanumeric()
            || matches!(character, '.' | '-')
            || (is_spread && is_spread_symbol_char(character))
    }) {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Bybit WebSocket topic: {topic}"
        )));
    }
    Ok(topic.to_string())
}

fn validate_orderbook_depth(category: &str, depth: u32) -> Result<()> {
    let is_supported = match category {
        "spot" | "linear" | "inverse" => matches!(depth, 1 | 50 | 200 | 1_000),
        "option" => matches!(depth, 25 | 100),
        "spread" => depth == 25,
        _ => false,
    };
    if is_supported {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(format!(
            "unsupported Bybit orderbook depth {depth} for {category} WebSocket category."
        )))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn option_symbols_preserve_fractional_strikes() {
        assert_eq!(
            normalize_option_symbol("SOXL-30OCT26-207.5-P-USDT").unwrap(),
            "SOXL-30OCT26-207.5-P-USDT"
        );
    }

    #[test]
    fn normalizes_category() {
        assert_eq!(normalize_category("LINEAR").expect("category"), "linear");
        assert_eq!(normalize_category("RFQ").expect("rfq"), "rfq");
        assert_eq!(category_url("rfq"), PUBLIC_RFQ_WS_URL);
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
        assert!(normalize_topic("linear", "publicTrade/BTCUSDT").is_err());
        assert!(normalize_topic("linear", "tickers.SOLUSDT_SOL/USDT").is_err());
        assert!(normalize_topic("option", "tickers.BTC-22JAN23-17500-C").is_ok());
    }

    #[test]
    fn option_topics_use_official_symbol_shapes() {
        let client = BybitPublicWebSocket::new("option", Duration::from_secs(1)).expect("client");
        assert_eq!(
            client
                .exchange_symbol("BTC-22JAN23-17500-C")
                .expect("symbol"),
            "BTC-22JAN23-17500-C"
        );
        assert_eq!(
            client
                .trade_topic_symbol("BTC-22JAN23-17500-C")
                .expect("trade symbol"),
            "BTC"
        );
    }

    #[test]
    fn canonical_product_type_must_match_websocket_category() {
        let spot = BybitPublicWebSocket::new("spot", Duration::from_secs(1)).expect("spot");
        assert!(spot.exchange_symbol("BTC-USDT-SWAP").is_err());
        for category in ["linear", "inverse", "option", "spread"] {
            let client =
                BybitPublicWebSocket::new(category, Duration::from_secs(1)).expect("client");
            assert!(client.exchange_symbol("BTC-USDT-SPOT").is_err());
            assert!(client.exchange_symbol("btc-usdt-spot").is_err());
        }
    }

    #[test]
    fn rejects_canonical_derivatives_in_wrong_category() {
        for (category, symbol) in [
            ("option", "BTC-USDT-SWAP"),
            ("spot", "BTC-USD-260327-FUTURES"),
            ("linear", "BTC-USD-SWAP"),
            ("inverse", "BTC-USDT-SWAP"),
            ("linear", "BTC-USD-260327-80000-C-OPTION"),
        ] {
            let client = BybitPublicWebSocket::new(category, Duration::from_secs(1)).unwrap();
            assert!(client.exchange_symbol(symbol).is_err());
            assert!(
                client
                    .exchange_symbol(&symbol.to_ascii_lowercase())
                    .is_err()
            );
        }
        for (category, symbol, native) in [
            ("linear", "BTC-USDT-SWAP", "BTCUSDT"),
            ("linear", "BTC-USDC-SWAP", "BTCPERP"),
            ("inverse", "BTC-USD-SWAP", "BTCUSD"),
        ] {
            let client = BybitPublicWebSocket::new(category, Duration::from_secs(1)).unwrap();
            assert_eq!(client.exchange_symbol(symbol).unwrap(), native);
        }
    }

    #[test]
    fn loaded_products_must_match_exchange_category() {
        let make = |product: &str, category: &str| crate::product_table::MarketInfo {
            exchange: "bybit".into(),
            exchange_symbol: "BTCUSDT".into(),
            product_symbol: product.into(),
            product_type: "swap".into(),
            exchange_type: category.into(),
            base_currency: "BTC".into(),
            quote_currency: "USDT".into(),
            price_precision: "0.1".into(),
            size_precision: "0.001".into(),
            min_size: "0.001".into(),
            min_notional: "5".into(),
            size_per_contract: "1".into(),
            ..Default::default()
        };
        let table = ProductTable::new(vec![
            make("BTC-USDT-SPOT", "spot"),
            make("BTC-USDT-SWAP", "linear"),
        ]);
        for category in ["spot", "linear"] {
            let client = BybitPublicWebSocket::new(category, Duration::from_secs(1))
                .unwrap()
                .with_product_table(table.clone());
            assert_eq!(client.exchange_symbol("BTCUSDT").unwrap(), "BTCUSDT");
        }
        let wrong = ProductTable::new(vec![make("BTC-USDT-SWAP", "inverse")]);
        let client = BybitPublicWebSocket::new("linear", Duration::from_secs(1))
            .unwrap()
            .with_product_table(wrong);
        assert!(client.exchange_symbol("BTC-USDT-SWAP").is_err());
        assert!(client.exchange_symbol("BTCUSDT").is_err());
    }

    #[test]
    fn spread_category_uses_spread_url_and_leg_symbols() {
        assert_eq!(normalize_category("SPREAD").expect("spread"), "spread");
        assert_eq!(category_url("spread"), PUBLIC_SPREAD_WS_URL);
        let client = BybitPublicWebSocket::new("spread", Duration::from_secs(1)).expect("client");
        assert_eq!(
            client.exchange_symbol("SOLUSDT_SOL/USDT").expect("symbol"),
            "SOLUSDT_SOL/USDT"
        );
        assert!(client.exchange_symbol("SOLUSDT SOL").is_err());
        assert_eq!(
            normalize_topic("spread", "orderbook.25.SOLUSDT_SOL/USDT").expect("topic"),
            "orderbook.25.SOLUSDT_SOL/USDT"
        );
        assert!(normalize_topic("spread", "tickers.SOL USDT").is_err());
        assert!(validate_orderbook_depth("spread", 25).is_ok());
        assert!(validate_orderbook_depth("spread", 50).is_err());
    }

    #[tokio::test]
    async fn spread_rejects_klines_before_transport() {
        let mut client =
            BybitPublicWebSocket::new("spread", Duration::from_secs(1)).expect("client");
        assert!(
            client
                .subscribe_klines("SOLUSDT_SOL/USDT", "1m")
                .await
                .is_err()
        );
    }

    #[test]
    fn validates_orderbook_depths_by_category() {
        assert!(validate_orderbook_depth("spot", 1_000).is_ok());
        assert!(validate_orderbook_depth("linear", 25).is_err());
        assert!(validate_orderbook_depth("option", 25).is_ok());
        assert!(validate_orderbook_depth("option", 200).is_err());
    }

    #[tokio::test]
    async fn validates_public_subscription_argument_limits_before_transport() {
        let mut spot = BybitPublicWebSocket::new("spot", Duration::from_secs(1)).expect("spot");
        let topics = (0..11)
            .map(|index| format!("tickers.SYMBOL{index}"))
            .collect();
        assert!(spot.subscribe(topics).await.is_err());

        let mut option =
            BybitPublicWebSocket::new("option", Duration::from_secs(1)).expect("option");
        option.subscriptions = (0..2_000)
            .map(|index| format!("tickers.OPTION{index}"))
            .collect();
        assert!(
            option
                .subscribe(vec!["tickers.OPTION2000".to_string()])
                .await
                .is_err()
        );
    }
}
