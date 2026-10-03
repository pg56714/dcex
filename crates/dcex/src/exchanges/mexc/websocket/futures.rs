//! MEXC contract WebSocket protocol (separate from Spot Protobuf streams).
use crate::crypto::hmac_sha256_hex;
use crate::exchange::unix_timestamp_ms;
use crate::exchanges::mexc::params::invalid;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};
use serde_json::{Value, json};
use std::collections::VecDeque;
use std::time::Duration;

pub struct MexcFuturesWebSocket {
    product_table: Option<std::sync::Arc<crate::product_table::ProductTable>>,
    connection: WebSocketConnection,
    credentials: Option<(String, String)>,
    timeout: Duration,
    authenticated: bool,
    pending: VecDeque<Vec<u8>>,
}

impl MexcFuturesWebSocket {
    fn exchange_symbol(&self, symbol: &str) -> Result<String> {
        if let Some(table) = &self.product_table {
            return Ok(table
                .resolve_symbol("mexc", symbol, Some("swap"), None)?
                .exchange_symbol
                .clone());
        }
        normalize_symbol(symbol)
    }

    pub fn set_product_table(&mut self, table: crate::product_table::ProductTable) {
        self.product_table = Some(std::sync::Arc::new(table));
    }

    pub fn with_product_table(mut self, table: crate::product_table::ProductTable) -> Self {
        self.set_product_table(table);
        self
    }

