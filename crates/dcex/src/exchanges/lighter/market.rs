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
        self.validate_public_params(method_name, &params)?;
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
            if params.get("authorization").is_some() {
                params.required("authorization")?;
            }
            if params.get("auth").is_some() {
                params.required("auth")?;
            }
            return Ok(None);
        }
        if self.api_private_keys.is_empty() {
            return Ok(None);
        }
        self.create_auth_token().map(Some)
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

    fn validate_public_params(&self, method_name: &str, params: &LighterParams) -> Result<()> {
        match method_name {
            "get_info"
            | "get_status"
            | "get_announcement"
            | "get_funding_rates"
            | "get_exchange_stats"
            | "get_deposit_networks"
            | "get_fastbridge_info"
            | "get_layer1_basic_info"
            | "get_lease_options"
            | "get_withdrawal_delay"
            | "get_system_config"
            | "get_token_list" => params.ensure_allowed(&[]),
            "get_order_book_details" | "get_order_books" => {
                params.ensure_allowed(&["market_id", "product_symbol", "filter"])?;
                validate_market_selector(params, false)?;
                params.optional_one_of("filter", &["all", "spot", "perp"])?;
                Ok(())
            }
            "get_order_book_orders" => {
                params.ensure_allowed(&["market_id", "product_symbol", "limit"])?;
                validate_market_selector(params, true)?;
                params.required_u64_range("limit", 1, 250)?;
                Ok(())
            }
            "get_recent_trades" => {
                params.ensure_allowed(&["market_id", "product_symbol", "limit"])?;
                validate_market_selector(params, true)?;
                params.required_u64_range("limit", 1, 100)?;
                Ok(())
            }
            "get_trades" => {
                params.ensure_allowed(&[
                    "market_id",
                    "product_symbol",
                    "market_type",
                    "account_index",
                    "order_index",
                    "sort_by",
                    "sort_dir",
                    "cursor",
                    "from_",
                    "ask_filter",
                    "role",
                    "type_",
                    "limit",
                    "aggregate",
                    "skip_ask_order_id",
                    "skip_bid_order_id",
                    "authorization",
                ])?;
                validate_market_selector(params, false)?;
                params.optional_one_of("market_type", &["all", "spot", "perp"])?;
                params.required_one_of("sort_by", &["block_height", "timestamp", "trade_id"])?;
                params.optional_one_of("sort_dir", &["desc"])?;
                params.optional_one_of("role", &["all", "maker", "taker"])?;
                params.optional_one_of(
                    "type_",
                    &[
                        "all",
                        "trade",
                        "liquidation",
                        "deleverage",
                        "market-settlement",
                    ],
                )?;
                params.required_u64_range("limit", 1, 100)?;
                validate_optional_i64(
                    params,
                    &["account_index", "order_index", "from_", "ask_filter"],
                )?;
                params.optional_bool("aggregate")?;
                validate_optional_nonempty(
                    params,
                    &[
                        "cursor",
                        "skip_ask_order_id",
                        "skip_bid_order_id",
                        "authorization",
                    ],
                )
            }
            "get_candles" => {
                params.ensure_allowed(&[
                    "market_id",
                    "product_symbol",
                    "resolution",
                    "start_timestamp",
                    "end_timestamp",
                    "count_back",
                    "set_timestamp_to_end",
                ])?;
                validate_market_selector(params, true)?;
                params.required_one_of(
                    "resolution",
                    &["1m", "5m", "15m", "30m", "1h", "4h", "12h", "1d", "1w"],
                )?;
                validate_time_series(params)?;
                params.optional_bool("set_timestamp_to_end")?;
                Ok(())
            }
            "get_fundings" => {
                params.ensure_allowed(&[
                    "market_id",
                    "product_symbol",
                    "resolution",
                    "start_timestamp",
                    "end_timestamp",
                    "count_back",
                ])?;
                validate_market_selector(params, true)?;
                params.required_one_of("resolution", &["1h", "1d"])?;
                validate_time_series(params)
            }
            "get_execute_stats" => {
                params.ensure_allowed(&["period"])?;
                params.required_one_of("period", &["d", "w", "m", "q", "y", "all"])?;
                Ok(())
            }
            "get_exchange_metrics" => {
                params.ensure_allowed(&["period", "kind", "filter", "value"])?;
                params.required_one_of("period", &["h", "d", "w", "m", "q", "y", "all"])?;
                params.required_one_of(
                    "kind",
                    &[
                        "volume",
                        "maker_fee",
                        "taker_fee",
                        "liquidation_fee",
                        "trade_count",
                        "liquidation_count",
                        "liquidation_volume",
                        "inflow",
                        "outflow",
                        "transfer_fee",
                        "withdraw_fee",
                        "open_interest",
                        "account_count",
                        "active_account_count",
                        "tps",
                        "buyback",
                        "buyback_usdc",
                    ],
                )?;
                params.optional_one_of("filter", &["byMarket"])?;
                validate_optional_nonempty(params, &["value"])
            }
            "get_account" => {
                params.ensure_allowed(&["by", "value", "active_only", "cursor"])?;
                params.required_one_of("by", &["index", "l1_address"])?;
                params.required("value")?;
                params.optional_bool("active_only")?;
                validate_optional_nonempty(params, &["cursor"])
            }
            "get_accounts_by_l1_address" => {
                params.ensure_allowed(&["l1_address", "cursor"])?;
                params.required("l1_address")?;
                validate_optional_nonempty(params, &["cursor"])
            }
            "get_account_metadata" => {
                params.ensure_allowed(&["by", "value", "cursor", "authorization"])?;
                params.required_one_of("by", &["index", "l1_address"])?;
                params.required("value")?;
                validate_optional_nonempty(params, &["cursor", "authorization"])
            }
            "get_api_keys" => {
                params.ensure_allowed(&["account_index", "api_key_index"])?;
                params.required_i64("account_index")?;
                params.optional_u64_range("api_key_index", 0, 255)?;
                Ok(())
            }
            "get_public_pools_metadata" => {
                params.ensure_allowed(&[
                    "filter",
                    "index",
                    "limit",
                    "account_index",
                    "authorization",
                ])?;
                params.optional_one_of(
                    "filter",
                    &["all", "user", "protocol", "account_index", "stake"],
                )?;
                params.required_i64("index")?;
                params.required_u64_range("limit", 1, 100)?;
                validate_optional_i64(params, &["account_index"])?;
                validate_optional_nonempty(params, &["authorization"])
            }
            "get_pnl" => {
                params.ensure_allowed(&[
                    "by",
                    "value",
                    "resolution",
                    "start_timestamp",
                    "end_timestamp",
                    "count_back",
                    "ignore_transfers",
                    "authorization",
                ])?;
                params.required_one_of("by", &["index"])?;
                params.required("value")?;
                params.required_one_of("resolution", &["1m", "5m", "15m", "1h", "4h", "1d"])?;
                validate_time_series(params)?;
                params.optional_bool("ignore_transfers")?;
                validate_optional_nonempty(params, &["authorization"])
            }
            "get_asset_details" => {
                params.ensure_allowed(&["asset_id"])?;
                validate_optional_i64(params, &["asset_id"])
            }
            "get_tokens" => {
                params.ensure_allowed(&["account_index", "authorization"])?;
                params.required_i64("account_index")?;
                validate_optional_nonempty(params, &["authorization"])
            }
            _ => Ok(()),
        }
    }
}

