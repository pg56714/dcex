use serde::de::{self, MapAccess, SeqAccess, Visitor};
use serde::Deserialize;
use serde_json::{Number, Value};

use crate::{DcexError, Result};

#[derive(Clone, Debug, PartialEq)]
pub(super) enum OrderedValue {
    Null,
    Bool(bool),
    Int(i64),
    Uint(u64),
    Float(f64),
    String(String),
    Array(Vec<OrderedValue>),
    Object(Vec<(String, OrderedValue)>),
}

impl OrderedValue {
    pub(super) fn to_json(&self) -> Value {
        match self {
            Self::Null => Value::Null,
            Self::Bool(value) => Value::Bool(*value),
            Self::Int(value) => Value::Number(Number::from(*value)),
            Self::Uint(value) => Value::Number(Number::from(*value)),
            Self::Float(value) => Number::from_f64(*value).map_or(Value::Null, Value::Number),
            Self::String(value) => Value::String(value.clone()),
            Self::Array(values) => Value::Array(values.iter().map(Self::to_json).collect()),
            Self::Object(values) => {
                let mut map = serde_json::Map::new();
                for (key, value) in values {
                    map.insert(key.clone(), value.to_json());
                }
                Value::Object(map)
            }
        }
    }
}

impl<'de> Deserialize<'de> for OrderedValue {
    fn deserialize<D>(deserializer: D) -> std::result::Result<Self, D::Error>
    where
        D: serde::Deserializer<'de>,
    {
        deserializer.deserialize_any(OrderedValueVisitor)
    }
}

struct OrderedValueVisitor;

impl<'de> Visitor<'de> for OrderedValueVisitor {
    type Value = OrderedValue;

    fn expecting(&self, formatter: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        formatter.write_str("a JSON value")
    }

    fn visit_bool<E>(self, value: bool) -> std::result::Result<Self::Value, E> {
        Ok(OrderedValue::Bool(value))
    }

    fn visit_i64<E>(self, value: i64) -> std::result::Result<Self::Value, E> {
        Ok(OrderedValue::Int(value))
    }

    fn visit_u64<E>(self, value: u64) -> std::result::Result<Self::Value, E> {
        Ok(OrderedValue::Uint(value))
    }

    fn visit_f64<E>(self, value: f64) -> std::result::Result<Self::Value, E> {
        Ok(OrderedValue::Float(value))
    }

    fn visit_str<E>(self, value: &str) -> std::result::Result<Self::Value, E>
    where
        E: de::Error,
    {
        Ok(OrderedValue::String(value.to_string()))
    }

    fn visit_string<E>(self, value: String) -> std::result::Result<Self::Value, E> {
        Ok(OrderedValue::String(value))
    }

    fn visit_none<E>(self) -> std::result::Result<Self::Value, E> {
        Ok(OrderedValue::Null)
    }

    fn visit_unit<E>(self) -> std::result::Result<Self::Value, E> {
        Ok(OrderedValue::Null)
    }

    fn visit_seq<A>(self, mut seq: A) -> std::result::Result<Self::Value, A::Error>
    where
        A: SeqAccess<'de>,
    {
        let mut values = Vec::new();
        while let Some(value) = seq.next_element()? {
            values.push(value);
        }
        Ok(OrderedValue::Array(values))
    }

    fn visit_map<A>(self, mut map: A) -> std::result::Result<Self::Value, A::Error>
    where
        A: MapAccess<'de>,
    {
        let mut values = Vec::new();
        while let Some((key, value)) = map.next_entry::<String, OrderedValue>()? {
            values.push((key, value));
        }
        Ok(OrderedValue::Object(values))
    }
}

pub(super) fn parse_ordered_json(value: &str, key: &str) -> Result<OrderedValue> {
    serde_json::from_str(value)
        .map_err(|error| DcexError::InvalidInput(format!("invalid JSON parameter {key}: {error}")))
}

