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
        self.validate_private_params(method_name, &params)?;
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
                self.market_query_renamed(
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
                auth_header_from_params(&params, self.auto_auth(&params)?)?,
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

    fn validate_private_params(&self, method_name: &str, params: &LighterParams) -> Result<()> {
        match method_name {
            "get_account_limits"
            | "get_fastwithdraw_info"
            | "get_referral_points"
            | "get_maker_only_api_keys" => {
                params.ensure_allowed(&["account_index", "authorization"])?;
                self.validate_private_account(params)?;
                validate_optional_nonempty(params, &["authorization"])
            }
            "get_account_active_orders" => {
                params.ensure_allowed(&[
                    "account_index",
                    "market_id",
                    "product_symbol",
                    "market_type",
                    "authorization",
                ])?;
                self.validate_private_account(params)?;
                validate_market_selector(params, false)?;
                params.optional_one_of("market_type", &["all", "spot", "perp"])?;
                validate_optional_nonempty(params, &["authorization"])
            }
            "get_account_inactive_orders" => {
                params.ensure_allowed(&[
                    "account_index",
                    "market_id",
                    "product_symbol",
                    "ask_filter",
                    "between_timestamps",
                    "cursor",
                    "limit",
                    "market_type",
                    "authorization",
                ])?;
                self.validate_private_account(params)?;
                validate_market_selector(params, false)?;
                params.optional_i64("ask_filter")?;
                params.required_u64_range("limit", 1, 100)?;
                params.optional_one_of("market_type", &["all", "spot", "perp"])?;
                validate_optional_nonempty(
                    params,
                    &["between_timestamps", "cursor", "authorization"],
                )
            }
            "get_deposit_history" => {
                params.ensure_allowed(&[
                    "account_index",
                    "l1_address",
                    "cursor",
                    "filter",
                    "authorization",
                ])?;
                self.validate_private_account(params)?;
                params.required("l1_address")?;
                params.optional_one_of("filter", &["all", "pending", "claimable"])?;
                validate_optional_nonempty(params, &["cursor", "authorization"])
            }
            "get_export" => {
                params.ensure_allowed(&[
                    "account_index",
                    "type_",
                    "market_id",
                    "product_symbol",
                    "start_timestamp",
                    "end_timestamp",
                    "side",
                    "role",
                    "trade_type",
                    "authorization",
                ])?;
                validate_market_selector(params, false)?;
                params.required_one_of("type_", &["funding", "trade"])?;
                params.optional_one_of("side", &["all", "long", "short"])?;
                params.optional_one_of("role", &["all", "maker", "taker"])?;
                params.optional_one_of(
                    "trade_type",
                    &[
                        "all",
                        "trade",
                        "liquidation",
                        "deleverage",
                        "market-settlement",
                    ],
                )?;
                validate_optional_timestamp_range(params, 1_735_689_600_000, 1_830_297_600_000)?;
                validate_optional_nonempty(params, &["authorization"])
            }
            "get_l1_metadata" => {
                params.ensure_allowed(&["l1_address", "authorization"])?;
                params.required("l1_address")?;
                validate_optional_nonempty(params, &["authorization"])
            }
            "get_liquidations" => {
                params.ensure_allowed(&[
                    "account_index",
                    "market_id",
                    "product_symbol",
                    "cursor",
                    "limit",
                    "authorization",
                ])?;
                self.validate_private_account(params)?;
                validate_market_selector(params, false)?;
                params.required_u64_range("limit", 1, 100)?;
                validate_optional_nonempty(params, &["cursor", "authorization"])
            }
            "get_referral_user_referrals" => {
                params.ensure_allowed(&[
                    "l1_address",
                    "cursor",
                    "auth",
                    "stats_start_timestamp",
                    "stats_end_timestamp",
                    "limit",
                    "authorization",
                ])?;
                params.required("l1_address")?;
                params.optional_u64_range("limit", 1, 300)?;
                validate_optional_timestamp_pair(
                    params,
                    "stats_start_timestamp",
                    "stats_end_timestamp",
                )?;
                validate_optional_nonempty(params, &["cursor", "auth", "authorization"])
            }
            "get_transfer_history" => {
                params.ensure_allowed_with_repeated(
                    &["account_index", "cursor", "type_", "authorization"],
                    &["type_"],
                )?;
                self.validate_private_account(params)?;
                const TYPES: &[&str] = &[
                    "all",
                    "L2Transfer",
                    "L2MintShares",
                    "L2BurnShares",
                    "L2StakeAssets",
                    "L2UnstakeAssets",
                ];
                for value in params.values("type_") {
                    if !TYPES.contains(&value) {
                        return Err(DcexError::InvalidInput(format!(
                            "invalid Lighter type_: {value}; expected one of {}",
                            TYPES.join(", ")
                        )));
                    }
                }
                validate_optional_nonempty(params, &["cursor", "authorization"])
            }
            "get_transfer_fee_info" => {
                params.ensure_allowed(&["account_index", "to_account_index", "authorization"])?;
                self.validate_private_account(params)?;
                params.optional_i64("to_account_index")?;
                validate_optional_nonempty(params, &["authorization"])
            }
            "get_withdraw_history" => {
                params.ensure_allowed(&["account_index", "cursor", "filter", "authorization"])?;
                self.validate_private_account(params)?;
                params.optional_one_of("filter", &["all", "pending", "claimable"])?;
                validate_optional_nonempty(params, &["cursor", "authorization"])
            }
            "get_position_funding" => {
                params.ensure_allowed(&[
                    "account_index",
                    "market_id",
                    "product_symbol",
                    "cursor",
                    "limit",
                    "side",
                    "start_timestamp",
                    "end_timestamp",
                    "authorization",
                ])?;
                self.validate_private_account(params)?;
                validate_market_selector(params, false)?;
                params.required_u64_range("limit", 1, 100)?;
                params.optional_one_of("side", &["long", "short", "all"])?;
                validate_optional_timestamp_pair(params, "start_timestamp", "end_timestamp")?;
                validate_optional_nonempty(params, &["cursor", "authorization"])
            }
            "get_leases" => {
                params.ensure_allowed(&[
                    "account_index",
                    "cursor",
                    "limit",
                    "auth",
                    "authorization",
                ])?;
                self.validate_private_account(params)?;
                params.optional_u64_range("limit", 1, 100)?;
                validate_optional_nonempty(params, &["cursor", "auth", "authorization"])
            }
            "get_partner_stats" => {
                params.ensure_allowed(&["account_index", "start_timestamp", "end_timestamp"])?;
                self.validate_private_account(params)?;
                validate_optional_timestamp_pair(params, "start_timestamp", "end_timestamp")
            }
            "get_next_nonce" => {
                params.ensure_allowed(&["account_index", "api_key_index"])?;
                self.validate_private_account(params)?;
                params.optional_u64_range("api_key_index", 0, 254)?;
                self.private_api_key_index(params.optional_u64("api_key_index")?)?;
                Ok(())
            }
            _ => Ok(()),
        }
    }

    fn validate_private_account(&self, params: &LighterParams) -> Result<()> {
        self.private_account_index(params.optional_u64("account_index")?)?;
        Ok(())
    }
}

