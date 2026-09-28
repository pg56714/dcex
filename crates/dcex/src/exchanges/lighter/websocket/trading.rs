use crate::{DcexError, Result};
use serde_json::{Value, json};

fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(format!("Lighter WebSocket: {message}"))
}

fn transaction(tx_type: u64, tx_info: &str, account: u64) -> Result<Value> {
    if ![14, 15, 16, 17, 20, 28, 29, 41, 42].contains(&tx_type) {
        return Err(invalid("unsupported trading or risk transaction type"));
    }
    let info: Value = serde_json::from_str(tx_info)
        .map_err(|_| invalid("tx_info must encode a signed JSON object"))?;
    let object = info
        .as_object()
        .ok_or_else(|| invalid("tx_info must encode a signed JSON object"))?;
    if object.get("AccountIndex").and_then(Value::as_u64) != Some(account) {
        return Err(invalid(
            "transaction AccountIndex differs from WebSocket account",
        ));
    }
    for key in ["ApiKeyIndex", "Nonce", "ExpiredAt"] {
        if object.get(key).and_then(Value::as_u64).is_none() {
            return Err(invalid(&format!("{key} must be an unsigned integer")));
        }
    }
    if object
        .get("Sig")
        .and_then(Value::as_str)
        .is_none_or(|s| s.is_empty())
    {
        return Err(invalid("signed transaction Sig is required"));
    }
    Ok(info)
}

pub(super) fn single(id: &str, tx_type: u64, tx_info: &str, account: u64) -> Result<Value> {
    if id.trim().is_empty() {
        return Err(invalid("request id must not be empty"));
    }
    Ok(
        json!({"type":"jsonapi/sendtx","data":{"id":id,"tx_type":tx_type,"tx_info":transaction(tx_type,tx_info,account)?}}),
    )
}

pub(super) fn batch(id: &str, types: &[u64], infos: &[String], account: u64) -> Result<Value> {
    if id.trim().is_empty() || types.is_empty() || types.len() > 15 || types.len() != infos.len() {
        return Err(invalid(
            "batch requires an id and 1..15 matching tx_types and tx_infos",
        ));
    }
    for (tx_type, info) in types.iter().zip(infos) {
        transaction(*tx_type, info, account)?;
    }
    Ok(
        json!({"type":"jsonapi/sendtxbatch","data":{"id":id,"tx_types":serde_json::to_string(types).map_err(|e|invalid(&e.to_string()))?,"tx_infos":serde_json::to_string(infos).map_err(|e|invalid(&e.to_string()))?}}),
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn single_is_object_but_batch_is_json_array_of_strings() {
        let info = r#"{"AccountIndex":1,"ApiKeyIndex":2,"Nonce":3,"ExpiredAt":4,"Sig":"signed"}"#;
        assert!(single("id", 15, info, 1).unwrap()["data"]["tx_info"].is_object());
        let frame = batch("id", &[15], &[info.into()], 1).unwrap();
        assert_eq!(
            serde_json::from_str::<Vec<String>>(frame["data"]["tx_infos"].as_str().unwrap())
                .unwrap(),
            vec![info]
        );
        assert!(batch("id", &[15], &[], 1).is_err());
        assert!(single("id", 15, info, 2).is_err());
        assert!(batch("id", &[15; 16], &vec![info.into(); 16], 1).is_err());
    }
}
