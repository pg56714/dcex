use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::MexcApi;
use super::client::MexcClient;
use super::endpoints::*;
use super::params::{
    MexcParams, add_pagination_defaults, require_one_identifier, require_paired, validate_enum,
    validate_u64_range,
};

const SPOT_KLINE_INTERVALS: &[&str] = &["1m", "5m", "15m", "30m", "60m", "4h", "1d", "1W", "1M"];
const CONTRACT_KLINE_INTERVALS: &[&str] = &[
    "Min1", "Min5", "Min15", "Min30", "Min60", "Hour4", "Hour8", "Day1", "Week1", "Month1",
];

impl MexcClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = MexcParams::from_pairs(params);
        if let Some(result) = self
            .stream_schema_request(method_name, &params, true)
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .wallet_schema_request(method_name, &params, true)
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .market_schema_request(method_name, &params, true)
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .account_schema_request(method_name, &params, true)
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .convert_schema_request(method_name, &params, true)
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self
            .subaccount_schema_request(method_name, &params, true)
            .await?
        {
            return Ok(result);
        }
        if let Some(result) = self.stp_schema_request(method_name, &params, true).await? {
            return Ok(result);
        }
        let (api, path, query) = match method_name {
            "ping" => {
                params.ensure_allowed(&[])?;
                (MexcApi::Spot, SPOT_PING.to_string(), Vec::new())
            }
            "get_spot_time" => {
                params.ensure_allowed(&[])?;
                (MexcApi::Spot, SPOT_TIME.to_string(), Vec::new())
            }
            "get_spot_default_symbols" => {
                params.ensure_allowed(&[])?;
                (MexcApi::Spot, SPOT_DEFAULT_SYMBOLS.to_string(), Vec::new())
            }
            "get_spot_exchange_info" => {
                params.ensure_allowed(&["product_symbol", "symbol", "symbols"])?;
                if params.get("symbols").is_some()
                    && (params.get("product_symbol").is_some() || params.get("symbol").is_some())
                {
                    return Err(DcexError::InvalidInput(
                        "MEXC exchangeInfo accepts either symbol or symbols, not both".to_string(),
                    ));
                }
                let mut query = params.into_inner();
                self.normalize_symbol_params(&mut query, "")?;
                (MexcApi::Spot, SPOT_EXCHANGE_INFO.to_string(), query)
            }
            "get_spot_orderbook" => {
                params.ensure_allowed(&["product_symbol", "symbol", "limit"])?;
                require_one_identifier(&params, &["product_symbol", "symbol"])?;
                validate_u64_range(&params, "limit", 1, 5_000)?;
                let mut query = params.into_inner();
                self.normalize_symbol_params(&mut query, "")?;
                (MexcApi::Spot, SPOT_ORDERBOOK.to_string(), query)
            }
            "get_spot_recent_trades" => {
                params.ensure_allowed(&["product_symbol", "symbol", "limit"])?;
                require_one_identifier(&params, &["product_symbol", "symbol"])?;
                validate_u64_range(&params, "limit", 1, 1_000)?;
                let mut query = params.into_inner();
                self.normalize_symbol_params(&mut query, "")?;
                (MexcApi::Spot, SPOT_RECENT_TRADES.to_string(), query)
            }
            "get_spot_agg_trades" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "startTime",
                    "endTime",
                    "limit",
                ])?;
                require_one_identifier(&params, &["product_symbol", "symbol"])?;
                require_paired(&params, "startTime", "endTime")?;
                validate_u64_range(&params, "limit", 1, 1_000)?;
                let mut query = params.into_inner();
                self.normalize_symbol_params(&mut query, "")?;
                (MexcApi::Spot, SPOT_AGG_TRADES.to_string(), query)
            }
            "get_spot_klines" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "interval",
                    "startTime",
                    "endTime",
                    "limit",
                ])?;
                require_one_identifier(&params, &["product_symbol", "symbol"])?;
                params.required("interval")?;
                validate_enum(&params, "interval", SPOT_KLINE_INTERVALS)?;
                validate_u64_range(&params, "limit", 1, 500)?;
                let mut query = params.into_inner();
                self.normalize_symbol_params(&mut query, "")?;
                (MexcApi::Spot, SPOT_KLINES.to_string(), query)
            }
            "get_spot_avg_price" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                require_one_identifier(&params, &["product_symbol", "symbol"])?;
                let mut query = params.into_inner();
                self.normalize_symbol_params(&mut query, "")?;
                (MexcApi::Spot, SPOT_AVG_PRICE.to_string(), query)
            }
            "get_spot_ticker_24hr" | "get_spot_ticker_price" | "get_spot_book_ticker" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let path = match method_name {
                    "get_spot_ticker_24hr" => SPOT_TICKER_24HR,
                    "get_spot_ticker_price" => SPOT_TICKER_PRICE,
                    _ => SPOT_BOOK_TICKER,
                };
                let mut query = params.into_inner();
                self.normalize_symbol_params(&mut query, "")?;
                (MexcApi::Spot, path.to_string(), query)
            }
            "get_contract_time" => {
                params.ensure_allowed(&[])?;
                (MexcApi::Contract, CONTRACT_PING.to_string(), Vec::new())
            }
            "get_contract_details" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = params.into_inner();
                self.normalize_symbol_params(&mut query, "_")?;
                (MexcApi::Contract, CONTRACT_DETAIL.to_string(), query)
            }
            "get_contract_ticker" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = params.into_inner();
                self.normalize_symbol_params(&mut query, "_")?;
                (MexcApi::Contract, CONTRACT_TICKER.to_string(), query)
            }
            "get_contract_depth" => {
                params.ensure_allowed(&["product_symbol", "symbol", "limit"])?;
                let mut query = params.into_inner();
                let symbol = self.take_symbol(&mut query, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/depth/{symbol}"),
                    query,
                )
            }
            "get_contract_depth_commits" => {
                params.ensure_allowed(&["product_symbol", "symbol", "limit"])?;
                params.required("limit")?;
                let mut query = params.into_inner();
                let symbol = self.take_symbol(&mut query, "_")?;
                let limit = super::client::take_param(&mut query, "limit").expect("validated");
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/depth_commits/{symbol}/{limit}"),
                    query,
                )
            }
            "get_contract_index_price" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = params.into_inner();
                let symbol = self.take_symbol(&mut query, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/index_price/{symbol}"),
                    query,
                )
            }
            "get_contract_fair_price" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = params.into_inner();
                let symbol = self.take_symbol(&mut query, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/fair_price/{symbol}"),
                    query,
                )
            }
            "get_contract_funding_rate" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = params.into_inner();
                let symbol = self.take_symbol(&mut query, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/funding_rate/{symbol}"),
                    query,
                )
            }
            "get_contract_kline"
            | "get_contract_index_price_kline"
            | "get_contract_fair_price_kline" => {
                params.ensure_allowed(&["product_symbol", "symbol", "interval", "start", "end"])?;
                validate_enum(&params, "interval", CONTRACT_KLINE_INTERVALS)?;
                let mut query = params.into_inner();
                if !query.iter().any(|(key, _)| key == "interval") {
                    query.push(("interval".to_string(), "Min1".to_string()));
                }
                let symbol = self.take_symbol(&mut query, "_")?;
                let prefix = match method_name {
                    "get_contract_kline" => "/api/v1/contract/kline",
                    "get_contract_index_price_kline" => "/api/v1/contract/kline/index_price",
                    _ => "/api/v1/contract/kline/fair_price",
                };
                (MexcApi::Contract, format!("{prefix}/{symbol}"), query)
            }
            "get_contract_deals" => {
                params.ensure_allowed(&["product_symbol", "symbol", "limit"])?;
                validate_u64_range(&params, "limit", 1, 100)?;
                let mut query = params.into_inner();
                let symbol = self.take_symbol(&mut query, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/deals/{symbol}"),
                    query,
                )
            }
            "get_contract_risk_reverse" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = params.into_inner();
                let symbol = self.take_symbol(&mut query, "_")?;
                (
                    MexcApi::Contract,
                    format!("/api/v1/contract/risk_reverse/{symbol}"),
                    query,
                )
            }
            "get_contract_risk_reverse_history" => {
                params.ensure_allowed(&["product_symbol", "symbol", "page_num", "page_size"])?;
                require_one_identifier(&params, &["product_symbol", "symbol"])?;
                validate_u64_range(&params, "page_num", 1, u64::MAX)?;
                validate_u64_range(&params, "page_size", 1, 100)?;
                let mut query = params.into_inner();
                add_pagination_defaults(&mut query);
                self.normalize_symbol_params(&mut query, "_")?;
                (
                    MexcApi::Contract,
                    CONTRACT_RISK_REVERSE_HISTORY.to_string(),
                    query,
                )
            }
            "get_contract_funding_rate_history" => {
                params.ensure_allowed(&["product_symbol", "symbol", "page_num", "page_size"])?;
                require_one_identifier(&params, &["product_symbol", "symbol"])?;
                validate_u64_range(&params, "page_num", 1, u64::MAX)?;
                validate_u64_range(&params, "page_size", 1, 1_000)?;
                let mut query = params.into_inner();
                add_pagination_defaults(&mut query);
                self.normalize_symbol_params(&mut query, "_")?;
                (
                    MexcApi::Contract,
                    CONTRACT_FUNDING_RATE_HISTORY.to_string(),
                    query,
                )
            }
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported MEXC public method: {method_name}"
                )));
            }
        };
        self.request(HttpMethod::Get, api, path, query, None, false)
            .await
    }
}

