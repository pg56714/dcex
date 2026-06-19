use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::{AsterClient, AsterMarket};
use super::endpoints::*;
use super::params::{push_optional_display, AsterParams};

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

    pub async fn get_spot_exchange_info(
        &self,
        product_symbol: Option<&str>,
        symbols: Option<Vec<String>>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = product_symbol {
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        }
        if let Some(symbols) = symbols {
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

    pub async fn get_spot_orderbook(
        &self,
        product_symbol: &str,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.symbol_request(AsterMarket::Spot, SPOT_DEPTH, product_symbol, limit)
            .await
    }

    pub async fn get_futures_orderbook(
        &self,
        product_symbol: &str,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.symbol_request(AsterMarket::Futures, FUTURES_DEPTH, product_symbol, limit)
            .await
    }

    pub async fn get_spot_recent_trades(
        &self,
        product_symbol: &str,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.symbol_request(AsterMarket::Spot, SPOT_TRADES, product_symbol, limit)
            .await
    }

    pub async fn get_futures_recent_trades(
        &self,
        product_symbol: &str,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.symbol_request(AsterMarket::Futures, FUTURES_TRADES, product_symbol, limit)
            .await
    }

    pub async fn get_spot_historical_trades(
        &self,
        product_symbol: &str,
        limit: Option<u64>,
        from_id: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.historical_trades_request(
            AsterMarket::Spot,
            SPOT_HISTORICAL_TRADES,
            product_symbol,
            limit,
            from_id,
        )
        .await
    }

    pub async fn get_futures_historical_trades(
        &self,
        product_symbol: &str,
        limit: Option<u64>,
        from_id: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.historical_trades_request(
            AsterMarket::Futures,
            FUTURES_HISTORICAL_TRADES,
            product_symbol,
            limit,
            from_id,
        )
        .await
    }

    pub async fn get_spot_agg_trades(
        &self,
        product_symbol: &str,
        from_id: Option<u64>,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.agg_trades_request(
            AsterMarket::Spot,
            SPOT_AGG_TRADES,
            product_symbol,
            from_id,
            start_time,
            end_time,
            limit,
        )
        .await
    }

    pub async fn get_futures_agg_trades(
        &self,
        product_symbol: &str,
        from_id: Option<u64>,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.agg_trades_request(
            AsterMarket::Futures,
            FUTURES_AGG_TRADES,
            product_symbol,
            from_id,
            start_time,
            end_time,
            limit,
        )
        .await
    }

    pub async fn get_spot_klines(
        &self,
        product_symbol: &str,
        interval: &str,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.klines_request(
            AsterMarket::Spot,
            SPOT_KLINES,
            product_symbol,
            interval,
            start_time,
            end_time,
            limit,
        )
        .await
    }

    pub async fn get_futures_klines(
        &self,
        product_symbol: &str,
        interval: &str,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.klines_request(
            AsterMarket::Futures,
            FUTURES_KLINES,
            product_symbol,
            interval,
            start_time,
            end_time,
            limit,
        )
        .await
    }

    pub async fn get_futures_index_price_klines(
        &self,
        pair: &str,
        interval: &str,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![
            ("pair".to_string(), pair.to_string()),
            ("interval".to_string(), interval.to_string()),
        ];
        push_optional_display(&mut params, "startTime", start_time);
        push_optional_display(&mut params, "endTime", end_time);
        push_optional_display(&mut params, "limit", limit);
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
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        self.klines_request(
            AsterMarket::Futures,
            FUTURES_MARK_PRICE_KLINES,
            product_symbol,
            interval,
            start_time,
            end_time,
            limit,
        )
        .await
    }

    pub async fn get_spot_ticker_24hr(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Spot, SPOT_TICKER_24HR, product_symbol)
            .await
    }

    pub async fn get_futures_ticker_24hr(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Futures, FUTURES_TICKER_24HR, product_symbol)
            .await
    }

    pub async fn get_spot_ticker_price(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Spot, SPOT_TICKER_PRICE, product_symbol)
            .await
    }

    pub async fn get_futures_ticker_price(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Futures, FUTURES_TICKER_PRICE, product_symbol)
            .await
    }

    pub async fn get_spot_book_ticker(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Spot, SPOT_BOOK_TICKER, product_symbol)
            .await
    }

    pub async fn get_futures_book_ticker(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Futures, FUTURES_BOOK_TICKER, product_symbol)
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

    pub async fn get_futures_premium_index(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Futures, FUTURES_PREMIUM_INDEX, product_symbol)
            .await
    }

    pub async fn get_futures_funding_rate(
        &self,
        product_symbol: Option<&str>,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = product_symbol {
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        }
        push_optional_display(&mut params, "startTime", start_time);
        push_optional_display(&mut params, "endTime", end_time);
        push_optional_display(&mut params, "limit", limit);
        self.request(
            HttpMethod::Get,
            AsterMarket::Futures,
            FUTURES_FUNDING_RATE,
            params,
            false,
        )
        .await
    }

    pub async fn get_futures_funding_info(
        &self,
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        self.optional_symbol_request(AsterMarket::Futures, FUTURES_FUNDING_INFO, product_symbol)
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
                self.get_spot_exchange_info(params.get("product_symbol"), params.values("symbols"))
                    .await
            }
            "get_futures_exchange_info" => self.get_futures_exchange_info().await,
            "get_spot_orderbook" => {
                self.get_spot_orderbook(params.required("product_symbol")?, params.u64("limit")?)
                    .await
            }
            "get_futures_orderbook" => {
                self.get_futures_orderbook(params.required("product_symbol")?, params.u64("limit")?)
                    .await
            }
            "get_spot_recent_trades" => {
                self.get_spot_recent_trades(
                    params.required("product_symbol")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_futures_recent_trades" => {
                self.get_futures_recent_trades(
                    params.required("product_symbol")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_spot_historical_trades" => {
                self.get_spot_historical_trades(
                    params.required("product_symbol")?,
                    params.u64("limit")?,
                    params.u64("fromId")?,
                )
                .await
            }
            "get_futures_historical_trades" => {
                self.get_futures_historical_trades(
                    params.required("product_symbol")?,
                    params.u64("limit")?,
                    params.u64("fromId")?,
                )
                .await
            }
            "get_spot_agg_trades" => {
                self.get_spot_agg_trades(
                    params.required("product_symbol")?,
                    params.u64("fromId")?,
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_futures_agg_trades" => {
                self.get_futures_agg_trades(
                    params.required("product_symbol")?,
                    params.u64("fromId")?,
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_spot_klines" => {
                self.get_spot_klines(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_futures_klines" => {
                self.get_futures_klines(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_futures_index_price_klines" => {
                self.get_futures_index_price_klines(
                    params.required("pair")?,
                    params.required("interval")?,
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_futures_mark_price_klines" => {
                self.get_futures_mark_price_klines(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_spot_ticker_24hr" => {
                self.get_spot_ticker_24hr(params.get("product_symbol"))
                    .await
            }
            "get_futures_ticker_24hr" => {
                self.get_futures_ticker_24hr(params.get("product_symbol"))
                    .await
            }
            "get_spot_ticker_price" => {
                self.get_spot_ticker_price(params.get("product_symbol"))
                    .await
            }
            "get_futures_ticker_price" => {
                self.get_futures_ticker_price(params.get("product_symbol"))
                    .await
            }
            "get_spot_book_ticker" => {
                self.get_spot_book_ticker(params.get("product_symbol"))
                    .await
            }
            "get_futures_book_ticker" => {
                self.get_futures_book_ticker(params.get("product_symbol"))
                    .await
            }
            "get_spot_withdraw_fee" => {
                self.get_spot_withdraw_fee(params.required("chainId")?, params.required("asset")?)
                    .await
            }
            "get_futures_premium_index" => {
                self.get_futures_premium_index(params.get("product_symbol"))
                    .await
            }
            "get_futures_funding_rate" => {
                self.get_futures_funding_rate(
                    params.get("product_symbol"),
                    params.u64("startTime")?,
                    params.u64("endTime")?,
                    params.u64("limit")?,
                )
                .await
            }
            "get_futures_funding_info" => {
                self.get_futures_funding_info(params.get("product_symbol"))
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
        product_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = product_symbol {
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
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        push_optional_display(&mut params, "limit", limit);
        self.request(HttpMethod::Get, market, path, params, false)
            .await
    }

    async fn historical_trades_request(
        &self,
        market: AsterMarket,
        path: &str,
        product_symbol: &str,
        limit: Option<u64>,
        from_id: Option<u64>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        push_optional_display(&mut params, "limit", limit);
        push_optional_display(&mut params, "fromId", from_id);
        self.request(HttpMethod::Get, market, path, params, false)
            .await
    }

    async fn agg_trades_request(
        &self,
        market: AsterMarket,
        path: &str,
        product_symbol: &str,
        from_id: Option<u64>,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        push_optional_display(&mut params, "fromId", from_id);
        push_optional_display(&mut params, "startTime", start_time);
        push_optional_display(&mut params, "endTime", end_time);
        push_optional_display(&mut params, "limit", limit);
        self.request(HttpMethod::Get, market, path, params, false)
            .await
    }

    async fn klines_request(
        &self,
        market: AsterMarket,
        path: &str,
        product_symbol: &str,
        interval: &str,
        start_time: Option<u64>,
        end_time: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![
            ("symbol".to_string(), self.exchange_symbol(product_symbol)?),
            ("interval".to_string(), interval.to_string()),
        ];
        push_optional_display(&mut params, "startTime", start_time);
        push_optional_display(&mut params, "endTime", end_time);
        push_optional_display(&mut params, "limit", limit);
        self.request(HttpMethod::Get, market, path, params, false)
            .await
    }
}
