use std::time::Duration;

use serde_json::{Value, json};

use crate::crypto::hmac_sha256_base64;
use crate::exchange::unix_timestamp_ms;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

const UTA_PRIVATE_WS_URL: &str = "wss://ws.bitget.com/v3/ws/private";
const LOGIN_METHOD: &str = "GET";
const LOGIN_PATH: &str = "/user/verify";
const UTA_INST_TYPE: &str = "UTA";

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct BitgetPrivateWebSocketArg {
    pub inst_type: String,
    pub channel: String,
    pub inst_id: Option<String>,
    pub coin: Option<String>,
}

impl BitgetPrivateWebSocketArg {
    pub fn new(inst_type: impl Into<String>, channel: impl Into<String>) -> Result<Self> {
        Self::with_filters(inst_type, channel, None, None)
    }

    pub fn with_inst_id(
        inst_type: impl Into<String>,
        channel: impl Into<String>,
        inst_id: impl Into<String>,
    ) -> Result<Self> {
        Self::with_filters(inst_type, channel, Some(inst_id.into()), None)
    }

    pub fn with_coin(
        inst_type: impl Into<String>,
        channel: impl Into<String>,
        coin: impl Into<String>,
    ) -> Result<Self> {
        Self::with_filters(inst_type, channel, None, Some(coin.into()))
    }

    pub fn with_inst_id_and_coin(
        inst_type: impl Into<String>,
        channel: impl Into<String>,
        inst_id: impl Into<String>,
        coin: impl Into<String>,
    ) -> Result<Self> {
        Self::with_filters(inst_type, channel, Some(inst_id.into()), Some(coin.into()))
    }

    fn with_filters(
        inst_type: impl Into<String>,
        channel: impl Into<String>,
        inst_id: Option<String>,
        coin: Option<String>,
    ) -> Result<Self> {
        let inst_type = normalize_inst_type(&inst_type.into())?;
        let channel = normalize_channel(&channel.into())?;
        let mut inst_id = inst_id.map(|value| normalize_inst_id(&value)).transpose()?;
        let coin = coin.map(|value| normalize_coin(&value)).transpose()?;
        if inst_type == UTA_INST_TYPE {
            if !matches!(
                channel.as_str(),
                "order"
                    | "fill"
                    | "position"
                    | "account"
                    | "strategy-order"
                    | "fast-fill"
                    | "adl-notification"
                    | "reality-orderbook"
            ) {
                return Err(DcexError::InvalidInput(
                    "unsupported Bitget UTA private topic".into(),
                ));
            }
            let supports_symbol = matches!(
                channel.as_str(),
                "strategy-order" | "reality-orderbook" | "fast-fill"
            );
            if (inst_id.is_some() && !supports_symbol) || coin.is_some() {
                return Err(DcexError::InvalidInput(
                    "Bitget UTA private topics cover all products and do not support instId or coin filters."
                        .to_string(),
                ));
            }
            if channel == "strategy-order" && inst_id.is_none() {
                inst_id = Some("default".to_string());
            }
            if channel == "strategy-order" && inst_id.as_deref() != Some("default") {
                return Err(DcexError::InvalidInput(
                    "Bitget UTA strategy-order only supports symbol default.".into(),
                ));
            }
            if channel == "reality-orderbook" && inst_id.is_none() {
                return Err(DcexError::InvalidInput(
                    "reality-orderbook requires a symbol".into(),
                ));
            }
            return Ok(Self {
                inst_type,
                channel,
                inst_id,
                coin,
            });
        }
        let retained_margin = inst_type == "MARGIN"
            && matches!(
                channel.as_str(),
                "orders-crossed" | "orders-isolated" | "account-crossed" | "account-isolated"
            );
        if !retained_margin && !matches!(channel.as_str(), "equity" | "positions-history") {
            return Err(DcexError::InvalidInput(
                "Bitget classic subscription was replaced by UTA; use a V3 private topic.".into(),
            ));
        }
        if channel == "equity" && (inst_type == "SPOT" || inst_id.is_some() || coin.is_some()) {
            return Err(DcexError::InvalidInput(
                "Bitget equity channel supports futures instrument types without filters."
                    .to_string(),
            ));
        }
        Ok(Self {
            inst_type,
            channel,
            inst_id,
            coin,
        })
    }

