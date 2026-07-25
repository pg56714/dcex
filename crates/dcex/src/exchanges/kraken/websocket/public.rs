use std::time::Duration;

use serde_json::{json, Value};

use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

const PUBLIC_WS_URL: &str = "wss://ws.kraken.com/v2";

pub struct KrakenPublicWebSocket {
    connection: WebSocketConnection,
    next_request_id: u64,
}

impl KrakenPublicWebSocket {
    pub fn new(timeout: Duration) -> Result<Self> {
        Self::with_url(PUBLIC_WS_URL.to_string(), timeout)
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
        self.connection.connect().await
    }

    pub async fn close(&mut self) -> Result<()> {
        self.connection.close().await
    }

    pub async fn ping(&mut self) -> Result<u64> {
        let request_id = self.next_request_id();
        let payload = json!({
            "method": "ping",
            "req_id": request_id,
        });
        self.connection.send_json(&payload).await?;
        Ok(request_id)
    }

    pub async fn subscribe_channel(
        &mut self,
        channel: &str,
        product_symbols: Vec<String>,
    ) -> Result<u64> {
        self.send_subscription("subscribe", channel, product_symbols, None)
            .await
    }

    pub async fn unsubscribe_channel(
        &mut self,
        channel: &str,
        product_symbols: Vec<String>,
    ) -> Result<u64> {
        self.send_subscription("unsubscribe", channel, product_symbols, None)
            .await
    }

    pub async fn subscribe_ticker(&mut self, product_symbol: &str) -> Result<u64> {
        self.subscribe_ticker_with_options(product_symbol, "trades", true)
            .await
    }

    pub async fn subscribe_ticker_with_options(
        &mut self,
        product_symbol: &str,
        event_trigger: &str,
        snapshot: bool,
    ) -> Result<u64> {
        let mut extra = serde_json::Map::new();
        extra.insert(
            "event_trigger".to_string(),
            Value::String(normalize_ticker_trigger(event_trigger)?.to_string()),
        );
        extra.insert("snapshot".to_string(), Value::Bool(snapshot));
        self.send_subscription(
            "subscribe",
            "ticker",
            vec![product_symbol.to_string()],
            Some(extra),
        )
        .await
    }

    pub async fn subscribe_trades(&mut self, product_symbol: &str) -> Result<u64> {
        self.subscribe_trades_with_options(product_symbol, false)
            .await
    }

    pub async fn subscribe_trades_with_options(
        &mut self,
        product_symbol: &str,
        snapshot: bool,
    ) -> Result<u64> {
        let mut extra = serde_json::Map::new();
        extra.insert("snapshot".to_string(), Value::Bool(snapshot));
        self.send_subscription(
            "subscribe",
            "trade",
            vec![product_symbol.to_string()],
            Some(extra),
        )
        .await
    }

    pub async fn subscribe_orderbook(&mut self, product_symbol: &str, depth: u32) -> Result<u64> {
        self.subscribe_orderbook_with_options(product_symbol, depth, true)
            .await
    }

    pub async fn subscribe_orderbook_with_options(
        &mut self,
        product_symbol: &str,
        depth: u32,
        snapshot: bool,
    ) -> Result<u64> {
        let mut extra = serde_json::Map::new();
        extra.insert("depth".to_string(), Value::from(normalize_depth(depth)?));
        extra.insert("snapshot".to_string(), Value::Bool(snapshot));
        self.send_subscription(
            "subscribe",
            "book",
            vec![product_symbol.to_string()],
            Some(extra),
        )
        .await
    }

    pub async fn subscribe_klines(&mut self, product_symbol: &str, interval: u32) -> Result<u64> {
        self.subscribe_klines_with_options(product_symbol, interval, true)
            .await
    }

    pub async fn subscribe_klines_with_options(
        &mut self,
        product_symbol: &str,
        interval: u32,
        snapshot: bool,
    ) -> Result<u64> {
        let mut extra = serde_json::Map::new();
        extra.insert(
            "interval".to_string(),
            Value::from(normalize_interval(interval)?),
        );
        extra.insert("snapshot".to_string(), Value::Bool(snapshot));
        self.send_subscription(
            "subscribe",
            "ohlc",
            vec![product_symbol.to_string()],
            Some(extra),
        )
        .await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }

    async fn send_subscription(
        &mut self,
        method: &str,
        channel: &str,
        product_symbols: Vec<String>,
        extra_params: Option<serde_json::Map<String, Value>>,
    ) -> Result<u64> {
        if product_symbols.is_empty() {
            return Err(DcexError::InvalidInput(
                "at least one Kraken WebSocket symbol is required.".to_string(),
            ));
        }
        let method = normalize_method(method)?;
        let channel = normalize_channel(channel)?;
        let symbols = product_symbols
            .into_iter()
            .map(|symbol| normalize_symbol(&symbol))
            .collect::<Result<Vec<_>>>()?;
        let request_id = self.next_request_id();
        let payload = subscription_payload(method, channel, symbols, extra_params, request_id);
        self.connection.send_json(&payload).await?;
        Ok(request_id)
    }

    fn next_request_id(&mut self) -> u64 {
        let id = self.next_request_id;
        self.next_request_id = self.next_request_id.saturating_add(1).max(1);
        id
    }
}

