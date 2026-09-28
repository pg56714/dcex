//! Subaccount operations.
use crate::exchange::ValidatedResponse;
use crate::exchanges::mexc::client::{MexcApi, MexcClient};
use crate::exchanges::mexc::params::{MexcParams, validate_u64_range};
use crate::http::HttpMethod;
use crate::{DcexError, Result};
impl MexcClient {
    pub(in crate::exchanges::mexc) async fn subaccount_schema_request(
        &self,
        name: &str,
        p: &MexcParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, api, verb, signed, allowed, required): (
            &str,
            MexcApi,
            HttpMethod,
            bool,
            &[&str],
            &[&str],
        ) = match name {
            "create_sub_account" => (
                "/api/v3/sub-account/virtualSubAccount",
                MexcApi::Spot,
                HttpMethod::Post,
                true,
                &["subAccount", "note", "recvWindow"],
                &["subAccount", "note"],
            ),
            "delete_sub_account_api_key" => (
                "/api/v3/sub-account/apiKey",
                MexcApi::Spot,
                HttpMethod::Delete,
                true,
                &["subAccount", "apiKey", "recvWindow"],
                &["subAccount", "apiKey"],
            ),
            "create_sub_account_api_key" => (
                "/api/v3/sub-account/apiKey",
                MexcApi::Spot,
                HttpMethod::Post,
                true,
                &["subAccount", "note", "permissions", "ip", "recvWindow"],
                &["subAccount", "note", "permissions"],
            ),
            "get_sub_account_api_keys" => (
                "/api/v3/sub-account/apiKey",
                MexcApi::Spot,
                HttpMethod::Get,
                true,
                &["subAccount", "recvWindow"],
                &["subAccount"],
            ),
            _ => return Ok(None),
        };
        if public == signed {
            return Ok(None);
        }
        p.ensure_allowed(allowed)?;
        validate_u64_range(p, "recvWindow", 1, 60_000)?;
        let query = p.only(allowed);
        let unique: std::collections::BTreeSet<_> = query.iter().map(|(k, _)| k).collect();
        if unique.len() != query.len() {
            return Err(DcexError::InvalidInput("duplicate MEXC parameter".into()));
        }
        for key in required {
            if p.required(key)?.trim().is_empty() {
                return Err(DcexError::InvalidInput(format!("{key} cannot be empty")));
            }
        }
        validate_u64_range(p, "page", 1, u64::MAX)?;
        validate_u64_range(p, "limit", 1, 1000)?;
        validate_u64_range(p, "startTime", 0, u64::MAX)?;
        validate_u64_range(p, "endTime", 0, u64::MAX)?;
        if let (Some(start), Some(end)) = (p.get("startTime"), p.get("endTime"))
            && start.parse::<u64>().unwrap() > end.parse::<u64>().unwrap()
        {
            return Err(DcexError::InvalidInput("startTime exceeds endTime".into()));
        }
        let path = path.to_string();
        Ok(Some(
            self.request(verb, api, path, query, None, signed).await?,
        ))
    }
}
