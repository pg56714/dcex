use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::BitmexClient;
use super::endpoints::*;
use super::params::{
    push_optional, require_at_most_one, validate_bool, validate_enum, validate_json_object,
    validate_u64_range, BitmexBucketParams, BitmexInstrumentInfoParams, BitmexOrderbookParams,
    BitmexParams, BitmexTableParams,
};

const POOLS: &[&str] = &["Primary", "Secondary", "Aggregated"];
const BIN_SIZES: &[&str] = &["1m", "5m", "1h", "1d"];

impl BitmexClient {
    pub fn get_instrument_info(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(self, "get_instrument_info", Vec::new())
    }

    pub(super) async fn send_get_instrument_info(
        &self,
        request: BitmexInstrumentInfoParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = request.product_symbol {
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        }
        push_optional(&mut params, "filter", request.filter);
        push_optional(&mut params, "columns", request.columns);
        push_optional(&mut params, "count", request.count);
        push_optional(&mut params, "start", request.start);
        push_optional(&mut params, "reverse", request.reverse);
        push_optional(&mut params, "startTime", request.start_time);
        push_optional(&mut params, "endTime", request.end_time);
        let path = if params.is_empty() {
            ACTIVE_INSTRUMENTS
        } else {
            INSTRUMENT_INFO
        };
        self.public_get(path, params).await
    }

