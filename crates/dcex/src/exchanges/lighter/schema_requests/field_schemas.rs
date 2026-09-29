//! Referral, RFQ response and fast-withdraw REST operations.
use crate::exchanges::lighter::{
    LighterClient, LighterContentType, market::auth_header_required, params::LighterParams,
};
use crate::{DcexError, Result, exchange::ValidatedResponse, http::HttpMethod};
use serde::Deserialize;
use serde_json::Value;
use std::sync::OnceLock;

#[derive(Deserialize)]
struct Field {
    name: String,
    #[serde(rename = "type")]
    kind: String,
    required: bool,
    minimum: Option<f64>,
    maximum: Option<f64>,
    #[serde(rename = "enum", default)]
    choices: Vec<String>,
}
#[derive(Deserialize)]
struct Endpoint {
    name: String,
    path: String,
    method: String,
    fields: Vec<Field>,
}
fn invalid(message: impl std::fmt::Display) -> DcexError {
    DcexError::InvalidInput(format!("Lighter: {message}"))
}

impl LighterClient {
    pub(in crate::exchanges::lighter) async fn field_schema_request(
        &self,
        name: &str,
        p: &LighterParams,
    ) -> Result<Option<ValidatedResponse>> {
        match crate::exchanges::schema::fund_domain(name) {
            Some(crate::exchanges::schema::FundDomain::Withdrawals) => {
                self.withdrawals_field_schema_request(name, p).await
            }
            Some(crate::exchanges::schema::FundDomain::Transfers) => {
                self.transfers_field_schema_request(name, p).await
            }
            None => self.field_schema_request_transport(name, p).await,
        }
    }

    pub(in crate::exchanges::lighter) async fn field_schema_request_transport(
        &self,
        name: &str,
        p: &LighterParams,
    ) -> Result<Option<ValidatedResponse>> {
        static ENDPOINTS: OnceLock<Vec<Endpoint>> = OnceLock::new();
        let endpoints = ENDPOINTS.get_or_init(load_schemas);
        let Some(e) = endpoints.iter().find(|e| e.name == name) else {
            return Ok(None);
        };
        let mut allowed: Vec<_> = e.fields.iter().map(|f| f.name.as_str()).collect();
        allowed.push("authorization");
        p.ensure_allowed(&allowed)?;
        for f in &e.fields {
            let Some(value) = p.get(&f.name) else {
                if f.required {
                    return Err(invalid(format!("{} is required", f.name)));
                }
                continue;
            };
            p.required(&f.name)?;
            if !f.choices.is_empty() && !f.choices.iter().any(|v| v == value) {
                return Err(invalid(format!("invalid {}", f.name)));
            }
            crate::exchanges::schema::encode(&f.name, value, &f.kind)?;
            match f.kind.as_str() {
                "integer" => {
                    p.required_u64_range(
                        &f.name,
                        f.minimum.unwrap_or(0.0) as u64,
                        f.maximum.unwrap_or(i64::MAX as f64) as u64,
                    )?;
                }
                "number" => {
                    let n = value
                        .parse::<f64>()
                        .map_err(|_| invalid("invalid percentage"))?;
                    if !n.is_finite()
                        || n < f.minimum.unwrap_or(0.0)
                        || n > f.maximum.unwrap_or(f64::MAX)
                    {
                        return Err(invalid("percentage must be within 0..100"));
                    }
                }
                "boolean" => {
                    p.optional_bool(&f.name)?;
                }
                _ => {}
            }
        }
        if let Some(address) = p.get("l1_address").or_else(|| p.get("to_address"))
            && (address.len() != 42
                || !address.starts_with("0x")
                || !address[2..].bytes().all(|b| b.is_ascii_hexdigit()))
        {
            return Err(invalid("address must contain 20 hex bytes"));
        }
        if name == "submit_fast_withdrawal" {
            let tx: Value = serde_json::from_str(p.required("tx_info")?)
                .map_err(|_| invalid("tx_info must contain signed transaction JSON"))?;
            for key in ["Sig", "L1Sig"] {
                if tx
                    .get(key)
                    .and_then(Value::as_str)
                    .is_none_or(|v| v.is_empty())
                {
                    return Err(invalid(format!("fast withdrawal requires {key}")));
                }
            }
        }
        let headers = auth_header_required(self, p)?;
        let fields: Vec<_> = e.fields.iter().map(|f| f.name.as_str()).collect();
        let pairs = p.query(&fields);
        let response = if e.method == "POST" {
            self.path_request(
                HttpMethod::Post,
                &e.path,
                Vec::new(),
                pairs,
                headers,
                LighterContentType::Form,
            )
            .await?
        } else {
            self.get_path(&e.path, pairs, headers).await?
        };
        Ok(Some(response))
    }
}

fn load_schemas() -> Vec<Endpoint> {
    [
        include_str!("../schemas/fast_withdrawals.json"),
        include_str!("../schemas/referral.json"),
        include_str!("../schemas/rfq.json"),
    ]
    .into_iter()
    .flat_map(|raw| serde_json::from_str::<Vec<Endpoint>>(raw).expect("checked endpoint schemas"))
    .collect()
}
