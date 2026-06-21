use std::time::Duration;

use futures_util::{SinkExt, StreamExt};
use serde_json::Value;
use tokio::net::TcpStream;
use tokio::time::timeout;
use tokio_tungstenite::tungstenite::protocol::Message;
use tokio_tungstenite::{connect_async, MaybeTlsStream, WebSocketStream};

use crate::{DcexError, Result};

type TungsteniteStream = WebSocketStream<MaybeTlsStream<TcpStream>>;

#[derive(Clone, Debug, PartialEq)]
pub struct WebSocketConfig {
    pub url: String,
    pub timeout: Duration,
}

impl WebSocketConfig {
    pub fn new(url: impl Into<String>, timeout: Duration) -> Result<Self> {
        let url = url.into();
        if url.trim().is_empty() {
            return Err(DcexError::InvalidInput(
                "WebSocket URL must not be empty.".to_string(),
            ));
        }
        if timeout.is_zero() {
            return Err(DcexError::InvalidInput(
                "WebSocket timeout must be greater than zero.".to_string(),
            ));
        }
        Ok(Self { url, timeout })
    }
}

pub struct WebSocketConnection {
    config: WebSocketConfig,
    stream: Option<TungsteniteStream>,
}

impl WebSocketConnection {
    pub fn new(config: WebSocketConfig) -> Self {
        Self {
            config,
            stream: None,
        }
    }

    pub fn config(&self) -> &WebSocketConfig {
        &self.config
    }

    pub fn is_connected(&self) -> bool {
        self.stream.is_some()
    }

    pub async fn connect(&mut self) -> Result<()> {
        if self.stream.is_some() {
            return Ok(());
        }
        let url = self.config.url.clone();
        let connect_result = timeout(self.config.timeout, connect_async(&url))
            .await
            .map_err(|_| DcexError::Transport(format!("WebSocket connect timed out: {url}")))?;
        let (stream, _) = connect_result
            .map_err(|error| DcexError::Transport(format!("WebSocket connect failed: {error}")))?;
        self.stream = Some(stream);
        Ok(())
    }

    pub async fn send_json(&mut self, value: &Value) -> Result<()> {
        let payload = serde_json::to_string(value).map_err(|error| {
            DcexError::Decode(format!("failed to encode WebSocket JSON: {error}"))
        })?;
        self.send_text(payload).await
    }

    pub async fn send_text(&mut self, payload: impl Into<String>) -> Result<()> {
        let timeout_duration = self.config.timeout;
        let stream = self.stream_mut()?;
        timeout(
            timeout_duration,
            stream.send(Message::Text(payload.into().into())),
        )
        .await
        .map_err(|_| DcexError::Transport("WebSocket send timed out.".to_string()))?
        .map_err(|error| DcexError::Transport(format!("WebSocket send failed: {error}")))
    }

    pub async fn recv_json(&mut self) -> Result<Value> {
        let payload = self.recv_text().await?;
        serde_json::from_str(&payload)
            .map_err(|error| DcexError::Decode(format!("failed to decode WebSocket JSON: {error}")))
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        loop {
            let timeout_duration = self.config.timeout;
            let stream = self.stream_mut()?;
            let message = timeout(timeout_duration, stream.next())
                .await
                .map_err(|_| DcexError::Transport("WebSocket receive timed out.".to_string()))?
                .ok_or_else(|| DcexError::Transport("WebSocket connection closed.".to_string()))?
                .map_err(|error| {
                    DcexError::Transport(format!("WebSocket receive failed: {error}"))
                })?;

            match message {
                Message::Text(payload) => return Ok(payload.to_string().into_bytes()),
                Message::Binary(payload) => return Ok(payload.to_vec()),
                Message::Ping(payload) => {
                    let stream = self.stream_mut()?;
                    timeout(timeout_duration, stream.send(Message::Pong(payload)))
                        .await
                        .map_err(|_| {
                            DcexError::Transport("WebSocket pong send timed out.".to_string())
                        })?
                        .map_err(|error| {
                            DcexError::Transport(format!("WebSocket pong send failed: {error}"))
                        })?;
                }
                Message::Pong(_) | Message::Frame(_) => {}
                Message::Close(_) => {
                    self.stream = None;
                    return Err(DcexError::Transport(
                        "WebSocket connection closed.".to_string(),
                    ));
                }
            }
        }
    }

    pub async fn recv_text(&mut self) -> Result<String> {
        loop {
            let timeout_duration = self.config.timeout;
            let stream = self.stream_mut()?;
            let message = timeout(timeout_duration, stream.next())
                .await
                .map_err(|_| DcexError::Transport("WebSocket receive timed out.".to_string()))?
                .ok_or_else(|| DcexError::Transport("WebSocket connection closed.".to_string()))?
                .map_err(|error| {
                    DcexError::Transport(format!("WebSocket receive failed: {error}"))
                })?;

            match message {
                Message::Text(payload) => return Ok(payload.to_string()),
                Message::Binary(payload) => {
                    return String::from_utf8(payload.to_vec()).map_err(|error| {
                        DcexError::Decode(format!(
                            "failed to decode WebSocket binary text: {error}"
                        ))
                    });
                }
                Message::Ping(payload) => {
                    let stream = self.stream_mut()?;
                    timeout(timeout_duration, stream.send(Message::Pong(payload)))
                        .await
                        .map_err(|_| {
                            DcexError::Transport("WebSocket pong send timed out.".to_string())
                        })?
                        .map_err(|error| {
                            DcexError::Transport(format!("WebSocket pong send failed: {error}"))
                        })?;
                }
                Message::Pong(_) | Message::Frame(_) => {}
                Message::Close(_) => {
                    self.stream = None;
                    return Err(DcexError::Transport(
                        "WebSocket connection closed.".to_string(),
                    ));
                }
            }
        }
    }

    pub async fn close(&mut self) -> Result<()> {
        if let Some(mut stream) = self.stream.take() {
            timeout(self.config.timeout, stream.close(None))
                .await
                .map_err(|_| DcexError::Transport("WebSocket close timed out.".to_string()))?
                .map_err(|error| {
                    DcexError::Transport(format!("WebSocket close failed: {error}"))
                })?;
        }
        Ok(())
    }

    fn stream_mut(&mut self) -> Result<&mut TungsteniteStream> {
        self.stream.as_mut().ok_or_else(|| {
            DcexError::InvalidInput("WebSocket is not connected; call connect first.".to_string())
        })
    }
}
