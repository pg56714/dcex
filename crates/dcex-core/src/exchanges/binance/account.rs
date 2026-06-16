use super::client::{BinanceClient, BinanceMarket};
use super::endpoints::*;
use super::params::{push_optional, push_optional_display};
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

    pub async fn get_income_history(
        &self,
        product_symbol: Option<&str>,
        income_type: Option<&str>,
        start_time: Option<u64>,
        end_time: Option<u64>,
        page: Option<u64>,
        limit: Option<u64>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = product_symbol {
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        }
        push_optional(&mut params, "incomeType", income_type);
        push_optional_display(&mut params, "startTime", start_time);
        push_optional_display(&mut params, "endTime", end_time);
        push_optional_display(&mut params, "page", page);
        push_optional_display(&mut params, "limit", limit);
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

    pub async fn get_wallet_balance(&self, quote_asset: Option<&str>) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        push_optional(&mut params, "quoteAsset", quote_asset);
        self.request(
            HttpMethod::Get,
            BinanceMarket::Spot,
            WALLET_BALANCE,
            params,
            true,
        )
        .await
    }

    pub async fn get_funding_wallet(
        &self,
        asset: Option<&str>,
        need_btc_valuation: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        push_optional(&mut params, "asset", asset);
        push_optional(&mut params, "needBtcValuation", need_btc_valuation);
        self.request(
            HttpMethod::Post,
            BinanceMarket::Spot,
            FUNDING_WALLET,
            params,
            true,
        )
        .await
    }

    pub async fn create_universal_transfer(
        &self,
        transfer_type: &str,
        asset: &str,
        amount: &str,
        from_symbol: Option<&str>,
        to_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![
            ("type".to_string(), transfer_type.to_string()),
            ("asset".to_string(), asset.to_string()),
            ("amount".to_string(), amount.to_string()),
        ];
        push_optional(&mut params, "fromSymbol", from_symbol);
        push_optional(&mut params, "toSymbol", to_symbol);
        self.request(
            HttpMethod::Post,
            BinanceMarket::Spot,
            UNIVERSAL_TRANSFER,
            params,
            true,
        )
        .await
    }

    pub async fn get_universal_transfer_history(
        &self,
        transfer_type: &str,
        start_time: Option<u64>,
        end_time: Option<u64>,
        current: Option<u64>,
        size: Option<u64>,
        from_symbol: Option<&str>,
        to_symbol: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("type".to_string(), transfer_type.to_string())];
        push_optional_display(&mut params, "startTime", start_time);
        push_optional_display(&mut params, "endTime", end_time);
        push_optional_display(&mut params, "current", current);
        push_optional_display(&mut params, "size", size);
        push_optional(&mut params, "fromSymbol", from_symbol);
        push_optional(&mut params, "toSymbol", to_symbol);
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
