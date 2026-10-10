use crate::{DcexError, Result};
use serde_json::{Value, json};

pub(super) fn payload(id: u64, kind: &str, payload: Value) -> Result<Value> {
    let invalid =
        |message: &str| DcexError::InvalidInput(format!("Hyperliquid WebSocket: {message}"));
    let object = payload
        .as_object()
        .ok_or_else(|| invalid("payload must be an object"))?;
    if kind == "info" {
        let name = object
            .get("type")
            .and_then(Value::as_str)
            .filter(|v| !v.trim().is_empty())
            .ok_or_else(|| invalid("info type is required"))?;
        if name == "explorer" {
            return Err(invalid(
                "explorer requests are not supported over WebSocket",
            ));
        }
    } else {
        if let Some(key) = object.keys().find(|key| {
            ![
                "action",
                "nonce",
                "signature",
                "vaultAddress",
                "expiresAfter",
            ]
            .contains(&key.as_str())
        }) {
            return Err(invalid(&format!(
                "unsupported signed action envelope field: {key}"
            )));
        }
        let action = object
            .get("action")
            .and_then(Value::as_object)
            .ok_or_else(|| invalid("action must be an object"))?;
        let name = action
            .get("type")
            .and_then(Value::as_str)
            .ok_or_else(|| invalid("action type is required"))?;
        if ![
            "order",
            "cancel",
            "cancelByCloid",
            "modify",
            "batchModify",
            "scheduleCancel",
            "updateLeverage",
            "updateIsolatedMargin",
            "twapOrder",
            "twapCancel",
            "noop",
            "reserveRequestWeight",
            "agentSetAbstraction",
            "userSetAbstraction",
            "usdClassTransfer",
            "borrowLend",
        ]
        .contains(&name)
        {
            return Err(invalid("unsupported trading or risk action"));
        }
        if object.get("nonce").and_then(Value::as_u64).is_none() {
            return Err(invalid("nonce must be an unsigned integer"));
        }
        let signature = object
            .get("signature")
            .and_then(Value::as_object)
            .ok_or_else(|| invalid("signed action signature is required"))?;
        for key in ["r", "s"] {
            if !signature.get(key).and_then(Value::as_str).is_some_and(|v| {
                v.starts_with("0x")
                    && v.len() == 66
                    && v[2..].bytes().all(|c| c.is_ascii_hexdigit())
            }) {
                return Err(invalid("signature r and s must be 32-byte hex values"));
            }
        }
        if !matches!(signature.get("v").and_then(Value::as_u64), Some(27 | 28)) {
            return Err(invalid("signature v must be 27 or 28"));
        }
        if let Some(vault) = object.get("vaultAddress").filter(|v| !v.is_null()) {
            super::normalize_user(
                vault
                    .as_str()
                    .ok_or_else(|| invalid("invalid vaultAddress"))?,
            )?;
        }
        if object
            .get("expiresAfter")
            .is_some_and(|v| !v.is_null() && v.as_u64().is_none())
        {
            return Err(invalid("expiresAfter must be an unsigned integer"));
        }
    }
    Ok(json!({"method":"post","id":id,"request":{"type":kind,"payload":payload}}))
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn preserves_signed_envelope_and_rejects_unsigned_actions() {
        let action = json!({"action":{"type":"cancel","cancels":[{"a":1,"o":123}]},"nonce":1700000000000_u64,"signature":{"r":format!("0x{}","11".repeat(32)),"s":format!("0x{}","22".repeat(32)),"v":27},"vaultAddress":null,"expiresAfter":1700000001000_u64});
        let frame = payload(123, "action", action.clone()).unwrap();
        assert_eq!(frame["request"]["payload"], action);
        assert_eq!(frame["id"], 123);
        assert!(payload(1, "action", json!({"action":{"type":"cancel"},"nonce":1})).is_err());
        assert!(payload(1, "info", json!({"type":"explorer"})).is_err());
    }
}
