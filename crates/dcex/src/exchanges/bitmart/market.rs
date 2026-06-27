use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::{BitmartClient, BitmartMarket};
use super::endpoints::*;
use super::params::{
    bitmart_timeframe, push_optional, BitmartContractsDetailsParams,
    BitmartFundingRateHistoryParams, BitmartParams, BitmartSpotKlineParams,
};

impl BitmartClient {
    pub async fn get_spot_currencies(&self) -> Result<ValidatedResponse> {
        self.public_get(BitmartMarket::Spot, SPOT_CURRENCIES, Vec::new())
            .await
    }

    pub async fn get_trading_pairs(&self) -> Result<ValidatedResponse> {
        self.public_get(BitmartMarket::Spot, SPOT_SYMBOLS, Vec::new())
            .await
    }

    pub async fn get_trading_pairs_details(&self) -> Result<ValidatedResponse> {
        self.public_get(BitmartMarket::Spot, SPOT_SYMBOL_DETAILS, Vec::new())
            .await
    }

    pub async fn get_ticker_of_all_pairs(&self) -> Result<ValidatedResponse> {
        self.public_get(BitmartMarket::Spot, SPOT_TICKERS, Vec::new())
            .await
    }

    pub async fn get_ticker_of_a_pair(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.public_get(
            BitmartMarket::Spot,
            SPOT_TICKER,
            vec![(
                "symbol".to_string(),
                self.exchange_symbol(product_symbol, true)?,
            )],
        )
        .await
    }

    pub async fn get_spot_kline(
        &self,
        product_symbol: &str,
        interval: &str,
    ) -> Result<ValidatedResponse> {
        self.get_spot_kline_with(product_symbol, interval, BitmartSpotKlineParams::default())
            .await
    }

    pub async fn get_spot_kline_with(
        &self,
        product_symbol: &str,
        interval: &str,
        request: BitmartSpotKlineParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![
            (
                "symbol".to_string(),
                self.exchange_symbol(product_symbol, true)?,
            ),
            ("step".to_string(), bitmart_timeframe(interval)?.to_string()),
        ];
        push_optional(&mut params, "before", request.before);
        push_optional(&mut params, "after", request.after);
        push_optional(&mut params, "limit", request.limit);
        self.public_get(BitmartMarket::Spot, SPOT_KLINE, params)
            .await
    }

    pub async fn get_contracts_details(&self) -> Result<ValidatedResponse> {
        self.get_contracts_details_with(BitmartContractsDetailsParams::default())
            .await
    }

    pub async fn get_contracts_details_with(
        &self,
        request: BitmartContractsDetailsParams<'_>,
    ) -> Result<ValidatedResponse> {
        self.public_get(
            BitmartMarket::Futures,
            FUTURES_CONTRACT_DETAILS,
            self.optional_symbol_params(request.product_symbol, false)?,
        )
        .await
    }

    pub async fn get_depth(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.futures_symbol_get(FUTURES_DEPTH, product_symbol).await
    }

    pub async fn get_contract_kline(
        &self,
        product_symbol: &str,
        interval: &str,
        start_time: &str,
        end_time: &str,
    ) -> Result<ValidatedResponse> {
        self.futures_kline_get(
            FUTURES_KLINE,
            product_symbol,
            interval,
            start_time,
            end_time,
        )
        .await
    }

    pub async fn get_open_interest(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.futures_symbol_get(FUTURES_OPEN_INTEREST, product_symbol)
            .await
    }

    pub async fn get_mark_price_kline(
        &self,
        product_symbol: &str,
        interval: &str,
        start_time: &str,
        end_time: &str,
    ) -> Result<ValidatedResponse> {
        self.futures_kline_get(
            FUTURES_MARK_PRICE_KLINE,
            product_symbol,
            interval,
            start_time,
            end_time,
        )
        .await
    }

    pub async fn get_leverage_bracket(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.futures_symbol_get(FUTURES_LEVERAGE_BRACKET, product_symbol)
            .await
    }

    pub async fn get_current_funding_rate(
        &self,
        product_symbol: &str,
    ) -> Result<ValidatedResponse> {
        self.futures_symbol_get(FUTURES_FUNDING_RATE, product_symbol)
            .await
    }

