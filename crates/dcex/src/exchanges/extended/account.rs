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
                self.private_get(ACCOUNT_INFO, Vec::new()).await
            }
            "get_accounts" | "get_sub_accounts" => self.private_get(ACCOUNTS, Vec::new()).await,
            "get_balance" => self.private_get(BALANCE, Vec::new()).await,
            "get_asset_operations" => {
                self.private_get(
                    ASSET_OPERATIONS,
                    params.only(&["type", "status", "cursor", "limit"]),
                )
                .await
            }
            "get_spot_balances" => {
                self.private_get(SPOT_BALANCES, params.only(&["accountId"]))
                    .await
            }
            "get_positions" => {
                self.private_get(POSITIONS, params.only(&["market", "side"]))
                    .await
            }
            "get_positions_history" => {
                self.private_get(
                    POSITIONS_HISTORY,
                    params.only(&["market", "side", "cursor", "limit"]),
                )
                .await
            }
            "get_trades_history" | "get_fills" => {
                self.private_get(
                    FILLS,
                    params.only(&["market", "type", "side", "cursor", "limit"]),
                )
                .await
            }
            "get_funding_payments" => {
                self.private_get(
                    FUNDING_PAYMENTS,
                    params.only(&["market", "side", "startTime", "cursor", "limit"]),
                )
                .await
            }
            "get_leverage" => self.private_get(LEVERAGE, params.only(&["market"])).await,
            "get_fees" => {
                self.private_get(FEES, params.only(&["market", "builderId"]))
                    .await
            }
            "get_rebates" => self.private_get(REBATES, Vec::new()).await,
            "get_builder_dashboard" => self.private_get(BUILDER_DASHBOARD, Vec::new()).await,
            "get_builder_trades" => {
                self.private_get(BUILDER_TRADES, params.only(&["cursor", "limit"]))
                    .await
            }
            "get_bridge_config" => self.private_get(BRIDGE_CONFIG, Vec::new()).await,
            "get_bridge_quote" => {
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