fn validate_market_selector(params: &LighterParams, required: bool) -> Result<()> {
    let market_id = params.get("market_id");
    let product_symbol = params.get("product_symbol");
    if market_id.is_some() && product_symbol.is_some() {
        return Err(DcexError::InvalidInput(
            "Lighter accepts either market_id or product_symbol, not both".to_string(),
        ));
    }
    if required && market_id.is_none() && product_symbol.is_none() {
        return Err(DcexError::InvalidInput(
            "missing required parameter: market_id or product_symbol".to_string(),
        ));
    }
    if let Some(market_id) = market_id {
        super::params::parse_i64(market_id, "market_id")?;
    }
    if product_symbol.is_some() {
        params.required("product_symbol")?;
    }
    Ok(())
}

fn validate_optional_timestamp_pair(
    params: &LighterParams,
    start_key: &str,
    end_key: &str,
) -> Result<()> {
    params.optional_u64(start_key)?;
    params.optional_u64(end_key)?;
    params.ensure_time_order(start_key, end_key)
}

fn validate_optional_timestamp_range(params: &LighterParams, min: u64, max: u64) -> Result<()> {
    params.optional_u64_range("start_timestamp", min, max)?;
    params.optional_u64_range("end_timestamp", min, max)?;
    params.ensure_time_order("start_timestamp", "end_timestamp")
}

fn validate_optional_nonempty(params: &LighterParams, keys: &[&str]) -> Result<()> {
    for key in keys {
        if params.get(key).is_some() {
            params.required(key)?;
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use std::time::Duration;

    use super::*;

    #[test]
    fn export_accepts_authorization_without_account_index() {
        let client = LighterClient::new(Duration::from_secs(1)).expect("client");
        let params = LighterParams::from_pairs(vec![
            ("type_".to_string(), "trade".to_string()),
            ("authorization".to_string(), "token".to_string()),
        ]);

        client
            .validate_private_params("get_export", &params)
            .expect("account_index is optional for export");
    }
}
