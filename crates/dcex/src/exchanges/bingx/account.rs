use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::BingxClient;
use super::endpoints::*;
use super::params::{
    push_optional, require_pair_or_identifier, validate_enum, validate_positive_number,
    validate_time_range, validate_u64_range, BingxParams,
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
