use std::time::Duration;

use serde_json::Value;

use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::super::params::{
    exchange_symbol_fallback, is_canonical_product_symbol, is_equity_product_symbol,
};

const EQUITY_WS_BASE_URL: &str = "wss://nbstream.binance.com/equity";

pub struct BinanceEquityWebSocket {
    connection: WebSocketConnection,
}

impl BinanceEquityWebSocket {
    pub fn new(
        stream: &str,
        product_symbol: Option<&str>,
        interval: Option<&str>,
        listen_key: Option<&str>,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_url(
            stream,
            product_symbol,
            interval,
            listen_key,
            timeout,
            EQUITY_WS_BASE_URL.to_string(),
        )
    }

    pub fn with_base_url(
        stream: &str,
        product_symbol: Option<&str>,
        interval: Option<&str>,
        listen_key: Option<&str>,
        timeout: Duration,
        base_url: String,
    ) -> Result<Self> {
        let url = equity_stream_url(&base_url, stream, product_symbol, interval, listen_key)?;
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
        })
    }

    pub fn price(timeout: Duration) -> Result<Self> {
        Self::new("price", None, None, None, timeout)
    }

    pub fn quote(product_symbol: &str, timeout: Duration) -> Result<Self> {
        Self::new("quote", Some(product_symbol), None, None, timeout)
    }

    pub fn klines(product_symbol: &str, interval: &str, timeout: Duration) -> Result<Self> {
        Self::new("kline", Some(product_symbol), Some(interval), None, timeout)
    }

    pub fn calendar(timeout: Duration) -> Result<Self> {
        Self::new("calendar", None, None, None, timeout)
    }

    pub fn tradability(product_symbol: &str, timeout: Duration) -> Result<Self> {
        Self::new("tradability", Some(product_symbol), None, None, timeout)
    }

    pub fn trading_status(product_symbol: &str, timeout: Duration) -> Result<Self> {
        Self::new("trading_status", Some(product_symbol), None, None, timeout)
    }

    pub fn order_reports(listen_key: &str, timeout: Duration) -> Result<Self> {
        Self::new("order_report", None, None, Some(listen_key), timeout)
    }

    pub fn url(&self) -> &str {
        &self.connection.config().url
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

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }
}

fn equity_stream_url(
    base_url: &str,
    stream: &str,
    product_symbol: Option<&str>,
    interval: Option<&str>,
    listen_key: Option<&str>,
) -> Result<String> {
    let base_url = normalize_base_url(base_url)?;
    let path = match stream {
        "price" => {
            ensure_absent(product_symbol, "product_symbol", stream)?;
            ensure_absent(interval, "interval", stream)?;
            ensure_absent(listen_key, "listen_key", stream)?;
            "price".to_string()
        }
        "quote" => {
            ensure_absent(interval, "interval", stream)?;
            ensure_absent(listen_key, "listen_key", stream)?;
            format!(
                "{}@quote",
                equity_symbol(required(product_symbol, "product_symbol")?)?
            )
        }
        "kline" | "klines" => {
            ensure_absent(listen_key, "listen_key", stream)?;
            let interval = validate_component(required(interval, "interval")?, "interval")?;
            format!(
                "{}@kline_{interval}",
                equity_symbol(required(product_symbol, "product_symbol")?)?
            )
        }
        "calendar" => {
            ensure_absent(product_symbol, "product_symbol", stream)?;
            ensure_absent(interval, "interval", stream)?;
            ensure_absent(listen_key, "listen_key", stream)?;
            "calendar".to_string()
        }
        "tradability" => {
            ensure_absent(interval, "interval", stream)?;
            ensure_absent(listen_key, "listen_key", stream)?;
            format!(
                "{}@tradability",
                equity_symbol(required(product_symbol, "product_symbol")?)?
            )
        }
        "trading_status" | "tradingStatus" => {
            ensure_absent(interval, "interval", stream)?;
            ensure_absent(listen_key, "listen_key", stream)?;
            format!(
                "{}@tradingStatus",
                equity_symbol(required(product_symbol, "product_symbol")?)?
            )
        }
        "order_report" | "orderReport" => {
            ensure_absent(product_symbol, "product_symbol", stream)?;
            ensure_absent(interval, "interval", stream)?;
            let listen_key = validate_component(required(listen_key, "listen_key")?, "listen_key")?;
            format!("{listen_key}@orderReport")
        }
        _ => {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Binance Equity WebSocket stream: {stream}"
            )))
        }
    };
    Ok(format!("{base_url}/ws/{path}"))
}

