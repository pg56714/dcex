pub(in crate::exchanges::okx) use serde_json::Value;

pub(in crate::exchanges::okx) use crate::Result;
pub(in crate::exchanges::okx) use crate::exchange::ValidatedResponse;

pub(in crate::exchanges::okx) use super::client::OkxClient;
pub(in crate::exchanges::okx) use super::endpoints::*;
pub(in crate::exchanges::okx) use super::params::{OkxParams, push_optional_owned};

impl OkxClient {
    pub(super) async fn asset_private_request(
        &self,
        method_name: &str,
        params: &OkxParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_currencies" => {
                params.ensure_allowed(&["ccy"])?;
                let mut query = Vec::new();
                push_optional_owned(&mut query, "ccy", params.csv("ccy")?);
                self.get_request(ASSET_CURRENCIES, query).await
            }
            "get_balances" => {
                params.ensure_allowed(&["ccy"])?;
                let mut query = Vec::new();
                push_optional_owned(&mut query, "ccy", params.csv("ccy")?);
                self.get_request(ASSET_BALANCES, query).await
            }
            "get_asset_valuation" => {
                params.ensure_allowed(&["ccy"])?;
                let mut query = Vec::new();
                push_optional_owned(&mut query, "ccy", params.csv("ccy")?);
                self.get_request(ASSET_VALUATION, query).await
            }
            "funds_transfer" => self.dispatch_funds_transfer(method_name, params).await,
            "get_transfer_state" => self.dispatch_get_transfer_state(method_name, params).await,
            "get_bills" => {
                params.ensure_allowed(&[
                    "ccy",
                    "type",
                    "thirdPartyType",
                    "clientId",
                    "after",
                    "before",
                    "limit",
                ])?;
                self.get_request(
                    ASSET_BILLS,
                    params.only(&[
                        "ccy",
                        "type",
                        "thirdPartyType",
                        "clientId",
                        "after",
                        "before",
                        "limit",
                    ]),
                )
                .await
            }
            "get_deposit_address" => {
                params.ensure_allowed(&["ccy"])?;
                self.get_request(ASSET_DEPOSIT_ADDRESS, params.required_only(&["ccy"])?)
                    .await
            }
            "get_deposit_history" => {
                params.ensure_allowed(&[
                    "ccy", "depId", "fromWdId", "txId", "type", "state", "after", "before", "limit",
                ])?;
                self.get_request(
                    ASSET_DEPOSIT_HISTORY,
                    params.only(&[
                        "ccy", "depId", "fromWdId", "txId", "type", "state", "after", "before",
                        "limit",
                    ]),
                )
                .await
            }
            "get_deposit_withdraw_status" => {
                self.dispatch_get_deposit_withdraw_status(method_name, params)
                    .await
            }
            "get_exchange_list" => {
                params.ensure_allowed(&[])?;
                self.get_request(ASSET_EXCHANGE_LIST, Vec::new()).await
            }
            "post_monthly_statement" => {
                params.ensure_allowed(&["month"])?;
                self.post_request(
                    ASSET_MONTHLY_STATEMENT,
                    Value::Object(params.body(&["month"])),
                )
                .await
            }
            "get_monthly_statement" => {
                params.ensure_allowed(&["month"])?;
                self.get_request(ASSET_MONTHLY_STATEMENT, params.required_only(&["month"])?)
                    .await
            }
            "get_convert_currencies" => {
                params.ensure_allowed(&[])?;
                self.get_request(ASSET_CONVERT_CURRENCIES, Vec::new()).await
            }
            "get_convert_history" => {
                params.ensure_allowed(&["clTReqId", "after", "before", "limit", "tag"])?;
                self.get_request(
                    ASSET_CONVERT_HISTORY,
                    params.only(&["clTReqId", "after", "before", "limit", "tag"]),
                )
                .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
