//! Spot trading, transfers and builder-code routes (same host and HMAC auth as perps).
use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::OndoClient;
use super::endpoints::*;
use super::market::validate_pagination_and_time;
use super::params::{OndoParams, path_with_id};

/// Documented Spot order fields; Spot orders take a base `size` and no `quoteSize`.
const SPOT_ORDER_FIELDS: &[&str] = &[
    "market",
    "side",
    "price",
    "size",
    "clientOrderId",
    "type",
    "timeInForce",
    "postOnly",
];
const ORDER_QUERY: &[&str] = &[
    "cursor",
    "limit",
    "market",
    "status",
    "orderType",
    "hasFill",
    "activeOnly",
    "startTime",
    "endTime",
];
const FILL_QUERY: &[&str] = &["cursor", "limit", "market", "startTime", "endTime"];

impl OndoClient {
    pub(super) async fn spot_private_request(
        &self,
        method_name: &str,
        params: &OndoParams,
    ) -> Result<Option<ValidatedResponse>> {
        let response = match method_name {
            "place_spot_order" | "place_spot_order_delayed" => {
                let path = if method_name == "place_spot_order" {
                    SPOT_ORDERS.to_string()
                } else {
                    format!("{SPOT_ORDERS}/delayed")
                };
                self.spot_post(&path, spot_order_body(params)?).await
            }
            "place_spot_batch_orders" | "place_spot_batch_orders_delayed" => {
                let body = params.body(&["orders"], &["orders"], &[], &[], &["orders"])?;
                let orders = body
                    .get("orders")
                    .and_then(Value::as_array)
                    .filter(|orders| (1..=20).contains(&orders.len()))
                    .ok_or_else(|| {
                        DcexError::InvalidInput(
                            "Ondo Spot batch orders must be a JSON array of 1 to 20 orders"
                                .to_string(),
                        )
                    })?;
                for order in orders {
                    validate_spot_order(order)?;
                }
                let path = if method_name == "place_spot_batch_orders" {
                    SPOT_BATCH_ORDERS.to_string()
                } else {
                    format!("{SPOT_BATCH_ORDERS}/delayed")
                };
                self.spot_post(&path, body).await
            }
            "cancel_spot_batch_orders" => {
                params.ensure_allowed(&["orderIDs"])?;
                params.ensure_required(&["orderIDs"])?;
                self.spot_query(
                    HttpMethod::Delete,
                    SPOT_BATCH_ORDERS,
                    params.only(&["orderIDs"]),
                )
                .await
            }
            "get_spot_orders" => {
                params.ensure_allowed(ORDER_QUERY)?;
                params.optional_one_of("status", &["open", "fullyFilled", "canceled"])?;
                params.optional_bool("hasFill")?;
                params.optional_bool("activeOnly")?;
                validate_pagination_and_time(params)?;
                self.spot_query(HttpMethod::Get, SPOT_ORDERS, params.only(ORDER_QUERY))
                    .await
            }
            "cancel_spot_orders" => {
                params.ensure_allowed(&["market"])?;
                self.spot_query(HttpMethod::Delete, SPOT_ORDERS, params.only(&["market"]))
                    .await
            }
            "get_spot_order" | "cancel_spot_order" | "get_spot_order_fills" => {
                params.ensure_allowed(&["orderID"])?;
                let path = path_with_id(SPOT_ORDERS, params.path_segment("orderID")?);
                match method_name {
                    "get_spot_order" => self.spot_query(HttpMethod::Get, &path, Vec::new()).await,
                    "cancel_spot_order" => {
                        self.spot_query(HttpMethod::Delete, &path, Vec::new()).await
                    }
                    _ => {
                        self.spot_query(HttpMethod::Get, &format!("{path}/fills"), Vec::new())
                            .await
                    }
                }
            }
            "get_spot_fills" => {
                params.ensure_allowed(FILL_QUERY)?;
                validate_pagination_and_time(params)?;
                self.spot_query(HttpMethod::Get, SPOT_FILLS, params.only(FILL_QUERY))
                    .await
            }
            "export_spot_orders_csv" => {
                const KEYS: &[&str] = &["market", "startTime", "endTime", "status", "orderType"];
                params.ensure_allowed(KEYS)?;
                params.ensure_time_order("startTime", "endTime")?;
                self.spot_query(
                    HttpMethod::Get,
                    &format!("{SPOT_ORDERS}/csv"),
                    params.only(KEYS),
                )
                .await
            }
            "export_spot_fills_csv" => {
                const KEYS: &[&str] = &["market", "startTime", "endTime", "status"];
                params.ensure_allowed(KEYS)?;
                params.ensure_time_order("startTime", "endTime")?;
                self.spot_query(
                    HttpMethod::Get,
                    &format!("{SPOT_FILLS}/csv"),
                    params.only(KEYS),
                )
                .await
            }
            "get_spot_candles" => {
                const KEYS: &[&str] = &["market", "resolution", "from", "to", "countback"];
                params.ensure_allowed(KEYS)?;
                params.ensure_required(&["market", "resolution", "to"])?;
                if params.get("from").is_some() == params.get("countback").is_some() {
                    return Err(DcexError::InvalidInput(
                        "Ondo Spot candles require exactly one of from or countback".to_string(),
                    ));
                }
                params.optional_u64("from")?;
                params.optional_u64("to")?;
                params.optional_u64_range("countback", 1, u64::MAX)?;
                params.ensure_time_order("from", "to")?;
                self.spot_query(HttpMethod::Get, SPOT_CANDLES, params.only(KEYS))
                    .await
            }
            "get_spot_balances" => {
                params.ensure_allowed(&[])?;
                self.spot_query(HttpMethod::Get, SPOT_BALANCES, Vec::new())
                    .await
            }
            "get_spot_transfers" => {
                params.ensure_allowed(&["cursor", "limit", "startTime", "endTime"])?;
                validate_pagination_and_time(params)?;
                self.spot_query(
                    HttpMethod::Get,
                    SPOT_TRANSFERS,
                    params.only(&["cursor", "limit", "startTime", "endTime"]),
                )
                .await
            }
            "create_spot_transfer" => {
                let body = params.body(
                    &["from", "to", "symbol", "amount"],
                    &["from", "to", "symbol", "amount"],
                    &[],
                    &[],
                    &["from", "to"],
                )?;
                validate_spot_transfer(&body)?;
                self.spot_post(SPOT_TRANSFERS, body).await
            }
            "get_builder_code_stats" => {
                params.ensure_allowed(&["startTime", "endTime"])?;
                params.ensure_required(&["startTime"])?;
                params.ensure_time_order("startTime", "endTime")?;
                self.spot_query(
                    HttpMethod::Get,
                    BUILDER_CODE_STATS,
                    params.only(&["startTime", "endTime"]),
                )
                .await
            }
            "get_builder_code_fills" => {
                params.ensure_allowed(&[])?;
                self.spot_query(HttpMethod::Get, BUILDER_CODE_FILLS, Vec::new())
                    .await
            }
            _ => return Ok(None),
        }?;
        Ok(Some(response))
    }
}

