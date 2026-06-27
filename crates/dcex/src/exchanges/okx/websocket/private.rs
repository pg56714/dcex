use std::time::Duration;

use serde_json::{json, Value};

use crate::crypto::hmac_sha256_base64;
use crate::exchange::unix_timestamp_ms;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

const PRIVATE_WS_URL: &str = "wss://ws.okx.com:8443/ws/v5/private";
const LOGIN_METHOD: &str = "GET";
const LOGIN_PATH: &str = "/users/self/verify";

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct OkxPrivateWebSocketArg {
    pub channel: String,
    pub inst_type: Option<String>,
    pub inst_id: Option<String>,
    pub ccy: Option<String>,
}

impl OkxPrivateWebSocketArg {
    pub fn new(channel: impl Into<String>) -> Result<Self> {
        Self::with_filters(channel, None, None, None)
    }

    pub fn with_inst_type(
        channel: impl Into<String>,
        inst_type: impl Into<String>,
    ) -> Result<Self> {
        Self::with_filters(channel, Some(inst_type.into()), None, None)
    }

    pub fn with_inst_id(channel: impl Into<String>, inst_id: impl Into<String>) -> Result<Self> {
        Self::with_filters(channel, None, Some(inst_id.into()), None)
    }

    pub fn with_inst_type_and_id(
        channel: impl Into<String>,
        inst_type: impl Into<String>,
        inst_id: impl Into<String>,
    ) -> Result<Self> {
        Self::with_filters(channel, Some(inst_type.into()), Some(inst_id.into()), None)
    }

    pub fn with_ccy(channel: impl Into<String>, ccy: impl Into<String>) -> Result<Self> {
        Self::with_filters(channel, None, None, Some(ccy.into()))
    }

    pub fn with_inst_type_and_ccy(
        channel: impl Into<String>,
        inst_type: impl Into<String>,
        ccy: impl Into<String>,
    ) -> Result<Self> {
        Self::with_filters(channel, Some(inst_type.into()), None, Some(ccy.into()))
    }

    pub fn with_inst_id_and_ccy(
        channel: impl Into<String>,
        inst_id: impl Into<String>,
        ccy: impl Into<String>,
    ) -> Result<Self> {
        Self::with_filters(channel, None, Some(inst_id.into()), Some(ccy.into()))
    }

    pub fn with_inst_type_and_id_and_ccy(
        channel: impl Into<String>,
        inst_type: impl Into<String>,
        inst_id: impl Into<String>,
        ccy: impl Into<String>,
    ) -> Result<Self> {
        Self::with_filters(
            channel,
            Some(inst_type.into()),
            Some(inst_id.into()),
            Some(ccy.into()),
        )
    }

    fn with_filters(
        channel: impl Into<String>,
        inst_type: Option<String>,
        inst_id: Option<String>,
        ccy: Option<String>,
    ) -> Result<Self> {
        Ok(Self {
            channel: normalize_channel(&channel.into())?,
            inst_type: inst_type
                .map(|value| normalize_token(&value, "instType"))
                .transpose()?,
            inst_id: inst_id.map(|value| normalize_inst_id(&value)).transpose()?,
            ccy: ccy
                .map(|value| normalize_token(&value, "ccy"))
                .transpose()?,
        })
    }

    fn to_json(&self) -> Value {
        let mut arg = serde_json::Map::new();
        arg.insert("channel".to_string(), Value::String(self.channel.clone()));
        if let Some(inst_type) = &self.inst_type {
            arg.insert("instType".to_string(), Value::String(inst_type.clone()));
        }
        if let Some(inst_id) = &self.inst_id {
            arg.insert("instId".to_string(), Value::String(inst_id.clone()));
        }
        if let Some(ccy) = &self.ccy {
            arg.insert("ccy".to_string(), Value::String(ccy.clone()));
        }
        Value::Object(arg)
    }
}

pub struct OkxPrivateWebSocket {
    connection: WebSocketConnection,
    api_key: String,
    api_secret: String,
    passphrase: String,
    logged_in: bool,
}

impl OkxPrivateWebSocket {
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
        validate_credential("OKX API key", &api_key)?;
        validate_credential("OKX API secret", &api_secret)?;
        validate_credential("OKX passphrase", &passphrase)?;
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

