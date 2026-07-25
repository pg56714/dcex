use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::ExtendedClient;
use super::endpoints::*;
use super::params::ExtendedParams;

impl ExtendedClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &ExtendedParams,
    ) -> Result<Option<ValidatedResponse>> {
        let response = match method_name {
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
