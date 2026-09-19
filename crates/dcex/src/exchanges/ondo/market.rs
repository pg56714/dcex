use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::OndoClient;
use super::endpoints::*;
use super::params::OndoParams;

impl OndoClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = OndoParams::from_pairs(params);
        let response = match method_name {
            "get_status" => {
                params.ensure_allowed(&[])?;
                self.public_get(STATUS, Vec::new()).await
            }
            "hello" | "ping" => {
                params.ensure_allowed(&[])?;
                self.public_get(HELLO, Vec::new()).await
            }
            "get_markets" => {
                params.ensure_allowed(&[])?;
                self.public_get(MARKETS, Vec::new()).await
            }
            "get_trades" | "get_recent_trades" => {
                let query = self.market_query(&params, &["limit", "cursor"])?;
                params.optional_u64("limit")?;
                self.public_get(TRADES, query).await
            }
            "get_order_book_depth" | "get_depth" => {
                let query = self.market_query(&params, &["depth"])?;
                params.optional_u64("depth")?;
                self.public_get(DEPTH, query).await
            }
            "get_symbol_info" => {
                params.ensure_allowed(&[])?;
                self.public_get(SYMBOL_INFO, Vec::new()).await
            }
            "get_price_history" => {
                params.ensure_allowed(&["symbol", "resolution", "from", "to"])?;
                params.ensure_required(&["symbol", "resolution", "from", "to"])?;
                params.ensure_time_order("from", "to")?;
                let query = params.only(&["symbol", "resolution", "from", "to"]);
                self.public_get(HISTORY, query).await
            }
            "get_funding_rates" => {
                self.public_get(FUNDING_RATES, self.market_query(&params, &[])?)
                    .await
            }
            "get_funding_rate_history" => {
                let query =
                    self.market_query(&params, &["limit", "cursor", "startTime", "endTime"])?;
                validate_pagination_and_time(&params)?;
                self.public_get(FUNDING_RATE_HISTORY, query).await
            }
            "get_mark_prices" => {
                params.ensure_allowed(&[])?;
                self.public_get(MARK_PRICES, Vec::new()).await
            }
            "get_open_interest" => {
                params.ensure_allowed(&[])?;
                self.public_get(OPEN_INTEREST, Vec::new()).await
            }
            "get_volume" => {
                params.ensure_allowed(&[])?;
                self.public_get(VOLUME, Vec::new()).await
            }
            "get_contracts" => {
                params.ensure_allowed(&["sparkline"])?;
                params.optional_bool("sparkline")?;
                self.public_get(CONTRACTS, params.only(&["sparkline"]))
                    .await
            }
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Ondo public method: {method_name}"
                )))
            }
        }?;
        Ok(response)
    }

    pub(super) fn required_market(&self, params: &OndoParams) -> Result<String> {
        let value = params
            .get("product_symbol")
            .or_else(|| params.get("market"))
            .or_else(|| params.get("symbol"))
            .ok_or_else(|| {
                DcexError::InvalidInput(
                    "missing required parameter: market or product_symbol".to_string(),
                )
            })?;
        self.exchange_symbol(value)
    }

    pub(super) fn market_query(
        &self,
        params: &OndoParams,
        extra: &[&str],
    ) -> Result<Vec<(String, String)>> {
        let mut allowed = vec!["market", "product_symbol"];
        allowed.extend_from_slice(extra);
        params.ensure_allowed(&allowed)?;
        let mut query = vec![("market".to_string(), self.required_market(params)?)];
        query.extend(params.only(extra));
        Ok(query)
    }
}

pub(super) fn validate_pagination_and_time(params: &OndoParams) -> Result<()> {
    params.optional_u64("limit")?;
    params.optional_u64("startTime")?;
    params.optional_u64("endTime")?;
    params.ensure_time_order("startTime", "endTime")
}
