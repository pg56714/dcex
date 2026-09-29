//! Additional documented SDK operations; Alpha has its own host and Fiat uses JSON.
use crate::exchanges::binance::{BinanceClient, params::PublicParams};
use crate::exchanges::schema::{self, Field};
use crate::{Result, exchange::ValidatedResponse, http::HttpMethod};
use serde::Deserialize;
use serde_json::Value;
use std::sync::OnceLock;
#[derive(Deserialize)]
struct Endpoint {
    name: String,
    method: String,
    path: String,
    public: bool,
    json_body: bool,
    fields: Vec<Field>,
}
use crate::exchanges::binance::params::invalid;
impl BinanceClient {
    pub(in crate::exchanges::binance) async fn catalog_request(
        &self,
        name: &str,
        p: &PublicParams,
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

    pub(in crate::exchanges::binance) async fn catalog_request_transport(
        &self,
        name: &str,
        p: &PublicParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        static ENDPOINTS: OnceLock<Vec<Endpoint>> = OnceLock::new();
        let endpoints = ENDPOINTS.get_or_init(load_schemas);
        let Some(e) = endpoints
            .iter()
            .find(|e| e.name == name && e.public == public)
        else {
            return Ok(None);
        };
        let allowed: Vec<&str> = e.fields.iter().map(|f| f.name.as_str()).collect();
        p.ensure_allowed(&allowed)?;
        let mut fields = schema::request_in_schema_order(&e.fields, &p.0)?;
        if name == "prediction_batch_cancel_orders"
            && fields
                .get("cancelInfoList")
                .and_then(Value::as_array)
                .is_none_or(Vec::is_empty)
        {
            return Err(invalid("cancelInfoList must be a nonempty array"));
        }
        let method = match e.method.as_str() {
            "GET" => HttpMethod::Get,
            "POST" => HttpMethod::Post,
            "DELETE" => HttpMethod::Delete,
            "PUT" => HttpMethod::Put,
            _ => return Err(invalid("unsupported verb")),
        };
        let mut query = Vec::new();
        let body = if e.json_body {
            if let Some(v) = fields.remove("recvWindow") {
                query.push(("recvWindow".into(), v.to_string()));
            }
            Some(Value::Object(fields))
        } else {
            for (key, value) in fields {
                if key == "cancelInfoList" {
                    for (index, item) in value
                        .as_array()
                        .ok_or_else(|| invalid("cancelInfoList must be an array"))?
                        .iter()
                        .enumerate()
                    {
                        let object = item
                            .as_object()
                            .ok_or_else(|| invalid("cancelInfoList entries must be objects"))?;
                        for (field, value) in object {
                            query.push((
                                format!("{key}[{index}].{field}"),
                                crate::exchanges::binance::signing::json_value_string(value),
                            ));
                        }
                    }
                } else if let Some(items) = value.as_array() {
                    for item in items {
                        query.push((
                            key.clone(),
                            crate::exchanges::binance::signing::json_value_string(item),
                        ));
                    }
                } else {
                    query.push((
                        key,
                        crate::exchanges::binance::signing::json_value_string(&value),
                    ));
                }
            }
            None
        };
        self.inventory_transport(method, &e.path, query, body, !public)
            .await
            .map(Some)
    }
}

fn load_schemas() -> Vec<Endpoint> {
    [
        include_str!("../schemas/alpha.json"),
        include_str!("../schemas/c2c.json"),
        include_str!("../schemas/fiat.json"),
        include_str!("../schemas/gift_card.json"),
        include_str!("../schemas/mining.json"),
        include_str!("../schemas/pay.json"),
        include_str!("../schemas/tax.json"),
        include_str!("../schemas/loan.json"),
        include_str!("../schemas/vip_loan.json"),
        include_str!("../schemas/prediction.json"),
    ]
    .into_iter()
    .flat_map(|raw| serde_json::from_str::<Vec<Endpoint>>(raw).expect("checked endpoint schemas"))
    .collect()
}
