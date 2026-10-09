use super::client::BybitClient;
use super::endpoints::*;
use super::params::{BybitParams, bybit_timeframe};
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

impl BybitClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        crate::exchanges::input_contracts::pairs("bybit", method_name, &params)?;
        if let Some(result) = self
            .field_schema_request(method_name, &BybitParams::from_pairs(params.clone()), true)
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .table_request(method_name, &BybitParams::from_pairs(params.clone()), true)
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
        // Official query fields per endpoint, plus the canonical `product_symbol`.
        let official: Option<&[&str]> = match method_name {
            "get_instruments_info" => Some(&[
                "category",
                "symbol",
                "symbolType",
                "status",
                "baseCoin",
                "limit",
                "cursor",
            ]),
            "get_kline"
            | "get_mark_price_kline"
            | "get_index_price_kline"
            | "get_premium_index_price_kline" => {
                Some(&["category", "symbol", "interval", "start", "end", "limit"])
            }
            "get_orderbook" => Some(&["category", "symbol", "limit"]),
            "get_tickers" => Some(&["category", "symbol", "baseCoin", "expDate"]),
            "get_funding_rate_history" => {
                Some(&["category", "symbol", "startTime", "endTime", "limit"])
            }
            "get_public_trade_history" => {
                Some(&["category", "symbol", "baseCoin", "optionType", "limit"])
            }
            "get_open_interest" => Some(&[
                "category",
                "symbol",
                "intervalTime",
                "startTime",
                "endTime",
                "limit",
                "cursor",
            ]),
            "get_long_short_ratio" => Some(&[
                "category",
                "symbol",
                "period",
                "startTime",
                "endTime",
                "limit",
                "cursor",
            ]),
            "get_historical_volatility" => Some(&[
                "category",
                "baseCoin",
                "quoteCoin",
                "period",
                "startTime",
                "endTime",
            ]),
            "get_insurance_pool" => Some(&["coin"]),
            "get_delivery_price" => Some(&[
                "category",
                "symbol",
                "baseCoin",
                "settleCoin",
                "limit",
                "cursor",
            ]),
            "get_order_price_limit" => Some(&["category", "symbol"]),
            "get_adl_alert" => Some(&["symbol"]),
            "get_risk_limit" => Some(&["category", "symbol", "cursor"]),
            _ => None,
        };
        if let Some(official) = official {
            let mut allowed = official.to_vec();
            if official.contains(&"symbol") {
                allowed.push("product_symbol");
            }
            BybitParams::from_pairs(params.clone()).ensure_allowed(&allowed)?;
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
                if let (Some(start), Some(end)) = (values.get("start"), values.get("end"))
                    && start.parse::<u64>().unwrap() > end.parse::<u64>().unwrap()
                {
                    return Err(DcexError::InvalidInput("start must not exceed end".into()));
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
            "get_risk_limit" => (RISK_LIMIT, self.normalize_risk_limit_params(params)?),
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
        let category = params
            .iter()
            .find(|(key, _)| key == "category")
            .map(|(_, value)| value.as_str());
        let input = params
            .iter()
            .find(|(key, _)| key == "product_symbol")
            .or_else(|| params.iter().find(|(key, _)| key == "symbol"));
        let resolved = input
            .map(|(_, symbol)| self.symbol_category(symbol, category))
            .transpose()?;
        let mut output: Vec<_> = params
            .into_iter()
            .filter(|(key, _)| key != "symbol" && key != "product_symbol")
            .collect();
        if let Some((symbol, category)) = resolved {
            output.push(("symbol".into(), symbol));
            if include_product_category {
                output.retain(|(key, _)| key != "category");
                output.insert(0, ("category".into(), category));
            }
        } else if include_product_category && !output.iter().any(|(key, _)| key == "category") {
            output.insert(0, ("category".into(), "linear".into()));
        }
        Ok(output)
    }

    /// `/v5/market/risk-limit` only serves `category=linear|inverse`.
    fn normalize_risk_limit_params(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<Vec<(String, String)>> {
        const ALLOWED: [&str; 2] = ["linear", "inverse"];
        let explicit = params.iter().any(|(key, _)| key == "category");
        let symbol = params
            .iter()
            .find(|(key, _)| key == "product_symbol")
            .or_else(|| params.iter().find(|(key, _)| key == "symbol"))
            .map(|(_, value)| value.clone());
        let output = match symbol {
            Some(symbol) if !explicit => {
                let (native, category) = self.symbol_category_within(&symbol, &ALLOWED)?;
                let mut output: Vec<_> = params
                    .into_iter()
                    .filter(|(key, _)| key != "symbol" && key != "product_symbol")
                    .collect();
                output.insert(0, ("category".into(), category));
                output.push(("symbol".into(), native));
                output
            }
            _ => self.normalize_symbol_params(params, true)?,
        };
        if let Some((_, category)) = output.iter().find(|(key, _)| key == "category")
            && !ALLOWED.contains(&category.as_str())
        {
            return Err(DcexError::InvalidInput(format!(
                "Bybit get_risk_limit supports category linear or inverse only, got {category}"
            )));
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

    fn table_client() -> BybitClient {
        let row = |product: &str, native: &str, kind: &str, exchange_type: &str| {
            crate::product_table::MarketInfo {
                exchange: "bybit".into(),
                exchange_symbol: native.into(),
                product_symbol: product.into(),
                product_type: kind.into(),
                exchange_type: exchange_type.into(),
                ..Default::default()
            }
        };
        client().with_product_table(crate::product_table::ProductTable::new(vec![
            row("BTC-USDT-SPOT", "BTCUSDT", "spot", "spot"),
            row("BTC-USDT-SWAP", "BTCUSDT", "swap", "linear"),
            row("BTC-USD-SWAP", "BTCUSD", "swap", "inverse"),
        ]))
    }

    fn pairs(items: &[(&str, &str)]) -> Vec<(String, String)> {
        items
            .iter()
            .map(|(key, value)| ((*key).to_string(), (*value).to_string()))
            .collect()
    }

    #[test]
    fn risk_limit_category_is_limited_to_linear_and_inverse() {
        let table = table_client();
        for (input, expected) in [
            (
                vec![("symbol", "BTCUSDT")],
                vec![("category", "linear"), ("symbol", "BTCUSDT")],
            ),
            (
                vec![("product_symbol", "BTC-USD-SWAP")],
                vec![("category", "inverse"), ("symbol", "BTCUSD")],
            ),
            (
                vec![("cursor", "c")],
                vec![("category", "linear"), ("cursor", "c")],
            ),
        ] {
            assert_eq!(
                table
                    .normalize_risk_limit_params(pairs(&input))
                    .expect("params"),
                pairs(&expected)
            );
        }
        for client in [&table, &client()] {
            let error = client
                .normalize_risk_limit_params(pairs(&[("product_symbol", "BTC-USDT-SPOT")]))
                .expect_err("spot is unsupported");
            assert!(error.to_string().contains("BTC-USDT-SPOT"), "{error}");
            assert!(
                client
                    .normalize_risk_limit_params(pairs(&[("category", "spot")]))
                    .is_err()
            );
        }
    }

    #[test]
    fn ambiguity_hint_only_for_multiple_candidates() {
        let table = table_client();
        let ambiguous = table
            .symbol_category("BTCUSDT", None)
            .expect_err("ambiguous");
        assert!(
            ambiguous.to_string().contains("pass category="),
            "{ambiguous}"
        );
        let missing = table.symbol_category("ETHUSDT", None).expect_err("missing");
        assert!(!missing.to_string().contains("pass category="), "{missing}");
    }

    #[test]
    fn kline_takes_only_the_official_start_and_end_names() {
        let params = client()
            .normalize_kline_params(vec![
                ("product_symbol".to_string(), "BTC-USDT-SPOT".to_string()),
                ("interval".to_string(), "1m".to_string()),
                ("start".to_string(), "100".to_string()),
                ("end".to_string(), "200".to_string()),
            ])
            .expect("params");
        assert!(params.contains(&("start".to_string(), "100".to_string())));
        assert!(params.contains(&("end".to_string(), "200".to_string())));
        assert!(params.contains(&("interval".to_string(), "1".to_string())));
        let client = client();
        let error = crate::http::block_on(async move {
            client
                .public_request(
                    "get_kline",
                    vec![
                        ("product_symbol".to_string(), "BTC-USDT-SPOT".to_string()),
                        ("interval".to_string(), "1m".to_string()),
                        ("startTime".to_string(), "100".to_string()),
                    ],
                )
                .await
        })
        .expect_err("startTime is not a kline field");
        assert!(
            error
                .to_string()
                .contains("unsupported Bybit parameter: startTime")
        );
    }
}
