use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::BingxClient;
use super::endpoints::*;
use super::params::{
    push_optional_value, validate_enum, validate_time_range, validate_u64_range, BingxParams,
};

const KLINE_INTERVALS: &[&str] = &[
    "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M",
];

impl BingxClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = BingxParams::from_pairs(params);
        match method_name {
            "get_swap_instrument_info" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, &params)?;
                self.public_get(SWAP_INSTRUMENT_INFO, query).await
            }
            "get_spot_instrument_info" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, &params)?;
                self.public_get(SPOT_SYMBOLS, query).await
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
                self.public_get(SPOT_ORDERBOOK_V2, query).await
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
                self.public_get(SPOT_PUBLIC_TRADE, query).await
            }
            "get_kline" => self.kline_get(SWAP_KLINE, &params).await,
            "get_spot_kline" => self.kline_get(SPOT_KLINE, &params).await,
            "get_spot_kline_v2" => self.kline_get(SPOT_KLINE_V2, &params).await,
            "get_open_interest" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, &params)?;
                self.public_get(SWAP_OPEN_INTEREST, query).await
            }
            "get_mark_price_kline" => self.kline_get(SWAP_MARK_PRICE_KLINE, &params).await,
            "get_ticker" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, &params)?;
                self.public_get(SWAP_TICKER, query).await
            }
            "get_spot_ticker" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, &params)?;
                self.public_get(SPOT_TICKER, query).await
            }
            "get_spot_book_ticker" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, &params)?;
                self.public_get(SPOT_BOOK_TICKER, query).await
            }
            "get_spot_price_ticker" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, &params)?;
                self.public_get(SPOT_PRICE_TICKER, query).await
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
            if let Some(limit) = params.get("limit") {
                if !matches!(limit, "5" | "10" | "20" | "50" | "100" | "500" | "1000") {
                    return Err(DcexError::InvalidInput(format!(
                        "unsupported BingX swap orderbook limit: {limit}"
                    )));
                }
            }
        } else if path == SPOT_ORDERBOOK {
            validate_u64_range(params, "limit", 1, 1000)?;
        } else if path == SWAP_PUBLIC_TRADE {
            validate_u64_range(params, "limit", 1, 1000)?;
        }
        if let Some(type_) = type_ {
            query.push(("type".to_string(), type_.to_string()));
        }
        push_optional_value(&mut query, limit_key, params.get("limit"));
        self.public_get(path, query).await
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
