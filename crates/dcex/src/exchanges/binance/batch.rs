//! USD-M and COIN-M batch order lifecycle.
//!
//! Place, amend and cancel responses contain `ok` and `errors` arrays. Each entry
//! retains the zero-based request `index` and the full exchange `response`.
//! Callers must inspect `errors`, even when the HTTP status is 200.
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
                        } else if value.as_str().is_none_or(|v| v.is_empty()) {
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
                validate_order(object, method == HttpMethod::Put, market)?;
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
        let mut response = self.request(method, market, path, query, true).await?;
        response.data = split_batch_results(response.data)?;
        Ok(Some(response))
    }
    pub(super) fn batch_symbol(
        &self,
        product: Option<&str>,
        symbol: Option<&str>,
        market: BinanceMarket,
    ) -> Result<String> {
        match (product, symbol) {
            (Some(product), None) if !product.contains('-') => {
                self.batch_symbol(None, Some(product), market)
            }
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
                let coin_symbol = symbol.split_once('_').is_some_and(|(pair, expiry)| {
                    pair.ends_with("USD")
                        && (expiry == "PERP"
                            || (expiry.len() == 6 && expiry.bytes().all(|b| b.is_ascii_digit())))
                });
                if coin_symbol != (market == BinanceMarket::CoinFutures) {
                    return Err(invalid("native symbol does not match endpoint market"));
                }
                Ok(symbol.into())
            }
            _ => Err(invalid(
                "provide exactly one valid product_symbol or native symbol",
            )),
        }
    }
}

pub(super) fn split_batch_results(data: Value) -> Result<Value> {
    let Value::Array(items) = data else {
        return Err(DcexError::Runtime(
            "Binance batch response must be an array of item outcomes".into(),
        ));
    };
    let mut ok = Vec::new();
    let mut errors = Vec::new();
    for (index, item) in items.into_iter().enumerate() {
        let object = item.as_object().ok_or_else(|| {
            DcexError::Runtime(format!(
                "Binance batch response item {index} must be an object"
            ))
        })?;
        let failed = object
            .get("code")
            .is_some_and(|code| super::signing::json_value_string(code) != "200");
        let entry = serde_json::json!({"index": index, "response": item});
        if failed {
            errors.push(entry);
        } else {
            ok.push(entry);
        }
    }
    Ok(serde_json::json!({"ok": ok, "errors": errors}))
}

fn positive_decimal(value: &Value) -> bool {
    let Some(text) = value.as_str() else {
        return false;
    };
    let (integer, fraction) = text.split_once('.').unwrap_or((text, "0"));
    !integer.is_empty()
        && !fraction.is_empty()
        && integer
            .bytes()
            .chain(fraction.bytes())
            .all(|b| b.is_ascii_digit())
        && text.bytes().any(|b| matches!(b, b'1'..=b'9'))
}

