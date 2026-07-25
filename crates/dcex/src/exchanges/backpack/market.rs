use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::BackpackClient;
use super::endpoints::*;
use super::params::BackpackParams;

impl BackpackClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = BackpackParams::from_pairs(params);
        self.validate_public_params(method_name, &params)?;
        let response = match method_name {
            "get_assets" => self.public_get(ASSETS, params.only(&["country"])).await,
            "get_collateral" => self.public_get(COLLATERAL, Vec::new()).await,
            "get_borrow_lend_markets" => self.public_get(BORROW_LEND_MARKETS, Vec::new()).await,
            "get_borrow_lend_market_history" => {
                self.public_get(
                    BORROW_LEND_MARKET_HISTORY,
                    params.only(&["interval", "symbol"]),
                )
                .await
            }
            "get_borrow_lend_apy" => {
                self.public_get(BORROW_LEND_APY, params.only(&["tierId"]))
                    .await
            }
            "get_markets" => self.public_get(MARKETS, params.only(&["marketType"])).await,
            "get_market" => {
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, &params)?;
                self.public_get(MARKET, query).await
            }
            "get_order_book_depth" => {
                let mut query = params.only(&["limit"]);
                self.push_required_symbol(&mut query, &params)?;
                self.public_get(DEPTH, query).await
            }
            "get_market_sessions" => self.public_get(MARKET_SESSIONS, Vec::new()).await,
            "get_securities" => self.public_get(SECURITIES, Vec::new()).await,
            "get_mark_prices" => {
                let mut query = params.only(&["marketType"]);
                self.push_optional_symbol(&mut query, &params)?;
                self.public_get(MARK_PRICES, query).await
            }
            "get_open_interest" => {
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, &params)?;
                self.public_get(OPEN_INTEREST, query).await
            }
            "get_funding_rates" => {
                let mut query = params.only(&["limit", "offset"]);
                self.push_required_symbol(&mut query, &params)?;
                self.public_get(FUNDING_RATES, query).await
            }
            "get_klines" => {
                let mut query =
                    params.only(&["interval", "startTime", "endTime", "priceType", "source"]);
                self.push_required_symbol(&mut query, &params)?;
                self.public_get(KLINES, query).await
            }
            "get_ticker" => {
                let mut query = params.only(&["interval", "source"]);
                self.push_required_symbol(&mut query, &params)?;
                self.public_get(TICKER, query).await
            }
            "get_tickers" => {
                self.public_get(TICKERS, params.only(&["interval", "source"]))
                    .await
            }
            "get_status" => self.public_get(STATUS, Vec::new()).await,
            "ping" => self.public_get(PING, Vec::new()).await,
            "get_time" => self.public_get(TIME, Vec::new()).await,
            "get_wallets" => self.public_get(WALLETS, Vec::new()).await,
            "get_recent_trades" => {
                let mut query = params.only(&["limit"]);
                self.push_required_symbol(&mut query, &params)?;
                self.public_get(TRADES, query).await
            }
            "get_historical_trades" => {
                let mut query = params.only(&["limit", "offset"]);
                self.push_required_symbol(&mut query, &params)?;
                self.public_get(HISTORICAL_TRADES, query).await
            }
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Backpack public method: {method_name}"
                )))
            }
        }?;
        Ok(response)
    }

    fn validate_public_params(&self, method_name: &str, params: &BackpackParams) -> Result<()> {
        const MARKET_TYPES: &[&str] = &["SPOT", "PERP", "IPERP", "DATED", "PREDICTION", "RFQ"];
        const KLINE_INTERVALS: &[&str] = &[
            "1s", "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d",
            "1w", "1month",
        ];
        match method_name {
            "get_assets" => params.ensure_allowed(&["country"], &[]),
            "get_collateral"
            | "get_borrow_lend_markets"
            | "get_market_sessions"
            | "get_securities"
            | "get_status"
            | "ping"
            | "get_time"
            | "get_wallets" => params.ensure_allowed(&[], &[]),
            "get_borrow_lend_market_history" => {
                params.ensure_allowed(&["interval", "symbol"], &[])?;
                params.required("interval")?;
                params.optional_one_of("interval", &["1d", "1w", "1month", "1year"])
            }
            "get_borrow_lend_apy" => {
                params.ensure_allowed(&["tierId"], &[])?;
                params.optional_i64_range("tierId", i32::MIN.into(), i32::MAX.into())
            }
            "get_markets" => {
                params.ensure_allowed(&["marketType"], &["marketType"])?;
                params.values_one_of("marketType", MARKET_TYPES)
            }
            "get_market" => {
                params.ensure_allowed(&["product_symbol", "symbol"], &[])?;
                validate_symbol_selector(params, true)
            }
            "get_order_book_depth" => {
                params.ensure_allowed(&["product_symbol", "symbol", "limit"], &[])?;
                validate_symbol_selector(params, true)?;
                params.optional_one_of("limit", &["5", "10", "20", "50", "100", "500", "1000"])
            }
            "get_mark_prices" => {
                params.ensure_allowed(&["product_symbol", "symbol", "marketType"], &[])?;
                validate_symbol_selector(params, false)?;
                params.optional_one_of("marketType", MARKET_TYPES)
            }
            "get_open_interest" => {
                params.ensure_allowed(&["product_symbol", "symbol"], &[])?;
                validate_symbol_selector(params, false)
            }
            "get_funding_rates" => {
                params.ensure_allowed(&["product_symbol", "symbol", "limit", "offset"], &[])?;
                validate_symbol_selector(params, true)?;
                params.optional_u64_range("limit", 1, 10_000)?;
                params.optional_u64_range("offset", 0, u64::MAX)
            }
            "get_klines" => {
                params.ensure_allowed(
                    &[
                        "product_symbol",
                        "symbol",
                        "interval",
                        "startTime",
                        "endTime",
                        "priceType",
                        "source",
                    ],
                    &[],
                )?;
                validate_symbol_selector(params, true)?;
                params.required("interval")?;
                params.optional_one_of("interval", KLINE_INTERVALS)?;
                params.required("startTime")?;
                params.ensure_time_order("startTime", "endTime")?;
                params.optional_one_of("priceType", &["Last", "Index", "Mark"])?;
                params.optional_one_of("source", &["Venue", "External"])?;
                if params.get("source") == Some("External")
                    && !matches!(params.get("priceType"), None | Some("Last"))
                {
                    return Err(DcexError::InvalidInput(
                        "Backpack External K-line data requires priceType=Last".to_string(),
                    ));
                }
                Ok(())
            }
            "get_ticker" => {
                params.ensure_allowed(&["product_symbol", "symbol", "interval", "source"], &[])?;
                validate_symbol_selector(params, true)?;
                validate_ticker_params(params)
            }
            "get_tickers" => {
                params.ensure_allowed(&["interval", "source"], &[])?;
                validate_ticker_params(params)
            }
            "get_recent_trades" => {
                params.ensure_allowed(&["product_symbol", "symbol", "limit"], &[])?;
                validate_symbol_selector(params, true)?;
                params.optional_u64_range("limit", 1, 1_000)
            }
            "get_historical_trades" => {
                params.ensure_allowed(&["product_symbol", "symbol", "limit", "offset"], &[])?;
                validate_symbol_selector(params, true)?;
                params.optional_u64_range("limit", 1, 1_000)?;
                params.optional_u64_range("offset", 0, u64::MAX)
            }
            _ => Ok(()),
        }
    }

    pub(super) fn push_required_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &BackpackParams,
    ) -> Result<()> {
        let symbol = params.required_any(&["product_symbol", "symbol"])?;
        query.push(("symbol".to_string(), self.exchange_symbol(symbol)?));
        Ok(())
    }

    pub(super) fn push_optional_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &BackpackParams,
    ) -> Result<()> {
        if let Some(symbol) = params.get_any(&["product_symbol", "symbol"]) {
            query.push(("symbol".to_string(), self.exchange_symbol(symbol)?));
        }
        Ok(())
    }
}

pub(super) fn validate_symbol_selector(params: &BackpackParams, required: bool) -> Result<()> {
    let product_symbol = params.get("product_symbol");
    let symbol = params.get("symbol");
    if product_symbol.is_some() && symbol.is_some() {
        return Err(DcexError::InvalidInput(
            "Backpack accepts either product_symbol or symbol, not both".to_string(),
        ));
    }
    if required && product_symbol.is_none() && symbol.is_none() {
        return Err(DcexError::InvalidInput(
            "missing required parameter: product_symbol or symbol".to_string(),
        ));
    }
    if product_symbol.is_some() {
        params.required("product_symbol")?;
    }
    if symbol.is_some() {
        params.required("symbol")?;
    }
    Ok(())
}

fn validate_ticker_params(params: &BackpackParams) -> Result<()> {
    params.optional_one_of("interval", &["1d", "1w"])?;
    params.optional_one_of("source", &["Venue", "External"])?;
    if params.get("source") == Some("External") && params.get("interval") != Some("1d") {
        return Err(DcexError::InvalidInput(
            "Backpack External ticker data requires interval=1d".to_string(),
        ));
    }
    Ok(())
}
