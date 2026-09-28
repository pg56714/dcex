//! Wallet-authorized API key administration. Signatures are supplied by the caller.
use super::ArcusClient;
use crate::exchange::ValidatedResponse;
use crate::http::{HttpMethod, HttpRequest};
use crate::{DcexError, Result};
use serde_json::Value;

fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(format!("Arcus: {message}"))
}
fn address(value: &str) -> bool {
    value
        .strip_prefix("0x")
        .is_some_and(|s| s.len() == 40 && s.bytes().all(|b| b.is_ascii_hexdigit()))
}
impl ArcusClient {
    pub(super) async fn onboarding_request(
        &self,
        name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let mut p = std::collections::BTreeMap::new();
        for (key, value) in params {
            if p.insert(key, value).is_some() {
                return Err(invalid("duplicate onboarding parameter"));
            }
        }
        if name == "get_api_keys" {
            if p.keys()
                .any(|k| !matches!(k.as_str(), "address" | "accountIndex"))
            {
                return Err(invalid("unknown API key query parameter"));
            }
            let account = p
                .get("address")
                .map(String::as_str)
                .or(self.address.as_deref())
                .ok_or_else(|| invalid("address is required"))?;
            if !address(account) {
                return Err(invalid("invalid address"));
            }
            let mut query = vec![("address".into(), account.to_string())];
            if let Some(index) = p.get("accountIndex") {
                if !index.parse::<u8>().is_ok_and(|v| v <= 9) {
                    return Err(invalid("accountIndex must be 0..9"));
                }
                query.push(("accountIndex".into(), index.clone()));
            }
            // Omission deliberately lists every subaccount; do not insert the client's default index.
            let mut request = HttpRequest::new(HttpMethod::Get, &self.base_url, "/v1/apiKeys");
            request.query = query;
            return self.execute(request).await;
        }
        if p.len() != 1 || !p.contains_key("body") {
            return Err(invalid("a signed body is required"));
        }
        let body: Value =
            serde_json::from_str(&p["body"]).map_err(|_| invalid("invalid signed JSON body"))?;
        let object = body
            .as_object()
            .ok_or_else(|| invalid("body must be an object"))?;
        let create = name == "create_api_key_signed";
        for key in object.keys() {
            if !([
                "address",
                "publicKey",
                "apiWalletName",
                "accountIndex",
                "nonce",
                "signature",
            ]
            .contains(&key.as_str())
                || (create && key == "validUntil"))
            {
                return Err(invalid("unknown signed API key field"));
            }
        }
        if !body["address"].as_str().is_some_and(address)
            || !body["publicKey"]
                .as_str()
                .is_some_and(|s| s.len() == 64 && s.bytes().all(|b| b.is_ascii_hexdigit()))
        {
            return Err(invalid("invalid address or Ed25519 publicKey"));
        }
        if !body["apiWalletName"]
            .as_str()
            .is_some_and(|s| !s.is_empty() && s.chars().count() <= 64)
        {
            return Err(invalid("apiWalletName must contain 1..64 characters"));
        }
        if let Some(index) = body.get("accountIndex")
            && !index.as_u64().is_some_and(|v| v <= 9 || v == 255)
        {
            return Err(invalid("API key scope must be 0..9 or 255"));
        }
        if let Some(until) = body.get("validUntil")
            && until.as_u64().is_none_or(|v| v == 0)
        {
            return Err(invalid(
                "validUntil must be a positive millisecond timestamp",
            ));
        }
        if let Some(nonce) = body.get("nonce")
            && !nonce
                .as_str()
                .is_some_and(|s| !s.is_empty() && s.len() <= 64)
        {
            return Err(invalid("nonce must contain 1..64 characters"));
        }
        let signature = body["signature"]
            .as_object()
            .ok_or_else(|| invalid("wallet signature must contain r, s and v"))?;
        if signature.len() != 3 {
            return Err(invalid("wallet signature must contain only r, s and v"));
        }
        for (key, max) in [("r", 64), ("s", 64), ("v", 8)] {
            let value = signature
                .get(key)
                .and_then(Value::as_str)
                .ok_or_else(|| invalid("wallet signature components must be hex strings"))?;
            let value = value.strip_prefix("0x").unwrap_or(value);
            if value.is_empty()
                || value.len() > max
                || !value.bytes().all(|b| b.is_ascii_hexdigit())
                || (key != "v" && value.bytes().all(|b| b == b'0'))
            {
                return Err(invalid("invalid wallet signature component"));
            }
        }
        let path = if create {
            "/v1/createApiKey"
        } else {
            "/v1/revokeApiKey"
        };
        self.execute(HttpRequest::new(HttpMethod::Post, &self.base_url, path).json(body))
            .await
    }
}
