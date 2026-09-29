//! RFQ, affiliate, and funding endpoints with their documented parameter locations.
use std::sync::OnceLock;

use serde::Deserialize;
use serde_json::{Map, Value};

use crate::Result;
use crate::exchange::ValidatedResponse;
use crate::exchanges::kraken::{KrakenAuth, KrakenClient, params::KrakenParams};
use crate::http::HttpMethod;

#[derive(Deserialize)]
struct Field {
    name: String,
    location: String,
    required: bool,
    schema: Value,
}
#[derive(Deserialize)]
struct Endpoint {
    name: String,
    method: String,
    path: String,
    auth: String,
    fields: Vec<Field>,
}
static ENDPOINTS: OnceLock<Vec<Endpoint>> = OnceLock::new();
use crate::exchanges::kraken::params::invalid;

impl KrakenClient {
    pub(in crate::exchanges::kraken) async fn field_schema_request(
        &self,
        name: &str,
        params: &KrakenParams,
    ) -> Result<Option<ValidatedResponse>> {
        match crate::exchanges::schema::fund_domain(name) {
            Some(crate::exchanges::schema::FundDomain::Withdrawals) => {
                self.withdrawals_field_schema_request(name, params).await
            }
            Some(crate::exchanges::schema::FundDomain::Transfers) => {
                self.transfers_field_schema_request(name, params).await
            }
            None => self.field_schema_request_transport(name, params).await,
        }
    }

    pub(in crate::exchanges::kraken) async fn field_schema_request_transport(
        &self,
        name: &str,
        params: &KrakenParams,
    ) -> Result<Option<ValidatedResponse>> {
        let endpoints = ENDPOINTS.get_or_init(load_schemas);
        let Some(e) = endpoints.iter().find(|e| e.name == name) else {
            return Ok(None);
        };
        let keys: Vec<_> = e.fields.iter().map(|f| f.name.as_str()).collect();
        params.ensure_allowed(&keys)?;
        let mut fields = Map::new();
        let mut query = Vec::new();
        let mut body = None;
        let mut body_fields = Map::new();
        let mut path = e.path.clone();
        for f in &e.fields {
            let Some(raw) = params.get(&f.name) else {
                if f.required {
                    return Err(invalid(format!("{} is required", f.name)));
                }
                continue;
            };
            if raw.is_empty() {
                return Err(invalid(format!("{} cannot be empty", f.name)));
            }
            let json = matches!(
                f.schema["type"].as_str(),
                Some("object" | "array" | "boolean" | "integer" | "number")
            ) || f.schema.get("oneOf").is_some()
                || f.schema.get("allOf").is_some();
            let value: Value = if json {
                serde_json::from_str(raw)
                    .map_err(|_| invalid(format!("invalid {} JSON value", f.name)))?
            } else {
                raw.into()
            };
            let original = value.clone();
            let value = crate::exchanges::schema::encode_shape(value, &f.schema, &f.name)?;
            validate(&value, &f.schema, &f.name)?;
            match f.location.as_str() {
                "path" => {
                    if !raw
                        .bytes()
                        .all(|b| b.is_ascii_alphanumeric() || b"_-".contains(&b))
                    {
                        return Err(invalid("invalid path identifier"));
                    }
                    path = path.replace(&format!("{{{}}}", f.name), raw);
                }
                "body" => body = Some(value.clone()),
                "body_field" => {
                    body_fields.insert(f.name.clone(), value.clone());
                }
                "query" => {
                    if e.auth == "header" {
                        nested_query(&f.name, &value, &mut query)?;
                    } else {
                        query.push((
                            f.name.clone(),
                            if json && value != original {
                                value.to_string()
                            } else {
                                raw.to_owned()
                            },
                        ));
                    }
                }
                "header" => {}
                _ => return Err(invalid("unknown embedded parameter location")),
            }
            fields.insert(f.name.clone(), value);
        }
        validate_endpoint(name, &fields)?;
        let method = match e.method.as_str() {
            "GET" => HttpMethod::Get,
            "POST" => HttpMethod::Post,
            "PUT" => HttpMethod::Put,
            "DELETE" => HttpMethod::Delete,
            _ => return Err(invalid("unknown HTTP verb")),
        };
        if e.auth == "header" {
            return self
                .request_header_nonce(method, path, query, body, params.get("otp"))
                .await
                .map(Some);
        }
        if e.auth == "spot" {
            let body = serde_json::to_vec(&Value::Object(body_fields)).map_err(invalid)?;
            return self
                .request(method, KrakenAuth::Spot, path, Vec::new(), Some(body), true)
                .await
                .map(Some);
        }
        self.request(method, KrakenAuth::Futures, path, query, None, true)
            .await
            .map(Some)
    }
}

fn nested_query(key: &str, value: &Value, out: &mut Vec<(String, String)>) -> Result<()> {
    match value {
        Value::Object(object) => {
            for (child, value) in object {
                nested_query(&format!("{key}[{child}]"), value, out)?;
            }
        }
        Value::Array(values) => {
            // Matches the official guide's Python _nested_query helper. The
            // status.list array representation is not independently confirmed.
            let mut items = Vec::new();
            for item in values {
                items.push(format!(
                    "'{}'",
                    item.as_str()
                        .ok_or_else(|| invalid("query list requires strings"))?
                ));
            }
            out.push((key.into(), format!("[{}]", items.join(", "))));
        }
        Value::Null => {}
        Value::String(s) => out.push((key.into(), s.clone())),
        _ => out.push((key.into(), value.to_string())),
    }
    Ok(())
}

