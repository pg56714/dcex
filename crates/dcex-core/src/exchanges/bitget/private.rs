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
        let params = BitgetParams::from_pairs(params);
        if let Some(result) = self.account_private_request(method_name, &params).await? {
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
