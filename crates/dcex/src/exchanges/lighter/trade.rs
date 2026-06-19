use serde_json::json;

use crate::exchange::ValidatedResponse;
use crate::http::block_on;
use crate::{DcexError, Result};

use super::client::LighterClient;
use super::endpoints::{SEND_TX, SEND_TX_BATCH};
use super::params::LighterParams;
use super::signing::{attributes, expiry_ms, order_expiry_ms, sign_payload};

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct LighterSignedTransaction {
    pub tx_type: u64,
    pub tx_info: String,
    pub tx_hash: String,
}

impl LighterClient {
    pub async fn sign_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        let params = LighterParams::from_pairs(params);
        self.sign_request_params(method_name, &params).await
    }

    pub fn sign_request_blocking(
        &self,
        method_name: String,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        let client = self.clone();
        block_on(async move { client.sign_request(&method_name, params).await })
    }

    pub(super) async fn trade_request(
        &self,
        method_name: &str,
        params: &LighterParams,
    ) -> Result<Option<ValidatedResponse>> {
        match method_name {
            "send_tx" => {
                let mut body = params.query(&["tx_type", "tx_info", "price_protection"]);
                body.retain(|(_, value)| !value.is_empty());
                Ok(Some(self.post_form(SEND_TX, body).await?))
            }
            "send_tx_batch" => Ok(Some(
                self.post_form(SEND_TX_BATCH, params.query(&["tx_types", "tx_infos"]))
                    .await?,
            )),
            "create_order" | "place_order" => Ok(Some(
                self.submit_signed_tx(
                    self.sign_create_order_from_params(params).await?,
                    params.optional_bool("price_protection")?,
                )
                .await?,
            )),
            "cancel_order" => Ok(Some(
                self.submit_signed_tx(
                    self.sign_cancel_order_from_params(params).await?,
                    params.optional_bool("price_protection")?,
                )
                .await?,
            )),
            "modify_order" => Ok(Some(
                self.submit_signed_tx(
                    self.sign_modify_order_from_params(params).await?,
                    params.optional_bool("price_protection")?,
                )
                .await?,
            )),
            "cancel_all_orders" => Ok(Some(
                self.submit_signed_tx(
                    self.sign_cancel_all_orders_from_params(params).await?,
                    params.optional_bool("price_protection")?,
                )
                .await?,
            )),
            "update_leverage" => Ok(Some(
                self.submit_signed_tx(
                    self.sign_update_leverage_from_params(params).await?,
                    params.optional_bool("price_protection")?,
                )
                .await?,
            )),
            "update_margin" => Ok(Some(
                self.submit_signed_tx(
                    self.sign_update_margin_from_params(params).await?,
                    params.optional_bool("price_protection")?,
                )
                .await?,
            )),
            _ => Ok(None),
        }
    }

    async fn sign_request_params(
        &self,
        method_name: &str,
        params: &LighterParams,
    ) -> Result<LighterSignedTransaction> {
        match method_name {
            "sign_create_order" => self.sign_create_order_from_params(params).await,
            "sign_cancel_order" => self.sign_cancel_order_from_params(params).await,
            "sign_modify_order" => self.sign_modify_order_from_params(params).await,
            "sign_cancel_all_orders" => self.sign_cancel_all_orders_from_params(params).await,
            "sign_update_leverage" => self.sign_update_leverage_from_params(params).await,
            "sign_update_margin" => self.sign_update_margin_from_params(params).await,
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported Lighter sign method: {method_name}"
            ))),
        }
    }

    async fn sign_create_order_from_params(
        &self,
        params: &LighterParams,
    ) -> Result<LighterSignedTransaction> {
        let api_key_index = self.private_api_key_index(params.optional_u64("api_key_index")?)?;
        let nonce = self
            .next_nonce(params.optional_i64("nonce")?, Some(api_key_index))
            .await?;
        let expired_at = expiry_ms()?;
        let order_expiry = match params.optional_i64("order_expiry")? {
            Some(-1) | None => order_expiry_ms()? as i64,
            Some(value) => value,
        };
        let market_index = self.market_index(params)?;
        let client_order_index = params.required_i64("client_order_index")?;
        let base_amount = params.required_i64("base_amount")?;
        let price = params.required_i64("price")?;
        let is_ask = params.required_bool("is_ask")?;
        let order_type = params.required_i64("order_type")?;
        let time_in_force = params.required_i64("time_in_force")?;
        let reduce_only = params.optional_bool("reduce_only")?.unwrap_or(false);
        let trigger_price = params.optional_i64("trigger_price")?.unwrap_or(0);
        let attrs = attributes(
            params
                .optional_u64("integrator_account_index")?
                .unwrap_or(0),
            params.optional_u64("integrator_taker_fee")?.unwrap_or(0),
            params.optional_u64("integrator_maker_fee")?.unwrap_or(0),
            params.optional_u64("skip_nonce")?.unwrap_or(0),
            255,
        );
        let payload = json!({
            "AccountIndex": self.private_account_index(None)?,
            "ApiKeyIndex": api_key_index,
            "MarketIndex": market_index,
            "ClientOrderIndex": client_order_index,
            "BaseAmount": base_amount,
            "Price": price,
            "IsAsk": i64::from(is_ask),
            "Type": order_type,
            "TimeInForce": time_in_force,
            "ReduceOnly": i64::from(reduce_only),
            "TriggerPrice": trigger_price,
            "OrderExpiry": order_expiry,
            "ExpiredAt": expired_at,
            "Nonce": nonce,
        });
        let values = vec![
            self.chain_id as i128,
            14,
            nonce as i128,
            expired_at as i128,
            self.private_account_index(None)? as i128,
            api_key_index as i128,
            market_index as i128,
            client_order_index as i128,
            base_amount as i128,
            price as i128,
            i128::from(is_ask),
            order_type as i128,
            time_in_force as i128,
            i128::from(reduce_only),
            trigger_price as i128,
            order_expiry as i128,
        ];
        self.sign_tx(14, values, payload, attrs, api_key_index)
    }

    async fn sign_cancel_order_from_params(
        &self,
        params: &LighterParams,
    ) -> Result<LighterSignedTransaction> {
        let api_key_index = self.private_api_key_index(params.optional_u64("api_key_index")?)?;
        let nonce = self
            .next_nonce(params.optional_i64("nonce")?, Some(api_key_index))
            .await?;
        let expired_at = expiry_ms()?;
        let market_index = self.market_index(params)?;
        let order_index = params.required_i64("order_index")?;
        let attrs = attributes(
            0,
            0,
            0,
            params.optional_u64("skip_nonce")?.unwrap_or(0),
            255,
        );
        let payload = json!({
            "AccountIndex": self.private_account_index(None)?,
            "ApiKeyIndex": api_key_index,
            "MarketIndex": market_index,
            "Index": order_index,
            "ExpiredAt": expired_at,
            "Nonce": nonce,
        });
        let values = vec![
            self.chain_id as i128,
            15,
            nonce as i128,
            expired_at as i128,
            self.private_account_index(None)? as i128,
            api_key_index as i128,
            market_index as i128,
            order_index as i128,
        ];
        self.sign_tx(15, values, payload, attrs, api_key_index)
    }

    async fn sign_modify_order_from_params(
        &self,
        params: &LighterParams,
    ) -> Result<LighterSignedTransaction> {
        let api_key_index = self.private_api_key_index(params.optional_u64("api_key_index")?)?;
        let nonce = self
            .next_nonce(params.optional_i64("nonce")?, Some(api_key_index))
            .await?;
        let expired_at = expiry_ms()?;
        let market_index = self.market_index(params)?;
        let order_index = params.required_i64("order_index")?;
        let base_amount = params.required_i64("base_amount")?;
        let price = params.required_i64("price")?;
        let trigger_price = params.optional_i64("trigger_price")?.unwrap_or(0);
        let attrs = attributes(
            params
                .optional_u64("integrator_account_index")?
                .unwrap_or(0),
            params.optional_u64("integrator_taker_fee")?.unwrap_or(0),
            params.optional_u64("integrator_maker_fee")?.unwrap_or(0),
            params.optional_u64("skip_nonce")?.unwrap_or(0),
            255,
        );
        let payload = json!({
            "AccountIndex": self.private_account_index(None)?,
            "ApiKeyIndex": api_key_index,
            "MarketIndex": market_index,
            "Index": order_index,
            "BaseAmount": base_amount,
            "Price": price,
            "TriggerPrice": trigger_price,
            "ExpiredAt": expired_at,
            "Nonce": nonce,
        });
        let values = vec![
            self.chain_id as i128,
            17,
            nonce as i128,
            expired_at as i128,
            self.private_account_index(None)? as i128,
            api_key_index as i128,
            market_index as i128,
            order_index as i128,
            base_amount as i128,
            price as i128,
            trigger_price as i128,
        ];
        self.sign_tx(17, values, payload, attrs, api_key_index)
    }

    async fn sign_cancel_all_orders_from_params(
        &self,
        params: &LighterParams,
    ) -> Result<LighterSignedTransaction> {
        let api_key_index = self.private_api_key_index(params.optional_u64("api_key_index")?)?;
        let nonce = self
            .next_nonce(params.optional_i64("nonce")?, Some(api_key_index))
            .await?;
        let expired_at = expiry_ms()?;
        let time_in_force = params.required_i64("time_in_force")?;
        let timestamp_ms = params.required_i64("timestamp_ms")?;
        let attrs = attributes(
            0,
            0,
            0,
            params.optional_u64("skip_nonce")?.unwrap_or(0),
            255,
        );
        let payload = json!({
            "AccountIndex": self.private_account_index(None)?,
            "ApiKeyIndex": api_key_index,
            "TimeInForce": time_in_force,
            "Time": timestamp_ms,
            "ExpiredAt": expired_at,
            "Nonce": nonce,
        });
        let values = vec![
            self.chain_id as i128,
            16,
            nonce as i128,
            expired_at as i128,
            self.private_account_index(None)? as i128,
            api_key_index as i128,
            time_in_force as i128,
            timestamp_ms as i128,
        ];
        self.sign_tx(16, values, payload, attrs, api_key_index)
    }

    async fn sign_update_leverage_from_params(
        &self,
        params: &LighterParams,
    ) -> Result<LighterSignedTransaction> {
        let api_key_index = self.private_api_key_index(params.optional_u64("api_key_index")?)?;
        let nonce = self
            .next_nonce(params.optional_i64("nonce")?, Some(api_key_index))
            .await?;
        let expired_at = expiry_ms()?;
        let market_index = self.market_index(params)?;
        let fraction = params.required_i64("fraction")?;
        let margin_mode = params.required_i64("margin_mode")?;
        let attrs = attributes(
            0,
            0,
            0,
            params.optional_u64("skip_nonce")?.unwrap_or(0),
            255,
        );
        let payload = json!({
            "AccountIndex": self.private_account_index(None)?,
            "ApiKeyIndex": api_key_index,
            "MarketIndex": market_index,
            "InitialMarginFraction": fraction,
            "MarginMode": margin_mode,
            "ExpiredAt": expired_at,
            "Nonce": nonce,
        });
        let values = vec![
            self.chain_id as i128,
            20,
            nonce as i128,
            expired_at as i128,
            self.private_account_index(None)? as i128,
            api_key_index as i128,
            market_index as i128,
            fraction as i128,
            margin_mode as i128,
        ];
        self.sign_tx(20, values, payload, attrs, api_key_index)
    }

    async fn sign_update_margin_from_params(
        &self,
        params: &LighterParams,
    ) -> Result<LighterSignedTransaction> {
        let api_key_index = self.private_api_key_index(params.optional_u64("api_key_index")?)?;
        let nonce = self
            .next_nonce(params.optional_i64("nonce")?, Some(api_key_index))
            .await?;
        let expired_at = expiry_ms()?;
        let market_index = self.market_index(params)?;
        let usdc_amount = params.required_i64("usdc_amount")?;
        let direction = params.required_i64("direction")?;
        let attrs = attributes(
            0,
            0,
            0,
            params.optional_u64("skip_nonce")?.unwrap_or(0),
            255,
        );
        let payload = json!({
            "AccountIndex": self.private_account_index(None)?,
            "ApiKeyIndex": api_key_index,
            "MarketIndex": market_index,
            "USDCAmount": usdc_amount,
            "Direction": direction,
            "ExpiredAt": expired_at,
            "Nonce": nonce,
        });
        let amount_bits = usdc_amount as u64;
        let values = vec![
            self.chain_id as i128,
            29,
            nonce as i128,
            expired_at as i128,
            self.private_account_index(None)? as i128,
            api_key_index as i128,
            market_index as i128,
            (amount_bits & 0xffff_ffff) as i128,
            (amount_bits >> 32) as i128,
            direction as i128,
        ];
        self.sign_tx(29, values, payload, attrs, api_key_index)
    }

    fn sign_tx(
        &self,
        tx_type: u64,
        values: Vec<i128>,
        payload: serde_json::Value,
        attributes: Vec<(u64, u64)>,
        api_key_index: u64,
    ) -> Result<LighterSignedTransaction> {
        let private_key = self.private_key(api_key_index)?;
        let (tx_type, tx_info, tx_hash) =
            sign_payload(tx_type, values, payload, attributes, private_key)?;
        Ok(LighterSignedTransaction {
            tx_type,
            tx_info,
            tx_hash,
        })
    }

    fn market_index(&self, params: &LighterParams) -> Result<i64> {
        if let Some(product_symbol) = params.get("product_symbol") {
            return self
                .market_id(product_symbol)?
                .parse::<i64>()
                .map_err(|error| {
                    DcexError::InvalidInput(format!("invalid Lighter market id: {error}"))
                });
        }
        params.required_i64("market_index")
    }
}