pub(super) fn auth_header_from_params(
    params: &LighterParams,
    fallback: Option<String>,
) -> Result<BTreeMap<String, String>> {
    let mut headers = BTreeMap::new();
    let authorization = params
        .get("authorization")
        .map(|_| params.required("authorization").map(str::to_string))
        .transpose()?
        .or(fallback);
    if let Some(authorization) = authorization {
        headers.insert("Authorization".to_string(), authorization);
    }
    Ok(headers)
}

pub(super) fn auth_header_required(
    client: &LighterClient,
    params: &LighterParams,
) -> Result<BTreeMap<String, String>> {
    let authorization = if params.get("authorization").is_some() {
        params.required("authorization")?.to_string()
    } else {
        client.create_auth_token()?
    };
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

fn validate_time_series(params: &LighterParams) -> Result<()> {
    params.required_u64_range("start_timestamp", 0, 5_000_000_000_000)?;
    params.required_u64_range("end_timestamp", 0, 5_000_000_000_000)?;
    params.required_i64("count_back")?;
    params.ensure_time_order("start_timestamp", "end_timestamp")
}

fn validate_optional_i64(params: &LighterParams, keys: &[&str]) -> Result<()> {
    for key in keys {
        params.optional_i64(key)?;
    }
    Ok(())
}

fn validate_optional_nonempty(params: &LighterParams, keys: &[&str]) -> Result<()> {
    for key in keys {
        if params.get(key).is_some() {
            params.required(key)?;
        }
    }
    Ok(())
}