    /// Builds a UTA V3 private topic such as `order`, `fill`, `position` or `account`.
    pub fn uta(topic: impl Into<String>) -> Result<Self> {
        Self::new(UTA_INST_TYPE, topic)
    }

    pub fn is_uta(&self) -> bool {
        self.inst_type == UTA_INST_TYPE
    }

    fn to_json(&self) -> Value {
        if self.is_uta() {
            let mut value = json!({"instType": UTA_INST_TYPE, "topic": self.channel});
            if let Some(symbol) = &self.inst_id {
                value["symbol"] = Value::String(symbol.clone());
            }
            return value;
        }
        let mut arg = serde_json::Map::new();
        arg.insert(
            "instType".to_string(),
            Value::String(self.inst_type.clone()),
        );
        arg.insert("channel".to_string(), Value::String(self.channel.clone()));
        if let Some(inst_id) = &self.inst_id {
            arg.insert("instId".to_string(), Value::String(inst_id.clone()));
        }
        if let Some(coin) = &self.coin {
            arg.insert("coin".to_string(), Value::String(coin.clone()));
        }
        Value::Object(arg)
    }
}

pub struct BitgetPrivateWebSocket {
    connection: WebSocketConnection,
    api_key: String,
    api_secret: String,
    passphrase: String,
    logged_in: bool,
    uta_v3: bool,
}

impl BitgetPrivateWebSocket {
    pub fn new(
        api_key: String,
        api_secret: String,
        passphrase: String,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_url(
            api_key,
            api_secret,
            passphrase,
            UTA_PRIVATE_WS_URL.to_string(),
            timeout,
        )
    }

