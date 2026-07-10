use std::time::Duration;

use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::{stream_url, USER_AGENT, WS_URL};

pub struct ExtendedPrivateWebSocket {
    connection: WebSocketConnection,
    api_key: String,
}

impl ExtendedPrivateWebSocket {
    pub fn new(api_key: String, timeout: Duration) -> Result<Self> {
        Self::with_url(api_key, WS_URL.to_string(), timeout)
    }

    pub fn with_url(
        api_key: String,
        base_url: impl Into<String>,
        timeout: Duration,
    ) -> Result<Self> {
        if api_key.trim().is_empty() {
            return Err(DcexError::InvalidInput(
                "Extended API key must not be empty.".to_string(),
            ));
        }
        let url = stream_url(&base_url.into(), "account")?;
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            api_key,
        })
    }

    pub fn is_connected(&self) -> bool {
        self.connection.is_connected()
    }

    pub async fn connect(&mut self) -> Result<()> {
        self.connection
            .connect_with_headers(vec![
                ("User-Agent".to_string(), USER_AGENT.to_string()),
                ("X-Api-Key".to_string(), self.api_key.clone()),
            ])
            .await
    }

    pub async fn subscribe_account(&mut self) -> Result<()> {
        self.connect().await
    }

    pub async fn close(&mut self) -> Result<()> {
        self.connection.close().await
    }

    pub async fn ping(&mut self) -> Result<()> {
        self.connection.send_ping(Vec::new()).await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rejects_empty_api_key() {
        assert!(ExtendedPrivateWebSocket::new("".to_string(), Duration::from_secs(1)).is_err());
    }
}
