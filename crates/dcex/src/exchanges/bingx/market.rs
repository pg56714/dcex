use crate::exchange::{ValidatedResponse, unix_timestamp_ms};
use crate::{DcexError, Result};

use super::client::BingxClient;
use super::endpoints::*;
use super::params::{
    BingxParams, push_optional_value, validate_enum, validate_time_range, validate_u64_range,
};

/// Public market paths whose official request tables mark `timestamp` as required.
/// Spot v2 depth, spot price ticker and spot book ticker do not list it.
const TIMESTAMP_REQUIRED_PATHS: &[&str] = &[
    SWAP_INSTRUMENT_INFO,
    SWAP_ORDERBOOK,
    SWAP_PUBLIC_TRADE,
    SWAP_KLINE,
    SWAP_TICKER,
    SWAP_PREMIUM_INDEX,
    SWAP_FUNDING_RATE,
    SWAP_BOOK_TICKER,
    SWAP_TRADING_RULES,
    SWAP_OPEN_INTEREST,
    SWAP_MARK_PRICE_KLINE,
    SPOT_SYMBOLS,
    SPOT_ORDERBOOK,
    SPOT_PUBLIC_TRADE,
    SPOT_KLINE_V2,
    SPOT_TICKER,
];

const KLINE_INTERVALS: &[&str] = &[
    "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M",
];

