//! Kraken Derivatives public and signed-challenge account streams.
use crate::crypto::{hmac_sha512_base64, sha256};
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};
use base64::Engine;
use serde_json::{Value, json};
use std::collections::VecDeque;
use std::time::Duration;

pub struct KrakenFuturesWebSocket {
    product_table: Option<std::sync::Arc<crate::product_table::ProductTable>>,
    connection: WebSocketConnection,
    credentials: Option<(String, Vec<u8>)>,
    challenge: Option<(String, String)>,
    pending: VecDeque<Vec<u8>>,
    timeout: Duration,
}

impl KrakenFuturesWebSocket {
    fn exchange_symbol(&self, symbol: &str) -> Result<String> {
        if let Some(table) = &self.product_table {
            return Ok(table
                .resolve_symbol_in("kraken", symbol, |row| {
                    matches!(row.product_type.as_str(), "swap" | "futures")
                })?
                .exchange_symbol
                .clone());
        }
        normalize_product(symbol)
    }

    pub fn set_product_table(&mut self, table: crate::product_table::ProductTable) {
        self.product_table = Some(std::sync::Arc::new(table));
    }

    pub fn with_product_table(mut self, table: crate::product_table::ProductTable) -> Self {
        self.set_product_table(table);
        self
    }

    pub fn new(timeout: Duration) -> Result<Self> {
        Self::with_url("wss://futures.kraken.com/ws/v1", timeout)
    }
    pub fn with_url(url: impl Into<String>, timeout: Duration) -> Result<Self> {
        Ok(Self {
            product_table: None,
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            credentials: None,
            challenge: None,
            pending: VecDeque::new(),
            timeout,
        })
    }
    pub fn with_credentials(mut self, api_key: String, api_secret: String) -> Result<Self> {
        if api_key.trim().is_empty() {
            return Err(invalid("API key is empty"));
        }
        let secret = base64::engine::general_purpose::STANDARD
            .decode(api_secret)
            .map_err(|_| invalid("API secret must be Base64"))?;
        if secret.is_empty() {
            return Err(invalid("API secret is empty"));
        }
        self.credentials = Some((api_key, secret));
        Ok(self)
    }
    pub fn is_connected(&self) -> bool {
        self.connection.is_connected()
    }
    pub async fn connect(&mut self) -> Result<()> {
        self.challenge = None;
        self.pending.clear();
        self.connection.connect().await?;
        if let Some((key, secret)) = &self.credentials {
            let result = tokio::time::timeout(self.timeout, async {
                self.connection
                    .send_json(&json!({"event":"challenge","api_key":key}))
                    .await?;
                loop {
                    let raw = self.connection.recv_bytes().await?;
                    let data: Value = serde_json::from_slice(&raw)
                        .map_err(|e| DcexError::Decode(e.to_string()))?;
                    if data["event"] == "challenge" {
                        let challenge = data["message"]
                            .as_str()
                            .filter(|v| !v.is_empty())
                            .ok_or_else(|| invalid("empty challenge"))?;
                        let signature = hmac_sha512_base64(secret, &sha256(challenge.as_bytes()))?;
                        return Ok((challenge.to_string(), signature));
                    }
                    if data["event"] == "error" {
                        return Err(invalid("challenge request rejected"));
                    }
                    if self.pending.len() >= 100 {
                        return Err(invalid("too many messages before challenge"));
                    }
                    self.pending.push_back(raw);
                }
            })
            .await
            .map_err(|_| invalid("challenge timed out"))
            .and_then(|v| v);
            match result {
                Ok(challenge) => self.challenge = Some(challenge),
                Err(error) => {
                    let _ = self.connection.close().await;
                    self.pending.clear();
                    return Err(error);
                }
            }
        }
        Ok(())
    }
    pub async fn close(&mut self) -> Result<()> {
        self.challenge = None;
        self.pending.clear();
        self.connection.close().await
    }
    /// Send at least once per 60 seconds while maintaining a connection.
    pub async fn ping(&mut self) -> Result<()> {
        self.connection.send_ping(Vec::new()).await
    }
    pub async fn recv(&mut self) -> Result<Vec<u8>> {
        if let Some(raw) = self.pending.pop_front() {
            return Ok(raw);
        }
        self.connection.recv_bytes().await
    }
    pub async fn subscribe(&mut self, feed: &str, product_ids: Option<Vec<String>>) -> Result<()> {
        self.subscription(true, feed, product_ids).await
    }
    pub async fn unsubscribe(
        &mut self,
        feed: &str,
        product_ids: Option<Vec<String>>,
    ) -> Result<()> {
        self.subscription(false, feed, product_ids).await
    }
    async fn subscription(
        &mut self,
        subscribe: bool,
        feed: &str,
        product_ids: Option<Vec<String>>,
    ) -> Result<()> {
        let public = matches!(
            feed,
            "book" | "ticker" | "ticker_lite" | "trade" | "heartbeat"
        );
        if !public
            && !matches!(
                feed,
                "fills"
                    | "open_orders"
                    | "open_orders_verbose"
                    | "open_position"
                    | "balances"
                    | "account_log"
                    | "notifications"
            )
        {
            return Err(invalid("unsupported feed"));
        }
        let accepts_products =
            matches!(feed, "book" | "ticker" | "ticker_lite" | "trade" | "fills");
        if product_ids.is_some() && !accepts_products {
            return Err(invalid("this feed does not accept product_ids"));
        }
        let mut request =
            json!({"event":if subscribe {"subscribe"} else {"unsubscribe"},"feed":feed});
        if let Some(products) = product_ids {
            if products.is_empty() {
                return Err(invalid("product_ids cannot be empty"));
            }
            let products = products
                .iter()
                .map(|p| self.exchange_symbol(p))
                .collect::<Result<Vec<_>>>()?;
            request["product_ids"] = json!(products);
        } else if public && feed != "heartbeat" {
            return Err(invalid("public market feed requires product_ids"));
        }
        if !public {
            let (key, _) = self
                .credentials
                .as_ref()
                .ok_or_else(|| invalid("private feed requires credentials"))?;
            let (original, signed) = self
                .challenge
                .as_ref()
                .ok_or_else(|| invalid("connect before subscribing to private feeds"))?;
            request["api_key"] = key.clone().into();
            request["original_challenge"] = original.clone().into();
            request["signed_challenge"] = signed.clone().into();
        }
        self.connection.send_json(&request).await
    }
}

fn normalize_product(product: &str) -> Result<String> {
    let parts = product.split('-').collect::<Vec<_>>();
    let value = if parts.len() == 3 && parts[2] == "SWAP" {
        format!(
            "PF_{}{}",
            if parts[0] == "BTC" { "XBT" } else { parts[0] },
            parts[1]
        )
    } else {
        product.to_string()
    };
    if !(value.starts_with("PF_")
        || value.starts_with("PI_")
        || value.starts_with("FI_")
        || value.starts_with("FF_"))
        || !value
            .bytes()
            .all(|c| c.is_ascii_uppercase() || c.is_ascii_digit() || c == b'_')
    {
        return Err(invalid(
            "use a native derivatives symbol or BASE-QUOTE-SWAP",
        ));
    }
    Ok(value)
}
fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(format!("Kraken futures WebSocket: {message}"))
}
