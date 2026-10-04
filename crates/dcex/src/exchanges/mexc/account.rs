pub(in crate::exchanges::mexc) use serde_json::Value;

pub(in crate::exchanges::mexc) use crate::exchange::ValidatedResponse;
pub(in crate::exchanges::mexc) use crate::http::HttpMethod;
pub(in crate::exchanges::mexc) use crate::{DcexError, Result};

pub(in crate::exchanges::mexc) use super::client::MexcClient;
pub(in crate::exchanges::mexc) use super::endpoints::*;
pub(in crate::exchanges::mexc) use super::params::{
    MexcParams, add_pagination_defaults, insert_number, validate_enum, validate_u64_range,
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
                self.dispatch_get_withdraw_history(method_name, params)
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
            "get_subaccounts" => {
                params.ensure_allowed(&[
                    "subAccount",
                    "isFreeze",
                    "page",
                    "limit",
                    "recvWindow",
                ])?;
                validate_enum(params, "isFreeze", &["true", "false"])?;
                validate_u64_range(params, "page", 1, u64::MAX)?;
                validate_u64_range(params, "limit", 1, 200)?;
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_SUBACCOUNT_LIST,
                    params.only(&["subAccount", "isFreeze", "page", "limit", "recvWindow"]),
                )
                .await
            }
            "get_subaccount_asset" => {
                params.ensure_allowed(&["subAccount", "accountType", "recvWindow"])?;
                params.required("subAccount")?;
                params.required("accountType")?;
                validate_enum(params, "accountType", &["SPOT"])?;
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_SUBACCOUNT_ASSET,
                    params.only(&["subAccount", "accountType", "recvWindow"]),
                )
                .await
            }
            "transfer_subaccount_assets" => {
                self.dispatch_transfer_subaccount_assets(method_name, params)
                    .await
            }
            "get_subaccount_transfer_history" => {
                self.dispatch_get_subaccount_transfer_history(method_name, params)
                    .await
            }
            "user_universal_transfer" => {
                self.dispatch_user_universal_transfer(method_name, params)
                    .await
            }
            "get_user_universal_transfer_history" => {
                self.dispatch_get_user_universal_transfer_history(method_name, params)
                    .await
            }
            "get_user_universal_transfer_by_id" => {
                self.dispatch_get_user_universal_transfer_by_id(method_name, params)
                    .await
            }
            "get_internal_transfer_history" => {
                self.dispatch_get_internal_transfer_history(method_name, params)
                    .await
            }
            "get_contract_assets" => {
                params.ensure_allowed(&[])?;
                self.contract_get(CONTRACT_ASSETS, Vec::new()).await
            }
            "change_contract_multi_asset_mode" => {
                params.ensure_allowed(&["isMultiAssetMode"])?;
                validate_enum(params, "isMultiAssetMode", &["true", "false"])?;
                let path = CONTRACT_CHANGE_MULTI_ASSET_MODE
                    .replace("{isMultiAssetMode}", params.required("isMultiAssetMode")?);
                self.contract_post_json(&path, Value::Object(Default::default()))
                    .await
            }
            "get_contract_asset" => {
                params.ensure_allowed(&["currency"])?;
                let path = CONTRACT_ASSET.replace("{currency}", params.required("currency")?);
                self.contract_get(&path, Vec::new()).await
            }
            "get_contract_transfer_records" => {
                self.dispatch_get_contract_transfer_records(method_name, params)
                    .await
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
                let body = params.body(&["positionId", "amount", "type"], &["positionId"], &[])?;
                self.contract_post_json(CONTRACT_CHANGE_MARGIN, Value::Object(body))
                    .await
            }
            "change_contract_auto_add_margin" => {
                params.ensure_allowed(&["positionId", "isEnabled"])?;
                params.required("positionId")?;
                validate_enum(params, "isEnabled", &["true", "false"])?;
                params.required("isEnabled")?;
                let body = params.body(
                    &["positionId", "isEnabled"],
                    &["positionId"],
                    &["isEnabled"],
                )?;
                self.contract_post_json(CONTRACT_CHANGE_AUTO_ADD_MARGIN, Value::Object(body))
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
                )?;
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