    pub async fn get_funding_rate_history(
        &self,
        product_symbol: &str,
    ) -> Result<ValidatedResponse> {
        self.get_funding_rate_history_with(
            product_symbol,
            BitmartFundingRateHistoryParams::default(),
        )
        .await
    }

    pub async fn get_funding_rate_history_with(
        &self,
        product_symbol: &str,
        request: BitmartFundingRateHistoryParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![(
            "symbol".to_string(),
            self.exchange_symbol(product_symbol, false)?,
        )];
        push_optional(&mut params, "limit", request.limit);
        self.public_get(BitmartMarket::Futures, FUTURES_FUNDING_RATE_HISTORY, params)
            .await
    }

    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = BitmartParams::from_pairs(params);
        match method_name {
            "get_spot_currencies" => self.get_spot_currencies().await,
            "get_trading_pairs" => self.get_trading_pairs().await,
            "get_trading_pairs_details" => self.get_trading_pairs_details().await,
            "get_ticker_of_all_pairs" => self.get_ticker_of_all_pairs().await,
            "get_ticker_of_a_pair" => {
                self.get_ticker_of_a_pair(params.required("product_symbol")?)
                    .await
            }
            "get_spot_kline" => {
                self.get_spot_kline_with(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    BitmartSpotKlineParams {
                        before: params.get("before"),
                        after: params.get("after"),
                        limit: params.get("limit"),
                    },
                )
                .await
            }
            "get_contracts_details" => {
                self.get_contracts_details_with(BitmartContractsDetailsParams {
                    product_symbol: params.get("product_symbol"),
                })
                .await
            }
            "get_depth" => self.get_depth(params.required("product_symbol")?).await,
            "get_contract_kline" => {
                self.get_contract_kline(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    params.required("start_time")?,
                    params.required("end_time")?,
                )
                .await
            }
            "get_open_interest" => {
                self.get_open_interest(params.required("product_symbol")?)
                    .await
            }
            "get_mark_price_kline" => {
                self.get_mark_price_kline(
                    params.required("product_symbol")?,
                    params.required("interval")?,
                    params.required("start_time")?,
                    params.required("end_time")?,
                )
                .await
            }
            "get_leverage_bracket" => {
                self.get_leverage_bracket(params.required("product_symbol")?)
                    .await
            }
            "get_current_funding_rate" => {
                self.get_current_funding_rate(params.required("product_symbol")?)
                    .await
            }
            "get_funding_rate_history" => {
                self.get_funding_rate_history_with(
                    params.required("product_symbol")?,
                    BitmartFundingRateHistoryParams {
                        limit: params.get("limit"),
                    },
                )
                .await
            }
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported BitMart public method: {method_name}"
            ))),
        }
    }

    async fn futures_symbol_get(
        &self,
        path: &str,
        product_symbol: &str,
    ) -> Result<ValidatedResponse> {
        self.public_get(
            BitmartMarket::Futures,
            path,
            vec![(
                "symbol".to_string(),
                self.exchange_symbol(product_symbol, false)?,
            )],
        )
        .await
    }

    async fn futures_kline_get(
        &self,
        path: &str,
        product_symbol: &str,
        interval: &str,
        start_time: &str,
        end_time: &str,
    ) -> Result<ValidatedResponse> {
        self.public_get(
            BitmartMarket::Futures,
            path,
            vec![
                (
                    "symbol".to_string(),
                    self.exchange_symbol(product_symbol, false)?,
                ),
                ("step".to_string(), bitmart_timeframe(interval)?.to_string()),
                ("start_time".to_string(), start_time.to_string()),
                ("end_time".to_string(), end_time.to_string()),
            ],
        )
        .await
    }

    pub(super) fn optional_symbol_params(
        &self,
        product_symbol: Option<&str>,
        spot: bool,
    ) -> Result<Vec<(String, String)>> {
        product_symbol
            .map(|product_symbol| {
                self.exchange_symbol(product_symbol, spot)
                    .map(|symbol| vec![("symbol".to_string(), symbol)])
            })
            .unwrap_or_else(|| Ok(Vec::new()))
    }
}
