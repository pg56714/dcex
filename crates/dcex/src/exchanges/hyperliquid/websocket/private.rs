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

    /// Sign a batch of wire-format orders offline for `post_action`.
    /// The caller supplies a unique millisecond nonce and the intended network.
    #[allow(clippy::too_many_arguments)]
    pub fn sign_order(
        orders_json: &str,
        grouping: &str,
        nonce: u64,
        private_key: &str,
        testnet: bool,
        vault_address: Option<&str>,
        expires_after: Option<u64>,
    ) -> Result<Value> {
        use super::super::msgpack::OrderedValue;
        if !["na", "normalTpsl", "positionTpsl"].contains(&grouping) {
            return Err(crate::DcexError::InvalidInput(
                "invalid order grouping".into(),
            ));
        }
        let orders: OrderedValue = serde_json::from_str(orders_json)
            .map_err(|e| crate::DcexError::InvalidInput(e.to_string()))?;
        let OrderedValue::Array(orders) = orders else {
            return Err(crate::DcexError::InvalidInput(
                "orders must be an array".into(),
            ));
        };
        if orders.is_empty() {
            return Err(crate::DcexError::InvalidInput(
                "orders must not be empty".into(),
            ));
        }
        let orders = orders
            .iter()
            .map(super::super::trade::normalize_wire_order)
            .collect::<Result<Vec<_>>>()?;
        let action = OrderedValue::Object(vec![
            ("type".into(), OrderedValue::String("order".into())),
            ("orders".into(), OrderedValue::Array(orders)),
            ("grouping".into(), OrderedValue::String(grouping.into())),
        ]);
        signed_action(
            action,
            nonce,
            private_key,
            testnet,
            vault_address,
            expires_after,
        )
    }

    /// Sign wire-format `{a: asset_id, o: order_id}` cancellations offline.
    pub fn sign_cancel(
        cancels_json: &str,
        nonce: u64,
        private_key: &str,
        testnet: bool,
        vault_address: Option<&str>,
        expires_after: Option<u64>,
    ) -> Result<Value> {
        use super::super::msgpack::OrderedValue;
        let cancels: Value = serde_json::from_str(cancels_json)
            .map_err(|e| crate::DcexError::InvalidInput(e.to_string()))?;
        let cancels = cancels
            .as_array()
            .filter(|items| !items.is_empty())
            .ok_or_else(|| {
                crate::DcexError::InvalidInput("cancels must be a nonempty array".into())
            })?;
        let cancels = cancels
            .iter()
            .map(|cancel| {
                let item = cancel
                    .as_object()
                    .filter(|item| item.len() == 2)
                    .ok_or_else(|| {
                        crate::DcexError::InvalidInput("cancel requires only a and o".into())
                    })?;
                ["a", "o"]
                    .into_iter()
                    .map(|key| {
                        let value = item.get(key).and_then(Value::as_u64).ok_or_else(|| {
                            crate::DcexError::InvalidInput(format!("cancel {key} must be unsigned"))
                        })?;
                        Ok((key.to_string(), OrderedValue::Uint(value)))
                    })
                    .collect::<Result<Vec<_>>>()
                    .map(OrderedValue::Object)
            })
            .collect::<Result<Vec<_>>>()?;
        let action = OrderedValue::Object(vec![
            ("type".into(), OrderedValue::String("cancel".into())),
            ("cancels".into(), OrderedValue::Array(cancels)),
        ]);
        signed_action(
            action,
            nonce,
            private_key,
            testnet,
            vault_address,
            expires_after,
        )
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

fn signed_action(
    action: super::super::msgpack::OrderedValue,
    nonce: u64,
    private_key: &str,
    testnet: bool,
    vault_address: Option<&str>,
    expires_after: Option<u64>,
) -> Result<Value> {
    use super::super::{
        msgpack::encode_msgpack,
        signing::{hyperliquid_signature, parse_private_key},
    };
    let signature = hyperliquid_signature(
        &encode_msgpack(&action),
        nonce,
        vault_address,
        expires_after,
        testnet,
        &parse_private_key(private_key)?,
    )?;
    let mut payload = serde_json::json!({"action":action.to_json(),"nonce":nonce,
        "signature":{"r":signature.r,"s":signature.s,"v":signature.v}});
    if let Some(vault) = vault_address {
        payload["vaultAddress"] = vault.into();
    }
    if let Some(expires) = expires_after {
        payload["expiresAfter"] = expires.into();
    }
    super::post::payload(0, "action", payload.clone())?;
    Ok(payload)
}
