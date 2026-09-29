//! Withdrawal, Travel Rule and options block endpoints from the official SDK.
use std::sync::OnceLock;

use serde::Deserialize;
use serde_json::Value;

use crate::exchanges::binance::{BinanceClient, BinanceMarket, params::PublicParams};
use crate::{
    Result, common::is_positive_plain_decimal, exchange::ValidatedResponse, http::HttpMethod,
};

use crate::exchanges::schema::Field;
#[derive(Deserialize)]
struct Endpoint {
    name: String,
    method: String,
    path: String,
    parameters: Vec<Field>,
}

use crate::exchanges::binance::params::invalid;

fn validate_pii(value: &Value) -> Result<()> {
    let obj = value
        .as_object()
        .ok_or_else(|| invalid("PII must be a JSON object"))?;
    match obj.get("piiType").and_then(Value::as_u64) {
        Some(0) => {
            let names = obj
                .get("latinNames")
                .and_then(Value::as_array)
                .filter(|v| !v.is_empty())
                .ok_or_else(|| invalid("natural-person PII requires latinNames"))?;
            for name in names {
                if name
                    .get("firstName")
                    .and_then(Value::as_str)
                    .is_none_or(|v| v.trim().is_empty())
                {
                    return Err(invalid("each latinNames entry requires firstName"));
                }
            }
            if obj
                .get("residenceCountry")
                .and_then(Value::as_str)
                .is_none_or(|v| v.trim().is_empty())
            {
                return Err(invalid("natural-person PII requires residenceCountry"));
            }
        }
        Some(1) => {
            for key in ["latinName", "registrationCountry"] {
                if obj
                    .get(key)
                    .and_then(Value::as_str)
                    .is_none_or(|v| v.trim().is_empty())
                {
                    return Err(invalid(format!("legal-person PII requires {key}")));
                }
            }
        }
        _ => return Err(invalid("PII piiType must be 0 or 1")),
    }
    Ok(())
}

fn validate_legs(value: &Value) -> Result<()> {
    let legs = value
        .as_array()
        .filter(|v| v.len() == 1)
        .ok_or_else(|| invalid("options block orders support exactly one leg"))?;
    let leg = legs[0]
        .as_object()
        .ok_or_else(|| invalid("leg must be an object"))?;
    if leg
        .keys()
        .any(|k| !["symbol", "side", "type", "quantity", "price"].contains(&k.as_str()))
    {
        return Err(invalid("unknown block leg field"));
    }
    if !leg
        .get("symbol")
        .and_then(Value::as_str)
        .is_some_and(|s| !s.is_empty() && s.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'-'))
    {
        return Err(invalid("leg requires a native options symbol"));
    }
    if !matches!(
        leg.get("side").and_then(Value::as_str),
        Some("BUY" | "SELL")
    ) || leg.get("type").and_then(Value::as_str) != Some("LIMIT")
    {
        return Err(invalid("block leg requires BUY/SELL and LIMIT"));
    }
    for key in ["quantity", "price"] {
        if key == "price" && !leg.contains_key(key) {
            continue;
        }
        if !leg
            .get(key)
            .and_then(Value::as_str)
            .is_some_and(is_positive_plain_decimal)
        {
            return Err(invalid(format!(
                "{key} must be a positive plain decimal string"
            )));
        }
    }
    Ok(())
}

impl BinanceClient {
    pub(in crate::exchanges::binance) async fn field_schema_request(
        &self,
        name: &str,
        p: &PublicParams,
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

    pub(in crate::exchanges::binance) async fn field_schema_request_transport(
        &self,
        name: &str,
        p: &PublicParams,
    ) -> Result<Option<ValidatedResponse>> {
        static ENDPOINTS: OnceLock<Vec<Endpoint>> = OnceLock::new();
        let endpoints = ENDPOINTS.get_or_init(load_schemas);
        let Some(endpoint) = endpoints.iter().find(|e| e.name == name) else {
            return Ok(None);
        };
        let allowed: Vec<_> = endpoint
            .parameters
            .iter()
            .map(|f| f.name.as_str())
            .collect();
        p.ensure_allowed(&allowed)?;
        let mut seen = std::collections::BTreeSet::new();
        if p.0.iter().any(|(k, _)| !seen.insert(k)) {
            return Err(invalid("duplicate parameter"));
        }
        for f in &endpoint.parameters {
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
            match f.kind.as_str() {
                "int" => {
                    value
                        .parse::<u64>()
                        .map_err(|_| invalid(format!("{} must be an unsigned integer", f.name)))?;
                }
                "decimal" if !is_positive_plain_decimal(value) => {
                    return Err(invalid("amount must be a positive plain decimal string"));
                }
                "bool" if !["true", "false"].contains(&value) => {
                    return Err(invalid("invalid boolean"));
                }
                "json" => {
                    let parsed: Value = serde_json::from_str(value)
                        .map_err(|_| invalid(format!("invalid JSON for {}", f.name)))?;
                    match f.name.as_str() {
                        "legs" => validate_legs(&parsed)?,
                        "originatorPii" | "beneficiaryPii" => validate_pii(&parsed)?,
                        _ if !parsed.is_object() => {
                            return Err(invalid("questionnaire must be a JSON object"));
                        }
                        _ => {}
                    }
                }
                _ => {}
            }
        }
        if p.get("walletType")
            .is_some_and(|v| !["0", "1"].contains(&v))
        {
            return Err(invalid("walletType must be 0 or 1"));
        }
        if p.get("liquidity")
            .is_some_and(|v| !["MAKER", "TAKER"].contains(&v))
        {
            return Err(invalid("liquidity must be MAKER or TAKER"));
        }
        if let Some(window) = p.u64("recvWindow")?
            && (window == 0 || window > 60_000)
        {
            return Err(invalid("recvWindow must be 1..60000"));
        }
        if let (Some(start), Some(end)) = (p.u64("startTime")?, p.u64("endTime")?)
            && start > end
        {
            return Err(invalid("startTime exceeds endTime"));
        }
        let method = match endpoint.method.as_str() {
            "GET" => HttpMethod::Get,
            "POST" => HttpMethod::Post,
            "PUT" => HttpMethod::Put,
            "DELETE" => HttpMethod::Delete,
            _ => unreachable!(),
        };
        let market = if endpoint.path.starts_with("/eapi/") {
            BinanceMarket::Options
        } else {
            BinanceMarket::Spot
        };
        Ok(Some(
            self.request(method, market, endpoint.path.clone(), p.0.clone(), true)
                .await?,
        ))
    }
}

fn load_schemas() -> Vec<Endpoint> {
    [
        include_str!("../schemas/options_block.json"),
        include_str!("../schemas/withdrawals.json"),
        include_str!("../schemas/fast_withdrawals.json"),
        include_str!("../schemas/travel_rule.json"),
    ]
    .into_iter()
    .flat_map(|raw| serde_json::from_str::<Vec<Endpoint>>(raw).expect("checked endpoint schemas"))
    .collect()
}
