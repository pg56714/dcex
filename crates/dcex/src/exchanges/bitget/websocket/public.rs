use std::sync::Arc;
use std::time::Duration;

use serde_json::{Value, json};

use crate::product_table::ProductTable;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::super::params::exchange_symbol_fallback;

const UTA_PUBLIC_WS_URL: &str = "wss://ws.bitget.com/v3/ws/public";

/// Bitget public subscription argument.
///
/// Classic V2 args serialize as `{instType, channel, instId}`. UTA V3 args (built with
/// [`BitgetWebSocketArg::uta`]) serialize as `{instType (lowercase), topic, symbol?, interval?}`,
/// in which case `channel` holds the V3 topic and `inst_id` the symbol.
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct BitgetWebSocketArg {
    pub inst_type: String,
    pub channel: String,
    pub inst_id: String,
    pub interval: Option<String>,
    pub uta_v3: bool,
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
            interval: None,
            uta_v3: false,
        })
    }

    /// Builds a UTA V3 public topic (`ticker`, `publicTrade`, `books1`/`books5`/`books50`,
    /// or `kline` with an `interval`). Use an empty symbol for the futures-only `liquidation` topic.
    pub fn uta(
        inst_type: impl Into<String>,
        topic: impl Into<String>,
        symbol: impl Into<String>,
        interval: Option<String>,
    ) -> Result<Self> {
        let inst_type = normalize_inst_type(&inst_type.into())?;
        let topic = normalize_uta_topic(&topic.into())?;
        let symbol = symbol.into();
        let inst_id = if topic == "liquidation" {
            if !matches!(
                inst_type.as_str(),
                "USDT-FUTURES" | "COIN-FUTURES" | "USDC-FUTURES"
            ) || !symbol.trim().is_empty()
            {
                return Err(DcexError::InvalidInput(
                    "Bitget UTA liquidation requires a futures instrument type and no symbol."
                        .into(),
                ));
            }
            String::new()
        } else {
            normalize_inst_id(&symbol)?
        };
        let interval = match (topic.as_str(), interval) {
            ("kline", Some(interval)) => Some(normalize_uta_interval(&interval)?),
            ("kline", None) => {
                return Err(DcexError::InvalidInput(
                    "Bitget UTA kline topic requires an interval.".to_string(),
                ));
            }
            (_, Some(_)) => {
                return Err(DcexError::InvalidInput(format!(
                    "Bitget UTA {topic} topic does not take an interval."
                )));
            }
            (_, None) => None,
        };
        Ok(Self {
            inst_type,
            channel: topic,
            inst_id,
            interval,
            uta_v3: true,
        })
    }

    fn to_json(&self) -> Value {
        if self.uta_v3 {
            let mut arg = json!({
                "instType": self.inst_type.to_ascii_lowercase(),
                "topic": self.channel,
            });
            if self.channel != "liquidation" {
                arg["symbol"] = Value::String(self.inst_id.clone());
            }
            if let Some(interval) = &self.interval {
                arg["interval"] = Value::String(interval.clone());
            }
            return arg;
        }
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
    uta_v3: bool,
}

impl BitgetPublicWebSocket {
    pub fn new(default_inst_type: impl Into<String>, timeout: Duration) -> Result<Self> {
        Self::with_url(default_inst_type, UTA_PUBLIC_WS_URL.to_string(), timeout)
    }

