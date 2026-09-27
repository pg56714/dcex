use super::client::BybitClient;
use super::endpoints::*;
use super::params::{BybitParams, bybit_timeframe, is_canonical_product_symbol};
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

impl BybitClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        if let Some(result) = self
            .risk_request(method_name, &BybitParams::from_pairs(params.clone()), true)
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .spread_public_request(method_name, &BybitParams::from_pairs(params.clone()))
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .launchpool_public_request(method_name, &BybitParams::from_pairs(params.clone()))
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .rwa_earn_public_request(method_name, &BybitParams::from_pairs(params.clone()))
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .byusdt_public_request(method_name, &BybitParams::from_pairs(params.clone()))
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .hold_to_earn_public_request(method_name, &BybitParams::from_pairs(params.clone()))
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .fixed_earn_public_request(method_name, &BybitParams::from_pairs(params.clone()))
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .liquidity_mining_public_request(method_name, &BybitParams::from_pairs(params.clone()))
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .advanced_earn_public_request(method_name, &BybitParams::from_pairs(params.clone()))
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .earn_public_request(method_name, &BybitParams::from_pairs(params.clone()))
            .await?
        {
            return Ok(result);
        }
        let (path, params) = match method_name {
            "get_instruments_info" => (
                INSTRUMENTS_INFO,
                self.normalize_symbol_params(params, true)?,
            ),
            "get_kline" => (KLINE, self.normalize_kline_params(params)?),
            "get_mark_price_kline" | "get_index_price_kline" | "get_premium_index_price_kline" => {
                let normalized = self.normalize_kline_params(params)?;
                let values = BybitParams::from_pairs(normalized.clone());
                values.required("symbol")?;
                values.required("interval")?;
                let category = values.get("category").unwrap_or("linear");
                let allowed: &[&str] = match method_name {
                    "get_mark_price_kline" => &["linear", "inverse", "option"],
                    "get_index_price_kline" => &["linear", "inverse"],
                    _ => &["linear"],
                };
                if !allowed.contains(&category) {
                    return Err(DcexError::InvalidInput(
                        "category is not supported by this price kline endpoint".into(),
                    ));
                }
                for key in ["start", "end", "limit"] {
                    if let Some(value) = values.get(key) {
                        value
                            .parse::<u64>()
                            .map_err(|_| DcexError::InvalidInput(format!("invalid {key}")))?;
                    }
                }
                if let Some(limit) = values.get("limit") {
                    let limit: u64 = limit.parse().unwrap();
                    let max = if category == "option" { 500 } else { 1000 };
                    if limit == 0 || limit > max {
                        return Err(DcexError::InvalidInput(format!("limit must be 1..={max}")));
                    }
                }
                if let (Some(start), Some(end)) = (values.get("start"), values.get("end")) {
                    if start.parse::<u64>().unwrap() > end.parse::<u64>().unwrap() {
                        return Err(DcexError::InvalidInput("start must not exceed end".into()));
                    }
                }
                let path = match method_name {
                    "get_mark_price_kline" => "/v5/market/mark-price-kline",
                    "get_index_price_kline" => "/v5/market/index-price-kline",
                    _ => "/v5/market/premium-index-price-kline",
                };
                (path, normalized)
            }

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
            "get_adl_alert" => {
                let mut params = self.normalize_symbol_params(params, false)?;
                params.retain(|(key, _)| key != "category");
                (ADL_ALERT, params)
            }
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
                } else if key == "endTime" {
                    Ok(("end".to_string(), value))
                } else {
                    Ok((key, value))
                }
            })
            .collect()
    }
}

#[cfg(test)]
mod tests {
    use std::time::Duration;

    use super::*;

    fn client() -> BybitClient {
        BybitClient::public(5_000, false, Duration::from_secs(1)).expect("client")
    }

    #[test]
    fn kline_maps_official_start_and_end_names() {
        let params = client()
            .normalize_kline_params(vec![
                ("product_symbol".to_string(), "BTC-USDT-SPOT".to_string()),
                ("interval".to_string(), "1m".to_string()),
                ("startTime".to_string(), "100".to_string()),
                ("endTime".to_string(), "200".to_string()),
            ])
            .expect("params");

        assert!(params.contains(&("start".to_string(), "100".to_string())));
        assert!(params.contains(&("end".to_string(), "200".to_string())));
        assert!(
            !params
                .iter()
                .any(|(key, _)| key == "startTime" || key == "endTime")
        );
    }
}
