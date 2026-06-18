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
        let params = BingxParams::from_pairs(params);
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
