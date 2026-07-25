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
            "get_spot_coins" => self.public_get(SPOT_COINS, params.only(&["coin"])).await,
            "get_spot_symbols" => {
                self.public_get(
                    SPOT_SYMBOLS,
                    self.normalize_symbol_params(params.only(&["product_symbol"]))?,
                )
                .await
            }
            "get_spot_tickers" => {
                self.public_get(
                    SPOT_TICKERS,
                    self.normalize_symbol_params(params.only(&["product_symbol"]))?,
                )
                .await
            }
            "get_spot_orderbook" => {
                params.required("product_symbol")?;
                self.public_get(
                    SPOT_ORDERBOOK,
                    self.normalize_symbol_params(params.only(&[
                        "product_symbol",
                        "type",
                        "limit",
                    ]))?,
                )
                .await
            }
            "get_spot_kline" => {
                require_all(&params, &["product_symbol", "granularity"])?;
                self.public_get(
                    SPOT_CANDLES,
                    self.normalize_symbol_params(params.only(&[
                        "product_symbol",
                        "granularity",
                        "startTime",
                        "endTime",
                        "limit",
                    ]))?,
                )
                .await
            }
            "get_spot_history_kline" => {
                require_all(&params, &["product_symbol", "granularity", "endTime"])?;
                self.public_get(
                    SPOT_HISTORY_CANDLES,
                    self.normalize_symbol_params(params.only(&[
                        "product_symbol",
                        "granularity",
                        "endTime",
                        "limit",
                    ]))?,
                )
                .await
            }
            "get_spot_recent_trades" => {
                params.required("product_symbol")?;
                self.public_get(
                    SPOT_RECENT_TRADES,
                    self.normalize_symbol_params(params.only(&["product_symbol", "limit"]))?,
                )
                .await
            }
            "get_spot_market_trades" => {
                params.required("product_symbol")?;
                self.public_get(
                    SPOT_MARKET_TRADES,
                    self.normalize_symbol_params(params.only(&[
                        "product_symbol",
                        "limit",
                        "idLessThan",
                        "startTime",
                        "endTime",
                    ]))?,
                )
                .await
            }
            "get_futures_contracts" => {
                params.required("productType")?;
                self.public_get(
                    FUTURES_CONTRACTS,
                    self.normalize_symbol_params(params.only(&["product_symbol", "productType"]))?,
                )
                .await
            }
            "get_futures_ticker" => {
                require_all(&params, &["product_symbol", "productType"])?;
                self.public_get(
                    FUTURES_TICKER,
                    self.normalize_symbol_params(params.only(&["product_symbol", "productType"]))?,
                )
                .await
            }
            "get_futures_tickers" => {
                params.required("productType")?;
                self.public_get(FUTURES_TICKERS, params.only(&["productType"]))
                    .await
            }
            "get_futures_orderbook" => {
                require_all(&params, &["product_symbol", "productType"])?;
                self.public_get(
                    FUTURES_ORDERBOOK,
                    self.normalize_symbol_params(params.only(&[
                        "product_symbol",
                        "productType",
                        "precision",
                        "limit",
                    ]))?,
                )
                .await
            }
            "get_futures_kline" => {
                require_all(&params, &["product_symbol", "productType", "granularity"])?;
                self.public_get(
                    FUTURES_CANDLES,
                    self.normalize_symbol_params(params.only(&[
                        "product_symbol",
                        "productType",
                        "granularity",
                        "startTime",
                        "endTime",
                        "kLineType",
                        "limit",
                    ]))?,
                )
                .await
            }
            "get_futures_history_kline" => {
                require_all(&params, &["product_symbol", "productType", "granularity"])?;
                self.public_get(
                    FUTURES_HISTORY_CANDLES,
                    self.normalize_symbol_params(params.only(&[
                        "product_symbol",
                        "productType",
                        "granularity",
                        "startTime",
                        "endTime",
                        "limit",
                    ]))?,
                )
                .await
            }
            "get_futures_recent_trades" => {
                require_all(&params, &["product_symbol", "productType"])?;
                self.public_get(
                    FUTURES_RECENT_TRADES,
                    self.normalize_symbol_params(params.only(&[
                        "product_symbol",
                        "productType",
                        "limit",
                    ]))?,
                )
                .await
            }
            "get_futures_current_funding_rate" => {
                params.required("productType")?;
                self.public_get(
                    FUTURES_CURRENT_FUNDING_RATE,
                    self.normalize_symbol_params(params.only(&["product_symbol", "productType"]))?,
                )
                .await
            }
            "get_futures_history_funding_rate" => {
                require_all(&params, &["product_symbol", "productType"])?;
                self.public_get(
                    FUTURES_HISTORY_FUNDING_RATE,
                    self.normalize_symbol_params(params.only(&[
                        "product_symbol",
                        "productType",
                        "pageSize",
                        "pageNo",
                    ]))?,
                )
                .await
            }
            "get_futures_open_interest" => {
                require_all(&params, &["product_symbol", "productType"])?;
                self.public_get(
                    FUTURES_OPEN_INTEREST,
                    self.normalize_symbol_params(params.only(&["product_symbol", "productType"]))?,
                )
                .await
            }
            "get_uta_liquidations" => {
                params.required("category")?;
                self.public_get(
                    UTA_LIQUIDATIONS,
                    self.normalize_symbol_params(params.only(&[
                        "product_symbol",
                        "category",
                        "limit",
                        "cursor",
                    ]))?,
                )
                .await
            }
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported Bitget public method: {method_name}"
            ))),
        }
    }
}

fn require_all(params: &BitgetParams, keys: &[&str]) -> Result<()> {
    for key in keys {
        params.required(key)?;
    }
    Ok(())
}
