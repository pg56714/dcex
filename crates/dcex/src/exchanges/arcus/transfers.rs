//! Same-wallet collateral transfers.
mod trade_operations {
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
            if values.keys().any(|key| key != "signed_transfer_json") {
                return Err(DcexError::InvalidInput(
                    "unknown Arcus internal transfer parameter".into(),
                ));
            }
            let body: Value = serde_json::from_str(required(&values, "signed_transfer_json")?)
                .map_err(|error| {
                    DcexError::InvalidInput(format!("invalid transfer JSON: {error}"))
                })?;
            let object = body.as_object().ok_or_else(|| {
                DcexError::InvalidInput("Arcus internal transfer must be an object".into())
            })?;
            let transfer_address = object
                .get("ethereumAddress")
                .and_then(Value::as_str)
                .ok_or_else(|| {
                    DcexError::InvalidInput("transfer ethereumAddress is required".into())
                })?;
            if transfer_address.len() != 42
                || !transfer_address.starts_with("0x")
                || !transfer_address[2..]
                    .bytes()
                    .all(|byte| byte.is_ascii_hexdigit())
            {
                return Err(DcexError::InvalidInput(
                    "invalid transfer ethereumAddress".into(),
                ));
            }
            if self
                .address
                .as_deref()
                .is_some_and(|address| !address.eq_ignore_ascii_case(transfer_address))
            {
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
            for component in ["r", "s"] {
                let valid = signature
                    .get(component)
                    .and_then(Value::as_str)
                    .is_some_and(|value| {
                        value.len() == 66
                            && value.starts_with("0x")
                            && value[2..].bytes().all(|byte| byte.is_ascii_hexdigit())
                    });
                if !valid {
                    return Err(DcexError::InvalidInput(format!(
                        "transfer signature {component} must be 32-byte hex"
                    )));
                }
            }
            if !matches!(
                signature.get("v").and_then(Value::as_str),
                Some("0x1b" | "0x1c")
            ) {
                return Err(DcexError::InvalidInput(
                    "transfer signature v must be 0x1b or 0x1c".into(),
                ));
            }
            self.execute(
                HttpRequest::new(HttpMethod::Post, &self.base_url, "/v1/transfer").json(body),
            )
            .await
        }
    }
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