mod account_requests {
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::mexc::client::{MexcApi, MexcClient};
    use crate::exchanges::mexc::params::{MexcParams, validate_enum, validate_u64_range};
    use crate::http::HttpMethod;
    use crate::{DcexError, Result};
    impl MexcClient {
        pub(in crate::exchanges::mexc) async fn account_schema_request(
            &self,
            name: &str,
            p: &MexcParams,
            public: bool,
        ) -> Result<Option<ValidatedResponse>> {
            let (path, api, verb, signed, allowed, required): (
                &str,
                MexcApi,
                HttpMethod,
                bool,
                &[&str],
                &[&str],
            ) = match name {
                "get_uid" => (
                    "/api/v3/uid",
                    MexcApi::Spot,
                    HttpMethod::Get,
                    true,
                    &[],
                    &[],
                ),
                "get_api_key_info" => (
                    "/api/v3/apiKeyInfo",
                    MexcApi::Spot,
                    HttpMethod::Get,
                    true,
                    &["accessKey"],
                    &["accessKey"],
                ),
                "set_api_key_ip_whitelist" => (
                    "/api/v3/apiKeyInfo",
                    MexcApi::Spot,
                    HttpMethod::Post,
                    true,
                    &["apiKey", "ipWhiteList", "note"],
                    &["apiKey", "ipWhiteList"],
                ),
                "get_contract_profit_rate" => (
                    "/api/v1/private/account/profit_rate/{type}",
                    MexcApi::Contract,
                    HttpMethod::Get,
                    true,
                    &["type"],
                    &["type"],
                ),
                "get_contract_fee_deduction_config" => (
                    "/api/v1/private/account/feeDeductConfigs",
                    MexcApi::Contract,
                    HttpMethod::Get,
                    true,
                    &[],
                    &[],
                ),
                "get_contract_fee_discount_config" => (
                    "/api/v1/private/account/config/contractFeeDiscountConfig",
                    MexcApi::Contract,
                    HttpMethod::Get,
                    true,
                    &[],
                    &[],
                ),
                "get_contract_discount_usage" => (
                    "/api/v1/private/account/discountType",
                    MexcApi::Contract,
                    HttpMethod::Get,
                    true,
                    &[],
                    &[],
                ),
                _ => return Ok(None),
            };
            if public == signed {
                return Ok(None);
            }
            p.ensure_allowed(allowed)?;
            validate_u64_range(p, "recvWindow", 1, 60_000)?;
            let mut query = p.only(allowed);
            let unique: std::collections::BTreeSet<_> = query.iter().map(|(k, _)| k).collect();
            if unique.len() != query.len() {
                return Err(DcexError::InvalidInput("duplicate MEXC parameter".into()));
            }
            for key in required {
                if p.required(key)?.trim().is_empty() {
                    return Err(DcexError::InvalidInput(format!("{key} cannot be empty")));
                }
            }
            validate_u64_range(p, "page", 1, u64::MAX)?;
            validate_u64_range(p, "limit", 1, 1000)?;
            validate_u64_range(p, "startTime", 0, u64::MAX)?;
            validate_u64_range(p, "endTime", 0, u64::MAX)?;
            if let (Some(start), Some(end)) = (p.get("startTime"), p.get("endTime"))
                && start.parse::<u64>().unwrap() > end.parse::<u64>().unwrap()
            {
                return Err(DcexError::InvalidInput("startTime exceeds endTime".into()));
            }
            if name == "set_api_key_ip_whitelist" {
                let values: Vec<_> = p.required("ipWhiteList")?.split(',').collect();
                if values.len() > 20
                    || values
                        .iter()
                        .any(|v| v.parse::<std::net::IpAddr>().is_err())
                {
                    return Err(DcexError::InvalidInput(
                        "ipWhiteList requires 1..20 IP addresses".into(),
                    ));
                }
            }
            let path = if name == "get_contract_profit_rate" {
                validate_enum(p, "type", &["1", "2"])?;
                query.retain(|(k, _)| k != "type");
                path.replace("{type}", p.required("type")?)
            } else {
                path.to_string()
            };
            Ok(Some(
                self.request(verb, api, path, query, None, signed).await?,
            ))
        }
    }
}
