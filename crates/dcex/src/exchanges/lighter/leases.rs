//! Leases operations.
use crate::exchange::ValidatedResponse;
use crate::exchanges::lighter::{
    LighterClient, client::LighterContentType, market::auth_header_required, params::LighterParams,
};
use crate::http::HttpMethod;
use crate::{DcexError, Result};
type RequestRoute<'a> = (
    &'a str,
    bool,
    bool,
    &'a [&'a str],
    &'a [&'a str],
    &'a [&'a str],
    &'a [&'a str],
);
impl LighterClient {
    pub(in crate::exchanges::lighter) async fn leases_schema_request(
        &self,
        name: &str,
        p: &LighterParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, post, is_public, fields, required, integers, bools): RequestRoute<'_> =
            match name {
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
        {
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
