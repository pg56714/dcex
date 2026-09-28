//! Withdrawal and agent sub-account endpoints from the official OpenAPI catalog.
use serde_json::Value;

use super::client::BitgetClient;
use super::params::BitgetParams;
use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

impl BitgetClient {
    pub(super) async fn completion_private_request(
        &self,
        name: &str,
        params: &BitgetParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, fields, required) = match name {
            "create_spot_withdrawal" => (
                "/api/v2/spot/wallet/withdrawal",
                WITHDRAWAL_FIELDS,
                &WITHDRAWAL_REQUIRED[..],
            ),
            "create_uta_withdrawal" => (
                "/api/v3/account/withdrawal",
                UTA_WITHDRAWAL_FIELDS,
                &WITHDRAWAL_REQUIRED[..],
            ),
            "cancel_spot_withdrawal" => (
                "/api/v2/spot/wallet/cancel-withdrawal",
                &["orderId"][..],
                &["orderId"][..],
            ),
            "cancel_uta_withdrawal" => (
                "/api/v3/account/cancel-withdrawal",
                &["orderId", "clientOid"][..],
                &[][..],
            ),
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
            if name == "create_uta_withdrawal" {
                match params.get("identityType") {
                    Some("company") => {
                        nonempty(params, "companyName")?;
                    }
                    Some("user") => {
                        nonempty(params, "firstName")?;
                        nonempty(params, "lastName")?;
                    }
                    _ => {}
                }
                if let Some(accounts) = params.get("accountType") {
                    let mut seen = std::collections::HashSet::new();
                    if accounts
                        .split(',')
                        .any(|a| !["funding", "uta", "otc"].contains(&a) || !seen.insert(a))
                    {
                        return Err(invalid(
                            "accountType must contain distinct funding, uta or otc values",
                        ));
                    }
                }
            }
        }
        if name == "cancel_uta_withdrawal"
            && !["orderId", "clientOid"]
                .iter()
                .any(|k| params.get(k).is_some_and(|v| !v.is_empty()))
        {
            return Err(invalid("orderId or clientOid is required"));
        }
        if name.ends_with("agent_sub_account") {
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

const WITHDRAWAL_REQUIRED: [&str; 4] = ["coin", "transferType", "address", "size"];
const WITHDRAWAL_FIELDS: &[&str] = &[
    "coin",
    "transferType",
    "address",
    "size",
    "chain",
    "innerToType",
    "areaCode",
    "tag",
    "remark",
    "clientOid",
    "memberCode",
    "identityType",
    "companyName",
    "firstName",
    "lastName",
];
const UTA_WITHDRAWAL_FIELDS: &[&str] = &[
    "coin",
    "transferType",
    "address",
    "size",
    "chain",
    "innerToType",
    "areaCode",
    "tag",
    "remark",
    "clientOid",
    "memberCode",
    "identityType",
    "companyName",
    "firstName",
    "lastName",
    "accountType",
];

fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(message.into())
}
fn nonempty<'a>(params: &'a BitgetParams, key: &str) -> Result<&'a str> {
    params
        .get(key)
        .filter(|v| !v.is_empty())
        .ok_or_else(|| invalid(&format!("{key} is required")))
}
