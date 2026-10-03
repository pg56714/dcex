pub(in crate::exchanges::binance) use super::client::{BinanceClient, BinanceMarket};
pub(in crate::exchanges::binance) use super::endpoints::*;
pub(in crate::exchanges::binance) use super::params::{
    BinanceFundingWalletParams, BinanceIncomeHistoryParams, BinanceWalletBalanceParams,
    push_optional, push_optional_display,
};
pub(in crate::exchanges::binance) use crate::Result;
pub(in crate::exchanges::binance) use crate::exchange::ValidatedResponse;
pub(in crate::exchanges::binance) use crate::http::HttpMethod;

impl BinanceClient {
    pub async fn get_spot_fee_rates(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            BinanceMarket::Spot,
            SPOT_COMMISSION_RATE,
            vec![(
                "symbol".to_string(),
                self.exchange_symbol_for(product_symbol, super::client::BinanceMarket::Spot)?,
            )],
            true,
        )
        .await
    }

    pub async fn get_futures_fee_rates(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_COMMISSION_RATE,
            vec![(
                "symbol".to_string(),
                self.exchange_symbol_for(product_symbol, super::client::BinanceMarket::Futures)?,
            )],
            true,
        )
        .await
    }
    pub async fn get_account_balance(
        &self,
        market_type: &str,
        omit_zero_balances: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let (market, path) = if market_type == "spot" {
            (BinanceMarket::Spot, SPOT_ACCOUNT_BALANCE)
        } else {
            (BinanceMarket::Futures, FUTURES_ACCOUNT_BALANCE)
        };
        let mut params = Vec::new();
        if market == BinanceMarket::Spot {
            push_optional(&mut params, "omitZeroBalances", omit_zero_balances);
        }
        self.request(HttpMethod::Get, market, path, params, true)
            .await
    }

    pub fn get_income_history(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(self, "get_income_history", Vec::new())
    }

    pub(super) async fn send_get_income_history(
        &self,
        request: BinanceIncomeHistoryParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = request.product_symbol {
            params.push((
                "symbol".to_string(),
                self.exchange_symbol_for(product_symbol, super::client::BinanceMarket::Futures)?,
            ));
        }
        push_optional(&mut params, "incomeType", request.income_type);
        push_optional_display(&mut params, "startTime", request.start_time);
        push_optional_display(&mut params, "endTime", request.end_time);
        push_optional_display(&mut params, "page", request.page);
        push_optional_display(&mut params, "limit", request.limit);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_INCOME_HISTORY,
            params,
            true,
        )
        .await
    }

    pub async fn get_futures_account_info(&self) -> Result<ValidatedResponse> {
        self.request(
            HttpMethod::Get,
            BinanceMarket::Futures,
            FUTURES_ACCOUNT_INFO,
            Vec::new(),
            true,
        )
        .await
    }

    pub fn get_wallet_balance(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(self, "get_wallet_balance", Vec::new())
    }

    pub(super) async fn send_get_wallet_balance(
        &self,
        request: BinanceWalletBalanceParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        push_optional(&mut params, "quoteAsset", request.quote_asset);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Spot,
            WALLET_BALANCE,
            params,
            true,
        )
        .await
    }

    pub fn get_funding_wallet(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(self, "get_funding_wallet", Vec::new())
    }

    pub(super) async fn send_get_funding_wallet(
        &self,
        request: BinanceFundingWalletParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        push_optional(&mut params, "asset", request.asset);
        push_optional(&mut params, "needBtcValuation", request.need_btc_valuation);
        self.request(
            HttpMethod::Post,
            BinanceMarket::Spot,
            FUNDING_WALLET,
            params,
            true,
        )
        .await
    }
}
