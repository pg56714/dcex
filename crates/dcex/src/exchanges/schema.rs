//! Shared schema field validation and wire encoding.
//!
//! Exchange adapters own authentication, symbol conversion and conditional
//! business rules; scalar/JSON types and decimal syntax are enforced here.

use crate::{DcexError, Result};

/// Shared metadata for hand-written adapters with conditional signing rules.
pub(crate) struct Route {
    pub name: &'static str,
    pub path: &'static str,
    pub method: crate::http::HttpMethod,
    pub verb: &'static str,
    pub instruction: &'static str,
    pub is_public: bool,
    pub presigned: bool,
    pub fields: &'static [&'static str],
    pub required: &'static [&'static str],
    pub integers: &'static [&'static str],
    pub decimals: &'static [&'static str],
    pub strings: &'static [&'static str],
}

impl Route {
    pub fn validate<'a>(&self, get: impl Fn(&str) -> Option<&'a str>) -> Result<()> {
        for key in self.required {
            if get(key).is_none() {
                return Err(invalid(key, "required parameter is missing"));
            }
        }
        for key in self.fields.iter().chain(self.strings).chain(self.decimals) {
            if let Some(value) = get(key) {
                let kind = if self.decimals.contains(key) {
                    "decimal"
                } else if self.integers.contains(key) {
                    "uint"
                } else if value.starts_with('{') || value.starts_with('[') {
                    "json"
                } else {
                    "string"
                };
                encode(key, value, kind)?;
            }
        }
        Ok(())
    }
}

pub(crate) fn route(
    cache: &'static std::sync::OnceLock<Vec<Route>>,
    raw: &str,
    name: &str,
) -> Option<&'static Route> {
    cache
        .get_or_init(|| {
            load_tables(&[raw])
                .iter()
                .map(|row| {
                    let text = |key| row[key].as_str().unwrap_or("");
                    let strings = |key| {
                        if row[key].is_array() {
                            static_strings(&row[key])
                        } else {
                            &[]
                        }
                    };
                    Route {
                        name: text("name"),
                        path: text("path"),
                        method: match text("method").trim_start_matches("HttpMethod::") {
                            "Post" | "POST" => crate::http::HttpMethod::Post,
                            "Put" | "PUT" => crate::http::HttpMethod::Put,
                            "Delete" | "DELETE" => crate::http::HttpMethod::Delete,
                            "Patch" | "PATCH" => crate::http::HttpMethod::Patch,
                            _ => crate::http::HttpMethod::Get,
                        },
                        verb: text("verb"),
                        instruction: text("instruction"),
                        is_public: row["is_public"].as_bool().unwrap_or(false),
                        presigned: row["presigned"].as_bool().unwrap_or(false),
                        fields: strings("fields"),
                        required: strings("required"),
                        integers: strings("integers"),
                        decimals: strings("decimals"),
                        strings: strings("strings"),
                    }
                })
                .collect()
        })
        .iter()
        .find(|route| route.name == name)
}

// Embedded catalogs are loaded once by each generated LazyLock. Their borrowed
// strings and slices intentionally live for the process lifetime, like the
// former compiled Rust constants; no request allocates catalog metadata.
pub(crate) fn load_tables(sources: &[&str]) -> &'static [Value] {
    let rows: Vec<Value> = sources
        .iter()
        .flat_map(|raw| {
            serde_json::from_str::<Vec<Value>>(raw).expect("checked endpoint table JSON")
        })
        .collect();
    Box::leak(rows.into_boxed_slice())
}

