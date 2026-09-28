use std::time::Duration;

use serde_json::{Value, json};

use crate::crypto::hmac_sha256_base64;
use crate::exchange::unix_timestamp_ms;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

/// KuCoin's action/channel push protocol and authenticated V2 trading protocol.
/// https://www.kucoin.com/docs-new/websocket-api/introduction
pub struct KucoinProWebSocket {
    connection: WebSocketConnection,
    profile: String,
    credentials: Option<(String, String, String)>,
    ready: bool,
    endpoint: String,
    timeout: Duration,
}

impl KucoinProWebSocket {
    pub fn new(
        profile: &str,
        credentials: Option<(String, String, String)>,
        url: Option<String>,
        timeout: Duration,
    ) -> Result<Self> {
        let endpoint = match profile {
            "public_spot" => "wss://x-push-spot.kucoin.com",
            "public_futures" => "wss://x-push-futures.kucoin.com",
            "private" => "wss://wsapi-push.kucoin.com",
            "trade" => "wss://wsapi.kucoin.com/v2/private",
            "trade_v1" => "wss://wsapi.kucoin.com/v1/private",
            _ => {
                return Err(DcexError::InvalidInput(
                    "Unknown KuCoin Pro WS profile.".into(),
                ));
            }
        };
        if matches!(profile, "private" | "trade" | "trade_v1") {
            let (key, secret, passphrase) = credentials.as_ref().ok_or_else(|| {
                DcexError::InvalidInput(
                    "Private KuCoin Pro WS requires key, secret and passphrase.".into(),
                )
            })?;
            for value in [key, secret, passphrase] {
                super::validate_credential("KuCoin credential", value)?;
            }
        }
        let endpoint = url.unwrap_or_else(|| endpoint.into());
        Ok(Self {
            endpoint: endpoint.clone(),
            timeout,
            connection: WebSocketConnection::new(WebSocketConfig::new(endpoint, timeout)?),
            profile: profile.into(),
            credentials,
            ready: false,
        })
    }

    pub fn url(&self) -> &str {
        &self.endpoint
    }
    pub fn is_connected(&self) -> bool {
        self.ready && self.connection.is_connected()
    }

    /// Return the welcome event, including server heartbeat intervals.
    /// Call `ping` at the advertised interval; reconnect and resubscribe on closure.
    pub async fn connect(&mut self) -> Result<Value> {
        self.ready = false;
        if self.profile == "trade_v1" {
            let (key, secret, passphrase) =
                self.credentials.as_ref().expect("validated credentials");
            let timestamp = unix_timestamp_ms()?.to_string();
            let sign =
                hmac_sha256_base64(secret.as_bytes(), format!("{key}{timestamp}").as_bytes())?;
            let pass = hmac_sha256_base64(secret.as_bytes(), passphrase.as_bytes())?;
            let mut url = url::Url::parse(&self.endpoint)
                .map_err(|e| DcexError::InvalidInput(e.to_string()))?;
            url.query_pairs_mut()
                .clear()
                .append_pair("apikey", key)
                .append_pair("timestamp", &timestamp)
                .append_pair("sign", &sign)
                .append_pair("passphrase", &pass);
            self.connection =
                WebSocketConnection::new(WebSocketConfig::new(url.to_string(), self.timeout)?);
        }
        self.connection.connect().await?;
        let result = self.handshake().await;
        if result.is_err() {
            let _ = self.connection.close().await;
        }
        self.ready = result.is_ok();
        result
    }

    async fn handshake(&mut self) -> Result<Value> {
        if self.profile == "trade_v1" {
            // Sign the exact received text, including whitespace and field order,
            // as in the official Python example on /docs-new/3470133w0.
            let raw = self.connection.recv_text().await?;
            let challenge: Value =
                serde_json::from_str(&raw).map_err(|e| DcexError::Decode(e.to_string()))?;
            if !challenge["sessionId"].is_string() || !challenge["timestamp"].is_number() {
                return Err(DcexError::Runtime(
                    "Invalid KuCoin V1 session challenge.".into(),
                ));
            }
            let (_, secret, _) = self.credentials.as_ref().expect("validated credentials");
            let signature = hmac_sha256_base64(secret.as_bytes(), raw.as_bytes())?;
            self.connection.send_text(signature).await?;
            let welcome = self.connection.recv_json().await?;
            if welcome["data"] != "welcome" {
                return Err(DcexError::Runtime(
                    "KuCoin Pro WS authentication rejected.".into(),
                ));
            }
            return Ok(welcome);
        }
        let mut welcome = Value::Null;
        if self.profile != "trade" {
            welcome = self.connection.recv_json().await?;
            if welcome["message"] != "welcome" {
                return Err(DcexError::Runtime(
                    "KuCoin Pro WS did not send a welcome event.".into(),
                ));
            }
        }
        if matches!(self.profile.as_str(), "private" | "trade") {
            let (key, secret, passphrase) =
                self.credentials.as_ref().expect("validated credentials");
            let timestamp = unix_timestamp_ms()?.to_string();
            self.connection.send_json(&json!({
                "op": "auth", "kc-api-key": key, "kc-api-timestamp": timestamp,
                "kc-api-sign": hmac_sha256_base64(secret.as_bytes(), format!("{timestamp}POST/api/websocket/users/verify").as_bytes())?,
                "kc-api-passphrase": hmac_sha256_base64(secret.as_bytes(), passphrase.as_bytes())?,
            })).await?;
            let ack = self.connection.recv_json().await?;
            let accepted = if self.profile == "trade" {
                ack["data"] == "welcome"
            } else {
                ack["result"] == true
            };
            if !accepted {
                return Err(DcexError::Runtime(
                    "KuCoin Pro WS authentication rejected.".into(),
                ));
            }
            if self.profile == "trade" {
                welcome = ack;
            }
        }
        Ok(welcome)
    }

