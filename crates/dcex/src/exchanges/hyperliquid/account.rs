use serde_json::{json, Value};

use crate::exchange::ValidatedResponse;
use crate::Result;

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
                json!({"type": "userFees", "user": params.required("user")?})
            }
            "clearinghouse_state" => {
                let mut payload = json!({
                    "type": "clearinghouseState",
                    "user": params.required("user")?,
                });
                insert_optional_string(&mut payload, "dex", params.get("dex"));
                payload
            }
            "spot_clearinghouse_state" => json!({
                "type": "spotClearinghouseState",
                "user": params.required("user")?,
            }),
            "open_orders" => {
                let mut payload = json!({
                    "type": "openOrders",
                    "user": params.required("user")?,
                });
                insert_optional_string(&mut payload, "dex", params.get("dex"));
                payload
            }
            "user_fills" => {
                let mut payload = json!({
                    "type": "userFills",
                    "user": params.required("user")?,
                });
                if params.optional_bool("aggregateByTime")?.unwrap_or(false) {
                    insert_optional_bool(&mut payload, "aggregateByTime", Some(true));
                }
                payload
            }
            "user_rate_limit" => json!({
                "type": "userRateLimit",
                "user": params.required("user")?,
            }),
            "order_status" => json!({
                "type": "orderStatus",
                "user": params.required("user")?,
                "oid": order_id_value(params.required("oid")?),
            }),
            "historical_orders" => json!({
                "type": "historicalOrders",
                "user": params.required("user")?,
            }),
            "subaccounts" => json!({
                "type": "subAccounts",
                "user": params.required("user")?,
            }),
            "user_role" => json!({
                "type": "userRole",
                "user": params.required("user")?,
            }),
            "portfolio" => json!({
                "type": "portfolio",
                "user": params.required("user")?,
            }),
            _ => return Ok(None),
        };
        let mut response = self.info_payload(payload).await?;
        if method_name == "subaccounts" && response.data.is_null() {
            response.data = Value::Array(Vec::new());
        }
        Ok(Some(response))
    }
}

fn order_id_value(value: &str) -> Value {
    if value.starts_with("0x") || value.starts_with("0X") {
        return Value::String(value.to_string());
    }
    value
        .parse::<i64>()
        .map(|value| Value::Number(value.into()))
        .unwrap_or_else(|_| Value::String(value.to_string()))
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
