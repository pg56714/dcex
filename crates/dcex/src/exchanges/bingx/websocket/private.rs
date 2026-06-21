use std::time::Duration;

use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::super::client::BingxClient;
use super::super::endpoints::BASE_URL;
use super::{decode_event, is_application_ping, normalize_data_type, validate_credential};

const WS_URL: &str = "wss://open-api-ws.bingx.com/market";

pub struct BingxPrivateWebSocket {
    http_client: BingxClient,
    websocket_base_url: String,
    timeout: Duration,
    connection: Option<WebSocketConnection>,
    listen_key: Option<String>,
    next_request_id: u64,
}

impl BingxPrivateWebSocket {
    pub fn new(api_key: String, api_secret: String, timeout: Duration) -> Result<Self> {
        Self::with_urls(
            api_key,
            api_secret,
            timeout,
            BASE_URL.to_string(),
            WS_URL.to_string(),
        )
    }

    pub fn with_urls(
        api_key: String,
        api_secret: String,
        timeout: Duration,
        http_base_url: String,
        websocket_base_url: String,
    ) -> Result<Self> {
        validate_credential("BingX API key", &api_key)?;
        validate_credential("BingX API secret", &api_secret)?;
        let http_client =
            BingxClient::with_base_url(Some(api_key), Some(api_secret), timeout, http_base_url)?;
        Ok(Self {
            http_client,
            websocket_base_url: normalize_base_url(&websocket_base_url)?,
            timeout,
            connection: None,
            listen_key: None,
            next_request_id: 1,
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
                .ok_or_else(|| DcexError::Runtime("missing BingX listen key.".to_string()));
        }
        let listen_key = self.create_listen_key().await?;
        self.connect_with_listen_key(listen_key.clone()).await?;
        Ok(listen_key)
    }

    pub async fn connect_with_listen_key(&mut self, listen_key: String) -> Result<()> {
        let listen_key = validate_listen_key(&listen_key)?;
        let url = private_stream_url(&self.websocket_base_url, &listen_key);
        let mut connection = WebSocketConnection::new(WebSocketConfig::new(url, self.timeout)?);
        connection
            .connect_with_headers(vec![("Accept-Encoding".to_string(), "gzip".to_string())])
            .await?;
        self.listen_key = Some(listen_key);
        self.connection = Some(connection);
        Ok(())
    }

    pub async fn create_listen_key(&self) -> Result<String> {
        let response = self
            .http_client
            .private_request("get_listen_key", Vec::new())
            .await?;
        extract_listen_key(&response)
    }

    pub async fn keep_alive(&self) -> Result<String> {
        let listen_key = self.listen_key.as_deref().ok_or_else(|| {
            DcexError::InvalidInput(
                "BingX listen key is not available; call connect first.".to_string(),
            )
        })?;
        self.http_client
            .private_request(
                "keep_alive_listen_key",
                vec![("listen_key".to_string(), listen_key.to_string())],
            )
            .await?;
        Ok(listen_key.to_string())
    }

    pub async fn close(&mut self) -> Result<()> {
        if let Some(connection) = &mut self.connection {
            connection.close().await?;
        }
        self.connection = None;
        self.listen_key = None;
        Ok(())
    }

    pub async fn ping(&mut self) -> Result<()> {
        self.connection_mut()?.send_text("Ping").await
    }

    pub async fn subscribe(&mut self, data_type: &str) -> Result<String> {
        self.send_subscription("sub", data_type).await
    }

    pub async fn unsubscribe(&mut self, data_type: &str) -> Result<String> {
        self.send_subscription("unsub", data_type).await
    }

    pub async fn subscribe_orders(&mut self) -> Result<String> {
        self.subscribe("spot.executionReport").await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        loop {
            let payload = self.connection_mut()?.recv_bytes().await?;
            let event = decode_event(payload)?;
            if is_application_ping(&event) {
                self.connection_mut()?.send_text("Pong").await?;
                continue;
            }
            return Ok(event);
        }
    }

    async fn send_subscription(&mut self, req_type: &str, data_type: &str) -> Result<String> {
        let req_type = match req_type {
            "sub" | "unsub" => req_type,
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported BingX WebSocket reqType: {req_type}"
                )));
            }
        };
        let id = self.next_id();
        let data_type = normalize_data_type(data_type)?;
        self.connection_mut()?
            .send_json(&serde_json::json!({
                "id": id,
                "reqType": req_type,
                "dataType": data_type,
            }))
            .await?;
        Ok(id)
    }

    fn connection_mut(&mut self) -> Result<&mut WebSocketConnection> {
        self.connection.as_mut().ok_or_else(|| {
            DcexError::InvalidInput("WebSocket is not connected; call connect first.".to_string())
        })
    }

    fn next_id(&mut self) -> String {
        let id = self.next_request_id;
        self.next_request_id = self.next_request_id.saturating_add(1).max(1);
        format!("dcex-{id}")
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
                "BingX listen key response did not include listenKey: {:?}",
                response.data
            ))
        })
}

fn private_stream_url(base_url: &str, listen_key: &str) -> String {
    format!(
        "{}?listenKey={}",
        normalize_base_url_lossy(base_url),
        listen_key
    )
}

fn normalize_base_url(base_url: &str) -> Result<String> {
    let normalized = normalize_base_url_lossy(base_url);
    if normalized.is_empty() {
        return Err(DcexError::InvalidInput(
            "BingX private WebSocket base URL must not be empty.".to_string(),
        ));
    }
    Ok(normalized)
}

fn normalize_base_url_lossy(base_url: &str) -> String {
    base_url.trim().trim_end_matches('/').to_string()
}

fn validate_listen_key(listen_key: &str) -> Result<String> {
    let listen_key = listen_key.trim();
    if listen_key.is_empty() {
        return Err(DcexError::InvalidInput(
            "BingX listen key must not be empty.".to_string(),
        ));
    }
    if listen_key.contains('/') || listen_key.contains('\\') {
        return Err(DcexError::InvalidInput(
            "BingX listen key must not contain path separators.".to_string(),
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
        assert!(extract_listen_key(&ValidatedResponse {
            status: 200,
            headers: BTreeMap::new(),
            data: json!({}),
        })
        .is_err());
    }

    #[test]
    fn builds_private_stream_url() {
        assert_eq!(
            private_stream_url("wss://open-api-ws.bingx.com/market/", "listen-key"),
            "wss://open-api-ws.bingx.com/market?listenKey=listen-key"
        );
    }

    #[test]
    fn rejects_invalid_listen_key() {
        assert!(validate_listen_key("").is_err());
        assert!(validate_listen_key("bad/key").is_err());
    }
}
