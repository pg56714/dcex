use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::MexcApi;
use super::client::MexcClient;
use super::endpoints::*;
use super::params::MexcParams;

impl MexcClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let mut params = MexcParams::from_pairs(params).into_inner();
        let (api, path) = match method_name {
            "ping" => (MexcApi::Spot, SPOT_PING.to_string()),
            "get_spot_time" => (MexcApi::Spot, SPOT_TIME.to_string()),
            "get_spot_default_symbols" => (MexcApi::Spot, SPOT_DEFAULT_SYMBOLS.to_string()),
            "get_spot_exchange_info" => {
                self.normalize_symbol_params(&mut params, "")?;
                (MexcApi::Spot, SPOT_EXCHANGE_INFO.to_string())
            }
            "get_spot_orderbook" => {
                self.normalize_symbol_params(&mut params, "")?;
                (MexcApi::Spot, SPOT_ORDERBOOK.to_string())
            }
            "get_spot_recent_trades" => {
                self.normalize_symbol_params(&mut params, "")?;
                (MexcApi::Spot, SPOT_RECENT_TRADES.to_string())
            }
            "get_spot_agg_trades" => {
                self.normalize_symbol_params(&mut params, "")?;
                (MexcApi::Spot, SPOT_AGG_TRADES.to_string())
            }
            "get_spot_klines" => {
                self.normalize_symbol_params(&mut params, "")?;
                (MexcApi::Spot, SPOT_KLINES.to_string())
            }
            "get_spot_avg_price" => {
                self.normalize_symbol_params(&mut params, "")?;
                (MexcApi::Spot, SPOT_AVG_PRICE.to_string())
            }
            "get_spot_ticker_24hr" => {
                self.normalize_symbol_params(&mut params, "")?;
                (MexcApi::Spot, SPOT_TICKER_24HR.to_string())
            }
            "get_spot_ticker_price" => {
                self.normalize_symbol_params(&mut params, "")?;
                (MexcApi::Spot, SPOT_TICKER_PRICE.to_string())
            }
            "get_spot_book_ticker" => {
                self.normalize_symbol_params(&mut params, "")?;
                (MexcApi::Spot, SPOT_BOOK_TICKER.to_string())
            }
            "get_contract_time" => (MexcApi::Contract, CONTRACT_PING.to_string()),
            "get_contract_details" => {
                self.normalize_symbol_params(&mut params, "_")?;
                (MexcApi::Contract, CONTRACT_DETAIL.to_string())
            }
            "get_contract_ticker" => {
                self.normalize_symbol_params(&mut params, "_")?;
                (MexcApi::Contract, CONTRACT_TICKER.to_string())
            }
            "get_contract_depth" => {
                let symbol = self.take_symbol(&mut params, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/depth/{symbol}"),
                )
            }
            "get_contract_depth_commits" => {
                let symbol = self.take_symbol(&mut params, "_")?;
                let limit = super::client::take_param(&mut params, "limit")
                    .unwrap_or_else(|| "20".to_string());
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/depth_commits/{symbol}/{limit}"),
                )
            }
            "get_contract_index_price" => {
                let symbol = self.take_symbol(&mut params, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/index_price/{symbol}"),
                )
            }
            "get_contract_fair_price" => {
                let symbol = self.take_symbol(&mut params, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/fair_price/{symbol}"),
                )
            }
            "get_contract_funding_rate" => {
                let symbol = self.take_symbol(&mut params, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/funding_rate/{symbol}"),
                )
            }
            "get_contract_kline" => {
                let symbol = self.take_symbol(&mut params, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/kline/{symbol}"),
                )
            }
            "get_contract_index_price_kline" => {
                let symbol = self.take_symbol(&mut params, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/kline/index_price/{symbol}"),
                )
            }
            "get_contract_fair_price_kline" => {
                let symbol = self.take_symbol(&mut params, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/kline/fair_price/{symbol}"),
                )
            }
            "get_contract_deals" => {
                let symbol = self.take_symbol(&mut params, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/deals/{symbol}"),
                )
            }
            "get_contract_risk_reverse" => (MexcApi::Contract, CONTRACT_RISK_REVERSE.to_string()),
            "get_contract_risk_reverse_history" => {
                self.normalize_symbol_params(&mut params, "_")?;
                (MexcApi::Contract, CONTRACT_RISK_REVERSE_HISTORY.to_string())
            }
            "get_contract_funding_rate_history" => {
                self.normalize_symbol_params(&mut params, "_")?;
                (MexcApi::Contract, CONTRACT_FUNDING_RATE_HISTORY.to_string())
            }
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported MEXC public method: {method_name}"
                )));
            }
        };
        self.request(HttpMethod::Get, api, path, params, None, false)
            .await
    }
}
