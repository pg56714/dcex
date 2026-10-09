use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::BitgetClient;
use super::endpoints::*;
use super::params::BitgetParams;

/// UTA candle intervals the exchange accepts (official list plus 2H/3D/1W/1M, verified live).
const UTA_KLINE_INTERVALS: &[&str] = &[
    "1m", "3m", "5m", "15m", "30m", "1H", "2H", "4H", "6H", "12H", "1D", "3D", "1W", "1M",
];

impl BitgetClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        crate::exchanges::input_contracts::pairs("bitget", method_name, &params)?;
        let params = BitgetParams::from_pairs(params);
        if let Some(response) = self.catalog_request(method_name, &params, true).await? {
            return Ok(response);
        }
        if let Some(response) = self.table_request(method_name, &params, true).await? {
            return Ok(response);
        }
        if let Some(result) = self
            .trading_controls_request(method_name, &params, true)
            .await?
        {
            return Ok(result);
        }
        match method_name {
            "get_spot_coins" => {
                params.ensure_allowed(&["coin"], false)?;
                self.public_get(SPOT_COINS, params.only(&["coin"])).await
            }

            "get_spot_market_trades" => {
                params.ensure_allowed(
                    &[
                        "product_symbol",
                        "limit",
                        "idLessThan",
                        "startTime",
                        "endTime",
                        "productType",
                        "marginCoin",
                        "marginMode",
                        "granularity",
                        "interval",
                    ],
                    false,
                )?;
                let symbol = self
                    .exchange_symbol_category(params.required("product_symbol")?, Some("spot"))?;
                let mut query = params.only(&["limit", "idLessThan", "startTime", "endTime"]);
                query.push(("symbol".into(), symbol));
                self.public_get(SPOT_MARKET_TRADES, query).await
            }

            "get_uta_instruments" => {
                params.ensure_allowed(&["category", "product_symbol", "symbol"], false)?;
                params.required("category")?;
                self.public_get(
                    UTA_INSTRUMENTS,
                    self.normalize_symbol_params(params.only(&[
                        "product_symbol",
                        "symbol",
                        "category",
                    ]))?,
                )
                .await
            }
            "get_uta_tickers" => {
                params.ensure_allowed(&["category", "product_symbol", "symbol"], false)?;
                params.required("category")?;
                self.public_get(
                    UTA_TICKERS,
                    self.normalize_symbol_params(params.only(&[
                        "product_symbol",
                        "symbol",
                        "category",
                    ]))?,
                )
                .await
            }
            "get_uta_orderbook" => {
                params.ensure_allowed(&["product_symbol", "category", "limit"], false)?;
                require_all(&params, &["category", "product_symbol"])?;
                self.public_get(
                    UTA_ORDERBOOK,
                    self.normalize_symbol_params(params.only(&[
                        "product_symbol",
                        "category",
                        "limit",
                    ]))?,
                )
                .await
            }
            "get_uta_public_fills" => {
                params.ensure_allowed(&["product_symbol", "category", "limit"], false)?;
                require_all(&params, &["category", "product_symbol"])?;
                self.public_get(
                    UTA_PUBLIC_FILLS,
                    self.normalize_symbol_params(params.only(&[
                        "product_symbol",
                        "category",
                        "limit",
                    ]))?,
                )
                .await
            }
            "get_uta_kline" | "get_uta_history_kline" => {
                require_all(&params, &["category", "product_symbol", "interval"])?;
                // Case-sensitive: "1h"/"1d" are rejected by the exchange (verified live).
                let interval = params.required("interval")?;
                if !UTA_KLINE_INTERVALS.contains(&interval) {
                    return Err(DcexError::InvalidInput(format!(
                        "invalid Bitget UTA interval: {interval}; expected one of {}",
                        UTA_KLINE_INTERVALS.join(", ")
                    )));
                }
                let endpoint = if method_name == "get_uta_kline" {
                    UTA_CANDLES
                } else {
                    UTA_HISTORY_CANDLES
                };
                self.public_get(
                    endpoint,
                    self.normalize_symbol_params(params.only(&[
                        "product_symbol",
                        "category",
                        "interval",
                        "startTime",
                        "endTime",
                        "type",
                        "limit",
                    ]))?,
                )
                .await
            }
            "get_uta_liquidations" => {
                params.ensure_allowed(&["category", "product_symbol", "limit", "cursor"], false)?;
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
            "get_reality_stock_info" => {
                params.ensure_allowed(&["product_symbol", "symbol"], false)?;
                self.public_get(
                    REALITY_STOCK_INFO,
                    self.normalize_symbol_params(params.only(&["product_symbol", "symbol"]))?,
                )
                .await
            }
            "get_reality_market_states" => {
                params.ensure_allowed(&[], false)?;
                self.public_get(REALITY_MARKET_STATES, Vec::new()).await
            }
            "get_reality_market_calendar" => {
                params.ensure_allowed(&[], false)?;
                self.public_get(REALITY_MARKET_CALENDAR, Vec::new()).await
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
