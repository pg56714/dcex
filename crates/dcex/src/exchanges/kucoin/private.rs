use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::KucoinClient;
use super::params::KucoinParams;

impl KucoinClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = KucoinParams::from_pairs(params);
        if let Some(result) = self.account_private_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self.trade_private_request(method_name, &params).await? {
            return Ok(result);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported KuCoin private method: {method_name}"
        )))
    }
}