pub(crate) fn static_strings(value: &'static Value) -> &'static [&'static str] {
    let strings: Vec<_> = value
        .as_array()
        .expect("schema list")
        .iter()
        .map(|value| value.as_str().expect("schema string"))
        .collect();
    Box::leak(strings.into_boxed_slice())
}

pub(crate) fn static_fields<T>(
    value: &'static Value,
    convert: impl Fn(&'static Value) -> T,
) -> &'static [T] {
    Box::leak(
        value
            .as_array()
            .expect("schema fields")
            .iter()
            .map(convert)
            .collect::<Vec<_>>()
            .into_boxed_slice(),
    )
}
use serde::Deserialize;
use serde_json::{Map, Value};

fn invalid(key: &str, message: &str) -> DcexError {
    DcexError::InvalidInput(format!("{key}: {message}"))
}

/// Common field format used by all schema catalogs.
#[derive(Debug)]
pub(crate) struct Field {
    pub name: String,
    pub kind: String,
    pub required: bool,
    pub schema: Value,
    pub location: String,
}

impl<'de> Deserialize<'de> for Field {
    fn deserialize<D: serde::Deserializer<'de>>(
        deserializer: D,
    ) -> std::result::Result<Self, D::Error> {
        let value = Value::deserialize(deserializer)?;
        let name = value
            .get("wire")
            .or_else(|| value.get("name"))
            .or_else(|| value.get("key"))
            .and_then(Value::as_str)
            .ok_or_else(|| serde::de::Error::custom("field name is required"))?;
        Ok(Self {
            name: name.into(),
            kind: value
                .get("kind")
                .or_else(|| value.get("type"))
                .and_then(Value::as_str)
                .unwrap_or("string")
                .into(),
            required: value["required"].as_bool().unwrap_or(false),
            schema: value.get("schema").cloned().unwrap_or(Value::Null),
            location: value["location"].as_str().unwrap_or("").into(),
        })
    }
}

impl Field {
    pub fn encode(&self, raw: &str) -> Result<Value> {
        let kind = if self.schema["format"] == "decimal" {
            "decimal"
        } else {
            self.schema["type"].as_str().unwrap_or(&self.kind)
        };
        if self.schema.is_null() {
            return encode(&self.name, raw, kind);
        }
        let value = encode_shape(decode(&self.name, raw, kind)?, &self.schema, &self.name)?;
        validate(&value, &self.schema, &self.name)?;
        Ok(value)
    }
}

/// Validate required/unknown/duplicate fields and encode a catalog request.
pub(crate) fn request(fields: &[Field], pairs: &[(String, String)]) -> Result<Map<String, Value>> {
    let mut output = Map::new();
    for (key, raw) in pairs {
        let field = fields
            .iter()
            .find(|field| field.name == *key)
            .ok_or_else(|| invalid(key, "unknown parameter"))?;
        if field.required && raw.trim().is_empty() {
            return Err(invalid(key, "required parameter is empty"));
        }
        if output.insert(key.clone(), field.encode(raw)?).is_some() {
            return Err(invalid(key, "duplicate parameter"));
        }
    }
    for field in fields {
        if field.required && !output.contains_key(&field.name) {
            return Err(invalid(&field.name, "required parameter is missing"));
        }
    }
    Ok(output)
}

pub(crate) fn request_in_schema_order(
    fields: &[Field],
    pairs: &[(String, String)],
) -> Result<Map<String, Value>> {
    let mut values = request(fields, pairs)?;
    Ok(fields
        .iter()
        .filter_map(|field| {
            values
                .shift_remove(&field.name)
                .map(|value| (field.name.clone(), value))
        })
        .collect())
}

