use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::OkxClient;
use super::endpoints::*;
use super::params::{normalize_inst_id_query, OkxParams};

impl OkxClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let raw = OkxParams::from_pairs(params);
        let (required, allowed): (&[&str], &[&str]) = match method_name {
            "get_candles_ticks" => (
                &["product_symbol"],
                &[
                    "product_symbol",
                    "instId",
                    "bar",
                    "after",
                    "before",
                    "limit",
                    "adjust",
                ],
            ),
            "get_orderbook" => (&["product_symbol"], &["product_symbol", "instId", "sz"]),
            "get_tickers" => (&["instType"], &["instType", "instFamily"]),
            "get_public_trades" => (&["product_symbol"], &["product_symbol", "instId", "limit"]),
            "get_public_instruments" => (
                &["instType"],
                &[
                    "instType",
                    "seriesId",
                    "instFamily",
                    "product_symbol",
                    "instId",
                ],
            ),
            "get_funding_rate" => (&["product_symbol"], &["product_symbol", "instId"]),
            "get_funding_rate_history" => (
                &["product_symbol"],
                &["product_symbol", "instId", "before", "after", "limit"],
            ),
            "get_open_interest" => (
                &["instType"],
                &["instType", "instFamily", "product_symbol", "instId"],
            ),
            "get_position_tiers" => (
                &["instType", "tdMode"],
                &[
                    "instType",
                    "tdMode",
                    "instFamily",
                    "product_symbol",
                    "instId",
                    "ccy",
                    "tier",
                ],
            ),
            "get_trading_data_support_coin" => (&[], &[]),
            "get_taker_volume" => (&["ccy"], &["ccy", "instType", "begin", "end", "period"]),
            "get_contract_taker_volume" => (
                &["product_symbol"],
                &[
                    "product_symbol",
                    "instId",
                    "period",
                    "unit",
                    "end",
                    "begin",
                    "limit",
                ],
            ),
            "get_long_short_ratio" => (&["ccy"], &["ccy", "period", "end", "begin"]),
            "get_contract_long_short_ratio"
            | "get_top_trader_long_short_account_ratio"
            | "get_top_trader_long_short_position_ratio"
            | "get_contract_open_interest_history" => (
                &["product_symbol"],
                &[
                    "product_symbol",
                    "instId",
                    "period",
                    "end",
                    "begin",
                    "limit",
                ],
            ),
            "get_contracts_open_interest_and_volume" => {
                (&["ccy"], &["ccy", "period", "end", "begin"])
            }
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported OKX public method: {method_name}"
                )));
            }
        };
        for key in required {
            if *key == "product_symbol" {
                if raw.get("product_symbol").is_none() && raw.get("instId").is_none() {
                    return Err(DcexError::InvalidInput(
                        "one of product_symbol, instId is required".to_string(),
                    ));
                }
            } else {
                raw.required(key)?;
            }
        }
        let mut params = raw.only(allowed);
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
                normalize_position_tiers_query(&mut params);
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
            _ => unreachable!("public method was validated above"),
        };
        self.request(HttpMethod::Get, path, params, None, false)
            .await
    }
}

fn normalize_position_tiers_query(params: &mut Vec<(String, String)>) {
    normalize_inst_id_query(params);
    if !params.iter().any(|(key, value)| {
        key == "instType" && matches!(value.as_str(), "SWAP" | "FUTURES" | "OPTION")
    }) {
        return;
    }
    if params.iter().any(|(key, _)| key == "instFamily") {
        return;
    }
    let Some(inst_id) = params
        .iter()
        .find(|(key, _)| key == "instId")
        .map(|(_, value)| value)
    else {
        return;
    };
    let mut parts = inst_id.split('-');
    if let (Some(base), Some(quote)) = (parts.next(), parts.next()) {
        params.push(("instFamily".to_string(), format!("{base}-{quote}")));
    }
}
