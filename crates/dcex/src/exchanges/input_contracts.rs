//! Endpoint-specific decimal declarations shared with the Python boundary.

use crate::{DcexError, Result};
use serde_json::Value;
use std::sync::LazyLock;

static CATALOG: LazyLock<Value> = LazyLock::new(|| {
    serde_json::from_str(include_str!("input_contracts.json")).expect("input contracts")
});

fn resolve(schema: &Value) -> &Value {
    if let Some(reference) = schema["$ref"].as_str() {
        &CATALOG["definitions"][reference.trim_start_matches("#/definitions/")]
    } else {
        schema
    }
}

pub(crate) fn endpoint(exchange: &str, method: &str, websocket: bool) -> &'static Value {
    &CATALOG[if websocket { "websocket" } else { "exchanges" }][exchange][method]
}

pub(crate) fn relative_price(raw: &str) -> bool {
    static PATTERN: LazyLock<regex::Regex> = LazyLock::new(|| {
        let rule = CATALOG["definitions"]["kraken_relative_price"]["pattern"]
            .as_str()
            .expect("relative price rule");
        regex::Regex::new(&format!("^(?:{rule})$")).expect("relative price regex")
    });
    PATTERN.is_match(raw)
}

fn allows_zero(schema: &Value, context: &Value) -> bool {
    let matches = |conditions: &Value| {
        conditions.as_object().is_some_and(|conditions| {
            conditions.iter().all(|(key, allowed)| {
                allowed
                    .as_array()
                    .is_some_and(|values| values.contains(&context[key]))
            })
        })
    };
    let conditions = &schema["x-zero-when"];
    conditions
        .as_array()
        .map_or_else(|| matches(conditions), |groups| groups.iter().any(matches))
}

