use super::client::BybitClient;
use super::params::BybitParams;
use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

impl BybitClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = BybitParams::from_pairs(params);
        if let Some(result) = self.account_private_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self.asset_private_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self.position_private_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self.trade_private_request(method_name, &params).await? {
            return Ok(result);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported Bybit private method: {method_name}"
        )))
    }
}
