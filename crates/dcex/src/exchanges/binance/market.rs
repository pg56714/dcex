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

    pub fn get_spot_exchange_info(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(self, "get_spot_exchange_info", Vec::new())
    }

    pub(super) async fn send_get_spot_exchange_info(
        &self,
        request: BinanceSymbolListParams<'_>,
    ) -> Result<ValidatedResponse> {
        let has_symbol_filter =
            request.product_symbol.is_some() || request.product_symbols.is_some();
        if has_symbol_filter && request.permissions.is_some() {
            return Err(DcexError::InvalidInput(
                "Binance permissions cannot be combined with product_symbol or product_symbols."
                    .to_string(),
            ));
        }
        if has_symbol_filter && request.symbol_status.is_some() {
            return Err(DcexError::InvalidInput(
                "Binance symbolStatus cannot be combined with product_symbol or product_symbols."
                    .to_string(),
            ));
        }

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
        if let Some(permissions) = request.permissions {
            params.push((
                "permissions".to_string(),
                serde_json::to_string(&permissions)
                    .map_err(|error| DcexError::Decode(error.to_string()))?,
            ));
        }
        push_optional(
            &mut params,
            "showPermissionSets",
            request.show_permission_sets,
        );
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
        request: BinanceLimitParams,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        push_optional_display(&mut params, "limit", request.limit);
        push_optional(
            &mut params,
            "symbolStatus",
            request.symbol_status.as_deref(),
        );
        self.request(
            HttpMethod::Get,
            BinanceMarket::Spot,
            SPOT_ORDERBOOK,
            params,
            false,
        )
        .await
    }

    pub fn get_spot_trades(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_spot_trades",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub(super) async fn send_get_spot_trades(
        &self,
        product_symbol: &str,
        request: BinanceLimitParams,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        push_optional_display(&mut params, "limit", request.limit);
        push_optional(
            &mut params,
            "symbolStatus",
            request.symbol_status.as_deref(),
        );
        self.request(
            HttpMethod::Get,
            BinanceMarket::Spot,
            SPOT_TRADES,
            params,
            false,
        )
        .await
    }

    pub fn get_spot_price(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(self, "get_spot_price", Vec::new())
    }

    pub(super) async fn send_get_spot_price(
        &self,
        request: BinanceSymbolListParams<'_>,
    ) -> Result<ValidatedResponse> {
        if request.product_symbol.is_some() && request.product_symbols.is_some() {
            return Err(DcexError::InvalidInput(
                "Binance product_symbol and product_symbols cannot be combined.".to_string(),
            ));
        }

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

    pub fn get_klines(
        &self,
        product_symbol: &str,
        interval: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_klines",
            vec![
                ("product_symbol".to_string(), product_symbol.to_string()),
                ("interval".to_string(), interval.to_string()),
            ],
        )
    }

    pub(super) async fn send_get_klines(
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
        push_optional_display(&mut params, "endTime", request.end_time);
        push_optional_display(&mut params, "limit", request.limit);
        let market = self.market_for_product_symbol(product_symbol)?;
        if market == BinanceMarket::Spot {
            push_optional(&mut params, "timeZone", request.time_zone.as_deref());
        }
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

    pub fn get_futures_ticker(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(self, "get_futures_ticker", Vec::new())
    }

    pub(super) async fn send_get_futures_ticker(
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

    pub fn get_futures_premium_index(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_futures_premium_index",
            Vec::new(),
        )
    }

    pub(super) async fn send_get_futures_premium_index(
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

    pub fn get_futures_funding_rate(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_futures_funding_rate",
            Vec::new(),
        )
    }

    pub(super) async fn send_get_futures_funding_rate(
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

    pub fn get_futures_open_interest_history(
        &self,
        product_symbol: &str,
        period: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_futures_open_interest_history",
            vec![
                ("product_symbol".to_string(), product_symbol.to_string()),
                ("period".to_string(), period.to_string()),
            ],
        )
    }

    pub(super) async fn send_get_futures_open_interest_history(
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

    pub fn get_futures_global_long_short_account_ratio(
        &self,
        product_symbol: &str,
        period: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_futures_global_long_short_account_ratio",
            vec![
                ("product_symbol".to_string(), product_symbol.to_string()),
                ("period".to_string(), period.to_string()),
            ],
        )
    }

    pub(super) async fn send_get_futures_global_long_short_account_ratio(
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

    pub fn get_futures_top_long_short_account_ratio(
        &self,
        product_symbol: &str,
        period: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_futures_top_long_short_account_ratio",
            vec![
                ("product_symbol".to_string(), product_symbol.to_string()),
                ("period".to_string(), period.to_string()),
            ],
        )
    }

    pub(super) async fn send_get_futures_top_long_short_account_ratio(
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

    pub fn get_futures_top_long_short_position_ratio(
        &self,
        product_symbol: &str,
        period: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_futures_top_long_short_position_ratio",
            vec![
                ("product_symbol".to_string(), product_symbol.to_string()),
                ("period".to_string(), period.to_string()),
            ],
        )
    }

    pub(super) async fn send_get_futures_top_long_short_position_ratio(
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

    pub fn get_futures_taker_buy_sell_volume(
        &self,
        product_symbol: &str,
        period: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_futures_taker_buy_sell_volume",
            vec![
                ("product_symbol".to_string(), product_symbol.to_string()),
                ("period".to_string(), period.to_string()),
            ],
        )
    }

    pub(super) async fn send_get_futures_taker_buy_sell_volume(
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

    pub fn get_futures_basis(
        &self,
        product_symbol: &str,
        contract_type: &str,
        period: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_futures_basis",
            vec![
                ("product_symbol".to_string(), product_symbol.to_string()),
                ("contractType".to_string(), contract_type.to_string()),
                ("period".to_string(), period.to_string()),
            ],
        )
    }

    pub(super) async fn send_get_futures_basis(
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
                self.send_get_spot_exchange_info(BinanceSymbolListParams {
                    product_symbol: params.get("product_symbol"),
                    product_symbols: params.values("product_symbols"),
                    permissions: params.values("permissions"),
                    show_permission_sets: params.get("showPermissionSets"),
                    symbol_status: params.get("symbolStatus"),
                })
                .await
            }
            "get_spot_orderbook" => {
                self.send_get_spot_orderbook(
                    params.required("product_symbol")?,
                    BinanceLimitParams {
                        limit: params.u64("limit")?,
                        symbol_status: params.get("symbolStatus").map(str::to_string),
                    },
                )
                .await
            }
            "get_spot_trades" => {
                self.send_get_spot_trades(
                    params.required("product_symbol")?,
                    BinanceLimitParams {
                        limit: params.u64("limit")?,
                        symbol_status: params.get("symbolStatus").map(str::to_string),
                    },
                )
                .await
            }
            "get_spot_price" => {
                self.send_get_spot_price(BinanceSymbolListParams {
                    product_symbol: params.get("product_symbol"),
                    product_symbols: params.values("product_symbols"),
                    permissions: None,
                    show_permission_sets: None,
                    symbol_status: params.get("symbolStatus"),
                })
                .await
            }
            "get_klines" => {
                self.send_get_klines(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    BinanceKlinesParams {
                        start_time: params.u64("start_time")?,
                        end_time: params.u64("end_time")?,
                        time_zone: params.get("time_zone").map(str::to_string),
                        limit: params.u64("limit")?,
                    },
                )
                .await
            }
            "get_futures_exchange_info" => self.get_futures_exchange_info().await,
            "get_futures_ticker" => {
                self.send_get_futures_ticker(BinanceOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
            }
            "get_futures_premium_index" => {
                self.send_get_futures_premium_index(BinanceOptionalSymbolParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
            }
            "get_futures_funding_rate" => {
                self.send_get_futures_funding_rate(BinanceFundingRateParams {
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
                self.send_get_futures_open_interest_history(
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
                self.send_get_futures_global_long_short_account_ratio(
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
                self.send_get_futures_top_long_short_account_ratio(
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
                self.send_get_futures_top_long_short_position_ratio(
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
                self.send_get_futures_taker_buy_sell_volume(
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
                self.send_get_futures_basis(
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
