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
        crate::exchanges::input_contracts::pairs("bitget", method_name, &params)?;
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
