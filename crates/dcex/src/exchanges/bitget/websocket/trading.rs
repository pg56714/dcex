//! Trading frames use exchange-native symbols and decimal strings.
use crate::{DcexError, Result};
use serde_json::{Map, Value, json};

fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(format!("Bitget WebSocket: {message}"))
}

fn identifier(value: &str, max: usize) -> Result<()> {
    if value.trim().is_empty()
        || value.len() > max
        || !value
            .bytes()
            .all(|c| c.is_ascii_alphanumeric() || b"._:/-".contains(&c))
    {
        return Err(invalid("invalid request or client order identifier"));
    }
    Ok(())
}

fn required<'a>(arg: &'a Map<String, Value>, key: &str) -> Result<&'a str> {
    arg.get(key)
        .and_then(Value::as_str)
        .filter(|v| !v.trim().is_empty())
        .ok_or_else(|| invalid(&format!("{key} must be a non-empty string")))
}

fn choice(arg: &Map<String, Value>, key: &str, values: &[&str]) -> Result<()> {
    if arg.contains_key(key) && !values.contains(&required(arg, key)?) {
        return Err(invalid(&format!("invalid {key}")));
    }
    Ok(())
}

fn fields(arg: &Map<String, Value>, allowed: &[&str]) -> Result<()> {
    for (key, value) in arg {
        if !allowed.contains(&key.as_str()) {
            return Err(invalid(&format!("unsupported field: {key}")));
        }
        if key == "requestId" {
            if value
                .as_u64()
                .is_none_or(|n| n >= 1_000_000_000_000_000_000)
            {
                return Err(invalid("requestId must be an integer of at most 18 digits"));
            }
        } else {
            required(arg, key)?;
        }
    }
    if let Some(value) = arg.get("clientOid") {
        identifier(value.as_str().unwrap_or_default(), 32)?;
    }
    for key in [
        "qty",
        "size",
        "price",
        "takeprofit",
        "stoploss",
        "tpLimitPrice",
        "slLimitPrice",
        "presetStopSurplusPrice",
        "presetStopLossPrice",
    ] {
        if let Some(value) = arg.get(key)
            && !value
                .as_str()
                .and_then(|v| v.parse::<f64>().ok())
                .is_some_and(|n| n.is_finite() && n > 0.0)
        {
            return Err(invalid(&format!("{key} must be a positive decimal string")));
        }
    }
    choice(arg, "side", &["buy", "sell"])?;
    choice(arg, "orderType", &["limit", "market"])?;
    choice(arg, "posSide", &["long", "short"])?;
    choice(arg, "tradeSide", &["open", "close"])?;
    choice(
        arg,
        "stpMode",
        &["none", "cancel_taker", "cancel_maker", "cancel_both"],
    )?;
    choice(arg, "marginMode", &["crossed", "isolated"])?;
    choice(arg, "reduceOnly", &["YES", "NO", "yes", "no"])?;
    for key in ["autoCancel", "autoBorrow", "pxAmendType"] {
        choice(arg, key, &["yes", "no"])?;
    }
    for key in ["force", "timeInForce"] {
        choice(arg, key, &["gtc", "ioc", "fok", "post_only"])?;
    }
    for key in ["tpTriggerBy", "slTriggerBy"] {
        choice(arg, key, &["market", "mark"])?;
    }
    for (kind, trigger, price) in [
        ("tpOrderType", "takeprofit", "tpLimitPrice"),
        ("slOrderType", "stoploss", "slLimitPrice"),
    ] {
        choice(arg, kind, &["limit", "market"])?;
        if arg.contains_key(kind) || arg.contains_key(price) {
            required(arg, trigger)?;
        }
        if arg.get(kind).and_then(Value::as_str) == Some("limit") {
            required(arg, price)?;
        }
    }
    Ok(())
}

fn order_id(arg: &Map<String, Value>) -> Result<()> {
    if !arg.contains_key("orderId") && !arg.contains_key("clientOid") {
        return Err(invalid("orderId or clientOid is required"));
    }
    Ok(())
}

const PLACE: &[&str] = &[
    "symbol",
    "orderType",
    "qty",
    "price",
    "side",
    "posSide",
    "timeInForce",
    "reduceOnly",
    "clientOid",
    "stpMode",
    "tpTriggerBy",
    "slTriggerBy",
    "takeprofit",
    "stoploss",
    "tpOrderType",
    "slOrderType",
    "tpLimitPrice",
    "slLimitPrice",
    "marginMode",
    "autoBorrow",
    "pxAmendType",
    "receiveWindow",
];
const MODIFY: &[&str] = &[
    "orderId",
    "clientOid",
    "requestId",
    "qty",
    "price",
    "autoCancel",
    "symbol",
    "pxAmendType",
];
const CANCEL: &[&str] = &["orderId", "clientOid"];

