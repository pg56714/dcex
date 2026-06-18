use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::BingxClient;
use super::endpoints::*;
use super::params::{push_optional_value, BingxParams};

impl BingxClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = BingxParams::from_pairs(params);
        match method_name {
            "get_swap_instrument_info" => {
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, &params)?;
                self.public_get(SWAP_INSTRUMENT_INFO, query).await
            }
            "get_spot_instrument_info" => {
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, &params)?;
                self.public_get(SPOT_SYMBOLS, query).await
            }
            "get_orderbook" => self.depth_get(SWAP_ORDERBOOK, &params, "limit", None).await,
            "get_spot_orderbook" => self.depth_get(SPOT_ORDERBOOK, &params, "limit", None).await,
            "get_spot_orderbook_v2" => {
                let type_ = params.get("type_").unwrap_or("step0").to_string();
                self.depth_get(SPOT_ORDERBOOK_V2, &params, "depth", Some(&type_))
                    .await
            }
            "get_public_trades" => {
                self.depth_get(SWAP_PUBLIC_TRADE, &params, "limit", None)
                    .await
            }
            "get_spot_public_trades" => {
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, &params)?;
                self.public_get(SPOT_PUBLIC_TRADE, query).await
            }
            "get_kline" => self.kline_get(SWAP_KLINE, &params).await,
            "get_spot_kline" => self.kline_get(SPOT_KLINE, &params).await,
            "get_spot_kline_v2" => self.kline_get(SPOT_KLINE_V2, &params).await,
            "get_open_interest" => {
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, &params)?;
                self.public_get(SWAP_OPEN_INTEREST, query).await
            }
            "get_mark_price_kline" => self.kline_get(SWAP_MARK_PRICE_KLINE, &params).await,
            "get_ticker" => {
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, &params)?;
                self.public_get(SWAP_TICKER, query).await
            }
            "get_spot_ticker" => {
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, &params)?;
                self.public_get(SPOT_TICKER, query).await
            }
            "get_spot_book_ticker" => {
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, &params)?;
                self.public_get(SPOT_BOOK_TICKER, query).await
            }
            "get_spot_price_ticker" => {
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
        let mut query = Vec::new();
        self.push_required_symbol(&mut query, params)?;
        if let Some(type_) = type_ {
            query.push(("type".to_string(), type_.to_string()));
        }
        push_optional_value(&mut query, limit_key, params.get("limit"));
        self.public_get(path, query).await
    }

    async fn kline_get(&self, path: &str, params: &BingxParams) -> Result<ValidatedResponse> {
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
}
