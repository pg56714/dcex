use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::BitgetClient;
use super::params::BitgetParams;

impl BitgetClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let method_name = match method_name {
            "close_copy_futures_follower_positions" => {
                "classic_copytrading_future_copytrade_follower_close_positions"
            }
            "close_copy_futures_trader_positions" => {
                "classic_copytrading_future_copytrade_trader_trader_order_close_positions"
            }
            "convert_classic_asset" => "classic_trade",
            "convert_uta_small_assets" => "uta_small_assets_trade",
            "subscribe_classic_elite" => "classic_earn_elite_subscribe",
            "redeem_classic_elite" => "classic_earn_elite_redeem",
            "borrow_classic_earn_loan" => "classic_earn_loan_borrow",
            "repay_classic_earn_loan" => "classic_earn_loan_repay",
            "delete_uta_subaccount" => "uta_delete_sub",
            other => other,
        };
        let params = super::super::operation_guards::validate("bitget", method_name, params)?;
        let params = BitgetParams::from_pairs(params);
        if let Some(response) = self.catalog_request(method_name, &params, false).await? {
            return Ok(response);
        }
        if let Some(response) = self
            .withdrawals_schema_request(method_name, &params)
            .await?
        {
            return Ok(response);
        }
        if let Some(response) = self.subaccount_schema_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.batch_controls_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.table_request(method_name, &params, false).await? {
            return Ok(response);
        }
        if let Some(result) = self
            .trading_controls_request(method_name, &params, false)
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self.account_private_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self.earn_private_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self.loan_private_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self.trade_private_request(method_name, &params).await? {
            return Ok(result);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported Bitget private method: {method_name}"
        )))
    }
}
