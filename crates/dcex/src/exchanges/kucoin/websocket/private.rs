use std::time::Duration;

use serde_json::{json, Value};

use crate::http::HttpMethod;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::super::client::{KucoinClient, KucoinMarket};
use super::super::endpoints::{FUTURES_BASE_URL, SPOT_BASE_URL, SPOT_WS_PRIVATE_TOKEN};
use super::{extract_bullet_token, normalize_topic, validate_credential, websocket_url};

pub struct KucoinPrivateWebSocket {
    http_client: KucoinClient,
    timeout: Duration,
    connection: Option<WebSocketConnection>,
    next_request_id: u64,
}

impl KucoinPrivateWebSocket {
    pub fn new(
        api_key: String,
        api_secret: String,
        passphrase: String,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_base_urls(
            api_key,
            api_secret,
            passphrase,
            timeout,
            SPOT_BASE_URL.to_string(),
            FUTURES_BASE_URL.to_string(),
        )
    }

    pub fn with_base_urls(
        api_key: String,
        api_secret: String,
        passphrase: String,
        timeout: Duration,
        spot_http_base_url: String,
        futures_http_base_url: String,
    ) -> Result<Self> {
        validate_credential("KuCoin API key", &api_key)?;
        validate_credential("KuCoin API secret", &api_secret)?;
        validate_credential("KuCoin API passphrase", &passphrase)?;
        Ok(Self {
            http_client: KucoinClient::with_base_urls(
                Some(api_key),
                Some(api_secret),
                Some(passphrase),
                timeout,
                spot_http_base_url,
                futures_http_base_url,
            )?,
            timeout,
            connection: None,
            next_request_id: 1,
        })
    }

    pub fn is_connected(&self) -> bool {
        self.connection
            .as_ref()
            .is_some_and(WebSocketConnection::is_connected)
    }

    pub async fn connect(&mut self) -> Result<()> {
        if self.is_connected() {
            return Ok(());
        }
        let bullet = self.fetch_bullet_token().await?;
        let connect_id = self.next_id();
        let url = websocket_url(&bullet.endpoint, &bullet.token, &connect_id)?;
        let mut connection = WebSocketConnection::new(WebSocketConfig::new(url, self.timeout)?);
        connection.connect().await?;
        self.connection = Some(connection);
        Ok(())
    }

    async fn fetch_bullet_token(&self) -> Result<super::KucoinBulletToken> {
        let response = self
            .http_client
            .request(
                HttpMethod::Post,
                KucoinMarket::Spot,
                SPOT_WS_PRIVATE_TOKEN,
                Vec::new(),
                None,
                true,
            )
            .await?;
        extract_bullet_token(&response.data)
    }

    pub async fn close(&mut self) -> Result<()> {
        if let Some(connection) = &mut self.connection {
            connection.close().await?;
        }
        self.connection = None;
        Ok(())
    }

    pub async fn ping(&mut self) -> Result<String> {
        let id = self.next_id();
        self.connection_mut()?
            .send_json(&json!({
                "id": id,
                "type": "ping",
            }))
            .await?;
        Ok(id)
    }

    pub async fn subscribe(&mut self, topic: &str) -> Result<String> {
        self.send_topic("subscribe", topic).await
    }

    pub async fn unsubscribe(&mut self, topic: &str) -> Result<String> {
        self.send_topic("unsubscribe", topic).await
    }

    pub async fn subscribe_orders(&mut self) -> Result<String> {
        self.subscribe("/spotMarket/tradeOrders").await
    }

    pub async fn subscribe_balances(&mut self) -> Result<String> {
        self.subscribe("/account/balance").await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection_mut()?.recv_json().await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection_mut()?.recv_bytes().await
    }

    async fn send_topic(&mut self, message_type: &str, topic: &str) -> Result<String> {
        let message_type = match message_type {
            "subscribe" | "unsubscribe" => message_type,
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported KuCoin WebSocket message type: {message_type}"
                )));
            }
        };
        let id = self.next_id();
        let topic = normalize_topic(topic)?;
        self.connection_mut()?
            .send_json(&json!({
                "id": id,
                "type": message_type,
                "topic": topic,
                "privateChannel": true,
                "response": true,
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
