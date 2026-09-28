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
            validate(child, &schema["properties"][name], name)?;
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
    for (key, raw) in pairs {
        validate(&Value::String(raw.clone()), &schema["properties"][key], key)?;
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
    validate(&Value::String(raw.clone()), schema, key)?;
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
}
