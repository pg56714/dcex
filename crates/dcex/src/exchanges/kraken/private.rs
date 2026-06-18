use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::KrakenClient;
use super::params::KrakenParams;

impl KrakenClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = KrakenParams::from_pairs(params);

        if let Some(result) = self.account_private_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self.trade_private_request(method_name, &params).await? {
            return Ok(result);
        }

        Err(DcexError::InvalidInput(format!(
            "unsupported Kraken private method: {method_name}"
        )))
    }
}
