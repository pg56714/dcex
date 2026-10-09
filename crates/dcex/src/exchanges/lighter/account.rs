use std::collections::BTreeMap;

use crate::{DcexError, Result};

use super::client::LighterClient;
use super::endpoints::*;
use super::params::{LighterParams, insert_optional_pair};

impl LighterClient {
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

    pub(super) fn account_query(
        &self,
        params: &LighterParams,
        keys: &[&str],
    ) -> Result<Vec<(String, String)>> {
        self.account_query_renamed(
            params,
            &keys.iter().map(|key| (*key, *key)).collect::<Vec<_>>(),
        )
    }

    pub(super) fn account_market_query(
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

    pub(super) fn account_market_query_renamed(
        &self,
        params: &LighterParams,
        keys: &[(&str, &str)],
    ) -> Result<Vec<(String, String)>> {
        let mut query = self.account_query_renamed(params, keys)?;
        if let Some(product_symbol) = params.get("product_symbol") {
            super::market::upsert(&mut query, "market_id", self.market_id(product_symbol)?);
        }
        Ok(query)
    }

    pub(super) fn account_query_renamed(
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

    pub(super) fn validate_private_params(
        &self,
        method_name: &str,
        params: &LighterParams,
    ) -> Result<()> {
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
            "get_account_orders" => {
                params.ensure_allowed(&[
                    "account_index",
                    "client_order_indexes",
                    "authorization",
                ])?;
                self.validate_private_account(params)?;
                let indexes = params.required("client_order_indexes")?;
                let parts: Vec<_> = indexes.split(',').collect();
                if parts.len() > 20 {
                    return Err(DcexError::InvalidInput(
                        "Lighter client_order_indexes must contain 1..=20 values".into(),
                    ));
                }
                for part in parts {
                    super::params::parse_i64(part, "client_order_indexes")?;
                }
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
                    "type",
                    "market_id",
                    "product_symbol",
                    "start_timestamp",
                    "end_timestamp",
                    "side",
                    "role",
                    "trade_type",
                    "aggregate",
                    "authorization",
                ])?;
                self.validate_private_account(params)?;
                validate_market_selector(params, false)?;
                params.required_one_of("type", &["funding", "trade"])?;
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
                params.optional_bool("aggregate")?;
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
                    &["account_index", "cursor", "type", "authorization"],
                    &["type"],
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
                for value in params.values("type") {
                    if !TYPES.contains(&value) {
                        return Err(DcexError::InvalidInput(format!(
                            "invalid Lighter type: {value}; expected one of {}",
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
            "get_withdraw_history" => self.get_withdraw_history_validation(params),
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

    pub(super) fn validate_private_account(&self, params: &LighterParams) -> Result<()> {
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

pub(super) fn validate_optional_nonempty(params: &LighterParams, keys: &[&str]) -> Result<()> {
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
    fn export_accepts_configured_account_index() {
        let client = LighterClient::with_base_url_and_credentials(
            Duration::from_secs(10),
            "https://mainnet.zklighter.elliot.ai".to_string(),
            Some(12),
            None,
            None,
        )
        .expect("client");
        let params = LighterParams::from_pairs(vec![
            ("type".to_string(), "trade".to_string()),
            ("authorization".to_string(), "token".to_string()),
        ]);

        client
            .validate_private_params("get_export", &params)
            .expect("configured account_index is accepted for export");
    }
}

mod account_requests {
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::lighter::{
        LighterClient, client::LighterContentType, market::auth_header_required,
        params::LighterParams,
    };
    use crate::http::HttpMethod;
    use crate::{DcexError, Result};
    type RequestRoute<'a> = (
        &'a str,
        bool,
        bool,
        &'a [&'a str],
        &'a [&'a str],
        &'a [&'a str],
        &'a [&'a str],
    );
    impl LighterClient {
        pub(in crate::exchanges::lighter) async fn account_schema_request(
            &self,
            name: &str,
            p: &LighterParams,
            public: bool,
        ) -> Result<Option<ValidatedResponse>> {
            let (path, post, is_public, fields, required, integers, bools): RequestRoute<'_> =
                match name {
                    "set_maker_only_api_keys" => (
                        "/api/v1/setMakerOnlyApiKeys",
                        true,
                        false,
                        &["account_index", "api_key_indexes", "authorization"],
                        &["account_index", "api_key_indexes"],
                        &["account_index"],
                        &[],
                    ),
                    "change_account_tier" => (
                        "/api/v1/changeAccountTier",
                        true,
                        false,
                        &["account_index", "new_tier", "authorization"],
                        &["account_index", "new_tier"],
                        &["account_index"],
                        &[],
                    ),
                    "create_read_only_token" => (
                        "/api/v1/tokens/create",
                        true,
                        false,
                        &[
                            "name",
                            "account_index",
                            "expiry",
                            "sub_account_access",
                            "authorization",
                            "scopes",
                        ],
                        &["name", "account_index", "expiry", "sub_account_access"],
                        &["account_index", "expiry"],
                        &["sub_account_access"],
                    ),
                    "revoke_read_only_token" => (
                        "/api/v1/tokens/revoke",
                        true,
                        false,
                        &["token_id", "account_index", "authorization"],
                        &["token_id", "account_index"],
                        &["token_id", "account_index"],
                        &[],
                    ),
                    "acknowledge_notification" => (
                        "/api/v1/notification/ack",
                        true,
                        false,
                        &["notif_id", "account_index", "authorization"],
                        &["notif_id", "account_index"],
                        &["account_index"],
                        &[],
                    ),
                    _ => return Ok(None),
                };
            if public != is_public {
                return Ok(None);
            }
            p.ensure_allowed(fields)?;
            for key in required {
                p.required(key)?;
            }
            for key in fields {
                if p.get(key).is_some() {
                    p.required(key)?;
                }
            }
            for key in integers {
                p.optional_u64_range(key, 0, u64::MAX)?;
            }
            for key in bools {
                p.optional_one_of(key, &["true", "false"])?;
            }
            if name == "set_maker_only_api_keys" {
                let indexes: Vec<u64> = serde_json::from_str(p.required("api_key_indexes")?)
                    .map_err(|_| {
                        DcexError::InvalidInput(
                            "api_key_indexes must be a JSON integer array".into(),
                        )
                    })?;
                let distinct: std::collections::BTreeSet<_> = indexes.iter().copied().collect();
                if indexes.iter().any(|v| *v > 254) || distinct.len() != indexes.len() {
                    return Err(DcexError::InvalidInput(
                        "API key indexes must be distinct and within 0..254".into(),
                    ));
                }
                p.required_u64_range("account_index", 0, 281474976710654)?;
            }
            let headers = if public {
                std::collections::BTreeMap::new()
            } else {
                auth_header_required(self, p)?
            };
            let pairs = p.query(
                &fields
                    .iter()
                    .copied()
                    .filter(|k| *k != "authorization")
                    .collect::<Vec<_>>(),
            );
            let response = if post {
                self.path_request(
                    HttpMethod::Post,
                    path,
                    Vec::new(),
                    pairs,
                    headers,
                    LighterContentType::Form,
                )
                .await
            } else {
                self.get_path(path, pairs, headers).await
            };
            response.map(Some)
        }
    }
}
