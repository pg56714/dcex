use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::BitmexClient;
use super::endpoints::*;
use super::params::{
    push_optional, BitmexBucketParams, BitmexInstrumentInfoParams, BitmexOrderbookParams,
    BitmexParams, BitmexTableParams,
};

impl BitmexClient {
    pub async fn get_instrument_info(&self) -> Result<ValidatedResponse> {
        self.get_instrument_info_with(BitmexInstrumentInfoParams::default())
            .await
    }

    pub async fn get_instrument_info_with(
        &self,
        request: BitmexInstrumentInfoParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = request.product_symbol {
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        }
        push_optional(&mut params, "filter", request.filter);
        push_optional(&mut params, "count", request.count);
        let path = if params.is_empty() {
            ACTIVE_INSTRUMENTS
        } else {
            INSTRUMENT_INFO
        };
        self.public_get(path, params).await
    }

    pub async fn get_orderbook(&self, product_symbol: &str) -> Result<ValidatedResponse> {
        self.get_orderbook_with(product_symbol, BitmexOrderbookParams::default())
            .await
    }

    pub async fn get_orderbook_with(
        &self,
        product_symbol: &str,
        request: BitmexOrderbookParams<'_>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        push_optional(&mut params, "depth", request.depth);
        self.public_get(ORDERBOOK, params).await
    }

    pub async fn get_trades(&self) -> Result<ValidatedResponse> {
        self.get_trades_with(BitmexTableParams::default()).await
    }

    pub async fn get_trades_with(
        &self,
        request: BitmexTableParams<'_>,
    ) -> Result<ValidatedResponse> {
        let params = self.table_params(request)?;
        self.public_get(TRADE, params).await
    }

    pub async fn get_ticker(&self) -> Result<ValidatedResponse> {
        self.get_ticker_with(BitmexBucketParams::default()).await
    }

    pub async fn get_ticker_with(
        &self,
        request: BitmexBucketParams<'_>,
    ) -> Result<ValidatedResponse> {
        let params = self.bucket_params(request)?;
        self.public_get(TICKER, params).await
    }

    pub async fn get_kline(&self) -> Result<ValidatedResponse> {
        self.get_kline_with(BitmexBucketParams::default()).await
    }

    pub async fn get_kline_with(
        &self,
        request: BitmexBucketParams<'_>,
    ) -> Result<ValidatedResponse> {
        let params = self.bucket_params(request)?;
        self.public_get(KLINE, params).await
    }

    pub async fn get_funding(&self) -> Result<ValidatedResponse> {
        self.get_funding_with(BitmexTableParams::default()).await
    }

    pub async fn get_funding_with(
        &self,
        request: BitmexTableParams<'_>,
    ) -> Result<ValidatedResponse> {
        let params = self.table_params(request)?;
        self.public_get(FUNDING, params).await
    }

    pub async fn get_liquidations(&self) -> Result<ValidatedResponse> {
        self.get_liquidations_with(BitmexTableParams::default())
            .await
    }

    pub async fn get_liquidations_with(
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
                self.get_instrument_info_with(BitmexInstrumentInfoParams {
                    product_symbol: public_params.get("product_symbol"),
                    filter: public_params.get("filter"),
                    count: public_params.get("count"),
                })
                .await
            }
            "get_orderbook" => {
                self.get_orderbook_with(
                    public_params.required("product_symbol")?,
                    BitmexOrderbookParams {
                        depth: public_params.get("depth"),
                    },
                )
                .await
            }
            "get_trades" => {
                self.get_trades_with(BitmexTableParams {
                    product_symbol: public_params.get("product_symbol"),
                    symbol: public_params.get("symbol"),
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
            "get_ticker" => {
                self.get_ticker_with(BitmexBucketParams {
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
                })
                .await
            }
            "get_kline" => {
                self.get_kline_with(BitmexBucketParams {
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
                })
                .await
            }
            "get_funding" => {
                self.get_funding_with(BitmexTableParams {
                    product_symbol: public_params.get("product_symbol"),
                    symbol: public_params.get("symbol"),
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
            "get_liquidations" => {
                self.get_liquidations_with(BitmexTableParams {
                    product_symbol: public_params.get("product_symbol"),
                    symbol: public_params.get("symbol"),
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
        Ok(params)
    }
}