    pub fn with_url(
        api_key: String,
        api_secret: String,
        passphrase: String,
        url: impl Into<String>,
        timeout: Duration,
    ) -> Result<Self> {
        validate_credential("Bitget API key", &api_key)?;
        validate_credential("Bitget API secret", &api_secret)?;
        validate_credential("Bitget passphrase", &passphrase)?;
        let url = url.into();
        let uta_v3 = url
            .split('?')
            .next()
            .is_some_and(|path| path.ends_with("/v3/ws/private"));
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            api_key,
            api_secret,
            passphrase,
            logged_in: false,
            uta_v3,
        })
    }

    pub fn is_connected(&self) -> bool {
        self.connection.is_connected()
    }

    pub fn is_logged_in(&self) -> bool {
        self.logged_in
    }

    /// Whether this client targets the UTA V3 private endpoint (`instType=UTA` topics).
    pub fn is_uta_v3(&self) -> bool {
        self.uta_v3
    }

    pub async fn connect(&mut self) -> Result<()> {
        self.connection.connect().await?;
        self.login().await
    }

    pub async fn login(&mut self) -> Result<()> {
        self.logged_in = false;
        let timestamp = websocket_timestamp(unix_timestamp_ms()?);
        let sign = login_signature(&self.api_secret, &timestamp)?;
        let payload = json!({
            "op": "login",
            "args": [{
                "apiKey": self.api_key,
                "passphrase": self.passphrase,
                "timestamp": timestamp,
                "sign": sign,
            }],
        });
        self.connection.send_json(&payload).await?;
        let event = self.connection.recv_json().await?;
        validate_login_ack(&event)?;
        self.logged_in = true;
        Ok(())
    }

    pub async fn close(&mut self) -> Result<()> {
        self.logged_in = false;
        self.connection.close().await
    }

    pub async fn ping(&mut self) -> Result<()> {
        self.connection.send_text("ping").await
    }

    /// Sends a UTA trade frame. Read acknowledgements and per-order results with `recv`.
    pub async fn trade_request(
        &mut self,
        id: &str,
        topic: &str,
        category: Option<&str>,
        args: Value,
        request_time: Option<u64>,
    ) -> Result<()> {
        let payload = super::trading::uta(id, topic, category, args, request_time)?;
        if !self.uta_v3 || !self.logged_in {
            return Err(DcexError::InvalidInput(
                "Bitget UTA trading requires a logged-in V3 private connection.".into(),
            ));
        }
        self.connection.send_json(&payload).await
    }

    pub async fn subscribe(&mut self, args: Vec<BitgetPrivateWebSocketArg>) -> Result<()> {
        self.send_subscription("subscribe", args).await
    }

    pub async fn unsubscribe(&mut self, args: Vec<BitgetPrivateWebSocketArg>) -> Result<()> {
        self.send_subscription("unsubscribe", args).await
    }

    pub async fn subscribe_channel(&mut self, inst_type: &str, channel: &str) -> Result<()> {
        self.subscribe(vec![BitgetPrivateWebSocketArg::new(inst_type, channel)?])
            .await
    }

    pub async fn subscribe_channel_with_inst_id(
        &mut self,
        inst_type: &str,
        channel: &str,
        inst_id: &str,
    ) -> Result<()> {
        self.subscribe(vec![BitgetPrivateWebSocketArg::with_inst_id(
            inst_type, channel, inst_id,
        )?])
        .await
    }

    pub async fn subscribe_channel_with_coin(
        &mut self,
        inst_type: &str,
        channel: &str,
        coin: &str,
    ) -> Result<()> {
        self.subscribe(vec![BitgetPrivateWebSocketArg::with_coin(
            inst_type, channel, coin,
        )?])
        .await
    }

    pub async fn subscribe_channel_with_inst_id_and_coin(
        &mut self,
        inst_type: &str,
        channel: &str,
        inst_id: &str,
        coin: &str,
    ) -> Result<()> {
        self.subscribe(vec![BitgetPrivateWebSocketArg::with_inst_id_and_coin(
            inst_type, channel, inst_id, coin,
        )?])
        .await
    }

    pub async fn unsubscribe_channel(&mut self, inst_type: &str, channel: &str) -> Result<()> {
        self.unsubscribe(vec![BitgetPrivateWebSocketArg::new(inst_type, channel)?])
            .await
    }

    pub async fn unsubscribe_channel_with_inst_id(
        &mut self,
        inst_type: &str,
        channel: &str,
        inst_id: &str,
    ) -> Result<()> {
        self.unsubscribe(vec![BitgetPrivateWebSocketArg::with_inst_id(
            inst_type, channel, inst_id,
        )?])
        .await
    }

    pub async fn unsubscribe_channel_with_coin(
        &mut self,
        inst_type: &str,
        channel: &str,
        coin: &str,
    ) -> Result<()> {
        self.unsubscribe(vec![BitgetPrivateWebSocketArg::with_coin(
            inst_type, channel, coin,
        )?])
        .await
    }

    pub async fn unsubscribe_channel_with_inst_id_and_coin(
        &mut self,
        inst_type: &str,
        channel: &str,
        inst_id: &str,
        coin: &str,
    ) -> Result<()> {
        self.unsubscribe(vec![BitgetPrivateWebSocketArg::with_inst_id_and_coin(
            inst_type, channel, inst_id, coin,
        )?])
        .await
    }

    /// Subscribes to UTA order updates. This sends the V3
    /// `{"instType":"UTA","topic":"order"}` subscription covering every product.
    pub async fn subscribe_orders(&mut self) -> Result<()> {
        self.subscribe_channel("UTA", "order").await
    }

    pub async fn subscribe_fills(&mut self) -> Result<()> {
        self.subscribe_channel("UTA", "fill").await
    }

    pub async fn subscribe_positions(&mut self) -> Result<()> {
        self.subscribe_channel("UTA", "position").await
    }

    pub async fn subscribe_account(&mut self) -> Result<()> {
        self.subscribe_channel("UTA", "account").await
    }

    pub async fn subscribe_equity(&mut self, inst_type: &str) -> Result<()> {
        if is_uta_inst_type(inst_type) {
            return Err(DcexError::InvalidInput(
                "Bitget UTA has no equity topic; subscribe to the UTA account topic instead."
                    .to_string(),
            ));
        }
        self.subscribe_channel(inst_type, "equity").await
    }

    pub async fn subscribe_reality_orderbook(&mut self, symbol: &str) -> Result<()> {
        self.send_reality_orderbook("subscribe", symbol).await
    }

    pub async fn unsubscribe_reality_orderbook(&mut self, symbol: &str) -> Result<()> {
        self.send_reality_orderbook("unsubscribe", symbol).await
    }

    async fn send_reality_orderbook(&mut self, op: &str, symbol: &str) -> Result<()> {
        if !self.uta_v3 || !self.logged_in {
            return Err(DcexError::InvalidInput(
                "Bitget Reality orderbook requires an authenticated UTA V3 private WebSocket."
                    .to_string(),
            ));
        }
        let symbol = normalize_inst_id(symbol)?;
        self.connection
            .send_json(&json!({
                "op": op,
                "args": [{"instType": "UTA", "topic": "reality-orderbook", "symbol": symbol}],
            }))
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
        op: &str,
        args: Vec<BitgetPrivateWebSocketArg>,
    ) -> Result<()> {
        if args.is_empty() {
            return Err(DcexError::InvalidInput(
                "at least one Bitget private WebSocket channel is required.".to_string(),
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

fn subscription_payload(
    op: &str,
    uta_v3: bool,
    args: &[BitgetPrivateWebSocketArg],
) -> Result<Value> {
    validate_subscription_endpoint(uta_v3, args)?;
    Ok(json!({
        "op": op,
        "args": args.iter().map(BitgetPrivateWebSocketArg::to_json).collect::<Vec<_>>(),
    }))
}

fn login_signature(api_secret: &str, timestamp: &str) -> Result<String> {
    let payload = format!("{timestamp}{LOGIN_METHOD}{LOGIN_PATH}");
    hmac_sha256_base64(api_secret.as_bytes(), payload.as_bytes())
}

fn websocket_timestamp(timestamp_ms: u64) -> String {
    (timestamp_ms / 1_000).to_string()
}

fn normalize_inst_type(inst_type: &str) -> Result<String> {
    let inst_type = inst_type.trim().to_ascii_uppercase();
    match inst_type.as_str() {
        "MARGIN" | "SPOT" | "USDT-FUTURES" | "COIN-FUTURES" | "USDC-FUTURES" | UTA_INST_TYPE => {
            Ok(inst_type)
        }
        _ => Err(DcexError::InvalidInput(format!(
            "unsupported Bitget WebSocket instrument type: {inst_type}"
        ))),
    }
}

fn is_uta_inst_type(inst_type: &str) -> bool {
    inst_type.trim().eq_ignore_ascii_case(UTA_INST_TYPE)
}

fn validate_subscription_endpoint(uta_v3: bool, args: &[BitgetPrivateWebSocketArg]) -> Result<()> {
    for arg in args {
        BitgetPrivateWebSocketArg::with_filters(
            arg.inst_type.clone(),
            arg.channel.clone(),
            arg.inst_id.clone(),
            arg.coin.clone(),
        )?;
        if arg.is_uta() != uta_v3 {
            let message = if uta_v3 {
                "Bitget UTA V3 private WebSocket only accepts instType=UTA topics."
            } else {
                "Bitget instType=UTA topics require the UTA V3 private WebSocket (/v3/ws/private)."
            };
            return Err(DcexError::InvalidInput(message.to_string()));
        }
    }
    Ok(())
}

fn normalize_channel(channel: &str) -> Result<String> {
    let channel = channel.trim();
    if channel.is_empty() {
        return Err(DcexError::InvalidInput(
            "Bitget private WebSocket channel must not be empty.".to_string(),
        ));
    }
    if !channel
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || matches!(character, '-' | '_'))
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Bitget private WebSocket channel: {channel}"
        )));
    }
    Ok(channel.to_string())
}

