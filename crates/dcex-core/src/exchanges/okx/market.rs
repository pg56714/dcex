use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::OkxClient;
use super::endpoints::*;
use super::params::normalize_inst_id_query;

impl OkxClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        mut params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let path = match method_name {
            "get_candles_ticks" => {
                normalize_inst_id_query(&mut params);
                MARKET_CANDLES
            }
            "get_orderbook" => {
                normalize_inst_id_query(&mut params);
                MARKET_ORDERBOOK
            }
            "get_tickers" => MARKET_TICKERS,
            "get_public_trades" => {
                normalize_inst_id_query(&mut params);
                MARKET_PUBLIC_TRADES
            }
            "get_public_instruments" => {
                normalize_inst_id_query(&mut params);
                PUBLIC_INSTRUMENTS
            }
            "get_funding_rate" => {
                normalize_inst_id_query(&mut params);
                PUBLIC_FUNDING_RATE
            }
            "get_funding_rate_history" => {
                normalize_inst_id_query(&mut params);
                PUBLIC_FUNDING_RATE_HISTORY
            }
            "get_open_interest" => {
                normalize_inst_id_query(&mut params);
                PUBLIC_OPEN_INTEREST
            }
            "get_position_tiers" => {
                normalize_inst_id_query(&mut params);
                PUBLIC_POSITION_TIERS
            }
            "get_trading_data_support_coin" => PUBLIC_TRADING_DATA_SUPPORT_COIN,
            "get_taker_volume" => PUBLIC_TAKER_VOLUME,
            "get_contract_taker_volume" => {
                normalize_inst_id_query(&mut params);
                PUBLIC_CONTRACT_TAKER_VOLUME
            }
            "get_long_short_ratio" => PUBLIC_LONG_SHORT_RATIO,
            "get_contract_long_short_ratio" => {
                normalize_inst_id_query(&mut params);
                PUBLIC_CONTRACT_LONG_SHORT_RATIO
            }
            "get_top_trader_long_short_account_ratio" => {
                normalize_inst_id_query(&mut params);
                PUBLIC_TOP_TRADER_LONG_SHORT_ACCOUNT_RATIO
            }
            "get_top_trader_long_short_position_ratio" => {
                normalize_inst_id_query(&mut params);
                PUBLIC_TOP_TRADER_LONG_SHORT_POSITION_RATIO
            }
            "get_contracts_open_interest_and_volume" => PUBLIC_CONTRACTS_OPEN_INTEREST_VOLUME,
            "get_contract_open_interest_history" => {
                normalize_inst_id_query(&mut params);
                PUBLIC_CONTRACT_OPEN_INTEREST_HISTORY
            }
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported OKX public method: {method_name}"
                )));
            }
        };
        self.request(HttpMethod::Get, path, params, None, false)
            .await
    }
}