pub(crate) fn decimal_field(key: &str) -> bool {
    matches!(
        key.replace('_', "").to_ascii_lowercase().as_str(),
        "price"
            | "quantity"
            | "qty"
            | "amount"
            | "size"
            | "volume"
            | "vol"
            | "notional"
            | "funds"
            | "sz"
            | "px"
            | "amt"
            | "submittedquantity"
            | "submittedprice"
            | "limitprice"
            | "stopprice"
            | "triggerprice"
            | "activationprice"
            | "callbackrate"
            | "newqty"
            | "newquantity"
            | "origqty"
            | "quoteorderqty"
            | "baseqty"
            | "quoteqty"
            | "orderqty"
            | "orderprice"
            | "orderamount"
            | "minprice"
            | "maxprice"
            | "lowerprice"
            | "upperprice"
            | "investment"
            | "totalinvestment"
            | "reservedmargin"
            | "takeprofit"
            | "stoploss"
            | "tpprice"
            | "slprice"
            | "tptriggerpx"
            | "sltriggerpx"
            | "tpordpx"
            | "slordpx"
            | "execqty"
            | "execprice"
            | "baseamount"
            | "quoteamount"
            | "newprice"
            | "entryprice"
            | "bidprice"
            | "askprice"
            | "openprice"
            | "openamount"
            | "trailingamount"
            | "monitorprice"
            | "takeprofitprice"
            | "stoplossprice"
            | "investmentamount"
            | "tokenizedassetamount"
            | "underlyingassetamount"
            | "price2"
    )
}

pub(crate) fn input(key: &str, value: &impl ToString) -> Result<String> {
    if decimal_field(key)
        && matches!(
            std::any::type_name_of_val(value).trim_start_matches('&'),
            "f32" | "f64"
        )
    {
        return Err(invalid(
            key,
            "requires an exact decimal string, not a float",
        ));
    }
    let text = value.to_string();
    if matches!(key, "price" | "price2") && relative_price(&text) {
        return Ok(text);
    }
    if key == "amount" && text.starts_with('-') && plain(&text[1..], false) {
        return Ok(text);
    }
    validate_pairs(&[(key.into(), text.clone())])?;
    Ok(text)
}

pub(crate) fn relative_price(raw: &str) -> bool {
    raw.strip_prefix(['+', '-'])
        .is_some_and(|value| plain(value.strip_suffix('%').unwrap_or(value), false))
}

fn plain(value: &str, positive: bool) -> bool {
    if crate::common::is_positive_plain_decimal(value) {
        return true;
    }
    !positive
        && !value.is_empty()
        && value.bytes().all(|b| b == b'0' || b == b'.')
        && value.bytes().filter(|b| *b == b'.').count() <= 1
        && !value.starts_with('.')
        && !value.ends_with('.')
}

/// Check financial values recursively without converting them through f64.
pub(crate) fn validate_numbers(value: &Value, key: &str) -> Result<()> {
    match value {
        Value::Object(items) => {
            for (name, item) in items {
                validate_numbers(item, name)?;
            }
        }
        Value::Array(items) => {
            for item in items {
                validate_numbers(item, key)?;
            }
        }
        _ if decimal_field(key) => {
            let valid = match value {
                Value::String(raw) => {
                    plain(raw, false) || (matches!(key, "tpOrdPx" | "slOrdPx") && raw == "-1")
                }
                Value::Number(number) => number.is_u64(),
                _ => false,
            };
            if !valid {
                return Err(invalid(key, "requires a nonnegative plain decimal string"));
            }
        }
        _ => {}
    }
    Ok(())
}

fn decode(key: &str, raw: &str, kind: &str) -> Result<Value> {
    if kind == "number" {
        if !plain(raw, false) {
            return Err(invalid(key, "requires a nonnegative plain decimal"));
        }
        return serde_json::from_str::<serde_json::Number>(raw)
            .map(Value::Number)
            .map_err(|_| invalid(key, "requires a JSON decimal"));
    }
    let value = match kind {
        "int" | "integer" | "int64" | "long" | "i" => Value::from(
            raw.parse::<i64>()
                .map_err(|_| invalid(key, "requires an integer"))?,
        ),
        "uint" => Value::from(
            raw.parse::<u64>()
                .map_err(|_| invalid(key, "requires an unsigned integer"))?,
        ),
        "bool" | "boolean" | "b" => Value::from(
            raw.parse::<bool>()
                .map_err(|_| invalid(key, "requires true or false"))?,
        ),
        "decimal" | "positive" | "d" => {
            if !plain(raw, true) {
                return Err(invalid(key, "requires a positive plain decimal string"));
            }
            Value::String(raw.into())
        }
        kind if kind.starts_with("array")
            || kind.ends_with("[]")
            || kind == "object"
            || kind == "json" =>
        {
            let value: Value =
                serde_json::from_str(raw).map_err(|_| invalid(key, "requires JSON"))?;
            if ((kind.starts_with("array") || kind.ends_with("[]")) && !value.is_array())
                || (kind == "object" && !value.is_object())
            {
                return Err(invalid(key, "has the wrong JSON type"));
            }
            value
        }
        _ => Value::String(raw.into()),
    };
    Ok(value)
}

