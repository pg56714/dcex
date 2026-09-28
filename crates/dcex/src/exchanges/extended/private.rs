use super::client::ExtendedClient;
use super::params::ExtendedParams;
use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

impl ExtendedClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        crate::exchanges::input_contracts::pairs("extended", method_name, &params)?;
        let params = ExtendedParams::from_pairs(params);
        if let Some(response) = self
            .portfolio_schema_request(method_name, &params, false)
            .await?
        {
            return Ok(response);
        }
        if let Some(response) = self
            .interest_schema_request(method_name, &params, false)
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
        if let Some(response) = self
            .rewards_schema_request(method_name, &params, false)
            .await?
        {
            return Ok(response);
        }
        if let Some(response) = self.account_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.trade_private_request(method_name, &params).await? {
            return Ok(response);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported Extended private method: {method_name}"
        )))
    }
}
