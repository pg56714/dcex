use super::client::BinanceMarket;
use crate::{DcexError, Result};

#[derive(Clone, Debug, Default)]
pub struct BinanceAccountTradesParams<'a> {
    pub order_id: Option<&'a str>,
    pub start_time: Option<&'a str>,
    pub end_time: Option<&'a str>,
    pub from_id: Option<&'a str>,
    pub limit: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct BinanceAlgoOrderLookupParams<'a> {
    pub algo_id: Option<&'a str>,
    pub client_algo_id: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct BinanceAllFuturesAlgoOrdersParams<'a> {
    pub algo_id: Option<&'a str>,
    pub start_time: Option<&'a str>,
    pub end_time: Option<&'a str>,
    pub limit: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct BinanceAllOpenOrdersParams<'a> {
    pub product_symbol: Option<&'a str>,
    pub market_type: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct BinanceAllOrdersParams<'a> {
    pub order_id: Option<&'a str>,
    pub start_time: Option<&'a str>,
    pub end_time: Option<&'a str>,
    pub limit: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct BinanceFundingRateParams<'a> {
    pub product_symbol: Option<&'a str>,
    pub start_time: Option<u64>,
    pub end_time: Option<u64>,
    pub limit: Option<u64>,
}

#[derive(Clone, Debug, Default)]
pub struct BinanceFundingWalletParams<'a> {
    pub asset: Option<&'a str>,
    pub need_btc_valuation: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct BinanceFuturesBasisParams {
    pub limit: Option<u64>,
    pub start_time: Option<u64>,
    pub end_time: Option<u64>,
}

#[derive(Clone, Debug, Default)]
pub struct BinanceFuturesPeriodParams {
    pub limit: Option<u64>,
    pub start_time: Option<u64>,
    pub end_time: Option<u64>,
}

#[derive(Clone, Debug, Default)]
pub struct BinanceIncomeHistoryParams<'a> {
    pub product_symbol: Option<&'a str>,
    pub income_type: Option<&'a str>,
    pub start_time: Option<u64>,
    pub end_time: Option<u64>,
    pub page: Option<u64>,
    pub limit: Option<u64>,
}

#[derive(Clone, Debug, Default)]
pub struct BinanceKlinesParams {
    pub start_time: Option<u64>,
    pub limit: Option<u64>,
}

#[derive(Clone, Debug, Default)]
pub struct BinanceLimitParams {
    pub limit: Option<u64>,
}

#[derive(Clone, Debug, Default)]
pub struct BinanceLimitOrderParams<'a> {
    pub position_side: Option<&'a str>,
    pub reduce_only: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct BinanceMarketOrderParams<'a> {
    pub position_side: Option<&'a str>,
    pub reduce_only: Option<&'a str>,
    pub new_order_resp_type: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct BinanceOpenFuturesAlgoOrdersParams<'a> {
    pub product_symbol: Option<&'a str>,
    pub algo_type: Option<&'a str>,
    pub algo_id: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct BinanceOptionalSymbolParams<'a> {
    pub product_symbol: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct BinanceOrderLookupParams<'a> {
    pub order_id: Option<&'a str>,
    pub orig_client_order_id: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct BinancePostOnlyOrderParams<'a> {
    pub position_side: Option<&'a str>,
    pub reduce_only: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct BinanceSymbolListParams<'a> {
    pub product_symbol: Option<&'a str>,
    pub product_symbols: Option<Vec<String>>,
    pub symbol_status: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct BinanceUniversalTransferHistoryParams<'a> {
    pub start_time: Option<u64>,
    pub end_time: Option<u64>,
    pub current: Option<u64>,
    pub size: Option<u64>,
    pub from_symbol: Option<&'a str>,
    pub to_symbol: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct BinanceUniversalTransferParams<'a> {
    pub from_symbol: Option<&'a str>,
    pub to_symbol: Option<&'a str>,
}

#[derive(Clone, Debug, Default)]
pub struct BinanceWalletBalanceParams<'a> {
    pub quote_asset: Option<&'a str>,
}

pub(super) struct PublicParams(pub(super) Vec<(String, String)>);

impl PublicParams {
    pub(super) fn get(&self, key: &str) -> Option<&str> {
        self.0
            .iter()
            .find(|(candidate, _)| candidate == key)
            .map(|(_, value)| value.as_str())
    }

    pub(super) fn values(&self, key: &str) -> Option<Vec<String>> {
        let values = self
            .0
            .iter()
            .filter(|(candidate, _)| candidate == key)
            .map(|(_, value)| value.clone())
            .collect::<Vec<_>>();
        if values.is_empty() {
            None
        } else {
            Some(values)
        }
    }

    pub(super) fn required(&self, key: &str) -> Result<&str> {
        self.get(key)
            .ok_or_else(|| DcexError::InvalidInput(format!("missing required parameter: {key}")))
    }

    pub(super) fn u64(&self, key: &str) -> Result<Option<u64>> {
        self.get(key)
            .map(|value| {
                value.parse::<u64>().map_err(|error| {
                    DcexError::InvalidInput(format!("invalid integer parameter {key}: {error}"))
                })
            })
            .transpose()
    }

    pub(super) fn without(&self, excluded: &[&str]) -> Vec<(String, String)> {
        self.0
            .iter()
            .filter(|(key, _)| !excluded.contains(&key.as_str()))
            .cloned()
            .collect()
    }
}

pub(super) fn exchange_symbol_fallback(product_symbol: &str) -> String {
    let mut parts = product_symbol.split('-');
    match (parts.next(), parts.next(), parts.next()) {
        (Some(base), Some(quote), Some(_kind)) => format!("{base}{quote}"),
        _ => product_symbol.to_string(),
    }
}

pub(super) fn is_canonical_product_symbol(product_symbol: &str) -> bool {
    product_symbol.contains('-')
}

pub(super) fn is_spot_product_symbol(product_symbol: &str) -> bool {
    product_symbol.ends_with("-SPOT")
}

pub(super) fn market_for_product_symbol_fallback(product_symbol: &str) -> BinanceMarket {
    if is_spot_product_symbol(product_symbol) {
        BinanceMarket::Spot
    } else {
        BinanceMarket::Futures
    }
}

pub(super) fn market_from_type(market_type: &str) -> BinanceMarket {
    if market_type.eq_ignore_ascii_case("spot") {
        BinanceMarket::Spot
    } else {
        BinanceMarket::Futures
    }
}

pub(super) fn normalize_order_side(side: &str) -> Result<String> {
    if side.eq_ignore_ascii_case("buy") {
        Ok("BUY".to_string())
    } else if side.eq_ignore_ascii_case("sell") {
        Ok("SELL".to_string())
    } else {
        Err(DcexError::InvalidInput(format!(
            "unsupported Binance order side: {side}"
        )))
    }
}

pub(super) fn ensure_futures_listen_key_market(market_type: &str) -> Result<()> {
    if market_type.eq_ignore_ascii_case("spot") {
        Err(DcexError::InvalidInput(
            "Binance Spot user data streams are subscribed through the WebSocket API.".to_string(),
        ))
    } else {
        Ok(())
    }
}

pub(super) fn push_optional(params: &mut Vec<(String, String)>, key: &str, value: Option<&str>) {
    if let Some(value) = value {
        params.push((key.to_string(), value.to_string()));
    }
}

pub(super) fn push_optional_display<T: ToString>(
    params: &mut Vec<(String, String)>,
    key: &str,
    value: Option<T>,
) {
    if let Some(value) = value {
        params.push((key.to_string(), value.to_string()));
    }
}
