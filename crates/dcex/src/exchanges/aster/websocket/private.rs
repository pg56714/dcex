use std::time::Duration;

use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::super::{AsterClient, AsterMarket};

const FUTURES_PRIVATE_WS_BASE_URL: &str = "wss://fstream.asterdex.com";
const SPOT_PRIVATE_WS_BASE_URL: &str = "wss://sstream.asterdex.com";

pub struct AsterPrivateWebSocket {
    http_client: AsterClient,
    market: AsterMarket,
    websocket_base_url: String,
    timeout: Duration,
    connection: Option<WebSocketConnection>,
    listen_key: Option<String>,
}

impl AsterPrivateWebSocket {
    pub fn new(
        user_address: Option<String>,
        signer_address: String,
        private_key: String,
        market: AsterMarket,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_urls(
            user_address,
            signer_address,
            private_key,
            market,
            timeout,
            super::super::endpoints::SPOT_BASE_URL.to_string(),
            super::super::endpoints::FUTURES_BASE_URL.to_string(),
            private_ws_base_url(market).to_string(),
        )
    }

    pub fn with_urls(
        user_address: Option<String>,
        signer_address: String,
        private_key: String,
        market: AsterMarket,
        timeout: Duration,
        spot_http_base_url: String,
        futures_http_base_url: String,
        websocket_base_url: String,
    ) -> Result<Self> {
        validate_credential("Aster signer address", &signer_address)?;
        validate_credential("Aster private key", &private_key)?;
        if market == AsterMarket::Futures {
            validate_optional_credential("Aster user address", user_address.as_deref())?;
        }
        let http_client = AsterClient::with_base_urls(
            user_address,
            Some(signer_address),
            Some(private_key),
            timeout,
            spot_http_base_url,
            futures_http_base_url,
        )?;
        Ok(Self {
            http_client,
            market,
            websocket_base_url: normalize_base_url(&websocket_base_url)?,
            timeout,
            connection: None,
            listen_key: None,
        })
    }

    pub fn market(&self) -> AsterMarket {
        self.market
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
                .ok_or_else(|| DcexError::Runtime("missing Aster listen key.".to_string()));
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
        let response = match self.market {
            AsterMarket::Futures => self.http_client.create_futures_listen_key().await?,
            AsterMarket::Spot => self.http_client.create_spot_listen_key().await?,
        };
        extract_listen_key(&response)
    }

    pub async fn keep_alive(&self) -> Result<()> {
        let listen_key = self.listen_key.as_deref().ok_or_else(|| {
            DcexError::InvalidInput(
                "Aster listen key is not available; call connect first.".to_string(),
            )
        })?;
        match self.market {
            AsterMarket::Futures => {
                self.http_client.keep_alive_futures_listen_key().await?;
            }
            AsterMarket::Spot => {
                self.http_client
                    .keep_alive_spot_listen_key(listen_key)
                    .await?;
            }
        }
        Ok(())
    }

    pub async fn close_listen_key(&mut self) -> Result<()> {
        if let Some(listen_key) = self.listen_key.take() {
            match self.market {
                AsterMarket::Futures => {
                    self.http_client.close_futures_listen_key().await?;
                }
                AsterMarket::Spot => {
                    self.http_client.close_spot_listen_key(&listen_key).await?;
                }
            }
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
                "Aster listen key response did not include listenKey: {:?}",
                response.data
            ))
        })
}

fn private_ws_base_url(market: AsterMarket) -> &'static str {
    match market {
        AsterMarket::Futures => FUTURES_PRIVATE_WS_BASE_URL,
        AsterMarket::Spot => SPOT_PRIVATE_WS_BASE_URL,
    }
}

fn private_stream_url(base_url: &str, listen_key: &str) -> String {
    format!("{}/ws/{}", normalize_base_url_lossy(base_url), listen_key)
}

fn normalize_base_url(base_url: &str) -> Result<String> {
    let normalized = normalize_base_url_lossy(base_url);
    if normalized.is_empty() {
        return Err(DcexError::InvalidInput(
            "Aster private WebSocket base URL must not be empty.".to_string(),
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

fn validate_optional_credential(label: &str, value: Option<&str>) -> Result<()> {
    match value {
        Some(value) => validate_credential(label, value),
        None => Err(DcexError::InvalidInput(format!(
            "{label} is required for Aster futures private WebSocket streams."
        ))),
    }
}

fn validate_listen_key(listen_key: &str) -> Result<String> {
    let listen_key = listen_key.trim();
    if listen_key.is_empty() {
        return Err(DcexError::InvalidInput(
            "Aster listen key must not be empty.".to_string(),
        ));
    }
    if listen_key.contains('/') || listen_key.contains('\\') {
        return Err(DcexError::InvalidInput(
            "Aster listen key must not contain path separators.".to_string(),
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
            private_stream_url("wss://fstream.asterdex.com/", "listen-key"),
            "wss://fstream.asterdex.com/ws/listen-key"
        );
    }

    #[test]
    fn rejects_invalid_listen_key() {
        assert!(validate_listen_key("").is_err());
        assert!(validate_listen_key("bad/key").is_err());
    }
}
