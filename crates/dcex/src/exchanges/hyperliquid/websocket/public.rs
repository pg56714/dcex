use std::sync::Arc;
use std::time::Duration;

use serde_json::Value;

use crate::product_table::ProductTable;
use crate::ws::{WebSocketConfig, WebSocketConnection};
use crate::{DcexError, Result};

use super::{
    all_mids_subscription, candle_subscription, coin_subscription, l2_book_subscription,
    subscription_payload, websocket_url,
};

pub struct HyperliquidPublicWebSocket {
    connection: WebSocketConnection,
    product_table: Option<Arc<ProductTable>>,
}

impl HyperliquidPublicWebSocket {
    pub fn new(testnet: bool, timeout: Duration) -> Result<Self> {
        Self::with_url(websocket_url(testnet).to_string(), timeout)
    }

    pub fn with_url(url: impl Into<String>, timeout: Duration) -> Result<Self> {
        Ok(Self {
            connection: WebSocketConnection::new(WebSocketConfig::new(url, timeout)?),
            product_table: None,
        })
    }

    pub fn set_product_table(&mut self, product_table: ProductTable) {
        self.product_table = Some(Arc::new(product_table));
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

    pub async fn subscribe_all_mids(&mut self) -> Result<()> {
        self.subscribe(all_mids_subscription(None)?).await
    }

    pub async fn subscribe_all_mids_for_dex(&mut self, dex: &str) -> Result<()> {
        self.subscribe(all_mids_subscription(Some(dex))?).await
    }

    pub async fn subscribe_trades(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe(coin_subscription("trades", self.coin(product_symbol)?)?)
            .await
    }

    pub async fn subscribe_orderbook(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_l2_book(product_symbol).await
    }

    pub async fn subscribe_l2_book(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe_l2_book_with_optional_precision(product_symbol, None, None)
            .await
    }

    pub async fn subscribe_l2_book_with_n_sig_figs(
        &mut self,
        product_symbol: &str,
        n_sig_figs: u64,
    ) -> Result<()> {
        self.subscribe_l2_book_with_optional_precision(product_symbol, Some(n_sig_figs), None)
            .await
    }

    pub async fn subscribe_l2_book_with_mantissa(
        &mut self,
        product_symbol: &str,
        mantissa: u64,
    ) -> Result<()> {
        self.subscribe_l2_book_with_precision(product_symbol, 5, mantissa)
            .await
    }

    pub async fn subscribe_l2_book_with_precision(
        &mut self,
        product_symbol: &str,
        n_sig_figs: u64,
        mantissa: u64,
    ) -> Result<()> {
        self.subscribe_l2_book_with_optional_precision(
            product_symbol,
            Some(n_sig_figs),
            Some(mantissa),
        )
        .await
    }

    async fn subscribe_l2_book_with_optional_precision(
        &mut self,
        product_symbol: &str,
        n_sig_figs: Option<u64>,
        mantissa: Option<u64>,
    ) -> Result<()> {
        self.subscribe(l2_book_subscription(
            self.coin(product_symbol)?,
            n_sig_figs,
            mantissa,
        )?)
        .await
    }

    pub async fn subscribe_bbo(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe(coin_subscription("bbo", self.coin(product_symbol)?)?)
            .await
    }

    pub async fn subscribe_klines(&mut self, product_symbol: &str, interval: &str) -> Result<()> {
        self.subscribe(candle_subscription(self.coin(product_symbol)?, interval)?)
            .await
    }

    pub async fn subscribe_active_asset_ctx(&mut self, product_symbol: &str) -> Result<()> {
        self.subscribe(coin_subscription(
            "activeAssetCtx",
            self.coin(product_symbol)?,
        )?)
        .await
    }

    pub async fn recv(&mut self) -> Result<Value> {
        self.connection.recv_json().await
    }

    pub async fn recv_bytes(&mut self) -> Result<Vec<u8>> {
        self.connection.recv_bytes().await
    }

    fn coin(&self, product_symbol: &str) -> Result<String> {
        if super::is_canonical_product_symbol(product_symbol) {
            if let Some(table) = &self.product_table {
                let exchange_symbol = table.get_exchange_symbol("hyperliquid", product_symbol)?;
                let value: Value = serde_json::from_str(&exchange_symbol).map_err(|error| {
                    DcexError::InvalidInput(format!("invalid Hyperliquid exchange symbol: {error}"))
                })?;
                return value
                    .as_array()
                    .and_then(|values| values.first())
                    .and_then(Value::as_str)
                    .map(str::to_string)
                    .ok_or_else(|| {
                        DcexError::InvalidInput(
                            "Hyperliquid exchange symbol must contain a coin".to_string(),
                        )
                    });
            }
        }
        Ok(product_symbol.to_string())
    }
}
