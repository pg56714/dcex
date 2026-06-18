use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::BitmexClient;
use super::params::BitmexParams;

impl BitmexClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = BitmexParams::from_pairs(params);
        if let Some(response) = self.trade_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.position_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.account_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.trading_private_request(method_name, &params).await? {
            return Ok(response);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported BitMEX private method: {method_name}"
        )))
    }
}
