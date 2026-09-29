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

pub(crate) fn validate(value: &Value, schema: &Value, key: &str) -> Result<()> {
    let schema = resolve(schema);
    let invalid = || DcexError::InvalidInput(format!("{key} requires a plain decimal string"));
    if value.is_null() || schema.is_null() {
        return Ok(());
    }
    if matches!(schema["type"].as_str(), Some("object" | "array"))
        && let Some(raw) = value.as_str()
    {
        let parsed: Value = serde_json::from_str(raw).map_err(|_| invalid())?;
        return validate(&parsed, schema, key);
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
        if !(positive || zero && schema["x-positive"] != true) {
            return Err(invalid());
        }
    }
    if let Some(object) = value.as_object() {
        for (name, child) in object {
            let field = &schema["properties"][name];
            if field["x-zero-when"].as_object().is_some_and(|conditions| {
                conditions.iter().all(|(key, allowed)| {
                    allowed
                        .as_array()
                        .is_some_and(|values| values.contains(&value[key]))
                })
            }) {
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
        if field["x-zero-when"].as_object().is_some_and(|conditions| {
            conditions.iter().all(|(name, allowed)| {
                allowed
                    .as_array()
                    .is_some_and(|values| values.contains(&context[name]))
            })
        }) {
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
    if schema["x-zero-when"].is_object() {
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
}