pub(crate) fn encode(key: &str, raw: &str, kind: &str) -> Result<Value> {
    let value = decode(key, raw, kind)?;
    if kind != "number" {
        validate_numbers(&value, key)?;
    }
    Ok(value)
}

/// Validate native pairs before an adapter performs symbol or body conversion.
pub(crate) fn validate_pairs(pairs: &[(String, String)]) -> Result<()> {
    for (key, raw) in pairs {
        if raw.starts_with('{') || raw.starts_with('[') {
            if let Ok(value) = serde_json::from_str::<Value>(raw) {
                validate_numbers(&value, key)?;
            }
        } else {
            validate_numbers(&Value::String(raw.clone()), key)?;
        }
    }
    Ok(())
}

/// Convert exact string decimals to documented JSON numbers without f64.
pub(crate) fn encode_shape(mut value: Value, schema: &Value, key: &str) -> Result<Value> {
    if schema["type"] == "number" {
        let raw = value
            .as_str()
            .map(str::to_owned)
            .unwrap_or_else(|| value.to_string());
        let digits = if schema["x-signed"] == true {
            raw.strip_prefix('-').unwrap_or(&raw)
        } else {
            &raw
        };
        if !plain(digits, false) {
            return Err(invalid(key, "requires a plain decimal number"));
        }
        return serde_json::from_str::<serde_json::Number>(&raw)
            .map(Value::Number)
            .map_err(|_| invalid(key, "invalid JSON number"));
    }
    if let Some(object) = value.as_object_mut() {
        for (name, child) in object {
            *child = encode_shape(child.take(), &schema["properties"][name], name)?;
        }
    } else if let Some(items) = value.as_array_mut() {
        for item in items {
            *item = encode_shape(item.take(), &schema["items"], key)?;
        }
    }
    Ok(value)
}

/// Recursive JSON-schema constraints shared by catalog adapters.
pub(crate) fn validate(value: &Value, schema: &Value, key: &str) -> Result<()> {
    validate_with(value, schema, key, false, false)
}

