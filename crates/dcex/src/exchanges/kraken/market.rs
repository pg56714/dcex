use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::{KrakenAuth, KrakenClient};
use super::endpoints::*;
use super::params::{take_param, KrakenParams};

impl KrakenClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let mut params = KrakenParams::from_pairs(params).into_inner();
        if matches!(
            method_name,
            "get_spot_spread"
                | "get_spot_ticker"
                | "get_spot_orderbook"
                | "get_spot_public_trades"
                | "get_spot_kline"
        ) && !params.iter().any(|(key, _)| key == "asset_class")
        {
            let inferred_asset_class = params
                .iter()
                .find(|(key, _)| key == "product_symbol")
                .map(|(_, value)| self.spot_asset_class(value))
                .transpose()?
                .flatten();
            if let Some(asset_class) = inferred_asset_class {
                params.push(("asset_class".to_string(), asset_class));
            }
        }
        let (auth, path) = match method_name {
            "get_server_time" => (KrakenAuth::Spot, SPOT_SERVER_TIME.to_string()),
            "get_spot_system_status" => (KrakenAuth::Spot, SPOT_SYSTEM_STATUS.to_string()),
            "get_spot_assets" => (KrakenAuth::Spot, SPOT_ASSETS.to_string()),
            "get_spot_asset_pairs" => (KrakenAuth::Spot, SPOT_ASSET_PAIRS.to_string()),
            "get_spot_spread" => {
                self.normalize_symbol_query(&mut params, "pair", "")?;
                require_query_param(&params, "pair")?;
                (KrakenAuth::Spot, SPOT_SPREAD.to_string())
            }
            "get_spot_ticker" => {
                self.normalize_symbol_query(&mut params, "pair", "")?;
                (KrakenAuth::Spot, SPOT_TICKER.to_string())
            }
            "get_spot_orderbook" => {
                self.normalize_symbol_query(&mut params, "pair", "")?;
                require_query_param(&params, "pair")?;
                (KrakenAuth::Spot, SPOT_ORDERBOOK.to_string())
            }
            "get_spot_public_trades" => {
                self.normalize_symbol_query(&mut params, "pair", "")?;
                require_query_param(&params, "pair")?;
                (KrakenAuth::Spot, SPOT_PUBLIC_TRADES.to_string())
            }
            "get_spot_kline" => {
                self.normalize_symbol_query(&mut params, "pair", "")?;
                require_query_param(&params, "pair")?;
                (KrakenAuth::Spot, SPOT_OHLC.to_string())
            }
            "get_futures_instruments" => (KrakenAuth::Futures, FUTURES_INSTRUMENTS.to_string()),
            "get_futures_tickers" => {
                self.normalize_symbol_query(&mut params, "symbol", "PF_")?;
                (KrakenAuth::Futures, FUTURES_TICKERS.to_string())
            }
            "get_futures_orderbook" => {
                self.normalize_symbol_query(&mut params, "symbol", "PF_")?;
                require_query_param(&params, "symbol")?;
                (KrakenAuth::Futures, FUTURES_ORDERBOOK.to_string())
            }
            "get_futures_public_trades" => {
                self.normalize_symbol_query(&mut params, "symbol", "PF_")?;
                require_query_param(&params, "symbol")?;
                (KrakenAuth::Futures, FUTURES_PUBLIC_TRADES.to_string())
            }
            "get_futures_kline" => {
                let tick_type =
                    take_param(&mut params, "tick_type").unwrap_or_else(|| "trade".to_string());
                let symbol = self.take_symbol(&mut params, "PF_")?;
                let resolution = take_param(&mut params, "timeframe")
                    .ok_or_else(|| DcexError::InvalidInput("timeframe is required.".to_string()))?;
                validate_candle_path(&tick_type, &resolution)?;
                (
                    KrakenAuth::Futures,
                    format!("{FUTURES_CANDLES}/{tick_type}/{symbol}/{resolution}"),
                )
            }
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Kraken public method: {method_name}"
                )));
            }
        };

        let allowed_params: &[&str] = match method_name {
            "get_server_time" | "get_spot_system_status" => &[],
            "get_spot_assets" => &["asset", "aclass", "assetVersion"],
            "get_spot_asset_pairs" => &[
                "assetVersion",
                "pair",
                "aclass_base",
                "info",
                "country_code",
                "execution_venue",
            ],
            "get_spot_spread" => &["pair", "assetVersion", "since", "asset_class"],
            "get_spot_ticker" => &["pair", "assetVersion", "asset_class"],
            "get_spot_orderbook" => &["pair", "assetVersion", "count", "asset_class"],
            "get_spot_public_trades" => &["pair", "assetVersion", "since", "count", "asset_class"],
            "get_spot_kline" => &["pair", "assetVersion", "interval", "since", "asset_class"],
            "get_futures_instruments" => &["contractType", "expired"],
            "get_futures_tickers" => &["contractType", "symbol"],
            "get_futures_orderbook" => &["symbol"],
            "get_futures_public_trades" => &["symbol", "lastTime"],
            "get_futures_kline" => &["from", "from_", "to", "count"],
            _ => unreachable!("method was validated above"),
        };
        params.retain(|(key, _)| allowed_params.contains(&key.as_str()));
        for (key, _) in &mut params {
            if key == "from_" {
                *key = "from".to_string();
            }
        }
        validate_public_params(method_name, &params)?;

        self.request(HttpMethod::Get, auth, path, params, None, false)
            .await
    }

    fn take_symbol(
        &self,
        params: &mut Vec<(String, String)>,
        futures_prefix: &str,
    ) -> Result<String> {
        if let Some(symbol) = take_param(params, "symbol") {
            return self.exchange_symbol(&symbol, futures_prefix);
        }
        if let Some(product_symbol) = take_param(params, "product_symbol") {
            return self.exchange_symbol(&product_symbol, futures_prefix);
        }
        Err(DcexError::InvalidInput(
            "Kraken symbol is required.".to_string(),
        ))
    }

    fn normalize_symbol_query(
        &self,
        params: &mut [(String, String)],
        target_key: &str,
        futures_prefix: &str,
    ) -> Result<()> {
        for (key, value) in params.iter_mut() {
            if key == "product_symbol" {
                *key = target_key.to_string();
                *value = self.exchange_symbol(value, futures_prefix)?;
            } else if key == target_key {
                *value = self.exchange_symbol(value, futures_prefix)?;
            }
        }
        Ok(())
    }
}

