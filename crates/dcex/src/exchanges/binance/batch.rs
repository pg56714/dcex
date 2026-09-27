//! USD-M and COIN-M batch order lifecycle.
use super::client::{BinanceClient, BinanceMarket};
use super::params::PublicParams;
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};
use serde_json::Value;

fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(format!("Binance batch: {message}"))
}
const PRICE_MATCH: &[&str] = &[
    "OPPONENT",
    "OPPONENT_5",
    "OPPONENT_10",
    "OPPONENT_20",
    "QUEUE",
    "QUEUE_5",
    "QUEUE_10",
    "QUEUE_20",
];

impl BinanceClient {
    pub(super) async fn batch_private_request(
        &self,
        name: &str,
        params: &PublicParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (market, method) = match name {
            "place_futures_batch_orders" => (BinanceMarket::Futures, HttpMethod::Post),
            "amend_futures_batch_orders" => (BinanceMarket::Futures, HttpMethod::Put),
            "cancel_futures_batch_orders" => (BinanceMarket::Futures, HttpMethod::Delete),
            "place_coin_futures_batch_orders" => (BinanceMarket::CoinFutures, HttpMethod::Post),
            "amend_coin_futures_batch_orders" => (BinanceMarket::CoinFutures, HttpMethod::Put),
            "cancel_coin_futures_batch_orders" => (BinanceMarket::CoinFutures, HttpMethod::Delete),
            _ => return Ok(None),
        };
        params.optional_u64_range("recvWindow", 1, 60000)?;
        let mut query = Vec::new();
        if let Some(window) = params.get("recvWindow") {
            query.push(("recvWindow".into(), window.into()));
        }
        if method == HttpMethod::Delete {
            params.ensure_allowed(&[
                "product_symbol",
                "symbol",
                "orderIdList",
                "origClientOrderIdList",
                "recvWindow",
            ])?;
            let symbol =
                self.batch_symbol(params.get("product_symbol"), params.get("symbol"), market)?;
            query.push(("symbol".into(), symbol));
            if params.get("orderIdList").is_some() == params.get("origClientOrderIdList").is_some()
            {
                return Err(invalid(
                    "provide exactly one of orderIdList or origClientOrderIdList",
                ));
            }
            for key in ["orderIdList", "origClientOrderIdList"] {
                if let Some(raw) = params.get(key) {
                    let values: Vec<Value> =
                        serde_json::from_str(raw).map_err(|e| invalid(&e.to_string()))?;
                    if !(1..=10).contains(&values.len()) {
                        return Err(invalid("cancel list must contain 1..=10 identifiers"));
                    }
                    for value in &values {
                        if key == "orderIdList" {
                            if !value
                                .as_u64()
                                .is_some_and(|v| v > 0 && v <= i64::MAX as u64)
                            {
                                return Err(invalid("orderIdList requires positive JSON integers"));
                            }
                        } else if !value.as_str().is_some_and(|v| !v.is_empty()) {
                            return Err(invalid("client identifiers must be nonempty strings"));
                        }
                    }
                    query.push((key.into(), serde_json::to_string(&values).unwrap()));
                }
            }
        } else {
            params.ensure_allowed(&["batchOrders", "recvWindow"])?;
            let mut orders: Vec<Value> = serde_json::from_str(params.required("batchOrders")?)
                .map_err(|e| invalid(&e.to_string()))?;
            if !(1..=5).contains(&orders.len()) {
                return Err(invalid("batchOrders must contain 1..=5 orders"));
            }
            for order in &mut orders {
                let object = order
                    .as_object_mut()
                    .ok_or_else(|| invalid("each batch order must be an object"))?;
                let symbol = self.batch_symbol(
                    object.get("product_symbol").and_then(Value::as_str),
                    object.get("symbol").and_then(Value::as_str),
                    market,
                )?;
                object.remove("product_symbol");
                object.insert("symbol".into(), symbol.into());
                validate_order(object, method == HttpMethod::Put)?;
            }
            query.push((
                "batchOrders".into(),
                serde_json::to_string(&orders).unwrap(),
            ));
        }
        let path = if market == BinanceMarket::Futures {
            "/fapi/v1/batchOrders"
        } else {
            "/dapi/v1/batchOrders"
        };
        Ok(Some(self.request(method, market, path, query, true).await?))
    }
    fn batch_symbol(
        &self,
        product: Option<&str>,
        symbol: Option<&str>,
        market: BinanceMarket,
    ) -> Result<String> {
        match (product, symbol) {
            (Some(product), None) => {
                if self.market_for_product_symbol(product)? != market {
                    return Err(invalid("product_symbol does not match endpoint market"));
                }
                self.exchange_symbol(product)
            }
            (None, Some(symbol))
                if !symbol.is_empty()
                    && symbol
                        .bytes()
                        .all(|b| b.is_ascii_uppercase() || b.is_ascii_digit() || b == b'_') =>
            {
                Ok(symbol.into())
            }
            _ => Err(invalid(
                "provide exactly one valid product_symbol or native symbol",
            )),
        }
    }
}

