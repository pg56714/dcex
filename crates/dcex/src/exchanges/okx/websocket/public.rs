use std::sync::Arc;
use std::time::Duration;

use serde_json::{Value, json};

use crate::product_table::ProductTable;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::super::params::exchange_symbol_fallback;
use super::is_business_channel;

/// Official base of the managed routes; each route appends its path segment.
const ROUTE_BASE_URL: &str = "wss://ws.okx.com:8443/ws/v5";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum OkxWebSocketRoute {
    Public,
    Business,
}

impl OkxWebSocketRoute {
    fn url(self, base: &str) -> String {
        match self {
            Self::Public => format!("{base}/public"),
            Self::Business => format!("{base}/business"),
        }
    }
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct OkxWebSocketArg {
    pub channel: String,
    pub inst_type: Option<String>,
    pub inst_family: Option<String>,
    pub inst_id: Option<String>,
    pub sprd_id: Option<String>,
}

impl OkxWebSocketArg {
    pub fn new(channel: impl Into<String>) -> Result<Self> {
        Self::with_filters(channel, None, None, None)
    }

    pub fn with_inst_id(channel: impl Into<String>, inst_id: impl Into<String>) -> Result<Self> {
        Self::with_filters(channel, None, None, Some(inst_id.into()))
    }

    /// Builds an arg for channels keyed by `instType`, e.g. `instruments` or
    /// `liquidation-orders`.
    pub fn with_inst_type(
        channel: impl Into<String>,
        inst_type: impl Into<String>,
    ) -> Result<Self> {
        Self::with_filters(channel, Some(inst_type.into()), None, None)
    }

    /// Builds an arg for channels keyed by `instFamily`, e.g. `opt-summary`.
    pub fn with_inst_family(
        channel: impl Into<String>,
        inst_family: impl Into<String>,
    ) -> Result<Self> {
        Self::with_filters(channel, None, Some(inst_family.into()), None)
    }

    /// Builds an arg with any combination of the documented public filters
    /// (`instType`, `instFamily`, `instId`).
    pub fn with_filters(
        channel: impl Into<String>,
        inst_type: Option<String>,
        inst_family: Option<String>,
        inst_id: Option<String>,
    ) -> Result<Self> {
        Ok(Self {
            channel: normalize_channel(&channel.into())?,
            inst_type: inst_type
                .map(|value| normalize_token(&value, "instType"))
                .transpose()?,
            inst_family: inst_family
                .map(|value| normalize_token(&value, "instFamily"))
                .transpose()?,
            inst_id: inst_id.map(|value| normalize_inst_id(&value)).transpose()?,
            sprd_id: None,
        })
    }

    /// Builds an arg for spread channels keyed by `sprdId`, e.g. `sprd-books5`.
    pub fn with_sprd_id(channel: impl Into<String>, sprd_id: impl Into<String>) -> Result<Self> {
        Self::new(channel)?.and_sprd_id(sprd_id)
    }

    /// Adds a `sprdId` filter (spread IDs such as `BTC-USDT_BTC-USDT-SWAP`
    /// contain `_`, which `instId` does not accept).
    pub fn and_sprd_id(mut self, sprd_id: impl Into<String>) -> Result<Self> {
        self.sprd_id = Some(normalize_token(&sprd_id.into(), "sprdId")?);
        Ok(self)
    }

    fn to_json(&self) -> Value {
        let mut arg = serde_json::Map::new();
        arg.insert("channel".to_string(), Value::String(self.channel.clone()));
        if let Some(inst_type) = &self.inst_type {
            arg.insert("instType".to_string(), Value::String(inst_type.clone()));
        }
        if let Some(inst_family) = &self.inst_family {
            arg.insert("instFamily".to_string(), Value::String(inst_family.clone()));
        }
        if let Some(inst_id) = &self.inst_id {
            arg.insert("instId".to_string(), Value::String(inst_id.clone()));
        }
        if let Some(sprd_id) = &self.sprd_id {
            arg.insert("sprdId".to_string(), Value::String(sprd_id.clone()));
        }
        Value::Object(arg)
    }
}

pub struct OkxPublicWebSocket {
    connection: WebSocketConnection,
    product_table: Option<Arc<ProductTable>>,
    timeout: Duration,
    managed_route: Option<OkxWebSocketRoute>,
    route_base: String,
    subscription_count: usize,
}

impl OkxPublicWebSocket {
    pub fn new(timeout: Duration) -> Result<Self> {
        Self::with_managed_route(ROUTE_BASE_URL, timeout)
    }