    pub fn get_orderbook(
        &self,
        product_symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_orderbook",
            vec![("product_symbol".to_string(), product_symbol.to_string())],
        )
    }

    pub(super) async fn send_get_orderbook(
        &self,
        product_symbol: &str,
        request: BitmexOrderbookParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        push_optional(&mut params, "depth", request.depth);
        self.public_get(ORDERBOOK, params).await
    }

    pub fn get_trades(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(self, "get_trades", Vec::new())
    }

    pub(super) async fn send_get_trades(
        &self,
        request: BitmexTableParams<'_>,
    ) -> Result<ValidatedResponse> {
        let params = self.table_params(request)?;
        self.public_get(TRADE, params).await
    }

    pub fn get_ticker(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(self, "get_ticker", Vec::new())
    }

    pub(super) async fn send_get_ticker(
        &self,
        request: BitmexBucketParams<'_>,
    ) -> Result<ValidatedResponse> {
        let params = self.bucket_params(request)?;
        self.public_get(TICKER, params).await
    }

    pub fn get_kline(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(self, "get_kline", Vec::new())
    }

    pub(super) async fn send_get_kline(
        &self,
        request: BitmexBucketParams<'_>,
    ) -> Result<ValidatedResponse> {
        let params = self.bucket_params(request)?;
        self.public_get(KLINE, params).await
    }

    pub fn get_funding(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(self, "get_funding", Vec::new())
    }

    pub(super) async fn send_get_funding(
        &self,
        request: BitmexTableParams<'_>,
    ) -> Result<ValidatedResponse> {
        let params = self.table_params(request)?;
        self.public_get(FUNDING, params).await
    }

    pub fn get_liquidations(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(self, "get_liquidations", Vec::new())
    }

    pub(super) async fn send_get_liquidations(
        &self,
        request: BitmexTableParams<'_>,
    ) -> Result<ValidatedResponse> {
        let params = self.table_params(request)?;
        self.public_get(LIQUIDATION, params).await
    }

    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let public_params = BitmexParams::from_pairs(params);
        match method_name {
            "get_instrument_info" => {
                public_params.ensure_allowed(&[
                    "product_symbol",
                    "filter",
                    "columns",
                    "count",
                    "start",
                    "reverse",
                    "startTime",
                    "endTime",
                ])?;
                validate_json_object(&public_params, "filter")?;
                validate_u64_range(&public_params, "count", 1, i32::MAX as u64)?;
                validate_u64_range(&public_params, "start", 0, i32::MAX as u64)?;
                validate_bool(&public_params, "reverse")?;
                self.send_get_instrument_info(BitmexInstrumentInfoParams {
                    product_symbol: public_params.get("product_symbol"),
                    filter: public_params.get("filter"),
                    columns: public_params.get("columns"),
                    count: public_params.get("count"),
                    start: public_params.get("start"),
                    reverse: public_params.get("reverse"),
                    start_time: public_params.get("startTime"),
                    end_time: public_params.get("endTime"),
                })
                .await
            }
            "get_orderbook" => {
                public_params.ensure_allowed(&["product_symbol", "depth"])?;
                validate_u64_range(&public_params, "depth", 0, u32::MAX as u64)?;
                self.send_get_orderbook(
                    public_params.required("product_symbol")?,
                    BitmexOrderbookParams {
                        depth: public_params.get("depth"),
                    },
                )
                .await
            }
            "get_trades" => {
                validate_table_request(
                    &public_params,
                    &[
                        "product_symbol",
                        "symbol",
                        "filter",
                        "columns",
                        "count",
                        "start",
                        "reverse",
                        "startTime",
                        "endTime",
                        "pool",
                    ],
                    true,
                )?;
                self.send_get_trades(BitmexTableParams {
                    product_symbol: public_params.get("product_symbol"),
                    symbol: public_params.get("symbol"),
                    filter: public_params.get("filter"),
                    columns: public_params.get("columns"),
                    count: public_params.get("count"),
                    start: public_params.get("start"),
                    reverse: public_params.get("reverse"),
                    start_time: public_params.get("startTime"),
                    end_time: public_params.get("endTime"),
                    pool: public_params.get("pool"),
                })
                .await
            }
            "get_ticker" => {
                validate_bucket_request(&public_params)?;
                self.send_get_ticker(BitmexBucketParams {
                    bin_size: public_params.get("binSize"),
                    partial: public_params.get("partial"),
                    symbol: public_params.get("symbol"),
                    filter: public_params.get("filter"),
                    columns: public_params.get("columns"),
                    count: public_params.get("count"),
                    start: public_params.get("start"),
                    reverse: public_params.get("reverse"),
                    start_time: public_params.get("startTime"),
                    end_time: public_params.get("endTime"),
                    pool: public_params.get("pool"),
                })
                .await
            }
            "get_kline" => {
                validate_bucket_request(&public_params)?;
                self.send_get_kline(BitmexBucketParams {
                    bin_size: public_params.get("binSize"),
                    partial: public_params.get("partial"),
                    symbol: public_params.get("symbol"),
                    filter: public_params.get("filter"),
                    columns: public_params.get("columns"),
                    count: public_params.get("count"),
                    start: public_params.get("start"),
                    reverse: public_params.get("reverse"),
                    start_time: public_params.get("startTime"),
                    end_time: public_params.get("endTime"),
                    pool: public_params.get("pool"),
                })
                .await
            }
            "get_funding" => {
                validate_table_request(
                    &public_params,
                    &[
                        "product_symbol",
                        "symbol",
                        "filter",
                        "columns",
                        "count",
                        "start",
                        "reverse",
                        "startTime",
                        "endTime",
                    ],
                    false,
                )?;
                self.send_get_funding(BitmexTableParams {
                    product_symbol: public_params.get("product_symbol"),
                    symbol: public_params.get("symbol"),
                    filter: public_params.get("filter"),
                    columns: public_params.get("columns"),
                    count: public_params.get("count"),
                    start: public_params.get("start"),
                    reverse: public_params.get("reverse"),
                    start_time: public_params.get("startTime"),
                    end_time: public_params.get("endTime"),
                    pool: None,
                })
                .await
            }
            "get_liquidations" => {
                validate_table_request(
                    &public_params,
                    &[
                        "product_symbol",
                        "symbol",
                        "filter",
                        "columns",
                        "count",
                        "start",
                        "reverse",
                    ],
                    false,
                )?;
                self.send_get_liquidations(BitmexTableParams {
                    product_symbol: public_params.get("product_symbol"),
                    symbol: public_params.get("symbol"),
                    filter: public_params.get("filter"),
                    columns: public_params.get("columns"),
                    count: public_params.get("count"),
                    start: public_params.get("start"),
                    reverse: public_params.get("reverse"),
                    start_time: None,
                    end_time: None,
                    pool: None,
                })
                .await
            }
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported BitMEX public method: {method_name}"
            ))),
        }
    }

    fn table_params(&self, request: BitmexTableParams<'_>) -> Result<Vec<(String, String)>> {
        let mut params = Vec::new();
        if let Some(product_symbol) = request.product_symbol {
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        } else if let Some(symbol) = request.symbol {
            params.push(("symbol".to_string(), self.exchange_symbol(symbol)?));
        }
        push_optional(&mut params, "filter", request.filter);
        push_optional(&mut params, "columns", request.columns);
        push_optional(&mut params, "count", request.count);
        push_optional(&mut params, "start", request.start);
        push_optional(&mut params, "reverse", request.reverse);
        push_optional(&mut params, "startTime", request.start_time);
        push_optional(&mut params, "endTime", request.end_time);
        push_optional(&mut params, "pool", request.pool);
        Ok(params)
    }

    fn bucket_params(&self, request: BitmexBucketParams<'_>) -> Result<Vec<(String, String)>> {
        let mut params = Vec::new();
        push_optional(&mut params, "binSize", request.bin_size);
        push_optional(&mut params, "partial", request.partial);
        if let Some(symbol) = request.symbol {
            params.push(("symbol".to_string(), self.exchange_symbol(symbol)?));
        }
        push_optional(&mut params, "filter", request.filter);
        push_optional(&mut params, "columns", request.columns);
        push_optional(&mut params, "count", request.count);
        push_optional(&mut params, "start", request.start);
        push_optional(&mut params, "reverse", request.reverse);
        push_optional(&mut params, "startTime", request.start_time);
        push_optional(&mut params, "endTime", request.end_time);
        push_optional(&mut params, "pool", request.pool);
        Ok(params)
    }
}

fn validate_table_request(params: &BitmexParams, allowed: &[&str], allow_pool: bool) -> Result<()> {
    params.ensure_allowed(allowed)?;
    require_at_most_one(params, &["product_symbol", "symbol"])?;
    validate_json_object(params, "filter")?;
    validate_u64_range(params, "count", 1, 500)?;
    validate_u64_range(params, "start", 0, i32::MAX as u64)?;
    validate_bool(params, "reverse")?;
    if allow_pool {
        validate_enum(params, "pool", POOLS)?;
    }
    Ok(())
}

fn validate_bucket_request(params: &BitmexParams) -> Result<()> {
    params.ensure_allowed(&[
        "binSize",
        "partial",
        "symbol",
        "filter",
        "columns",
        "count",
        "start",
        "reverse",
        "startTime",
        "endTime",
        "pool",
    ])?;
    validate_enum(params, "binSize", BIN_SIZES)?;
    validate_bool(params, "partial")?;
    validate_json_object(params, "filter")?;
    validate_u64_range(params, "count", 1, 500)?;
    validate_u64_range(params, "start", 0, i32::MAX as u64)?;
    validate_bool(params, "reverse")?;
    validate_enum(params, "pool", POOLS)?;
    Ok(())
}
