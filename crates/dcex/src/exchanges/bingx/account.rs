use crate::Result;
use crate::exchange::ValidatedResponse;

use super::client::BingxClient;
use super::endpoints::*;
use super::params::{
    BingxParams, push_optional, require_pair_or_identifier, validate_enum,
    validate_positive_number, validate_time_range, validate_u64_range,
};

const ACCOUNT_TYPES: &[&str] = &[
    "sopt",
    "stdFutures",
    "coinMPerp",
    "USDTMPerp",
    "copyTrading",
    "grid",
    "eran",
    "c2c",
];

const INCOME_TYPES: &[&str] = &[
    "TRANSFER",
    "REALIZED_PNL",
    "FUNDING_FEE",
    "TRADING_FEE",
    "INSURANCE_CLEAR",
    "TRIAL_FUND",
    "ADL",
    "SYSTEM_DEDUCTION",
    "GTD_PRICE",
];

impl BingxClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &BingxParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_account_balance" | "get_swap_account_balance" => {
                params.ensure_allowed(&["recvWindow"])?;
                validate_recv_window(params)?;
                self.private_get(SWAP_ACCOUNT_BALANCE, params.only(&["recvWindow"]))
                    .await
            }
            "get_swap_commission_rate" => {
                params.ensure_allowed(&["recvWindow"])?;
                validate_recv_window(params)?;
                self.private_get(SWAP_COMMISSION_RATE, params.only(&["recvWindow"]))
                    .await
            }
            "get_spot_account_balance" => {
                params.ensure_allowed(&["recvWindow"])?;
                validate_recv_window(params)?;
                self.private_get(SPOT_ACCOUNT_BALANCE, params.only(&["recvWindow"]))
                    .await
            }
            "get_fund_account_balance" => {
                params.ensure_allowed(&["asset", "recvWindow"])?;
                validate_recv_window(params)?;
                self.private_get(FUND_ACCOUNT_BALANCE, params.only(&["asset", "recvWindow"]))
                    .await
            }
            "get_all_account_balance" => {
                params.ensure_allowed(&["accountType", "recvWindow"])?;
                validate_enum(params, "accountType", ACCOUNT_TYPES)?;
                validate_recv_window(params)?;
                self.private_get(
                    FUND_ALL_ACCOUNT_BALANCE,
                    params.only(&["accountType", "recvWindow"]),
                )
                .await
            }
            "get_account_uid" => {
                params.ensure_allowed(&["recvWindow"])?;
                validate_recv_window(params)?;
                self.private_get(FUND_ACCOUNT_UID, params.only(&["recvWindow"]))
                    .await
            }
            "get_api_key_info" => {
                params.ensure_allowed(&["uid", "apiKey", "recvWindow"])?;
                params.required("uid")?;
                validate_u64_range(params, "uid", 1, u64::MAX)?;
                validate_recv_window(params)?;
                self.private_get(
                    FUND_API_KEY_INFO,
                    params.only(&["uid", "apiKey", "recvWindow"]),
                )
                .await
            }
            "get_transferable_coins" => {
                params.ensure_allowed(&["fromAccount", "toAccount", "recvWindow"])?;
                params.required("fromAccount")?;
                params.required("toAccount")?;
                validate_recv_window(params)?;
                self.private_get(
                    TRANSFERABLE_COINS,
                    params.only(&["fromAccount", "toAccount", "recvWindow"]),
                )
                .await
            }
            "asset_transfer" => {
                params.ensure_allowed(&[
                    "fromAccount",
                    "toAccount",
                    "asset",
                    "amount",
                    "recvWindow",
                ])?;
                params.required("fromAccount")?;
                params.required("toAccount")?;
                params.required("asset")?;
                params.required("amount")?;
                validate_positive_number(params, "amount")?;
                validate_recv_window(params)?;
                self.private_post(
                    ASSET_TRANSFER,
                    params.only(&["fromAccount", "toAccount", "asset", "amount", "recvWindow"]),
                )
                .await
            }
            "get_asset_transfer_records" => {
                params.ensure_allowed(&[
                    "fromAccount",
                    "toAccount",
                    "transferId",
                    "tranId",
                    "startTime",
                    "endTime",
                    "pageIndex",
                    "pageSize",
                    "recvWindow",
                ])?;
                if params.get("transferId").is_none() && params.get("tranId").is_none() {
                    require_pair_or_identifier(params, "fromAccount", "toAccount", "transferId")?;
                }
                validate_u64_range(params, "pageIndex", 1, u64::MAX)?;
                validate_u64_range(params, "pageSize", 1, 100)?;
                validate_u64_range(params, "transferId", 1, u64::MAX)?;
                validate_u64_range(params, "tranId", 1, u64::MAX)?;
                validate_time_range(params, "startTime", "endTime", None)?;
                validate_recv_window(params)?;
                let mut query = params.only(&[
                    "fromAccount",
                    "toAccount",
                    "transferId",
                    "startTime",
                    "endTime",
                    "pageIndex",
                    "pageSize",
                    "recvWindow",
                ]);
                if !query.iter().any(|(key, _)| key == "transferId") {
                    push_optional(&mut query, "transferId", params.get("tranId"));
                }
                self.private_get(TRANSFER_RECORDS, query).await
            }
            "get_subaccounts" => {
                params.ensure_allowed(&[
                    "subUid",
                    "subAccountString",
                    "isFeeze",
                    "page",
                    "limit",
                    "recvWindow",
                ])?;
                params.required("page")?;
                params.required("limit")?;
                validate_enum(params, "isFeeze", &["true", "false"])?;
                validate_u64_range(params, "subUid", 1, u64::MAX)?;
                validate_u64_range(params, "page", 1, u64::MAX)?;
                validate_u64_range(params, "limit", 1, 1000)?;
                validate_recv_window(params)?;
                self.private_get(
                    SUBACCOUNT_LIST,
                    params.only(&[
                        "subUid",
                        "subAccountString",
                        "isFeeze",
                        "page",
                        "limit",
                        "recvWindow",
                    ]),
                )
                .await
            }
            "get_subaccount_assets" => {
                params.ensure_allowed(&["subUid", "recvWindow"])?;
                params.required("subUid")?;
                validate_u64_range(params, "subUid", 1, u64::MAX)?;
                validate_recv_window(params)?;
                self.private_get(SUBACCOUNT_ASSETS, params.only(&["subUid", "recvWindow"]))
                    .await
            }
            "get_subaccount_all_account_balance" => {
                params.ensure_allowed(&[
                    "pageIndex",
                    "pageSize",
                    "subUid",
                    "accountType",
                    "recvWindow",
                ])?;
                params.required("pageIndex")?;
                params.required("pageSize")?;
                validate_u64_range(params, "pageIndex", 1, u64::MAX)?;
                validate_u64_range(params, "pageSize", 1, 10)?;
                validate_u64_range(params, "subUid", 1, u64::MAX)?;
                validate_recv_window(params)?;
                self.private_get(
                    SUBACCOUNT_ALL_ACCOUNT_BALANCE,
                    params.only(&[
                        "pageIndex",
                        "pageSize",
                        "subUid",
                        "accountType",
                        "recvWindow",
                    ]),
                )
                .await
            }
            "get_subaccount_transfer_history" => {
                params.ensure_allowed(&[
                    "uid",
                    "type",
                    "tranId",
                    "startTime",
                    "endTime",
                    "pageId",
                    "pagingSize",
                    "recvWindow",
                ])?;
                params.required("uid")?;
                validate_u64_range(params, "uid", 1, u64::MAX)?;
                validate_u64_range(params, "pageId", 1, u64::MAX)?;
                validate_u64_range(params, "pagingSize", 1, 100)?;
                validate_time_range(params, "startTime", "endTime", None)?;
                validate_recv_window(params)?;
                self.private_get(
                    SUBACCOUNT_TRANSFER_HISTORY,
                    params.only(&[
                        "uid",
                        "type",
                        "tranId",
                        "startTime",
                        "endTime",
                        "pageId",
                        "pagingSize",
                        "recvWindow",
                    ]),
                )
                .await
            }
            "get_subaccount_transferable_amounts" => {
                params.ensure_allowed(&[
                    "fromUid",
                    "fromAccountType",
                    "toUid",
                    "toAccountType",
                    "recvWindow",
                ])?;
                for key in ["fromUid", "fromAccountType", "toUid", "toAccountType"] {
                    params.required(key)?;
                }
                validate_u64_range(params, "fromUid", 1, u64::MAX)?;
                validate_u64_range(params, "toUid", 1, u64::MAX)?;
                validate_u64_range(params, "fromAccountType", 1, 3)?;
                validate_u64_range(params, "toAccountType", 1, 3)?;
                validate_recv_window(params)?;
                self.private_post(
                    SUBACCOUNT_TRANSFERABLE_AMOUNTS,
                    params.only(&[
                        "fromUid",
                        "fromAccountType",
                        "toUid",
                        "toAccountType",
                        "recvWindow",
                    ]),
                )
                .await
            }
            "transfer_subaccount_assets" => {
                params.ensure_allowed(&[
                    "assetName",
                    "transferAmount",
                    "fromUid",
                    "fromType",
                    "fromAccountType",
                    "toUid",
                    "toType",
                    "toAccountType",
                    "remark",
                    "recvWindow",
                ])?;
                for key in [
                    "assetName",
                    "transferAmount",
                    "fromUid",
                    "fromType",
                    "fromAccountType",
                    "toUid",
                    "toType",
                    "toAccountType",
                    "remark",
                ] {
                    params.required(key)?;
                }
                validate_positive_number(params, "transferAmount")?;
                validate_u64_range(params, "fromUid", 1, u64::MAX)?;
                validate_u64_range(params, "toUid", 1, u64::MAX)?;
                validate_u64_range(params, "fromType", 1, 2)?;
                validate_u64_range(params, "toType", 1, 2)?;
                validate_u64_range(params, "fromAccountType", 1, 3)?;
                validate_u64_range(params, "toAccountType", 1, 3)?;
                validate_recv_window(params)?;
                self.private_post(
                    SUBACCOUNT_ASSET_TRANSFER,
                    params.only(&[
                        "assetName",
                        "transferAmount",
                        "fromUid",
                        "fromType",
                        "fromAccountType",
                        "toUid",
                        "toType",
                        "toAccountType",
                        "remark",
                        "recvWindow",
                    ]),
                )
                .await
            }
            "get_open_positions" => {
                params.ensure_allowed(&["product_symbol", "symbol", "recvWindow"])?;
                validate_recv_window(params)?;
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params)?;
                push_optional(&mut query, "recvWindow", params.get("recvWindow"));
                self.private_get(SWAP_OPEN_POSITIONS, query).await
            }
            "get_fund_flow" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "income_type",
                    "start_time",
                    "end_time",
                    "limit",
                    "recvWindow",
                ])?;
                validate_enum(params, "income_type", INCOME_TYPES)?;
                validate_u64_range(params, "limit", 1, 1000)?;
                validate_time_range(params, "start_time", "end_time", None)?;
                validate_recv_window(params)?;
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params)?;
                push_optional(&mut query, "incomeType", params.get("income_type"));
                push_optional(&mut query, "startTime", params.get("start_time"));
                push_optional(&mut query, "endTime", params.get("end_time"));
                push_optional(&mut query, "limit", params.get("limit"));
                push_optional(&mut query, "recvWindow", params.get("recvWindow"));
                self.private_get(SWAP_FUND_FLOW, query).await
            }
            "get_listen_key" => {
                params.ensure_allowed(&[])?;
                self.unsigned_post_with_api_key(SWAP_LISTEN_KEY, Vec::new())
                    .await
            }
            "keep_alive_listen_key" => {
                params.ensure_allowed(&["listen_key"])?;
                self.private_put(
                    SWAP_LISTEN_KEY,
                    vec![(
                        "listenKey".to_string(),
                        params.required("listen_key")?.to_string(),
                    )],
                )
                .await
            }
            "close_listen_key" => {
                params.ensure_allowed(&["listen_key"])?;
                self.private_delete(
                    SWAP_LISTEN_KEY,
                    vec![(
                        "listenKey".to_string(),
                        params.required("listen_key")?.to_string(),
                    )],
                )
                .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}

fn validate_recv_window(params: &BingxParams) -> Result<()> {
    validate_u64_range(params, "recvWindow", 1, 5000)
}