    pub fn new(timeout: Duration) -> Result<Self> {
        Self::with_url("wss://contract.mexc.com/edge", timeout)
    }
    pub fn with_url(url: impl Into<String>, timeout: Duration) -> Result<Self> {
        Ok(Self {
            product_table: None,
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            credentials: None,
            timeout,
            authenticated: false,
            pending: VecDeque::new(),
        })
    }
    pub fn with_credentials(mut self, api_key: String, api_secret: String) -> Result<Self> {
        if api_key.trim().is_empty() || api_secret.trim().is_empty() {
            return Err(invalid("API key and secret must not be empty"));
        }
        self.credentials = Some((api_key, api_secret));
        Ok(self)
    }
    pub fn is_connected(&self) -> bool {
        self.connection.is_connected()
    }
    pub async fn connect(&mut self) -> Result<()> {
        self.authenticated = false;
        self.pending.clear();
        self.connection.connect().await?;
        if let Some((api_key, api_secret)) = &self.credentials {
            let timestamp = unix_timestamp_ms()?.to_string();
            let signature = hmac_sha256_hex(
                api_secret.as_bytes(),
                format!("{api_key}{timestamp}").as_bytes(),
            )?;
            self.connection.send_json(&json!({"method":"login","subscribe":true,"param":{"apiKey":api_key,"reqTime":timestamp,"signature":signature}})).await?;
            let result = tokio::time::timeout(self.timeout, async {
                loop {
                    let bytes = self.connection.recv_bytes().await?;
                    let event: Value = serde_json::from_slice(&bytes)
                        .map_err(|e| DcexError::Decode(e.to_string()))?;
                    if event["channel"] == "rs.login" && event["data"] == "success" {
                        return Ok(());
                    }
                    if event["channel"] == "rs.error" || event["channel"] == "rs.login" {
                        return Err(invalid("futures WebSocket login rejected"));
                    }
                    if self.pending.len() >= 100 {
                        return Err(invalid("too many events before login acknowledgement"));
                    }
                    self.pending.push_back(bytes);
                }
            })
            .await
            .map_err(|_| invalid("futures WebSocket login timed out"))
            .and_then(|r| r);
            if let Err(error) = result {
                let _ = self.connection.close().await;
                return Err(error);
            }
            self.authenticated = true;
        }
        Ok(())
    }
    pub async fn close(&mut self) -> Result<()> {
        self.authenticated = false;
        self.pending.clear();
        self.connection.close().await
    }
    pub async fn ping(&mut self) -> Result<()> {
        self.connection.send_json(&json!({"method":"ping"})).await
    }
    pub async fn recv(&mut self) -> Result<Vec<u8>> {
        if let Some(event) = self.pending.pop_front() {
            return Ok(event);
        }
        self.connection.recv_bytes().await
    }
    pub async fn subscribe(
        &mut self,
        channel: &str,
        symbol: Option<&str>,
        interval: Option<&str>,
        step: Option<&str>,
    ) -> Result<()> {
        self.subscription(true, channel, symbol, interval, step)
            .await
    }
    pub async fn unsubscribe(
        &mut self,
        channel: &str,
        symbol: Option<&str>,
        interval: Option<&str>,
        step: Option<&str>,
    ) -> Result<()> {
        self.subscription(false, channel, symbol, interval, step)
            .await
    }
    async fn subscription(
        &mut self,
        subscribe: bool,
        channel: &str,
        symbol: Option<&str>,
        interval: Option<&str>,
        step: Option<&str>,
    ) -> Result<()> {
        if ![
            "tickers",
            "ticker",
            "deal",
            "depth",
            "depth.step",
            "kline",
            "funding.rate",
            "index.price",
            "fair.price",
            "contract",
            "event.contract",
        ]
        .contains(&channel)
        {
            return Err(invalid("unsupported futures channel"));
        }
        let mut param = json!({});
        if matches!(channel, "tickers" | "contract" | "event.contract") {
            if symbol.is_some() {
                return Err(invalid("this channel does not accept a symbol"));
            }
        } else {
            param["symbol"] = self
                .exchange_symbol(symbol.ok_or_else(|| invalid("symbol is required"))?)?
                .into();
        }
        if channel == "kline" {
            if let Some(interval) = interval {
                let interval = match interval {
                    "1m" => "Min1",
                    "5m" => "Min5",
                    "15m" => "Min15",
                    "30m" => "Min30",
                    "1h" => "Min60",
                    "4h" => "Hour4",
                    "8h" => "Hour8",
                    "1d" => "Day1",
                    "1w" => "Week1",
                    "1M" => "Month1",
                    other => other,
                };
                if ![
                    "Min1", "Min5", "Min15", "Min30", "Min60", "Hour4", "Hour8", "Day1", "Week1",
                    "Month1",
                ]
                .contains(&interval)
                {
                    return Err(invalid("unsupported kline interval"));
                }
                param["interval"] = interval.into();
            } else if subscribe {
                return Err(invalid("kline subscription requires interval"));
            }
        } else if interval.is_some() {
            return Err(invalid("interval is only valid for kline"));
        }
        if channel == "depth.step" {
            let step = step.ok_or_else(|| invalid("depth.step requires step"))?;
            if !step.parse::<f64>().is_ok_and(|v| v.is_finite() && v > 0.0) {
                return Err(invalid("step must be positive"));
            }
            param["step"] = step.into();
        } else if step.is_some() {
            return Err(invalid("step is only valid for depth.step"));
        }
        let method = format!("{}.{channel}", if subscribe { "sub" } else { "unsub" });
        if matches!(channel, "contract" | "event.contract") {
            return self.connection.send_json(&json!({"method": method})).await;
        }
        self.connection
            .send_json(&json!({"method":method,"param":param,"gzip":false}))
            .await
    }
    /// Replace the private push filter; an empty list restores all default pushes.
    pub async fn set_private_filters(&mut self, filters: Value) -> Result<()> {
        if !self.authenticated {
            return Err(invalid("private filters require successful login"));
        }
        let mut filters = filters
            .as_array()
            .cloned()
            .ok_or_else(|| invalid("filters must be an array"))?;
        for filter in &mut filters {
            let object = filter
                .as_object_mut()
                .ok_or_else(|| invalid("filter must be an object"))?;
            if object.keys().any(|k| k != "filter" && k != "rules") {
                return Err(invalid("unsupported filter field"));
            }
            let key = object
                .get("filter")
                .and_then(Value::as_str)
                .ok_or_else(|| invalid("filter name required"))?
                .to_owned();
            if ![
                "order",
                "order.deal",
                "position",
                "plan.order",
                "stop.order",
                "stop.planorder",
                "risk.limit",
                "adl.level",
                "asset",
            ]
            .contains(&key.as_str())
            {
                return Err(invalid("unsupported private filter"));
            }
            if let Some(rules) = object.get_mut("rules") {
                let rules = rules
                    .as_array_mut()
                    .ok_or_else(|| invalid("rules must be a symbol array"))?;
                if ["asset", "adl.level"].contains(&key.as_str()) && !rules.is_empty() {
                    return Err(invalid("asset and adl.level cannot be filtered by symbol"));
                }
                for symbol in rules {
                    *symbol = self
                        .exchange_symbol(
                            symbol
                                .as_str()
                                .ok_or_else(|| invalid("symbol must be a string"))?,
                        )?
                        .into();
                }
            }
        }
        self.connection
            .send_json(&json!({"method":"personal.filter","param":{"filters":filters}}))
            .await
    }
    pub async fn subscribe_tickers(&mut self) -> Result<()> {
        self.subscribe("tickers", None, None, None).await
    }
    pub async fn subscribe_ticker(&mut self, symbol: &str) -> Result<()> {
        self.subscribe("ticker", Some(symbol), None, None).await
    }
    pub async fn subscribe_trades(&mut self, symbol: &str) -> Result<()> {
        self.subscribe("deal", Some(symbol), None, None).await
    }
    pub async fn subscribe_orderbook(&mut self, symbol: &str) -> Result<()> {
        self.subscribe("depth", Some(symbol), None, None).await
    }
    pub async fn subscribe_orderbook_step(&mut self, symbol: &str, step: &str) -> Result<()> {
        self.subscribe("depth.step", Some(symbol), None, Some(step))
            .await
    }
    pub async fn subscribe_klines(&mut self, symbol: &str, interval: &str) -> Result<()> {
        self.subscribe("kline", Some(symbol), Some(interval), None)
            .await
    }
    pub async fn subscribe_funding_rate(&mut self, symbol: &str) -> Result<()> {
        self.subscribe("funding.rate", Some(symbol), None, None)
            .await
    }
    pub async fn subscribe_index_price(&mut self, symbol: &str) -> Result<()> {
        self.subscribe("index.price", Some(symbol), None, None)
            .await
    }
    pub async fn subscribe_fair_price(&mut self, symbol: &str) -> Result<()> {
        self.subscribe("fair.price", Some(symbol), None, None).await
    }
}

