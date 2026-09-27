use std::time::Duration;

use serde_json::{Value, json};

use crate::exchanges::kraken::{KrakenAuth, KrakenClient};
use crate::http::HttpMethod;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

const PRIVATE_WS_URL: &str = "wss://ws-auth.kraken.com/v2";
const SPOT_HTTP_BASE_URL: &str = "https://api.kraken.com";
const TOKEN_PATH: &str = "/0/private/GetWebSocketsToken";

pub struct KrakenPrivateWebSocket {
    connection: WebSocketConnection,
    client: KrakenClient,
    token: Option<String>,
    next_request_id: u64,
}

impl KrakenPrivateWebSocket {
    /// Create a token-authenticated connection to the dedicated L3 feed.
    pub fn new_level3(api_key: String, api_secret: String, timeout: Duration) -> Result<Self> {
        Self::with_urls(
            api_key,
            api_secret,
            timeout,
            SPOT_HTTP_BASE_URL,
            "wss://ws-l3.kraken.com/v2",
        )
    }

    /// Subscribe on an L3 connection. Read per-symbol acknowledgements with recv.
    pub async fn subscribe_level3(
        &mut self,
        product_symbols: Vec<String>,
        depth: u32,
        snapshot: bool,
    ) -> Result<u64> {
        self.level3_subscription("subscribe", product_symbols, depth, Some(snapshot))
            .await
    }
    pub async fn unsubscribe_level3(
        &mut self,
        product_symbols: Vec<String>,
        depth: u32,
    ) -> Result<u64> {
        self.level3_subscription("unsubscribe", product_symbols, depth, None)
            .await
    }
    async fn level3_subscription(
        &mut self,
        method: &str,
        product_symbols: Vec<String>,
        depth: u32,
        snapshot: Option<bool>,
    ) -> Result<u64> {
        if ![10, 100, 1000].contains(&depth) || !(1..=200).contains(&product_symbols.len()) {
            return Err(DcexError::InvalidInput(
                "Kraken L3 requires 1..=200 symbols and depth 10, 100 or 1000".into(),
            ));
        }
        let symbols: Vec<String> = product_symbols
            .iter()
            .map(|s| super::public::normalize_symbol(s))
            .collect::<Result<_>>()?;
        let unique: std::collections::BTreeSet<_> = symbols.iter().collect();
        if unique.len() != symbols.len()
            || symbols
                .iter()
                .any(|s| s.split('/').count() != 2 || s.starts_with('/') || s.ends_with('/'))
        {
            return Err(DcexError::InvalidInput(
                "Kraken L3 requires distinct BASE/QUOTE pairs".into(),
            ));
        }
        let mut extra = serde_json::Map::new();
        extra.insert("symbol".into(), json!(symbols));
        extra.insert("depth".into(), depth.into());
        if let Some(snapshot) = snapshot {
            extra.insert("snapshot".into(), snapshot.into());
        }
        self.send_private_subscription(method, "level3", Some(extra))
            .await
    }
    pub fn new(api_key: String, api_secret: String, timeout: Duration) -> Result<Self> {
        Self::with_urls(
            api_key,
            api_secret,
            timeout,
            SPOT_HTTP_BASE_URL.to_string(),
            PRIVATE_WS_URL.to_string(),
        )
    }

