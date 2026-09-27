use std::sync::Arc;
use std::time::Duration;

use serde_json::Value;

use crate::Result;
use crate::product_table::ProductTable;
use crate::ws::{WebSocketConfig, WebSocketConnection};

use super::{
    coin_subscription, normalize_user, resolve_coin, subscription_payload, user_subscription,
    websocket_url,
};

pub struct HyperliquidPrivateWebSocket {
    connection: WebSocketConnection,
    user: String,
    product_table: Option<Arc<ProductTable>>,
}

impl HyperliquidPrivateWebSocket {
    pub fn new(user: String, testnet: bool, timeout: Duration) -> Result<Self> {
        Self::with_url(user, websocket_url(testnet).to_string(), timeout)
    }

    pub fn with_url(user: String, url: impl Into<String>, timeout: Duration) -> Result<Self> {
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            user: normalize_user(&user)?,
            product_table: None,
        })
    }

    /// Resolves canonical product symbols (for example `BTC-USDC-SWAP`) like the public client.
    pub fn set_product_table(&mut self, product_table: ProductTable) {
        self.product_table = Some(Arc::new(product_table));
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

    /// Sends an info request; match the response from `recv` by its numeric id.
    pub async fn post_info(&mut self, id: u64, payload: Value) -> Result<()> {
        self.connection
            .send_json(&super::post::payload(id, "info", payload)?)
            .await
    }

    /// Sends an already signed trading action without changing its nonce or signature.
    /// A successful send is not an acknowledgement; consume the `post` response.
    pub async fn post_action(&mut self, id: u64, signed_payload: Value) -> Result<()> {
        self.connection
            .send_json(&super::post::payload(id, "action", signed_payload)?)
            .await
    }

    pub async fn subscribe(&mut self, subscription: Value) -> Result<()> {
        let payload = subscription_payload("subscribe", subscription)?;
        self.connection.send_json(&payload).await
    }

    pub async fn unsubscribe(&mut self, subscription: Value) -> Result<()> {
        let payload = subscription_payload("unsubscribe", subscription)?;
        self.connection.send_json(&payload).await
    }

    pub async fn subscribe_user_subscription(&mut self, subscription_type: &str) -> Result<()> {
        self.subscribe(user_subscription(subscription_type, &self.user, None)?)
            .await
    }

    pub async fn subscribe_user_subscription_for_dex(
        &mut self,
        subscription_type: &str,
        dex: &str,
    ) -> Result<()> {
        self.subscribe(user_subscription(subscription_type, &self.user, Some(dex))?)
            .await
    }

    pub async fn unsubscribe_user_subscription(&mut self, subscription_type: &str) -> Result<()> {
        self.unsubscribe(user_subscription(subscription_type, &self.user, None)?)
            .await
    }

    pub async fn unsubscribe_user_subscription_for_dex(
        &mut self,
        subscription_type: &str,
        dex: &str,
    ) -> Result<()> {
        self.unsubscribe(user_subscription(subscription_type, &self.user, Some(dex))?)
            .await
    }

    pub async fn subscribe_notifications(&mut self) -> Result<()> {
        self.subscribe_user_subscription("notification").await
    }

    pub async fn subscribe_web_data3(&mut self) -> Result<()> {
        self.subscribe_user_subscription("webData3").await
    }

    pub async fn subscribe_clearinghouse_state(&mut self) -> Result<()> {
        self.subscribe_user_subscription("clearinghouseState").await
    }

    pub async fn subscribe_clearinghouse_state_for_dex(&mut self, dex: &str) -> Result<()> {
        self.subscribe_user_subscription_for_dex("clearinghouseState", dex)
            .await
    }

    pub async fn subscribe_open_orders(&mut self) -> Result<()> {
        self.subscribe_user_subscription("openOrders").await
    }

    pub async fn subscribe_open_orders_for_dex(&mut self, dex: &str) -> Result<()> {
        self.subscribe_user_subscription_for_dex("openOrders", dex)
            .await
    }

    pub async fn subscribe_order_updates(&mut self) -> Result<()> {
        self.subscribe_user_subscription("orderUpdates").await
    }

    pub async fn subscribe_user_events(&mut self) -> Result<()> {
        self.subscribe_user_subscription("userEvents").await
    }

    pub async fn subscribe_user_fills(&mut self) -> Result<()> {
        self.subscribe_user_fills_with_aggregate_by_time(false)
            .await
    }

    pub async fn subscribe_user_fills_with_aggregate_by_time(
        &mut self,
        aggregate_by_time: bool,
    ) -> Result<()> {
        let mut subscription = user_subscription("userFills", &self.user, None)?
            .as_object()
            .expect("user subscription object")
            .clone();
        if aggregate_by_time {
            subscription.insert(
                "aggregateByTime".to_string(),
                Value::Bool(aggregate_by_time),
            );
        }
        self.subscribe(Value::Object(subscription)).await
    }

    pub async fn subscribe_user_fundings(&mut self) -> Result<()> {
        self.subscribe_user_subscription("userFundings").await
    }

    pub async fn subscribe_user_non_funding_ledger_updates(&mut self) -> Result<()> {
        self.subscribe_user_subscription("userNonFundingLedgerUpdates")
            .await
    }

    pub async fn subscribe_twap_states(&mut self) -> Result<()> {
        self.subscribe_user_subscription("twapStates").await
    }

    pub async fn subscribe_twap_states_for_dex(&mut self, dex: &str) -> Result<()> {
        self.subscribe_user_subscription_for_dex("twapStates", dex)
            .await
    }

    pub async fn subscribe_user_twap_slice_fills(&mut self) -> Result<()> {
        self.subscribe_user_subscription("userTwapSliceFills").await
    }

    pub async fn subscribe_user_twap_history(&mut self) -> Result<()> {
        self.subscribe_user_subscription("userTwapHistory").await
    }

    pub async fn subscribe_active_asset_data(&mut self, product_symbol: &str) -> Result<()> {
        let mut subscription = coin_subscription(
            "activeAssetData",
            resolve_coin(self.product_table.as_deref(), product_symbol)?,
        )?
        .as_object()
        .expect("coin subscription object")
        .clone();
        subscription.insert("user".to_string(), Value::String(self.user.clone()));
        self.subscribe(Value::Object(subscription)).await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }
}
