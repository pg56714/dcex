use super::client::{BinanceClient, BinanceMarket};
use super::endpoints::*;
use super::params::{
    push_optional, push_optional_display, BinanceFundingRateParams, BinanceFuturesBasisParams,
    BinanceFuturesPeriodParams, BinanceKlinesParams, BinanceLimitParams,
    BinanceOptionalSymbolParams, BinanceSymbolListParams, PublicParams,
};
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

impl BinanceClient {
    pub async fn get_server_time(&self, market_type: &str) -> Result<ValidatedResponse> {
        let (market, path) = if market_type == "spot" {
            (BinanceMarket::Spot, SPOT_SERVER_TIME)
        } else {
            (BinanceMarket::Futures, FUTURES_SERVER_TIME)
        };
        self.request(HttpMethod::Get, market, path, Vec::new(), false)
            .await
    }

    pub async fn get_spot_exchange_info(&self) -> Result<ValidatedResponse> {
        self.get_spot_exchange_info_with(BinanceSymbolListParams::default())
            .await
    }

    pub async fn get_spot_exchange_info_with(
        &self,
        request: BinanceSymbolListParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = request.product_symbol {
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        }
        if let Some(product_symbols) = request.product_symbols {
            let symbols = product_symbols
                .iter()
                .map(|symbol| self.exchange_symbol(symbol))
                .collect::<Result<Vec<_>>>()?;
            params.push((
                "symbols".to_string(),
                serde_json::to_string(&symbols)
                    .map_err(|error| DcexError::Decode(error.to_string()))?,
            ));
        }
        push_optional(&mut params, "symbolStatus", request.symbol_status);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Spot,
            SPOT_EXCHANGE_INFO,
            params,
            false,
        )
        .await
    }

    pub async fn get_spot_orderbook(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.get_spot_orderbook_with(product_symbol, BinanceLimitParams::default())
            .await
    }

    pub async fn get_spot_orderbook_with(
        &self,
        product_symbol: &str,
        request: BinanceLimitParams,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        push_optional_display(&mut params, "limit", request.limit);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Spot,
            SPOT_ORDERBOOK,
            params,
            false,
        )
        .await
    }

    pub async fn get_spot_trades(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.get_spot_trades_with(product_symbol, BinanceLimitParams::default())
            .await
    }

    pub async fn get_spot_trades_with(
        &self,
        product_symbol: &str,
        request: BinanceLimitParams,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        push_optional_display(&mut params, "limit", request.limit);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Spot,
            SPOT_TRADES,
            params,
            false,
        )
        .await
    }

    pub async fn get_spot_price(&self) -> Result<ValidatedResponse> {
        self.get_spot_price_with(BinanceSymbolListParams::default())
            .await
    }

    pub async fn get_spot_price_with(
        &self,
        request: BinanceSymbolListParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = request.product_symbol {
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        }
        if let Some(product_symbols) = request.product_symbols {
            let symbols = product_symbols
                .iter()
                .map(|symbol| self.exchange_symbol(symbol))
                .collect::<Result<Vec<_>>>()?;
            params.push((
                "symbols".to_string(),
                serde_json::to_string(&symbols)
                    .map_err(|error| DcexError::Decode(error.to_string()))?,
            ));
        }
        push_optional(&mut params, "symbolStatus", request.symbol_status);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Spot,
            SPOT_PRICE,
            params,
            false,
        )
        .await
    }

    pub async fn get_klines(
        &self,
        product_symbol: &str,
        interval: &str,
    ) -> Result<ValidatedResponse> {
        self.get_klines_with(product_symbol, interval, BinanceKlinesParams::default())
            .await
    }

    pub async fn get_klines_with(
        &self,
        product_symbol: &str,
        interval: &str,
        request: BinanceKlinesParams,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![
            ("symbol".to_string(), self.exchange_symbol(product_symbol)?),
            ("interval".to_string(), interval.to_string()),
        ];
        push_optional_display(&mut params, "startTime", request.start_time);
        push_optional_display(&mut params, "limit", request.limit);
        let market = self.market_for_product_symbol(product_symbol)?;
        let path = if market == BinanceMarket::Spot {
            SPOT_KLINES
        } else {
            FUTURES_KLINES
        };
        self.request(HttpMethod::Get, market, path, params, false)
            .await
    }

    pub async fn get_futures_exchange_info(&self) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_EXCHANGE_INFO,
            Vec::new(),
            false,
        )
        .await
    }

    pub async fn get_futures_ticker(&self) -> Result<ValidatedResponse> {
        self.get_futures_ticker_with(BinanceOptionalSymbolParams::default())
            .await
    }

    pub async fn get_futures_ticker_with(
        &self,
        request: BinanceOptionalSymbolParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = request.product_symbol {
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        }
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_BOOK_TICKER,
            params,
            false,
        )
        .await
    }

    pub async fn get_futures_premium_index(&self) -> Result<ValidatedResponse> {
        self.get_futures_premium_index_with(BinanceOptionalSymbolParams::default())
            .await
    }

    pub async fn get_futures_premium_index_with(
        &self,
        request: BinanceOptionalSymbolParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = request.product_symbol {
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        }
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_PREMIUM_INDEX,
            params,
            false,
        )
        .await
    }

    pub async fn get_futures_funding_rate(&self) -> Result<ValidatedResponse> {
        self.get_futures_funding_rate_with(BinanceFundingRateParams::default())
            .await
    }

    pub async fn get_futures_funding_rate_with(
        &self,
        request: BinanceFundingRateParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = request.product_symbol {
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        }
        push_optional_display(&mut params, "startTime", request.start_time);
        push_optional_display(&mut params, "endTime", request.end_time);
        push_optional_display(&mut params, "limit", request.limit);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_FUNDING_RATE_HISTORY,
            params,
            false,
        )
        .await
    }

    pub async fn get_futures_open_interest(
        &self,
        product_symbol: &str,
    ) -> Result<ValidatedResponse> {
        self.futures_symbol_request(FUTURES_OPEN_INTEREST, product_symbol, Vec::new())
            .await
    }

    pub async fn get_futures_open_interest_history(
        &self,
        product_symbol: &str,
        period: &str,
    ) -> Result<ValidatedResponse> {
        self.get_futures_open_interest_history_with(
            product_symbol,
            period,
            BinanceFuturesPeriodParams::default(),
        )
        .await
    }

    pub async fn get_futures_open_interest_history_with(
        &self,
        product_symbol: &str,
        period: &str,
        request: BinanceFuturesPeriodParams,
    ) -> Result<ValidatedResponse> {
        self.futures_period_request(
            FUTURES_OPEN_INTEREST_HISTORY,
            product_symbol,
            period,
            request,
        )
        .await
    }

    pub async fn get_futures_global_long_short_account_ratio(
        &self,
        product_symbol: &str,
        period: &str,
    ) -> Result<ValidatedResponse> {
        self.get_futures_global_long_short_account_ratio_with(
            product_symbol,
            period,
            BinanceFuturesPeriodParams::default(),
        )
        .await
    }

    pub async fn get_futures_global_long_short_account_ratio_with(
        &self,
        product_symbol: &str,
        period: &str,
        request: BinanceFuturesPeriodParams,
    ) -> Result<ValidatedResponse> {
        self.futures_period_request(
            FUTURES_GLOBAL_LONG_SHORT_ACCOUNT_RATIO,
            product_symbol,
            period,
            request,
        )
        .await
    }

    pub async fn get_futures_top_long_short_account_ratio(
        &self,
        product_symbol: &str,
        period: &str,
    ) -> Result<ValidatedResponse> {
        self.get_futures_top_long_short_account_ratio_with(
            product_symbol,
            period,
            BinanceFuturesPeriodParams::default(),
        )
        .await
    }

    pub async fn get_futures_top_long_short_account_ratio_with(
        &self,
        product_symbol: &str,
        period: &str,
        request: BinanceFuturesPeriodParams,
    ) -> Result<ValidatedResponse> {
        self.futures_period_request(
            FUTURES_TOP_LONG_SHORT_ACCOUNT_RATIO,
            product_symbol,
            period,
            request,
        )
        .await
    }

    pub async fn get_futures_top_long_short_position_ratio(
        &self,
        product_symbol: &str,
        period: &str,
    ) -> Result<ValidatedResponse> {
        self.get_futures_top_long_short_position_ratio_with(
            product_symbol,
            period,
            BinanceFuturesPeriodParams::default(),
        )
        .await
    }

    pub async fn get_futures_top_long_short_position_ratio_with(
        &self,
        product_symbol: &str,
        period: &str,
        request: BinanceFuturesPeriodParams,
    ) -> Result<ValidatedResponse> {
        self.futures_period_request(
            FUTURES_TOP_LONG_SHORT_POSITION_RATIO,
            product_symbol,
            period,
            request,
        )
        .await
    }

    pub async fn get_futures_taker_buy_sell_volume(
        &self,
        product_symbol: &str,
        period: &str,
    ) -> Result<ValidatedResponse> {
        self.get_futures_taker_buy_sell_volume_with(
            product_symbol,
            period,
            BinanceFuturesPeriodParams::default(),
        )
        .await
    }

    pub async fn get_futures_taker_buy_sell_volume_with(
        &self,
        product_symbol: &str,
        period: &str,
        request: BinanceFuturesPeriodParams,
    ) -> Result<ValidatedResponse> {
        self.futures_period_request(
            FUTURES_TAKER_LONG_SHORT_RATIO,
            product_symbol,
            period,
            request,
        )
        .await
    }

    pub async fn get_futures_basis(
        &self,
        product_symbol: &str,
        contract_type: &str,
        period: &str,
    ) -> Result<ValidatedResponse> {
        self.get_futures_basis_with(
            product_symbol,
            contract_type,
            period,
            BinanceFuturesBasisParams::default(),
        )
        .await
    }

    pub async fn get_futures_basis_with(
        &self,
        product_symbol: &str,
        contract_type: &str,
        period: &str,
        request: BinanceFuturesBasisParams,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![
            ("pair".to_string(), self.exchange_symbol(product_symbol)?),
            ("contractType".to_string(), contract_type.to_string()),
            ("period".to_string(), period.to_string()),
        ];
        push_optional_display(&mut params, "limit", request.limit);
        push_optional_display(&mut params, "startTime", request.start_time);
        push_optional_display(&mut params, "endTime", request.end_time);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_BASIS,
            params,
            false,
        )
        .await
    }

    pub(super) async fn futures_symbol_request(
        &self,
        path: &str,
        product_symbol: &str,
        mut params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        params.insert(
            0,
            ("symbol".to_string(), self.exchange_symbol(product_symbol)?),
        );
        self.request(HttpMethod::Get, BinanceMarket::Futures, path, params, false)
            .await
    }

    pub(super) async fn futures_period_request(
        &self,
        path: &str,
        product_symbol: &str,
        period: &str,
        request: BinanceFuturesPeriodParams,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("period".to_string(), period.to_string())];
        push_optional_display(&mut params, "limit", request.limit);
        push_optional_display(&mut params, "startTime", request.start_time);
        push_optional_display(&mut params, "endTime", request.end_time);
        self.futures_symbol_request(path, product_symbol, params)
            .await
    }

    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = PublicParams(params);
        match method_name {
            "get_server_time" => {
                self.get_server_time(params.get("market_type").unwrap_or("spot"))
                    .await
            }
            "get_spot_exchange_info" => {
                self.get_spot_exchange_info_with(BinanceSymbolListParams {
                    product_symbol: params.get("product_symbol"),
                    product_symbols: params.values("product_symbols"),
                    symbol_status: params.get("symbolStatus"),
                })
                .await
            }
            "get_spot_orderbook" => {
                self.get_spot_orderbook_with(
                    params.required("product_symbol")?,
                    BinanceLimitParams {
                        limit: params.u64("limit")?,
                    },
                )
                .await
            }
            "get_spot_trades" => {
                self.get_spot_trades_with(
                    params.required("product_symbol")?,
                    BinanceLimitParams {
                        limit: params.u64("limit")?,
                    },
                )
                .await
            }
            "get_spot_price" => {
                self.get_spot_price_with(BinanceSymbolListParams {
                    product_symbol: params.get("product_symbol"),
                    product_symbols: params.values("product_symbols"),
                    symbol_status: params.get("symbolStatus"),
                })
                .await
            }
            "get_klines" => {
                self.get_klines_with(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    BinanceKlinesParams {
                        start_time: params.u64("start_time")?,
                        limit: params.u64("limit")?,
                    },
                )
                .await
            }
            "get_futures_exchange_info" => self.get_futures_exchange_info().await,
            "get_futures_ticker" => {
                self.get_futures_ticker_with(BinanceOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
            }
            "get_futures_premium_index" => {
                self.get_futures_premium_index_with(BinanceOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
            }
            "get_futures_funding_rate" => {
                self.get_futures_funding_rate_with(BinanceFundingRateParams {
                    product_symbol: params.get("product_symbol"),
                    start_time: params.u64("startTime")?,
                    end_time: params.u64("endTime")?,
                    limit: params.u64("limit")?,
                })
                .await
            }
            "get_futures_open_interest" => {
                self.get_futures_open_interest(params.required("product_symbol")?)
                    .await
            }
            "get_futures_open_interest_history" => {
                self.get_futures_open_interest_history_with(
                    params.required("product_symbol")?,
                    params.get("period").unwrap_or("5m"),
                    BinanceFuturesPeriodParams {
                        limit: params.u64("limit")?,
                        start_time: params.u64("startTime")?,
                        end_time: params.u64("endTime")?,
                    },
                )
                .await
            }
            "get_futures_global_long_short_account_ratio" => {
                self.get_futures_global_long_short_account_ratio_with(
                    params.required("product_symbol")?,
                    params.get("period").unwrap_or("5m"),
                    BinanceFuturesPeriodParams {
                        limit: params.u64("limit")?,
                        start_time: params.u64("startTime")?,
                        end_time: params.u64("endTime")?,
                    },
                )
                .await
            }
            "get_futures_top_long_short_account_ratio" => {
                self.get_futures_top_long_short_account_ratio_with(
                    params.required("product_symbol")?,
                    params.get("period").unwrap_or("5m"),
                    BinanceFuturesPeriodParams {
                        limit: params.u64("limit")?,
                        start_time: params.u64("startTime")?,
                        end_time: params.u64("endTime")?,
                    },
                )
                .await
            }
            "get_futures_top_long_short_position_ratio" => {
                self.get_futures_top_long_short_position_ratio_with(
                    params.required("product_symbol")?,
                    params.get("period").unwrap_or("5m"),
                    BinanceFuturesPeriodParams {
                        limit: params.u64("limit")?,
                        start_time: params.u64("startTime")?,
                        end_time: params.u64("endTime")?,
                    },
                )
                .await
            }
            "get_futures_taker_buy_sell_volume" => {
                self.get_futures_taker_buy_sell_volume_with(
                    params.required("product_symbol")?,
                    params.get("period").unwrap_or("5m"),
                    BinanceFuturesPeriodParams {
                        limit: params.u64("limit")?,
                        start_time: params.u64("startTime")?,
                        end_time: params.u64("endTime")?,
                    },
                )
                .await
            }
            "get_futures_basis" => {
                self.get_futures_basis_with(
                    params.required("product_symbol")?,
                    params.get("contractType").unwrap_or("PERPETUAL"),
                    params.get("period").unwrap_or("5m"),
                    BinanceFuturesBasisParams {
                        limit: params.u64("limit")?,
                        start_time: params.u64("startTime")?,
                        end_time: params.u64("endTime")?,
                    },
                )
                .await
            }
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported Binance public method: {method_name}"
            ))),
        }
    }
}
