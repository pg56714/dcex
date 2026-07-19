use std::time::Duration;

use serde_json::{json, Value};

use crate::crypto::hmac_sha256_base64;
use crate::exchange::unix_timestamp_ms;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

const PRIVATE_WS_URL: &str = "wss://ws.bitget.com/v2/ws/private";
const LOGIN_METHOD: &str = "GET";
const LOGIN_PATH: &str = "/user/verify";

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
        let inst_id = inst_id.map(|value| normalize_inst_id(&value)).transpose()?;
        let coin = coin.map(|value| normalize_coin(&value)).transpose()?;
        if channel == "positions"
            && (inst_type == "SPOT" || inst_id.as_deref() != Some("default") || coin.is_some())
        {
            return Err(DcexError::InvalidInput(
                "Bitget futures positions channel requires instId=default and does not support a coin filter."
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

    fn to_json(&self) -> Value {
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
            PRIVATE_WS_URL.to_string(),
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
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            api_key,
            api_secret,
            passphrase,
            logged_in: false,
        })
    }

    pub fn is_connected(&self) -> bool {
        self.connection.is_connected()
    }

    pub fn is_logged_in(&self) -> bool {
        self.logged_in
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

    pub async fn subscribe_orders(&mut self, inst_type: &str) -> Result<()> {
        self.subscribe_channel_with_inst_id(inst_type, "orders", "default")
            .await
    }

    pub async fn subscribe_orders_for_inst_id(
        &mut self,
        inst_type: &str,
        inst_id: &str,
    ) -> Result<()> {
        self.subscribe_channel_with_inst_id(inst_type, "orders", inst_id)
            .await
    }

    pub async fn subscribe_fills(&mut self, inst_type: &str) -> Result<()> {
        self.subscribe_channel_with_inst_id(inst_type, "fill", "default")
            .await
    }

    pub async fn subscribe_fills_for_inst_id(
        &mut self,
        inst_type: &str,
        inst_id: &str,
    ) -> Result<()> {
        self.subscribe_channel_with_inst_id(inst_type, "fill", inst_id)
            .await
    }

    pub async fn subscribe_positions(&mut self, inst_type: &str) -> Result<()> {
        self.subscribe_channel_with_inst_id(inst_type, "positions", "default")
            .await
    }

    pub async fn subscribe_positions_for_inst_id(
        &mut self,
        inst_type: &str,
        inst_id: &str,
    ) -> Result<()> {
        self.subscribe_channel_with_inst_id(inst_type, "positions", inst_id)
            .await
    }

    pub async fn subscribe_account(&mut self, inst_type: &str) -> Result<()> {
        self.subscribe_channel_with_coin(inst_type, "account", "default")
            .await
    }

    pub async fn subscribe_account_for_coin(&mut self, inst_type: &str, coin: &str) -> Result<()> {
        self.subscribe_channel_with_coin(inst_type, "account", coin)
            .await
    }

    pub async fn subscribe_equity(&mut self, inst_type: &str) -> Result<()> {
        self.subscribe_channel(inst_type, "equity").await
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
        let payload = json!({
            "op": op,
            "args": args.iter().map(BitgetPrivateWebSocketArg::to_json).collect::<Vec<_>>(),
        });
        self.connection.send_json(&payload).await
    }
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
        "SPOT" | "USDT-FUTURES" | "COIN-FUTURES" | "USDC-FUTURES" => Ok(inst_type),
        "MIX" | "SWAP" | "FUTURES" => Ok("USDT-FUTURES".to_string()),
        _ => Err(DcexError::InvalidInput(format!(
            "unsupported Bitget WebSocket instrument type: {inst_type}"
        ))),
    }
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
            BitgetPrivateWebSocketArg::with_inst_id("swap", "orders", "default").expect("arg");
        assert_eq!(arg.inst_type, "USDT-FUTURES");
        assert_eq!(arg.channel, "orders");
        assert_eq!(arg.inst_id.as_deref(), Some("default"));
        assert_eq!(arg.to_json()["instType"], "USDT-FUTURES");
        assert_eq!(arg.to_json()["instId"], "default");
    }

    #[test]
    fn rejects_invalid_private_arg() {
        assert!(BitgetPrivateWebSocketArg::new("USDT-FUTURES", "account").is_ok());
        assert!(BitgetPrivateWebSocketArg::new("bad", "orders").is_err());
        assert!(BitgetPrivateWebSocketArg::new("USDT-FUTURES", "orders/").is_err());
        assert!(BitgetPrivateWebSocketArg::new("USDT-FUTURES", "positions").is_err());
        assert!(
            BitgetPrivateWebSocketArg::with_inst_id("USDT-FUTURES", "positions", "BTCUSDT")
                .is_err()
        );
        assert!(BitgetPrivateWebSocketArg::with_inst_id("SPOT", "positions", "default").is_err());
        assert!(
            BitgetPrivateWebSocketArg::with_inst_id("USDT-FUTURES", "positions", "default").is_ok()
        );
        assert!(BitgetPrivateWebSocketArg::with_inst_id_and_coin(
            "USDT-FUTURES",
            "positions",
            "default",
            "USDT"
        )
        .is_err());
    }

    #[test]
    fn validates_login_ack() {
        assert!(validate_login_ack(&json!({"event": "login", "code": "0"})).is_ok());
        assert!(validate_login_ack(&json!({"event": "login", "code": "00000"})).is_ok());
        assert!(validate_login_ack(&json!({"event": "login", "code": "30001"})).is_err());
        assert!(validate_login_ack(&json!({"event": "subscribe", "code": "0"})).is_err());
    }
}
