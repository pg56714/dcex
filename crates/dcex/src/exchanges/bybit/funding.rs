pub(in crate::exchanges::bybit) use super::client::BybitClient;
pub(in crate::exchanges::bybit) use super::endpoints::*;
pub(in crate::exchanges::bybit) use super::params::{BybitParams, push_optional, string_body};
pub(in crate::exchanges::bybit) use crate::Result;
pub(in crate::exchanges::bybit) use crate::exchange::ValidatedResponse;

impl BybitClient {
    pub(super) async fn asset_private_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_coin_info" => {
                params.ensure_allowed(&["coin"])?;
                self.get_request(GET_COIN_INFO, params.only(&["coin"]))
                    .await
            }
            "get_sub_uid" => {
                params.ensure_allowed(&[])?;
                self.get_request(GET_SUB_UID, Vec::new()).await
            }
            "get_spot_asset_info" => {
                params.ensure_allowed(&["coin"])?;
                let mut query = vec![("accountType".to_string(), "SPOT".to_string())];
                push_optional(&mut query, "coin", params.get("coin"));
                self.get_request(GET_SPOT_ASSET_INFO, query).await
            }
            "get_coins_balance" => {
                params.ensure_allowed(&["accountType", "coin", "memberId", "withBonus"])?;
                let mut query = vec![(
                    "accountType".to_string(),
                    params.required("accountType")?.to_string(),
                )];
                push_optional(&mut query, "coin", params.get("coin"));
                push_optional(&mut query, "memberId", params.get("memberId"));
                push_optional(&mut query, "withBonus", params.get("withBonus"));
                self.get_request(GET_ALL_COINS_BALANCE, query).await
            }
            "get_coin_balance" => {
                params.ensure_allowed(&[
                    "accountType",
                    "coin",
                    "memberId",
                    "toMemberId",
                    "toAccountType",
                    "withBonus",
                    "withTransferSafeAmount",
                    "withLtvTransferSafeAmount",
                ])?;
                let mut query = vec![
                    (
                        "accountType".to_string(),
                        params.required("accountType")?.to_string(),
                    ),
                    ("coin".to_string(), params.required("coin")?.to_string()),
                ];
                push_optional(&mut query, "memberId", params.get("memberId"));
                push_optional(&mut query, "toMemberId", params.get("toMemberId"));
                push_optional(&mut query, "toAccountType", params.get("toAccountType"));
                push_optional(&mut query, "withBonus", params.get("withBonus"));
                push_optional(
                    &mut query,
                    "withTransferSafeAmount",
                    params.get("withTransferSafeAmount"),
                );
                push_optional(
                    &mut query,
                    "withLtvTransferSafeAmount",
                    params.get("withLtvTransferSafeAmount"),
                );
                self.get_request(GET_SINGLE_COIN_BALANCE, query).await
            }
            "get_withdrawable_amount" => {
                self.dispatch_get_withdrawable_amount(method_name, params)
                    .await
            }
            "get_internal_transfer_records" => {
                self.dispatch_get_internal_transfer_records(method_name, params)
                    .await
            }
            "get_transferable_coin" => {
                self.dispatch_get_transferable_coin(method_name, params)
                    .await
            }
            "create_internal_transfer" => {
                self.dispatch_create_internal_transfer(method_name, params)
                    .await
            }
            "create_universal_transfer" => {
                self.dispatch_create_universal_transfer(method_name, params)
                    .await
            }
            "get_universal_transfer_records" => {
                self.dispatch_get_universal_transfer_records(method_name, params)
                    .await
            }
            "set_deposit_account" => {
                params.ensure_allowed(&["accountType"])?;
                let body = string_body(&[("accountType", params.required("accountType")?)]);
                self.post_request(SET_DEPOSIT_ACCOUNT, body).await
            }
            "get_deposit_records" => {
                params.ensure_allowed(&[
                    "limit",
                    "id",
                    "txID",
                    "coin",
                    "startTime",
                    "endTime",
                    "cursor",
                ])?;
                let mut query = vec![(
                    "limit".to_string(),
                    params.get("limit").unwrap_or("20").to_string(),
                )];
                push_optional(&mut query, "id", params.get("id"));
                push_optional(&mut query, "txID", params.get("txID"));
                push_optional(&mut query, "coin", params.get("coin"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                push_optional(&mut query, "endTime", params.get("endTime"));
                push_optional(&mut query, "cursor", params.get("cursor"));
                self.get_request(GET_DEPOSIT_RECORDS, query).await
            }
            "get_sub_deposit_records" => {
                params.ensure_allowed(&[
                    "subMemberId",
                    "limit",
                    "id",
                    "txID",
                    "coin",
                    "startTime",
                    "endTime",
                    "cursor",
                ])?;
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
                push_optional(&mut query, "id", params.get("id"));
                push_optional(&mut query, "txID", params.get("txID"));
                push_optional(&mut query, "coin", params.get("coin"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                push_optional(&mut query, "endTime", params.get("endTime"));
                push_optional(&mut query, "cursor", params.get("cursor"));
                self.get_request(GET_SUB_ACCOUNT_DEPOSIT_RECORDS, query)
                    .await
            }
            "get_internal_deposit_records" => {
                params.ensure_allowed(&[
                    "limit",
                    "txID",
                    "coin",
                    "startTime",
                    "endTime",
                    "cursor",
                ])?;
                let mut query = vec![(
                    "limit".to_string(),
                    params.get("limit").unwrap_or("20").to_string(),
                )];
                push_optional(&mut query, "txID", params.get("txID"));
                push_optional(&mut query, "coin", params.get("coin"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                push_optional(&mut query, "endTime", params.get("endTime"));
                push_optional(&mut query, "cursor", params.get("cursor"));
                self.get_request(GET_INTERNAL_DEPOSIT_RECORDS, query).await
            }
            "get_master_deposit_address" => {
                params.ensure_allowed(&["coin", "chainType"])?;
                let mut query = vec![("coin".to_string(), params.required("coin")?.to_string())];
                push_optional(&mut query, "chainType", params.get("chainType"));
                self.get_request(GET_MASTER_DEPOSIT_ADDRESS, query).await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
