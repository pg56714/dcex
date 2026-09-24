use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::OkxClient;
use super::endpoints::*;
use super::params::{insert_optional_bool, okx_account_id, push_optional_owned, OkxParams};

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
                let mut body =
                    params.required_body(&["ccy", "amt", "fromSubAccount", "toSubAccount"])?;
                body.insert(
                    "from".to_string(),
                    Value::String(okx_account_id(params.required("from_account")?).to_string()),
                );
                body.insert(
                    "to".to_string(),
                    Value::String(okx_account_id(params.required("to_account")?).to_string()),
                );
                insert_optional_bool(&mut body, "loanTrans", params.get("loanTrans"))?;
                insert_optional_bool(&mut body, "omitPosRisk", params.get("omitPosRisk"))?;
                self.post_request(SUBACCOUNT_TRANSFER, Value::Object(body))
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