pub(crate) fn validate(value: &Value, schema: &Value, key: &str) -> Result<()> {
    let schema = resolve(schema);
    let invalid = || DcexError::InvalidInput(format!("{key} requires a plain decimal string"));
    if value.is_null() || schema.is_null() {
        return Ok(());
    }
    if schema["x-empty-as-absent"] == true
        && value.as_str().is_some_and(|raw| raw.trim().is_empty())
    {
        return Ok(());
    }
    if schema["x-delimited-string"] == true
        && let Some(raw) = value.as_str()
        && !raw.trim_start().starts_with('[')
    {
        if raw.split(',').any(|part| part.trim().is_empty()) {
            return Err(DcexError::InvalidInput(format!(
                "{key} requires nonempty comma-separated identifiers"
            )));
        }
        return Ok(());
    }
    if matches!(schema["type"].as_str(), Some("object" | "array"))
        && let Some(raw) = value.as_str()
    {
        let parsed: Value = serde_json::from_str(raw.trim()).map_err(|_| {
            DcexError::InvalidInput(format!(
                "{key} must be a JSON {}",
                schema["type"].as_str().unwrap_or("object")
            ))
        })?;
        return validate(&parsed, schema, key);
    }
    if schema["type"] == "object" && !value.is_object() {
        return Err(DcexError::InvalidInput(format!(
            "{key} must be a JSON object"
        )));
    }
    if schema["x-nonempty-object"] == true
        && value.as_object().is_some_and(|object| object.is_empty())
    {
        return Err(DcexError::InvalidInput(format!(
            "{key} must be a nonempty JSON object"
        )));
    }
    if schema["format"] == "decimal" {
        let raw = match value {
            Value::String(raw) => raw.clone(),
            Value::Number(number)
                if number.is_u64() || number.is_i64() || schema["type"] == "number" =>
            {
                number.to_string()
            }
            _ => return Err(invalid()),
        };
        if schema["x-decimal-sentinels"]
            .as_array()
            .is_some_and(|values| values.iter().any(|value| value.as_str() == Some(&raw)))
        {
            return Ok(());
        }
        if schema["x-relative"] == "kraken_relative_price" && relative_price(&raw) {
            return Ok(());
        }
        let digits = if schema["x-percent"] == true {
            raw.strip_suffix('%').unwrap_or(&raw)
        } else {
            &raw
        };
        let digits = if schema["x-signed"] == true {
            digits.strip_prefix('-').unwrap_or(digits)
        } else {
            digits
        };
        let positive = crate::common::is_positive_plain_decimal(digits);
        let zero = !digits.is_empty()
            && !digits.starts_with('.')
            && !digits.ends_with('.')
            && digits.bytes().all(|b| b == b'0' || b == b'.')
            && digits.bytes().filter(|b| *b == b'.').count() <= 1;
        if zero && schema["x-positive"] == true {
            return Err(DcexError::InvalidInput(format!(
                "{key} must be a positive plain decimal string"
            )));
        }
        if schema["x-percent-range"].is_array() && raw.ends_with('%') {
            let (whole, fraction) = digits.split_once('.').unwrap_or((digits, ""));
            let whole = whole.trim_start_matches('0');
            if !positive
                || whole.len() > 3
                || (whole.len() == 3
                    && (whole > "100" || whole == "100" && fraction.bytes().any(|b| b != b'0')))
            {
                return Err(DcexError::InvalidInput(format!(
                    "{key} requires a decimal percentage greater than 0% and at most 100%"
                )));
            }
        }
        if !(positive || zero && schema["x-positive"] != true) {
            return Err(invalid());
        }
        if let Some(minimum) = schema["x-minimum"].as_str() {
            let order = decimal_order(&raw, minimum);
            if order.is_lt()
                || order.is_eq() && schema["x-exclusive-minimum"] == true
                || zero && schema["x-nonzero"] == true
            {
                return Err(DcexError::InvalidInput(format!(
                    "{key} requires a decimal within its declared range"
                )));
            }
        }
    }
    if let Some(object) = value.as_object() {
        if schema["x-forbidden-keys"].as_array().is_some_and(|keys| {
            keys.iter()
                .filter_map(Value::as_str)
                .any(|name| object.contains_key(name))
        }) {
            return Err(DcexError::InvalidInput(format!(
                "{key} contains unsupported fields"
            )));
        }
        for (name, child) in object {
            let field = &schema["properties"][name];
            if allows_zero(field, value) {
                let mut relaxed = field.clone();
                relaxed["x-positive"] = Value::Bool(false);
                validate(child, &relaxed, name)?;
            } else {
                validate(child, field, name)?;
            }
        }
    }
    if let Some(array) = value.as_array() {
        for child in array {
            validate(child, &schema["items"], key)?;
        }
    }
    Ok(())
}

fn decimal_order(left: &str, right: &str) -> std::cmp::Ordering {
    fn parts(raw: &str) -> (bool, &str, &str) {
        let (whole, fraction) = raw
            .trim_start_matches('-')
            .split_once('.')
            .unwrap_or((raw.trim_start_matches('-'), ""));
        let whole = whole.trim_start_matches('0');
        let fraction = fraction.trim_end_matches('0');
        (
            raw.starts_with('-') && !(whole.is_empty() && fraction.is_empty()),
            whole,
            fraction,
        )
    }
    let (left_negative, left_whole, left_fraction) = parts(left);
    let (right_negative, right_whole, right_fraction) = parts(right);
    if left_negative != right_negative {
        return right_negative.cmp(&left_negative);
    }
    let order = left_whole
        .len()
        .cmp(&right_whole.len())
        .then_with(|| left_whole.cmp(right_whole))
        .then_with(|| {
            let length = left_fraction.len().max(right_fraction.len());
            left_fraction
                .bytes()
                .chain(std::iter::repeat(b'0'))
                .take(length)
                .cmp(
                    right_fraction
                        .bytes()
                        .chain(std::iter::repeat(b'0'))
                        .take(length),
                )
        });
    if left_negative {
        order.reverse()
    } else {
        order
    }
}

