use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::BingxClient;
use super::params::BingxParams;

impl BingxClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = super::super::operation_guards::validate("bingx", method_name, params)?;
        let params = BingxParams::from_pairs(params);
        if let Some(response) = self.catalog_request(method_name, &params, false).await? {
            return Ok(response);
        }
        if let Some(response) = self.wallet_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.table_request(method_name, &params, false).await? {
            return Ok(response);
        }
        if let Some(result) = self.trading_controls_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self.account_private_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self.trade_private_request(method_name, &params).await? {
            return Ok(result);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported BingX private method: {method_name}"
        )))
    }
}
