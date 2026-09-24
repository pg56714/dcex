use super::client::{BinanceClient, BinanceMarket};
use super::params::PublicParams;
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

const ROOT: &str = "/dapi/v1";

fn ensure_native_symbol(params: &PublicParams) -> Result<()> {
    let symbol = params.required("symbol")?;
    if !symbol
        .chars()
        .all(|ch| ch.is_ascii_uppercase() || ch.is_ascii_digit() || ch == '_')
    {
        return Err(DcexError::InvalidInput(
            "COIN-M symbol must be a native Binance symbol such as BTCUSD_PERP".into(),
        ));
    }
    Ok(())
}

fn positive(params: &PublicParams, key: &str) -> Result<()> {
    if let Some(value) = params.get(key) {
        if !value.parse::<f64>().is_ok_and(|v| v.is_finite() && v > 0.0) {
            return Err(DcexError::InvalidInput(format!("{key} must be positive")));
        }
    }
    Ok(())
}

impl BinanceClient {
    pub fn get_coin_futures_exchange_info(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_coin_futures_exchange_info",
            Vec::new(),
        )
    }

    pub fn get_coin_futures_orderbook(
        &self,
        symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_coin_futures_orderbook",
            vec![("symbol".into(), symbol.into())],
        )
    }

    pub fn get_coin_futures_balance(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_coin_futures_balance",
            Vec::new(),
        )
    }

    pub fn get_coin_futures_positions(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_coin_futures_positions",
            Vec::new(),
        )
    }

    pub fn get_coin_futures_trades(
        &self,
        symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_coin_futures_trades",
            vec![("symbol".into(), symbol.into())],
        )
    }

    pub fn get_coin_futures_klines(
        &self,
        symbol: &str,
        interval: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_coin_futures_klines",
            vec![
                ("symbol".into(), symbol.into()),
                ("interval".into(), interval.into()),
            ],
        )
    }

    pub fn get_coin_futures_ticker(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(self, "get_coin_futures_ticker", Vec::new())
    }

    pub fn get_coin_futures_mark_price(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_coin_futures_mark_price",
            Vec::new(),
        )
    }

    pub fn get_coin_futures_funding_rate(
        &self,
        symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_coin_futures_funding_rate",
            vec![("symbol".into(), symbol.into())],
        )
    }

    pub fn get_coin_futures_account(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_coin_futures_account",
            Vec::new(),
        )
    }

    pub fn get_coin_futures_open_orders(
        &self,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_coin_futures_open_orders",
            Vec::new(),
        )
    }

    pub fn get_coin_futures_order(
        &self,
        symbol: &str,
        order_id: u64,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "get_coin_futures_order",
            vec![
                ("symbol".into(), symbol.into()),
                ("orderId".into(), order_id.to_string()),
            ],
        )
    }

    pub fn place_coin_futures_order(
        &self,
        symbol: &str,
        side: &str,
        order_type: &str,
        quantity: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "place_coin_futures_order",
            vec![
                ("symbol".into(), symbol.into()),
                ("side".into(), side.into()),
                ("type".into(), order_type.into()),
                ("quantity".into(), quantity.into()),
            ],
        )
    }

    pub fn cancel_coin_futures_order(
        &self,
        symbol: &str,
        order_id: u64,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "cancel_coin_futures_order",
            vec![
                ("symbol".into(), symbol.into()),
                ("orderId".into(), order_id.to_string()),
            ],
        )
    }

    pub fn cancel_all_coin_futures_orders(
        &self,
        symbol: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "cancel_all_coin_futures_orders",
            vec![("symbol".into(), symbol.into())],
        )
    }

    pub fn place_coin_futures_limit_order(
        &self,
        symbol: &str,
        side: &str,
        quantity: &str,
        price: &str,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(
            self,
            "place_coin_futures_order",
            vec![
                ("symbol".into(), symbol.into()),
                ("side".into(), side.into()),
                ("type".into(), "LIMIT".into()),
                ("quantity".into(), quantity.into()),
                ("price".into(), price.into()),
                ("timeInForce".into(), "GTC".into()),
            ],
        )
    }

    pub(super) async fn coin_futures_public_request(
        &self,
        name: &str,
        params: &PublicParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, allowed): (&str, &[&str]) = match name {
            "get_coin_futures_exchange_info" => ("/dapi/v1/exchangeInfo", &[]),
            "get_coin_futures_orderbook" => ("/dapi/v1/depth", &["symbol", "limit"]),
            "get_coin_futures_trades" => ("/dapi/v1/trades", &["symbol", "limit"]),
            "get_coin_futures_klines" => (
                "/dapi/v1/klines",
                &["symbol", "interval", "startTime", "endTime", "limit"],
            ),
            "get_coin_futures_ticker" => ("/dapi/v1/ticker/price", &["symbol", "pair"]),
            "get_coin_futures_mark_price" => ("/dapi/v1/premiumIndex", &["symbol", "pair"]),
            "get_coin_futures_funding_rate" => (
                "/dapi/v1/fundingRate",
                &["symbol", "startTime", "endTime", "limit"],
            ),
            _ => return Ok(None),
        };
        debug_assert!(path.starts_with(ROOT));
        params.ensure_allowed(allowed)?;
        if matches!(
            name,
            "get_coin_futures_orderbook"
                | "get_coin_futures_trades"
                | "get_coin_futures_klines"
                | "get_coin_futures_funding_rate"
        ) {
            ensure_native_symbol(params)?;
        }
        if name == "get_coin_futures_klines" {
            params.required("interval")?;
            params.ensure_time_order("startTime", "endTime")?;
            params.optional_u64_range("limit", 1, 1500)?;
        }
        if name == "get_coin_futures_orderbook" {
            params.optional_one_of("limit", &["5", "10", "20", "50", "100", "500", "1000"])?;
        }
        if name == "get_coin_futures_trades" {
            params.optional_u64_range("limit", 1, 1000)?;
        }
        if name == "get_coin_futures_funding_rate" {
            params.ensure_time_order("startTime", "endTime")?;
            params.optional_u64_range("limit", 1, 1000)?;
        }
        if matches!(
            name,
            "get_coin_futures_ticker" | "get_coin_futures_mark_price"
        ) && params.get("symbol").is_some()
            && params.get("pair").is_some()
        {
            return Err(DcexError::InvalidInput(
                "symbol and pair cannot be sent together".into(),
            ));
        }
        Ok(Some(
            self.request(
                HttpMethod::Get,
                BinanceMarket::CoinFutures,
                path,
                params.0.clone(),
                false,
            )
            .await?,
        ))
    }

    pub(super) async fn coin_futures_private_request(
        &self,
        name: &str,
        params: &PublicParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (method, path, allowed): (HttpMethod, &str, &[&str]) = match name {
            "get_coin_futures_balance" => (HttpMethod::Get, "/dapi/v1/balance", &["recvWindow"]),
            "get_coin_futures_account" => (HttpMethod::Get, "/dapi/v1/account", &["recvWindow"]),
            "get_coin_futures_positions" => (
                HttpMethod::Get,
                "/dapi/v1/positionRisk",
                &["marginAsset", "pair", "recvWindow"],
            ),
            "get_coin_futures_open_orders" => (
                HttpMethod::Get,
                "/dapi/v1/openOrders",
                &["symbol", "pair", "recvWindow"],
            ),
            "get_coin_futures_order" => (
                HttpMethod::Get,
                "/dapi/v1/order",
                &["symbol", "orderId", "origClientOrderId", "recvWindow"],
            ),
            "place_coin_futures_order" => (
                HttpMethod::Post,
                "/dapi/v1/order",
                &[
                    "symbol",
                    "side",
                    "type",
                    "quantity",
                    "price",
                    "timeInForce",
                    "positionSide",
                    "reduceOnly",
                    "newClientOrderId",
                    "newOrderRespType",
                    "recvWindow",
                ],
            ),
            "cancel_coin_futures_order" => (
                HttpMethod::Delete,
                "/dapi/v1/order",
                &["symbol", "orderId", "origClientOrderId", "recvWindow"],
            ),
            "cancel_all_coin_futures_orders" => (
                HttpMethod::Delete,
                "/dapi/v1/allOpenOrders",
                &["symbol", "recvWindow"],
            ),
            _ => return Ok(None),
        };
        params.ensure_allowed(allowed)?;
        params.optional_u64_range("recvWindow", 1, 60_000)?;
        match name {
            "get_coin_futures_order" | "cancel_coin_futures_order" => {
                ensure_native_symbol(params)?;
                if params.get("orderId").is_none() && params.get("origClientOrderId").is_none() {
                    return Err(DcexError::InvalidInput(
                        "orderId or origClientOrderId is required".into(),
                    ));
                }
            }
            "place_coin_futures_order" => {
                ensure_native_symbol(params)?;
                params.required("side")?;
                params.optional_one_of("side", &["BUY", "SELL"])?;
                params.required("type")?;
                params.optional_one_of("type", &["LIMIT", "MARKET"])?;
                params.required("quantity")?;
                positive(params, "quantity")?;
                if params.get("type") == Some("LIMIT") {
                    params.required("price")?;
                    positive(params, "price")?;
                    params.required("timeInForce")?;
                }
                params.optional_one_of("timeInForce", &["GTC", "IOC", "FOK", "GTX"])?;
                params.optional_one_of("positionSide", &["BOTH", "LONG", "SHORT"])?;
                params.optional_bool("reduceOnly")?;
                params.optional_one_of("newOrderRespType", &["ACK", "RESULT"])?;
            }
            "cancel_all_coin_futures_orders" => {
                ensure_native_symbol(params)?;
            }
            "get_coin_futures_open_orders" => {
                if params.get("symbol").is_some() && params.get("pair").is_some() {
                    return Err(DcexError::InvalidInput(
                        "symbol and pair cannot be sent together".into(),
                    ));
                }
            }
            _ => {}
        }
        Ok(Some(
            self.request(
                method,
                BinanceMarket::CoinFutures,
                path,
                params.0.clone(),
                true,
            )
            .await?,
        ))
    }
}