fn subscription_payload(
    method: &str,
    channel: String,
    symbols: Vec<String>,
    extra_params: Option<serde_json::Map<String, Value>>,
    request_id: u64,
) -> Value {
    let mut params = serde_json::Map::new();
    params.insert("channel".to_string(), Value::String(channel));
    params.insert(
        "symbol".to_string(),
        Value::Array(symbols.into_iter().map(Value::String).collect()),
    );
    if let Some(extra_params) = extra_params {
        params.extend(extra_params);
    }
    json!({
        "method": method,
        "params": params,
        "req_id": request_id,
    })
}

fn normalize_method(method: &str) -> Result<&'static str> {
    match method.trim() {
        "subscribe" => Ok("subscribe"),
        "unsubscribe" => Ok("unsubscribe"),
        method => Err(DcexError::InvalidInput(format!(
            "unsupported Kraken WebSocket method: {method}"
        ))),
    }
}

fn normalize_channel(channel: &str) -> Result<String> {
    match channel.trim() {
        channel @ ("ticker" | "trade" | "book" | "ohlc") => Ok(channel.to_string()),
        channel => Err(DcexError::InvalidInput(format!(
            "unsupported Kraken WebSocket channel: {channel}"
        ))),
    }
}

fn normalize_symbol(symbol: &str) -> Result<String> {
    let symbol = symbol.trim();
    if symbol.is_empty() {
        return Err(DcexError::InvalidInput(
            "Kraken WebSocket symbol must not be empty.".to_string(),
        ));
    }
    if symbol.contains('/') {
        return validate_symbol(symbol).map(|_| symbol.to_ascii_uppercase());
    }
    let mut parts = symbol.split('-');
    match (parts.next(), parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(kind), None) => {
            if !kind.eq_ignore_ascii_case("SPOT") {
                return Err(DcexError::InvalidInput(format!(
                    "Kraken Spot WebSocket does not support non-Spot product: {symbol}"
                )));
            }
            let normalized = format!(
                "{}/{}",
                base.to_ascii_uppercase(),
                quote.to_ascii_uppercase()
            );
            validate_symbol(&normalized)?;
            Ok(normalized)
        }
        _ => validate_symbol(symbol).map(|_| symbol.to_ascii_uppercase()),
    }
}

fn validate_symbol(symbol: &str) -> Result<()> {
    if !symbol
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || matches!(character, '/' | '.'))
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Kraken WebSocket symbol: {symbol}"
        )));
    }
    Ok(())
}

fn normalize_depth(depth: u32) -> Result<u32> {
    match depth {
        10 | 25 | 100 | 500 | 1000 => Ok(depth),
        _ => Err(DcexError::InvalidInput(format!(
            "unsupported Kraken orderbook depth: {depth}"
        ))),
    }
}

fn normalize_interval(interval: u32) -> Result<u32> {
    match interval {
        1 | 5 | 15 | 30 | 60 | 240 | 1440 | 10080 | 21600 => Ok(interval),
        _ => Err(DcexError::InvalidInput(format!(
            "unsupported Kraken OHLC interval: {interval}"
        ))),
    }
}

fn normalize_ticker_trigger(event_trigger: &str) -> Result<&'static str> {
    match event_trigger.trim() {
        "bbo" => Ok("bbo"),
        "trades" => Ok("trades"),
        event_trigger => Err(DcexError::InvalidInput(format!(
            "unsupported Kraken ticker event trigger: {event_trigger}"
        ))),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn normalizes_canonical_symbol_to_ws_pair() {
        assert_eq!(normalize_symbol("BTC-USD-SPOT").expect("symbol"), "BTC/USD");
        assert_eq!(normalize_symbol("eth/usd").expect("symbol"), "ETH/USD");
        assert!(normalize_symbol("bad symbol").is_err());
        assert!(normalize_symbol("BTC-USD-SWAP").is_err());
    }

    #[test]
    fn validates_depth_and_interval() {
        assert_eq!(normalize_depth(10).expect("depth"), 10);
        assert!(normalize_depth(50).is_err());
        assert_eq!(normalize_interval(5).expect("interval"), 5);
        assert!(normalize_interval(2).is_err());
        assert_eq!(normalize_ticker_trigger("bbo").expect("trigger"), "bbo");
        assert!(normalize_ticker_trigger("trade").is_err());
    }

    #[test]
    fn subscription_payload_includes_req_id() {
        let payload = subscription_payload(
            "subscribe",
            "trade".to_string(),
            vec!["BTC/USD".to_string()],
            None,
            42,
        );

        assert_eq!(payload["method"], "subscribe");
        assert_eq!(payload["params"]["channel"], "trade");
        assert_eq!(payload["req_id"], 42);
        assert!(payload["params"].get("req_id").is_none());
    }

    #[test]
    fn subscription_payload_includes_channel_options() {
        let mut extra = serde_json::Map::new();
        extra.insert("snapshot".to_string(), Value::Bool(false));
        extra.insert(
            "event_trigger".to_string(),
            Value::String("bbo".to_string()),
        );
        let payload = subscription_payload(
            "subscribe",
            "ticker".to_string(),
            vec!["BTC/USD".to_string()],
            Some(extra),
            7,
        );

        assert_eq!(payload["params"]["snapshot"], false);
        assert_eq!(payload["params"]["event_trigger"], "bbo");
    }
}
