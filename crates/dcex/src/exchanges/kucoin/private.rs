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
        if method_name == "cancel_margin_stop_order_by_id_raw" {
            // Official docs omit all request parameters. Preserve the caller's query.
            return self
                .request(
                    crate::http::HttpMethod::Delete,
                    super::client::KucoinMarket::Spot,
                    "/api/v3/hf/margin/stop-order/cancel-by-id",
                    params,
                    None,
                    true,
                )
                .await;
        }
        let method_name = match method_name {
            "get_uta_oes_currency" => "get_uta_oe_scurrency",
            "get_otc_loan_accounts" => "get_accounts",
            other => other,
        };
        let params = super::super::operation_guards::validate("kucoin", method_name, params)?;
        let params = KucoinParams::from_pairs(params);
        if let Some(response) = self.catalog_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.withdrawal_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.table_request(method_name, &params, false).await? {
            return Ok(response);
        }
        if let Some(response) = self.classic_trading_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(result) = self.uta_private_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self.account_private_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self.earn_private_request(method_name, &params).await? {
            return Ok(result);
        }
        if let Some(result) = self.margin_private_request(method_name, &params).await? {
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
