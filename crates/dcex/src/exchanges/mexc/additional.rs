//! Supplementary account, platform and conversion endpoints from official MEXC docs.
use super::client::{MexcApi, MexcClient};
use super::params::{MexcParams, validate_enum, validate_u64_range};
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};
impl MexcClient {
    pub(super) async fn additional_request(
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
            "close_spot_listen_key" => (
                "/api/v3/userDataStream",
                MexcApi::Spot,
                HttpMethod::Delete,
                true,
                &["listenKey"],
                &["listenKey"],
            ),
            "keep_alive_spot_listen_key" => (
                "/api/v3/userDataStream",
                MexcApi::Spot,
                HttpMethod::Put,
                true,
                &["listenKey"],
                &["listenKey"],
            ),
            "get_spot_listen_keys" => (
                "/api/v3/userDataStream",
                MexcApi::Spot,
                HttpMethod::Get,
                true,
                &[],
                &[],
            ),
            "create_spot_listen_key" => (
                "/api/v3/userDataStream",
                MexcApi::Spot,
                HttpMethod::Post,
                true,
                &[],
                &[],
            ),
            "create_deposit_address" => (
                "/api/v3/capital/deposit/address",
                MexcApi::Spot,
                HttpMethod::Post,
                true,
                &["coin", "network"],
                &["coin", "network"],
            ),
            "get_spot_offline_symbols" => (
                "/api/v3/symbol/offline",
                MexcApi::Spot,
                HttpMethod::Get,
                false,
                &[],
                &[],
            ),
            "get_announcements" => (
                "/api/v3/announcements",
                MexcApi::Spot,
                HttpMethod::Get,
                false,
                &["language", "page", "limit"],
                &[],
            ),
            "get_contract_supported_currencies" => (
                "/api/v1/contract/support_currencies",
                MexcApi::Contract,
                HttpMethod::Get,
                false,
                &[],
                &[],
            ),
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
            "get_convertible_assets" => (
                "/api/v3/capital/convert/list",
                MexcApi::Spot,
                HttpMethod::Get,
                true,
                &[],
                &[],
            ),
            "convert_dust" => (
                "/api/v3/capital/convert",
                MexcApi::Spot,
                HttpMethod::Post,
                true,
                &["asset"],
                &["asset"],
            ),
            "get_dust_conversion_history" => (
                "/api/v3/capital/convert",
                MexcApi::Spot,
                HttpMethod::Get,
                true,
                &["startTime", "endTime", "page", "limit"],
                &[],
            ),
            "create_sub_account" => (
                "/api/v3/sub-account/virtualSubAccount",
                MexcApi::Spot,
                HttpMethod::Post,
                true,
                &["subAccount", "note", "recvWindow"],
                &["subAccount", "note"],
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
            "get_stp_strategy_group" => (
                "/api/v3/strategy/group",
                MexcApi::Spot,
                HttpMethod::Get,
                true,
                &["tradeGroupName"],
                &["tradeGroupName"],
            ),
            "remove_stp_strategy_group_members" => (
                "/api/v3/strategy/group/uid",
                MexcApi::Spot,
                HttpMethod::Delete,
                true,
                &["uid", "tradeGroupId"],
                &["uid", "tradeGroupId"],
            ),
            "get_withdrawal_addresses" => (
                "/api/v3/capital/withdraw/address",
                MexcApi::Spot,
                HttpMethod::Get,
                true,
                &["coin", "page", "limit"],
                &[],
            ),
            "delete_stp_strategy_group" => (
                "/api/v3/strategy/group",
                MexcApi::Spot,
                HttpMethod::Delete,
                true,
                &["tradeGroupId"],
                &["tradeGroupId"],
            ),
            "create_stp_strategy_group" => (
                "/api/v3/strategy/group",
                MexcApi::Spot,
                HttpMethod::Post,
                true,
                &["tradeGroupName"],
                &["tradeGroupName"],
            ),
            "add_stp_strategy_group_members" => (
                "/api/v3/strategy/group/uid",
                MexcApi::Spot,
                HttpMethod::Post,
                true,
                &["uid", "tradeGroupId"],
                &["uid", "tradeGroupId"],
            ),
            "delete_sub_account_api_key" => (
                "/api/v3/sub-account/apiKey",
                MexcApi::Spot,
                HttpMethod::Delete,
                true,
                &["subAccount", "apiKey", "recvWindow"],
                &["subAccount", "apiKey"],
            ),
            "create_sub_account_api_key" => (
                "/api/v3/sub-account/apiKey",
                MexcApi::Spot,
                HttpMethod::Post,
                true,
                &["subAccount", "note", "permissions", "ip", "recvWindow"],
                &["subAccount", "note", "permissions"],
            ),
            "get_sub_account_api_keys" => (
                "/api/v3/sub-account/apiKey",
                MexcApi::Spot,
                HttpMethod::Get,
                true,
                &["subAccount", "recvWindow"],
                &["subAccount"],
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
        validate_u64_range(
            p,
            "limit",
            1,
            if name == "get_announcements" {
                100
            } else {
                1000
            },
        )?;
        validate_u64_range(p, "startTime", 0, u64::MAX)?;
        validate_u64_range(p, "endTime", 0, u64::MAX)?;
        if let (Some(start), Some(end)) = (p.get("startTime"), p.get("endTime")) {
            if start.parse::<u64>().unwrap() > end.parse::<u64>().unwrap() {
                return Err(DcexError::InvalidInput("startTime exceeds endTime".into()));
            }
        }
        if name == "get_announcements"
            && p.get("limit")
                .is_some_and(|n| n.parse::<u64>().is_ok_and(|n| n % 5 != 0))
        {
            return Err(DcexError::InvalidInput(
                "announcement limit must be a multiple of 5".into(),
            ));
        }
        if name == "convert_dust" {
            let values: Vec<_> = p.required("asset")?.split(',').collect();
            if values.len() > 15
                || values.iter().any(|v| v.is_empty())
                || values
                    .iter()
                    .collect::<std::collections::BTreeSet<_>>()
                    .len()
                    != values.len()
            {
                return Err(DcexError::InvalidInput(
                    "asset requires 1..15 distinct comma-separated currencies".into(),
                ));
            }
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
