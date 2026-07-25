use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::MexcClient;
use super::params::{validate_u64_range, MexcParams};

impl MexcClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = MexcParams::from_pairs(params);
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
