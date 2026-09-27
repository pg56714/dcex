//! Current Spot WebSocket v2 trading parameters; deprecated aliases are excluded.
use crate::{DcexError, Result};
use serde_json::{Map, Value};

const ORDER_FIELDS: &[&str] = &[
    "order_type",
    "side",
    "order_qty",
    "symbol",
    "limit_price",
    "limit_price_type",
    "triggers",
    "time_in_force",
    "margin",
    "post_only",
    "reduce_only",
    "effective_time",
    "expire_time",
    "deadline",
    "cl_ord_id",
    "order_userref",
    "conditional",
    "display_qty",
    "fee_preference",
    "stp_type",
    "cash_order_qty",
    "validate",
    "sender_sub_id",
];

pub(super) fn validate(method: &str, params: &Value) -> Result<()> {
    let object = params
        .as_object()
        .ok_or_else(|| invalid("params must be a JSON object"))?;
    let fields: &[&str] = match method {
        "add_order" => ORDER_FIELDS,
        "amend_order" => &[
            "order_id",
            "cl_ord_id",
            "order_qty",
            "display_qty",
            "limit_price",
            "limit_price_type",
            "post_only",
            "trigger_price",
            "trigger_price_type",
            "deadline",
            "symbol",
        ],
        "cancel_order" => &["order_id", "cl_ord_id", "order_userref"],
        "cancel_all" => &[],
        "cancel_after" => &["timeout"],
        "batch_add" => &["symbol", "orders", "deadline", "validate"],
        "batch_cancel" => &["orders", "cl_ord_id"],
        _ => return Err(invalid("unsupported trading method")),
    };
    allowed(object, fields)?;
    validate_scalars(object)?;
    match method {
        "add_order" => validate_order(params, true)?,
        "amend_order" => {
            exactly_one(object, &["order_id", "cl_ord_id"])?;
            for key in ["order_id", "cl_ord_id"] {
                if object.contains_key(key) {
                    text(params, key)?;
                }
            }
            if !["order_qty", "display_qty", "limit_price", "trigger_price"]
                .iter()
                .any(|k| object.contains_key(*k))
            {
                return Err(invalid("amend requires a quantity or price change"));
            }
        }
        "cancel_after" => {
            if !params["timeout"].as_u64().is_some_and(|v| v < 86_400) {
                return Err(invalid("timeout must be an integer from 0 to 86399"));
            }
        }
        "cancel_order" | "batch_cancel" => {
            let keys = if method == "cancel_order" {
                &["order_id", "cl_ord_id", "order_userref"][..]
            } else {
                &["orders", "cl_ord_id"][..]
            };
            let mut count = 0;
            for k in keys {
                if let Some(v) = object.get(*k) {
                    let values = v
                        .as_array()
                        .filter(|v| !v.is_empty())
                        .ok_or_else(|| invalid("cancel identifiers must be nonempty arrays"))?;
                    for value in values {
                        let valid = if *k == "order_userref" {
                            value.as_i64().is_some_and(|v| i32::try_from(v).is_ok())
                        } else {
                            value.as_str().is_some_and(|v| !v.is_empty())
                        };
                        if !valid {
                            return Err(invalid("invalid cancel identifier type"));
                        }
                    }
                    count += values.len();
                }
            }
            if count == 0 || (method == "batch_cancel" && count > 50) {
                return Err(invalid("cancel list is empty or exceeds batch limit 50"));
            }
            if method == "cancel_order" {
                exactly_one(object, keys)?;
            }
        }
        "batch_add" => {
            text(params, "symbol")?;
            let orders = params["orders"]
                .as_array()
                .filter(|v| (2..=15).contains(&v.len()))
                .ok_or_else(|| invalid("batch_add requires 2..=15 orders"))?;
            for order in orders {
                let object = order
                    .as_object()
                    .ok_or_else(|| invalid("batch order must be an object"))?;
                allowed(object, ORDER_FIELDS)?;
                if ["symbol", "token", "deadline", "validate"]
                    .iter()
                    .any(|k| object.contains_key(*k))
                {
                    return Err(invalid(
                        "batch order cannot override batch-level parameters",
                    ));
                }
                validate_order(order, false)?;
            }
        }
        _ => {}
    }
    Ok(())
}

