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
                params.ensure_allowed(&["tx_type", "tx_info", "price_protection"])?;
                params.required_u64_range("tx_type", 0, u8::MAX.into())?;
                params.required("tx_info")?;
                params.optional_bool("price_protection")?;
                let mut body = params.query(&["tx_type", "tx_info", "price_protection"]);
                body.retain(|(_, value)| !value.is_empty());
                Ok(Some(self.post_form(SEND_TX, body).await?))
            }
            "send_tx_batch" => {
                params.ensure_allowed(&["tx_types", "tx_infos"])?;
                params.required("tx_types")?;
                params.required("tx_infos")?;
                Ok(Some(
                    self.post_form(SEND_TX_BATCH, params.query(&["tx_types", "tx_infos"]))
                        .await?,
                ))
            }
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
        params.ensure_allowed(&[
            "market_index",
            "product_symbol",
            "client_order_index",
            "base_amount",
            "price",
            "is_ask",
            "order_type",
            "time_in_force",
            "reduce_only",
            "trigger_price",
            "order_expiry",
            "integrator_account_index",
            "integrator_taker_fee",
            "integrator_maker_fee",
            "self_trade_behavior_mode",
            "self_trade_equality_mode",
            "skip_nonce",
            "nonce",
            "api_key_index",
            "price_protection",
        ])?;
        params.optional_bool("price_protection")?;
        let api_key_index = self.signing_api_key_index(params)?;
        let explicit_nonce = validate_nonce(params)?;
        let nonce = self.next_nonce(explicit_nonce, Some(api_key_index)).await?;
        let expired_at = expiry_ms()?;
        let order_expiry = match params.optional_i64("order_expiry")? {
            Some(-1) | None => order_expiry_ms()? as i64,
            Some(value) => value,
        };
        let market_index = self.market_index(params)?;
        validate_order_market_index(market_index)?;
        let client_order_index =
            required_i64_range(params, "client_order_index", 0, (1_i64 << 48) - 1)?;
        let base_amount = required_i64_range(params, "base_amount", 0, (1_i64 << 48) - 1)?;
        let price = required_i64_range(params, "price", 1, u32::MAX.into())?;
        let is_ask = params.required_bool("is_ask")?;
        let order_type = required_i64_range(params, "order_type", 0, 6)?;
        let time_in_force = required_i64_range(params, "time_in_force", 0, 2)?;
        let reduce_only = params.optional_bool("reduce_only")?.unwrap_or(false);
        let trigger_price =
            optional_i64_range(params, "trigger_price", 0, u32::MAX.into())?.unwrap_or(0);
        validate_create_order(
            market_index,
            base_amount,
            order_type,
            time_in_force,
            reduce_only,
            trigger_price,
            order_expiry,
        )?;
        let attrs = attributes(
            params
                .optional_u64("integrator_account_index")?
                .unwrap_or(0),
            params.optional_u64("integrator_taker_fee")?.unwrap_or(0),
            params.optional_u64("integrator_maker_fee")?.unwrap_or(0),
            params.optional_u64("skip_nonce")?.unwrap_or(0),
            255,
            params
                .optional_u64("self_trade_behavior_mode")?
                .unwrap_or(0),
            params
                .optional_u64("self_trade_equality_mode")?
                .unwrap_or(0),
        )?;
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
        params.ensure_allowed(&[
            "market_index",
            "product_symbol",
            "order_index",
            "skip_nonce",
            "nonce",
            "api_key_index",
            "price_protection",
        ])?;
        params.optional_bool("price_protection")?;
        let api_key_index = self.signing_api_key_index(params)?;
        let explicit_nonce = validate_nonce(params)?;
        let nonce = self.next_nonce(explicit_nonce, Some(api_key_index)).await?;
        let expired_at = expiry_ms()?;
        let market_index = self.market_index(params)?;
        validate_order_market_index(market_index)?;
        let order_index = required_i64_range(params, "order_index", 1, (1_i64 << 60) - 1)?;
        let attrs = attributes(
            0,
            0,
            0,
            params.optional_u64("skip_nonce")?.unwrap_or(0),
            255,
            0,
            0,
        )?;
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
        params.ensure_allowed(&[
            "market_index",
            "product_symbol",
            "order_index",
            "base_amount",
            "price",
            "trigger_price",
            "integrator_account_index",
            "integrator_taker_fee",
            "integrator_maker_fee",
            "self_trade_behavior_mode",
            "self_trade_equality_mode",
            "skip_nonce",
            "nonce",
            "api_key_index",
            "price_protection",
        ])?;
        params.optional_bool("price_protection")?;
        let api_key_index = self.signing_api_key_index(params)?;
        let explicit_nonce = validate_nonce(params)?;
        let nonce = self.next_nonce(explicit_nonce, Some(api_key_index)).await?;
        let expired_at = expiry_ms()?;
        let market_index = self.market_index(params)?;
        validate_order_market_index(market_index)?;
        let order_index = required_i64_range(params, "order_index", 1, (1_i64 << 60) - 1)?;
        let base_amount = required_i64_range(params, "base_amount", 0, (1_i64 << 48) - 1)?;
        let price = required_i64_range(params, "price", 1, u32::MAX.into())?;
        let trigger_price =
            optional_i64_range(params, "trigger_price", 0, u32::MAX.into())?.unwrap_or(0);
        let attrs = attributes(
            params
                .optional_u64("integrator_account_index")?
                .unwrap_or(0),
            params.optional_u64("integrator_taker_fee")?.unwrap_or(0),
            params.optional_u64("integrator_maker_fee")?.unwrap_or(0),
            params.optional_u64("skip_nonce")?.unwrap_or(0),
            255,
            params
                .optional_u64("self_trade_behavior_mode")?
                .unwrap_or(0),
            params
                .optional_u64("self_trade_equality_mode")?
                .unwrap_or(0),
        )?;
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
        params.ensure_allowed(&[
            "time_in_force",
            "timestamp_ms",
            "cancel_all_market_index",
            "skip_nonce",
            "nonce",
            "api_key_index",
            "price_protection",
        ])?;
        params.optional_bool("price_protection")?;
        let api_key_index = self.signing_api_key_index(params)?;
        let explicit_nonce = validate_nonce(params)?;
        let nonce = self.next_nonce(explicit_nonce, Some(api_key_index)).await?;
        let expired_at = expiry_ms()?;
        let time_in_force = required_i64_range(params, "time_in_force", 0, 2)?;
        let timestamp_ms = params.required_i64("timestamp_ms")?;
        let cancel_all_market_index = params
            .optional_u64("cancel_all_market_index")?
            .unwrap_or(255);
        validate_cancel_all(time_in_force, timestamp_ms, cancel_all_market_index)?;
        let attrs = attributes(
            0,
            0,
            0,
            params.optional_u64("skip_nonce")?.unwrap_or(0),
            cancel_all_market_index,
            0,
            0,
        )?;
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
        params.ensure_allowed(&[
            "market_index",
            "product_symbol",
            "fraction",
            "margin_mode",
            "skip_nonce",
            "nonce",
            "api_key_index",
            "price_protection",
        ])?;
        params.optional_bool("price_protection")?;
        let api_key_index = self.signing_api_key_index(params)?;
        let explicit_nonce = validate_nonce(params)?;
        let nonce = self.next_nonce(explicit_nonce, Some(api_key_index)).await?;
        let expired_at = expiry_ms()?;
        let market_index = self.market_index(params)?;
        validate_perps_market_index(market_index)?;
        let fraction = required_i64_range(params, "fraction", 1, 10_000)?;
        let margin_mode = required_i64_range(params, "margin_mode", 0, 1)?;
        let attrs = attributes(
            0,
            0,
            0,
            params.optional_u64("skip_nonce")?.unwrap_or(0),
            255,
            0,
            0,
        )?;
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
        params.ensure_allowed(&[
            "market_index",
            "product_symbol",
            "usdc_amount",
            "direction",
            "skip_nonce",
            "nonce",
            "api_key_index",
            "price_protection",
        ])?;
        params.optional_bool("price_protection")?;
        let api_key_index = self.signing_api_key_index(params)?;
        let explicit_nonce = validate_nonce(params)?;
        let nonce = self.next_nonce(explicit_nonce, Some(api_key_index)).await?;
        let expired_at = expiry_ms()?;
        let market_index = self.market_index(params)?;
        validate_perps_market_index(market_index)?;
        let usdc_amount = params.required_i64("usdc_amount")?;
        let amount_magnitude = usdc_amount.checked_abs().ok_or_else(|| {
            DcexError::InvalidInput("Lighter usdc_amount is outside the valid range".to_string())
        })?;
        if !(1..=(1_i64 << 60) - 1).contains(&amount_magnitude) {
            return Err(DcexError::InvalidInput(
                "Lighter usdc_amount magnitude must be between 1 and 1152921504606846975"
                    .to_string(),
            ));
        }
        let direction = required_i64_range(params, "direction", 0, 1)?;
        let attrs = attributes(
            0,
            0,
            0,
            params.optional_u64("skip_nonce")?.unwrap_or(0),
            255,
            0,
            0,
        )?;
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
        if params.get("product_symbol").is_some() && params.get("market_index").is_some() {
            return Err(DcexError::InvalidInput(
                "Lighter accepts either market_index or product_symbol, not both".to_string(),
            ));
        }
        if let Some(product_symbol) = params.get("product_symbol") {
            params.required("product_symbol")?;
            return self
                .market_id(product_symbol)?
                .parse::<i64>()
                .map_err(|error| {
                    DcexError::InvalidInput(format!("invalid Lighter market id: {error}"))
                });
        }
        params.required_i64("market_index")
    }

    fn signing_api_key_index(&self, params: &LighterParams) -> Result<u64> {
        let api_key_index = self.private_api_key_index(params.optional_u64("api_key_index")?)?;
        if api_key_index > 254 {
            return Err(DcexError::InvalidInput(
                "Lighter signing api_key_index must be between 0 and 254".to_string(),
            ));
        }
        let account_index = self.private_account_index(None)?;
        if account_index > (1 << 48) - 2 {
            return Err(DcexError::InvalidInput(
                "Lighter account_index is outside the valid range".to_string(),
            ));
        }
        self.private_key(api_key_index)?;
        Ok(api_key_index)
    }
}