fn normalize_inst_id(inst_id: &str) -> Result<String> {
    let inst_id = inst_id.trim();
    if inst_id.eq_ignore_ascii_case("default") {
        return Ok("default".to_string());
    }
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

fn normalize_coin(coin: &str) -> Result<String> {
    let coin = coin.trim();
    if coin.eq_ignore_ascii_case("default") {
        return Ok("default".to_string());
    }
    if coin.is_empty() {
        return Err(DcexError::InvalidInput(
            "Bitget coin must not be empty.".to_string(),
        ));
    }
    if !coin
        .chars()
        .all(|character| character.is_ascii_alphabetic())
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Bitget coin: {coin}"
        )));
    }
    Ok(coin.to_ascii_uppercase())
}

fn validate_credential(label: &str, value: &str) -> Result<()> {
    if value.trim().is_empty() {
        return Err(DcexError::InvalidInput(format!(
            "{label} must not be empty."
        )));
    }
    Ok(())
}

fn validate_login_ack(event: &Value) -> Result<()> {
    let event_name = event.get("event").and_then(Value::as_str);
    let code = event.get("code").and_then(value_as_string);
    if event_name == Some("login") && matches!(code.as_deref(), Some("0" | "00000")) {
        Ok(())
    } else {
        Err(DcexError::Runtime(format!(
            "Bitget WebSocket login rejected: {event}"
        )))
    }
}

