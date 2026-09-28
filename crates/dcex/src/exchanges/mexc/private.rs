use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::MexcClient;
use super::params::{MexcParams, validate_u64_range};

impl MexcClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = super::super::operation_guards::validate("mexc", method_name, params)?;
        let params = MexcParams::from_pairs(params);
        if let Some(result) = self.field_schema_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self
            .stream_schema_request(method_name, &params, false)
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .wallet_schema_request(method_name, &params, false)
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .market_schema_request(method_name, &params, false)
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .account_schema_request(method_name, &params, false)
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .convert_schema_request(method_name, &params, false)
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .subaccount_schema_request(method_name, &params, false)
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self.stp_schema_request(method_name, &params, false).await? {
            return Ok(result);
        }
        validate_u64_range(&params, "recvWindow", 1, 60_000)?;
        if let Some(result) = self.account_private_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self.trade_private_request(method_name, &params).await? {
            return Ok(result);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported MEXC private method: {method_name}"
        )))
    }
}
