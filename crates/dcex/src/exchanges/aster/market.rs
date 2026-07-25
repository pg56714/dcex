use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::{AsterClient, AsterMarket};
use super::endpoints::*;
use super::params::{
    push_optional_display, AsterAggTradesParams, AsterFundingRateParams,
    AsterHistoricalTradesParams, AsterIndexPriceKlinesParams, AsterKlinesParams, AsterLimitParams,
    AsterOptionalSymbolParams, AsterParams,
};

const KLINE_INTERVALS: &[&str] = &[
    "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M",
];

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
        self.request(
            HttpMethod::Get,
            AsterMarket::Spot,
            SPOT_EXCHANGE_INFO,
            Vec::new(),
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

    pub fn get_spot_orderbook(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_spot_orderbook",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub(super) async fn send_get_spot_orderbook(
        &self,
        product_symbol: &str,
        request: AsterLimitParams,
    ) -> Result<ValidatedResponse> {
        self.symbol_request(AsterMarket::Spot, SPOT_DEPTH, product_symbol, request)
            .await
    }

    pub fn get_futures_orderbook(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_futures_orderbook",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub(super) async fn send_get_futures_orderbook(
        &self,
        product_symbol: &str,
        request: AsterLimitParams,
    ) -> Result<ValidatedResponse> {
        self.symbol_request(AsterMarket::Futures, FUTURES_DEPTH, product_symbol, request)
            .await
    }

    pub fn get_spot_recent_trades(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_spot_recent_trades",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub(super) async fn send_get_spot_recent_trades(
        &self,
        product_symbol: &str,
        request: AsterLimitParams,
    ) -> Result<ValidatedResponse> {
        self.symbol_request(AsterMarket::Spot, SPOT_TRADES, product_symbol, request)
            .await
    }

    pub fn get_futures_recent_trades(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_futures_recent_trades",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub(super) async fn send_get_futures_recent_trades(
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

    pub fn get_spot_historical_trades(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_spot_historical_trades",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub(super) async fn send_get_spot_historical_trades(
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

    pub fn get_futures_historical_trades(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_futures_historical_trades",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub(super) async fn send_get_futures_historical_trades(
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

    pub fn get_spot_agg_trades(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_spot_agg_trades",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub(super) async fn send_get_spot_agg_trades(
        &self,
        product_symbol: &str,
        request: AsterAggTradesParams,
    ) -> Result<ValidatedResponse> {
        self.agg_trades_request(AsterMarket::Spot, SPOT_AGG_TRADES, product_symbol, request)
            .await
    }

    pub fn get_futures_agg_trades(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_futures_agg_trades",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub(super) async fn send_get_futures_agg_trades(
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

    pub fn get_spot_klines(
        &self,
        product_symbol: &str,
        interval: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_spot_klines",
            vec![
                ("product_symbol".to_string(), product_symbol.to_string()),
                ("interval".to_string(), interval.to_string()),
            ],
        )
    }

    pub(super) async fn send_get_spot_klines(
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

    pub fn get_futures_klines(
        &self,
        product_symbol: &str,
        interval: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_futures_klines",
            vec![
                ("product_symbol".to_string(), product_symbol.to_string()),
                ("interval".to_string(), interval.to_string()),
            ],
        )
    }

    pub(super) async fn send_get_futures_klines(
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

    pub fn get_futures_index_price_klines(
        &self,
        pair: &str,
        interval: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_futures_index_price_klines",
            vec![
                ("pair".to_string(), pair.to_string()),
                ("interval".to_string(), interval.to_string()),
            ],
        )
    }

    pub(super) async fn send_get_futures_index_price_klines(
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

    pub fn get_futures_mark_price_klines(
        &self,
        product_symbol: &str,
        interval: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_futures_mark_price_klines",
            vec![
                ("product_symbol".to_string(), product_symbol.to_string()),
                ("interval".to_string(), interval.to_string()),
            ],
        )
    }

    pub(super) async fn send_get_futures_mark_price_klines(
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

    pub fn get_spot_ticker_24hr(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(self, "get_spot_ticker_24hr", Vec::new())
    }

    pub(super) async fn send_get_spot_ticker_24hr(
        &self,
        request: AsterOptionalSymbolParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Spot, SPOT_TICKER_24HR, request)
            .await
    }

    pub fn get_futures_ticker_24hr(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(self, "get_futures_ticker_24hr", Vec::new())
    }

    pub(super) async fn send_get_futures_ticker_24hr(
        &self,
        request: AsterOptionalSymbolParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Futures, FUTURES_TICKER_24HR, request)
            .await
    }

    pub fn get_spot_ticker_price(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(self, "get_spot_ticker_price", Vec::new())
    }

    pub(super) async fn send_get_spot_ticker_price(
        &self,
        request: AsterOptionalSymbolParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Spot, SPOT_TICKER_PRICE, request)
            .await
    }

    pub fn get_futures_ticker_price(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_futures_ticker_price",
            Vec::new(),
        )
    }

    pub(super) async fn send_get_futures_ticker_price(
        &self,
        request: AsterOptionalSymbolParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Futures, FUTURES_TICKER_PRICE, request)
            .await
    }

    pub fn get_spot_book_ticker(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(self, "get_spot_book_ticker", Vec::new())
    }

    pub(super) async fn send_get_spot_book_ticker(
        &self,
        request: AsterOptionalSymbolParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Spot, SPOT_BOOK_TICKER, request)
            .await
    }

    pub fn get_futures_book_ticker(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(self, "get_futures_book_ticker", Vec::new())
    }

    pub(super) async fn send_get_futures_book_ticker(
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

    pub fn get_futures_premium_index(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_futures_premium_index",
            Vec::new(),
        )
    }

    pub(super) async fn send_get_futures_premium_index(
        &self,
        request: AsterOptionalSymbolParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Futures, FUTURES_PREMIUM_INDEX, request)
            .await
    }

    pub fn get_futures_funding_rate(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_futures_funding_rate",
            Vec::new(),
        )
    }

    pub(super) async fn send_get_futures_funding_rate(
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

    pub fn get_futures_funding_info(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_futures_funding_info",
            Vec::new(),
        )
    }

    pub(super) async fn send_get_futures_funding_info(
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
        validate_public_params(method_name, &params)?;
        match method_name {
            "ping_spot" => self.ping_spot().await,
            "ping_futures" => self.ping_futures().await,
            "get_spot_server_time" => self.get_spot_server_time().await,
            "get_futures_server_time" => self.get_futures_server_time().await,
            "get_spot_exchange_info" => self.get_spot_exchange_info().await,
            "get_futures_exchange_info" => self.get_futures_exchange_info().await,
            "get_spot_orderbook" => {
                self.send_get_spot_orderbook(
                    params.required("product_symbol")?,
                    AsterLimitParams {
                        limit: params.u64("limit")?,
                    },
                )
                .await
            }
            "get_futures_orderbook" => {
                self.send_get_futures_orderbook(
                    params.required("product_symbol")?,
                    AsterLimitParams {
                        limit: params.u64("limit")?,
                    },
                )
                .await
            }
            "get_spot_recent_trades" => {
                self.send_get_spot_recent_trades(
                    params.required("product_symbol")?,
                    AsterLimitParams {
                        limit: params.u64("limit")?,
                    },
                )
                .await
            }
            "get_futures_recent_trades" => {
                self.send_get_futures_recent_trades(
                    params.required("product_symbol")?,
                    AsterLimitParams {
                        limit: params.u64("limit")?,
                    },
                )
                .await
            }
            "get_spot_historical_trades" => {
                self.send_get_spot_historical_trades(
                    params.required("product_symbol")?,
                    AsterHistoricalTradesParams {
                        limit: params.u64("limit")?,
                        from_id: params.u64("fromId")?,
                    },
                )
                .await
            }
            "get_futures_historical_trades" => {
                self.send_get_futures_historical_trades(
                    params.required("product_symbol")?,
                    AsterHistoricalTradesParams {
                        limit: params.u64("limit")?,
                        from_id: params.u64("fromId")?,
                    },
                )
                .await
            }
            "get_spot_agg_trades" => {
                self.send_get_spot_agg_trades(
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
                self.send_get_futures_agg_trades(
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
                self.send_get_spot_klines(
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
                self.send_get_futures_klines(
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
                self.send_get_futures_index_price_klines(
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
                self.send_get_futures_mark_price_klines(
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
                self.send_get_spot_ticker_24hr(AsterOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
            }
            "get_futures_ticker_24hr" => {
                self.send_get_futures_ticker_24hr(AsterOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
            }
            "get_spot_ticker_price" => {
                self.send_get_spot_ticker_price(AsterOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
            }
            "get_futures_ticker_price" => {
                self.send_get_futures_ticker_price(AsterOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
            }
            "get_spot_book_ticker" => {
                self.send_get_spot_book_ticker(AsterOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
            }
            "get_futures_book_ticker" => {
                self.send_get_futures_book_ticker(AsterOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
            }
            "get_spot_withdraw_fee" => {
                self.get_spot_withdraw_fee(params.required("chainId")?, params.required("asset")?)
                    .await
            }
            "get_futures_premium_index" => {
                self.send_get_futures_premium_index(AsterOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
            }
            "get_futures_funding_rate" => {
                self.send_get_futures_funding_rate(AsterFundingRateParams {
                    product_symbol: params.get("product_symbol"),
                    start_time: params.u64("startTime")?,
                    end_time: params.u64("endTime")?,
                    limit: params.u64("limit")?,
                })
                .await
            }
            "get_futures_funding_info" => {
                self.send_get_futures_funding_info(AsterOptionalSymbolParams {
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

fn validate_public_params(method_name: &str, params: &AsterParams) -> Result<()> {
    match method_name {
        "ping_spot"
        | "ping_futures"
        | "get_spot_server_time"
        | "get_futures_server_time"
        | "get_spot_exchange_info"
        | "get_futures_exchange_info" => params.ensure_allowed(&[], &[]),
        "get_spot_orderbook" | "get_futures_orderbook" => {
            params.ensure_allowed(&["product_symbol", "limit"], &[])?;
            params.required("product_symbol")?;
            if let Some(limit) = params.u64("limit")? {
                if !matches!(limit, 5 | 10 | 20 | 50 | 100 | 500 | 1000) {
                    return Err(DcexError::InvalidInput(
                        "Aster depth limit must be one of 5, 10, 20, 50, 100, 500, 1000"
                            .to_string(),
                    ));
                }
            }
            Ok(())
        }
        "get_spot_recent_trades"
        | "get_futures_recent_trades"
        | "get_spot_historical_trades"
        | "get_futures_historical_trades" => {
            let mut allowed = vec!["product_symbol", "limit"];
            if method_name.contains("historical") {
                allowed.push("fromId");
            }
            params.ensure_allowed(&allowed, &[])?;
            params.required("product_symbol")?;
            params.optional_u64_range("limit", 1, 1000)?;
            params.u64("fromId")?;
            Ok(())
        }
        "get_spot_agg_trades" | "get_futures_agg_trades" => {
            params.ensure_allowed(
                &["product_symbol", "fromId", "startTime", "endTime", "limit"],
                &[],
            )?;
            params.required("product_symbol")?;
            params.u64("fromId")?;
            params.optional_u64_range("limit", 1, 1000)?;
            params.ensure_max_time_span("startTime", "endTime", 60 * 60 * 1000)
        }
        "get_spot_klines" | "get_futures_klines" | "get_futures_mark_price_klines" => {
            params.ensure_allowed(
                &[
                    "product_symbol",
                    "interval",
                    "startTime",
                    "endTime",
                    "limit",
                ],
                &[],
            )?;
            params.required("product_symbol")?;
            params.required_one_of("interval", KLINE_INTERVALS)?;
            params.optional_u64_range("limit", 1, 1500)?;
            params.ensure_time_order("startTime", "endTime")
        }
        "get_futures_index_price_klines" => {
            params.ensure_allowed(&["pair", "interval", "startTime", "endTime", "limit"], &[])?;
            params.required("pair")?;
            params.required_one_of("interval", KLINE_INTERVALS)?;
            params.optional_u64_range("limit", 1, 1500)?;
            params.ensure_time_order("startTime", "endTime")
        }
        "get_spot_ticker_24hr"
        | "get_futures_ticker_24hr"
        | "get_spot_ticker_price"
        | "get_futures_ticker_price"
        | "get_spot_book_ticker"
        | "get_futures_book_ticker"
        | "get_futures_premium_index"
        | "get_futures_funding_info" => params.ensure_allowed(&["product_symbol"], &[]),
        "get_spot_withdraw_fee" => {
            params.ensure_allowed(&["chainId", "asset"], &[])?;
            params.required_one_of("chainId", &["1", "56", "42161"])?;
            params.required("asset")?;
            Ok(())
        }
        "get_futures_funding_rate" => {
            params.ensure_allowed(&["product_symbol", "startTime", "endTime", "limit"], &[])?;
            params.optional_u64_range("limit", 1, 1000)?;
            params.ensure_time_order("startTime", "endTime")
        }
        "get_futures_index_references" => {
            params.ensure_allowed(&["product_symbol"], &[])?;
            params.required("product_symbol")?;
            Ok(())
        }
        _ => Ok(()),
    }
}

#[cfg(test)]
mod validation_tests {
    use super::*;

    #[test]
    fn spot_exchange_info_rejects_undocumented_filters() {
        let params = AsterParams::from_pairs(vec![(
            "product_symbol".to_string(),
            "BTC-USDT-SPOT".to_string(),
        )]);
        assert!(validate_public_params("get_spot_exchange_info", &params).is_err());
    }

    #[test]
    fn depth_limit_matches_documented_values() {
        let params = AsterParams::from_pairs(vec![
            ("product_symbol".to_string(), "BTC-USDT-SPOT".to_string()),
            ("limit".to_string(), "25".to_string()),
        ]);
        assert!(validate_public_params("get_spot_orderbook", &params).is_err());
    }
}
