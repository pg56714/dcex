use std::time::Duration;

use serde_json::Value;

use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::Result;

use super::{
    coin_subscription, normalize_user, subscription_payload, user_subscription, websocket_url,
};

pub struct HyperliquidPrivateWebSocket {
    connection: WebSocketConnection,
    user: String,
}

impl HyperliquidPrivateWebSocket {
    pub fn new(user: String, testnet: bool, timeout: Duration) -> Result<Self> {
        Self::with_url(user, websocket_url(testnet).to_string(), timeout)
    }

    pub fn with_url(user: String, url: impl Into<String>, timeout: Duration) -> Result<Self> {
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            user: normalize_user(&user)?,
        })
    }

    pub fn user(&self) -> &str {
        &self.user
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

    pub async fn subscribe(&mut self, subscription: Value) -> Result<()> {
        let payload = subscription_payload("subscribe", subscription)?;
        self.connection.send_json(&payload).await
    }

    pub async fn unsubscribe(&mut self, subscription: Value) -> Result<()> {
        let payload = subscription_payload("unsubscribe", subscription)?;
        self.connection.send_json(&payload).await
    }

    pub async fn subscribe_user_subscription(
        &mut self,
        subscription_type: &str,
        dex: Option<&str>,
    ) -> Result<()> {
        self.subscribe(user_subscription(subscription_type, &self.user, dex)?)
            .await
    }

    pub async fn unsubscribe_user_subscription(
        &mut self,
        subscription_type: &str,
        dex: Option<&str>,
    ) -> Result<()> {
        self.unsubscribe(user_subscription(subscription_type, &self.user, dex)?)
            .await
    }

    pub async fn subscribe_notifications(&mut self) -> Result<()> {
        self.subscribe_user_subscription("notification", None).await
    }

    pub async fn subscribe_web_data3(&mut self) -> Result<()> {
        self.subscribe_user_subscription("webData3", None).await
    }

    pub async fn subscribe_clearinghouse_state(&mut self, dex: Option<&str>) -> Result<()> {
        self.subscribe_user_subscription("clearinghouseState", dex)
            .await
    }

    pub async fn subscribe_open_orders(&mut self, dex: Option<&str>) -> Result<()> {
        self.subscribe_user_subscription("openOrders", dex).await
    }

    pub async fn subscribe_order_updates(&mut self) -> Result<()> {
        self.subscribe_user_subscription("orderUpdates", None).await
    }

    pub async fn subscribe_user_events(&mut self) -> Result<()> {
        self.subscribe_user_subscription("userEvents", None).await
    }

    pub async fn subscribe_user_fills(&mut self, aggregate_by_time: Option<bool>) -> Result<()> {
        let mut subscription = user_subscription("userFills", &self.user, None)?
            .as_object()
            .expect("user subscription object")
            .clone();
        if let Some(aggregate_by_time) = aggregate_by_time {
            subscription.insert(
                "aggregateByTime".to_string(),
                Value::Bool(aggregate_by_time),
            );
        }
        self.subscribe(Value::Object(subscription)).await
    }

    pub async fn subscribe_user_fundings(&mut self) -> Result<()> {
        self.subscribe_user_subscription("userFundings", None).await
    }

    pub async fn subscribe_user_non_funding_ledger_updates(&mut self) -> Result<()> {
        self.subscribe_user_subscription("userNonFundingLedgerUpdates", None)
            .await
    }

    pub async fn subscribe_twap_states(&mut self, dex: Option<&str>) -> Result<()> {
        self.subscribe_user_subscription("twapStates", dex).await
    }

    pub async fn subscribe_user_twap_slice_fills(&mut self) -> Result<()> {
        self.subscribe_user_subscription("userTwapSliceFills", None)
            .await
    }

    pub async fn subscribe_user_twap_history(&mut self) -> Result<()> {
        self.subscribe_user_subscription("userTwapHistory", None)
            .await
    }

    pub async fn subscribe_active_asset_data(&mut self, product_symbol: &str) -> Result<()> {
        let mut subscription = coin_subscription("activeAssetData", product_symbol.to_string())?
            .as_object()
            .expect("coin subscription object")
            .clone();
        subscription.insert("user".to_string(), Value::String(self.user.clone()));
        self.subscribe(Value::Object(subscription)).await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }
}
