use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};
use serde_json::{Value, json};
use std::time::Duration;

/// Spot WebSocket V1, preserving its event/subscription protocol and array events.
/// Obtain a private session token with the REST GetWebSocketsToken endpoint.
pub struct KrakenV1WebSocket {
    connection: WebSocketConnection,
    token: Option<String>,
}

impl KrakenV1WebSocket {
    pub fn new(token: Option<String>, url: Option<String>, timeout: Duration) -> Result<Self> {
        if token.as_ref().is_some_and(|t| t.trim().is_empty()) {
            return Err(DcexError::InvalidInput(
                "Kraken WS token must not be empty.".into(),
            ));
        }
        let default = if token.is_some() {
            "wss://ws-auth.kraken.com/"
        } else {
            "wss://ws.kraken.com/"
        };
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(
                url.unwrap_or_else(|| default.into()),
                timeout,
            )?),
            token,
        })
    }
    pub fn url(&self) -> &str {
        &self.connection.config().url
    }
    pub fn is_connected(&self) -> bool {
        self.connection.is_connected()
    }
    pub async fn connect(&mut self) -> Result<()> {
        self.connection.connect().await
    }
    pub async fn close(&mut self) -> Result<()> {
        self.connection.close().await
    }
    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }

    /// Send the documented V1 request shape. Read and inspect the matching status
    /// event with `recv_bytes`; a successful send does not imply order acceptance.
    /// Account-wide cancel and its countdown require `all_symbols=true`.
    pub async fn send_message(&mut self, mut message: Value, all_symbols: bool) -> Result<()> {
        let obj = message
            .as_object_mut()
            .ok_or_else(|| invalid("Request must be an object."))?;
        let event = obj
            .get("event")
            .and_then(Value::as_str)
            .unwrap_or("")
            .to_string();
        let trading = matches!(
            event.as_str(),
            "addOrder"
                | "amendOrder"
                | "editOrder"
                | "cancelOrder"
                | "cancelAll"
                | "cancelAllOrdersAfter"
        );
        if !trading && !matches!(event.as_str(), "subscribe" | "unsubscribe" | "ping") {
            return Err(invalid("Unsupported Kraken V1 event."));
        }
        let account_wide = matches!(event.as_str(), "cancelAll" | "cancelAllOrdersAfter");
        if account_wide != all_symbols {
            return Err(invalid(
                "Only account-wide cancellations require all_symbols=true.",
            ));
        }
        if trading {
            let token = self
                .token
                .as_ref()
                .ok_or_else(|| invalid("Trading requires a private session token."))?;
            obj.insert("token".into(), json!(token));
            match event.as_str() {
                "cancelOrder" => {
                    if obj
                        .get("txid")
                        .and_then(Value::as_array)
                        .is_none_or(|v| v.is_empty())
                    {
                        return Err(invalid("cancelOrder requires nonempty txid."));
                    }
                }
                "cancelAllOrdersAfter" => {
                    if obj.get("timeout").and_then(Value::as_u64).is_none() {
                        return Err(invalid("timeout must be a nonnegative integer."));
                    }
                }
                "addOrder" => {
                    for key in ["ordertype", "type", "pair", "volume"] {
                        if obj
                            .get(key)
                            .and_then(Value::as_str)
                            .is_none_or(|v| v.trim().is_empty())
                        {
                            return Err(invalid(&format!("addOrder requires {key}.")));
                        }
                    }
                }
                "editOrder" | "amendOrder" => {
                    if (if event == "editOrder" {
                        &["orderid"][..]
                    } else {
                        &["txid", "cl_ord_id"][..]
                    })
                    .iter()
                    .all(|key| {
                        obj.get(*key)
                            .and_then(Value::as_str)
                            .is_none_or(|v| v.trim().is_empty())
                    }) {
                        return Err(invalid("An order identifier is required."));
                    }
                }
                _ => {}
            }
        } else if event != "ping" {
            let sub = obj
                .get_mut("subscription")
                .and_then(Value::as_object_mut)
                .ok_or_else(|| invalid("subscription must be an object."))?;
            let channel = sub.get("name").and_then(Value::as_str).unwrap_or("");
            let private = matches!(channel, "openOrders" | "ownTrades");
            if !private
                && !matches!(
                    channel,
                    "book" | "ohlc" | "spread" | "ticker" | "trade" | "*"
                )
            {
                return Err(invalid("Unknown V1 subscription name."));
            }
            if channel == "*" && event == "subscribe" {
                return Err(invalid("Wildcard applies only to unsubscribe."));
            }
            if private {
                let token = self
                    .token
                    .as_ref()
                    .ok_or_else(|| invalid("Private subscriptions require a session token."))?;
                sub.insert("token".into(), json!(token));
            } else if self.token.is_some() && channel != "*" {
                return Err(invalid(
                    "Use a public V1 connection for market subscriptions.",
                ));
            }
        }
        self.connection.send_json(&message).await
    }
}

fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(message.into())
}
