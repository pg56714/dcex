use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::{KucoinClient, KucoinMarket};
use super::endpoints::*;
use super::params::{
    normalize_futures_timeframe, normalize_spot_timeframe, take_param, validate_enum,
    validate_time_range, validate_u64_range, KucoinParams,
};

impl KucoinClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        mut params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.validate_public_params(method_name, &params)?;
        let (market, path, signed) = match method_name {
            "get_spot_instrument_info" => {
                (KucoinMarket::Spot, SPOT_INSTRUMENT_INFO.to_string(), false)
            }
            "get_spot_ticker" => {
                self.normalize_symbol_query(&mut params, false)?;
                (KucoinMarket::Spot, SPOT_TICKER.to_string(), false)
            }
            "get_spot_all_tickers" => (KucoinMarket::Spot, SPOT_ALL_TICKERS.to_string(), false),
            "get_spot_orderbook" => {
                self.normalize_symbol_query(&mut params, false)?;
                (KucoinMarket::Spot, SPOT_ORDERBOOK.to_string(), false)
            }
            "get_spot_public_trades" => {
                self.normalize_symbol_query(&mut params, false)?;
                (KucoinMarket::Spot, SPOT_PUBLIC_TRADES.to_string(), false)
            }
            "get_spot_kline" => {
                self.normalize_symbol_query(&mut params, false)?;
                normalize_spot_timeframe(&mut params)?;
                (KucoinMarket::Spot, SPOT_KLINE.to_string(), false)
            }
            "get_futures_contracts" => {
                (KucoinMarket::Futures, FUTURES_CONTRACTS.to_string(), false)
            }
            "get_futures_contract" => {
                let symbol = if let Some(symbol) = take_param(&mut params, "symbol") {
                    self.exchange_symbol(&symbol, true)?
                } else if let Some(product_symbol) = take_param(&mut params, "product_symbol") {
                    self.exchange_symbol(&product_symbol, true)?
                } else {
                    return Err(DcexError::InvalidInput(
                        "KuCoin symbol is required.".to_string(),
                    ));
                };
                (
                    KucoinMarket::Futures,
                    format!("/api/v1/contracts/{symbol}"),
                    false,
                )
            }
            "get_futures_ticker" => {
                self.normalize_symbol_query(&mut params, true)?;
                (KucoinMarket::Futures, FUTURES_TICKER.to_string(), false)
            }
            "get_futures_orderbook" => {
                self.normalize_symbol_query(&mut params, true)?;
                let path = take_param(&mut params, "depth")
                    .map(|depth| format!("/api/v1/level2/depth{depth}"))
                    .unwrap_or_else(|| FUTURES_ORDERBOOK.to_string());
                (KucoinMarket::Futures, path, false)
            }
            "get_futures_public_trades" => {
                self.normalize_symbol_query(&mut params, true)?;
                (
                    KucoinMarket::Futures,
                    FUTURES_PUBLIC_TRADES.to_string(),
                    false,
                )
            }
            "get_futures_kline" => {
                self.normalize_symbol_query(&mut params, true)?;
                normalize_futures_timeframe(&mut params)?;
                (KucoinMarket::Futures, FUTURES_KLINE.to_string(), false)
            }
            "get_futures_open_interest" => {
                self.normalize_symbol_list_query(&mut params, true, 10)?;
                (KucoinMarket::Spot, FUTURES_OPEN_INTEREST.to_string(), false)
            }
            "get_uta_position_tiers" => {
                self.normalize_symbol_list_query(&mut params, true, 10)?;
                (KucoinMarket::Spot, UTA_POSITION_TIERS.to_string(), false)
            }
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported KuCoin public method: {method_name}"
                )));
            }
        };
        self.request(HttpMethod::Get, market, path, params, None, signed)
            .await
    }

    fn normalize_symbol_query(&self, params: &mut [(String, String)], futures: bool) -> Result<()> {
        for (key, value) in params.iter_mut() {
            if matches!(key.as_str(), "product_symbol" | "symbol") {
                *key = "symbol".to_string();
                *value = self.exchange_symbol(value, futures)?;
            }
        }
        Ok(())
    }

    fn normalize_symbol_list_query(
        &self,
        params: &mut [(String, String)],
        futures: bool,
        maximum: usize,
    ) -> Result<()> {
        for (key, value) in params.iter_mut() {
            if !matches!(key.as_str(), "product_symbol" | "symbol") {
                continue;
            }
            *key = "symbol".to_string();
            let raw_symbols = if let Ok(Value::Array(values)) = serde_json::from_str::<Value>(value)
            {
                values
                    .iter()
                    .map(|value| {
                        value.as_str().map(str::to_string).ok_or_else(|| {
                            DcexError::InvalidInput(
                                "KuCoin symbol list must contain strings".to_string(),
                            )
                        })
                    })
                    .collect::<Result<Vec<_>>>()?
            } else {
                value
                    .split(',')
                    .map(str::trim)
                    .map(str::to_string)
                    .collect()
            };
            if raw_symbols.is_empty()
                || raw_symbols.len() > maximum
                || raw_symbols.iter().any(|symbol| symbol.is_empty())
            {
                return Err(DcexError::InvalidInput(format!(
                    "KuCoin symbol list must contain between 1 and {maximum} symbols"
                )));
            }
            *value = raw_symbols
                .iter()
                .map(|symbol| self.exchange_symbol(symbol, futures))
                .collect::<Result<Vec<_>>>()?
                .join(",");
        }
        Ok(())
    }

    fn validate_public_params(
        &self,
        method_name: &str,
        raw_params: &[(String, String)],
    ) -> Result<()> {
        let params = KucoinParams::from_pairs(raw_params.to_vec());
        match method_name {
            "get_spot_instrument_info" => params.ensure_allowed(&["market"]),
            "get_spot_ticker" | "get_spot_orderbook" | "get_spot_public_trades" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                params.required_any(&["product_symbol", "symbol"])?;
                Ok(())
            }
            "get_spot_all_tickers" | "get_futures_contracts" => params.ensure_allowed(&[]),
            "get_spot_kline" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "timeframe",
                    "type",
                    "startAt",
                    "endAt",
                ])?;
                params.required_any(&["product_symbol", "symbol"])?;
                params.required_any(&["timeframe", "type"])?;
                validate_time_range(&params, "startAt", "endAt", None)
            }
            "get_futures_contract" | "get_futures_ticker" | "get_futures_public_trades" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                params.required_any(&["product_symbol", "symbol"])?;
                Ok(())
            }
            "get_futures_orderbook" => {
                params.ensure_allowed(&["product_symbol", "symbol", "depth"])?;
                if params.get("depth").is_some() {
                    params.required_any(&["product_symbol", "symbol"])?;
                    validate_enum(&params, "depth", &["20", "100"])?;
                }
                Ok(())
            }
            "get_futures_kline" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "timeframe",
                    "granularity",
                    "from",
                    "to",
                ])?;
                params.required_any(&["product_symbol", "symbol"])?;
                params.required_any(&["timeframe", "granularity"])?;
                validate_time_range(&params, "from", "to", None)
            }
            "get_futures_open_interest" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "interval",
                    "startAt",
                    "endAt",
                    "pageSize",
                ])?;
                validate_enum(
                    &params,
                    "interval",
                    &["5min", "15min", "30min", "1hour", "4hour", "1day"],
                )?;
                validate_u64_range(&params, "pageSize", 1, 200)?;
                validate_time_range(&params, "startAt", "endAt", None)?;
                let historical = ["startAt", "endAt", "pageSize"]
                    .iter()
                    .any(|key| params.get(key).is_some());
                if historical && params.get("interval").is_none() {
                    return Err(DcexError::InvalidInput(
                        "KuCoin open-interest history requires interval".to_string(),
                    ));
                }
                if params.get("interval").is_some() {
                    let symbols = params.required_any(&["product_symbol", "symbol"])?;
                    let count = parse_symbol_count(symbols)?;
                    if count != 1 {
                        return Err(DcexError::InvalidInput(
                            "KuCoin historical open interest requires exactly one symbol"
                                .to_string(),
                        ));
                    }
                }
                Ok(())
            }
            "get_uta_position_tiers" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "tradeType",
                    "currency",
                    "marginMode",
                    "data",
                    "accountType",
                ])?;
                params.required("tradeType")?;
                params.required("marginMode")?;
                params.required("data")?;
                params.required("accountType")?;
                validate_enum(&params, "tradeType", &["MARGIN", "FUTURES"])?;
                validate_enum(&params, "marginMode", &["CROSS"])?;
                validate_enum(&params, "data", &["BORROW", "RISK_LIMIT"])?;
                match params.required("data")? {
                    "BORROW" => validate_comma_list(params.required("currency")?, "currency", 10)?,
                    "RISK_LIMIT" => validate_comma_list(
                        params.required_any(&["product_symbol", "symbol"])?,
                        "symbol",
                        10,
                    )?,
                    _ => unreachable!(),
                }
                Ok(())
            }
            _ => Ok(()),
        }
    }
}

fn parse_symbol_count(value: &str) -> Result<usize> {
    if let Ok(Value::Array(values)) = serde_json::from_str::<Value>(value) {
        if values.iter().all(Value::is_string) {
            return Ok(values.len());
        }
        return Err(DcexError::InvalidInput(
            "KuCoin symbol list must contain strings".to_string(),
        ));
    }
    Ok(value.split(',').count())
}

fn validate_comma_list(value: &str, label: &str, maximum: usize) -> Result<()> {
    let count = parse_symbol_count(value)?;
    if (1..=maximum).contains(&count) && value.split(',').all(|entry| !entry.trim().is_empty()) {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "KuCoin {label} list must contain between 1 and {maximum} entries"
    )))
}
