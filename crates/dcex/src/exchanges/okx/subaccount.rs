pub(in crate::exchanges::okx) use crate::Result;
pub(in crate::exchanges::okx) use crate::exchange::ValidatedResponse;

pub(in crate::exchanges::okx) use super::client::OkxClient;
pub(in crate::exchanges::okx) use super::endpoints::*;
pub(in crate::exchanges::okx) use super::params::{OkxParams, push_optional_owned};

impl OkxClient {
    pub(super) async fn subaccount_private_request(
        &self,
        method_name: &str,
        params: &OkxParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_subaccount_list" => {
                self.get_request(
                    SUBACCOUNT_LIST,
                    params.only(&["enable", "subAcct", "after", "before", "limit"]),
                )
                .await
            }
            "get_subaccount_trading_balance" => {
                self.get_request(
                    SUBACCOUNT_TRADING_BALANCE,
                    params.required_only(&["subAcct"])?,
                )
                .await
            }
            "get_subaccount_funding_balance" => {
                let mut query = params.required_only(&["subAcct"])?;
                push_optional_owned(&mut query, "ccy", params.csv("ccy")?);
                self.get_request(SUBACCOUNT_FUNDING_BALANCE, query).await
            }
            "get_subaccount_bills" => {
                params.required("subAcct")?;
                self.get_request(
                    SUBACCOUNT_BILLS,
                    params.only(&["ccy", "type", "subAcct", "after", "before", "limit"]),
                )
                .await
            }
            "transfer_between_subaccounts" => {
                self.dispatch_transfer_between_subaccounts(method_name, params)
                    .await
            }
            "get_entrusted_subaccount_list" => {
                self.get_request(ENTRUSTED_SUBACCOUNT_LIST, params.only(&["subAcct"]))
                    .await
            }
            "get_subaccount_interest_limits" => {
                params.required("subAcct")?;
                self.get_request(SUBACCOUNT_INTEREST_LIMITS, params.only(&["subAcct", "ccy"]))
                    .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