mod market_requests {
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::mexc::client::{MexcApi, MexcClient};
    use crate::exchanges::mexc::params::{MexcParams, validate_u64_range};
    use crate::http::HttpMethod;
    use crate::{DcexError, Result};
    impl MexcClient {
        pub(in crate::exchanges::mexc) async fn market_schema_request(
            &self,
            name: &str,
            p: &MexcParams,
            public: bool,
        ) -> Result<Option<ValidatedResponse>> {
            let (path, api, verb, signed, allowed, required): (
                &str,
                MexcApi,
                HttpMethod,
                bool,
                &[&str],
                &[&str],
            ) = match name {
                "get_spot_offline_symbols" => (
                    "/api/v3/symbol/offline",
                    MexcApi::Spot,
                    HttpMethod::Get,
                    false,
                    &[],
                    &[],
                ),
                "get_announcements" => (
                    "/api/v3/announcements",
                    MexcApi::Spot,
                    HttpMethod::Get,
                    false,
                    &["language", "page", "limit"],
                    &[],
                ),
                "get_contract_supported_currencies" => (
                    "/api/v1/contract/support_currencies",
                    MexcApi::Contract,
                    HttpMethod::Get,
                    false,
                    &[],
                    &[],
                ),
                _ => return Ok(None),
            };
            if public == signed {
                return Ok(None);
            }
            p.ensure_allowed(allowed)?;
            validate_u64_range(p, "recvWindow", 1, 60_000)?;
            let query = p.only(allowed);
            let unique: std::collections::BTreeSet<_> = query.iter().map(|(k, _)| k).collect();
            if unique.len() != query.len() {
                return Err(DcexError::InvalidInput("duplicate MEXC parameter".into()));
            }
            for key in required {
                if p.required(key)?.trim().is_empty() {
                    return Err(DcexError::InvalidInput(format!("{key} cannot be empty")));
                }
            }
            validate_u64_range(p, "page", 1, u64::MAX)?;
            validate_u64_range(
                p,
                "limit",
                1,
                if name == "get_announcements" {
                    100
                } else {
                    1000
                },
            )?;
            validate_u64_range(p, "startTime", 0, u64::MAX)?;
            validate_u64_range(p, "endTime", 0, u64::MAX)?;
            if let (Some(start), Some(end)) = (p.get("startTime"), p.get("endTime"))
                && start.parse::<u64>().unwrap() > end.parse::<u64>().unwrap()
            {
                return Err(DcexError::InvalidInput("startTime exceeds endTime".into()));
            }
            if name == "get_announcements"
                && p.get("limit")
                    .is_some_and(|n| n.parse::<u64>().is_ok_and(|n| n % 5 != 0))
            {
                return Err(DcexError::InvalidInput(
                    "announcement limit must be a multiple of 5".into(),
                ));
            }
            let path = path.to_string();
            Ok(Some(
                self.request(verb, api, path, query, None, signed).await?,
            ))
        }
    }
}
