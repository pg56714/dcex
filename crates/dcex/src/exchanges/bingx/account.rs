pub(in crate::exchanges::bingx) use crate::exchange::ValidatedResponse;
pub(in crate::exchanges::bingx) use crate::{DcexError, Result};

pub(in crate::exchanges::bingx) use super::client::BingxClient;
pub(in crate::exchanges::bingx) use super::endpoints::*;
pub(in crate::exchanges::bingx) use super::params::{
    BingxParams, push_optional, validate_enum, validate_time_range, validate_u64_range,
};

pub(in crate::exchanges::bingx) const ACCOUNT_TYPES: &[&str] = &[
    "sopt",
    "stdFutures",
    "coinMPerp",
    "USDTMPerp",
    "copyTrading",
    "grid",
    "eran",
    "c2c",
];

pub(in crate::exchanges::bingx) const INCOME_TYPES: &[&str] = &[
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
                self.dispatch_get_transferable_coins(method_name, params)
                    .await
            }
            "asset_transfer" => self.dispatch_asset_transfer(method_name, params).await,
            "get_asset_transfer_records" => {
                self.dispatch_get_asset_transfer_records(method_name, params)
                    .await
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
                self.dispatch_get_subaccount_transfer_history(method_name, params)
                    .await
            }
            "get_subaccount_transferable_amounts" => {
                self.dispatch_get_subaccount_transferable_amounts(method_name, params)
                    .await
            }
            "transfer_subaccount_assets" => {
                self.dispatch_transfer_subaccount_assets(method_name, params)
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
                    "incomeType",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ])?;
                validate_enum(params, "incomeType", INCOME_TYPES)?;
                validate_u64_range(params, "limit", 1, 1000)?;
                validate_time_range(params, "startTime", "endTime", None)?;
                validate_recv_window(params)?;
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params)?;
                query.extend(params.only(&[
                    "incomeType",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ]));
                self.private_get(SWAP_FUND_FLOW, query).await
            }
            "get_listen_key" => {
                params.ensure_allowed(&[])?;
                self.unsigned_post_with_api_key(SWAP_LISTEN_KEY, Vec::new())
                    .await
            }
            "keep_alive_listen_key" => {
                params.ensure_allowed(&["listenKey"])?;
                self.private_put(SWAP_LISTEN_KEY, params.only(&["listenKey"]))
                    .await
            }
            "close_listen_key" => {
                params.ensure_allowed(&["listenKey"])?;
                self.private_delete(SWAP_LISTEN_KEY, params.only(&["listenKey"]))
                    .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}

pub(in crate::exchanges::bingx) fn validate_recv_window(params: &BingxParams) -> Result<()> {
    validate_u64_range(params, "recvWindow", 1, 5000)
}

impl BingxClient {
    /// Export swap income as the original Excel bytes. JSON errors are validated.
    pub async fn export_swap_income(&self, params: Vec<(String, String)>) -> Result<Vec<u8>> {
        let params = BingxParams::from_pairs(params);
        let fields = [
            "product_symbol",
            "incomeType",
            "startTime",
            "endTime",
            "limit",
            "recvWindow",
        ];
        params.ensure_allowed(&fields)?;
        validate_u64_range(&params, "limit", 1, 1000)?;
        validate_u64_range(&params, "recvWindow", 1, 5000)?;
        validate_time_range(&params, "startTime", "endTime", None)?;
        validate_enum(
            &params,
            "incomeType",
            &[
                "REALIZED_PNL",
                "FUNDING_FEE",
                "TRADING_FEE",
                "INSURANCE_CLEAR",
                "TRIAL_FUND",
                "ADL",
                "SYSTEM_DEDUCTION",
            ],
        )?;
        let mut query = params.only(&fields);
        query.retain(|(k, _)| k != "product_symbol");
        if let Some(symbol) = params.get("product_symbol") {
            query.push(("symbol".into(), self.exchange_symbol(symbol)?));
        }
        let response = self
            .request_raw(
                crate::http::HttpMethod::Get,
                "/openApi/swap/v2/user/income/export",
                query,
                true,
                vec![],
                None,
            )
            .await?;
        response.ensure_success("BingX")?;
        if response
            .headers
            .iter()
            .any(|(k, v)| k.eq_ignore_ascii_case("content-type") && v.contains("json"))
            || response.body.iter().find(|b| !b.is_ascii_whitespace()) == Some(&b'{')
        {
            crate::exchange::ResponseValidator::validate(
                &super::signing::BingxResponseValidator,
                &response,
            )?;
            return Err(DcexError::Decode(
                "BingX income export returned JSON instead of an Excel file".into(),
            ));
        }
        if response.body.is_empty() {
            return Err(DcexError::Decode(
                "BingX income export returned an empty file".into(),
            ));
        }
        Ok(response.body)
    }
}