fn require_query_param(params: &[(String, String)], key: &str) -> Result<()> {
    if params.iter().any(|(candidate, _)| candidate == key) {
        return Ok(());
    }
    Err(DcexError::InvalidInput(format!(
        "missing required parameter: {key}"
    )))
}

fn validate_candle_path(tick_type: &str, resolution: &str) -> Result<()> {
    if !matches!(tick_type, "spot" | "mark" | "trade") {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Kraken Futures candle tick type: {tick_type}"
        )));
    }
    if !matches!(
        resolution,
        "1m" | "5m" | "15m" | "30m" | "1h" | "4h" | "12h" | "1d" | "1w"
    ) {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Kraken Futures candle resolution: {resolution}"
        )));
    }
    Ok(())
}

fn validate_public_params(method_name: &str, params: &[(String, String)]) -> Result<()> {
    validate_optional_values(params, "assetVersion", &["1"])?;
    match method_name {
        "get_spot_assets" => {
            validate_optional_values(params, "aclass", &["currency", "tokenized_asset"])?;
        }
        "get_spot_asset_pairs" => {
            validate_optional_values(params, "aclass_base", &["currency", "tokenized_asset"])?;
            validate_optional_values(params, "info", &["info", "leverage", "fees", "margin"])?;
            validate_optional_values(
                params,
                "execution_venue",
                &["international", "bitnomial_exchange"],
            )?;
        }
        "get_spot_ticker" => {
            validate_optional_values(params, "asset_class", &["forex", "tokenized_asset"])?;
        }
        "get_spot_orderbook" => {
            validate_optional_values(params, "asset_class", &["tokenized_asset"])?;
            validate_optional_range(params, "count", 1, 500)?;
        }
        "get_spot_public_trades" => {
            validate_optional_values(params, "asset_class", &["tokenized_asset"])?;
            validate_optional_range(params, "count", 1, 1_000)?;
        }
        "get_spot_kline" => {
            validate_optional_values(params, "asset_class", &["tokenized_asset"])?;
            validate_optional_values(
                params,
                "interval",
                &["1", "5", "15", "30", "60", "240", "1440", "10080", "21600"],
            )?;
        }
        "get_spot_spread" => {
            validate_optional_values(params, "asset_class", &["tokenized_asset"])?;
        }
        _ => {}
    }
    Ok(())
}

fn validate_optional_values(
    params: &[(String, String)],
    key: &str,
    allowed: &[&str],
) -> Result<()> {
    for (_, value) in params.iter().filter(|(candidate, _)| candidate == key) {
        if !allowed.contains(&value.as_str()) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Kraken {key}: {value}"
            )));
        }
    }
    Ok(())
}

fn validate_optional_range(
    params: &[(String, String)],
    key: &str,
    minimum: u32,
    maximum: u32,
) -> Result<()> {
    for (_, value) in params.iter().filter(|(candidate, _)| candidate == key) {
        let value = value.parse::<u32>().map_err(|_| {
            DcexError::InvalidInput(format!("Kraken {key} must be an integer: {value}"))
        })?;
        if !(minimum..=maximum).contains(&value) {
            return Err(DcexError::InvalidInput(format!(
                "Kraken {key} must be between {minimum} and {maximum}."
            )));
        }
    }
    Ok(())
}
