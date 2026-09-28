use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};
use serde_json::Value;

use super::client::ExtendedClient;
use super::endpoints::*;
use super::params::{
    ExtendedParams, body_object, json_string, json_u64, object_required, validate_positive_decimal,
};

impl ExtendedClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &ExtendedParams,
    ) -> Result<Option<ValidatedResponse>> {
        let response = match method_name {
            "create_withdrawal_signed" => {
                params.ensure_allowed(&["body"], &[])?;
                let body: Value = serde_json::from_str(params.required("body")?).map_err(|_| {
                    DcexError::InvalidInput("Extended body must be valid JSON".into())
                })?;
                let object = body_object(&body, "withdrawal")?;
                for key in object.keys() {
                    if ![
                        "chainId",
                        "accountId",
                        "amount",
                        "asset",
                        "settlement",
                        "quoteId",
                        "description",
                    ]
                    .contains(&key.as_str())
                    {
                        return Err(DcexError::InvalidInput(format!(
                            "unsupported Extended withdrawal field: {key}"
                        )));
                    }
                }
                for key in ["chainId", "amount", "asset"] {
                    json_string(object, key, true)?;
                }
                json_u64(object, "accountId", true)?;
                if !crate::common::is_positive_plain_decimal(
                    json_string(object, "amount", true)?.expect("required"),
                ) {
                    return Err(DcexError::InvalidInput(
                        "Extended amount requires a positive plain decimal string".into(),
                    ));
                }
                if object["chainId"] != "STRK" {
                    json_string(object, "quoteId", true)?;
                }
                if let Some(description) = json_string(object, "description", false)?
                    && description.chars().count() > 250
                {
                    return Err(DcexError::InvalidInput(
                        "Extended description must not exceed 250 characters".into(),
                    ));
                }
                let settlement = object_required(object, "settlement")?
                    .as_object()
                    .ok_or_else(|| {
                        DcexError::InvalidInput("Extended settlement must be an object".into())
                    })?;
                for key in ["recipient", "collateralId", "amount"] {
                    json_string(settlement, key, true)?;
                }
                for key in ["positionId", "salt"] {
                    json_u64(settlement, key, true)?;
                }
                let expiration = object_required(settlement, "expiration")?
                    .as_object()
                    .ok_or_else(|| {
                        DcexError::InvalidInput("Extended expiration must be an object".into())
                    })?;
                json_u64(expiration, "seconds", true)?;
                let signature = object_required(settlement, "signature")?
                    .as_object()
                    .ok_or_else(|| {
                        DcexError::InvalidInput("Extended signature must be an object".into())
                    })?;
                for key in ["r", "s"] {
                    json_string(signature, key, true)?;
                }
                self.private_post_value(
                    "/api/v1/user/withdrawal",
                    Value::Object(object.clone()),
                    Vec::new(),
                )
                .await
            }
            "get_affiliate_data"
            | "get_referral_status"
            | "get_referral_links"
            | "get_referral_dashboard" => {
                let path = match method_name {
                    "get_affiliate_data" => "/api/v1/user/affiliate",
                    "get_referral_status" => "/api/v1/user/referrals/status",
                    "get_referral_links" => "/api/v1/user/referrals/links",
                    _ => "/api/v1/user/referrals/dashboard",
                };
                let keys: &[&str] = if method_name == "get_referral_dashboard" {
                    &["period"]
                } else {
                    &[]
                };
                params.ensure_allowed(keys, &[])?;
                if method_name == "get_referral_dashboard" {
                    params.required("period")?;
                }
                self.private_get(path, params.only(keys)).await
            }
            "use_referral_code" | "create_referral_code" | "update_referral_code" => {
                let keys: &[&str] = if method_name == "use_referral_code" {
                    &["code"]
                } else {
                    &["id", "isDefault", "hiddenAtUi"]
                };
                params.ensure_allowed(keys, &[])?;
                let key = if method_name == "use_referral_code" {
                    "code"
                } else {
                    "id"
                };
                let mut body = serde_json::Map::new();
                body.insert(key.into(), Value::String(params.required(key)?.into()));
                for key in ["isDefault", "hiddenAtUi"] {
                    if let Some(raw) = params.get(key) {
                        body.insert(
                            key.into(),
                            Value::Bool(raw.parse::<bool>().map_err(|_| {
                                DcexError::InvalidInput(format!("{key} must be a boolean"))
                            })?),
                        );
                    }
                }
                if method_name == "update_referral_code" {
                    self.private_put_value("/api/v1/user/referrals", Value::Object(body))
                        .await
                } else {
                    self.private_post_value(
                        if method_name == "use_referral_code" {
                            "/api/v1/user/referrals/use"
                        } else {
                            "/api/v1/user/referrals"
                        },
                        Value::Object(body),
                        Vec::new(),
                    )
                    .await
                }
            }
            "get_account_info" | "get_account_details" => {
                params.ensure_allowed(&[], &[])?;
                self.private_get(ACCOUNT_INFO, Vec::new()).await
            }
            "get_accounts" | "get_sub_accounts" => {
                params.ensure_allowed(&[], &[])?;
                self.private_get(ACCOUNTS, Vec::new()).await
            }
            "get_balance" => {
                params.ensure_allowed(&[], &[])?;
                self.private_get(BALANCE, Vec::new()).await
            }
            "get_asset_operations" => {
                params.ensure_allowed(
                    &[
                        "accountId",
                        "id",
                        "type",
                        "status",
                        "startTime",
                        "endTime",
                        "cursor",
                        "limit",
                    ],
                    &["accountId", "type", "status"],
                )?;
                params.repeated_one_of("type", &["DEPOSIT", "CLAIM", "TRANSFER", "WITHDRAWAL"])?;
                params.repeated_one_of(
                    "status",
                    &["CREATED", "IN_PROGRESS", "COMPLETED", "REJECTED"],
                )?;
                params.repeated_u64_range("accountId", 1, u64::MAX)?;
                params.optional_u64_range("startTime", 0, u64::MAX)?;
                params.optional_u64_range("endTime", 0, u64::MAX)?;
                params.ensure_time_order("startTime", "endTime")?;
                params.optional_u64_range("cursor", 0, u64::MAX)?;
                params.optional_u64_range("limit", 1, u64::MAX)?;
                self.private_get(
                    ASSET_OPERATIONS,
                    params.only(&[
                        "accountId",
                        "id",
                        "type",
                        "status",
                        "startTime",
                        "endTime",
                        "cursor",
                        "limit",
                    ]),
                )
                .await
            }
            "submit_internal_transfer" => {
                params.ensure_allowed(&["body"], &[])?;
                let body = params.body_required()?;
                let object = body_object(&body, "internal transfer")?;
                let from = json_u64(object, "fromAccount", true)?.expect("required");
                let to = json_u64(object, "toAccount", true)?.expect("required");
                if from == to {
                    return Err(DcexError::InvalidInput(
                        "Extended internal transfer requires distinct subaccounts".into(),
                    ));
                }
                let amount = json_string(object, "amount", true)?.expect("required");
                validate_positive_decimal("amount", amount)?;
                json_string(object, "transferredAsset", true)?;
                let settlement = object_required(object, "settlement")?;
                let settlement = settlement.as_object().ok_or_else(|| {
                    DcexError::InvalidInput("Extended transfer settlement must be an object".into())
                })?;
                for key in [
                    "amount",
                    "expirationTimestamp",
                    "nonce",
                    "receiverPositionId",
                    "senderPositionId",
                ] {
                    json_u64(settlement, key, true)?;
                }
                for key in ["assetId", "receiverPublicKey", "senderPublicKey"] {
                    json_string(settlement, key, true)?;
                }
                let signature = object_required(settlement, "signature")?;
                let signature = signature.as_object().ok_or_else(|| {
                    DcexError::InvalidInput("Extended transfer signature must be an object".into())
                })?;
                for key in ["r", "s"] {
                    json_string(signature, key, true)?;
                }
                self.private_post_value(
                    INTERNAL_TRANSFER,
                    Value::Object(object.clone()),
                    Vec::new(),
                )
                .await
            }
            "get_account_health" => {
                params.ensure_allowed(&["accountId"], &["accountId"])?;
                params.repeated_u64_range("accountId", 1, u64::MAX)?;
                if params.only(&["accountId"]).is_empty() {
                    return Err(crate::DcexError::InvalidInput(
                        "Extended accountId is required for account health".into(),
                    ));
                }
                self.private_get(ACCOUNT_HEALTH, params.only(&["accountId"]))
                    .await
            }
            "get_spot_balances" => {
                params.ensure_allowed(&["accountId"], &["accountId"])?;
                params.repeated_u64_range("accountId", 1, u64::MAX)?;
                self.private_get(SPOT_BALANCES, params.only(&["accountId"]))
                    .await
            }
            "get_positions" => {
                params.ensure_allowed(&["market", "side"], &["market"])?;
                params.optional_one_of("side", &["LONG", "SHORT"])?;
                self.private_get(POSITIONS, params.only(&["market", "side"]))
                    .await
            }
            "get_positions_history" => {
                validate_history_params(params, &["market", "side", "cursor", "limit"])?;
                params.optional_one_of("side", &["LONG", "SHORT"])?;
                self.private_get(
                    POSITIONS_HISTORY,
                    params.only(&["market", "side", "cursor", "limit"]),
                )
                .await
            }
            "get_trades_history" | "get_fills" => {
                validate_history_params(params, &["market", "type", "side", "cursor", "limit"])?;
                params.optional_one_of("type", &["TRADE", "LIQUIDATION", "DELEVERAGE"])?;
                params.optional_one_of("side", &["BUY", "SELL"])?;
                self.private_get(
                    FILLS,
                    params.only(&["market", "type", "side", "cursor", "limit"]),
                )
                .await
            }
            "get_funding_payments" => {
                validate_history_params(
                    params,
                    &["market", "side", "startTime", "cursor", "limit"],
                )?;
                params.optional_one_of("side", &["LONG", "SHORT"])?;
                params.required_u64_range("startTime", 0, u64::MAX)?;
                params.optional_u64_range("limit", 1, 1_000)?;
                self.private_get(
                    FUNDING_PAYMENTS,
                    params.only(&["market", "side", "startTime", "cursor", "limit"]),
                )
                .await
            }
            "get_leverage" => {
                params.ensure_allowed(&["market"], &["market"])?;
                self.private_get(LEVERAGE, params.only(&["market"])).await
            }
            "update_leverage" => {
                params.ensure_allowed(&["market", "leverage"], &[])?;
                params.required_positive_decimal("leverage")?;
                let body = serde_json::json!({
                    "market": params.required("market")?,
                    "leverage": params.required("leverage")?,
                });
                self.private_patch_value(LEVERAGE, body, Vec::new()).await
            }
            "get_fees" => {
                params.ensure_allowed(&["market", "builderId"], &["market"])?;
                params.optional_u64_range("builderId", 1, u64::MAX)?;
                self.private_get(FEES, params.only(&["market", "builderId"]))
                    .await
            }
            "get_rebates" => {
                params.ensure_allowed(&[], &[])?;
                self.private_get(REBATES, Vec::new()).await
            }
            "get_builder_dashboard" => {
                params.ensure_allowed(&[], &[])?;
                self.private_get(BUILDER_DASHBOARD, Vec::new()).await
            }
            "get_builder_trades" => {
                params.ensure_allowed(&["cursor", "limit"], &[])?;
                params.optional_u64_range("cursor", 0, u64::MAX)?;
                params.optional_u64_range("limit", 1, 1_000)?;
                self.private_get(BUILDER_TRADES, params.only(&["cursor", "limit"]))
                    .await
            }
            "get_bridge_config" => {
                params.ensure_allowed(&[], &[])?;
                self.private_get(BRIDGE_CONFIG, Vec::new()).await
            }
            "commit_bridge_quote" => {
                params.ensure_allowed(&["id"], &[])?;
                let id = params.required("id")?;
                self.request(
                    crate::http::HttpMethod::Post,
                    BRIDGE_QUOTE,
                    vec![("id".into(), id.into())],
                    None,
                    true,
                    Default::default(),
                )
                .await
            }
            "get_bridge_quote" => {
                params.ensure_allowed(&["chainIn", "chainOut", "amount", "asset"], &[])?;
                params.required_positive_decimal("amount")?;
                let mut query = vec![
                    (
                        "chainIn".to_string(),
                        params.required("chainIn")?.to_string(),
                    ),
                    (
                        "chainOut".to_string(),
                        params.required("chainOut")?.to_string(),
                    ),
                    ("amount".to_string(), params.required("amount")?.to_string()),
                ];
                if let Some(asset) = params.get("asset") {
                    query.push(("asset".to_string(), asset.to_string()));
                }
                self.private_get(BRIDGE_QUOTE, query).await
            }
            _ => return Ok(None),
        }?;
        Ok(Some(response))
    }
}

fn validate_history_params(params: &ExtendedParams, allowed: &[&str]) -> Result<()> {
    params.ensure_allowed(allowed, &["market"])?;
    params.optional_u64_range("cursor", 0, u64::MAX)?;
    params.optional_u64_range("limit", 1, 10_000)
}
