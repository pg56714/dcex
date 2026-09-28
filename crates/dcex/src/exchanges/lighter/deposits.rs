//! Deposits operations.
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
    pub(in crate::exchanges::lighter) async fn deposits_schema_request(
        &self,
        name: &str,
        p: &LighterParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, post, is_public, fields, required, integers, bools): RequestRoute<'_> =
            match name {
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
