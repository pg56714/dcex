use serde_json::{json, Value};

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
