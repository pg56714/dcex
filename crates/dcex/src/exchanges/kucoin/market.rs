use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::{KucoinClient, KucoinMarket};
use super::endpoints::*;
use super::params::{normalize_futures_timeframe, normalize_spot_timeframe, take_param};

impl KucoinClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        mut params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let (market, path, signed) = match method_name {
            "get_spot_instrument_info" => {
                (KucoinMarket::Spot, SPOT_INSTRUMENT_INFO.to_string(), false)
            }
            "get_spot_ticker" => {
                self.normalize_symbol_query(&mut params, false)?;
                (KucoinMarket::Spot, SPOT_TICKER.to_string(), false)
            }
            "get_spot_all_tickers" => (KucoinMarket::Spot, SPOT_ALL_TICKERS.to_string(), false),
            "get_spot_orderbook" => {
                self.normalize_symbol_query(&mut params, false)?;
                (KucoinMarket::Spot, SPOT_ORDERBOOK.to_string(), true)
            }
            "get_spot_public_trades" => {
                self.normalize_symbol_query(&mut params, false)?;
                (KucoinMarket::Spot, SPOT_PUBLIC_TRADES.to_string(), false)
            }
            "get_spot_kline" => {
                self.normalize_symbol_query(&mut params, false)?;
                normalize_spot_timeframe(&mut params)?;
                (KucoinMarket::Spot, SPOT_KLINE.to_string(), false)
            }
            "get_futures_contracts" => {
                (KucoinMarket::Futures, FUTURES_CONTRACTS.to_string(), false)
            }
            "get_futures_contract" => {
                let symbol = if let Some(symbol) = take_param(&mut params, "symbol") {
                    self.exchange_symbol(&symbol, true)?
                } else if let Some(product_symbol) = take_param(&mut params, "product_symbol") {
                    self.exchange_symbol(&product_symbol, true)?
                } else {
                    return Err(DcexError::InvalidInput(
                        "KuCoin symbol is required.".to_string(),
                    ));
                };
                (
                    KucoinMarket::Futures,
                    format!("/api/v1/contracts/{symbol}"),
                    false,
                )
            }
            "get_futures_ticker" => {
                self.normalize_symbol_query(&mut params, true)?;
                (KucoinMarket::Futures, FUTURES_TICKER.to_string(), false)
            }
            "get_futures_orderbook" => {
                self.normalize_symbol_query(&mut params, true)?;
                let path = take_param(&mut params, "depth")
                    .map(|depth| format!("/api/v1/level2/depth{depth}"))
                    .unwrap_or_else(|| FUTURES_ORDERBOOK.to_string());
                (KucoinMarket::Futures, path, false)
            }
            "get_futures_public_trades" => {
                self.normalize_symbol_query(&mut params, true)?;
                (
                    KucoinMarket::Futures,
                    FUTURES_PUBLIC_TRADES.to_string(),
                    false,
                )
            }
            "get_futures_kline" => {
                self.normalize_symbol_query(&mut params, true)?;
                normalize_futures_timeframe(&mut params)?;
                (KucoinMarket::Futures, FUTURES_KLINE.to_string(), false)
            }
            "get_futures_open_interest" => {
                self.normalize_symbol_query(&mut params, true)?;
                (KucoinMarket::Spot, FUTURES_OPEN_INTEREST.to_string(), false)
            }
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported KuCoin public method: {method_name}"
                )));
            }
        };
        self.request(HttpMethod::Get, market, path, params, None, signed)
            .await
    }

    fn normalize_symbol_query(&self, params: &mut [(String, String)], futures: bool) -> Result<()> {
        for (key, value) in params.iter_mut() {
            if matches!(key.as_str(), "product_symbol" | "symbol") {
                *key = "symbol".to_string();
                *value = self.exchange_symbol(value, futures)?;
            }
        }
        Ok(())
    }
}
