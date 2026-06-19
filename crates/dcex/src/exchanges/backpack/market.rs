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
            "get_markets" => self.public_get(MARKETS, Vec::new()).await,
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
                let mut query = params.only(&["interval", "startTime", "endTime", "priceType"]);
                self.push_required_symbol(&mut query, &params)?;
                self.public_get(KLINES, query).await
            }
            "get_ticker" => {
                let mut query = params.only(&["interval"]);
                self.push_required_symbol(&mut query, &params)?;
                self.public_get(TICKER, query).await
            }
            "get_tickers" => self.public_get(TICKERS, params.only(&["interval"])).await,
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