    pub async fn subscribe(&mut self, args: Vec<OkxPrivateWebSocketArg>) -> Result<()> {
        self.send_subscription("subscribe", args).await
    }

    pub async fn unsubscribe(&mut self, args: Vec<OkxPrivateWebSocketArg>) -> Result<()> {
        self.send_subscription("unsubscribe", args).await
    }

    pub async fn subscribe_orders(&mut self) -> Result<()> {
        self.subscribe(vec![OkxPrivateWebSocketArg::new("orders")?])
            .await
    }

    pub async fn subscribe_orders_for_type(&mut self, inst_type: &str) -> Result<()> {
        self.subscribe(vec![OkxPrivateWebSocketArg::with_inst_type(
            "orders", inst_type,
        )?])
        .await
    }

    pub async fn subscribe_orders_for_instrument(
        &mut self,
        inst_type: &str,
        inst_id: &str,
    ) -> Result<()> {
        self.subscribe(vec![OkxPrivateWebSocketArg::with_inst_type_and_id(
            "orders", inst_type, inst_id,
        )?])
        .await
    }

    pub async fn subscribe_account(&mut self) -> Result<()> {
        self.subscribe(vec![OkxPrivateWebSocketArg::new("account")?])
            .await
    }

    pub async fn subscribe_account_for_ccy(&mut self, ccy: &str) -> Result<()> {
        self.subscribe(vec![OkxPrivateWebSocketArg::with_ccy("account", ccy)?])
            .await
    }

    pub async fn subscribe_positions(&mut self) -> Result<()> {
        self.subscribe(vec![OkxPrivateWebSocketArg::new("positions")?])
            .await
    }

    pub async fn subscribe_positions_for_type(&mut self, inst_type: &str) -> Result<()> {
        self.subscribe(vec![OkxPrivateWebSocketArg::with_inst_type(
            "positions",
            inst_type,
        )?])
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
        args: Vec<OkxPrivateWebSocketArg>,
    ) -> Result<()> {
        if args.is_empty() {
            return Err(DcexError::InvalidInput(
                "at least one OKX private WebSocket channel is required.".to_string(),
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
            "args": args.iter().map(OkxPrivateWebSocketArg::to_json).collect::<Vec<_>>(),
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

fn normalize_channel(channel: &str) -> Result<String> {
    let channel = channel.trim();
    if channel.is_empty() {
        return Err(DcexError::InvalidInput(
            "OKX private WebSocket channel must not be empty.".to_string(),
        ));
    }
    if !channel
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || matches!(character, '-' | '_'))
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported OKX private WebSocket channel: {channel}"
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
    if event_name == Some("login") && code.as_deref() == Some("0") {
        Ok(())
    } else {
        Err(DcexError::Runtime(format!(
            "OKX WebSocket login rejected: {event}"
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
            "lhmJXK08fk9SI1ZwFXKFRrPtzfbNOwC+D1xMJJ/1KZg="
        );
    }

    #[test]
    fn builds_private_channel_arg() {
        let arg = OkxPrivateWebSocketArg::with_inst_type_and_id("orders", "swap", "btc-usdt-swap")
            .expect("arg");
        assert_eq!(arg.channel, "orders");
        assert_eq!(arg.inst_type.as_deref(), Some("SWAP"));
        assert_eq!(arg.inst_id.as_deref(), Some("BTC-USDT-SWAP"));
        assert_eq!(arg.to_json()["channel"], "orders");
        assert_eq!(arg.to_json()["instType"], "SWAP");
        assert_eq!(arg.to_json()["instId"], "BTC-USDT-SWAP");
    }

    #[test]
    fn rejects_invalid_channel_arg() {
        assert!(OkxPrivateWebSocketArg::new("bad channel").is_err());
        assert!(
            OkxPrivateWebSocketArg::with_inst_type_and_id("orders", "SWAP", "BTC/USDT").is_err()
        );
    }

    #[test]
    fn validates_login_ack() {
        assert!(validate_login_ack(&json!({"event": "login", "code": "0"})).is_ok());
        assert!(validate_login_ack(&json!({"event": "login", "code": "60012"})).is_err());
        assert!(validate_login_ack(&json!({"event": "subscribe", "code": "0"})).is_err());
    }
}