impl BingxClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        crate::exchanges::input_contracts::pairs("bingx", method_name, &params)?;
        let mut scoped = self.clone();
        scoped.symbol_product_type = Some(
            if method_name.contains("_spot_") || method_name.ends_with("_spot") {
                "spot"
            } else {
                "swap"
            },
        );
        scoped.public_request_scoped(method_name, params).await
    }

    async fn public_request_scoped(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = BingxParams::from_pairs(params);
        if let Some(response) = self.catalog_request(method_name, &params, true).await? {
            return Ok(response);
        }
        if let Some(response) = self.table_request(method_name, &params, true).await? {
            return Ok(response);
        }
        match method_name {
            "get_spot_server_time" => {
                params.ensure_allowed(&[])?;
                self.market_get("/openApi/spot/v1/server/time", vec![])
                    .await
            }
            "get_swap_instrument_info" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, &params)?;
                self.market_get(SWAP_INSTRUMENT_INFO, query).await
            }
            "get_spot_instrument_info" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, &params)?;
                self.market_get(SPOT_SYMBOLS, query).await
            }
            "get_orderbook" => self.depth_get(SWAP_ORDERBOOK, &params, "limit", None).await,
            "get_spot_orderbook" => self.depth_get(SPOT_ORDERBOOK, &params, "limit", None).await,
            "get_spot_orderbook_v2" => {
                params.ensure_allowed(&["product_symbol", "symbol", "limit", "depth", "type_"])?;
                let type_ = params.get("type_").unwrap_or("step0").to_string();
                validate_enum(
                    &params,
                    "type_",
                    &["step0", "step1", "step2", "step3", "step4", "step5"],
                )?;
                let depth = params
                    .get("depth")
                    .or_else(|| params.get("limit"))
                    .ok_or_else(|| {
                        DcexError::InvalidInput("missing required parameter: depth".to_string())
                    })?;
                depth
                    .parse::<u64>()
                    .ok()
                    .filter(|value| *value > 0)
                    .ok_or_else(|| {
                        DcexError::InvalidInput(
                            "BingX parameter depth must be a positive integer".to_string(),
                        )
                    })?;
                let mut query = Vec::new();
                self.push_required_spot_v2_depth_symbol(&mut query, &params)?;
                query.push(("depth".to_string(), depth.to_string()));
                query.push(("type".to_string(), type_));
                self.market_get(SPOT_ORDERBOOK_V2, query).await
            }
            "get_public_trades" => {
                self.depth_get(SWAP_PUBLIC_TRADE, &params, "limit", None)
                    .await
            }
            "get_spot_public_trades" => {
                params.ensure_allowed(&["product_symbol", "symbol", "limit"])?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, &params)?;
                validate_u64_range(&params, "limit", 1, 500)?;
                push_optional_value(&mut query, "limit", params.get("limit"));
                self.market_get(SPOT_PUBLIC_TRADE, query).await
            }
            "get_kline" => self.kline_get(SWAP_KLINE, &params).await,
            // BingX only documents the v2 spot kline route; keep both names on it.
            "get_spot_kline" | "get_spot_kline_v2" => self.kline_get(SPOT_KLINE_V2, &params).await,
            "get_open_interest" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, &params)?;
                self.market_get(SWAP_OPEN_INTEREST, query).await
            }
            "get_mark_price_kline" => self.kline_get(SWAP_MARK_PRICE_KLINE, &params).await,
            "get_ticker" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, &params)?;
                self.market_get(SWAP_TICKER, query).await
            }
            "get_swap_premium_index" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, &params)?;
                self.market_get(SWAP_PREMIUM_INDEX, query).await
            }
            "get_swap_funding_rate" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "start_time",
                    "end_time",
                    "limit",
                ])?;
                validate_time_range(&params, "start_time", "end_time", None)?;
                validate_u64_range(&params, "limit", 1, 1000)?;
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, &params)?;
                push_optional_value(&mut query, "startTime", params.get("start_time"));
                push_optional_value(&mut query, "endTime", params.get("end_time"));
                push_optional_value(&mut query, "limit", params.get("limit"));
                self.market_get(SWAP_FUNDING_RATE, query).await
            }
            "get_swap_book_ticker" | "get_swap_trading_rules" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, &params)?;
                let path = if method_name == "get_swap_book_ticker" {
                    SWAP_BOOK_TICKER
                } else {
                    SWAP_TRADING_RULES
                };
                self.market_get(path, query).await
            }
            "get_spot_ticker" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, &params)?;
                self.market_get(SPOT_TICKER, query).await
            }
            "get_spot_book_ticker" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, &params)?;
                self.market_get(SPOT_BOOK_TICKER, query).await
            }
            "get_spot_price_ticker" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, &params)?;
                self.market_get(SPOT_PRICE_TICKER, query).await
            }
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported BingX public method: {method_name}"
            ))),
        }
    }

    async fn depth_get(
        &self,
        path: &str,
        params: &BingxParams,
        limit_key: &str,
        type_: Option<&str>,
    ) -> Result<ValidatedResponse> {
        params.ensure_allowed(&["product_symbol", "symbol", "limit"])?;
        let mut query = Vec::new();
        self.push_required_symbol(&mut query, params)?;
        if path == SWAP_ORDERBOOK {
            if let Some(limit) = params.get("limit")
                && !matches!(limit, "5" | "10" | "20" | "50" | "100" | "500" | "1000")
            {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported BingX swap orderbook limit: {limit}"
                )));
            }
        } else if matches!(path, SPOT_ORDERBOOK | SWAP_PUBLIC_TRADE) {
            validate_u64_range(params, "limit", 1, 1000)?;
        }
        if let Some(type_) = type_ {
            query.push(("type".to_string(), type_.to_string()));
        }
        push_optional_value(&mut query, limit_key, params.get("limit"));
        self.market_get(path, query).await
    }

    async fn kline_get(&self, path: &str, params: &BingxParams) -> Result<ValidatedResponse> {
        params.ensure_allowed(&[
            "product_symbol",
            "symbol",
            "interval",
            "start_time",
            "end_time",
            "limit",
        ])?;
        validate_enum(params, "interval", KLINE_INTERVALS)?;
        validate_time_range(params, "start_time", "end_time", None)?;
        validate_u64_range(params, "limit", 1, 1440)?;
        let mut query = Vec::new();
        self.push_required_symbol(&mut query, params)?;
        query.push((
            "interval".to_string(),
            params.required("interval")?.to_string(),
        ));
        push_optional_value(&mut query, "startTime", params.get("start_time"));
        push_optional_value(&mut query, "endTime", params.get("end_time"));
        push_optional_value(&mut query, "limit", params.get("limit"));
        self.market_get(path, query).await
    }

    /// Public GET that adds `timestamp` where the BingX docs mark it required.
    async fn market_get(
        &self,
        path: &str,
        mut query: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        if TIMESTAMP_REQUIRED_PATHS.contains(&path) {
            push_timestamp(&mut query)?;
        }
        self.public_get(path, query).await
    }

    fn push_required_spot_v2_depth_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &BingxParams,
    ) -> Result<()> {
        let product_symbol = params.required_any(&["product_symbol", "symbol"])?;
        let symbol = self.exchange_symbol(product_symbol)?.replace('-', "_");
        query.push(("symbol".to_string(), symbol));
        Ok(())
    }
}

/// BingX documents `timestamp` as a required query field on these public endpoints.
fn push_timestamp(query: &mut Vec<(String, String)>) -> Result<()> {
    query.push(("timestamp".to_string(), unix_timestamp_ms()?.to_string()));
    Ok(())
}