fn validate_endpoint(name: &str, fields: &Map<String, Value>) -> Result<()> {
    let has = |key: &str| fields.contains_key(key);
    match name {
        "accept_rfq_offer" if has("bidAccepted") == has("askAccepted") => {
            return Err(invalid(
                "exactly one of bidAccepted or askAccepted is required",
            ));
        }
        "place_rfq_offer" => {
            let flat = has("bid") || has("ask");
            let legs = has("bidSide") || has("askSide");
            if flat == legs {
                return Err(invalid(
                    "supply bid/ask or per-leg bidSide/askSide exclusively",
                ));
            }
            for key in ["bidSide", "askSide"] {
                if let Some(raw) = fields.get(key).and_then(Value::as_str) {
                    let values: Vec<Value> = serde_json::from_str(raw)
                        .map_err(|_| invalid("side pricing must be a JSON array"))?;
                    if values.is_empty()
                        || values.iter().any(|v| {
                            v["tradeable"].as_str().is_none_or(|s| s.is_empty())
                                || !v["price"].is_number()
                        })
                    {
                        return Err(invalid("side pricing requires tradeable and numeric price"));
                    }
                }
            }
        }
        "create_user_rfq" => {
            let legs = fields["json"]["legs"]
                .as_array()
                .ok_or_else(|| invalid("RFQ legs must be an array"))?;
            let mut seen = std::collections::HashSet::new();
            if legs.is_empty()
                || legs.iter().any(|leg| {
                    !seen.insert(leg["tradeable"].as_str().unwrap_or(""))
                        || leg["size"].as_f64() == Some(0.0)
                })
            {
                return Err(invalid("RFQ legs must be nonempty, unique and nonzero"));
            }
        }
        "add_assignment_program" => {
            if has("baseCurrency") != has("quoteCurrency") {
                return Err(invalid(
                    "baseCurrency and quoteCurrency are required together",
                ));
            }
            if fields["contractType"] == "flex" && !has("contract") && !has("baseCurrency") {
                return Err(invalid(
                    "flex assignment requires contract or base/quote currencies",
                ));
            }
        }
        "update_rfq_assignment_max_leverage" => {
            if !fields["maxLeverage"].as_f64().is_some_and(|n| n > 0.0) {
                return Err(invalid("maxLeverage must be positive"));
            }
        }
        "create_spot_withdrawal" => {
            if !fields["amount"]
                .as_str()
                .is_some_and(crate::common::is_positive_plain_decimal)
            {
                return Err(invalid("amount must be a positive plain decimal string"));
            }
        }
        "get_affiliate_daily_activity" => {
            if has("activity_date") {
                if has("iiban") || has("start_date") || has("end_date") {
                    return Err(invalid(
                        "activity_date and history parameters are mutually exclusive",
                    ));
                }
            } else {
                if !has("iiban") || !has("start_date") || !has("end_date") {
                    return Err(invalid("history requires iiban, start_date and end_date"));
                }
                if fields.get("all_users") == Some(&Value::Bool(true)) {
                    return Err(invalid("all_users is only available for daily activity"));
                }
                if fields["start_date"].as_str() > fields["end_date"].as_str() {
                    return Err(invalid("start_date must not exceed end_date"));
                }
                let ids: Vec<_> = fields["iiban"]
                    .as_str()
                    .expect("validated string")
                    .split(',')
                    .collect();
                let unique: std::collections::HashSet<_> = ids.iter().collect();
                if ids.len() > 10 || unique.len() != ids.len() || ids.iter().any(|s| s.is_empty()) {
                    return Err(invalid("iiban requires 1..10 distinct identifiers"));
                }
            }
        }
        "claim_funding_deposit_address" => {
            if fields["body"]["method_id"]
                .as_str()
                .is_none_or(|s| s.is_empty())
            {
                return Err(invalid("body.method_id is required"));
            }
        }
        "update_funding_address" => {
            if fields["body"]["name"].as_str().is_none_or(|s| s.is_empty()) {
                return Err(invalid("body.name is required"));
            }
        }
        _ => {}
    }
    Ok(())
}

fn validate(value: &Value, schema: &Value, field: &str) -> Result<()> {
    crate::exchanges::schema::validate_with(value, schema, field, false, false)
}

fn load_schemas() -> Vec<Endpoint> {
    [
        include_str!("../schemas/affiliate.json"),
        include_str!("../schemas/assignment_programs.json"),
        include_str!("../schemas/funding.json"),
        include_str!("../schemas/deposits.json"),
        include_str!("../schemas/withdrawals.json"),
        include_str!("../schemas/rfq.json"),
    ]
    .into_iter()
    .flat_map(|raw| serde_json::from_str::<Vec<Endpoint>>(raw).expect("checked endpoint schemas"))
    .collect()
}