fn validate_order(params: &Value, has_symbol: bool) -> Result<()> {
    let object = params
        .as_object()
        .ok_or_else(|| invalid("order must be an object"))?;
    validate_scalars(object)?;
    let kind = text(params, "order_type")?;
    if ![
        "limit",
        "market",
        "iceberg",
        "stop-loss",
        "stop-loss-limit",
        "take-profit",
        "take-profit-limit",
        "trailing-stop",
        "trailing-stop-limit",
        "settle-position",
    ]
    .contains(&kind)
    {
        return Err(invalid("unsupported order_type"));
    }
    if !["buy", "sell"].contains(&text(params, "side")?) {
        return Err(invalid("side must be buy or sell"));
    }
    if has_symbol {
        text(params, "symbol")?;
    }
    exactly_one(object, &["order_qty", "cash_order_qty"])?;
    if params.get("cash_order_qty").is_some()
        && (kind != "market" || params["side"] != "buy" || params["margin"] == true)
    {
        return Err(invalid(
            "cash_order_qty requires a buy market order without margin",
        ));
    }
    if matches!(
        kind,
        "limit" | "iceberg" | "stop-loss-limit" | "take-profit-limit" | "trailing-stop-limit"
    ) && params.get("limit_price").is_none()
    {
        return Err(invalid("limit_price is required"));
    }
    if kind != "trailing-stop-limit"
        && params
            .get("limit_price")
            .and_then(Value::as_f64)
            .is_some_and(|v| v <= 0.0)
    {
        return Err(invalid(
            "limit_price must be positive for non-trailing orders",
        ));
    }
    if kind == "iceberg" {
        let display = params["display_qty"]
            .as_f64()
            .ok_or_else(|| invalid("iceberg requires display_qty"))?;
        let total = params["order_qty"]
            .as_f64()
            .ok_or_else(|| invalid("iceberg requires order_qty"))?;
        if display > total || display * 15.0 < total {
            return Err(invalid(
                "display_qty must be between order_qty/15 and order_qty",
            ));
        }
    }
    let triggered = matches!(
        kind,
        "stop-loss"
            | "stop-loss-limit"
            | "take-profit"
            | "take-profit-limit"
            | "trailing-stop"
            | "trailing-stop-limit"
    );
    if triggered {
        let triggers = params["triggers"]
            .as_object()
            .ok_or_else(|| invalid("triggered orders require triggers"))?;
        allowed(triggers, &["reference", "price", "price_type"])?;
        if !triggers
            .get("price")
            .and_then(Value::as_f64)
            .is_some_and(f64::is_finite)
        {
            return Err(invalid("trigger price must be a JSON number"));
        }
        enum_field(triggers, "reference", &["last", "index"])?;
        enum_field(triggers, "price_type", &["static", "pct", "quote"])?;
        if triggers
            .get("price_type")
            .and_then(Value::as_str)
            .unwrap_or("static")
            == "static"
            && triggers["price"].as_f64().is_some_and(|v| v <= 0.0)
        {
            return Err(invalid("static trigger price must be positive"));
        }
    } else if params.get("triggers").is_some() {
        return Err(invalid("triggers require a triggered order type"));
    }
    if params["post_only"] == true
        && params
            .get("time_in_force")
            .is_some_and(|v| v == "ioc" || v == "fok")
    {
        return Err(invalid("post_only is incompatible with ioc/fok"));
    }
    if params["time_in_force"] == "gtd" {
        text(params, "expire_time")?;
    }
    if object.contains_key("cl_ord_id") && object.contains_key("order_userref") {
        return Err(invalid(
            "cl_ord_id and order_userref are mutually exclusive",
        ));
    }
    if let Some(conditional) = object.get("conditional") {
        let conditional = conditional
            .as_object()
            .ok_or_else(|| invalid("conditional must be an object"))?;
        allowed(
            conditional,
            &[
                "order_type",
                "limit_price",
                "limit_price_type",
                "trigger_price",
                "trigger_price_type",
            ],
        )?;
        validate_scalars(conditional)?;
        enum_field(
            conditional,
            "order_type",
            &[
                "limit",
                "stop-loss",
                "stop-loss-limit",
                "take-profit",
                "take-profit-limit",
                "trailing-stop",
                "trailing-stop-limit",
            ],
        )?;
    }
    Ok(())
}
fn validate_scalars(object: &Map<String, Value>) -> Result<()> {
    for k in ["order_qty", "cash_order_qty", "display_qty"] {
        if let Some(v) = object.get(k) {
            if !v.as_f64().is_some_and(|v| v.is_finite() && v > 0.0) {
                return Err(invalid("quantity must be a positive JSON number"));
            }
        }
    }
    for k in ["limit_price", "trigger_price"] {
        if let Some(v) = object.get(k) {
            if !v.as_f64().is_some_and(f64::is_finite) {
                return Err(invalid("price must be a JSON number"));
            }
        }
    }
    for k in ["margin", "post_only", "reduce_only", "validate"] {
        if object.get(k).is_some_and(|v| !v.is_boolean()) {
            return Err(invalid("boolean fields require JSON booleans"));
        }
    }
    for (k, v) in object {
        if v.is_string() && v.as_str().is_some_and(|v| v.is_empty()) {
            return Err(invalid(&format!("{k} cannot be empty")));
        }
    }
    if let Some(v) = object.get("order_userref") {
        if !v.is_array() && !v.as_i64().is_some_and(|v| i32::try_from(v).is_ok()) {
            return Err(invalid("order_userref must be int32"));
        }
    }
    enum_field(object, "time_in_force", &["gtc", "gtd", "ioc", "fok"])?;
    enum_field(object, "fee_preference", &["base", "quote"])?;
    enum_field(
        object,
        "stp_type",
        &["cancel_newest", "cancel_oldest", "cancel_both"],
    )?;
    enum_field(object, "limit_price_type", &["static", "pct", "quote"])?;
    enum_field(object, "trigger_price_type", &["static", "pct", "quote"])?;
    Ok(())
}
fn allowed(object: &Map<String, Value>, keys: &[&str]) -> Result<()> {
    if object.keys().any(|k| !keys.contains(&k.as_str())) {
        return Err(invalid("unsupported or deprecated trading parameter"));
    }
    Ok(())
}
fn enum_field(object: &Map<String, Value>, key: &str, values: &[&str]) -> Result<()> {
    if let Some(v) = object.get(key) {
        if !v.as_str().is_some_and(|v| values.contains(&v)) {
            return Err(invalid(&format!("unsupported {key}")));
        }
    }
    Ok(())
}
fn exactly_one(object: &Map<String, Value>, keys: &[&str]) -> Result<()> {
    if keys.iter().filter(|k| object.contains_key(**k)).count() != 1 {
        return Err(invalid(&format!(
            "provide exactly one of {}",
            keys.join(", ")
        )));
    }
    Ok(())
}
fn text<'a>(params: &'a Value, key: &str) -> Result<&'a str> {
    params[key]
        .as_str()
        .filter(|v| !v.is_empty())
        .ok_or_else(|| invalid(&format!("{key} is required")))
}
fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(format!("Kraken Spot WebSocket: {message}"))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    #[test]
    fn rejects_wrong_identifiers_and_numeric_types() {
        for (method, params) in [
            ("amend_order", json!({"order_id":12,"order_qty":1})),
            (
                "cancel_order",
                json!({"order_id":["id"],"cl_ord_id":["client"]}),
            ),
            ("cancel_order", json!({"order_userref":["12"]})),
            ("cancel_after", json!({"timeout":86400})),
            (
                "add_order",
                json!({"symbol":"BTC/USD","side":"buy","order_type":"limit","order_qty":"1","limit_price":100}),
            ),
            (
                "add_order",
                json!({"symbol":"BTC/USD","side":"buy","order_type":"limit","order_qty":1,"limit_price":0}),
            ),
        ] {
            assert!(validate(method, &params).is_err(), "{method}: {params}");
        }
    }
    #[test]
    fn preserves_trailing_limit_offsets_and_batch_userrefs() {
        validate("add_order",&json!({"symbol":"BTC/USD","side":"sell","order_type":"trailing-stop-limit","order_qty":1,"limit_price":0,"limit_price_type":"quote","triggers":{"price":5,"price_type":"pct"}})).unwrap();
        validate(
            "batch_cancel",
            &json!({"orders":["12","ORDERX-IDXXX-XXXXX3"]}),
        )
        .unwrap();
    }
}