pub(super) fn uta(
    id: &str,
    topic: &str,
    category: Option<&str>,
    args: Value,
    request_time: Option<u64>,
) -> Result<Value> {
    identifier(id, 40)?;
    if let Some(category) = category
        && ![
            "spot",
            "margin",
            "usdt-futures",
            "coin-futures",
            "usdc-futures",
        ]
        .contains(&category)
    {
        return Err(invalid("invalid lowercase category"));
    }
    let allowed = match topic {
        "place-order" | "batch-place" => PLACE,
        "modify-order" | "batch-modify" => MODIFY,
        "cancel-order" | "batch-cancel" => CANCEL,
        _ => return Err(invalid("unsupported trading topic")),
    };
    let list = args
        .as_array()
        .ok_or_else(|| invalid("args must be an array"))?;
    let batch = topic.starts_with("batch-");
    if list.is_empty()
        || (!batch && list.len() != 1)
        || (matches!(topic, "batch-place" | "batch-cancel") && list.len() > 20)
    {
        return Err(invalid("invalid number of trading arguments"));
    }
    if matches!(topic, "place-order" | "batch-place") && category.is_none() {
        return Err(invalid("category is required for placing orders"));
    }
    if topic == "batch-cancel" && category.is_some() {
        return Err(invalid("batch-cancel does not accept category"));
    }
    if request_time.is_some() && topic != "place-order" {
        return Err(invalid("requestTime is only supported for place-order"));
    }
    let mut id_kind = None;
    for value in list {
        let arg = value
            .as_object()
            .ok_or_else(|| invalid("each argument must be an object"))?;
        fields(arg, allowed)?;
        if matches!(topic, "place-order" | "batch-place") {
            for key in ["symbol", "orderType", "qty", "side"] {
                required(arg, key)?;
            }
            if arg.get("orderType").and_then(Value::as_str) == Some("limit") {
                required(arg, "price")?;
            }
            if topic == "batch-place"
                && let Some(key) = ["reduceOnly", "marginMode", "autoBorrow", "receiveWindow"]
                    .iter()
                    .find(|k| arg.contains_key(**k))
            {
                return Err(invalid(&format!("unsupported batch-place field: {key}")));
            }
            if let Some(window) = arg.get("receiveWindow")
                && (request_time.is_none()
                    || !window
                        .as_str()
                        .and_then(|v| v.parse::<u64>().ok())
                        .is_some_and(|n| (10..=60000).contains(&n)))
            {
                return Err(invalid(
                    "receiveWindow requires requestTime and a value between 10 and 60000",
                ));
            }
        } else {
            order_id(arg)?;
            if topic.contains("modify") {
                if category == Some("coin-futures") {
                    return Err(invalid("COIN-M does not support order modification"));
                }
                if !arg.contains_key("qty") && !arg.contains_key("price") {
                    return Err(invalid("modification requires qty or price"));
                }
            }
        }
        if topic == "batch-cancel" {
            let kind = arg.contains_key("orderId");
            if arg.len() != 1 || id_kind.is_some_and(|old| old != kind) {
                return Err(invalid(
                    "batch-cancel must use only one identifier type throughout",
                ));
            }
            id_kind = Some(kind);
        }
    }
    let mut payload = json!({"op":"trade","id":id,"topic":topic,"args":args});
    if let Some(category) = category {
        payload["category"] = json!(category);
    }
    if let Some(time) = request_time {
        payload["requestTime"] = json!(time.to_string());
    }
    Ok(payload)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn identifiers_reject_whitespace_and_accept_rest_characters() {
        for id in ["a b", "a\tb", "a\rb", "a\nb", "a#b", "a+b"] {
            assert!(identifier(id, 64).is_err(), "{id:?}");
        }
        assert!(identifier("Aa09._:/-", 64).is_ok());
    }
    #[test]
    fn uta_has_documented_wire_envelope() {
        let order = json!({"symbol":"BTCUSDT","orderType":"limit","qty":"0.001","side":"buy","price":"123.4500","receiveWindow":"5000"});
        assert_eq!(
            uta(
                "id",
                "place-order",
                Some("spot"),
                json!([order.clone()]),
                Some(123)
            )
            .unwrap(),
            json!({"op":"trade","id":"id","topic":"place-order","category":"spot","requestTime":"123","args":[order]})
        );
    }
    #[test]
    fn rejects_mixed_batch_identifiers_and_invalid_numbers() {
        assert!(
            uta(
                "id",
                "batch-cancel",
                None,
                json!([{"orderId":"1"},{"clientOid":"2"}]),
                None
            )
            .is_err()
        );
        assert!(
            uta(
                "id",
                "modify-order",
                Some("spot"),
                json!([{"orderId":"1","price":"NaN"}]),
                None
            )
            .is_err()
        );
        assert!(
            uta(
                "id",
                "modify-order",
                Some("spot"),
                json!([{"orderId":"1","price":"1","requestId":1000000000000000000_u64}]),
                None
            )
            .is_err()
        );
        assert!(uta("id","batch-place",Some("spot"),json!([{"symbol":"BTCUSDT","orderType":"market","qty":"1","side":"buy","reduceOnly":"yes"}]),None).is_err());
    }
}
