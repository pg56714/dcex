use super::client::BackpackClient;
use super::params::BackpackParams;
use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

impl BackpackClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = super::super::operation_guards::validate("backpack", method_name, params)?;
        let params = BackpackParams::from_pairs(params);
        if let Some(response) = self.rfq_schema_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self
            .withdrawals_schema_request(method_name, &params)
            .await?
        {
            return Ok(response);
        }
        if let Some(response) = self
            .borrow_lend_schema_request(method_name, &params, false)
            .await?
        {
            return Ok(response);
        }
        if let Some(response) = self
            .prediction_schema_request(method_name, &params, false)
            .await?
        {
            return Ok(response);
        }
        if let Some(response) = self
            .vault_schema_request(method_name, &params, false)
            .await?
        {
            return Ok(response);
        }

        if let Some(response) = self.strategy_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.account_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.rfq_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.trade_private_request(method_name, &params).await? {
            return Ok(response);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported Backpack private method: {method_name}"
        )))
    }
}