fn validate_nonce(params: &LighterParams) -> Result<Option<i64>> {
    let nonce = params.optional_i64("nonce")?;
    if matches!(nonce, Some(value) if value < 0) {
        return Err(DcexError::InvalidInput(
            "Lighter nonce must be non-negative".to_string(),
        ));
    }
    Ok(nonce)
}

fn required_i64_range(params: &LighterParams, key: &str, min: i64, max: i64) -> Result<i64> {
    let value = params.required_i64(key)?;
    if value < min || value > max {
        return Err(DcexError::InvalidInput(format!(
            "Lighter parameter {key} must be between {min} and {max}"
        )));
    }
    Ok(value)
}

fn optional_i64_range(
    params: &LighterParams,
    key: &str,
    min: i64,
    max: i64,
) -> Result<Option<i64>> {
    let value = params.optional_i64(key)?;
    if matches!(value, Some(value) if value < min || value > max) {
        return Err(DcexError::InvalidInput(format!(
            "Lighter parameter {key} must be between {min} and {max}"
        )));
    }
    Ok(value)
}

fn validate_order_market_index(market_index: i64) -> Result<()> {
    if (0..=254).contains(&market_index) || (2048..=4094).contains(&market_index) {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(
            "Lighter order market_index must identify a perpetual or spot market".to_string(),
        ))
    }
}