fn value_as_string(value: &Value) -> Option<String> {
    match value {
        Value::String(value) => Some(value.clone()),
        Value::Number(value) => Some(value.to_string()),
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use serde_json::json;

    use super::*;

    #[test]
    fn websocket_timestamp_uses_seconds() {
        assert_eq!(websocket_timestamp(1_700_000_000_123), "1700000000");
    }

    #[test]
    fn login_signature_matches_known_payload() {
        assert_eq!(
            login_signature("secret", "1700000000").expect("signature"),
            "asp8h2LSGzNFWF9BshQJj0WiZA5uDIWsAk9FCfz2Ilk="
        );
    }

    #[test]
    fn builds_private_channel_arg() {
        let arg =
            BitgetPrivateWebSocketArg::with_inst_id("usdt-futures", "positions-history", "default")
                .expect("arg");
        assert_eq!(arg.inst_type, "USDT-FUTURES");
        assert_eq!(arg.channel, "positions-history");
        assert_eq!(arg.inst_id.as_deref(), Some("default"));
        assert_eq!(arg.to_json()["instType"], "USDT-FUTURES");
        assert_eq!(arg.to_json()["instId"], "default");
    }

    #[test]
    fn rejects_invalid_private_arg() {
        assert!(BitgetPrivateWebSocketArg::new("USDT-FUTURES", "account").is_err());
        assert!(
            BitgetPrivateWebSocketArg::with_coin("USDT-FUTURES", "account", "default").is_err()
        );
        assert!(BitgetPrivateWebSocketArg::new("bad", "orders").is_err());
        assert!(BitgetPrivateWebSocketArg::new("USDT-FUTURES", "orders/").is_err());
        assert!(BitgetPrivateWebSocketArg::new("USDT-FUTURES", "positions").is_err());
        assert!(
            BitgetPrivateWebSocketArg::with_inst_id("USDT-FUTURES", "positions", "BTCUSDT")
                .is_err()
        );
        assert!(BitgetPrivateWebSocketArg::with_inst_id("SPOT", "positions", "default").is_err());
        assert!(BitgetPrivateWebSocketArg::new("SPOT", "orders").is_err());
        assert!(
            BitgetPrivateWebSocketArg::with_inst_id("USDT-FUTURES", "positions", "default")
                .is_err()
        );
        assert!(
            BitgetPrivateWebSocketArg::with_inst_id_and_coin(
                "USDT-FUTURES",
                "positions",
                "default",
                "USDT"
            )
            .is_err()
        );
    }

    #[test]
    fn builds_uta_private_topic_arg() {
        for topic in [
            "order",
            "fill",
            "position",
            "account",
            "fast-fill",
            "adl-notification",
        ] {
            let arg = BitgetPrivateWebSocketArg::new("uta", topic).expect("uta arg");
            assert!(arg.is_uta());
            assert_eq!(arg.to_json(), json!({"instType": "UTA", "topic": topic}));
        }
        assert_eq!(
            BitgetPrivateWebSocketArg::uta("order").expect("uta"),
            BitgetPrivateWebSocketArg::new("UTA", "order").expect("uta")
        );
        assert!(BitgetPrivateWebSocketArg::with_inst_id("UTA", "order", "default").is_err());
        assert!(BitgetPrivateWebSocketArg::with_coin("UTA", "account", "default").is_err());
    }

    #[test]
    fn strategy_topic_preserves_documented_symbol() {
        let arg = BitgetPrivateWebSocketArg::with_inst_id("UTA", "strategy-order", "default")
            .expect("strategy topic");
        assert_eq!(
            subscription_payload("subscribe", true, &[arg]).expect("frame"),
            json!({"op":"subscribe","args":[{"instType":"UTA","topic":"strategy-order","symbol":"default"}]})
        );
        assert_eq!(
            BitgetPrivateWebSocketArg::uta("strategy-order")
                .expect("default")
                .to_json(),
            json!({"instType":"UTA","topic":"strategy-order","symbol":"default"})
        );
        assert!(BitgetPrivateWebSocketArg::uta("unknown-topic").is_err());
        assert!(
            BitgetPrivateWebSocketArg::with_inst_id("UTA", "strategy-order", "BTCUSDT").is_err()
        );
    }

    #[test]
    fn fast_fill_supports_optional_symbol() {
        for symbol in ["default", "BTCUSDT"] {
            let arg = BitgetPrivateWebSocketArg::with_inst_id("UTA", "fast-fill", symbol)
                .expect("fast-fill");
            assert_eq!(
                arg.to_json(),
                json!({"instType":"UTA","topic":"fast-fill","symbol":symbol})
            );
        }
        assert_eq!(
            BitgetPrivateWebSocketArg::uta("fast-fill")
                .expect("all products")
                .to_json(),
            json!({"instType":"UTA","topic":"fast-fill"})
        );
    }

    #[test]
    fn uta_topics_require_v3_endpoint_and_classic_requires_v2() {
        let uta = vec![BitgetPrivateWebSocketArg::uta("position").expect("uta")];
        let classic = vec![
            BitgetPrivateWebSocketArg::with_inst_id("USDT-FUTURES", "positions-history", "default")
                .expect("classic"),
        ];
        assert_eq!(
            subscription_payload("subscribe", true, &uta).expect("payload"),
            json!({"op": "subscribe", "args": [{"instType": "UTA", "topic": "position"}]})
        );
        assert_eq!(
            subscription_payload("subscribe", false, &classic).expect("payload"),
            json!({"op": "subscribe", "args": [
                {"instType": "USDT-FUTURES", "channel": "positions-history", "instId": "default"}
            ]})
        );
        assert!(subscription_payload("subscribe", false, &uta).is_err());
        assert!(subscription_payload("subscribe", true, &classic).is_err());
    }

    #[test]
    fn detects_uta_v3_private_url() {
        let timeout = std::time::Duration::from_secs(1);
        let uta = BitgetPrivateWebSocket::new("k".into(), "s".into(), "p".into(), timeout)
            .expect("uta client");
        assert!(uta.is_uta_v3());
    }

    #[test]
    fn validates_login_ack() {
        assert!(validate_login_ack(&json!({"event": "login", "code": "0"})).is_ok());
        assert!(validate_login_ack(&json!({"event": "login", "code": "00000"})).is_ok());
        assert!(validate_login_ack(&json!({"event": "login", "code": "30001"})).is_err());
        assert!(validate_login_ack(&json!({"event": "subscribe", "code": "0"})).is_err());
    }
}
