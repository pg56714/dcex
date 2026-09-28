//! Maker quotes and withdrawal payloads from the official OpenAPI.
use super::{BackpackClient, params::BackpackParams};
use crate::{DcexError, Result, exchange::ValidatedResponse};
use serde_json::{Map, Value};

impl BackpackClient {
    pub(super) async fn completion_private_request(
        &self,
        name: &str,
        p: &BackpackParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, instruction, required, strings, decimals): (
            &str,
            &str,
            &[&str],
            &[&str],
            &[&str],
        ) = match name {
            "submit_rfq_quote" => (
                "/api/v1/rfq/quote",
                "quoteSubmit",
                &["rfqId", "bidPrice", "askPrice"],
                &["rfqId"],
                &["bidPrice", "askPrice"],
            ),
            "create_withdrawal" => (
                "/wapi/v1/capital/withdrawals",
                "withdraw",
                &["address", "blockchain", "quantity", "symbol"],
                &[
                    "address",
                    "blockchain",
                    "quantity",
                    "symbol",
                    "clientId",
                    "twoFactorToken",
                ],
                &["quantity"],
            ),
            _ => return Ok(None),
        };
        let allowed: &[&str] = if name == "submit_rfq_quote" {
            &[
                "rfqId",
                "bidPrice",
                "askPrice",
                "clientId",
                "autoLend",
                "autoLendRedeem",
                "autoBorrow",
                "autoBorrowRepay",
            ]
        } else {
            &[
                "address",
                "blockchain",
                "quantity",
                "symbol",
                "clientId",
                "twoFactorToken",
                "autoBorrow",
                "autoLendRedeem",
                "recipientInformation",
            ]
        };
        p.ensure_allowed(allowed, &[])?;
        for key in required {
            p.required(key)?;
        }
        let mut body = Map::new();
        for key in strings.iter().chain(decimals.iter()) {
            if let Some(raw) = p.get(key) {
                body.insert((*key).into(), Value::String(raw.into()));
            }
        }
        for key in decimals {
            if !p
                .get(key)
                .is_some_and(crate::common::is_positive_plain_decimal)
            {
                return Err(invalid(format!(
                    "{key} requires a positive plain decimal string"
                )));
            }
        }
        for key in [
            "autoLend",
            "autoLendRedeem",
            "autoBorrow",
            "autoBorrowRepay",
        ] {
            if let Some(raw) = p.get(key) {
                body.insert(
                    key.into(),
                    Value::Bool(
                        raw.parse::<bool>()
                            .map_err(|_| invalid(format!("{key} requires a boolean")))?,
                    ),
                );
            }
        }
        if name == "submit_rfq_quote" {
            if let Some(raw) = p.get("clientId") {
                body.insert(
                    "clientId".into(),
                    Value::from(
                        raw.parse::<u32>()
                            .map_err(|_| invalid("clientId requires uint32"))?,
                    ),
                );
            }
        } else {
            if p.get("clientId")
                .is_some_and(|s| s.len() > 255 || s.starts_with("fulfill-"))
            {
                return Err(invalid(
                    "clientId must be at most 255 bytes and must not start with fulfill-",
                ));
            }
            if let Some(raw) = p.get("recipientInformation") {
                let value: Value = serde_json::from_str(raw)
                    .map_err(|_| invalid("recipientInformation requires an object"))?;
                let obj = value
                    .as_object()
                    .ok_or_else(|| invalid("recipientInformation requires an object"))?;
                if obj
                    .get("withdrawal_address_id")
                    .and_then(Value::as_i64)
                    .is_none_or(|n| i32::try_from(n).is_err())
                {
                    return Err(invalid(
                        "recipientInformation.withdrawal_address_id requires int32",
                    ));
                }
                for (key, v) in obj {
                    let valid = match key.as_str() {
                        "withdrawal_address_id" => true,
                        "withdrawal_purpose" => v.is_string(),
                        "sanctions_representation" => v.is_boolean(),
                        _ => false,
                    };
                    if !valid {
                        return Err(invalid(format!("invalid recipientInformation.{key}")));
                    }
                }
                body.insert("recipientInformation".into(), value);
            }
        }
        self.private_post_value(path, Value::Object(body), instruction)
            .await
            .map(Some)
    }
}
fn invalid(message: impl Into<String>) -> DcexError {
    DcexError::InvalidInput(format!("Backpack: {}", message.into()))
}
