use super::api::BinanceWebSocketApiMarket;
use super::api_schema::{Field, Kind};
use crate::Result;
use serde_json::{Map, Value};

pub(super) fn validate(
    market: BinanceWebSocketApiMarket,
    method: &str,
    params: &Map<String, Value>,
    fields: &[Field],
) -> Result<()> {
    for field in fields {
        if field.required && !params.contains_key(field.name) {
            return Err(invalid(&format!("{} is required", field.name)));
        }
    }
    for (key, value) in params {
        if key == "returnRateLimits" {
            if !value.is_boolean() {
                return Err(invalid("returnRateLimits must be boolean"));
            }
            continue;
        }
        let field = fields
            .iter()
            .find(|f| f.name == key)
            .ok_or_else(|| invalid(&format!("unsupported parameter {key}")))?;
        let valid = match field.kind {
            Kind::Text => value.as_str().is_some_and(|v| !v.is_empty()),
            Kind::Integer => value.as_u64().is_some(),
            Kind::Decimal if key == "recvWindow" => {
                let text = value
                    .as_str()
                    .map(str::to_owned)
                    .unwrap_or_else(|| value.to_string());
                text.parse::<f64>()
                    .is_ok_and(|v| v.is_finite() && v > 0.0 && v <= 60_000.0)
                    && text
                        .split_once('.')
                        .is_none_or(|(_, fraction)| fraction.len() <= 3)
            }
            Kind::Decimal => {
                value.is_string()
                    && crate::exchanges::input_contracts::validate(
                        value,
                        &serde_json::json!({"format":"decimal", "x-positive":true}),
                        key,
                    )
                    .is_ok()
            }
            Kind::Bool => value.is_boolean(),
            Kind::Strings => value.as_array().is_some_and(|v| {
                !v.is_empty() && v.iter().all(|v| v.as_str().is_some_and(|v| !v.is_empty()))
            }),
        };
        if !valid {
            return Err(invalid(&format!(
                "invalid JSON type or value for {key}; decimal amounts must be positive strings and integers must be JSON numbers"
            )));
        }
    }
    if market != BinanceWebSocketApiMarket::Spot
        && params
            .get("recvWindow")
            .and_then(Value::as_u64)
            .is_some_and(|v| v == 0 || v > 60_000)
    {
        return Err(invalid("recvWindow must be 1..=60000"));
    }
    exclusive(params, &["symbol", "symbols"])?;
    exclusive(params, &["price", "priceMatch"])?;
    exclusive(params, &["quantity", "quoteOrderQty"])?;
    for key in ["side", "workingSide", "pendingSide"] {
        enum_value(params, key, &["BUY", "SELL"])?;
    }
    enum_value(params, "positionSide", &["BOTH", "LONG", "SHORT"])?;
    enum_value(
        params,
        "cancelReplaceMode",
        &["STOP_ON_FAILURE", "ALLOW_FAILURE"],
    )?;
    enum_value(
        params,
        "workingType",
        if method == "algoOrder.place" {
            &["MARK_PRICE", "CONTRACT_PRICE"]
        } else {
            &["LIMIT", "LIMIT_MAKER"]
        },
    )?;
    for key in ["reduceOnly", "closePosition"] {
        enum_value(params, key, &["true", "false"])?;
    }
    enum_value(params, "priceProtect", &["TRUE", "FALSE"])?;
    if matches!(
        method,
        "order.status" | "order.cancel" | "order.modify" | "order.amend.keepPriority"
    ) {
        any(params, &["orderId", "origClientOrderId"])?;
    }
    if matches!(method, "orderList.status" | "orderList.cancel") {
        any(
            params,
            &["orderListId", "listClientOrderId", "origClientOrderId"],
        )?;
    }
    if method == "order.cancelReplace" {
        any(params, &["cancelOrderId", "cancelOrigClientOrderId"])?;
    }
    if method == "algoOrder.cancel" {
        any(params, &["algoId", "clientAlgoId"])?;
    }
    if method == "order.modify" {
        any(params, &["price", "priceMatch"])?;
    }
    if matches!(
        method,
        "order.place" | "order.test" | "order.cancelReplace" | "sor.order.place" | "sor.order.test"
    ) {
        let kind = params
            .get("type")
            .and_then(Value::as_str)
            .ok_or_else(|| invalid("type is required"))?;
        let types = if market != BinanceWebSocketApiMarket::Spot || method.starts_with("sor.") {
            &["LIMIT", "MARKET"][..]
        } else {
            &[
                "LIMIT",
                "MARKET",
                "STOP_LOSS",
                "STOP_LOSS_LIMIT",
                "TAKE_PROFIT",
                "TAKE_PROFIT_LIMIT",
                "LIMIT_MAKER",
            ][..]
        };
        if !types.contains(&kind) {
            // Current COIN-M order.place documentation also rejects migrated
            // conditional orders with -4120; do not restore the legacy types.
            // https://developers.binance.com/docs/derivatives/coin-margined-futures/trade/websocket-api/New-Order
            return Err(invalid(match market {
                BinanceWebSocketApiMarket::Futures => {
                    "unsupported order type; USD-M conditional orders use algoOrder.place"
                }
                BinanceWebSocketApiMarket::CoinFutures => {
                    "unsupported order type; COIN-M conditional orders use place_coin_futures_algo_order (REST /dapi/v1/algoOrder) after migration"
                }
                BinanceWebSocketApiMarket::Spot => "unsupported order type",
            }));
        }
        any(params, &["quantity", "quoteOrderQty"])?;
        if kind != "MARKET" && params.contains_key("quoteOrderQty") {
            return Err(invalid("quoteOrderQty is only valid for MARKET orders"));
        }
        if matches!(
            kind,
            "LIMIT" | "LIMIT_MAKER" | "STOP_LOSS_LIMIT" | "TAKE_PROFIT_LIMIT"
        ) {
            any(params, &["price", "priceMatch", "pegPriceType"])?;
            if kind != "LIMIT_MAKER" {
                any(params, &["timeInForce"])?;
            }
        }
        if matches!(
            kind,
            "STOP_LOSS" | "STOP_LOSS_LIMIT" | "TAKE_PROFIT" | "TAKE_PROFIT_LIMIT"
        ) {
            any(params, &["stopPrice", "trailingDelta"])?;
        }
        if params.contains_key("icebergQty")
            && params.get("timeInForce").and_then(Value::as_str) != Some("GTC")
            && kind != "LIMIT_MAKER"
        {
            return Err(invalid("iceberg orders require GTC"));
        }
        if params.contains_key("pegOffsetValue") != params.contains_key("pegOffsetType") {
            return Err(invalid(
                "pegOffsetValue and pegOffsetType must be supplied together",
            ));
        }
    }
    if method == "algoOrder.place" {
        enum_value(params, "algoType", &["CONDITIONAL"])?;
        enum_value(
            params,
            "type",
            &[
                "STOP",
                "TAKE_PROFIT",
                "STOP_MARKET",
                "TAKE_PROFIT_MARKET",
                "TRAILING_STOP_MARKET",
            ],
        )?;
        let kind = params["type"].as_str().unwrap_or_default();
        let close = params.get("closePosition").and_then(Value::as_str) == Some("true");
        if close {
            if !matches!(kind, "STOP_MARKET" | "TAKE_PROFIT_MARKET")
                || params.contains_key("quantity")
                || params.contains_key("reduceOnly")
            {
                return Err(invalid(
                    "closePosition requires STOP_MARKET/TAKE_PROFIT_MARKET without quantity/reduceOnly",
                ));
            }
        } else {
            any(params, &["quantity"])?;
        }
        if kind == "TRAILING_STOP_MARKET" {
            any(params, &["callbackRate"])?;
            if !params["callbackRate"]
                .as_str()
                .and_then(|s| s.parse::<f64>().ok())
                .is_some_and(|v| (0.1..=10.0).contains(&v))
            {
                return Err(invalid("callbackRate must be 0.1..=10"));
            }
        } else {
            any(params, &["triggerPrice"])?;
        }
        if matches!(kind, "STOP" | "TAKE_PROFIT") {
            any(params, &["price", "priceMatch"])?;
        }
    }
    if params
        .get("positionSide")
        .and_then(Value::as_str)
        .is_some_and(|s| s != "BOTH")
        && params.contains_key("reduceOnly")
    {
        return Err(invalid("reduceOnly cannot be sent in hedge mode"));
    }
    if params.get("timeInForce").and_then(Value::as_str) == Some("GTD") {
        any(params, &["goodTillDate"])?;
    }
    if let (Some(start), Some(end)) = (
        params.get("startTime").and_then(Value::as_u64),
        params.get("endTime").and_then(Value::as_u64),
    ) && start > end
    {
        return Err(invalid("startTime cannot exceed endTime"));
    }
    if let Some(kind) = method.strip_prefix("orderList.place.") {
        let converted = super::super::params::PublicParams(
            params
                .iter()
                .map(|(k, v)| {
                    (
                        k.clone(),
                        v.as_str()
                            .map(str::to_owned)
                            .unwrap_or_else(|| v.to_string()),
                    )
                })
                .collect(),
        );
        super::super::order_lists::validate(&format!("/api/v3/orderList/{kind}"), &converted)?;
    }
    Ok(())
}

fn any(params: &Map<String, Value>, keys: &[&str]) -> Result<()> {
    if keys.iter().any(|k| params.contains_key(*k)) {
        Ok(())
    } else {
        Err(invalid(&format!("one of {} is required", keys.join(", "))))
    }
}
fn exclusive(params: &Map<String, Value>, keys: &[&str]) -> Result<()> {
    if keys.iter().filter(|k| params.contains_key(**k)).count() > 1 {
        Err(invalid(&format!(
            "{} are mutually exclusive",
            keys.join(", ")
        )))
    } else {
        Ok(())
    }
}
fn enum_value(params: &Map<String, Value>, key: &str, values: &[&str]) -> Result<()> {
    if params
        .get(key)
        .is_some_and(|v| !v.as_str().is_some_and(|s| values.contains(&s)))
    {
        Err(invalid(&format!("invalid {key}")))
    } else {
        Ok(())
    }
}
use crate::exchanges::binance::params::invalid_ws as invalid;
