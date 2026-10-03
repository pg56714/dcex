//! Additional operations extracted from Bitget's published OpenAPI documentation.
use crate::exchanges::bitget::{client::BitgetClient, params::BitgetParams};
use crate::{Result, exchange::ValidatedResponse, http::HttpMethod};
use serde::Deserialize;
use serde_json::{Map, Value};
use std::sync::OnceLock;

use crate::exchanges::schema::Field;
#[derive(Deserialize)]
struct Endpoint {
    name: String,
    method: String,
    path: String,
    public: bool,
    confirm: bool,
    fields: Vec<Field>,
}

use crate::exchanges::bitget::params::schema_invalid as invalid;

impl BitgetClient {
    pub(in crate::exchanges::bitget) async fn catalog_request(
        &self,
        name: &str,
        p: &BitgetParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        match crate::exchanges::schema::fund_domain(name) {
            Some(crate::exchanges::schema::FundDomain::Withdrawals) => {
                self.withdrawals_catalog_request(name, p, public).await
            }
            Some(crate::exchanges::schema::FundDomain::Transfers) => {
                self.transfers_catalog_request(name, p, public).await
            }
            None => self.catalog_request_transport(name, p, public).await,
        }
    }

    pub(in crate::exchanges::bitget) async fn catalog_request_transport(
        &self,
        name: &str,
        p: &BitgetParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        static ENDPOINTS: OnceLock<Vec<Endpoint>> = OnceLock::new();
        let endpoints = ENDPOINTS.get_or_init(load_schemas);
        let Some(endpoint) = endpoints
            .iter()
            .find(|e| e.name == name && e.public == public)
        else {
            return Ok(None);
        };
        let mut allowed: Vec<&str> = endpoint.fields.iter().map(|f| f.name.as_str()).collect();
        if endpoint.confirm {
            allowed.push("confirm");
            if p.get("confirm") != Some("true") {
                return Err(invalid("confirm=true is required"));
            }
        }
        p.ensure_allowed(&allowed, false)?;
        let mut query = Vec::new();
        let mut body = Map::new();
        for field in &endpoint.fields {
            let Some(raw) = p.get(&field.name) else {
                if field.required {
                    return Err(invalid(format!("missing {}", field.name)));
                }
                continue;
            };
            let value = field.encode(raw)?;
            if field.location == "query" {
                query.push((field.name.clone(), raw.into()));
            } else {
                body.insert(field.name.clone(), value);
            }
        }
        let response = if endpoint.method == "GET" {
            if public {
                self.public_get(&endpoint.path, query).await?
            } else {
                self.get_private(&endpoint.path, query).await?
            }
        } else {
            let path = if query.is_empty() {
                endpoint.path.clone()
            } else {
                format!(
                    "{}?{}",
                    endpoint.path,
                    crate::exchanges::bitget::signing::encode_params(&query)
                )
            };
            let body = if endpoint.fields.iter().any(|f| f.location == "body") {
                Some(serde_json::to_vec(&Value::Object(body)).map_err(|e| invalid(e.to_string()))?)
            } else {
                None
            };
            self.request(HttpMethod::Post, path, vec![], body, !public)
                .await?
        };
        Ok(Some(response))
    }
}

fn load_schemas() -> Vec<Endpoint> {
    [
        include_str!("../schemas/broker.json"),
        include_str!("../schemas/cfd.json"),
        include_str!("../schemas/market.json"),
        include_str!("../schemas/loan.json"),
        include_str!("../schemas/margin.json"),
        include_str!("../schemas/announcements.json"),
        include_str!("../schemas/copy_trading.json"),
        include_str!("../schemas/institutional_loan.json"),
        include_str!("../schemas/p2p.json"),
        include_str!("../schemas/tax.json"),
        include_str!("../schemas/stocks.json"),
    ]
    .into_iter()
    .flat_map(|raw| serde_json::from_str::<Vec<Endpoint>>(raw).expect("checked endpoint schemas"))
    .collect()
}
