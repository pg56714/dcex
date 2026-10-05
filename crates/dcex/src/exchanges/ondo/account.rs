use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::OndoClient;
use super::endpoints::*;
use super::market::validate_pagination_and_time;
use super::params::{OndoParams, path_with_id};

impl OndoClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &OndoParams,
    ) -> Result<Option<ValidatedResponse>> {
        let response = match method_name {
            "create_withdrawal" | "sandbox_withdrawal" => {
                self.dispatch_create_withdrawal(method_name, params).await
            }
            "get_account" => self.empty_private_get(params, ACCOUNT).await,
            "get_open_order_counts" => self.empty_private_get(params, ORDER_COUNTS).await,
            "get_deposits" => self.empty_private_get(params, DEPOSITS).await,
            "get_withdrawals" => self.empty_private_get(params, WITHDRAWALS).await,
            "get_withdrawal_limits" => self.empty_private_get(params, WITHDRAWAL_LIMITS).await,
            "get_address_book" => self.empty_private_get(params, ADDRESS_BOOK).await,
            "get_address_book_challenge" => {
                let body = params.body(
                    &["walletAddress", "chainId", "withdrawalAddress"],
                    &["walletAddress", "chainId", "withdrawalAddress"],
                    &[],
                    &[],
                    &[],
                )?;
                require_string_fields(&body, &["walletAddress", "chainId", "withdrawalAddress"])?;
                require_enum_field(&body, "chainId", &["1", "43114"])?;
                self.private_post(ADDRESS_BOOK_CHALLENGE, body).await
            }
            "complete_address_book_challenge" => {
                let body = params.body(
                    &["id", "signature", "addressLabel"],
                    &["id", "signature"],
                    &[],
                    &[],
                    &[],
                )?;
                require_string_fields(&body, &["id", "signature"])?;
                optional_string_field(&body, "addressLabel")?;
                self.private_post(ADDRESS_BOOK_COMPLETE, body).await
            }
            "sandbox_deposit" => {
                let body = params.body(
                    &["amount", "symbol", "deposit_destination", "chain_id"],
                    &["amount", "symbol", "deposit_destination", "chain_id"],
                    &[],
                    &[],
                    &["deposit_destination"],
                )?;
                require_string_fields(&body, &["amount", "symbol", "chain_id"])?;
                require_enum_field(
                    &body,
                    "chain_id",
                    &[
                        "avax-c-chain",
                        "avax-fuji-c-chain",
                        "eth-mainnet",
                        "eth-sepolia",
                        "btc-mainnet",
                        "btc-testnet",
                        "sol-mainnet",
                        "sol-testnet",
                        "bsc-mainnet",
                        "bsc-testnet",
                    ],
                )?;
                validate_account_wallet_key(&body, "deposit_destination")?;
                self.private_post(SANDBOX_DEPOSIT, body).await
            }
            "provision_deposit_address" => {
                let body = params.body(
                    &["network", "symbol", "deposit_destination"],
                    &["network", "symbol", "deposit_destination"],
                    &[],
                    &[],
                    &["deposit_destination"],
                )?;
                require_string_fields(&body, &["network", "symbol"])?;
                require_enum_field(&body, "network", &["avalanche", "ethereum", "solana"])?;
                validate_account_wallet_key(&body, "deposit_destination")?;
                self.private_post(PROVISION_ADDRESS, body).await
            }
            "get_withdrawal_status" => self.get_withdrawal_status_request(params).await,
            "edit_address_book_entry" => {
                let body = params.body(
                    &["withdrawalAddress", "addressLabel"],
                    &["withdrawalAddress"],
                    &[],
                    &[],
                    &[],
                )?;
                require_string_fields(&body, &["withdrawalAddress"])?;
                optional_string_field(&body, "addressLabel")?;
                self.private_put(ADDRESS_BOOK, body).await
            }
            "remove_address_book_entry" => {
                let body = params.body(
                    &["withdrawalAddress"],
                    &["withdrawalAddress"],
                    &[],
                    &[],
                    &[],
                )?;
                require_string_fields(&body, &["withdrawalAddress"])?;
                self.private_delete_body(ADDRESS_BOOK, body).await
            }
            "get_positions" => self.empty_private_get(params, POSITIONS).await,
            "get_balance" => self.empty_private_get(params, BALANCE).await,
            "get_order_summaries" => self.empty_private_get(params, ORDER_SUMMARIES).await,
            "get_portfolio_summary" => self.empty_private_get(params, PORTFOLIO_SUMMARY).await,
            "get_deposit" => {
                params.ensure_allowed(&["depositID"])?;
                let id = params.path_segment("depositID")?;
                self.private_get(&path_with_id(DEPOSITS, id), Vec::new())
                    .await
            }
            "get_withdrawal" => self.get_withdrawal_request(params).await,
            "get_deposit_addresses" => {
                let body = params.body(
                    &["coins", "network", "depositDestination"],
                    &["coins"],
                    &[],
                    &[],
                    &["coins", "depositDestination"],
                )?;
                self.private_post(DEPOSIT_ADDRESSES, body).await
            }
            "export_deposits_csv" | "export_withdrawals_csv" => {
                let body = params.body(
                    &["start_time", "end_time"],
                    &[],
                    &[],
                    &["start_time", "end_time"],
                    &[],
                )?;
                let path = if method_name == "export_deposits_csv" {
                    DEPOSITS_CSV
                } else {
                    WITHDRAWALS_CSV
                };
                self.private_post(path, body).await
            }
            "get_klines" | "get_candles" => {
                params.ensure_allowed(&["market", "product_symbol", "resolution", "from", "to"])?;
                params.ensure_required(&["resolution", "from", "to"])?;
                params.ensure_time_order("from", "to")?;
                let mut query = vec![("market".to_string(), self.required_market(params)?)];
                query.extend(params.only(&["resolution", "from", "to"]));
                self.private_get(CANDLES, query).await
            }
            "get_funding_fee_payments" | "get_liquidation_history" => {
                params.ensure_allowed(&["market", "limit", "cursor", "startTime", "endTime"])?;
                validate_pagination_and_time(params)?;
                let path = if method_name == "get_funding_fee_payments" {
                    FUNDING_FEES
                } else {
                    LIQUIDATION_HISTORY
                };
                self.private_get(
                    path,
                    params.only(&["market", "limit", "cursor", "startTime", "endTime"]),
                )
                .await
            }
            "get_max_order_size" => {
                let query = self.market_query(params, &["buffer"])?;
                self.private_get(MAX_ORDER_SIZE, query).await
            }
            "get_leverage" => {
                params.ensure_allowed(&["market", "product_symbol"])?;
                let query =
                    if params.get("market").is_some() || params.get("product_symbol").is_some() {
                        vec![("market".to_string(), self.required_market(params)?)]
                    } else {
                        Vec::new()
                    };
                self.private_get(LEVERAGE, query).await
            }
            "set_leverage" => {
                let body = params.body(
                    &["market", "leverage"],
                    &["market", "leverage"],
                    &[],
                    &[],
                    &[],
                )?;
                self.private_post(LEVERAGE, body).await
            }
            "get_portfolio_summary_graph" => {
                params.ensure_allowed(&["range"])?;
                params.optional_one_of("range", &["24h", "7d", "30d", "all"])?;
                self.private_get(PORTFOLIO_GRAPH, params.only(&["range"]))
                    .await
            }
            _ => return Ok(None),
        }?;
        Ok(Some(response))
    }

    async fn empty_private_get(
        &self,
        params: &OndoParams,
        path: &str,
    ) -> Result<ValidatedResponse> {
        params.ensure_allowed(&[])?;
        self.private_get(path, Vec::new()).await
    }
}