    pub fn with_url(url: impl Into<String>, timeout: Duration) -> Result<Self> {
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            product_table: None,
            timeout,
            managed_route: None,
            route_base: ROUTE_BASE_URL.to_string(),
            subscription_count: 0,
        })
    }

    /// Starts on the public route and moves to business channels as subscriptions need.
    pub(super) fn with_managed_route(route_base: &str, timeout: Duration) -> Result<Self> {
        let route = OkxWebSocketRoute::Public;
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(
                route.url(route_base),
                timeout,
            )?),
            product_table: None,
            timeout,
            managed_route: Some(route),
            route_base: route_base.to_string(),
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

    /// Builds a subscription arg, resolving `product_symbol` to an OKX `instId`
    /// through the product table when one is configured.
    pub fn channel_arg(
        &self,
        channel: &str,
        product_symbol: Option<&str>,
        inst_type: Option<&str>,
        inst_family: Option<&str>,
        sprd_id: Option<&str>,
    ) -> Result<OkxWebSocketArg> {
        let inst_id = product_symbol
            .map(|symbol| self.exchange_symbol(symbol))
            .transpose()?;
        let arg = OkxWebSocketArg::with_filters(
            channel,
            inst_type.map(str::to_string),
            inst_family.map(str::to_string),
            inst_id,
        )?;
        match sprd_id {
            Some(sprd_id) => arg.and_sprd_id(sprd_id),
            None => Ok(arg),
        }
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

    /// Subscribe with complete documented argument objects, including extra filters.
    pub async fn subscription_args(&mut self, op: &str, args: Vec<Value>) -> Result<()> {
        super::validate_raw_subscriptions(op, &args)?;
        let typed = args
            .iter()
            .map(|value| {
                let field = |key| value[key].as_str().map(str::to_owned);
                let mut arg = OkxWebSocketArg::with_filters(
                    value["channel"].as_str().unwrap(),
                    field("instType"),
                    field("instFamily"),
                    field("instId"),
                )?;
                if let Some(id) = field("sprdId") {
                    arg = arg.and_sprd_id(id)?;
                }
                Ok(arg)
            })
            .collect::<Result<Vec<_>>>()?;
        if op == "subscribe" {
            self.prepare_subscription_route(&typed).await?;
        } else {
            self.validate_subscription_route(&typed)?;
        }
        self.connection
            .send_json(&json!({"op":op,"args":args}))
            .await?;
        if op == "subscribe" {
            self.subscription_count += typed.len();
        } else {
            self.subscription_count = self.subscription_count.saturating_sub(typed.len());
        }
        Ok(())
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }

    fn exchange_symbol(&self, product_symbol: &str) -> Result<String> {
        if let Some(table) = &self.product_table {
            return Ok(table
                .resolve_symbol("okx", product_symbol, None, None)?
                .exchange_symbol
                .clone());
        }
        exchange_symbol_fallback(product_symbol)
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
        self.connection = WebSocketConnection::new(WebSocketConfig::new(
            target_route.url(&self.route_base),
            self.timeout,
        )?);
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
        let candidate = if is_business_channel(&arg.channel) {
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

fn normalize_token(value: &str, label: &str) -> Result<String> {
    let value = value.trim();
    if value.is_empty() {
        return Err(DcexError::InvalidInput(format!(
            "OKX {label} must not be empty."
        )));
    }
    if !value
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || character == '-' || character == '_')
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported OKX {label}: {value}"
        )));
    }
    Ok(value.to_ascii_uppercase())
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
    use serde_json::json;

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
    fn routes_official_business_channels_to_the_business_websocket() {
        let candle = OkxWebSocketArg::new("candle1m").expect("candle");
        let mark_price_candle =
            OkxWebSocketArg::new("mark-price-candle1m").expect("mark price candle");
        let index_candle = OkxWebSocketArg::new("index-candle1m").expect("index candle");
        let all_trades = OkxWebSocketArg::new("trades-all").expect("all trades");
        let trades = OkxWebSocketArg::new("trades").expect("trades");
        for business_channel in [candle.clone(), mark_price_candle, index_candle, all_trades] {
            assert_eq!(
                subscription_route(&[business_channel]).expect("route"),
                OkxWebSocketRoute::Business
            );
        }
        assert_eq!(
            subscription_route(std::slice::from_ref(&trades)).expect("route"),
            OkxWebSocketRoute::Public
        );
        assert!(subscription_route(&[candle, trades]).is_err());
    }

    #[test]
    fn builds_inst_type_and_inst_family_args() {
        let instruments = OkxWebSocketArg::with_inst_type("instruments", "spot").expect("arg");
        assert_eq!(
            instruments.to_json(),
            json!({"channel": "instruments", "instType": "SPOT"})
        );
        let summary = OkxWebSocketArg::with_inst_family("opt-summary", "btc-usd").expect("arg");
        assert_eq!(
            summary.to_json(),
            json!({"channel": "opt-summary", "instFamily": "BTC-USD"})
        );
        let option_trades = OkxWebSocketArg::with_filters(
            "option-trades",
            Some("OPTION".to_string()),
            Some("BTC-USD".to_string()),
            None,
        )
        .expect("arg");
        assert_eq!(
            option_trades.to_json(),
            json!({"channel": "option-trades", "instType": "OPTION", "instFamily": "BTC-USD"})
        );
        for (channel, inst_type) in [
            ("liquidation-orders", "SWAP"),
            ("adl-warning", "FUTURES"),
            ("estimated-price", "OPTION"),
        ] {
            let arg = OkxWebSocketArg::with_inst_type(channel, inst_type).expect("arg");
            assert_eq!(arg.to_json()["instType"], inst_type);
            assert!(arg.to_json().get("instId").is_none());
        }
        assert!(OkxWebSocketArg::with_inst_type("instruments", " ").is_err());
        assert!(OkxWebSocketArg::with_inst_family("opt-summary", "BTC/USD").is_err());
    }

    #[test]
    fn channel_arg_resolves_product_symbol_with_filters() {
        let client = OkxPublicWebSocket::new(Duration::from_secs(1)).expect("client");
        let arg = client
            .channel_arg(
                "estimated-price",
                Some("BTC-USD-SWAP"),
                Some("swap"),
                None,
                None,
            )
            .expect("arg");
        assert_eq!(
            arg.to_json(),
            json!({"channel": "estimated-price", "instType": "SWAP", "instId": "BTC-USD-SWAP"})
        );
        let bare = client
            .channel_arg("adl-warning", None, Some("SWAP"), Some("BTC-USDT"), None)
            .expect("arg");
        assert_eq!(
            bare.to_json(),
            json!({"channel": "adl-warning", "instType": "SWAP", "instFamily": "BTC-USDT"})
        );
    }

    #[test]
    fn builds_spread_args_with_sprd_id() {
        let books =
            OkxWebSocketArg::with_sprd_id("sprd-books5", "btc-usdt_btc-usdt-swap").expect("arg");
        assert_eq!(
            books.to_json(),
            json!({"channel": "sprd-books5", "sprdId": "BTC-USDT_BTC-USDT-SWAP"})
        );
        assert_eq!(
            subscription_route(std::slice::from_ref(&books)).expect("route"),
            OkxWebSocketRoute::Business
        );
        let client = OkxPublicWebSocket::new(Duration::from_secs(1)).expect("client");
        let tickers = client
            .channel_arg(
                "sprd-tickers",
                None,
                None,
                None,
                Some("BTC-USDT_BTC-USDT-SWAP"),
            )
            .expect("arg");
        assert_eq!(
            tickers.to_json(),
            json!({"channel": "sprd-tickers", "sprdId": "BTC-USDT_BTC-USDT-SWAP"})
        );
        assert!(OkxWebSocketArg::with_sprd_id("sprd-books5", "BTC/USDT").is_err());
        assert!(OkxWebSocketArg::with_sprd_id("sprd-books5", " ").is_err());
        // instId validation stays strict for non-spread channels.
        assert!(OkxWebSocketArg::with_inst_id("trades", "BTC-USDT_BTC-USDT-SWAP").is_err());
    }

    #[test]
    fn routes_spread_and_other_documented_business_channels() {
        for channel in [
            "sprd-books5",
            "sprd-books-l2-tbt",
            "sprd-bbo-tbt",
            "sprd-public-trades",
            "sprd-tickers",
            "sprd-candle1m",
        ] {
            let arg = OkxWebSocketArg::new(channel).expect("arg");
            assert_eq!(
                subscription_route(&[arg]).expect("route"),
                OkxWebSocketRoute::Business,
                "{channel}"
            );
        }
        let instruments = OkxWebSocketArg::with_inst_type("instruments", "SPOT").expect("arg");
        assert_eq!(
            subscription_route(&[instruments]).expect("route"),
            OkxWebSocketRoute::Public
        );
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
