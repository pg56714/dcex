//! Additional ordinary account and deposit endpoints from the official Lighter SDK.
use super::{
    LighterClient, client::LighterContentType, market::auth_header_required, params::LighterParams,
};
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};
type AdditionalRoute<'a> = (
    &'a str,
    bool,
    bool,
    &'a [&'a str],
    &'a [&'a str],
    &'a [&'a str],
    &'a [&'a str],
);
impl LighterClient {
    pub(super) async fn additional_request(
        &self,
        name: &str,
        p: &LighterParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        if !public && let Some(response) = self.completion_request(name, p).await? {
            return Ok(Some(response));
        }
        if let Some(response) = self.explorer_request(name, p, public).await? {
            return Ok(Some(response));
        }
        let (path, post, is_public, fields, required, integers, bools): AdditionalRoute<'_> =
            match name {
                "set_maker_only_api_keys" => (
                    "/api/v1/setMakerOnlyApiKeys",
                    true,
                    false,
                    &["account_index", "api_key_indexes", "authorization"],
                    &["account_index", "api_key_indexes"],
                    &["account_index"],
                    &[],
                ),
                "change_account_tier" => (
                    "/api/v1/changeAccountTier",
                    true,
                    false,
                    &["account_index", "new_tier", "authorization"],
                    &["account_index", "new_tier"],
                    &["account_index"],
                    &[],
                ),
                "create_read_only_token" => (
                    "/api/v1/tokens/create",
                    true,
                    false,
                    &[
                        "name",
                        "account_index",
                        "expiry",
                        "sub_account_access",
                        "authorization",
                        "scopes",
                    ],
                    &["name", "account_index", "expiry", "sub_account_access"],
                    &["account_index", "expiry"],
                    &["sub_account_access"],
                ),
                "revoke_read_only_token" => (
                    "/api/v1/tokens/revoke",
                    true,
                    false,
                    &["token_id", "account_index", "authorization"],
                    &["token_id", "account_index"],
                    &["token_id", "account_index"],
                    &[],
                ),
                "get_transaction" => (
                    "/api/v1/tx",
                    false,
                    true,
                    &["by", "value"],
                    &["by", "value"],
                    &[],
                    &[],
                ),
                "get_transaction_by_l1_hash" => (
                    "/api/v1/txFromL1TxHash",
                    false,
                    true,
                    &["hash"],
                    &["hash"],
                    &[],
                    &[],
                ),
                "acknowledge_notification" => (
                    "/api/v1/notification/ack",
                    true,
                    false,
                    &["notif_id", "account_index", "authorization"],
                    &["notif_id", "account_index"],
                    &["account_index"],
                    &[],
                ),
                "create_deposit_intent_address" => (
                    "/api/v1/createIntentAddress",
                    true,
                    true,
                    &["chain_id", "from_addr", "amount", "is_external_deposit"],
                    &["chain_id", "from_addr", "amount"],
                    &[],
                    &["is_external_deposit"],
                ),
                "get_latest_deposit" => (
                    "/api/v1/deposit/latest",
                    false,
                    true,
                    &["l1_address"],
                    &["l1_address"],
                    &[],
                    &[],
                ),
                "submit_lit_lease" => (
                    "/api/v1/litLease",
                    true,
                    false,
                    &["tx_info", "lease_amount", "duration_days", "authorization"],
                    &["tx_info", "lease_amount", "duration_days"],
                    &["duration_days"],
                    &[],
                ),
                _ => return Ok(None),
            };
        if public != is_public {
            return Ok(None);
        }
        p.ensure_allowed(fields)?;
        for key in required {
            p.required(key)?;
        }
        for key in fields {
            if p.get(key).is_some() {
                p.required(key)?;
            }
        }
        for key in integers {
            p.optional_u64_range(key, 0, u64::MAX)?;
        }
        for key in bools {
            p.optional_one_of(key, &["true", "false"])?;
        }
        if name == "create_deposit_intent_address"
            && !p
                .required("amount")?
                .parse::<f64>()
                .is_ok_and(|v| v.is_finite() && v > 0.0)
        {
            return Err(DcexError::InvalidInput(
                "Lighter deposit amount must be positive".into(),
            ));
        }
        if name == "submit_lit_lease" {
            let tx: serde_json::Value =
                serde_json::from_str(p.required("tx_info")?).map_err(|_| {
                    DcexError::InvalidInput("tx_info must be signed transaction JSON".into())
                })?;
            if !tx.is_object()
                || tx
                    .get("Sig")
                    .and_then(serde_json::Value::as_str)
                    .is_none_or(str::is_empty)
            {
                return Err(DcexError::InvalidInput("tx_info must contain Sig".into()));
            }
            p.required_u64_range("duration_days", 1, u64::MAX)?;
            let amount = p.required("lease_amount")?;
            if amount.is_empty()
                || !amount.bytes().all(|b| b.is_ascii_digit())
                || amount.bytes().all(|b| b == b'0')
            {
                return Err(DcexError::InvalidInput(
                    "lease_amount must be positive integer raw units".into(),
                ));
            }
        }
        if name == "set_maker_only_api_keys" {
            let indexes: Vec<u64> =
                serde_json::from_str(p.required("api_key_indexes")?).map_err(|_| {
                    DcexError::InvalidInput("api_key_indexes must be a JSON integer array".into())
                })?;
            let distinct: std::collections::BTreeSet<_> = indexes.iter().copied().collect();
            if indexes.iter().any(|v| *v > 254) || distinct.len() != indexes.len() {
                return Err(DcexError::InvalidInput(
                    "API key indexes must be distinct and within 0..254".into(),
                ));
            }
            p.required_u64_range("account_index", 0, 281474976710654)?;
        }
        let headers = if public {
            std::collections::BTreeMap::new()
        } else {
            auth_header_required(self, p)?
        };
        let pairs = p.query(
            &fields
                .iter()
                .copied()
                .filter(|k| *k != "authorization")
                .collect::<Vec<_>>(),
        );
        let response = if post {
            self.path_request(
                HttpMethod::Post,
                path,
                Vec::new(),
                pairs,
                headers,
                LighterContentType::Form,
            )
            .await
        } else {
            self.get_path(path, pairs, headers).await
        };
        response.map(Some)
    }
}
