use std::time::Duration;

use serde_json::{json, Value};

use crate::http::HttpMethod;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::super::client::{KucoinClient, KucoinMarket};
use super::super::endpoints::{FUTURES_BASE_URL, SPOT_BASE_URL, WS_PUBLIC_TOKEN};
use super::{extract_bullet_token, normalize_symbol, normalize_topic, websocket_url};

pub struct KucoinPublicWebSocket {
    http_client: KucoinClient,
    market: KucoinMarket,
    timeout: Duration,
    connection: Option<WebSocketConnection>,
    next_request_id: u64,
}

impl KucoinPublicWebSocket {
    pub fn new(timeout: Duration) -> Result<Self> {
        Self::with_market_base_urls(
            timeout,
            SPOT_BASE_URL.to_string(),
            FUTURES_BASE_URL.to_string(),
            KucoinMarket::Spot,
        )
    }

    pub fn new_futures(timeout: Duration) -> Result<Self> {
        Self::with_market_base_urls(
            timeout,
            SPOT_BASE_URL.to_string(),
            FUTURES_BASE_URL.to_string(),
            KucoinMarket::Futures,
        )
    }

    pub fn with_base_urls(
        timeout: Duration,
        spot_http_base_url: String,
        futures_http_base_url: String,
    ) -> Result<Self> {
        Self::with_market_base_urls(
            timeout,
            spot_http_base_url,
            futures_http_base_url,
            KucoinMarket::Spot,
        )
    }

    pub fn with_market_base_urls(
        timeout: Duration,
        spot_http_base_url: String,
        futures_http_base_url: String,
        market: KucoinMarket,
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
            market,
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
                self.market,
                WS_PUBLIC_TOKEN,
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
        let futures = matches!(self.market, KucoinMarket::Futures);
        let symbol = normalize_symbol(product_symbol, futures)?;
        let topic = if futures {
            format!("/contractMarket/tickerV2:{symbol}")
        } else {
            format!("/market/ticker:{symbol}")
        };
        self.subscribe(&topic).await
    }

    pub async fn subscribe_trades(&mut self, product_symbol: &str) -> Result<String> {
        let futures = matches!(self.market, KucoinMarket::Futures);
        let symbol = normalize_symbol(product_symbol, futures)?;
        let topic = if futures {
            format!("/contractMarket/execution:{symbol}")
        } else {
            format!("/market/match:{symbol}")
        };
        self.subscribe(&topic).await
    }

    pub async fn subscribe_orderbook(&mut self, product_symbol: &str) -> Result<String> {
        let futures = matches!(self.market, KucoinMarket::Futures);
        let symbol = normalize_symbol(product_symbol, futures)?;
        let topic = if futures {
            format!("/contractMarket/level2:{symbol}")
        } else {
            format!("/market/level2:{symbol}")
        };
        self.subscribe(&topic).await
    }

    pub async fn subscribe_klines(
        &mut self,
        product_symbol: &str,
        interval: &str,
    ) -> Result<String> {
        let futures = matches!(self.market, KucoinMarket::Futures);
        let symbol = normalize_symbol(product_symbol, futures)?;
        let interval = normalize_interval(interval, futures)?;
        let topic = if futures {
            format!("/contractMarket/limitCandle:{symbol}_{interval}")
        } else {
            format!("/market/candles:{symbol}_{interval}")
        };
        self.subscribe(&topic).await
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

fn normalize_interval(interval: &str, futures: bool) -> Result<String> {
    let interval = interval.trim();
    let supported = if futures {
        matches!(
            interval,
            "1min"
                | "3min"
                | "5min"
                | "15min"
                | "30min"
                | "1hour"
                | "2hour"
                | "4hour"
                | "8hour"
                | "12hour"
                | "1day"
                | "1week"
                | "1month"
        )
    } else {
        matches!(
            interval,
            "1min"
                | "3min"
                | "15min"
                | "30min"
                | "1hour"
                | "2hour"
                | "4hour"
                | "6hour"
                | "8hour"
                | "12hour"
                | "1day"
                | "1week"
        )
    };
    if !supported {
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
        assert_eq!(normalize_interval("1min", false).expect("interval"), "1min");
        assert!(normalize_interval("5min", false).is_err());
        assert_eq!(
            normalize_interval("5min", true).expect("futures interval"),
            "5min"
        );
        assert!(normalize_interval("6hour", true).is_err());
        assert!(normalize_interval("1 min", false).is_err());
    }
}
