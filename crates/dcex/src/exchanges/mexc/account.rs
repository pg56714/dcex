use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::MexcClient;
use super::endpoints::*;
use super::params::{
    add_pagination_defaults, insert_number, validate_enum, validate_u64_range, MexcParams,
};

impl MexcClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &MexcParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_kyc_status" => {
                params.ensure_allowed(&["recvWindow"])?;
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_KYC_STATUS,
                    params.only(&["recvWindow"]),
                )
                .await
            }
            "get_spot_self_symbols" => {
                params.ensure_allowed(&["recvWindow"])?;
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_SELF_SYMBOLS,
                    params.only(&["recvWindow"]),
                )
                .await
            }
            "get_spot_account" => {
                params.ensure_allowed(&["recvWindow"])?;
                self.spot_private(HttpMethod::Get, SPOT_ACCOUNT, params.only(&["recvWindow"]))
                    .await
            }
            "get_spot_mx_deduct_status" => {
                params.ensure_allowed(&["recvWindow"])?;
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_MX_DEDUCT_ENABLE,
                    params.only(&["recvWindow"]),
                )
                .await
            }
            "set_spot_mx_deduct" => {
                params.ensure_allowed(&["mxDeductEnable", "recvWindow"])?;
                params.required("mxDeductEnable")?;
                validate_enum(params, "mxDeductEnable", &["true", "false"])?;
                self.spot_private(
                    HttpMethod::Post,
                    SPOT_MX_DEDUCT_ENABLE,
                    params.only(&["mxDeductEnable", "recvWindow"]),
                )
                .await
            }
            "get_spot_symbol_commission" => {
                params.ensure_allowed(&["product_symbol", "symbol", "recvWindow"])?;
                let mut query = params.only(&["recvWindow"]);
                self.push_required_product_symbol(&mut query, params, "")?;
                self.spot_private(HttpMethod::Get, SPOT_SYMBOL_COMMISSION, query)
                    .await
            }
            "get_currency_info" => {
                params.ensure_allowed(&["recvWindow"])?;
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_CURRENCY_INFO,
                    params.only(&["recvWindow"]),
                )
                .await
            }
            "get_deposit_history" => {
                params.ensure_allowed(&[
                    "coin",
                    "status",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ])?;
                validate_u64_range(params, "status", 1, 12)?;
                validate_u64_range(params, "limit", 1, 1_000)?;
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_DEPOSIT_HISTORY,
                    params.only(&[
                        "coin",
                        "status",
                        "startTime",
                        "endTime",
                        "limit",
                        "recvWindow",
                    ]),
                )
                .await
            }
            "get_withdraw_history" => {
                params.ensure_allowed(&[
                    "coin",
                    "status",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ])?;
                validate_u64_range(params, "status", 1, 10)?;
                validate_u64_range(params, "limit", 1, 1_000)?;
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_WITHDRAW_HISTORY,
                    params.only(&[
                        "coin",
                        "status",
                        "startTime",
                        "endTime",
                        "limit",
                        "recvWindow",
                    ]),
                )
                .await
            }
            "get_deposit_address" => {
                params.ensure_allowed(&["coin", "network", "recvWindow"])?;
                params.required("coin")?;
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_DEPOSIT_ADDRESS,
                    params.only(&["coin", "network", "recvWindow"]),
                )
                .await
            }
            "user_universal_transfer" => {
                params.ensure_allowed(&[
                    "fromAccountType",
                    "toAccountType",
                    "asset",
                    "amount",
                    "recvWindow",
                ])?;
                for key in ["fromAccountType", "toAccountType", "asset", "amount"] {
                    params.required(key)?;
                }
                validate_enum(params, "fromAccountType", &["SPOT", "FUTURES"])?;
                validate_enum(params, "toAccountType", &["SPOT", "FUTURES"])?;
                self.spot_private(
                    HttpMethod::Post,
                    SPOT_USER_UNIVERSAL_TRANSFER,
                    params.only(&[
                        "fromAccountType",
                        "toAccountType",
                        "asset",
                        "amount",
                        "recvWindow",
                    ]),
                )
                .await
            }
            "get_user_universal_transfer_history" => {
                params.ensure_allowed(&[
                    "fromAccountType",
                    "toAccountType",
                    "startTime",
                    "endTime",
                    "page",
                    "size",
                    "recvWindow",
                ])?;
                params.required("fromAccountType")?;
                params.required("toAccountType")?;
                validate_enum(params, "fromAccountType", &["SPOT", "FUTURES"])?;
                validate_enum(params, "toAccountType", &["SPOT", "FUTURES"])?;
                validate_u64_range(params, "page", 1, u64::MAX)?;
                validate_u64_range(params, "size", 1, 100)?;
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_USER_UNIVERSAL_TRANSFER,
                    params.only(&[
                        "fromAccountType",
                        "toAccountType",
                        "startTime",
                        "endTime",
                        "page",
                        "size",
                        "recvWindow",
                    ]),
                )
                .await
            }
            "get_user_universal_transfer_by_id" => {
                params.ensure_allowed(&["tranId", "recvWindow"])?;
                params.required("tranId")?;
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_USER_UNIVERSAL_TRANSFER_BY_ID,
                    params.only(&["tranId", "recvWindow"]),
                )
                .await
            }
            "get_internal_transfer_history" => {
                params.ensure_allowed(&[
                    "tranId",
                    "startTime",
                    "endTime",
                    "page",
                    "limit",
                    "recvWindow",
                ])?;
                validate_u64_range(params, "page", 1, u64::MAX)?;
                validate_u64_range(params, "limit", 1, u64::MAX)?;
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_INTERNAL_TRANSFER_HISTORY,
                    params.only(&[
                        "tranId",
                        "startTime",
                        "endTime",
                        "page",
                        "limit",
                        "recvWindow",
                    ]),
                )
                .await
            }
            "get_contract_assets" => {
                params.ensure_allowed(&[])?;
                self.contract_get(CONTRACT_ASSETS, Vec::new()).await
            }
            "get_contract_asset" => {
                params.ensure_allowed(&["currency"])?;
                let path = CONTRACT_ASSET.replace("{currency}", params.required("currency")?);
                self.contract_get(&path, Vec::new()).await
            }
            "get_contract_transfer_records" => {
                params.ensure_allowed(&["currency", "state", "type", "page_num", "page_size"])?;
                validate_enum(params, "state", &["WAIT", "SUCCESS", "FAILED"])?;
                validate_enum(params, "type", &["IN", "OUT"])?;
                validate_u64_range(params, "page_num", 1, u64::MAX)?;
                validate_u64_range(params, "page_size", 1, 100)?;
                let mut query =
                    params.only(&["currency", "state", "type", "page_num", "page_size"]);
                add_pagination_defaults(&mut query);
                self.contract_get(CONTRACT_TRANSFER_RECORDS, query).await
            }
            "get_contract_history_positions" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "type",
                    "start_time",
                    "end_time",
                    "position_type",
                    "page_num",
                    "page_size",
                ])?;
                validate_enum(params, "type", &["1", "2"])?;
                validate_enum(params, "position_type", &["1", "2"])?;
                validate_u64_range(params, "page_num", 1, u64::MAX)?;
                validate_u64_range(params, "page_size", 1, 100)?;
                let mut query = params.only(&[
                    "type",
                    "start_time",
                    "end_time",
                    "position_type",
                    "page_num",
                    "page_size",
                ]);
                self.push_product_symbol(&mut query, params, "_")?;
                add_pagination_defaults(&mut query);
                self.contract_get(CONTRACT_HISTORY_POSITIONS, query).await
            }
            "get_contract_open_positions" => {
                params.ensure_allowed(&["product_symbol", "symbol", "positionId"])?;
                let mut query = params.only(&["positionId"]);
                self.push_product_symbol(&mut query, params, "_")?;
                self.contract_get(CONTRACT_OPEN_POSITIONS, query).await
            }
            "get_contract_funding_records" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "position_id",
                    "position_type",
                    "start_time",
                    "end_time",
                    "page_num",
                    "page_size",
                ])?;
                validate_enum(params, "position_type", &["1", "2"])?;
                validate_u64_range(params, "page_num", 1, u64::MAX)?;
                validate_u64_range(params, "page_size", 1, 100)?;
                let mut query = params.only(&[
                    "position_id",
                    "position_type",
                    "start_time",
                    "end_time",
                    "page_num",
                    "page_size",
                ]);
                self.push_product_symbol(&mut query, params, "_")?;
                add_pagination_defaults(&mut query);
                self.contract_get(CONTRACT_FUNDING_RECORDS, query).await
            }
            "get_contract_risk_limits" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_product_symbol(&mut query, params, "_")?;
                self.contract_get(CONTRACT_RISK_LIMITS, query).await
            }
            "get_contract_trading_fee_rate" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_product_symbol(&mut query, params, "_")?;
                self.contract_get(CONTRACT_TRADING_FEE_RATE, query).await
            }
            "get_contract_leverage" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_required_product_symbol(&mut query, params, "_")?;
                self.contract_get(CONTRACT_LEVERAGE, query).await
            }
            "change_contract_margin" => {
                params.ensure_allowed(&["positionId", "amount", "type"])?;
                params.required("positionId")?;
                params.required("amount")?;
                params.required("type")?;
                validate_enum(params, "type", &["ADD", "SUB"])?;
                let body = params.body(&["positionId", "amount", "type"], &["positionId"], &[]);
                self.contract_post_json(CONTRACT_CHANGE_MARGIN, Value::Object(body))
                    .await
            }
            "change_contract_leverage" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "positionId",
                    "leverage",
                    "openType",
                    "positionType",
                    "leverageMode",
                    "marginSelected",
                    "leverageSelected",
                ])?;
                params.required("leverage")?;
                if params.get("positionId").is_none() {
                    params.required("openType")?;
                    params
                        .get("product_symbol")
                        .or_else(|| params.get("symbol"))
                        .ok_or_else(|| {
                            DcexError::InvalidInput(
                                "MEXC symbol is required when positionId is absent".to_string(),
                            )
                        })?;
                    params.required("positionType")?;
                }
                validate_enum(params, "openType", &["1", "2"])?;
                validate_enum(params, "positionType", &["1", "2"])?;
                validate_enum(params, "leverageMode", &["1", "2"])?;
                let mut body = params.body(
                    &[
                        "positionId",
                        "leverage",
                        "openType",
                        "positionType",
                        "leverageMode",
                        "marginSelected",
                        "leverageSelected",
                    ],
                    &[
                        "positionId",
                        "leverage",
                        "openType",
                        "positionType",
                        "leverageMode",
                    ],
                    &["marginSelected", "leverageSelected"],
                );
                self.insert_product_symbol(&mut body, params, "_")?;
                self.contract_post_json(CONTRACT_CHANGE_LEVERAGE, Value::Object(body))
                    .await
            }
            "get_contract_position_mode" => {
                params.ensure_allowed(&[])?;
                self.contract_get(CONTRACT_POSITION_MODE, Vec::new()).await
            }
            "change_contract_position_mode" => {
                params.ensure_allowed(&["positionMode"])?;
                let mut body = serde_json::Map::new();
                validate_enum(params, "positionMode", &["1", "2"])?;
                let position_mode = params.required("positionMode")?.parse().map_err(|error| {
                    DcexError::InvalidInput(format!("invalid positionMode: {error}"))
                })?;
                insert_number(&mut body, "positionMode", position_mode);
                self.contract_post_json(CONTRACT_CHANGE_POSITION_MODE, Value::Object(body))
                    .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