fn spot_order_body(params: &OndoParams) -> Result<Value> {
    let body = params.body(
        SPOT_ORDER_FIELDS,
        &["market", "side", "size"],
        &["postOnly"],
        &[],
        &[],
    )?;
    validate_spot_order(&body)?;
    Ok(body)
}

/// Spot limit orders carry a price; market orders carry neither price, timeInForce nor postOnly.
fn validate_spot_order(order: &Value) -> Result<()> {
    let object = order.as_object().ok_or_else(|| {
        DcexError::InvalidInput("Ondo Spot order must be a JSON object".to_string())
    })?;
    if let Some(key) = object
        .keys()
        .find(|key| !SPOT_ORDER_FIELDS.contains(&key.as_str()))
    {
        return Err(DcexError::InvalidInput(format!(
            "unsupported Ondo Spot order field: {key}"
        )));
    }
    let text = |key: &str| object.get(key).and_then(Value::as_str);
    for key in ["market", "side", "size"] {
        if text(key).is_none_or(|value| value.trim().is_empty()) {
            return Err(DcexError::InvalidInput(format!(
                "Ondo Spot order requires {key}"
            )));
        }
    }
    if !matches!(text("side"), Some("buy" | "sell")) {
        return Err(DcexError::InvalidInput(
            "Ondo Spot order side must be buy or sell".to_string(),
        ));
    }
    if text("clientOrderId").is_some_and(|id| {
        id.is_empty()
            || !id
                .bytes()
                .all(|b| b.is_ascii_alphanumeric() || matches!(b, b'_' | b'-'))
    }) {
        return Err(DcexError::InvalidInput(
            "Ondo Spot clientOrderId must match [A-Za-z0-9_-]+".to_string(),
        ));
    }
    if object
        .get("postOnly")
        .is_some_and(|value| !value.is_boolean())
    {
        return Err(DcexError::InvalidInput(
            "Ondo Spot postOnly must be boolean".to_string(),
        ));
    }
    if text("timeInForce").is_some_and(|tif| !matches!(tif, "GTC" | "IOC")) {
        return Err(DcexError::InvalidInput(
            "Ondo Spot timeInForce must be GTC or IOC".to_string(),
        ));
    }
    match text("type").unwrap_or("limit") {
        "limit" => {
            if text("price").is_none() {
                return Err(DcexError::InvalidInput(
                    "Ondo Spot limit orders require price".to_string(),
                ));
            }
        }
        "market" => {
            if ["price", "timeInForce", "postOnly"]
                .iter()
                .any(|key| object.contains_key(*key))
            {
                return Err(DcexError::InvalidInput(
                    "Ondo Spot market orders cannot include price, timeInForce, or postOnly"
                        .to_string(),
                ));
            }
        }
        _ => {
            return Err(DcexError::InvalidInput(
                "Ondo Spot order type must be limit or market".to_string(),
            ));
        }
    }
    Ok(())
}

