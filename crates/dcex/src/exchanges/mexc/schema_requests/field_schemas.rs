//! Withdrawals, rebates and MM STP groups from endpoint-specific official tables.
use crate::exchanges::mexc::params::invalid;
use crate::exchanges::mexc::{
    client::{MexcApi, MexcClient},
    params::{MexcParams, validate_u64_range},
};
use crate::{DcexError, Result, exchange::ValidatedResponse, http::HttpMethod};
use serde::Deserialize;
use serde_json::{Map, Value};
use std::{collections::HashMap, sync::OnceLock};

use crate::exchanges::schema::Field;
#[derive(Deserialize)]
struct Endpoint {
    name: String,
    method: String,
    path: String,
    fields: Vec<Field>,
}

fn endpoints() -> &'static HashMap<String, Endpoint> {
    static CACHE: OnceLock<HashMap<String, Endpoint>> = OnceLock::new();
    CACHE.get_or_init(|| {
        let items: Vec<Endpoint> = load_schemas();
        items.into_iter().map(|e| (e.name.clone(), e)).collect()
    })
}

impl MexcClient {
    pub(in crate::exchanges::mexc) async fn field_schema_request(
        &self,
        name: &str,
        p: &MexcParams,
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

    pub(in crate::exchanges::mexc) async fn field_schema_request_transport(
        &self,
        name: &str,
        p: &MexcParams,
    ) -> Result<Option<ValidatedResponse>> {
        if name == "place_contract_batch_orders" {
            p.ensure_allowed(&["orders"])?;
            let orders = p.json_required("orders")?;
            let items = orders
                .as_array()
                .filter(|a| !a.is_empty() && a.len() <= 50)
                .ok_or_else(|| invalid("orders requires 1..50 objects"))?;
            for item in items {
                let object = item
                    .as_object()
                    .ok_or_else(|| invalid("each order must be an object"))?;
                for key in [
                    "symbol", "price", "vol", "side", "type", "openType", "stpMode",
                ] {
                    if !object.contains_key(key) {
                        return Err(invalid(format!("{key} is required")));
                    }
                }
                if item["symbol"].as_str().is_none_or(|s| s.trim().is_empty()) {
                    return Err(invalid("symbol must be a nonempty native symbol"));
                }
                if !item["vol"]
                    .as_str()
                    .is_some_and(crate::common::is_positive_plain_decimal)
                {
                    return Err(invalid("vol requires a positive plain decimal string"));
                }
                let price = item["price"]
                    .as_str()
                    .ok_or_else(|| invalid("price requires a decimal string"))?;
                if !(crate::common::is_positive_plain_decimal(price)
                    || price == "0" && item["type"].as_u64() == Some(5))
                {
                    return Err(invalid(
                        "price requires a positive decimal or 0 for market orders",
                    ));
                }
                for (key, low, high) in [
                    ("side", 1, 4),
                    ("type", 1, 5),
                    ("openType", 1, 2),
                    ("stpMode", 0, 3),
                ] {
                    if !item[key].as_u64().is_some_and(|n| n >= low && n <= high) {
                        return Err(invalid(format!("invalid {key}")));
                    }
                }
                if matches!(item["side"].as_u64(), Some(1 | 3))
                    && item["leverage"].as_u64().is_none_or(|n| n == 0)
                {
                    return Err(invalid("opening orders require positive integer leverage"));
                }
            }
            return self
                .contract_post_json("/api/v1/private/order/submit_batch", orders)
                .await
                .map(Some);
        }
        let Some(e) = endpoints().get(name) else {
            return Ok(None);
        };
        let keys: Vec<_> = e.fields.iter().map(|f| f.name.as_str()).collect();
        p.ensure_allowed(&keys)?;
        let mut body = Map::new();
        for f in &e.fields {
            if f.required && p.required(&f.name)?.trim().is_empty() {
                return Err(invalid(format!("{} is required", f.name)));
            }
            if let Some(raw) = p.get(&f.name) {
                f.encode(raw)?;
                let value = if f.kind == "number[]" {
                    let values: Vec<u64> = serde_json::from_str(raw)
                        .map_err(|_| invalid("blacklist requires integer UIDs"))?;
                    if values.is_empty()
                        || (name == "create_contract_stp_group" && values.len() < 2)
                    {
                        return Err(invalid(
                            "create STP group requires at least two UIDs; update requires a nonempty list",
                        ));
                    }
                    serde_json::to_value(values).map_err(|e| DcexError::Decode(e.to_string()))?
                } else {
                    if matches!(f.kind.as_str(), "int" | "long") {
                        raw.parse::<u64>().map_err(|_| {
                            invalid(format!("{} requires an unsigned integer", f.name))
                        })?;
                    }
                    Value::String(raw.into())
                };
                body.insert(f.name.clone(), value);
            }
        }
        validate_u64_range(p, "recvWindow", 1, 60000)?;
        if let Some(amount) = p.get("amount")
            && !crate::common::is_positive_plain_decimal(amount)
        {
            return Err(invalid("amount requires a positive plain decimal string"));
        }
        if e.path.starts_with("/api/v1/") && e.method == "POST" {
            return self
                .contract_post_json(&e.path, Value::Object(body))
                .await
                .map(Some);
        }
        let method = match e.method.as_str() {
            "GET" => HttpMethod::Get,
            "POST" => HttpMethod::Post,
            "DELETE" => HttpMethod::Delete,
            _ => return Err(invalid("unsupported method")),
        };
        let api = if e.path.starts_with("/api/v3/") {
            MexcApi::Spot
        } else {
            MexcApi::Contract
        };
        self.request(method, api, &e.path, p.only(&keys), None, true)
            .await
            .map(Some)
    }
}

fn load_schemas() -> Vec<Endpoint> {
    [
        include_str!("../schemas/stp.json"),
        include_str!("../schemas/affiliate.json"),
        include_str!("../schemas/tax.json"),
        include_str!("../schemas/rebates.json"),
        include_str!("../schemas/referral.json"),
        include_str!("../schemas/withdrawals.json"),
        include_str!("../schemas/transfers.json"),
    ]
    .into_iter()
    .flat_map(|raw| serde_json::from_str::<Vec<Endpoint>>(raw).expect("checked endpoint schemas"))
    .collect()
}