pub(crate) fn validate_with(
    value: &Value,
    schema: &Value,
    key: &str,
    closed: bool,
    nonempty: bool,
) -> Result<()> {
    if !value.is_object() && !value.is_array() {
        if schema["type"] == "number" && decimal_field(key) {
            let raw = value.to_string();
            let digits = if schema["x-signed"] == true {
                raw.strip_prefix('-').unwrap_or(&raw)
            } else {
                &raw
            };
            if !plain(digits, false) {
                return Err(invalid(key, "requires a plain decimal number"));
            }
        } else {
            validate_numbers(value, key)?;
        }
    }
    if let Some(branches) = schema["allOf"].as_array() {
        for branch in branches {
            validate_with(value, branch, key, closed, nonempty)?;
        }
    }
    if let Some(branches) = schema["oneOf"].as_array() {
        let branches: Vec<_> = branches
            .iter()
            .filter(|branch| {
                branch["properties"]
                    .as_object()
                    .is_none_or(|props| props.keys().any(|k| value.get(k).is_some()))
            })
            .collect();
        if branches.len() != 1 {
            return Err(invalid(key, "requires exactly one documented variant"));
        }
        validate_with(value, branches[0], key, closed, nonempty)?;
    }
    let valid = match schema["type"].as_str() {
        Some("string") => value.is_string(),
        Some("integer") => value.is_i64() || value.is_u64(),
        Some("number") => value.is_number() || value.as_str().is_some_and(|v| plain(v, false)),
        Some("boolean") => value.is_boolean(),
        Some("array") => value.is_array(),
        Some("object") => value.is_object(),
        _ => true,
    };
    if !valid {
        return Err(invalid(key, "has the wrong JSON type"));
    }
    if let Some(choices) = schema["enum"].as_array()
        && !choices.contains(value)
    {
        return Err(invalid(key, "is outside the allowed values"));
    }
    if let Some(number) = value.as_f64()
        && (schema["minimum"]
            .as_f64()
            .is_some_and(|v| number < v || number == v && schema["exclusiveMinimum"] == true)
            || schema["maximum"].as_f64().is_some_and(|v| number > v))
    {
        return Err(invalid(key, "is outside the documented range"));
    }
    if let Some(items) = value.as_array() {
        if schema["minItems"]
            .as_u64()
            .is_some_and(|n| items.len() < n as usize)
            || schema["maxItems"]
                .as_u64()
                .is_some_and(|n| items.len() > n as usize)
        {
            return Err(invalid(key, "array length is outside the documented range"));
        }
        for item in items {
            validate_with(item, &schema["items"], key, closed, nonempty)?;
        }
    }
    if let Some(object) = value.as_object() {
        if let Some(required) = schema["required"].as_array() {
            for field in required.iter().filter_map(Value::as_str) {
                if !object.contains_key(field) {
                    return Err(invalid(field, "required nested field is missing"));
                }
            }
        }
        for (field, item) in object {
            if (closed || schema["additionalProperties"] == false)
                && schema["properties"].get(field).is_none()
            {
                return Err(invalid(field, "unknown nested field"));
            }
            validate_with(item, &schema["properties"][field], field, closed, nonempty)?;
        }
    }
    if let Some(raw) = value.as_str() {
        if schema["format"] == "decimal" && !plain(raw, true) {
            return Err(invalid(key, "requires a positive plain decimal string"));
        }
        if (nonempty && raw.trim().is_empty() && schema["x-allow-empty"] != true)
            || schema["minLength"]
                .as_u64()
                .is_some_and(|n| raw.chars().count() < n as usize)
            || schema["maxLength"]
                .as_u64()
                .is_some_and(|n| raw.chars().count() > n as usize)
        {
            return Err(invalid(key, "has an invalid string length"));
        }
        if let Some(pattern) = schema["pattern"].as_str() {
            // Nonzero cryptographic scalars are checked by the signing adapter.
            let pattern = pattern.replace("(?=.*[1-9a-fA-F])", "");
            if !regex::Regex::new(&pattern)
                .map_err(|_| invalid(key, "invalid embedded pattern"))?
                .is_match(raw)
            {
                return Err(invalid(key, "has an invalid format"));
            }
        }
        if schema["format"] == "uuid"
            && !(raw.len() == 36
                && raw.bytes().enumerate().all(|(i, b)| {
                    if [8, 13, 18, 23].contains(&i) {
                        b == b'-'
                    } else {
                        b.is_ascii_hexdigit()
                    }
                }))
        {
            return Err(invalid(key, "requires a UUID"));
        }
    }
    Ok(())
}

