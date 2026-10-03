//! Withdrawals operations.
use serde_json::Value;

use crate::Result;
use crate::exchange::ValidatedResponse;
use crate::exchanges::bitget::client::BitgetClient;
use crate::exchanges::bitget::params::BitgetParams;

impl BitgetClient {
    pub(in crate::exchanges::bitget) async fn withdrawals_schema_request(
        &self,
        name: &str,
        params: &BitgetParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, fields, required) = match name {
            "create_uta_withdrawal" => (
                "/api/v3/account/withdrawal",
                UTA_WITHDRAWAL_FIELDS,
                &WITHDRAWAL_REQUIRED[..],
            ),
            "cancel_uta_withdrawal" => (
                "/api/v3/account/cancel-withdrawal",
                &["orderId", "clientOid"][..],
                &[][..],
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
        self.post_private(path, Value::Object(params.body(fields)))
            .await
            .map(Some)
    }
}

const WITHDRAWAL_REQUIRED: [&str; 4] = ["coin", "transferType", "address", "size"];
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

use crate::exchanges::bitget::params::invalid;
use crate::exchanges::bitget::params::nonempty;

impl super::client::BitgetClient {
    pub(in crate::exchanges::bitget) async fn withdrawals_table_request(
        &self,
        name: &str,
        params: &super::params::BitgetParams,
        public: bool,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        self.table_request_transport(name, params, public).await
    }
}

impl super::client::BitgetClient {
    pub(in crate::exchanges::bitget) async fn withdrawals_catalog_request(
        &self,
        name: &str,
        p: &super::params::BitgetParams,
        public: bool,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        self.catalog_request_transport(name, p, public).await
    }
}
