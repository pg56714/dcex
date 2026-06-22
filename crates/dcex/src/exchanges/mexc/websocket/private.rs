use std::time::Duration;

use serde_json::{json, Value};

use crate::crypto::hmac_sha256_hex;
use crate::exchange::unix_timestamp_ms;
use crate::http::{AsyncHttpClient, HttpMethod, HttpRequest};
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::super::signing::encode_params;

const SPOT_HTTP_BASE_URL: &str = "https://api.mexc.com";
const WS_BASE_URL: &str = "wss://wbs-api.mexc.com/ws";
const LISTEN_KEY_PATH: &str = "/api/v3/userDataStream";

pub struct MexcPrivateWebSocket {
    connection: WebSocketConnection,
    transport: AsyncHttpClient,
    api_key: String,
    api_secret: Option<String>,
    spot_http_base_url: String,
    ws_base_url: String,
    timeout: Duration,
    listen_key: Option<String>,
}

impl MexcPrivateWebSocket {
    pub fn new(api_key: String, timeout: Duration) -> Result<Self> {
        Self::with_urls_and_secret(
            api_key,
            None,
            timeout,
            SPOT_HTTP_BASE_URL.to_string(),
            WS_BASE_URL.to_string(),
        )
    }

    pub fn with_secret(api_key: String, api_secret: String, timeout: Duration) -> Result<Self> {
        Self::with_urls_and_secret(
            api_key,
            Some(api_secret),
            timeout,
            SPOT_HTTP_BASE_URL.to_string(),
            WS_BASE_URL.to_string(),
        )
    }

    pub fn with_urls(
        api_key: String,
        timeout: Duration,
        spot_http_base_url: impl Into<String>,
        ws_base_url: impl Into<String>,
    ) -> Result<Self> {
        Self::with_urls_and_secret(api_key, None, timeout, spot_http_base_url, ws_base_url)
    }

    pub fn with_urls_and_secret(
        api_key: String,
        api_secret: Option<String>,
        timeout: Duration,
        spot_http_base_url: impl Into<String>,
        ws_base_url: impl Into<String>,
    ) -> Result<Self> {
        validate_credential("MEXC API key", &api_key)?;
        if let Some(api_secret) = api_secret.as_deref() {
            validate_credential("MEXC API secret", api_secret)?;
        }
        let spot_http_base_url = spot_http_base_url.into();
        let ws_base_url = ws_base_url.into();
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(
                private_ws_url(&ws_base_url, "")?,
                timeout,
            )?),
            transport: AsyncHttpClient::new(timeout)?,
            api_key,
            api_secret,
            spot_http_base_url,
            ws_base_url,
            timeout,
            listen_key: None,
        })
    }

    pub fn is_connected(&self) -> bool {
        self.connection.is_connected()
    }

    pub fn listen_key(&self) -> Option<&str> {
        self.listen_key.as_deref()
    }

    pub async fn connect(&mut self) -> Result<String> {
        let listen_key = self.create_listen_key().await?;
        self.connection = WebSocketConnection::new(WebSocketConfig::new(
            private_ws_url(&self.ws_base_url, &listen_key)?,
            self.timeout,
        )?);
        self.connection.connect().await?;
        Ok(listen_key)
    }

    pub async fn create_listen_key(&mut self) -> Result<String> {
        let response = self
            .transport
            .execute(self.listen_key_request(HttpMethod::Post, None)?)
            .await?;
        response.ensure_success()?;
        let data = response.json()?;
        let listen_key = extract_listen_key(&data)?;
        self.listen_key = Some(listen_key.clone());
        Ok(listen_key)
    }

    pub async fn keep_alive(&mut self) -> Result<String> {
        let listen_key = self
            .listen_key
            .clone()
            .ok_or_else(|| DcexError::InvalidInput("MEXC listen key is missing.".to_string()))?;
        let response = self
            .transport
            .execute(self.listen_key_request(HttpMethod::Put, Some(&listen_key))?)
            .await?;
        response.ensure_success()?;
        let data = response.json()?;
        Ok(extract_listen_key(&data).unwrap_or(listen_key))
    }

    pub async fn close_listen_key(&mut self) -> Result<()> {
        if let Some(listen_key) = self.listen_key.take() {
            let response = self
                .transport
                .execute(self.listen_key_request(HttpMethod::Delete, Some(&listen_key))?)
                .await?;
            response.ensure_success()?;
        }
        Ok(())
    }

    pub async fn close(&mut self) -> Result<()> {
        let close_result = self.connection.close().await;
        let listen_key_result = self.close_listen_key().await;
        close_result?;
        listen_key_result
    }

    pub async fn ping(&mut self) -> Result<()> {
        self.connection.send_json(&json!({"method": "PING"})).await
    }

    pub async fn subscribe(&mut self, channels: Vec<String>) -> Result<()> {
        self.send_subscription("SUBSCRIPTION", channels).await
    }

    pub async fn unsubscribe(&mut self, channels: Vec<String>) -> Result<()> {
        self.send_subscription("UNSUBSCRIPTION", channels).await
    }

    pub async fn subscribe_account(&mut self) -> Result<()> {
        self.subscribe(vec!["spot@private.account.v3.api.pb".to_string()])
            .await
    }

    pub async fn subscribe_deals(&mut self) -> Result<()> {
        self.subscribe(vec!["spot@private.deals.v3.api.pb".to_string()])
            .await
    }

    pub async fn subscribe_orders(&mut self) -> Result<()> {
        self.subscribe(vec!["spot@private.orders.v3.api.pb".to_string()])
            .await
    }

    pub async fn recv(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }

    async fn send_subscription(&mut self, method: &str, channels: Vec<String>) -> Result<()> {
        if channels.is_empty() {
            return Err(DcexError::InvalidInput(
                "at least one MEXC private WebSocket channel is required.".to_string(),
            ));
        }
        let method = match method {
            "SUBSCRIPTION" | "UNSUBSCRIPTION" => method,
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported MEXC WebSocket method: {method}"
                )));
            }
        };
        let channels = channels
            .into_iter()
            .map(|channel| normalize_channel(&channel))
            .collect::<Result<Vec<_>>>()?;
        let payload = json!({
            "method": method,
            "params": channels,
        });
        self.connection.send_json(&payload).await
    }

    fn listen_key_request(
        &self,
        method: HttpMethod,
        listen_key: Option<&str>,
    ) -> Result<HttpRequest> {
        let mut request = HttpRequest::new(method, &self.spot_http_base_url, LISTEN_KEY_PATH)
            .header("X-MEXC-APIKEY", self.api_key.clone());
        let mut query = Vec::new();
        if let Some(listen_key) = listen_key {
            query.push(("listenKey".to_string(), listen_key.to_string()));
        }
        if let Some(api_secret) = self.api_secret.as_deref() {
            query.push(("timestamp".to_string(), unix_timestamp_ms()?.to_string()));
            let signature =
                hmac_sha256_hex(api_secret.as_bytes(), encode_params(&query).as_bytes())?;
            query.push(("signature".to_string(), signature));
        }
        request.query = query;
        Ok(request)
    }
}

