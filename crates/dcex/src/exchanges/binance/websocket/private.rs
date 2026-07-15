use std::time::Duration;

use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::super::client::BinanceClient;
use super::super::endpoints::{FUTURES_BASE_URL, SPOT_BASE_URL};

const FUTURES_PRIVATE_WS_BASE_URL: &str = "wss://fstream.binance.com";

pub struct BinancePrivateWebSocket {
    http_client: BinanceClient,
    websocket_base_url: String,
    timeout: Duration,
    connection: Option<WebSocketConnection>,
    listen_key: Option<String>,
}

impl BinancePrivateWebSocket {
    pub fn new(api_key: String, api_secret: String, timeout: Duration) -> Result<Self> {
        Self::with_urls(
            api_key,
            api_secret,
            timeout,
            SPOT_BASE_URL.to_string(),
            FUTURES_BASE_URL.to_string(),
            FUTURES_PRIVATE_WS_BASE_URL.to_string(),
        )
    }

    pub fn with_urls(
        api_key: String,
        api_secret: String,
        timeout: Duration,
        spot_http_base_url: String,
        futures_http_base_url: String,
        websocket_base_url: String,
    ) -> Result<Self> {
        validate_credential("Binance API key", &api_key)?;
        validate_credential("Binance API secret", &api_secret)?;
        let http_client = BinanceClient::with_base_urls(
            Some(api_key),
            Some(api_secret),
            timeout,
            spot_http_base_url,
            futures_http_base_url,
        )?;
        Ok(Self {
            http_client,
            websocket_base_url: normalize_base_url(&websocket_base_url)?,
            timeout,
            connection: None,
            listen_key: None,
        })
    }

    pub fn listen_key(&self) -> Option<&str> {
        self.listen_key.as_deref()
    }

    pub fn is_connected(&self) -> bool {
        self.connection
            .as_ref()
            .is_some_and(WebSocketConnection::is_connected)
    }

    pub async fn connect(&mut self) -> Result<String> {
        if self.is_connected() {
            return self
                .listen_key
                .clone()
                .ok_or_else(|| DcexError::Runtime("missing Binance listen key.".to_string()));
        }
        let listen_key = self.create_listen_key().await?;
        self.connect_with_listen_key(listen_key.clone()).await?;
        Ok(listen_key)
    }

    pub async fn connect_with_listen_key(&mut self, listen_key: String) -> Result<()> {
        let listen_key = validate_listen_key(&listen_key)?;
        let url = private_stream_url(&self.websocket_base_url, &listen_key);
        let mut connection = WebSocketConnection::new(WebSocketConfig::new(url, self.timeout)?);
        connection.connect().await?;
        self.listen_key = Some(listen_key);
        self.connection = Some(connection);
        Ok(())
    }

    pub async fn create_listen_key(&self) -> Result<String> {
        let response = self.http_client.create_futures_listen_key().await?;
        extract_listen_key(&response)
    }

    pub async fn keep_alive(&self) -> Result<()> {
        let listen_key = self.listen_key.as_deref().ok_or_else(|| {
            DcexError::InvalidInput(
                "Binance listen key is not available; call connect first.".to_string(),
            )
        })?;
        self.http_client
            .keep_alive_futures_listen_key(listen_key)
            .await?;
        Ok(())
    }

    pub async fn close_listen_key(&mut self) -> Result<()> {
        if let Some(listen_key) = self.listen_key.take() {
            self.http_client
                .close_futures_listen_key(&listen_key)
                .await?;
        }
        Ok(())
    }

    pub async fn close(&mut self) -> Result<()> {
        let close_connection_result = if let Some(connection) = &mut self.connection {
            connection.close().await
        } else {
            Ok(())
        };
        self.connection = None;
        let close_listen_key_result = self.close_listen_key().await;
        close_connection_result.and(close_listen_key_result)
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection_mut()?.recv_json().await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection_mut()?.recv_bytes().await
    }

    fn connection_mut(&mut self) -> Result<&mut WebSocketConnection> {
        self.connection.as_mut().ok_or_else(|| {
            DcexError::InvalidInput("WebSocket is not connected; call connect first.".to_string())
        })
    }
}

fn extract_listen_key(response: &ValidatedResponse) -> Result<String> {
    response
        .data
        .get("listenKey")
        .and_then(Value::as_str)
        .map(ToString::to_string)
        .filter(|value| !value.trim().is_empty())
        .ok_or_else(|| {
            DcexError::Decode(format!(
                "Binance listen key response did not include listenKey: {:?}",
                response.data
            ))
        })
}

fn private_stream_url(base_url: &str, listen_key: &str) -> String {
    format!("{}/ws/{}", normalize_base_url_lossy(base_url), listen_key)
}

fn normalize_base_url(base_url: &str) -> Result<String> {
    let normalized = normalize_base_url_lossy(base_url);
    if normalized.is_empty() {
        return Err(DcexError::InvalidInput(
            "Binance private WebSocket base URL must not be empty.".to_string(),
        ));
    }
    Ok(normalized)
}

fn normalize_base_url_lossy(base_url: &str) -> String {
    base_url.trim().trim_end_matches('/').to_string()
}

fn validate_credential(label: &str, value: &str) -> Result<()> {
    if value.trim().is_empty() {
        return Err(DcexError::InvalidInput(format!(
            "{label} must not be empty."
        )));
    }
    Ok(())
}

fn validate_listen_key(listen_key: &str) -> Result<String> {
    let listen_key = listen_key.trim();
    if listen_key.is_empty() {
        return Err(DcexError::InvalidInput(
            "Binance listen key must not be empty.".to_string(),
        ));
    }
    if listen_key.contains('/') || listen_key.contains('\\') {
        return Err(DcexError::InvalidInput(
            "Binance listen key must not contain path separators.".to_string(),
        ));
    }
    Ok(listen_key.to_string())
}

#[cfg(test)]
mod tests {
    use std::collections::BTreeMap;

    use serde_json::json;

    use super::*;

    #[test]
    fn extracts_listen_key() {
        let response = ValidatedResponse {
            status: 200,
            headers: BTreeMap::new(),
            data: json!({"listenKey": "abc123"}),
        };
        assert_eq!(extract_listen_key(&response).expect("key"), "abc123");
    }

    #[test]
    fn rejects_missing_listen_key() {
        let response = ValidatedResponse {
            status: 200,
            headers: BTreeMap::new(),
            data: json!({}),
        };
        assert!(extract_listen_key(&response).is_err());
    }

    #[test]
    fn builds_private_stream_url() {
        assert_eq!(
            private_stream_url("wss://fstream.binance.com/", "listen-key"),
            "wss://fstream.binance.com/ws/listen-key"
        );
    }

    #[test]
    fn rejects_invalid_listen_key() {
        assert!(validate_listen_key("").is_err());
        assert!(validate_listen_key("bad/key").is_err());
    }
}
