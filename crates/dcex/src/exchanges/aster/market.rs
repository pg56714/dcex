use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::{AsterClient, AsterMarket};
use super::endpoints::*;
use super::params::{
    push_optional_display, AsterAggTradesParams, AsterExchangeInfoParams, AsterFundingRateParams,
    AsterHistoricalTradesParams, AsterIndexPriceKlinesParams, AsterKlinesParams, AsterLimitParams,
    AsterOptionalSymbolParams, AsterParams,
};

impl AsterClient {
    pub async fn ping_spot(&self) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            AsterMarket::Spot,
            SPOT_PING,
            Vec::new(),
            false,
        )
        .await
    }

    pub async fn ping_futures(&self) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            AsterMarket::Futures,
            FUTURES_PING,
            Vec::new(),
            false,
        )
        .await
    }

    pub async fn get_spot_server_time(&self) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            AsterMarket::Spot,
            SPOT_SERVER_TIME,
            Vec::new(),
            false,
        )
        .await
    }

    pub async fn get_futures_server_time(&self) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            AsterMarket::Futures,
            FUTURES_SERVER_TIME,
            Vec::new(),
            false,
        )
        .await
    }

    pub async fn get_spot_exchange_info(&self) -> Result<ValidatedResponse> {
        self.get_spot_exchange_info_with(AsterExchangeInfoParams::default())
            .await
    }

    pub async fn get_spot_exchange_info_with(
        &self,
        request: AsterExchangeInfoParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = request.product_symbol {
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        }
        if let Some(symbols) = request.symbols {
            params.push((
                "symbols".to_string(),
                serde_json::to_string(&symbols)
                    .map_err(|error| DcexError::Decode(error.to_string()))?,
            ));
        }
        self.request(
            HttpMethod::Get,
            AsterMarket::Spot,
            SPOT_EXCHANGE_INFO,
            params,
            false,
        )
        .await
    }

    pub async fn get_futures_exchange_info(&self) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            AsterMarket::Futures,
            FUTURES_EXCHANGE_INFO,
            Vec::new(),
            false,
        )
        .await
    }

    pub async fn get_spot_orderbook(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.get_spot_orderbook_with(product_symbol, AsterLimitParams::default())
            .await
    }

    pub async fn get_spot_orderbook_with(
        &self,
        product_symbol: &str,
        request: AsterLimitParams,
    ) -> Result<ValidatedResponse> {
        self.symbol_request(AsterMarket::Spot, SPOT_DEPTH, product_symbol, request)
            .await
    }

    pub async fn get_futures_orderbook(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.get_futures_orderbook_with(product_symbol, AsterLimitParams::default())
            .await
    }

    pub async fn get_futures_orderbook_with(
        &self,
        product_symbol: &str,
        request: AsterLimitParams,
    ) -> Result<ValidatedResponse> {
        self.symbol_request(AsterMarket::Futures, FUTURES_DEPTH, product_symbol, request)
            .await
    }

    pub async fn get_spot_recent_trades(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.get_spot_recent_trades_with(product_symbol, AsterLimitParams::default())
            .await
    }

    pub async fn get_spot_recent_trades_with(
        &self,
        product_symbol: &str,
        request: AsterLimitParams,
    ) -> Result<ValidatedResponse> {
        self.symbol_request(AsterMarket::Spot, SPOT_TRADES, product_symbol, request)
            .await
    }

    pub async fn get_futures_recent_trades(
        &self,
        product_symbol: &str,
    ) -> Result<ValidatedResponse> {
        self.get_futures_recent_trades_with(product_symbol, AsterLimitParams::default())
            .await
    }

    pub async fn get_futures_recent_trades_with(
        &self,
        product_symbol: &str,
        request: AsterLimitParams,
    ) -> Result<ValidatedResponse> {
        self.symbol_request(
            AsterMarket::Futures,
            FUTURES_TRADES,
            product_symbol,
            request,
        )
        .await
    }

    pub async fn get_spot_historical_trades(
        &self,
        product_symbol: &str,
    ) -> Result<ValidatedResponse> {
        self.get_spot_historical_trades_with(product_symbol, AsterHistoricalTradesParams::default())
            .await
    }

    pub async fn get_spot_historical_trades_with(
        &self,
        product_symbol: &str,
        request: AsterHistoricalTradesParams,
    ) -> Result<ValidatedResponse> {
        self.historical_trades_request(
            AsterMarket::Spot,
            SPOT_HISTORICAL_TRADES,
            product_symbol,
            request,
        )
        .await
    }

    pub async fn get_futures_historical_trades(
        &self,
        product_symbol: &str,
    ) -> Result<ValidatedResponse> {
        self.get_futures_historical_trades_with(
            product_symbol,
            AsterHistoricalTradesParams::default(),
        )
        .await
    }

    pub async fn get_futures_historical_trades_with(
        &self,
        product_symbol: &str,
        request: AsterHistoricalTradesParams,
    ) -> Result<ValidatedResponse> {
        self.historical_trades_request(
            AsterMarket::Futures,
            FUTURES_HISTORICAL_TRADES,
            product_symbol,
            request,
        )
        .await
    }

    pub async fn get_spot_agg_trades(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.get_spot_agg_trades_with(product_symbol, AsterAggTradesParams::default())
            .await
    }

    pub async fn get_spot_agg_trades_with(
        &self,
        product_symbol: &str,
        request: AsterAggTradesParams,
    ) -> Result<ValidatedResponse> {
        self.agg_trades_request(AsterMarket::Spot, SPOT_AGG_TRADES, product_symbol, request)
            .await
    }

    pub async fn get_futures_agg_trades(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.get_futures_agg_trades_with(product_symbol, AsterAggTradesParams::default())
            .await
    }

    pub async fn get_futures_agg_trades_with(
        &self,
        product_symbol: &str,
        request: AsterAggTradesParams,
    ) -> Result<ValidatedResponse> {
        self.agg_trades_request(
            AsterMarket::Futures,
            FUTURES_AGG_TRADES,
            product_symbol,
            request,
        )
        .await
    }

    pub async fn get_spot_klines(
        &self,
        product_symbol: &str,
        interval: &str,
    ) -> Result<ValidatedResponse> {
        self.get_spot_klines_with(product_symbol, interval, AsterKlinesParams::default())
            .await
    }

    pub async fn get_spot_klines_with(
        &self,
        product_symbol: &str,
        interval: &str,
        request: AsterKlinesParams,
    ) -> Result<ValidatedResponse> {
        self.klines_request(
            AsterMarket::Spot,
            SPOT_KLINES,
            product_symbol,
            interval,
            request,
        )
        .await
    }

    pub async fn get_futures_klines(
        &self,
        product_symbol: &str,
        interval: &str,
    ) -> Result<ValidatedResponse> {
        self.get_futures_klines_with(product_symbol, interval, AsterKlinesParams::default())
            .await
    }

    pub async fn get_futures_klines_with(
        &self,
        product_symbol: &str,
        interval: &str,
        request: AsterKlinesParams,
    ) -> Result<ValidatedResponse> {
        self.klines_request(
            AsterMarket::Futures,
            FUTURES_KLINES,
            product_symbol,
            interval,
            request,
        )
        .await
    }

    pub async fn get_futures_index_price_klines(
        &self,
        pair: &str,
        interval: &str,
    ) -> Result<ValidatedResponse> {
        self.get_futures_index_price_klines_with(
            pair,
            interval,
            AsterIndexPriceKlinesParams::default(),
        )
        .await
    }

    pub async fn get_futures_index_price_klines_with(
        &self,
        pair: &str,
        interval: &str,
        request: AsterIndexPriceKlinesParams,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![
            ("pair".to_string(), pair.to_string()),
            ("interval".to_string(), interval.to_string()),
        ];
        push_optional_display(&mut params, "startTime", request.start_time);
        push_optional_display(&mut params, "endTime", request.end_time);
        push_optional_display(&mut params, "limit", request.limit);
        self.request(
            HttpMethod::Get,
            AsterMarket::Futures,
            FUTURES_INDEX_PRICE_KLINES,
            params,
            false,
        )
        .await
    }

    pub async fn get_futures_mark_price_klines(
        &self,
        product_symbol: &str,
        interval: &str,
    ) -> Result<ValidatedResponse> {
        self.get_futures_mark_price_klines_with(
            product_symbol,
            interval,
            AsterKlinesParams::default(),
        )
        .await
    }

    pub async fn get_futures_mark_price_klines_with(
        &self,
        product_symbol: &str,
        interval: &str,
        request: AsterKlinesParams,
    ) -> Result<ValidatedResponse> {
        self.klines_request(
            AsterMarket::Futures,
            FUTURES_MARK_PRICE_KLINES,
            product_symbol,
            interval,
            request,
        )
        .await
    }

    pub async fn get_spot_ticker_24hr(&self) -> Result<ValidatedResponse> {
        self.get_spot_ticker_24hr_with(AsterOptionalSymbolParams::default())
            .await
    }

    pub async fn get_spot_ticker_24hr_with(
        &self,
        request: AsterOptionalSymbolParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Spot, SPOT_TICKER_24HR, request)
            .await
    }

    pub async fn get_futures_ticker_24hr(&self) -> Result<ValidatedResponse> {
        self.get_futures_ticker_24hr_with(AsterOptionalSymbolParams::default())
            .await
    }

    pub async fn get_futures_ticker_24hr_with(
        &self,
        request: AsterOptionalSymbolParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Futures, FUTURES_TICKER_24HR, request)
            .await
    }

    pub async fn get_spot_ticker_price(&self) -> Result<ValidatedResponse> {
        self.get_spot_ticker_price_with(AsterOptionalSymbolParams::default())
            .await
    }

    pub async fn get_spot_ticker_price_with(
        &self,
        request: AsterOptionalSymbolParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Spot, SPOT_TICKER_PRICE, request)
            .await
    }

    pub async fn get_futures_ticker_price(&self) -> Result<ValidatedResponse> {
        self.get_futures_ticker_price_with(AsterOptionalSymbolParams::default())
            .await
    }

    pub async fn get_futures_ticker_price_with(
        &self,
        request: AsterOptionalSymbolParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Futures, FUTURES_TICKER_PRICE, request)
            .await
    }

    pub async fn get_spot_book_ticker(&self) -> Result<ValidatedResponse> {
        self.get_spot_book_ticker_with(AsterOptionalSymbolParams::default())
            .await
    }

    pub async fn get_spot_book_ticker_with(
        &self,
        request: AsterOptionalSymbolParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Spot, SPOT_BOOK_TICKER, request)
            .await
    }

    pub async fn get_futures_book_ticker(&self) -> Result<ValidatedResponse> {
        self.get_futures_book_ticker_with(AsterOptionalSymbolParams::default())
            .await
    }

    pub async fn get_futures_book_ticker_with(
        &self,
        request: AsterOptionalSymbolParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Futures, FUTURES_BOOK_TICKER, request)
            .await
    }

    pub async fn get_spot_withdraw_fee(
        &self,
        chain_id: &str,
        asset: &str,
    ) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            AsterMarket::Spot,
            SPOT_WITHDRAW_FEE,
            vec![
                ("chainId".to_string(), chain_id.to_string()),
                ("asset".to_string(), asset.to_string()),
            ],
            false,
        )
        .await
    }

    pub async fn get_futures_premium_index(&self) -> Result<ValidatedResponse> {
        self.get_futures_premium_index_with(AsterOptionalSymbolParams::default())
            .await
    }

    pub async fn get_futures_premium_index_with(
        &self,
        request: AsterOptionalSymbolParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Futures, FUTURES_PREMIUM_INDEX, request)
            .await
    }

    pub async fn get_futures_funding_rate(&self) -> Result<ValidatedResponse> {
        self.get_futures_funding_rate_with(AsterFundingRateParams::default())
            .await
    }

    pub async fn get_futures_funding_rate_with(
        &self,
        request: AsterFundingRateParams<'_>,
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
            AsterMarket::Futures,
            FUTURES_FUNDING_RATE,
            params,
            false,
        )
        .await
    }

    pub async fn get_futures_funding_info(&self) -> Result<ValidatedResponse> {
        self.get_futures_funding_info_with(AsterOptionalSymbolParams::default())
            .await
    }

    pub async fn get_futures_funding_info_with(
        &self,
        request: AsterOptionalSymbolParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Futures, FUTURES_FUNDING_INFO, request)
            .await
    }

    pub async fn get_futures_index_references(
        &self,
        product_symbol: &str,
    ) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            AsterMarket::Futures,
            FUTURES_INDEX_REFERENCES,
            vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)],
            false,
        )
        .await
    }

    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = AsterParams::from_pairs(params);
        match method_name {
            "ping_spot" => self.ping_spot().await,
            "ping_futures" => self.ping_futures().await,
            "get_spot_server_time" => self.get_spot_server_time().await,
            "get_futures_server_time" => self.get_futures_server_time().await,
            "get_spot_exchange_info" => {
                self.get_spot_exchange_info_with(AsterExchangeInfoParams {
                    product_symbol: params.get("product_symbol"),
                    symbols: params.values("symbols"),
                })
                .await
            }
            "get_futures_exchange_info" => self.get_futures_exchange_info().await,
            "get_spot_orderbook" => {
                self.get_spot_orderbook_with(
                    params.required("product_symbol")?,
                    AsterLimitParams {
                        limit: params.u64("limit")?,
                    },
                )
                .await
            }
            "get_futures_orderbook" => {
                self.get_futures_orderbook_with(
                    params.required("product_symbol")?,
                    AsterLimitParams {
                        limit: params.u64("limit")?,
                    },
                )
                .await
            }
            "get_spot_recent_trades" => {
                self.get_spot_recent_trades_with(
                    params.required("product_symbol")?,
                    AsterLimitParams {
                        limit: params.u64("limit")?,
                    },
                )
                .await
            }
            "get_futures_recent_trades" => {
                self.get_futures_recent_trades_with(
                    params.required("product_symbol")?,
                    AsterLimitParams {
                        limit: params.u64("limit")?,
                    },
                )
                .await
            }
            "get_spot_historical_trades" => {
                self.get_spot_historical_trades_with(
                    params.required("product_symbol")?,
                    AsterHistoricalTradesParams {
                        limit: params.u64("limit")?,
                        from_id: params.u64("fromId")?,
                    },
                )
                .await
            }
            "get_futures_historical_trades" => {
                self.get_futures_historical_trades_with(
                    params.required("product_symbol")?,
                    AsterHistoricalTradesParams {
                        limit: params.u64("limit")?,
                        from_id: params.u64("fromId")?,
                    },
                )
                .await
            }
            "get_spot_agg_trades" => {
                self.get_spot_agg_trades_with(
                    params.required("product_symbol")?,
                    AsterAggTradesParams {
                        from_id: params.u64("fromId")?,
                        start_time: params.u64("startTime")?,
                        end_time: params.u64("endTime")?,
                        limit: params.u64("limit")?,
                    },
                )
                .await
            }
            "get_futures_agg_trades" => {
                self.get_futures_agg_trades_with(
                    params.required("product_symbol")?,
                    AsterAggTradesParams {
                        from_id: params.u64("fromId")?,
                        start_time: params.u64("startTime")?,
                        end_time: params.u64("endTime")?,
                        limit: params.u64("limit")?,
                    },
                )
                .await
            }
            "get_spot_klines" => {
                self.get_spot_klines_with(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    AsterKlinesParams {
                        start_time: params.u64("startTime")?,
                        end_time: params.u64("endTime")?,
                        limit: params.u64("limit")?,
                    },
                )
                .await
            }
            "get_futures_klines" => {
                self.get_futures_klines_with(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    AsterKlinesParams {
                        start_time: params.u64("startTime")?,
                        end_time: params.u64("endTime")?,
                        limit: params.u64("limit")?,
                    },
                )
                .await
            }
            "get_futures_index_price_klines" => {
                self.get_futures_index_price_klines_with(
                    params.required("pair")?,
                    params.required("interval")?,
                    AsterIndexPriceKlinesParams {
                        start_time: params.u64("startTime")?,
                        end_time: params.u64("endTime")?,
                        limit: params.u64("limit")?,
                    },
                )
                .await
            }
            "get_futures_mark_price_klines" => {
                self.get_futures_mark_price_klines_with(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    AsterKlinesParams {
                        start_time: params.u64("startTime")?,
                        end_time: params.u64("endTime")?,
                        limit: params.u64("limit")?,
                    },
                )
                .await
            }
            "get_spot_ticker_24hr" => {
                self.get_spot_ticker_24hr_with(AsterOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
            }
            "get_futures_ticker_24hr" => {
                self.get_futures_ticker_24hr_with(AsterOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
            }
            "get_spot_ticker_price" => {
                self.get_spot_ticker_price_with(AsterOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
            }
            "get_futures_ticker_price" => {
                self.get_futures_ticker_price_with(AsterOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
            }
            "get_spot_book_ticker" => {
                self.get_spot_book_ticker_with(AsterOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
            }
            "get_futures_book_ticker" => {
                self.get_futures_book_ticker_with(AsterOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
            }
            "get_spot_withdraw_fee" => {
                self.get_spot_withdraw_fee(params.required("chainId")?, params.required("asset")?)
                    .await
            }
            "get_futures_premium_index" => {
                self.get_futures_premium_index_with(AsterOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
            }
            "get_futures_funding_rate" => {
                self.get_futures_funding_rate_with(AsterFundingRateParams {
                    product_symbol: params.get("product_symbol"),
                    start_time: params.u64("startTime")?,
                    end_time: params.u64("endTime")?,
                    limit: params.u64("limit")?,
                })
                .await
            }
            "get_futures_funding_info" => {
                self.get_futures_funding_info_with(AsterOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
            }
            "get_futures_index_references" => {
                self.get_futures_index_references(params.required("product_symbol")?)
                    .await
            }
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported Aster public method: {method_name}"
            ))),
        }
    }

    async fn optional_symbol_request(
        &self,
        market: AsterMarket,
        path: &str,
        request: AsterOptionalSymbolParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = request.product_symbol {
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        }
        self.request(HttpMethod::Get, market, path, params, false)
            .await
    }

    async fn symbol_request(
        &self,
        market: AsterMarket,
        path: &str,
        product_symbol: &str,
        request: AsterLimitParams,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        push_optional_display(&mut params, "limit", request.limit);
        self.request(HttpMethod::Get, market, path, params, false)
            .await
    }

    async fn historical_trades_request(
        &self,
        market: AsterMarket,
        path: &str,
        product_symbol: &str,
        request: AsterHistoricalTradesParams,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        push_optional_display(&mut params, "limit", request.limit);
        push_optional_display(&mut params, "fromId", request.from_id);
        self.request(HttpMethod::Get, market, path, params, false)
            .await
    }

    async fn agg_trades_request(
        &self,
        market: AsterMarket,
        path: &str,
        product_symbol: &str,
        request: AsterAggTradesParams,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        push_optional_display(&mut params, "fromId", request.from_id);
        push_optional_display(&mut params, "startTime", request.start_time);
        push_optional_display(&mut params, "endTime", request.end_time);
        push_optional_display(&mut params, "limit", request.limit);
        self.request(HttpMethod::Get, market, path, params, false)
            .await
    }

    async fn klines_request(
        &self,
        market: AsterMarket,
        path: &str,
        product_symbol: &str,
        interval: &str,
        request: AsterKlinesParams,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![
            ("symbol".to_string(), self.exchange_symbol(product_symbol)?),
            ("interval".to_string(), interval.to_string()),
        ];
        push_optional_display(&mut params, "startTime", request.start_time);
        push_optional_display(&mut params, "endTime", request.end_time);
        push_optional_display(&mut params, "limit", request.limit);
        self.request(HttpMethod::Get, market, path, params, false)
            .await
    }
}