fn validate_order(order: &mut serde_json::Map<String, Value>, amend: bool) -> Result<()> {
    let allowed = if amend {
        &[
            "symbol",
            "side",
            "quantity",
            "price",
            "priceMatch",
            "orderId",
            "origClientOrderId",
            "modifyId",
            "stopPrice",
        ][..]
    } else {
        &[
            "symbol",
            "side",
            "positionSide",
            "type",
            "timeInForce",
            "quantity",
            "reduceOnly",
            "price",
            "newClientOrderId",
            "stopPrice",
            "closePosition",
            "activationPrice",
            "callbackRate",
            "workingType",
            "priceProtect",
            "newOrderRespType",
            "priceMatch",
            "selfTradePreventionMode",
            "goodTillDate",
        ][..]
    };
    if order.keys().any(|k| !allowed.contains(&k.as_str())) {
        return Err(invalid("unsupported order field"));
    }
    if !order
        .get("side")
        .and_then(Value::as_str)
        .is_some_and(|s| ["BUY", "SELL"].contains(&s))
    {
        return Err(invalid("side must be BUY or SELL"));
    }
    for key in [
        "quantity",
        "price",
        "stopPrice",
        "activationPrice",
        "callbackRate",
    ] {
        if let Some(value) = order.get(key) {
            let amount = value
                .as_str()
                .and_then(|v| v.parse::<f64>().ok())
                .or_else(|| value.as_f64());
            if !amount.is_some_and(|v| v.is_finite() && v > 0.0) {
                return Err(invalid("quantity and prices must be positive"));
            }
        }
    }
    for key in ["reduceOnly", "closePosition"] {
        if let Some(value) = order.get_mut(key) {
            if let Some(boolean) = value.as_bool() {
                *value = boolean.to_string().into();
            }
            if !value
                .as_str()
                .is_some_and(|v| ["true", "false"].contains(&v))
            {
                return Err(invalid("invalid boolean order field"));
            }
        }
    }
    if let Some(value) = order.get("priceMatch") {
        if !value.as_str().is_some_and(|v| PRICE_MATCH.contains(&v)) || order.contains_key("price")
        {
            return Err(invalid(
                "priceMatch must be valid and cannot accompany price",
            ));
        }
    }
    if amend {
        if !["orderId", "origClientOrderId"].iter().any(|key| {
            order.get(*key).is_some_and(|v| {
                v.as_str().is_some_and(|s| !s.is_empty()) || v.as_u64().is_some_and(|n| n > 0)
            })
        }) {
            return Err(invalid("orderId or origClientOrderId is required"));
        }
        if !order.contains_key("quantity")
            || !order.contains_key("price") && !order.contains_key("priceMatch")
        {
            return Err(invalid("amend requires quantity and price or priceMatch"));
        }
    } else {
        let kind = order
            .get("type")
            .and_then(Value::as_str)
            .ok_or_else(|| invalid("type is required"))?;
        if ![
            "LIMIT",
            "MARKET",
            "STOP",
            "STOP_MARKET",
            "TAKE_PROFIT",
            "TAKE_PROFIT_MARKET",
            "TRAILING_STOP_MARKET",
        ]
        .contains(&kind)
        {
            return Err(invalid("unsupported order type"));
        }
        let close_all = order.get("closePosition").and_then(Value::as_str) == Some("true");
        if close_all {
            if !["STOP_MARKET", "TAKE_PROFIT_MARKET"].contains(&kind)
                || order.contains_key("quantity")
                || order.contains_key("reduceOnly")
            {
                return Err(invalid(
                    "closePosition only supports conditional close-all without quantity/reduceOnly",
                ));
            }
        } else if !order.contains_key("quantity") {
            return Err(invalid("quantity is required"));
        }
        if ["LIMIT", "STOP", "TAKE_PROFIT"].contains(&kind)
            && !order.contains_key("price")
            && !order.contains_key("priceMatch")
        {
            return Err(invalid("limit execution requires price or priceMatch"));
        }
        if kind == "LIMIT" && !order.contains_key("timeInForce") {
            return Err(invalid("LIMIT requires timeInForce"));
        }
        if ["STOP", "STOP_MARKET", "TAKE_PROFIT", "TAKE_PROFIT_MARKET"].contains(&kind)
            && !order.contains_key("stopPrice")
        {
            return Err(invalid("conditional order requires stopPrice"));
        }
        if kind == "TRAILING_STOP_MARKET" && !order.contains_key("callbackRate") {
            return Err(invalid("trailing stop requires callbackRate"));
        }
        if let Some(value) = order.get("callbackRate") {
            let rate = value
                .as_str()
                .and_then(|v| v.parse::<f64>().ok())
                .or_else(|| value.as_f64())
                .unwrap();
            if !(0.1..=10.0).contains(&rate) {
                return Err(invalid("callbackRate must be 0.1..=10"));
            }
        }
    }
    Ok(())
}