fn private_ws_url(base_url: &str, listen_key: &str) -> Result<String> {
    let base_url = base_url.trim_end_matches('/');
    if base_url.is_empty() {
        return Err(DcexError::InvalidInput(
            "MEXC WebSocket base URL must not be empty.".to_string(),
        ));
    }
    Ok(if listen_key.is_empty() {
        base_url.to_string()
    } else {
        format!("{base_url}?listenKey={listen_key}")
    })
}

fn extract_listen_key(data: &Value) -> Result<String> {
    data.get("listenKey")
        .and_then(Value::as_str)
        .filter(|value| !value.trim().is_empty())
        .map(ToString::to_string)
        .ok_or_else(|| DcexError::Decode("MEXC listen key missing.".to_string()))
}

fn normalize_channel(channel: &str) -> Result<String> {
    let channel = channel.trim();
    if channel.is_empty() {
        return Err(DcexError::InvalidInput(
            "MEXC private WebSocket channel must not be empty.".to_string(),
        ));
    }
    if !channel
        .chars()
        .all(|character| character.is_ascii_alphanumeric() || matches!(character, '@' | '.'))
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported MEXC private WebSocket channel: {channel}"
        )));
    }
    Ok(channel.to_string())
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
    fn extracts_listen_key() {
        let data = json!({"listenKey": "abc"});
        assert_eq!(extract_listen_key(&data).expect("listen key"), "abc");
        assert!(extract_listen_key(&json!({})).is_err());
    }

    #[test]
    fn builds_private_ws_url() {
        assert_eq!(
            private_ws_url("wss://wbs-api.mexc.com/ws/", "abc").expect("url"),
            "wss://wbs-api.mexc.com/ws?listenKey=abc"
        );
    }

    #[test]
    fn signs_listen_key_request_when_secret_is_available() {
        let ws = MexcPrivateWebSocket::with_urls_and_secret(
            "key".to_string(),
            Some("secret".to_string()),
            Duration::from_secs(10),
            "https://api.mexc.com",
            "wss://wbs-api.mexc.com/ws",
        )
        .expect("ws");
        let request = ws
            .listen_key_request(HttpMethod::Put, Some("listen-key"))
            .expect("request");

        assert!(request
            .query
            .iter()
            .any(|(key, value)| { key == "listenKey" && value == "listen-key" }));
        assert!(request
            .query
            .iter()
            .any(|(key, value)| { key == "timestamp" && !value.is_empty() }));
        assert!(request
            .query
            .iter()
            .any(|(key, value)| { key == "signature" && !value.is_empty() }));
    }
}