    pub fn with_url(
        default_inst_type: impl Into<String>,
        url: impl Into<String>,
        timeout: Duration,
    ) -> Result<Self> {
        let url = url.into();
        let uta_v3 = url.split('?').next().is_some_and(|path| {
            path.ends_with("/v3/ws/public") || path.ends_with("/v3/ws/public/sbe")
        });
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            default_inst_type: normalize_inst_type(&default_inst_type.into())?,
            product_table: None,
            uta_v3,
        })
    }

    /// Whether this client targets the UTA V3 public endpoint.
    pub fn is_uta_v3(&self) -> bool {
        self.uta_v3
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

    /// Subscribes to a channel; on a UTA V3 client `channel` is the V3 topic name.
    pub async fn subscribe_channel(&mut self, channel: &str, product_symbol: &str) -> Result<()> {
        let arg = self.arg(channel, product_symbol, None)?;
        self.subscribe(vec![arg]).await
    }

    pub async fn unsubscribe_channel(&mut self, channel: &str, product_symbol: &str) -> Result<()> {
        let arg = self.arg(channel, product_symbol, None)?;
        self.unsubscribe(vec![arg]).await
    }

    pub async fn subscribe_ticker(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_channel("ticker", product_symbol).await
    }

    pub async fn subscribe_trades(&mut self, product_symbol: &str) -> Result<()> {
        let channel = "publicTrade";
        self.subscribe_channel(channel, product_symbol).await
    }

    pub async fn subscribe_orderbook(&mut self, product_symbol: &str, depth: u32) -> Result<()> {
        let channel = uta_orderbook_topic(depth)?;
        self.subscribe_channel(channel, product_symbol).await
    }

    pub async fn subscribe_klines(&mut self, product_symbol: &str, interval: &str) -> Result<()> {
        let arg = self.arg("kline", product_symbol, Some(interval.to_string()))?;
        self.subscribe(vec![arg]).await
    }

    fn arg(
        &self,
        channel: &str,
        product_symbol: &str,
        interval: Option<String>,
    ) -> Result<BitgetWebSocketArg> {
        if self.uta_v3 && channel.trim() == "liquidation" {
            return BitgetWebSocketArg::uta(
                &self.default_inst_type,
                channel,
                product_symbol,
                interval,
            );
        }
        let (inst_type, inst_id) = self.instrument(product_symbol)?;
        let mut arg = if self.uta_v3 {
            BitgetWebSocketArg::uta(inst_type, channel, &inst_id, interval)
        } else {
            BitgetWebSocketArg::new(inst_type, channel, &inst_id)
        }?;
        if self.product_table.is_some() {
            arg.inst_id = inst_id;
        }
        Ok(arg)
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }

    fn instrument(&self, product_symbol: &str) -> Result<(String, String)> {
        if let Some(table) = &self.product_table {
            let canonical = table
                .rows()
                .iter()
                .any(|row| row.exchange == "bitget" && row.product_symbol == product_symbol);
            let row = table.resolve_symbol_in("bitget", product_symbol, |row| {
                canonical
                    || row
                        .exchange_type
                        .eq_ignore_ascii_case(&self.default_inst_type)
            })?;
            return Ok((
                normalize_inst_type(&row.exchange_type)?,
                row.exchange_symbol.clone(),
            ));
        }
        let inst_id = exchange_symbol_fallback(product_symbol)?;
        Ok((
            self.inst_type_for(product_symbol)?,
            normalize_inst_id(&inst_id)?,
        ))
    }

    fn inst_type_for(&self, product_symbol: &str) -> Result<String> {
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
        let payload = subscription_payload(op, self.uta_v3, &args)?;
        self.connection.send_json(&payload).await
    }
}

fn subscription_payload(op: &str, uta_v3: bool, args: &[BitgetWebSocketArg]) -> Result<Value> {
    for arg in args {
        if !arg.uta_v3 {
            normalize_channel(&arg.channel)?;
        }
    }
    if args.iter().any(|arg| arg.uta_v3 != uta_v3) {
        let message = if uta_v3 {
            "Bitget UTA V3 public WebSocket requires topic args built with BitgetWebSocketArg::uta."
        } else {
            "Bitget UTA topic args require the UTA V3 public WebSocket (/v3/ws/public)."
        };
        return Err(DcexError::InvalidInput(message.to_string()));
    }
    Ok(json!({
        "op": op,
        "args": args.iter().map(BitgetWebSocketArg::to_json).collect::<Vec<_>>(),
    }))
}

fn normalize_uta_topic(topic: &str) -> Result<String> {
    let topic = topic.trim();
    match topic {
        "ticker" | "publicTrade" | "kline" | "books" | "books1" | "books5" | "books50"
        | "liquidation" | "rpi-books" | "rpi-books1" | "rpi-books5" | "rpi-books50" => {
            Ok(topic.to_string())
        }
        _ => Err(DcexError::InvalidInput(format!(
            "unsupported Bitget UTA WebSocket topic: {topic}"
        ))),
    }
}

fn normalize_uta_interval(interval: &str) -> Result<String> {
    let interval = interval.trim();
    if interval.is_empty()
        || !interval
            .chars()
            .all(|character| character.is_ascii_alphanumeric())
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Bitget UTA kline interval: {interval}"
        )));
    }
    Ok(interval.to_string())
}

fn uta_orderbook_topic(depth: u32) -> Result<&'static str> {
    match depth {
        1 => Ok("books1"),
        5 => Ok("books5"),
        50 => Ok("books50"),
        _ => Err(DcexError::InvalidInput(format!(
            "Bitget UTA orderbook depth must be 1, 5 or 50, got {depth}."
        ))),
    }
}

fn normalize_inst_type(inst_type: &str) -> Result<String> {
    let inst_type = inst_type.trim().to_ascii_uppercase();
    match inst_type.as_str() {
        "MARGIN" | "SPOT" | "USDT-FUTURES" | "COIN-FUTURES" | "USDC-FUTURES" => Ok(inst_type),
        _ => Err(DcexError::InvalidInput(format!(
            "unsupported Bitget WebSocket instrument type: {inst_type}"
        ))),
    }
}

fn normalize_channel(channel: &str) -> Result<String> {
    let channel = channel.trim();
    match channel {
        "auction" | "index-price" => Ok(channel.to_string()),
        _ => Err(DcexError::InvalidInput(format!(
            "unsupported Bitget WebSocket channel: {channel}"
        ))),
    }
}

