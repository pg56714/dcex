use std::time::Duration;

use serde_json::{json, Value};

use crate::http::HttpMethod;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::super::client::{KucoinClient, KucoinMarket};
use super::super::endpoints::{FUTURES_BASE_URL, SPOT_BASE_URL, SPOT_WS_PUBLIC_TOKEN};
use super::{extract_bullet_token, normalize_symbol, normalize_topic, websocket_url};

pub struct KucoinPublicWebSocket {
    http_client: KucoinClient,
    timeout: Duration,
    connection: Option<WebSocketConnection>,
    next_request_id: u64,
}

impl KucoinPublicWebSocket {
    pub fn new(timeout: Duration) -> Result<Self> {
        Self::with_base_urls(
            timeout,
            SPOT_BASE_URL.to_string(),
            FUTURES_BASE_URL.to_string(),
        )
    }

    pub fn with_base_urls(
        timeout: Duration,
        spot_http_base_url: String,
        futures_http_base_url: String,
    ) -> Result<Self> {
        Ok(Self {
            http_client: KucoinClient::with_base_urls(
                None,
                None,
                None,
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
                SPOT_WS_PUBLIC_TOKEN,
                Vec::new(),
                None,
                false,
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
        self.send_topic("subscribe", topic, false).await
    }

    pub async fn unsubscribe(&mut self, topic: &str) -> Result<String> {
        self.send_topic("unsubscribe", topic, false).await
    }

    pub async fn subscribe_ticker(&mut self, product_symbol: &str) -> Result<String> {
        let symbol = normalize_symbol(product_symbol, false)?;
        self.subscribe(&format!("/market/ticker:{symbol}")).await
    }

    pub async fn subscribe_trades(&mut self, product_symbol: &str) -> Result<String> {
        let symbol = normalize_symbol(product_symbol, false)?;
        self.subscribe(&format!("/market/match:{symbol}")).await
    }

    pub async fn subscribe_orderbook(&mut self, product_symbol: &str) -> Result<String> {
        let symbol = normalize_symbol(product_symbol, false)?;
        self.subscribe(&format!("/market/level2:{symbol}")).await
    }

    pub async fn subscribe_klines(
        &mut self,
        product_symbol: &str,
        interval: &str,
    ) -> Result<String> {
        let symbol = normalize_symbol(product_symbol, false)?;
        let interval = normalize_interval(interval)?;
        self.subscribe(&format!("/market/candles:{symbol}_{interval}"))
            .await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection_mut()?.recv_json().await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection_mut()?.recv_bytes().await
    }

    async fn send_topic(
        &mut self,
        message_type: &str,
        topic: &str,
        private_channel: bool,
    ) -> Result<String> {
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
                "privateChannel": private_channel,
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

fn normalize_interval(interval: &str) -> Result<String> {
    let interval = interval.trim();
    if interval.is_empty() {
        return Err(DcexError::InvalidInput(
            "KuCoin kline interval must not be empty.".to_string(),
        ));
    }
    if !interval
        .chars()
        .all(|character| character.is_ascii_alphanumeric())
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported KuCoin kline interval: {interval}"
        )));
    }
    Ok(interval.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn validates_interval() {
        assert_eq!(normalize_interval("1min").expect("interval"), "1min");
        assert!(normalize_interval("1 min").is_err());
    }
}