fn validate_perps_market_index(market_index: i64) -> Result<()> {
    if (0..=254).contains(&market_index) {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(
            "Lighter margin market_index must be between 0 and 254".to_string(),
        ))
    }
}

fn validate_create_order(
    market_index: i64,
    base_amount: i64,
    order_type: i64,
    time_in_force: i64,
    reduce_only: bool,
    trigger_price: i64,
    order_expiry: i64,
) -> Result<()> {
    let is_spot = (2048..=4094).contains(&market_index);
    if !reduce_only && base_amount == 0 {
        return Err(DcexError::InvalidInput(
            "Lighter base_amount must be positive unless reduce_only is true".to_string(),
        ));
    }
    if is_spot && reduce_only {
        return Err(DcexError::InvalidInput(
            "Lighter spot orders cannot be reduce-only".to_string(),
        ));
    }
    if order_expiry < 0 {
        return Err(DcexError::InvalidInput(
            "Lighter order_expiry is outside the valid range".to_string(),
        ));
    }
    let valid = match order_type {
        0 => {
            trigger_price == 0
                && ((time_in_force == 0 && order_expiry == 0)
                    || (time_in_force != 0 && order_expiry != 0))
        }
        1 => time_in_force == 0 && order_expiry == 0 && trigger_price == 0,
        2 | 4 => !is_spot && time_in_force == 0 && trigger_price != 0 && order_expiry != 0,
        3 | 5 => !is_spot && trigger_price != 0 && order_expiry != 0,
        6 => time_in_force == 1 && trigger_price == 0 && order_expiry != 0,
        _ => false,
    };
    if !valid {
        return Err(DcexError::InvalidInput(
            "Lighter order type, time-in-force, trigger price, and expiry combination is invalid"
                .to_string(),
        ));
    }
    Ok(())
}

fn validate_cancel_all(
    time_in_force: i64,
    timestamp_ms: i64,
    cancel_all_market_index: u64,
) -> Result<()> {
    if cancel_all_market_index > 255 {
        return Err(DcexError::InvalidInput(
            "Lighter cancel_all_market_index must be between 0 and 255".to_string(),
        ));
    }
    if cancel_all_market_index != 255 && time_in_force != 0 {
        return Err(DcexError::InvalidInput(
            "Lighter market-specific cancel-all must use immediate time-in-force".to_string(),
        ));
    }
    let valid = match time_in_force {
        0 | 2 => timestamp_ms == 0,
        1 => timestamp_ms > 0,
        _ => false,
    };
    if !valid {
        return Err(DcexError::InvalidInput(
            "Lighter cancel-all timestamp does not match time_in_force".to_string(),
        ));
    }
    Ok(())
}