fn normalize_inst_id(inst_id: &str) -> Result<String> {
    let inst_id = inst_id.trim();
    if inst_id == "default" {
        return Ok(inst_id.into());
    }
    if inst_id.is_empty() {
        return Err(DcexError::InvalidInput(
            "Bitget instrument ID must not be empty.".to_string(),
        ));
    }
    if !inst_id
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || character == '_')
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Bitget instrument ID: {inst_id}"
        )));
    }
    Ok(inst_id.to_ascii_uppercase())
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::*;

    #[test]
    fn normalizes_instrument_type_aliases() {
        assert_eq!(
            normalize_inst_type("usdt-futures").expect("inst_type"),
            "USDT-FUTURES"
        );
        // Only the documented instType values; no guessing which futures market "swap" means.
        for alias in ["swap", "mix", "futures"] {
            assert!(normalize_inst_type(alias).is_err(), "{alias}");
        }
        assert!(normalize_inst_type("bad").is_err());
    }

    #[test]
    fn builds_channel_arg() {
        let arg = BitgetWebSocketArg::new("spot", "auction", "btcusdt").expect("arg");
        assert_eq!(arg.inst_type, "SPOT");
        assert_eq!(arg.channel, "auction");
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
    fn builds_uta_v3_topic_args() {
        for topic in [
            "books",
            "rpi-books",
            "rpi-books1",
            "rpi-books5",
            "rpi-books50",
        ] {
            let arg = BitgetWebSocketArg::uta("USDT-FUTURES", topic, "BTCUSDT", None)
                .expect("official topic");
            assert_eq!(
                arg.to_json(),
                json!({"instType":"usdt-futures", "topic":topic, "symbol":"BTCUSDT"})
            );
        }
        let ticker =
            BitgetWebSocketArg::uta("USDT-FUTURES", "ticker", "btcusdt", None).expect("ticker");
        assert_eq!(
            ticker.to_json(),
            json!({"instType": "usdt-futures", "topic": "ticker", "symbol": "BTCUSDT"})
        );
        let kline = BitgetWebSocketArg::uta("spot", "kline", "BTCUSDT", Some("1m".to_string()))
            .expect("kline");
        assert_eq!(
            kline.to_json(),
            json!({"instType": "spot", "topic": "kline", "symbol": "BTCUSDT", "interval": "1m"})
        );
        assert!(BitgetWebSocketArg::uta("spot", "kline", "BTCUSDT", None).is_err());
        assert!(
            BitgetWebSocketArg::uta("spot", "ticker", "BTCUSDT", Some("1m".to_string())).is_err()
        );
        assert!(BitgetWebSocketArg::uta("spot", "trade", "BTCUSDT", None).is_err());
        assert!(BitgetWebSocketArg::uta("spot", "books15", "BTCUSDT", None).is_err());
    }

    #[test]
    fn uta_public_client_uses_v3_topics() {
        let client = BitgetPublicWebSocket::new("SPOT", Duration::from_secs(1)).expect("uta");
        assert!(client.is_uta_v3());
        let arg = client
            .arg("publicTrade", "BTC-USDT-SPOT", None)
            .expect("arg");
        assert_eq!(
            subscription_payload("subscribe", true, std::slice::from_ref(&arg)).expect("payload"),
            json!({"op": "subscribe", "args": [
                {"instType": "spot", "topic": "publicTrade", "symbol": "BTCUSDT"}
            ]})
        );
        let classic = BitgetWebSocketArg::new("spot", "auction", "BTCUSDT").expect("classic");
        assert!(subscription_payload("subscribe", true, std::slice::from_ref(&classic)).is_err());
        assert!(subscription_payload("subscribe", false, &[arg]).is_err());
        assert!(
            BitgetPublicWebSocket::new("SPOT", Duration::from_secs(1))
                .expect("classic")
                .is_uta_v3()
        );
        assert_eq!(uta_orderbook_topic(50).expect("books50"), "books50");
        assert!(uta_orderbook_topic(15).is_err());
    }

    #[test]
    fn maps_orderbook_depth_to_channel() {
        assert_eq!(uta_orderbook_topic(1).expect("books1"), "books1");
        assert_eq!(uta_orderbook_topic(5).expect("books5"), "books5");
        assert!(uta_orderbook_topic(15).is_err());
        assert!(uta_orderbook_topic(100).is_err());
        assert!(uta_orderbook_topic(0).is_err());
    }

    #[test]
    fn liquidation_uses_futures_scope_without_symbol() {
        for inst_type in ["usdt-futures", "coin-futures", "usdc-futures"] {
            let client =
                BitgetPublicWebSocket::new(inst_type, Duration::from_secs(1)).expect("client");
            let arg = client.arg("liquidation", "", None).expect("liquidation");
            for op in ["subscribe", "unsubscribe"] {
                assert_eq!(
                    subscription_payload(op, true, std::slice::from_ref(&arg)).expect("frame"),
                    json!({"op":op,"args":[{"instType":inst_type,"topic":"liquidation"}]})
                );
            }
            assert!(client.arg("liquidation", "BTCUSDT", None).is_err());
        }
        for inst_type in ["spot", "margin"] {
            assert!(BitgetWebSocketArg::uta(inst_type, "liquidation", "", None).is_err());
        }
    }
}
