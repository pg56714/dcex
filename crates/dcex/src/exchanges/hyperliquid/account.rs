use serde_json::{Value, json};

use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::HyperliquidClient;
use super::params::HyperliquidParams;

impl HyperliquidClient {
    pub(super) async fn account_public_request(
        &self,
        method_name: &str,
        params: &HyperliquidParams,
    ) -> Result<Option<ValidatedResponse>> {
        let payload = match method_name {
            "get_spot_fee_rates" | "get_futures_fee_rates" => {
                params.ensure_allowed(&["user"])?;
                json!({"type": "userFees", "user": params.address("user")?})
            }
            "clearinghouse_state" => {
                params.ensure_allowed(&["user", "dex"])?;
                let mut payload = json!({
                    "type": "clearinghouseState",
                    "user": params.address("user")?,
                });
                insert_optional_string(
                    &mut payload,
                    "dex",
                    params
                        .get("dex")
                        .map(|_| params.required("dex"))
                        .transpose()?,
                );
                payload
            }
            "spot_clearinghouse_state" => {
                params.ensure_allowed(&["user"])?;
                json!({
                    "type": "spotClearinghouseState",
                    "user": params.address("user")?,
                })
            }
            "open_orders" => {
                params.ensure_allowed(&["user", "dex"])?;
                let mut payload = json!({
                    "type": "openOrders",
                    "user": params.address("user")?,
                });
                insert_optional_string(
                    &mut payload,
                    "dex",
                    params
                        .get("dex")
                        .map(|_| params.required("dex"))
                        .transpose()?,
                );
                payload
            }
            "user_fills" => {
                params.ensure_allowed(&["user", "aggregateByTime"])?;
                let mut payload = json!({
                    "type": "userFills",
                    "user": params.address("user")?,
                });
                if params.optional_bool("aggregateByTime")?.unwrap_or(false) {
                    insert_optional_bool(&mut payload, "aggregateByTime", Some(true));
                }
                payload
            }
            "user_fills_by_time" => time_range_payload(params, "userFillsByTime", true)?,
            "user_funding" => time_range_payload(params, "userFunding", false)?,
            "user_non_funding_ledger_updates" => {
                time_range_payload(params, "userNonFundingLedgerUpdates", false)?
            }
            "user_rate_limit" => user_payload(params, "userRateLimit")?,
            "order_status" => {
                params.ensure_allowed(&["user", "oid"])?;
                json!({
                    "type": "orderStatus",
                    "user": params.address("user")?,
                    "oid": order_id_value(params.required("oid")?)?,
                })
            }
            "historical_orders" => user_payload(params, "historicalOrders")?,
            "subaccounts" => user_payload(params, "subAccounts")?,
            "user_role" => user_payload(params, "userRole")?,
            "portfolio" => user_payload(params, "portfolio")?,
            _ => return Ok(None),
        };
        let mut response = self.info_payload(payload).await?;
        if method_name == "subaccounts" && response.data.is_null() {
            response.data = Value::Array(Vec::new());
        }
        Ok(Some(response))
    }
}

fn user_payload(params: &HyperliquidParams, request_type: &str) -> Result<Value> {
    params.ensure_allowed(&["user"])?;
    Ok(json!({
        "type": request_type,
        "user": params.address("user")?,
    }))
}

fn time_range_payload(
    params: &HyperliquidParams,
    request_type: &str,
    allow_aggregate: bool,
) -> Result<Value> {
    if allow_aggregate {
        params.ensure_allowed(&["user", "startTime", "endTime", "aggregateByTime"])?;
    } else {
        params.ensure_allowed(&["user", "startTime", "endTime"])?;
    }
    let start = params.required_u64("startTime")?;
    let end = params.optional_u64("endTime")?;
    if end.is_some_and(|end| end < start) {
        return Err(DcexError::InvalidInput(
            "Hyperliquid endTime must not precede startTime".into(),
        ));
    }
    let mut payload = json!({
        "type": request_type,
        "user": params.address("user")?,
        "startTime": start,
    });
    if let Some(end) = end {
        payload["endTime"] = json!(end);
    }
    if allow_aggregate {
        if let Some(aggregate) = params.optional_bool("aggregateByTime")? {
            payload["aggregateByTime"] = json!(aggregate);
        }
    }
    Ok(payload)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn time_range_queries_preserve_official_request_types() {
        let params = HyperliquidParams::from_pairs(vec![
            ("user".into(), format!("0x{}", "11".repeat(20))),
            ("startTime".into(), "1000".into()),
            ("endTime".into(), "2000".into()),
            ("aggregateByTime".into(), "true".into()),
        ]);
        let fills = time_range_payload(&params, "userFillsByTime", true).expect("fills");
        assert_eq!(fills["type"], "userFillsByTime");
        assert_eq!(fills["startTime"], 1000);
        assert_eq!(fills["endTime"], 2000);
        assert_eq!(fills["aggregateByTime"], true);
        assert!(time_range_payload(&params, "userFunding", false).is_err());
        let funding = HyperliquidParams::from_pairs(vec![
            ("user".into(), format!("0x{}", "11".repeat(20))),
            ("startTime".into(), "2000".into()),
            ("endTime".into(), "1000".into()),
        ]);
        assert!(time_range_payload(&funding, "userFunding", false).is_err());
    }
}

fn order_id_value(value: &str) -> Result<Value> {
    if value.starts_with("0x") || value.starts_with("0X") {
        return Ok(Value::String(super::params::normalize_cloid(value, "oid")?));
    }
    value
        .parse::<u64>()
        .map(|value| Value::Number(value.into()))
        .map_err(|error| {
            DcexError::InvalidInput(format!(
                "Hyperliquid oid must be an unsigned integer or client order id: {error}"
            ))
        })
}

fn insert_optional_string(payload: &mut Value, key: &str, value: Option<&str>) {
    if let Some(value) = value {
        if let Some(object) = payload.as_object_mut() {
            object.insert(key.to_string(), Value::String(value.to_string()));
        }
    }
}

fn insert_optional_bool(payload: &mut Value, key: &str, value: Option<bool>) {
    if let Some(value) = value {
        if let Some(object) = payload.as_object_mut() {
            object.insert(key.to_string(), Value::Bool(value));
        }
    }
}
