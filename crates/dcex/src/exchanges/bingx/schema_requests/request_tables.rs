//! Request tables from the official BingX documentation.
use crate::exchanges::bingx::{BingxClient, params::BingxParams};
use crate::{Result, exchange::ValidatedResponse, http::HttpMethod};
use serde::Deserialize;
use serde_json::Value;
use std::sync::OnceLock;

use crate::exchanges::schema::Field;
#[derive(Deserialize)]
struct Endpoint {
    name: String,
    method: String,
    path: String,
    signed: bool,
    scoped: bool,
    fields: Vec<Field>,
}
use crate::exchanges::bingx::params::invalid;
impl BingxClient {
    pub(in crate::exchanges::bingx) async fn catalog_request(
        &self,
        name: &str,
        p: &BingxParams,
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

    pub(in crate::exchanges::bingx) async fn catalog_request_transport(
        &self,
        name: &str,
        p: &BingxParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        static ENDPOINTS: OnceLock<Vec<Endpoint>> = OnceLock::new();
        let endpoints = ENDPOINTS.get_or_init(load_schemas);
        let Some(e) = endpoints
            .iter()
            .find(|e| e.name == name && e.signed != public)
        else {
            return Ok(None);
        };
        let mut allowed: Vec<&str> = e.fields.iter().map(|f| f.name.as_str()).collect();
        if e.scoped {
            allowed.push("all_symbols");
            let symbol = p.get("symbol").is_some_and(|s| !s.trim().is_empty());
            let all = p.get("all_symbols") == Some("true");
            if symbol == all {
                return Err(invalid("provide a symbol or all_symbols=true exclusively"));
            }
        }
        p.ensure_allowed(&allowed)?;
        for f in &e.fields {
            let Some(value) = p.get(&f.name) else {
                if f.required {
                    return Err(invalid(format!("{} is required", f.name)));
                }
                continue;
            };
            if value.trim().is_empty() {
                return Err(invalid(format!("{} cannot be empty", f.name)));
            }
            f.encode(value)?;
        }
        let method = match e.method.as_str() {
            "GET" => HttpMethod::Get,
            "POST" => HttpMethod::Post,
            "DELETE" => HttpMethod::Delete,
            _ => return Err(invalid("unsupported method")),
        };
        let fields: Vec<&str> = e.fields.iter().map(|f| f.name.as_str()).collect();
        if e.path.starts_with("/api/lindorm/") {
            let mut body = serde_json::Map::new();
            for field in &e.fields {
                if matches!(field.name.as_str(), "access_token" | "proxy_user") {
                    continue;
                }
                if let Some(value) = p.get(&field.name) {
                    body.insert(
                        field.name.clone(),
                        if field.kind == "int" {
                            value
                                .parse::<i64>()
                                .map(Value::from)
                                .map_err(|_| invalid("invalid integer"))?
                        } else {
                            Value::from(value)
                        },
                    );
                }
            }
            return self
                .lindorm_request(
                    &e.path,
                    Value::Object(body),
                    vec![
                        ("access_token".into(), p.required("access_token")?.into()),
                        ("proxy_user".into(), p.required("proxy_user")?.into()),
                    ],
                )
                .await
                .map(Some);
        }
        self.request(
            method,
            e.path.clone(),
            p.only(&fields),
            e.signed,
            vec![],
            None,
        )
        .await
        .map(Some)
    }
}

fn load_schemas() -> Vec<Endpoint> {
    [
        include_str!("../schemas/affiliate.json"),
        include_str!("../schemas/coin_futures.json"),
        include_str!("../schemas/market.json"),
        include_str!("../schemas/copy_trading.json"),
        include_str!("../schemas/earn.json"),
        include_str!("../schemas/deposits.json"),
        include_str!("../schemas/announcements.json"),
    ]
    .into_iter()
    .flat_map(|raw| serde_json::from_str::<Vec<Endpoint>>(raw).expect("checked endpoint schemas"))
    .collect()
}
