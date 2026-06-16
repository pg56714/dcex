use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::BitgetClient;
use super::endpoints::*;
use super::params::BitgetParams;

impl BitgetClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = BitgetParams::from_pairs(params);
        match method_name {
            "get_spot_coins" => self.public_get(SPOT_COINS, params.into_inner()).await,
            "get_spot_symbols" => {
                self.public_get(
                    SPOT_SYMBOLS,
                    self.normalize_symbol_params(params.into_inner())?,
                )
                .await
            }
            "get_spot_tickers" => {
                self.public_get(
                    SPOT_TICKERS,
                    self.normalize_symbol_params(params.into_inner())?,
                )
                .await
            }
            "get_spot_orderbook" => {
                self.public_get(
                    SPOT_ORDERBOOK,
                    self.normalize_symbol_params(params.into_inner())?,
                )
                .await
            }
            "get_spot_kline" => {
                self.public_get(
                    SPOT_CANDLES,
                    self.normalize_symbol_params(params.into_inner())?,
                )
                .await
            }
            "get_spot_history_kline" => {
                self.public_get(
                    SPOT_HISTORY_CANDLES,
                    self.normalize_symbol_params(params.into_inner())?,
                )
                .await
            }
            "get_spot_recent_trades" => {
                self.public_get(
                    SPOT_RECENT_TRADES,
                    self.normalize_symbol_params(params.into_inner())?,
                )
                .await
            }
            "get_spot_market_trades" => {
                self.public_get(
                    SPOT_MARKET_TRADES,
                    self.normalize_symbol_params(params.into_inner())?,
                )
                .await
            }
            "get_futures_contracts" => {
                self.public_get(
                    FUTURES_CONTRACTS,
                    self.normalize_symbol_params(params.into_inner())?,
                )
                .await
            }
            "get_futures_ticker" => {
                self.public_get(
                    FUTURES_TICKER,
                    self.normalize_symbol_params(params.into_inner())?,
                )
                .await
            }
            "get_futures_tickers" => self.public_get(FUTURES_TICKERS, params.into_inner()).await,
            "get_futures_orderbook" => {
                self.public_get(
                    FUTURES_ORDERBOOK,
                    self.normalize_symbol_params(params.into_inner())?,
                )
                .await
            }
            "get_futures_kline" => {
                self.public_get(
                    FUTURES_CANDLES,
                    self.normalize_symbol_params(params.into_inner())?,
                )
                .await
            }
            "get_futures_history_kline" => {
                self.public_get(
                    FUTURES_HISTORY_CANDLES,
                    self.normalize_symbol_params(params.into_inner())?,
                )
                .await
            }
            "get_futures_recent_trades" => {
                self.public_get(
                    FUTURES_RECENT_TRADES,
                    self.normalize_symbol_params(params.into_inner())?,
                )
                .await
            }
            "get_futures_current_funding_rate" => {
                self.public_get(
                    FUTURES_CURRENT_FUNDING_RATE,
                    self.normalize_symbol_params(params.into_inner())?,
                )
                .await
            }
            "get_futures_history_funding_rate" => {
                self.public_get(
                    FUTURES_HISTORY_FUNDING_RATE,
                    self.normalize_symbol_params(params.into_inner())?,
                )
                .await
            }
            "get_futures_open_interest" => {
                self.public_get(
                    FUTURES_OPEN_INTEREST,
                    self.normalize_symbol_params(params.into_inner())?,
                )
                .await
            }
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported Bitget public method: {method_name}"
            ))),
        }
    }
}