pub(super) fn require_string_fields(body: &Value, keys: &[&str]) -> Result<()> {
    for key in keys {
        if body
            .get(*key)
            .and_then(Value::as_str)
            .is_none_or(|value| value.trim().is_empty())
        {
            return Err(DcexError::InvalidInput(format!(
                "Ondo body field {key} must be a nonempty string"
            )));
        }
    }
    Ok(())
}

pub(super) fn optional_string_field(body: &Value, key: &str) -> Result<()> {
    if body.get(key).is_some()
        && body
            .get(key)
            .and_then(Value::as_str)
            .is_none_or(|value| value.trim().is_empty())
    {
        return Err(DcexError::InvalidInput(format!(
            "Ondo body field {key} must be a nonempty string"
        )));
    }
    Ok(())
}

pub(super) fn require_enum_field(body: &Value, key: &str, allowed: &[&str]) -> Result<()> {
    let value = body.get(key).and_then(Value::as_str).ok_or_else(|| {
        DcexError::InvalidInput(format!("Ondo body field {key} must be a string"))
    })?;
    if !allowed.contains(&value) {
        return Err(DcexError::InvalidInput(format!(
            "invalid Ondo {key}: {value}; expected one of {}",
            allowed.join(", ")
        )));
    }
    Ok(())
}

pub(super) fn validate_account_wallet_key(body: &Value, key: &str) -> Result<()> {
    let wallet_key = body.get(key).and_then(Value::as_object).ok_or_else(|| {
        DcexError::InvalidInput(format!("Ondo body field {key} must be an object"))
    })?;
    for field in wallet_key.keys() {
        if !matches!(field.as_str(), "id" | "wallet") {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Ondo {key} field: {field}"
            )));
        }
    }
    if wallet_key
        .get("id")
        .and_then(Value::as_str)
        .is_none_or(|value| value.trim().is_empty())
    {
        return Err(DcexError::InvalidInput(format!(
            "Ondo body field {key}.id must be a nonempty string"
        )));
    }
    if !matches!(
        wallet_key.get("wallet").and_then(Value::as_str),
        Some("main" | "margin")
    ) {
        return Err(DcexError::InvalidInput(format!(
            "Ondo body field {key}.wallet must be main or margin"
        )));
    }
    Ok(())
}
