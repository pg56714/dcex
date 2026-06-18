use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::GateioClient;
use super::params::GateioParams;

impl GateioClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = GateioParams::from_pairs(params);
        if let Some(result) = self.account_private_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self.trade_private_request(method_name, &params).await? {
            return Ok(result);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported Gate.io private method: {method_name}"
        )))
    }
}