fn equity_symbol(product_symbol: &str) -> Result<String> {
    if is_canonical_product_symbol(product_symbol) && !is_equity_product_symbol(product_symbol) {
        return Err(DcexError::InvalidInput(format!(
            "Binance Equity WebSocket requires an Equity product symbol: {product_symbol}"
        )));
    }
    validate_component(&exchange_symbol_fallback(product_symbol), "product_symbol")
}

fn required<'a>(value: Option<&'a str>, key: &str) -> Result<&'a str> {
    value.ok_or_else(|| DcexError::InvalidInput(format!("Binance Equity {key} is required.")))
}

fn ensure_absent(value: Option<&str>, key: &str, stream: &str) -> Result<()> {
    if value.is_some() {
        return Err(DcexError::InvalidInput(format!(
            "Binance Equity {stream} stream does not accept {key}."
        )));
    }
    Ok(())
}

fn validate_component(value: &str, label: &str) -> Result<String> {
    let value = value.trim();
    if value.is_empty()
        || !value.chars().all(|character| {
            character.is_ascii_alphanumeric() || matches!(character, '.' | '_' | '-')
        })
    {
        return Err(DcexError::InvalidInput(format!(
            "invalid Binance Equity WebSocket {label}: {value}"
        )));
    }
    Ok(value.to_string())
}

fn normalize_base_url(base_url: &str) -> Result<String> {
    let base_url = base_url.trim().trim_end_matches('/');
    if base_url.is_empty() {
        return Err(DcexError::InvalidInput(
            "Binance Equity WebSocket base URL must not be empty.".to_string(),
        ));
    }
    Ok(base_url.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn builds_all_documented_equity_stream_urls() {
        let base = "wss://nbstream.binance.com/equity/";
        assert_eq!(
            equity_stream_url(base, "price", None, None, None).expect("price"),
            "wss://nbstream.binance.com/equity/ws/price"
        );
        assert_eq!(
            equity_stream_url(base, "quote", Some("AAPL-USDC-EQUITY"), None, None).expect("quote"),
            "wss://nbstream.binance.com/equity/ws/AAPL@quote"
        );
        assert_eq!(
            equity_stream_url(base, "kline", Some("AAPL-USDC-EQUITY"), Some("1m"), None,)
                .expect("kline"),
            "wss://nbstream.binance.com/equity/ws/AAPL@kline_1m"
        );
        assert_eq!(
            equity_stream_url(base, "calendar", None, None, None).expect("calendar"),
            "wss://nbstream.binance.com/equity/ws/calendar"
        );
        assert_eq!(
            equity_stream_url(base, "tradability", Some("AAPL-USDC-EQUITY"), None, None,)
                .expect("tradability"),
            "wss://nbstream.binance.com/equity/ws/AAPL@tradability"
        );
        assert_eq!(
            equity_stream_url(base, "trading_status", Some("AAPL-USDC-EQUITY"), None, None,)
                .expect("trading status"),
            "wss://nbstream.binance.com/equity/ws/AAPL@tradingStatus"
        );
        assert_eq!(
            equity_stream_url(base, "order_report", None, None, Some("listen-key"))
                .expect("order report"),
            "wss://nbstream.binance.com/equity/ws/listen-key@orderReport"
        );
    }

    #[test]
    fn validates_equity_stream_arguments() {
        assert!(equity_stream_url(
            EQUITY_WS_BASE_URL,
            "quote",
            Some("BTC-USDT-SPOT"),
            None,
            None,
        )
        .is_err());
        assert!(equity_stream_url(
            EQUITY_WS_BASE_URL,
            "order_report",
            None,
            None,
            Some("bad/key"),
        )
        .is_err());
        assert!(equity_stream_url(EQUITY_WS_BASE_URL, "unknown", None, None, None).is_err());
    }
}
