use serde_json::Value;

use super::client::BybitClient;
use super::endpoints::*;
use super::params::{generate_transfer_id, push_optional, string_body, BybitParams};
use crate::exchange::ValidatedResponse;
use crate::Result;

impl BybitClient {
    pub(super) async fn asset_private_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_coin_info" => {
                self.get_request(GET_COIN_INFO, params.only(&["coin"]))
                    .await
            }
            "get_sub_uid" => self.get_request(GET_SUB_UID, Vec::new()).await,
            "get_spot_asset_info" => {
                let mut query = vec![("accountType".to_string(), "SPOT".to_string())];
                push_optional(&mut query, "coin", params.get("coin"));
                self.get_request(GET_SPOT_ASSET_INFO, query).await
            }
            "get_coins_balance" => {
                let mut query = vec![(
                    "accountType".to_string(),
                    params.required("accountType")?.to_string(),
                )];
                push_optional(&mut query, "coin", params.get("coin"));
                push_optional(&mut query, "memberId", params.get("memberId"));
                self.get_request(GET_ALL_COINS_BALANCE, query).await
            }
            "get_coin_balance" => {
                let mut query = vec![
                    (
                        "accountType".to_string(),
                        params.required("accountType")?.to_string(),
                    ),
                    ("coin".to_string(), params.required("coin")?.to_string()),
                ];
                push_optional(&mut query, "memberId", params.get("memberId"));
                push_optional(&mut query, "toAccountType", params.get("toAccountType"));
                self.get_request(GET_SINGLE_COIN_BALANCE, query).await
            }
            "get_withdrawable_amount" => {
                self.get_request(
                    GET_WITHDRAWABLE_AMOUNT,
                    vec![("coin".to_string(), params.required("coin")?.to_string())],
                )
                .await
            }
            "get_internal_transfer_records" => {
                let mut query = vec![(
                    "limit".to_string(),
                    params.get("limit").unwrap_or("20").to_string(),
                )];
                push_optional(&mut query, "coin", params.get("coin"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                self.get_request(GET_INTERNAL_TRANSFER_RECORDS, query).await
            }
            "get_transferable_coin" => {
                let query = vec![
                    (
                        "fromAccountType".to_string(),
                        params.required("fromAccountType")?.to_string(),
                    ),
                    (
                        "toAccountType".to_string(),
                        params.required("toAccountType")?.to_string(),
                    ),
                ];
                self.get_request(GET_TRANSFERABLE_COIN, query).await
            }
            "create_internal_transfer" => {
                let mut body = string_body(&[
                    ("coin", params.required("coin")?),
                    ("amount", params.required("amount")?),
                    ("fromAccountType", params.required("fromAccountType")?),
                    ("toAccountType", params.required("toAccountType")?),
                ]);
                let transfer_id = params
                    .get("transferId")
                    .map(str::to_string)
                    .unwrap_or_else(generate_transfer_id);
                body.insert("transferId".to_string(), Value::String(transfer_id));
                self.post_request(CREATE_INTERNAL_TRANSFER, body).await
            }
            "get_universal_transfer_records" => {
                let mut query = vec![(
                    "limit".to_string(),
                    params.get("limit").unwrap_or("20").to_string(),
                )];
                push_optional(&mut query, "coin", params.get("coin"));
                push_optional(&mut query, "status", params.get("status"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                self.get_request(GET_UNIVERSAL_TRANSFER_RECORDS, query)
                    .await
            }
            "set_deposit_account" => {
                let body = string_body(&[("accountType", params.required("accountType")?)]);
                self.post_request(SET_DEPOSIT_ACCOUNT, body).await
            }
            "get_deposit_records" => {
                let mut query = vec![(
                    "limit".to_string(),
                    params.get("limit").unwrap_or("20").to_string(),
                )];
                push_optional(&mut query, "coin", params.get("coin"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                self.get_request(GET_DEPOSIT_RECORDS, query).await
            }
            "get_sub_deposit_records" => {
                let mut query = vec![
                    (
                        "subMemberId".to_string(),
                        params.required("subMemberId")?.to_string(),
                    ),
                    (
                        "limit".to_string(),
                        params.get("limit").unwrap_or("20").to_string(),
                    ),
                ];
                push_optional(&mut query, "coin", params.get("coin"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                self.get_request(GET_SUB_ACCOUNT_DEPOSIT_RECORDS, query)
                    .await
            }
            "get_internal_deposit_records" => {
                let mut query = vec![(
                    "limit".to_string(),
                    params.get("limit").unwrap_or("20").to_string(),
                )];
                push_optional(&mut query, "coin", params.get("coin"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                self.get_request(GET_INTERNAL_DEPOSIT_RECORDS, query).await
            }
            "get_master_deposit_address" => {
                self.get_request(
                    GET_MASTER_DEPOSIT_ADDRESS,
                    vec![("coin".to_string(), params.required("coin")?.to_string())],
                )
                .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
