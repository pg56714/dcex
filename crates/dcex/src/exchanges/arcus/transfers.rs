//! Same-wallet collateral transfers.
mod trade_operations {
    use super::strip_hex_prefix;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::arcus::client::ArcusClient;
    use crate::exchanges::arcus::params::required;

    use crate::http::{HttpMethod, HttpRequest};
    use crate::{DcexError, Result};

    use serde_json::Value;
    use std::collections::BTreeMap;
    impl ArcusClient {
        pub(in crate::exchanges::arcus) async fn submit_internal_transfer_request(
            &self,
            params: Vec<(String, String)>,
        ) -> Result<ValidatedResponse> {
            let values: BTreeMap<_, _> = params.into_iter().collect();
            if let Some(key) = values.keys().find(|key| *key != "signed_transfer_json") {
                return Err(DcexError::InvalidInput(format!(
                    "unknown Arcus internal transfer parameter: {key}"
                )));
            }
            let body: Value = serde_json::from_str(required(&values, "signed_transfer_json")?)
                .map_err(|error| {
                    DcexError::InvalidInput(format!("invalid transfer JSON: {error}"))
                })?;
            let object = body.as_object().ok_or_else(|| {
                DcexError::InvalidInput("Arcus internal transfer must be an object".into())
            })?;
            const FIELDS: &[&str] = &[
                "ethereumAddress",
                "fromAccountIndex",
                "toAccountIndex",
                "amount",
                "nonce",
                "signature",
            ];
            if let Some(key) = object.keys().find(|key| !FIELDS.contains(&key.as_str())) {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Arcus transfer field: {key}"
                )));
            }
            let transfer_address = object
                .get("ethereumAddress")
                .and_then(Value::as_str)
                .ok_or_else(|| {
                    DcexError::InvalidInput("transfer ethereumAddress is required".into())
                })?;
            // 40 hex digits with an optional 0x/0X prefix.
            let transfer_hex = strip_hex_prefix(transfer_address);
            if transfer_hex.len() != 40
                || !transfer_hex.bytes().all(|byte| byte.is_ascii_hexdigit())
            {
                return Err(DcexError::InvalidInput(
                    "invalid transfer ethereumAddress".into(),
                ));
            }
            if self.address.as_deref().is_some_and(|address| {
                !strip_hex_prefix(address).eq_ignore_ascii_case(transfer_hex)
            }) {
                return Err(DcexError::InvalidInput(
                    "transfer ethereumAddress does not match configured wallet".into(),
                ));
            }
            let from = object
                .get("fromAccountIndex")
                .and_then(Value::as_u64)
                .ok_or_else(|| DcexError::InvalidInput("fromAccountIndex is required".into()))?;
            let to = object
                .get("toAccountIndex")
                .and_then(Value::as_u64)
                .ok_or_else(|| DcexError::InvalidInput("toAccountIndex is required".into()))?;
            if from > 9 || to > 9 || from == to {
                return Err(DcexError::InvalidInput(
                    "transfer account indexes must differ and be 0..=9".into(),
                ));
            }
            let amount = object
                .get("amount")
                .and_then(Value::as_str)
                .ok_or_else(|| DcexError::InvalidInput("transfer amount is required".into()))?;
            if amount.is_empty() || !amount.bytes().all(|byte| byte.is_ascii_digit()) {
                return Err(DcexError::InvalidInput(
                    "transfer amount must be decimal quote quantums".into(),
                ));
            }
            let amount = amount
                .parse::<i64>()
                .map_err(|_| DcexError::InvalidInput("invalid transfer amount".into()))?;
            if amount <= 0 {
                return Err(DcexError::InvalidInput(
                    "transfer amount must be positive quote quantums".into(),
                ));
            }
            let nonce = object
                .get("nonce")
                .and_then(Value::as_str)
                .ok_or_else(|| DcexError::InvalidInput("transfer nonce is required".into()))?;
            if nonce.is_empty() || nonce.len() > 64 {
                return Err(DcexError::InvalidInput(
                    "transfer nonce must be 1..=64 characters".into(),
                ));
            }
            let signature = object
                .get("signature")
                .and_then(Value::as_object)
                .ok_or_else(|| DcexError::InvalidInput("transfer signature is required".into()))?;
            if let Some(key) = signature
                .keys()
                .find(|key| !matches!(key.as_str(), "r" | "s" | "v"))
            {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Arcus transfer signature field: {key}"
                )));
            }
            // r and s are nonzero values of up to 32 bytes; v is a raw, legacy or EIP-155
            // recovery value of up to 4 bytes. Each is hex with an optional 0x prefix.
            for (component, max_digits, nonzero) in
                [("r", 64, true), ("s", 64, true), ("v", 8, false)]
            {
                let digits = signature
                    .get(component)
                    .and_then(Value::as_str)
                    .map(strip_hex_prefix)
                    .unwrap_or_default();
                if digits.is_empty()
                    || digits.len() > max_digits
                    || !digits.bytes().all(|byte| byte.is_ascii_hexdigit())
                    || (nonzero && digits.bytes().all(|byte| byte == b'0'))
                {
                    return Err(DcexError::InvalidInput(format!(
                        "invalid transfer signature {component}"
                    )));
                }
            }
            self.execute(
                HttpRequest::new(HttpMethod::Post, &self.base_url, "/v1/transfer").json(body),
            )
            .await
        }
    }
}

fn strip_hex_prefix(value: &str) -> &str {
    value
        .strip_prefix("0x")
        .or_else(|| value.strip_prefix("0X"))
        .unwrap_or(value)
}

mod wrappers {
    use crate::exchanges::arcus::ArcusClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; ArcusClient;
     public [

     ];
     private [
    submit_internal_transfer(signed_transfer_json => "signed_transfer_json")
     ];
    }
}

impl super::client::ArcusClient {
    pub(in crate::exchanges::arcus) async fn transfers_field_schema_request(
        &self,
        name: &str,
        params: Vec<(String, String)>,
    ) -> crate::Result<crate::exchange::ValidatedResponse> {
        self.field_schema_request_transport(name, params).await
    }
}
