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
        if let Some(result) = self
            .launchpool_private_request(method_name, &params)
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self.rwa_earn_private_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self.byusdt_private_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self
            .hold_to_earn_private_request(method_name, &params)
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .fixed_earn_private_request(method_name, &params)
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .liquidity_mining_private_request(method_name, &params)
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .advanced_earn_private_request(method_name, &params)
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self.account_private_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self.asset_private_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self.earn_private_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self.rfq_private_request(method_name, &params).await? {
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