fn validate_order(
    order: &mut serde_json::Map<String, Value>,
    amend: bool,
    market: BinanceMarket,
) -> Result<()> {
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
        if let Some(value) = order.get(key)
            && !positive_decimal(value)
        {
            return Err(invalid(&format!(
                "{key} must be a positive plain decimal string; JSON numbers are not accepted"
            )));
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
    if let Some(value) = order.get("priceMatch")
        && (!value.as_str().is_some_and(|v| PRICE_MATCH.contains(&v))
            || order.contains_key("price"))
    {
        return Err(invalid(
            "priceMatch must be valid and cannot accompany price",
        ));
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
        // USD-M migration: derivatives changelog, 2025-11-06 (effective 2025-12-09).
        // COIN-M also migrated: the current POST /dapi/v1/batchOrders documentation
        // explicitly reports element-level -4120 for these types after migration.
        // https://developers.binance.com/docs/derivatives/coin-margined-futures/trade/rest-api/Place-Multiple-Orders
        if !["LIMIT", "MARKET"].contains(&kind) {
            return Err(invalid(if market == BinanceMarket::Futures {
                "USD-M conditional orders cannot be batched; use place_futures_algo_order"
            } else {
                "COIN-M conditional orders cannot be batched after migration; use REST /dapi/v1/algoOrder"
            }));
        }
        let close_all = order.get("closePosition").and_then(Value::as_str) == Some("true");
        if close_all {
            return Err(invalid(
                "closePosition is not supported for LIMIT/MARKET batches",
            ));
        }
        if !order.contains_key("quantity") {
            return Err(invalid("quantity is required"));
        }
        if kind == "LIMIT" && !order.contains_key("price") && !order.contains_key("priceMatch") {
            return Err(invalid("limit execution requires price or priceMatch"));
        }
        if kind == "LIMIT" && !order.contains_key("timeInForce") {
            return Err(invalid("LIMIT requires timeInForce"));
        }
        if let Some(value) = order.get("callbackRate") {
            let rate = value
                .as_str()
                .and_then(|v| v.parse::<f64>().ok())
                .ok_or_else(|| invalid("callbackRate must be 0.1..=10"))?;
            if !(0.1..=10.0).contains(&rate) {
                return Err(invalid("callbackRate must be 0.1..=10"));
            }
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[tokio::test]
    async fn conditional_batches_fail_before_transport_for_both_markets() {
        let listener = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
        listener.set_nonblocking(true).unwrap();
        let base = format!("http://{}", listener.local_addr().unwrap());
        let client = BinanceClient::with_base_urls(
            Some("key".into()),
            Some("secret".into()),
            std::time::Duration::from_secs(1),
            base.clone(),
            base.clone(),
        )
        .unwrap()
        .with_coin_futures_base_url(base);
        for (name, symbol, target) in [
            (
                "place_futures_batch_orders",
                "BTCUSDT",
                "place_futures_algo_order",
            ),
            (
                "place_coin_futures_batch_orders",
                "BTCUSD_PERP",
                "/dapi/v1/algoOrder",
            ),
        ] {
            for kind in [
                "STOP",
                "STOP_MARKET",
                "TAKE_PROFIT",
                "TAKE_PROFIT_MARKET",
                "TRAILING_STOP_MARKET",
            ] {
                let orders = json!([
                    {"symbol": symbol, "side": "BUY", "type": "LIMIT", "timeInForce": "GTC", "quantity": "1", "price": "50000"},
                    {"symbol": symbol, "side": "SELL", "type": kind, "quantity": "1", "price": "49000", "stopPrice": "49000", "callbackRate": "1"}
                ]);
                let error = client
                    .private_request(name, vec![("batchOrders".into(), orders.to_string())])
                    .await
                    .unwrap_err();
                assert!(matches!(error, DcexError::InvalidInput(_)), "{error}");
                assert!(error.to_string().contains(target), "{error}");
            }
        }
        assert_eq!(
            listener.accept().unwrap_err().kind(),
            std::io::ErrorKind::WouldBlock
        );
    }

    #[test]
    fn batch_results_preserve_item_indices_and_exchange_payloads() {
        let success = json!({"orderId": 42, "status": "CANCELED"});
        let failure = json!({"code": -2011, "msg": "Unknown order sent."});
        assert_eq!(
            split_batch_results(json!([success, failure])).unwrap(),
            json!({
                "ok": [{"index": 0, "response": success}],
                "errors": [{"index": 1, "response": failure}]
            })
        );
        assert_eq!(
            split_batch_results(json!([failure, failure])).unwrap()["ok"],
            json!([])
        );
        assert_eq!(
            split_batch_results(json!([success, success])).unwrap()["errors"],
            json!([])
        );
        assert_eq!(
            split_batch_results(json!([])).unwrap(),
            json!({"ok": [], "errors": []})
        );
        assert!(split_batch_results(json!({"unexpected": true})).is_err());
        assert!(split_batch_results(json!([null])).is_err());
        assert_eq!(
            split_batch_results(json!([{"code": "-2011", "msg": "Unknown"}])).unwrap()["ok"],
            json!([])
        );
        assert_eq!(
            split_batch_results(json!([{"code": 200, "msg": "success"}])).unwrap()["errors"],
            json!([])
        );
    }

    #[test]
    fn batch_decimal_fields_reject_numbers_and_non_plain_strings() {
        for key in [
            "quantity",
            "price",
            "stopPrice",
            "activationPrice",
            "callbackRate",
        ] {
            for value in [
                json!(0.1),
                json!(1),
                json!(true),
                Value::Null,
                json!("1e-5"),
                json!("0"),
                json!("-1"),
                json!("NaN"),
                json!("inf"),
                json!(" 1"),
                json!(".1"),
                json!("1."),
                json!("1.2.3"),
            ] {
                let mut order = json!({"symbol": "BTCUSDT", "side": "BUY", "type": "LIMIT", "timeInForce": "GTC", "quantity": "1", "price": "50000"}).as_object().unwrap().clone();
                order.insert(key.into(), value.clone());
                let error = validate_order(&mut order, false, BinanceMarket::Futures).unwrap_err();
                assert!(
                    error.to_string().contains("decimal string"),
                    "{key}={value}: {error}"
                );
            }
        }
        for value in [
            "0.000000000000000000000000000001",
            "12345678901234567890.12345678901234567890",
        ] {
            assert!(positive_decimal(&json!(value)));
        }
    }
}