fn normalize_symbol(symbol: &str) -> Result<String> {
    if symbol.ends_with("-SWAP") {
        return Err(invalid(
            "MEXC contract display names require a product table; pass the official exchange symbol to WebSocket",
        ));
    }
    let symbol = symbol.to_owned();
    if !symbol.contains('_')
        || !symbol
            .bytes()
            .all(|c| c.is_ascii_uppercase() || c.is_ascii_digit() || c == b'_')
    {
        return Err(invalid("expected contract symbol or canonical SWAP symbol"));
    }
    Ok(symbol)
}

#[cfg(test)]
mod tests {
    use super::*;
    use futures_util::{SinkExt, StreamExt};
    use tokio::net::TcpListener;
    use tokio_tungstenite::{accept_async, tungstenite::Message};

    #[tokio::test]
    async fn futures_login_subscription_filter_and_heartbeat_match_protocol() {
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let url = format!("ws://{}", listener.local_addr().unwrap());
        let server = tokio::spawn(async move {
            let (stream, _) = listener.accept().await.unwrap();
            let mut ws = accept_async(stream).await.unwrap();
            let message = ws.next().await.unwrap().unwrap();
            let login: Value = serde_json::from_str(message.to_text().unwrap()).unwrap();
            assert_eq!(login["method"], "login");
            assert_eq!(login["param"]["apiKey"], "key");
            let timestamp = login["param"]["reqTime"].as_str().unwrap();
            assert_eq!(
                login["param"]["signature"],
                hmac_sha256_hex(b"secret", format!("key{timestamp}").as_bytes()).unwrap()
            );
            ws.send(Message::Text(
                r#"{"channel":"rs.login","data":"success"}"#.into(),
            ))
            .await
            .unwrap();
            let mut events = Vec::new();
            for _ in 0..4 {
                let message = ws.next().await.unwrap().unwrap();
                events.push(serde_json::from_str::<Value>(message.to_text().unwrap()).unwrap());
            }
            ws.send(Message::Text(
                r#"{"channel":"push.personal.asset","data":{"currency":"USDT"}}"#.into(),
            ))
            .await
            .unwrap();
            events
        });
        let mut client = MexcFuturesWebSocket::with_url(url, Duration::from_secs(10))
            .unwrap()
            .with_credentials("key".into(), "secret".into())
            .unwrap();
        client.connect().await.unwrap();
        client.subscribe_orderbook("BTC_USDT").await.unwrap();
        client.subscribe_klines("BTC_USDT", "1h").await.unwrap();
        client
            .set_private_filters(
                json!([{"filter":"order","rules":["BTC_USDT"]},{"filter":"asset"}]),
            )
            .await
            .unwrap();
        client.ping().await.unwrap();
        let received: Value = serde_json::from_slice(&client.recv().await.unwrap()).unwrap();
        assert_eq!(received["channel"], "push.personal.asset");
        let events = server.await.unwrap();
        assert_eq!(
            events[0],
            json!({"method":"sub.depth","param":{"symbol":"BTC_USDT"},"gzip":false})
        );
        assert_eq!(
            events[1],
            json!({"method":"sub.kline","param":{"symbol":"BTC_USDT","interval":"Min60"},"gzip":false})
        );
        assert_eq!(events[2]["param"]["filters"][0]["rules"][0], "BTC_USDT");
        assert_eq!(events[3], json!({"method":"ping"}));
    }

    #[tokio::test]
    async fn rejected_login_does_not_enable_private_filters() {
        let listener = TcpListener::bind("127.0.0.1:0").await.unwrap();
        let url = format!("ws://{}", listener.local_addr().unwrap());
        let server = tokio::spawn(async move {
            let (stream, _) = listener.accept().await.unwrap();
            let mut ws = accept_async(stream).await.unwrap();
            ws.next().await.unwrap().unwrap();
            ws.send(Message::Text(
                r#"{"channel":"rs.error","data":"invalid signature"}"#.into(),
            ))
            .await
            .unwrap();
        });
        let mut client = MexcFuturesWebSocket::with_url(url, Duration::from_secs(10))
            .unwrap()
            .with_credentials("key".into(), "secret".into())
            .unwrap();
        assert!(client.connect().await.is_err());
        assert!(!client.is_connected());
        assert!(client.set_private_filters(json!([])).await.is_err());
        server.await.unwrap();
    }
}
