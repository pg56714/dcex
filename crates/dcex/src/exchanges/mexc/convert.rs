//! Convert operations.
use crate::exchange::ValidatedResponse;
use crate::exchanges::mexc::client::{MexcApi, MexcClient};
use crate::exchanges::mexc::params::{MexcParams, validate_u64_range};
use crate::http::HttpMethod;
use crate::{DcexError, Result};
impl MexcClient {
    pub(in crate::exchanges::mexc) async fn convert_schema_request(
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
            "get_convertible_assets" => (
                "/api/v3/capital/convert/list",
                MexcApi::Spot,
                HttpMethod::Get,
                true,
                &[],
                &[],
            ),
            "convert_dust" => (
                "/api/v3/capital/convert",
                MexcApi::Spot,
                HttpMethod::Post,
                true,
                &["asset"],
                &["asset"],
            ),
            "get_dust_conversion_history" => (
                "/api/v3/capital/convert",
                MexcApi::Spot,
                HttpMethod::Get,
                true,
                &["startTime", "endTime", "page", "limit"],
                &[],
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
        if name == "convert_dust" {
            let values: Vec<_> = p.required("asset")?.split(',').collect();
            if values.len() > 15
                || values.iter().any(|v| v.is_empty())
                || values
                    .iter()
                    .collect::<std::collections::BTreeSet<_>>()
                    .len()
                    != values.len()
            {
                return Err(DcexError::InvalidInput(
                    "asset requires 1..15 distinct comma-separated currencies".into(),
                ));
            }
        }
        let path = path.to_string();
        Ok(Some(
            self.request(verb, api, path, query, None, signed).await?,
        ))
    }
}