pub(super) fn encode_msgpack(value: &OrderedValue) -> Vec<u8> {
    let mut output = Vec::new();
    encode_value(value, &mut output);
    output
}

fn encode_value(value: &OrderedValue, output: &mut Vec<u8>) {
    match value {
        OrderedValue::Null => output.push(0xc0),
        OrderedValue::Bool(false) => output.push(0xc2),
        OrderedValue::Bool(true) => output.push(0xc3),
        OrderedValue::Int(value) => encode_i64(*value, output),
        OrderedValue::Uint(value) => encode_u64(*value, output),
        OrderedValue::Float(value) => {
            output.push(0xcb);
            output.extend_from_slice(&value.to_bits().to_be_bytes());
        }
        OrderedValue::String(value) => encode_str(value, output),
        OrderedValue::Array(values) => {
            encode_array_len(values.len(), output);
            for value in values {
                encode_value(value, output);
            }
        }
        OrderedValue::Object(values) => {
            encode_map_len(values.len(), output);
            for (key, value) in values {
                encode_str(key, output);
                encode_value(value, output);
            }
        }
    }
}

fn encode_i64(value: i64, output: &mut Vec<u8>) {
    if value >= 0 {
        encode_u64(value as u64, output);
    } else if value >= -32 {
        output.push(value as i8 as u8);
    } else if value >= i8::MIN as i64 {
        output.push(0xd0);
        output.push(value as i8 as u8);
    } else if value >= i16::MIN as i64 {
        output.push(0xd1);
        output.extend_from_slice(&(value as i16).to_be_bytes());
    } else if value >= i32::MIN as i64 {
        output.push(0xd2);
        output.extend_from_slice(&(value as i32).to_be_bytes());
    } else {
        output.push(0xd3);
        output.extend_from_slice(&value.to_be_bytes());
    }
}

fn encode_u64(value: u64, output: &mut Vec<u8>) {
    if value <= 0x7f {
        output.push(value as u8);
    } else if u8::try_from(value).is_ok() {
        output.push(0xcc);
        output.push(value as u8);
    } else if u16::try_from(value).is_ok() {
        output.push(0xcd);
        output.extend_from_slice(&(value as u16).to_be_bytes());
    } else if u32::try_from(value).is_ok() {
        output.push(0xce);
        output.extend_from_slice(&(value as u32).to_be_bytes());
    } else {
        output.push(0xcf);
        output.extend_from_slice(&value.to_be_bytes());
    }
}

fn encode_str(value: &str, output: &mut Vec<u8>) {
    let bytes = value.as_bytes();
    let len = bytes.len();
    if len <= 31 {
        output.push(0xa0 | len as u8);
    } else if u8::try_from(len).is_ok() {
        output.push(0xd9);
        output.push(len as u8);
    } else if u16::try_from(len).is_ok() {
        output.push(0xda);
        output.extend_from_slice(&(len as u16).to_be_bytes());
    } else {
        output.push(0xdb);
        output.extend_from_slice(&(len as u32).to_be_bytes());
    }
    output.extend_from_slice(bytes);
}

fn encode_array_len(len: usize, output: &mut Vec<u8>) {
    if len <= 15 {
        output.push(0x90 | len as u8);
    } else if u16::try_from(len).is_ok() {
        output.push(0xdc);
        output.extend_from_slice(&(len as u16).to_be_bytes());
    } else {
        output.push(0xdd);
        output.extend_from_slice(&(len as u32).to_be_bytes());
    }
}

fn encode_map_len(len: usize, output: &mut Vec<u8>) {
    if len <= 15 {
        output.push(0x80 | len as u8);
    } else if u16::try_from(len).is_ok() {
        output.push(0xde);
        output.extend_from_slice(&(len as u16).to_be_bytes());
    } else {
        output.push(0xdf);
        output.extend_from_slice(&(len as u32).to_be_bytes());
    }
}
