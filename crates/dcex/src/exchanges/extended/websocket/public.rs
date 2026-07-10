use std::time::Duration;

use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::{
    normalize_candle_interval, normalize_candle_type, normalize_market, optional_market_path,
    stream_url, USER_AGENT, WS_URL,
};

pub struct ExtendedPublicWebSocket {
    base_url: String,
    timeout: Duration,
    connection: Option<WebSocketConnection>,
}

impl ExtendedPublicWebSocket {
    pub fn new(timeout: Duration) -> Result<Self> {
        Self::with_url(WS_URL.to_string(), timeout)
    }

    pub fn with_url(base_url: impl Into<String>, timeout: Duration) -> Result<Self> {
        let base_url = base_url.into();
        stream_url(&base_url, "orderbooks")?;
        Ok(Self {
            base_url,
            timeout,
            connection: None,
        })
    }

    pub fn is_connected(&self) -> bool {
        self.connection
            .as_ref()
            .is_some_and(WebSocketConnection::is_connected)
    }

    pub async fn close(&mut self) -> Result<()> {
        if let Some(mut connection) = self.connection.take() {
            connection.close().await?;
        }
        Ok(())
    }

    pub async fn ping(&mut self) -> Result<()> {
        self.connection_mut()?.send_ping(Vec::new()).await
    }

    pub async fn subscribe_orderbook(
        &mut self,
        market: Option<&str>,
        depth: Option<u8>,
    ) -> Result<()> {
        let mut path = optional_market_path("orderbooks", market)?;
        if let Some(depth) = depth {
            if depth != 1 {
                return Err(DcexError::InvalidInput(
                    "Extended order book depth must be 1 when specified.".to_string(),
                ));
            }
            path.push_str("?depth=1");
        }
        self.select_stream(path).await
    }

    pub async fn subscribe_trades(&mut self, market: Option<&str>) -> Result<()> {
        self.select_stream(optional_market_path("publicTrades", market)?)
            .await
    }

    pub async fn subscribe_funding(&mut self, market: Option<&str>) -> Result<()> {
        self.select_stream(optional_market_path("funding", market)?)
            .await
    }

    pub async fn subscribe_candles(
        &mut self,
        market: &str,
        candle_type: &str,
        interval: &str,
    ) -> Result<()> {
        let market = normalize_market(market)?;
        let candle_type = normalize_candle_type(candle_type)?;
        let interval = normalize_candle_interval(interval)?;
        self.select_stream(format!(
            "candles/{market}/{candle_type}?interval={interval}"
        ))
        .await
    }

    pub async fn subscribe_mark_price(&mut self, market: Option<&str>) -> Result<()> {
        self.select_stream(optional_market_path("prices/mark", market)?)
            .await
    }

    pub async fn subscribe_index_price(&mut self, market: Option<&str>) -> Result<()> {
        self.select_stream(optional_market_path("prices/index", market)?)
            .await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection_mut()?.recv_bytes().await
    }

    async fn select_stream(&mut self, path: String) -> Result<()> {
        let url = stream_url(&self.base_url, &path)?;
        if self
            .connection
            .as_ref()
            .is_some_and(|connection| connection.is_connected() && connection.config().url == url)
        {
            return Ok(());
        }
        self.close().await?;
        let mut connection = WebSocketConnection::new(WebSocketConfig::new(url, self.timeout)?);
        connection
            .connect_with_headers(vec![("User-Agent".to_string(), USER_AGENT.to_string())])
            .await?;
        self.connection = Some(connection);
        Ok(())
    }

    fn connection_mut(&mut self) -> Result<&mut WebSocketConnection> {
        self.connection.as_mut().ok_or_else(|| {
            DcexError::InvalidInput(
                "Extended public WebSocket has no stream; call subscribe_* first.".to_string(),
            )
        })
    }
}
