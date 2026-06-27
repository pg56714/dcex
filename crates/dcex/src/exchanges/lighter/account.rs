use std::collections::BTreeMap;

use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::LighterClient;
use super::endpoints::*;
use super::market::{auth_header_from_params, auth_header_required};
use super::params::{insert_optional_pair, LighterParams};

impl LighterClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = LighterParams::from_pairs(params);
        if let Some(response) = self.trade_request(method_name, &params).await? {
            return Ok(response);
        }
        let (path, mut query, mut headers) = match method_name {
            "get_account_limits" => (
                ACCOUNT_LIMITS,
                self.account_query(&params, &["account_index"])?,
                auth_header_required(self, &params)?,
            ),
            "get_account_active_orders" => (
                ACCOUNT_ACTIVE_ORDERS,
                self.account_market_query(&params, &["account_index", "market_id", "market_type"])?,
                auth_header_required(self, &params)?,
            ),
            "get_account_inactive_orders" => (
                ACCOUNT_INACTIVE_ORDERS,
                self.account_market_query(
                    &params,
                    &[
                        "account_index",
                        "market_id",
                        "ask_filter",
                        "between_timestamps",
                        "cursor",
                        "limit",
                        "market_type",
                    ],
                )?,
                auth_header_required(self, &params)?,
            ),
            "get_deposit_history" => (
                DEPOSIT_HISTORY,
                self.account_query(
                    &params,
                    &["account_index", "l1_address", "cursor", "filter"],
                )?,
                auth_header_required(self, &params)?,
            ),
            "get_export" => (
                EXPORT,
                self.account_query_renamed(
                    &params,
                    &[
                        ("account_index", "account_index"),
                        ("type_", "type"),
                        ("market_id", "market_id"),
                        ("start_timestamp", "start_timestamp"),
                        ("end_timestamp", "end_timestamp"),
                        ("side", "side"),
                        ("role", "role"),
                        ("trade_type", "trade_type"),
                    ],
                )?,
                auth_header_required(self, &params)?,
            ),
            "get_fastwithdraw_info" => (
                FASTWITHDRAW_INFO,
                self.account_query(&params, &["account_index"])?,
                auth_header_required(self, &params)?,
            ),
            "get_l1_metadata" => (
                L1_METADATA,
                params.query(&["l1_address"]),
                auth_header_required(self, &params)?,
            ),
            "get_liquidations" => (
                LIQUIDATIONS,
                self.account_market_query(
                    &params,
                    &["account_index", "market_id", "cursor", "limit"],
                )?,
                auth_header_required(self, &params)?,
            ),
            "get_referral_points" => (
                REFERRAL_POINTS,
                self.account_query(&params, &["account_index"])?,
                auth_header_required(self, &params)?,
            ),
            "get_referral_user_referrals" => (
                REFERRAL_USER_REFERRALS,
                params.query(&[
                    "l1_address",
                    "cursor",
                    "auth",
                    "stats_start_timestamp",
                    "stats_end_timestamp",
                    "limit",
                ]),
                auth_header_from_params(&params, self.auto_auth(&params)?)?,
            ),
            "get_transfer_history" => (
                TRANSFER_HISTORY,
                self.account_query_renamed(
                    &params,
                    &[
                        ("account_index", "account_index"),
                        ("cursor", "cursor"),
                        ("type_", "type"),
                    ],
                )?,
                auth_header_from_params(
                    &params,
                    if self.api_private_keys.is_empty() {
                        None
                    } else {
                        Some(self.create_auth_token()?)
                    },
                )?,
            ),
            "get_transfer_fee_info" => (
                TRANSFER_FEE_INFO,
                self.account_query(&params, &["account_index", "to_account_index"])?,
                auth_header_required(self, &params)?,
            ),
            "get_withdraw_history" => (
                WITHDRAW_HISTORY,
                self.account_query(&params, &["account_index", "cursor", "filter"])?,
                auth_header_required(self, &params)?,
            ),
            "get_position_funding" => (
                POSITION_FUNDING,
                self.account_market_query(
                    &params,
                    &[
                        "account_index",
                        "market_id",
                        "cursor",
                        "limit",
                        "side",
                        "start_timestamp",
                        "end_timestamp",
                    ],
                )?,
                auth_header_required(self, &params)?,
            ),
            "get_leases" => (
                LEASES,
                self.account_query(&params, &["account_index", "cursor", "limit", "auth"])?,
                auth_header_from_params(&params, self.auto_auth(&params)?)?,
            ),
            "get_partner_stats" => (
                PARTNER_STATS,
                self.account_query(
                    &params,
                    &["account_index", "start_timestamp", "end_timestamp"],
                )?,
                BTreeMap::new(),
            ),
            "get_maker_only_api_keys" => (
                GET_MAKER_ONLY_API_KEYS,
                self.account_query(&params, &["account_index"])?,
                auth_header_required(self, &params)?,
            ),
            "get_next_nonce" => (
                NEXT_NONCE,
                vec![
                    (
                        "account_index".to_string(),
                        self.private_account_index(params.optional_u64("account_index")?)?
                            .to_string(),
                    ),
                    (
                        "api_key_index".to_string(),
                        self.private_api_key_index(params.optional_u64("api_key_index")?)?
                            .to_string(),
                    ),
                ],
                BTreeMap::new(),
            ),
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Lighter private method: {method_name}"
                )))
            }
        };
        query.retain(|(_, value)| !value.is_empty());
        headers.retain(|_, value| !value.is_empty());
        self.get_path(path, query, headers).await
    }

    pub(super) async fn next_nonce(
        &self,
        nonce: Option<i64>,
        api_key_index: Option<u64>,
    ) -> Result<i64> {
        if let Some(nonce) = nonce {
            return Ok(nonce);
        }
        let response = self
            .get_path(
                NEXT_NONCE,
                vec![
                    (
                        "account_index".to_string(),
                        self.private_account_index(None)?.to_string(),
                    ),
                    (
                        "api_key_index".to_string(),
                        self.private_api_key_index(api_key_index)?.to_string(),
                    ),
                ],
                BTreeMap::new(),
            )
            .await?;
        response
            .data
            .get("nonce")
            .and_then(|value| {
                value
                    .as_i64()
                    .or_else(|| value.as_str()?.parse::<i64>().ok())
            })
            .ok_or_else(|| {
                DcexError::Decode(format!(
                    "Unexpected Lighter nonce response: {:?}",
                    response.data
                ))
            })
    }

    fn account_query(
        &self,
        params: &LighterParams,
        keys: &[&str],
    ) -> Result<Vec<(String, String)>> {
        self.account_query_renamed(
            params,
            &keys.iter().map(|key| (*key, *key)).collect::<Vec<_>>(),
        )
    }

    fn account_market_query(
        &self,
        params: &LighterParams,
        keys: &[&str],
    ) -> Result<Vec<(String, String)>> {
        let mut query = self.account_query(params, keys)?;
        if let Some(product_symbol) = params.get("product_symbol") {
            super::market::upsert(&mut query, "market_id", self.market_id(product_symbol)?);
        }
        Ok(query)
    }

    fn account_query_renamed(
        &self,
        params: &LighterParams,
        keys: &[(&str, &str)],
    ) -> Result<Vec<(String, String)>> {
        let mut query = params.query_renamed(keys);
        if keys.iter().any(|(_, target)| *target == "account_index")
            && !query.iter().any(|(key, _)| key == "account_index")
        {
            insert_optional_pair(
                &mut query,
                "account_index",
                Some(self.private_account_index(None)?),
            );
        }
        Ok(query)
    }
}
