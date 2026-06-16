use super::client::BybitClient;
use super::endpoints::*;
use super::params::{bybit_timeframe, is_canonical_product_symbol};
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

impl BybitClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let (path, params) = match method_name {
            "get_instruments_info" => (
                INSTRUMENTS_INFO,
                self.normalize_symbol_params(params, true)?,
            ),
            "get_kline" => (KLINE, self.normalize_kline_params(params)?),
            "get_orderbook" => (ORDERBOOK, self.normalize_symbol_params(params, true)?),
            "get_tickers" => (TICKERS, self.normalize_symbol_params(params, true)?),
            "get_funding_rate_history" => (
                FUNDING_RATE_HISTORY,
                self.normalize_symbol_params(params, true)?,
            ),
            "get_public_trade_history" => (
                PUBLIC_TRADE_HISTORY,
                self.normalize_symbol_params(params, true)?,
            ),
            "get_open_interest" => (OPEN_INTEREST, self.normalize_symbol_params(params, true)?),
            "get_long_short_ratio" => (
                LONG_SHORT_RATIO,
                self.normalize_symbol_params(params, true)?,
            ),
            "get_historical_volatility" => (HISTORICAL_VOLATILITY, params),
            "get_insurance_pool" => (INSURANCE_POOL, params),
            "get_delivery_price" => (DELIVERY_PRICE, self.normalize_symbol_params(params, true)?),
            "get_order_price_limit" => (
                ORDER_PRICE_LIMIT,
                self.normalize_symbol_params(params, true)?,
            ),
            "get_adl_alert" => (ADL_ALERT, self.normalize_symbol_params(params, true)?),
            "get_risk_limit" => (RISK_LIMIT, self.normalize_symbol_params(params, false)?),
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Bybit public method: {method_name}"
                )));
            }
        };
        self.request(HttpMethod::Get, path, params, None, false)
            .await
    }

    fn normalize_symbol_params(
        &self,
        params: Vec<(String, String)>,
        include_product_category: bool,
    ) -> Result<Vec<(String, String)>> {
        let mut output = Vec::with_capacity(params.len() + 1);
        let mut product_symbol = None;
        let mut explicit_category = None;

        for (key, value) in params {
            match key.as_str() {
                "product_symbol" => product_symbol = Some(value),
                "category" => explicit_category = Some(value),
                "symbol" if is_canonical_product_symbol(&value) => {
                    output.push(("symbol".to_string(), self.exchange_symbol(&value)?));
                    if include_product_category {
                        explicit_category =
                            Some(self.category_for_product_symbol(&value, "linear")?);
                    }
                }
                _ => output.push((key, value)),
            }
        }

        if let Some(product_symbol) = product_symbol {
            output.push(("symbol".to_string(), self.exchange_symbol(&product_symbol)?));
            if include_product_category {
                explicit_category =
                    Some(self.category_for_product_symbol(&product_symbol, "linear")?);
            }
        }
        if let Some(category) = explicit_category {
            output.retain(|(key, _)| key != "category");
            output.insert(0, ("category".to_string(), category));
        }
        Ok(output)
    }

    fn normalize_kline_params(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<Vec<(String, String)>> {
        let normalized = self.normalize_symbol_params(params, true)?;
        normalized
            .into_iter()
            .map(|(key, value)| {
                if key == "interval" {
                    Ok((key, bybit_timeframe(&value)?.to_string()))
                } else if key == "startTime" {
                    Ok(("start".to_string(), value))
                } else {
                    Ok((key, value))
                }
            })
            .collect()
    }
}