    pub async fn close(&mut self) -> Result<()> {
        self.ready = false;
        self.connection.close().await
    }
    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }

    pub async fn ping(&mut self, id: &str) -> Result<()> {
        self.ensure_ready()?;
        self.connection
            .send_json(&json!({"id": id, "op": "ping"}))
            .await
    }

    /// Send one complete documented subscription, preserving optional filters.
    pub async fn subscription(&mut self, mut message: Value, subscribe: bool) -> Result<()> {
        self.ensure_ready()?;
        if self.profile.starts_with("trade") {
            return Err(DcexError::InvalidInput(
                "Trade connections do not accept subscriptions.".into(),
            ));
        }
        let obj = message
            .as_object_mut()
            .ok_or_else(|| DcexError::InvalidInput("Subscription must be an object.".into()))?;
        for field in ["channel"] {
            if obj
                .get(field)
                .and_then(Value::as_str)
                .is_none_or(|v| v.trim().is_empty())
            {
                return Err(DcexError::InvalidInput(format!(
                    "Subscription requires {field}."
                )));
            }
        }
        let expected = match self.profile.as_str() {
            "public_spot" => Some("SPOT"),
            "public_futures" => Some("FUTURES"),
            _ => None,
        };
        let channel = obj["channel"].as_str().unwrap_or("");
        let implied_market = match channel {
            "mark-price" | "funding-fee" | "funding-fee-all-symbols" => Some("FUTURES"),
            "callAuctionInfo" => Some("SPOT"),
            _ => None,
        };
        if channel == "balance" {
            if obj
                .get("accountType")
                .and_then(Value::as_str)
                .is_none_or(|v| v.is_empty())
            {
                return Err(DcexError::InvalidInput(
                    "Balance subscriptions require accountType.".into(),
                ));
            }
        } else if implied_market.is_none()
            && obj
                .get("tradeType")
                .and_then(Value::as_str)
                .is_none_or(|v| v.is_empty())
        {
            return Err(DcexError::InvalidInput(
                "Subscription requires tradeType.".into(),
            ));
        }
        if expected.is_some_and(|v| {
            implied_market.unwrap_or_else(|| obj["tradeType"].as_str().unwrap_or("")) != v
        }) {
            return Err(DcexError::InvalidInput(
                "tradeType does not match this public connection.".into(),
            ));
        }
        obj.insert(
            "action".into(),
            json!(if subscribe {
                "SUBSCRIBE"
            } else {
                "UNSUBSCRIBE"
            }),
        );
        self.connection.send_json(&message).await
    }

    /// Submit a V2 UTA operation. Read `recv_bytes` and check the response code;
    /// sending a frame alone does not confirm that the exchange accepted an order.
    pub async fn send_operation(&mut self, id: &str, operation: &str, args: Value) -> Result<()> {
        self.ensure_ready()?;
        let allowed = if self.profile == "trade_v1" {
            matches!(
                operation,
                "spot.order"
                    | "spot.sync_order"
                    | "spot.cancel"
                    | "spot.sync_cancel"
                    | "margin.order"
                    | "margin.cancel"
                    | "futures.order"
                    | "futures.cancel"
                    | "futures.multi_order"
                    | "futures.multi_cancel"
                    | "uta.order"
                    | "uta.cancel"
                    | "uta.amend"
            )
        } else {
            self.profile == "trade" && matches!(operation, "uta.order" | "uta.cancel" | "uta.amend")
        };
        if !allowed {
            return Err(DcexError::InvalidInput(
                "Operation is unsupported on this KuCoin trade profile.".into(),
            ));
        }
        let valid_args = if operation == "futures.multi_order" {
            args.as_array()
                .is_some_and(|items| !items.is_empty() && items.iter().all(Value::is_object))
        } else {
            args.as_object().is_some_and(|object| !object.is_empty())
        };
        if id.trim().is_empty() || !valid_args {
            return Err(DcexError::InvalidInput(
                "Trading requires an id and nonempty documented args shape.".into(),
            ));
        }
        if matches!(
            operation,
            "uta.cancel"
                | "uta.amend"
                | "spot.cancel"
                | "spot.sync_cancel"
                | "margin.cancel"
                | "futures.cancel"
        ) && ["orderId", "clientOid"].iter().all(|f| {
            args.get(f)
                .is_none_or(|v| v.as_str().is_none_or(|s| s.trim().is_empty()))
        }) {
            return Err(DcexError::InvalidInput(
                "Cancel/amend requires orderId or clientOid.".into(),
            ));
        }
        self.connection
            .send_json(&json!({"id": id, "op": operation, "args": args}))
            .await
    }

    fn ensure_ready(&self) -> Result<()> {
        if self.is_connected() {
            Ok(())
        } else {
            Err(DcexError::InvalidInput(
                "Connect and authenticate before sending KuCoin messages.".into(),
            ))
        }
    }
}
