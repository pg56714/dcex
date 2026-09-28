use super::client::OndoClient;
use super::params::OndoParams;
use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

impl OndoClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        crate::exchanges::input_contracts::pairs("ondo", method_name, &params)?;
        let params = super::super::operation_guards::validate("ondo", method_name, params)?;
        let params = OndoParams::from_pairs(params);
        if let Some(response) = self.account_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.trade_private_request(method_name, &params).await? {
            return Ok(response);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported Ondo private method: {method_name}"
        )))
    }
}
