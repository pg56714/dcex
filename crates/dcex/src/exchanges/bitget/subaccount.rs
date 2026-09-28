//! Subaccount operations.
use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::exchanges::bitget::client::BitgetClient;
use crate::exchanges::bitget::params::BitgetParams;
use crate::{DcexError, Result};

impl BitgetClient {
    pub(in crate::exchanges::bitget) async fn subaccount_schema_request(
        &self,
        name: &str,
        params: &BitgetParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, fields, required) = match name {
            "create_classic_agent_sub_account" => (
                "/api/v2/user/create-agent-subaccount",
                &["username", "passphrase", "note"][..],
                &["username", "passphrase"][..],
            ),
            "create_uta_agent_sub_account" => (
                "/api/v3/user/sub-account/agent-create",
                &["username", "passphrase", "note"][..],
                &["username", "passphrase"][..],
            ),
            _ => return Ok(None),
        };
        params.ensure_allowed(fields, false)?;
        for key in required {
            nonempty(params, key)?;
        }
        if name.starts_with("create_") && name.ends_with("withdrawal") {
            let transfer_type = nonempty(params, "transferType")?;
            if !["on_chain", "internal_transfer"].contains(&transfer_type) {
                return Err(invalid(
                    "transferType must be on_chain or internal_transfer",
                ));
            }
            if transfer_type == "on_chain" {
                nonempty(params, "chain")?;
            }
            if !crate::common::is_positive_plain_decimal(params.required("size")?) {
                return Err(invalid("size must be a positive plain decimal string"));
            }
            if let Some(kind) = params.get("innerToType") {
                if !["uid", "email", "mobile"].contains(&kind) {
                    return Err(invalid("invalid innerToType"));
                }
                if kind == "mobile" {
                    nonempty(params, "areaCode")?;
                }
            }
            for (key, values) in [
                ("memberCode", &["bithumb", "korbit", "coinone"][..]),
                ("identityType", &["user", "company"][..]),
            ] {
                if params.get(key).is_some_and(|v| !values.contains(&v)) {
                    return Err(invalid(&format!("invalid {key}")));
                }
            }
        }
        {
            let username = nonempty(params, "username")?;
            if username.len() > 20 || !username.bytes().all(|b| b.is_ascii_lowercase()) {
                return Err(invalid("username requires 1..20 lowercase ASCII letters"));
            }
            let passphrase = nonempty(params, "passphrase")?;
            if !(8..=32).contains(&passphrase.len())
                || !passphrase.bytes().all(|b| b.is_ascii_alphanumeric())
            {
                return Err(invalid(
                    "passphrase requires 8..32 ASCII letters and digits",
                ));
            }
        }
        self.post_private(path, Value::Object(params.body(fields)))
            .await
            .map(Some)
    }
}

fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(message.into())
}
fn nonempty<'a>(params: &'a BitgetParams, key: &str) -> Result<&'a str> {
    params
        .get(key)
        .filter(|v| !v.is_empty())
        .ok_or_else(|| invalid(&format!("{key} is required")))
}
