use std::time::Duration;

use serde_json::Value;

use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::Result;

use super::super::client::LighterClient;
use super::{account_channel, http_url, market_channel, subscription_payload, websocket_url};

pub struct LighterPrivateWebSocket {
    connection: WebSocketConnection,
    client: LighterClient,
    account_index: u64,
}

impl LighterPrivateWebSocket {
    pub fn new(
        account_index: u64,
        api_key_index: u64,
        api_private_key: String,
        testnet: bool,
        timeout: Duration,
    ) -> Result<Self> {
        Self::with_urls(
            account_index,
            api_key_index,
            api_private_key,
            websocket_url(testnet).to_string(),
            http_url(testnet).to_string(),
            timeout,
        )
    }

    pub fn with_urls(
        account_index: u64,
        api_key_index: u64,
        api_private_key: String,
        websocket_url: impl Into<String>,
        http_base_url: String,
        timeout: Duration,
    ) -> Result<Self> {
        let client = LighterClient::with_base_url_and_credentials(
            timeout,
            http_base_url,
            Some(account_index),
            Some(api_key_index),
            Some(api_private_key),
        )?;
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(websocket_url, timeout)?),
            client,
            account_index,
        })
    }

    pub fn account_index(&self) -> u64 {
        self.account_index
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

    pub async fn ping(&mut self) -> Result<()> {
        self.connection.send_ping(Vec::new()).await
    }

    pub fn create_auth_token(
        &self,
        deadline: Option<u64>,
        api_key_index: Option<u64>,
    ) -> Result<String> {
        self.client.create_auth_token(deadline, api_key_index)
    }

    pub async fn subscribe(&mut self, channel: &str, auth: Option<String>) -> Result<()> {
        let payload = subscription_payload("subscribe", channel, auth)?;
        self.connection.send_json(&payload).await
    }

    pub async fn unsubscribe(&mut self, channel: &str) -> Result<()> {
        let payload = subscription_payload("unsubscribe", channel, None)?;
        self.connection.send_json(&payload).await
    }

    pub async fn subscribe_authenticated(&mut self, channel: &str) -> Result<()> {
        let auth = self.create_auth_token(None, None)?;
        self.subscribe(channel, Some(auth)).await
    }

    pub async fn subscribe_account_all(&mut self) -> Result<()> {
        self.subscribe(&account_channel("account_all", self.account_index)?, None)
            .await
    }

    pub async fn subscribe_account_market(&mut self, market_id: u64) -> Result<()> {
        self.subscribe_authenticated(&format!(
            "account_market/{market_id}/{}",
            self.account_index
        ))
        .await
    }

    pub async fn subscribe_user_stats(&mut self) -> Result<()> {
        self.subscribe(&account_channel("user_stats", self.account_index)?, None)
            .await
    }

    pub async fn subscribe_account_tx(&mut self) -> Result<()> {
        self.subscribe_authenticated(&account_channel("account_tx", self.account_index)?)
            .await
    }

    pub async fn subscribe_account_all_orders(&mut self) -> Result<()> {
        self.subscribe_authenticated(&account_channel("account_all_orders", self.account_index)?)
            .await
    }

    pub async fn subscribe_pool_data(&mut self) -> Result<()> {
        self.subscribe_authenticated(&account_channel("pool_data", self.account_index)?)
            .await
    }

    pub async fn subscribe_pool_info(&mut self) -> Result<()> {
        self.subscribe_authenticated(&account_channel("pool_info", self.account_index)?)
            .await
    }

    pub async fn subscribe_notifications(&mut self) -> Result<()> {
        self.subscribe_authenticated(&account_channel("notification", self.account_index)?)
            .await
    }

    pub async fn subscribe_account_orders(&mut self, market_id: u64) -> Result<()> {
        self.subscribe_authenticated(&format!(
            "account_orders/{market_id}/{}",
            self.account_index
        ))
        .await
    }

    pub async fn subscribe_account_all_trades(&mut self) -> Result<()> {
        self.subscribe(
            &account_channel("account_all_trades", self.account_index)?,
            None,
        )
        .await
    }

    pub async fn subscribe_account_all_positions(&mut self) -> Result<()> {
        self.subscribe(
            &account_channel("account_all_positions", self.account_index)?,
            None,
        )
        .await
    }

    pub async fn subscribe_account_all_assets(&mut self) -> Result<()> {
        self.subscribe_authenticated(&account_channel("account_all_assets", self.account_index)?)
            .await
    }

    pub async fn subscribe_account_spot_avg_entry_prices(&mut self) -> Result<()> {
        self.subscribe_authenticated(&account_channel(
            "account_spot_avg_entry_prices",
            self.account_index,
        )?)
        .await
    }

    pub async fn subscribe_rfq(&mut self) -> Result<()> {
        self.subscribe_authenticated("rfq").await
    }

    pub async fn subscribe_private_market_channel(
        &mut self,
        prefix: &str,
        market_id: u64,
    ) -> Result<()> {
        self.subscribe_authenticated(&market_channel(prefix, market_id)?)
            .await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }
}
