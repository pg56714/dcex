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
        crate::exchanges::input_contracts::pairs("ondo", method_name, &params)?;
        let params = OndoParams::from_pairs(params);
        let response = match method_name {
            "get_spot_depth" | "get_spot_trades" => {
                params.ensure_allowed(&["market", "product_symbol"])?;
                let raw = params
                    .get("market")
                    .or_else(|| params.get("product_symbol"))
                    .ok_or_else(|| DcexError::InvalidInput("missing Ondo spot market".into()))?;
                let market = raw.strip_suffix("-SPOT").unwrap_or(raw);
                let parts: Vec<_> = market.split('-').collect();
                if parts.len() != 2
                    || parts.iter().any(|part| {
                        part.is_empty()
                            || !part.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'_')
                    })
                {
                    return Err(DcexError::InvalidInput(
                        "Ondo spot market requires BASE-QUOTE or BASE-QUOTE-SPOT".into(),
                    ));
                }
                let path = if method_name == "get_spot_depth" {
                    SPOT_DEPTH
                } else {
                    SPOT_TRADES
                };
                self.spot_public_get(path, vec![("market".into(), market.into())])
                    .await
            }
            "get_spot_symbol_info" => {
                params.ensure_allowed(&[])?;
                self.spot_public_get(SPOT_SYMBOL_INFO, vec![]).await
            }
            "get_spot_price_history" => {
                params.ensure_allowed(&["symbol", "resolution", "from", "to"])?;
                params.ensure_required(&["symbol", "resolution", "from", "to"])?;
                let symbol = params.required("symbol")?;
                if !symbol
                    .bytes()
                    .all(|b| b.is_ascii_alphanumeric() || b == b'_')
                {
                    return Err(DcexError::InvalidInput(
                        "Ondo spot history requires a TradingView symbol such as SPYUSDC".into(),
                    ));
                }
                params.optional_u64("from")?;
                params.optional_u64("to")?;
                params.ensure_time_order("from", "to")?;
                self.spot_public_get(
                    SPOT_HISTORY,
                    params.only(&["symbol", "resolution", "from", "to"]),
                )
                .await
            }
            "get_login_challenge" | "complete_login_challenge" => {
                static ROUTES: std::sync::OnceLock<Vec<crate::exchanges::schema::Route>> =
                    std::sync::OnceLock::new();
                let route = crate::exchanges::schema::route(
                    &ROUTES,
                    include_str!("schemas/routes_auth.json"),
                    method_name,
                )
                .expect("matched auth route");
                route.validate(|key| params.get(key))?;
                let path = route.path;
                let body = params.body(route.fields, route.required, &[], &[], &[])?;
                if body.as_object().is_some_and(|o| {
                    o.values()
                        .any(|v| v.as_str().is_none_or(|s| s.trim().is_empty()))
                }) {
                    return Err(DcexError::InvalidInput(
                        "Ondo login fields must be nonempty strings".into(),
                    ));
                }
                if method_name == "get_login_challenge"
                    && !["1", "43114"].contains(&body["chainId"].as_str().unwrap_or_default())
                {
                    return Err(DcexError::InvalidInput(
                        "Ondo login chainId must be 1 or 43114".into(),
                    ));
                }
                self.request(
                    crate::http::HttpMethod::Post,
                    path,
                    vec![],
                    Some(serde_json::to_vec(&body).map_err(|e| DcexError::Decode(e.to_string()))?),
                    false,
                    std::collections::BTreeMap::new(),
                )
                .await
            }
            "get_status" => {
                params.ensure_allowed(&[])?;
                self.public_get(STATUS, Vec::new()).await
            }
            "hello" => {
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
                )));
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

    async fn spot_public_get(
        &self,
        path: &str,
        query: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.request(
            crate::http::HttpMethod::Get,
            path,
            query,
            None,
            false,
            std::collections::BTreeMap::new(),
        )
        .await
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
