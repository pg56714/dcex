use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::BitmexClient;
use super::endpoints::*;
use super::params::{push_optional, BitmexParams};

impl BitmexClient {
    pub async fn get_instrument_info(
        &self,
        product_symbol: Option<&str>,
        filter: Option<&str>,
        count: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = Vec::new();
        if let Some(product_symbol) = product_symbol {
            params.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
        }
        push_optional(&mut params, "filter", filter);
        push_optional(&mut params, "count", count);
        let path = if params.is_empty() {
            ACTIVE_INSTRUMENTS
        } else {
            INSTRUMENT_INFO
        };
        self.public_get(path, params).await
    }

    pub async fn get_orderbook(
        &self,
        product_symbol: &str,
        depth: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut params = vec![("symbol".to_string(), self.exchange_symbol(product_symbol)?)];
        push_optional(&mut params, "depth", depth);
        self.public_get(ORDERBOOK, params).await
    }

    pub async fn get_trades(&self, mut params: Vec<(String, String)>) -> Result<ValidatedResponse> {
        self.normalize_symbol_params(&mut params)?;
        self.public_get(TRADE, params).await
    }

    pub async fn get_ticker(&self, mut params: Vec<(String, String)>) -> Result<ValidatedResponse> {
        self.normalize_symbol_params(&mut params)?;
        self.public_get(TICKER, params).await
    }

    pub async fn get_kline(&self, mut params: Vec<(String, String)>) -> Result<ValidatedResponse> {
        self.normalize_symbol_params(&mut params)?;
        self.public_get(KLINE, params).await
    }

    pub async fn get_funding(
        &self,
        mut params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.normalize_symbol_params(&mut params)?;
        self.public_get(FUNDING, params).await
    }

    pub async fn get_liquidations(
        &self,
        mut params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        self.normalize_symbol_params(&mut params)?;
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
                self.get_instrument_info(
                    public_params.get("product_symbol"),
                    public_params.get("filter"),
                    public_params.get("count"),
                )
                .await
            }
            "get_orderbook" => {
                self.get_orderbook(
                    public_params.required("product_symbol")?,
                    public_params.get("depth"),
                )
                .await
            }
            "get_trades" => {
                self.get_trades(public_params.only(&[
                    "symbol",
                    "product_symbol",
                    "filter",
                    "columns",
                    "count",
                    "start",
                    "reverse",
                    "startTime",
                    "endTime",
                ]))
                .await
            }
            "get_ticker" => {
                self.get_ticker(public_params.only(&[
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
                ]))
                .await
            }
            "get_kline" => {
                self.get_kline(public_params.only(&[
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
                ]))
                .await
            }
            "get_funding" => {
                self.get_funding(public_params.only(&[
                    "symbol",
                    "product_symbol",
                    "filter",
                    "columns",
                    "count",
                    "start",
                    "reverse",
                    "startTime",
                    "endTime",
                ]))
                .await
            }
            "get_liquidations" => {
                self.get_liquidations(public_params.only(&[
                    "symbol",
                    "product_symbol",
                    "filter",
                    "columns",
                    "count",
                    "start",
                    "reverse",
                    "startTime",
                    "endTime",
                ]))
                .await
            }
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported BitMEX public method: {method_name}"
            ))),
        }
    }
}