/// Form encoding with an explicit indexed-key policy; values are always escaped.
pub(crate) fn form(pairs: &[(String, String)], literal_brackets: bool) -> String {
    pairs
        .iter()
        .map(|(key, value)| {
            let mut encoded = url::form_urlencoded::Serializer::new(String::new());
            encoded.append_pair(key, value);
            let encoded = encoded.finish();
            if literal_brackets {
                let (key, value) = encoded.split_once('=').expect("encoded pair");
                format!("{}={value}", key.replace("%5B", "[").replace("%5D", "]"))
            } else {
                encoded
            }
        })
        .collect::<Vec<_>>()
        .join("&")
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn decimal_syntax_preserves_arbitrary_precision() {
        for value in ["1e-7", "1E7", "-3", "abc", "NaN", "inf", ".1", "1.", " 1"] {
            assert!(
                encode("submittedPrice", value, "string").is_err(),
                "{value}"
            );
            assert!(encode("investment", value, "decimal").is_err(), "{value}");
        }
        let exact = format!("0.{}12345678901234567890123456789", "0".repeat(400));
        assert_eq!(encode("price", &exact, "decimal").unwrap(), json!(exact));
        assert_eq!(
            encode("price", &exact, "number").unwrap().to_string(),
            exact
        );
        assert!(validate_numbers(&json!({"orders": [{"price": 0.3}]}), "args").is_err());
        assert!(validate_numbers(&json!({"orders": [{"price": "1e-3"}]}), "args").is_err());
    }

    #[test]
    fn field_catalog_handles_wire_names_and_types_without_losing_them() {
        let fields: Vec<Field> = serde_json::from_value(json!([
            {"name": "submitted_price", "wire": "submittedPrice", "type": "str", "kind": "decimal", "required": true},
            {"name": "count", "type": "integer"},
            {"name": "active", "type": "boolean"},
            {"name": "orders", "type": "array"}
        ])).unwrap();
        let values = vec![
            ("submittedPrice".into(), "0.0000001".into()),
            ("count".into(), "3".into()),
            ("active".into(), "true".into()),
            ("orders".into(), r#"[{"qty":"2"}]"#.into()),
        ];
        let body = request(&fields, &values).unwrap();
        assert_eq!(
            Value::Object(body),
            json!({"submittedPrice":"0.0000001", "count":3, "active":true, "orders":[{"qty":"2"}]})
        );
        assert!(request(&fields, &[]).is_err());
        let mut duplicate = values.clone();
        duplicate.push(values[0].clone());
        assert!(request(&fields, &duplicate).is_err());
    }

    #[test]
    fn indexed_form_keys_preserve_brackets_but_values_remain_escaped() {
        let pairs = vec![("cancelInfoList[0].clientOrderId".into(), "a[b]&= +".into())];
        assert_eq!(
            form(&pairs, true),
            "cancelInfoList[0].clientOrderId=a%5Bb%5D%26%3D+%2B"
        );
        assert_eq!(
            form(&pairs, false),
            "cancelInfoList%5B0%5D.clientOrderId=a%5Bb%5D%26%3D+%2B"
        );
    }

    #[test]
    fn schema_decimal_format_does_not_depend_on_field_name() {
        let shape = json!({"type": "string", "format": "decimal"});
        for raw in ["-1", "1e-5", "abc", "0"] {
            assert!(validate(&json!(raw), &shape, "bid").is_err());
        }
        assert!(validate(&json!("0.000000000000000000001"), &shape, "bid").is_ok());
    }

    #[test]
    fn signed_json_numbers_require_explicit_schema_and_keep_precision() {
        let shape = json!({"type": "object", "properties": {
            "size": {"type": "number", "x-signed": true},
            "entryPrice": {"type": "number"}
        }});
        let raw =
            json!({"size": "-1.25000000000000000001", "entryPrice": "60000.250000000000000001"});
        let encoded = encode_shape(raw, &shape, "position").unwrap();
        validate(&encoded, &shape, "position").unwrap();
        assert_eq!(encoded["size"].to_string(), "-1.25000000000000000001");
        assert_eq!(
            encoded["entryPrice"].to_string(),
            "60000.250000000000000001"
        );
        assert!(encode_shape(json!("-1"), &json!({"type":"number"}), "price").is_err());
    }
}
