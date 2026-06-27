use super::client::{BinanceClient, BinanceMarket};
use super::endpoints::*;
use super::params::{
    push_optional, push_optional_display, BinanceFundingWalletParams, BinanceIncomeHistoryParams,
    BinanceUniversalTransferHistoryParams, BinanceUniversalTransferParams,
    BinanceWalletBalanceParams,
};
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::Result;

impl BinanceClient {
    pub async fn get_account_balance(&self, market_type: &str) -> Result<ValidatedResponse> {
        let (market, path) = if market_type == "spot" {
            (BinanceMarket::Spot, SPOT_ACCOUNT_BALANCE)
        } else {
            (BinanceMarket::Futures, FUTURES_ACCOUNT_BALANCE)
        };
        self.request(HttpMethod::Get, market, path, Vec::new(), true)
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
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
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

    pub fn create_universal_transfer(
        &self,
        transfer_type: &str,
        asset: &str,
        amount: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "create_universal_transfer",
            vec![
                ("type".to_string(), transfer_type.to_string()),
                ("asset".to_string(), asset.to_string()),
                ("amount".to_string(), amount.to_string()),
            ],
        )
    }

    pub(super) async fn send_create_universal_transfer(
        &self,
        transfer_type: &str,
        asset: &str,
        amount: &str,
        request: BinanceUniversalTransferParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![
            ("type".to_string(), transfer_type.to_string()),
            ("asset".to_string(), asset.to_string()),
            ("amount".to_string(), amount.to_string()),
        ];
        push_optional(&mut params, "fromSymbol", request.from_symbol);
        push_optional(&mut params, "toSymbol", request.to_symbol);
        self.request(
            HttpMethod::Post,
            BinanceMarket::Spot,
            UNIVERSAL_TRANSFER,
            params,
            true,
        )
        .await
    }

    pub fn get_universal_transfer_history(
        &self,
        transfer_type: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_universal_transfer_history",
            vec![("type".to_string(), transfer_type.to_string())],
        )
    }

    pub(super) async fn send_get_universal_transfer_history(
        &self,
        transfer_type: &str,
        request: BinanceUniversalTransferHistoryParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("type".to_string(), transfer_type.to_string())];
        push_optional_display(&mut params, "startTime", request.start_time);
        push_optional_display(&mut params, "endTime", request.end_time);
        push_optional_display(&mut params, "current", request.current);
        push_optional_display(&mut params, "size", request.size);
        push_optional(&mut params, "fromSymbol", request.from_symbol);
        push_optional(&mut params, "toSymbol", request.to_symbol);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Spot,
            UNIVERSAL_TRANSFER,
            params,
            true,
        )
        .await
    }
}