/// Same-account moves between the main or margin wallet and the spot wallet.
fn validate_spot_transfer(body: &Value) -> Result<()> {
    let wallet = |side: &str| -> Result<&str> {
        let key = body[side].as_object().ok_or_else(|| {
            DcexError::InvalidInput(format!("Ondo Spot transfer {side} must be an object"))
        })?;
        if let Some(name) = key
            .keys()
            .find(|name| !matches!(name.as_str(), "id" | "wallet"))
        {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Ondo Spot transfer {side} field: {name}"
            )));
        }
        key.get("wallet")
            .and_then(Value::as_str)
            .filter(|wallet| matches!(*wallet, "main" | "margin" | "spot"))
            .ok_or_else(|| {
                DcexError::InvalidInput(format!(
                    "Ondo Spot transfer {side}.wallet must be main, margin or spot"
                ))
            })
    };
    let (from, to) = (wallet("from")?, wallet("to")?);
    if from == to || (from != "spot" && to != "spot") {
        return Err(DcexError::InvalidInput(
            "Ondo Spot transfers move between spot and main or margin".to_string(),
        ));
    }
    if body["from"].get("id") != body["to"].get("id") {
        return Err(DcexError::InvalidInput(
            "Ondo Spot transfer from.id and to.id must name the same account".to_string(),
        ));
    }
    if !body["amount"]
        .as_str()
        .is_some_and(crate::common::is_positive_plain_decimal)
    {
        return Err(DcexError::InvalidInput(
            "Ondo Spot transfer amount must be a positive decimal".to_string(),
        ));
    }
    Ok(())
}