pub(crate) fn pairs(exchange: &str, method: &str, pairs: &[(String, String)]) -> Result<()> {
    let schema = endpoint(exchange, method, false);
    let object: serde_json::Map<String, Value> = pairs
        .iter()
        .map(|(key, raw)| (key.clone(), Value::String(raw.clone())))
        .collect();
    let context = Value::Object(object);
    for (key, raw) in pairs {
        let field = &schema["properties"][key];
        let value = Value::String(raw.clone());
        if field["x-repeated-query"] == true {
            validate(&value, &field["items"], key)?;
        } else if allows_zero(field, &context) {
            let mut relaxed = field.clone();
            relaxed["x-positive"] = Value::Bool(false);
            validate(&value, &relaxed, key)?;
        } else {
            validate(&value, field, key)?;
        }
    }
    Ok(())
}

pub(crate) fn input(
    exchange: &str,
    method: &str,
    key: &str,
    value: &impl ToString,
) -> Result<String> {
    let schema = &endpoint(exchange, method, false)["properties"][key];
    if resolve(schema)["format"] == "decimal"
        && matches!(
            std::any::type_name_of_val(value).trim_start_matches('&'),
            "f32" | "f64"
        )
    {
        return Err(DcexError::InvalidInput(format!(
            "{key} requires an exact decimal string, not a float"
        )));
    }
    let raw = value.to_string();
    if !schema["x-zero-when"].is_null() {
        // Typed builders validate sibling-dependent zero controls at dispatch.
        let mut deferred = schema.clone();
        deferred["x-positive"] = Value::Bool(false);
        validate(&Value::String(raw.clone()), &deferred, key)?;
    } else {
        validate(&Value::String(raw.clone()), schema, key)?;
    }
    Ok(raw)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn attached_trigger_ratios_use_exact_signed_bounds_and_delete_controls() {
        for method in [
            "place_order",
            "place_batch_orders",
            "amend_order",
            "amend_algo_order",
            "amend_multiple_orders",
        ] {
            let parent = endpoint("okx", method, false);
            let parent = if method == "place_batch_orders" || method == "amend_multiple_orders" {
                &parent["properties"]["orders"]["items"]
            } else {
                parent
            };
            let attached = &parent["properties"]["attachAlgoOrds"]["items"];
            let amendment = method.starts_with("amend");
            for field in if amendment {
                ["newTpTriggerRatio", "newSlTriggerRatio"]
            } else {
                ["tpTriggerRatio", "slTriggerRatio"]
            } {
                let rule = &attached["properties"][field];
                let tp = field.contains("Tp") || field.starts_with("tp");
                assert_eq!(validate(&json!("-0.1"), rule, field).is_ok(), tp);
                assert_eq!(validate(&json!("0"), rule, field).is_ok(), amendment);
                assert!(validate(&json!("-1"), rule, field).is_err());
                assert!(validate(&json!("-1.000000000000000001"), rule, field).is_err());
                assert!(validate(&json!("0.125000000000000001"), rule, field).is_ok());
            }
            if amendment {
                assert!(validate(&json!({"newSz":"1e-7"}), attached, "attached").is_err());
            }
        }
        assert!(decimal_order("-0.999999999999999999999", "-1").is_gt());
        assert!(decimal_order("-1.000000000000000000001", "-1").is_lt());
        assert!(decimal_order("-0.000", "0").is_eq());
    }

    #[test]
    fn algo_attached_size_is_not_a_documented_field() {
        for alias in ["attachAlgoOrds", "attach_algo_ords"] {
            let schema = endpoint("okx", "place_algo_order", false);
            assert!(validate(&json!({alias:[{"sz":"1"}]}), schema, "algo").is_err());
        }
    }

    fn walk(schema: &Value, count: &mut usize) {
        let schema = resolve(schema);
        if schema["format"] == "decimal" {
            *count += 1;
            validate(&json!("0.125000000000000001"), schema, "value").unwrap();
            for value in [
                json!(true),
                json!("1e-7"),
                json!("NaN"),
                json!("abc"),
                json!(" 1"),
                json!(".1"),
            ] {
                assert!(
                    validate(&value, schema, "value").is_err(),
                    "{schema}: {value}"
                );
            }
            if schema["x-signed"] != true && schema["x-relative"].is_null() {
                assert!(validate(&json!("-3"), schema, "value").is_err());
            }
        }
        if let Some(properties) = schema["properties"].as_object() {
            for child in properties.values() {
                walk(child, count);
            }
        }
        if !schema["items"].is_null() {
            walk(&schema["items"], count);
        }
    }

    #[test]
    fn every_declared_decimal_is_validated() {
        let mut count = 0;
        for protocol in ["exchanges", "websocket"] {
            for methods in CATALOG[protocol].as_object().unwrap().values() {
                for schema in methods.as_object().unwrap().values() {
                    walk(schema, &mut count);
                }
            }
        }
        assert!(count > 2000, "catalog unexpectedly empty: {count}");
    }

    #[test]
    fn typed_inputs_and_relative_rules_are_scoped() {
        assert!(input("binance", "place_order", "icebergQty", &0.1_f64).is_err());
        for value in ["+5", "-5", "#5", "-5%", "+5.25%", "#5.5%"] {
            pairs(
                "kraken",
                "amend_spot_order",
                &[("limit_price".into(), value.into())],
            )
            .unwrap();
            assert!(pairs("binance", "place_order", &[("price".into(), value.into())]).is_err());
        }
        assert!(relative_price("#5%"));
        assert!(!relative_price("+1e-7"));
    }

    #[test]
    fn zero_quantity_requires_both_closing_flags_and_all_pairs_are_checked() {
        let quantity = ("qty".into(), "0".into());
        assert!(pairs("bybit", "place_order", std::slice::from_ref(&quantity)).is_err());
        let closing = vec![
            quantity,
            ("reduceOnly".into(), "true".into()),
            ("closeOnTrigger".into(), "true".into()),
        ];
        pairs("bybit", "place_order", &closing).unwrap();
        let mut duplicate = closing;
        duplicate.insert(0, ("qty".into(), "1e-7".into()));
        assert!(pairs("bybit", "place_order", &duplicate).is_err());
        assert!(input("bybit", "place_order", "qty", &"0").is_ok());
        assert!(input("bybit", "place_order", "qty", &0.1_f64).is_err());
    }

    #[test]
    fn batch_quantities_reject_zero_except_documented_closes() {
        for (exchange, method, array, field) in [
            ("okx", "place_batch_orders", "orders", "sz"),
            ("bybit", "place_batch_order", "request", "qty"),
            ("bingx", "place_swap_batch_order", "batchOrders", "quantity"),
        ] {
            let schema = endpoint(exchange, method, false);
            assert!(validate(&json!({array: [{field: "0"}]}), schema, method).is_err());
            assert!(validate(&json!({array: [{field: "1"}]}), schema, method).is_ok());
        }
        let schema = endpoint("bybit", "place_batch_order", false);
        assert!(
            validate(
                &json!({"request": [{"qty": "0", "reduceOnly": true}]}),
                schema,
                "batch"
            )
            .is_err()
        );
        validate(
            &json!({"request": [{"qty": "0", "reduceOnly": true, "closeOnTrigger": true}]}),
            schema,
            "batch",
        )
        .unwrap();
    }

    #[test]
    fn kraken_zero_volume_requires_a_close_condition() {
        let schema = endpoint("kraken", "place_spot_order", false);
        assert!(
            validate(
                &json!({"volume": "0", "ordertype": "limit", "side": "buy"}),
                schema,
                "order"
            )
            .is_err()
        );
        for condition in [
            json!({"volume": "0", "reduce_only": true}),
            json!({"volume": "0", "ordertype": "settle-position"}),
        ] {
            validate(&condition, schema, "order").unwrap();
        }
    }

    #[test]
    fn percent_quantity_uses_exact_open_closed_bounds() {
        let schema = &endpoint("backpack", "place_order", false)["properties"]["triggerQuantity"];
        for valid in ["0.000000000000000001%", "50%", "100%", "00100.000%"] {
            validate(&json!(valid), schema, "triggerQuantity").unwrap();
        }
        for invalid in ["0%", "150%", "100.000000000000000001%", "-1%"] {
            assert!(validate(&json!(invalid), schema, "triggerQuantity").is_err());
        }
    }
}
