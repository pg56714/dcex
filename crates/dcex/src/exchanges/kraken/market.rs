use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::{KrakenAuth, KrakenClient};
use super::endpoints::*;
use super::params::{take_param, KrakenParams};

impl KrakenClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let mut params = KrakenParams::from_pairs(params).into_inner();
        let (auth, path) = match method_name {
            "get_server_time" => (KrakenAuth::Spot, SPOT_SERVER_TIME.to_string()),
            "get_spot_asset_pairs" => (KrakenAuth::Spot, SPOT_ASSET_PAIRS.to_string()),
            "get_spot_ticker" => {
                self.normalize_symbol_query(&mut params, "pair", "")?;
                (KrakenAuth::Spot, SPOT_TICKER.to_string())
            }
            "get_spot_orderbook" => {
                self.normalize_symbol_query(&mut params, "pair", "")?;
                (KrakenAuth::Spot, SPOT_ORDERBOOK.to_string())
            }
            "get_spot_public_trades" => {
                self.normalize_symbol_query(&mut params, "pair", "")?;
                (KrakenAuth::Spot, SPOT_PUBLIC_TRADES.to_string())
            }
            "get_spot_kline" => {
                self.normalize_symbol_query(&mut params, "pair", "")?;
                (KrakenAuth::Spot, SPOT_OHLC.to_string())
            }
            "get_futures_instruments" => (KrakenAuth::Futures, FUTURES_INSTRUMENTS.to_string()),
            "get_futures_tickers" => {
                self.normalize_symbol_query(&mut params, "symbol", "PF_")?;
                (KrakenAuth::Futures, FUTURES_TICKERS.to_string())
            }
            "get_futures_orderbook" => {
                self.normalize_symbol_query(&mut params, "symbol", "PF_")?;
                (KrakenAuth::Futures, FUTURES_ORDERBOOK.to_string())
            }
            "get_futures_public_trades" => {
                self.normalize_symbol_query(&mut params, "symbol", "PF_")?;
                (KrakenAuth::Futures, FUTURES_PUBLIC_TRADES.to_string())
            }
            "get_futures_kline" => {
                let tick_type =
                    take_param(&mut params, "tick_type").unwrap_or_else(|| "trade".to_string());
                let symbol = self.take_symbol(&mut params, "PF_")?;
                let resolution = take_param(&mut params, "timeframe")
                    .ok_or_else(|| DcexError::InvalidInput("timeframe is required.".to_string()))?;
                (
                    KrakenAuth::Futures,
                    format!("{FUTURES_CANDLES}/{tick_type}/{symbol}/{resolution}"),
                )
            }
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Kraken public method: {method_name}"
                )));
            }
        };

        self.request(HttpMethod::Get, auth, path, params, None, false)
            .await
    }

    fn take_symbol(
        &self,
        params: &mut Vec<(String, String)>,
        futures_prefix: &str,
    ) -> Result<String> {
        if let Some(symbol) = take_param(params, "symbol") {
            return self.exchange_symbol(&symbol, futures_prefix);
        }
        if let Some(product_symbol) = take_param(params, "product_symbol") {
            return self.exchange_symbol(&product_symbol, futures_prefix);
        }
        Err(DcexError::InvalidInput(
            "Kraken symbol is required.".to_string(),
        ))
    }

    fn normalize_symbol_query(
        &self,
        params: &mut [(String, String)],
        target_key: &str,
        futures_prefix: &str,
    ) -> Result<()> {
        for (key, value) in params.iter_mut() {
            if key == "product_symbol" {
                *key = target_key.to_string();
                *value = self.exchange_symbol(value, futures_prefix)?;
            } else if key == target_key {
                *value = self.exchange_symbol(value, futures_prefix)?;
            }
        }
        Ok(())
    }
}