    pub fn with_urls(
        api_key: String,
        api_secret: String,
        timeout: Duration,
        spot_http_base_url: impl Into<String>,
        ws_base_url: impl Into<String>,
    ) -> Result<Self> {
        validate_credential("Kraken API key", &api_key)?;
        validate_credential("Kraken API secret", &api_secret)?;
        let client = KrakenClient::with_base_urls(
            Some(api_key),
            Some(api_secret),
            None,
            None,
            timeout,
            spot_http_base_url.into(),
            "https://futures.kraken.com".to_string(),
        )?;
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(ws_base_url, timeout)?),
            client,
            token: None,
            next_request_id: 1,
        })
    }

    pub fn is_connected(&self) -> bool {
        self.connection.is_connected()
    }

    pub fn token(&self) -> Option<&str> {
        self.token.as_deref()
    }

    pub async fn connect(&mut self) -> Result<String> {
        let token = self.fetch_token().await?;
        self.connection.connect().await?;
        Ok(token)
    }

    pub async fn fetch_token(&mut self) -> Result<String> {
        let response = self
            .client
            .request(
                HttpMethod::Post,
                KrakenAuth::Spot,
                TOKEN_PATH,
                Vec::new(),
                None,
                true,
            )
            .await?;
        let token = extract_token(&response.data)?;
        self.token = Some(token.clone());
        Ok(token)
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

    pub async fn subscribe_balances(
        &mut self,
        snapshot: bool,
        rebased: bool,
        users: Option<String>,
    ) -> Result<u64> {
        let mut extra = serde_json::Map::new();
        extra.insert("snapshot".to_string(), Value::Bool(snapshot));
        extra.insert("rebased".to_string(), Value::Bool(rebased));
        insert_users(&mut extra, users)?;
        self.send_private_subscription("subscribe", "balances", Some(extra))
            .await
    }

    pub async fn unsubscribe_balances(&mut self) -> Result<u64> {
        self.send_private_subscription("unsubscribe", "balances", None)
            .await
    }

    pub async fn subscribe_executions(
        &mut self,
        snap_orders: bool,
        snap_trades: bool,
        order_status: bool,
        rebased: bool,
        ratecounter: bool,
        users: Option<String>,
    ) -> Result<u64> {
        let mut extra = serde_json::Map::new();
        extra.insert("snap_orders".to_string(), Value::Bool(snap_orders));
        extra.insert("snap_trades".to_string(), Value::Bool(snap_trades));
        extra.insert("order_status".to_string(), Value::Bool(order_status));
        extra.insert("rebased".to_string(), Value::Bool(rebased));
        extra.insert("ratecounter".to_string(), Value::Bool(ratecounter));
        insert_users(&mut extra, users)?;
        self.send_private_subscription("subscribe", "executions", Some(extra))
            .await
    }

    pub async fn unsubscribe_executions(&mut self) -> Result<u64> {
        self.send_private_subscription("unsubscribe", "executions", None)
            .await
    }

    /// Send a Spot v2 trading request and return its req_id. Read the outcome with recv.
    pub async fn trade_request(&mut self, method: &str, mut params: Value) -> Result<u64> {
        super::trading::validate(method, &params)?;
        let token = self
            .token
            .as_ref()
            .ok_or_else(|| {
                DcexError::InvalidInput("Kraken WebSocket token is missing; connect first".into())
            })?
            .clone();
        params["token"] = token.into();
        let request_id = self.next_request_id();
        self.connection
            .send_json(&json!({"method":method,"params":params,"req_id":request_id}))
            .await?;
        Ok(request_id)
    }
    pub async fn add_order(&mut self, params: Value) -> Result<u64> {
        self.trade_request("add_order", params).await
    }
    pub async fn amend_order(&mut self, params: Value) -> Result<u64> {
        self.trade_request("amend_order", params).await
    }
    pub async fn cancel_order(&mut self, params: Value) -> Result<u64> {
        self.trade_request("cancel_order", params).await
    }
    pub async fn batch_add(&mut self, params: Value) -> Result<u64> {
        self.trade_request("batch_add", params).await
    }
    pub async fn batch_cancel(&mut self, params: Value) -> Result<u64> {
        self.trade_request("batch_cancel", params).await
    }
    pub async fn cancel_all(&mut self) -> Result<u64> {
        self.trade_request("cancel_all", json!({})).await
    }
    pub async fn cancel_after(&mut self, timeout: u64) -> Result<u64> {
        self.trade_request("cancel_after", json!({"timeout":timeout}))
            .await
    }
    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }

    async fn send_private_subscription(
        &mut self,
        method: &str,
        channel: &str,
        extra_params: Option<serde_json::Map<String, Value>>,
    ) -> Result<u64> {
        let method = normalize_method(method)?;
        let channel = normalize_channel(channel)?;
        let token = self
            .token
            .as_ref()
            .ok_or_else(|| {
                DcexError::InvalidInput("Kraken WebSocket token is missing.".to_string())
            })?
            .clone();
        let request_id = self.next_request_id();
        let mut params = serde_json::Map::new();
        params.insert("channel".to_string(), Value::String(channel));
        params.insert("token".to_string(), Value::String(token));
        if let Some(extra_params) = extra_params {
            params.extend(extra_params);
        }
        let payload = json!({
            "method": method,
            "params": params,
            "req_id": request_id,
        });
        self.connection.send_json(&payload).await?;
        Ok(request_id)
    }

    fn next_request_id(&mut self) -> u64 {
        let id = self.next_request_id;
        self.next_request_id = self.next_request_id.saturating_add(1).max(1);
        id
    }
}

fn extract_token(data: &Value) -> Result<String> {
    data.get("result")
        .and_then(|result| result.get("token"))
        .and_then(Value::as_str)
        .filter(|token| !token.trim().is_empty())
        .map(ToString::to_string)
        .ok_or_else(|| DcexError::Decode("Kraken WebSocket token missing.".to_string()))
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
        channel @ ("balances" | "executions" | "level3") => Ok(channel.to_string()),
        channel => Err(DcexError::InvalidInput(format!(
            "unsupported Kraken private WebSocket channel: {channel}"
        ))),
    }
}

fn insert_users(params: &mut serde_json::Map<String, Value>, users: Option<String>) -> Result<()> {
    if let Some(users) = users {
        if users != "all" {
            return Err(DcexError::InvalidInput(
                "Kraken WebSocket users must be 'all'.".to_string(),
            ));
        }
        params.insert("users".to_string(), Value::String(users));
    }
    Ok(())
}

fn validate_credential(label: &str, value: &str) -> Result<()> {
    if value.trim().is_empty() {
        return Err(DcexError::InvalidInput(format!(
            "{label} must not be empty."
        )));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn extracts_websocket_token() {
        let data = json!({
            "error": [],
            "result": {"token": "token-value", "expires": 900}
        });
        assert_eq!(extract_token(&data).expect("token"), "token-value");
    }

    #[test]
    fn rejects_missing_token() {
        let data = json!({"error": [], "result": {}});
        assert!(extract_token(&data).is_err());
    }
}
