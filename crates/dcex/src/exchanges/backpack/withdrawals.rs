//! Withdrawals operations.
use crate::exchanges::backpack::{BackpackClient, params::BackpackParams};
use crate::{DcexError, Result, exchange::ValidatedResponse};
use serde_json::{Map, Value};

impl BackpackClient {
    pub(in crate::exchanges::backpack) async fn withdrawals_schema_request(
        &self,
        name: &str,
        p: &BackpackParams,
    ) -> Result<Option<ValidatedResponse>> {
        static ROUTES: std::sync::OnceLock<Vec<crate::exchanges::schema::Route>> =
            std::sync::OnceLock::new();
        let Some(route) = crate::exchanges::schema::route(
            &ROUTES,
            include_str!("schemas/routes_withdrawals.json"),
            name,
        ) else {
            return Ok(None);
        };
        route.validate(|key| p.get(key))?;
        let (path, instruction, required, strings, decimals) = (
            route.path,
            route.instruction,
            route.required,
            route.strings,
            route.decimals,
        );
        let allowed: &[&str] = {
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
        {
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
