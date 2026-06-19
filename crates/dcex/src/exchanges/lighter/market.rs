use std::collections::BTreeMap;

use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::LighterClient;
use super::endpoints::*;
use super::params::{insert_optional_pair, LighterParams};

impl LighterClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = LighterParams::from_pairs(params);
        let (path, mut query, mut headers) = match method_name {
            "get_info" => (INFO, Vec::new(), BTreeMap::new()),
            "get_status" => (STATUS, Vec::new(), BTreeMap::new()),
            "get_announcement" => (ANNOUNCEMENT, Vec::new(), BTreeMap::new()),
            "get_order_book_details" => (
                ORDER_BOOK_DETAILS,
                self.market_query(&params, &["market_id", "filter"])?,
                BTreeMap::new(),
            ),
            "get_order_books" => (
                ORDER_BOOKS,
                self.market_query(&params, &["market_id", "filter"])?,
                BTreeMap::new(),
            ),
            "get_order_book_orders" => (
                ORDER_BOOK_ORDERS,
                self.market_query(&params, &["market_id", "limit"])?,
                BTreeMap::new(),
            ),
            "get_recent_trades" => (
                RECENT_TRADES,
                self.market_query(&params, &["market_id", "limit"])?,
                BTreeMap::new(),
            ),
            "get_trades" => (
                TRADES,
                self.market_query_renamed(
                    &params,
                    &[
                        ("market_id", "market_id"),
                        ("market_type", "market_type"),
                        ("account_index", "account_index"),
                        ("order_index", "order_index"),
                        ("sort_by", "sort_by"),
                        ("sort_dir", "sort_dir"),
                        ("cursor", "cursor"),
                        ("from_", "from"),
                        ("ask_filter", "ask_filter"),
                        ("role", "role"),
                        ("type_", "type"),
                        ("limit", "limit"),
                        ("aggregate", "aggregate"),
                        ("skip_ask_order_id", "skip_ask_order_id"),
                        ("skip_bid_order_id", "skip_bid_order_id"),
                        ("auth", "auth"),
                    ],
                )?,
                auth_header_from_params(&params, self.auto_auth(&params)?)?,
            ),
            "get_candles" => (
                CANDLES,
                self.market_query(
                    &params,
                    &[
                        "market_id",
                        "resolution",
                        "start_timestamp",
                        "end_timestamp",
                        "count_back",
                        "set_timestamp_to_end",
                    ],
                )?,
                BTreeMap::new(),
            ),
            "get_funding_rates" => (FUNDING_RATES, Vec::new(), BTreeMap::new()),
            "get_fundings" => (
                FUNDINGS,
                self.market_query(
                    &params,
                    &[
                        "market_id",
                        "resolution",
                        "start_timestamp",
                        "end_timestamp",
                        "count_back",
                    ],
                )?,
                BTreeMap::new(),
            ),
            "get_exchange_stats" => (EXCHANGE_STATS, Vec::new(), BTreeMap::new()),
            "get_execute_stats" => (EXECUTE_STATS, params.query(&["period"]), BTreeMap::new()),
            "get_exchange_metrics" => (
                EXCHANGE_METRICS,
                params.query(&["period", "kind", "filter", "value"]),
                BTreeMap::new(),
            ),
            "get_deposit_networks" => (DEPOSIT_NETWORKS, Vec::new(), BTreeMap::new()),
            "get_fastbridge_info" => (FASTBRIDGE_INFO, Vec::new(), BTreeMap::new()),
            "get_layer1_basic_info" => (LAYER1_BASIC_INFO, Vec::new(), BTreeMap::new()),
            "get_lease_options" => (LEASE_OPTIONS, Vec::new(), BTreeMap::new()),
            "get_withdrawal_delay" => (WITHDRAWAL_DELAY, Vec::new(), BTreeMap::new()),
            "get_account" => (
                ACCOUNT,
                params.query(&["by", "value", "active_only", "cursor"]),
                BTreeMap::new(),
            ),
            "get_accounts_by_l1_address" => (
                ACCOUNTS_BY_L1_ADDRESS,
                params.query(&["l1_address", "cursor"]),
                BTreeMap::new(),
            ),
            "get_account_metadata" => (
                ACCOUNT_METADATA,
                params.query(&["by", "value", "cursor"]),
                auth_header_from_params(&params, self.auto_auth(&params)?)?,
            ),
            "get_api_keys" => (
                API_KEYS,
                params.query(&["account_index", "api_key_index"]),
                BTreeMap::new(),
            ),
            "get_public_pools_metadata" => (
                PUBLIC_POOLS_METADATA,
                params.query(&["filter", "index", "limit", "account_index"]),
                auth_header_from_params(&params, self.auto_auth(&params)?)?,
            ),
            "get_pnl" => (
                PNL,
                params.query(&[
                    "by",
                    "value",
                    "resolution",
                    "start_timestamp",
                    "end_timestamp",
                    "count_back",
                    "ignore_transfers",
                ]),
                auth_header_from_params(&params, self.auto_auth(&params)?)?,
            ),
            "get_asset_details" => (ASSET_DETAILS, params.query(&["asset_id"]), BTreeMap::new()),
            "get_system_config" => (SYSTEM_CONFIG, Vec::new(), BTreeMap::new()),
            "get_tokens" => (
                TOKENS,
                params.query(&["account_index"]),
                auth_header_from_params(&params, self.auto_auth(&params)?)?,
            ),
            "get_token_list" => (TOKENLIST, Vec::new(), BTreeMap::new()),
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Lighter public method: {method_name}"
                )))
            }
        };
        query.retain(|(_, value)| !value.is_empty());
        headers.retain(|_, value| !value.is_empty());
        self.get_path(path, query, headers).await
    }

    pub(super) fn auto_auth(&self, params: &LighterParams) -> Result<Option<String>> {
        if params.get("authorization").is_some() || params.get("auth").is_some() {
            return Ok(None);
        }
        if self.api_private_keys.is_empty() {
            return Ok(None);
        }
        self.create_auth_token(None, None).map(Some)
    }

    pub(super) fn market_query(
        &self,
        params: &LighterParams,
        keys: &[&str],
    ) -> Result<Vec<(String, String)>> {
        self.market_query_renamed(
            params,
            &keys.iter().map(|key| (*key, *key)).collect::<Vec<_>>(),
        )
    }

    pub(super) fn market_query_renamed(
        &self,
        params: &LighterParams,
        keys: &[(&str, &str)],
    ) -> Result<Vec<(String, String)>> {
        let mut query = params.query_renamed(keys);
        if let Some(product_symbol) = params.get("product_symbol") {
            upsert(&mut query, "market_id", self.market_id(product_symbol)?);
        }
        Ok(query)
    }
}

pub(super) fn auth_header_from_params(
    params: &LighterParams,
    fallback: Option<String>,
) -> Result<BTreeMap<String, String>> {
    let mut headers = BTreeMap::new();
    let authorization = params.get("authorization").map(str::to_string).or(fallback);
    if let Some(authorization) = authorization {
        headers.insert("Authorization".to_string(), authorization);
    }
    Ok(headers)
}

pub(super) fn auth_header_required(
    client: &LighterClient,
    params: &LighterParams,
) -> Result<BTreeMap<String, String>> {
    let authorization = params
        .get("authorization")
        .map(str::to_string)
        .map(Ok)
        .unwrap_or_else(|| client.create_auth_token(None, None))?;
    let mut headers = BTreeMap::new();
    headers.insert("Authorization".to_string(), authorization);
    Ok(headers)
}

pub(super) fn upsert(query: &mut Vec<(String, String)>, key: &str, value: impl ToString) {
    if let Some((_, existing)) = query.iter_mut().find(|(candidate, _)| candidate == key) {
        *existing = value.to_string();
    } else {
        insert_optional_pair(query, key, Some(value));
    }
}
