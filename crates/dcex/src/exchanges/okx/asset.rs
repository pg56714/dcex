use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::OkxClient;
use super::endpoints::*;
use super::params::{
    insert_optional_string, okx_account_id, push_optional_owned, validate_deposit_withdraw_status,
    OkxParams,
};

impl OkxClient {
    pub(super) async fn asset_private_request(
        &self,
        method_name: &str,
        params: &OkxParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_currencies" => {
                let mut query = Vec::new();
                push_optional_owned(&mut query, "ccy", params.csv("ccy")?);
                self.get_request(ASSET_CURRENCIES, query).await
            }
            "get_balances" => {
                let mut query = Vec::new();
                push_optional_owned(&mut query, "ccy", params.csv("ccy")?);
                self.get_request(ASSET_BALANCES, query).await
            }
            "get_asset_valuation" => {
                let mut query = Vec::new();
                push_optional_owned(&mut query, "ccy", params.csv("ccy")?);
                self.get_request(ASSET_VALUATION, query).await
            }
            "funds_transfer" => {
                let mut body = params.required_body(&["ccy", "amt"])?;
                body.insert(
                    "from".to_string(),
                    Value::String(okx_account_id(params.required("from_account")?).to_string()),
                );
                body.insert(
                    "to".to_string(),
                    Value::String(okx_account_id(params.required("to_account")?).to_string()),
                );
                for key in ["type", "subAcct", "loanTrans"] {
                    insert_optional_string(&mut body, key, params.get(key));
                }
                self.post_request(ASSET_TRANSFER, Value::Object(body)).await
            }
            "get_transfer_state" => {
                self.get_request(
                    ASSET_TRANSFER_STATE,
                    params.only(&["transId", "clientId", "type"]),
                )
                .await
            }
            "get_bills" => {
                self.get_request(
                    ASSET_BILLS,
                    params.only(&["type", "clientId", "after", "before", "limit"]),
                )
                .await
            }
            "get_deposit_address" => {
                self.get_request(ASSET_DEPOSIT_ADDRESS, params.required_only(&["ccy"])?)
                    .await
            }
            "get_deposit_history" => {
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
                validate_deposit_withdraw_status(&params)?;
                self.get_request(
                    ASSET_DEPOSIT_WITHDRAW_STATUS,
                    params.only(&["wdId", "txId", "ccy", "to", "chain"]),
                )
                .await
            }
            "get_exchange_list" => self.get_request(ASSET_EXCHANGE_LIST, Vec::new()).await,
            "post_monthly_statement" => {
                self.post_request(
                    ASSET_MONTHLY_STATEMENT,
                    Value::Object(params.body(&["month"])),
                )
                .await
            }
            "get_monthly_statement" => {
                self.get_request(ASSET_MONTHLY_STATEMENT, params.required_only(&["month"])?)
                    .await
            }
            "get_convert_currencies" => {
                self.get_request(ASSET_CONVERT_CURRENCIES, Vec::new()).await
            }
            "get_convert_history" => {
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
