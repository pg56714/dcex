use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::GateioClient;
use super::endpoints::*;

impl GateioClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        mut params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let path = match method_name {
            "get_all_futures_contracts" => {
                let settle = take_settle(&mut params);
                fill_settle(FUTURES_CONTRACTS, &settle)
            }
            "get_a_single_futures_contract" => {
                let settle = take_settle(&mut params);
                let contract = self.take_contract(&mut params)?;
                fill_contract(FUTURES_CONTRACT, &settle, &contract)
            }
            "get_contract_order_book" => {
                let settle = take_settle(&mut params);
                let market = take_market_path(&mut params)?;
                self.normalize_contract_query(&mut params)?;
                let endpoint =
                    market_path(&market, "order_book", "order_book").ok_or_else(|| {
                        DcexError::InvalidInput(format!(
                            "unsupported Gate.io market path: {market}"
                        ))
                    })?;
                fill_settle(endpoint, &settle)
            }
            "get_contract_kline" => {
                let settle = take_settle(&mut params);
                let market = take_market_path(&mut params)?;
                self.normalize_contract_query(&mut params)?;
                let endpoint =
                    market_path(&market, "candlesticks", "candlesticks").ok_or_else(|| {
                        DcexError::InvalidInput(format!(
                            "unsupported Gate.io market path: {market}"
                        ))
                    })?;
                fill_settle(endpoint, &settle)
            }
            "get_contract_list_tickers" => {
                let settle = take_settle(&mut params);
                let market = take_market_path(&mut params)?;
                self.normalize_contract_query(&mut params)?;
                let endpoint = market_path(&market, "tickers", "tickers").ok_or_else(|| {
                    DcexError::InvalidInput(format!("unsupported Gate.io market path: {market}"))
                })?;
                fill_settle(endpoint, &settle)
            }
            "get_futures_funding_rate_history" => {
                let settle = take_settle(&mut params);
                self.normalize_contract_query(&mut params)?;
                fill_settle(FUTURES_FUNDING_RATE, &settle)
            }
            "get_futures_contract_stats" => {
                let settle = take_settle(&mut params);
                self.normalize_contract_query(&mut params)?;
                fill_settle(FUTURES_CONTRACT_STATS, &settle)
            }
            "get_all_delivery_contracts" => {
                let settle = take_settle(&mut params);
                fill_settle(DELIVERY_CONTRACTS, &settle)
            }
            "get_spot_all_currency_pairs" => SPOT_CURRENCY_PAIRS.to_string(),
            "get_spot_order_book" => {
                self.normalize_currency_pair_query(&mut params)?;
                SPOT_ORDER_BOOK.to_string()
            }
            "get_spot_kline" => {
                self.normalize_currency_pair_query(&mut params)?;
                SPOT_CANDLESTICKS.to_string()
            }
            "get_spot_list_tickers" => {
                self.normalize_currency_pair_query(&mut params)?;
                SPOT_TICKERS.to_string()
            }
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Gate.io public method: {method_name}"
                )));
            }
        };
        self.request(HttpMethod::Get, api_path(&path), params, None, false)
            .await
    }

    pub(super) fn take_contract(&self, params: &mut Vec<(String, String)>) -> Result<String> {
        take_param(params, "contract")
            .or_else(|| take_param(params, "product_symbol"))
            .map(|value| self.exchange_symbol(&value))
            .transpose()?
            .ok_or_else(|| DcexError::InvalidInput("Gate.io contract is required.".to_string()))
    }
}

pub(super) fn take_param(params: &mut Vec<(String, String)>, key: &str) -> Option<String> {
    params
        .iter()
        .position(|(param_key, _)| param_key == key)
        .map(|index| params.remove(index).1)
}

pub(super) fn take_settle(params: &mut Vec<(String, String)>) -> String {
    take_param(params, "settle")
        .or_else(|| take_param(params, "ccy"))
        .unwrap_or_else(|| "usdt".to_string())
}

fn take_market_path(params: &mut Vec<(String, String)>) -> Result<String> {
    let market_path = take_param(params, "path").unwrap_or_else(|| "futures".to_string());
    match market_path.as_str() {
        "futures" | "delivery" => Ok(market_path),
        _ => Err(DcexError::InvalidInput(format!(
            "unsupported Gate.io market path: {market_path}"
        ))),
    }
}
