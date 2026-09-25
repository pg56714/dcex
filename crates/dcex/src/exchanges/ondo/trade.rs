use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::OndoClient;
use super::endpoints::*;
use super::market::validate_pagination_and_time;
use super::params::{OndoParams, path_with_id};

const ORDER_FIELDS: &[&str] = &[
    "market",
    "side",
    "price",
    "size",
    "quoteSize",
    "clientOrderId",
    "type",
    "timeInForce",
    "postOnly",
    "reduceOnly",
    "takeProfit",
    "stopLoss",
    "builderCode",
];

impl OndoClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = OndoParams::from_pairs(params);
        if let Some(response) = self.account_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.trade_private_request(method_name, &params).await? {
            return Ok(response);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported Ondo private method: {method_name}"
        )))
    }

    async fn trade_private_request(
        &self,
        method_name: &str,
        params: &OndoParams,
    ) -> Result<Option<ValidatedResponse>> {
        let response = match method_name {
            "get_orders" => {
                params.ensure_allowed(&[
                    "limit",
                    "cursor",
                    "market",
                    "status",
                    "startTime",
                    "endTime",
                ])?;
                validate_pagination_and_time(params)?;
                self.private_get(
                    ORDERS,
                    params.only(&[
                        "limit",
                        "cursor",
                        "market",
                        "status",
                        "startTime",
                        "endTime",
                    ]),
                )
                .await
            }
            "get_open_orders" => {
                params.ensure_allowed(&["market"])?;
                let mut query = params.only(&["market"]);
                query.push(("status".to_string(), "open".to_string()));
                self.private_get(ORDERS, query).await
            }
            "place_order" => self.private_post(ORDERS, self.order_body(params)?).await,
            "cancel_all_orders" | "cancel_open_orders" => {
                params.ensure_allowed(&["market"])?;
                self.private_delete(ORDERS, params.only(&["market"])).await
            }
            "place_batch_orders" => {
                let body = params.body(&["orders"], &["orders"], &[], &[], &["orders"])?;
                let orders = body
                    .get("orders")
                    .and_then(Value::as_array)
                    .ok_or_else(|| {
                        DcexError::InvalidInput("Ondo orders must be a JSON array".to_string())
                    })?;
                if orders.is_empty() || orders.len() > 20 {
                    return Err(DcexError::InvalidInput(
                        "Ondo batch orders must contain between 1 and 20 orders".to_string(),
                    ));
                }
                for order in orders {
                    validate_order_value(order)?;
                }
                self.private_post(BATCH_ORDERS, body).await
            }
            "batch_cancel_orders" => {
                params.ensure_allowed(&["orderIDs"])?;
                params.ensure_required(&["orderIDs"])?;
                self.private_delete(BATCH_ORDERS, params.only(&["orderIDs"]))
                    .await
            }
            "place_twap_order" => {
                let body = params.body(
                    &[
                        "market",
                        "side",
                        "size",
                        "runningTime",
                        "frequency",
                        "reduceOnly",
                        "maxPrice",
                        "minPrice",
                    ],
                    &["market", "side", "size", "runningTime", "frequency"],
                    &["reduceOnly"],
                    &["runningTime", "frequency"],
                    &[],
                )?;
                self.private_post(TWAP_ORDER, body).await
            }
            "get_twap_order" | "cancel_twap_order" | "get_twap_order_fills" => {
                params.ensure_allowed(&["orderID"])?;
                let id = params.path_segment("orderID")?;
                let path = path_with_id(TWAP_ORDER, id);
                if method_name == "get_twap_order" {
                    self.private_get(&path, Vec::new()).await
                } else if method_name == "cancel_twap_order" {
                    self.private_delete(&path, Vec::new()).await
                } else {
                    self.private_get(&format!("{path}/fills"), Vec::new()).await
                }
            }
            "get_running_twap_orders" => {
                params.ensure_allowed(&["market"])?;
                self.private_get(TWAP_RUNNING, params.only(&["market"]))
                    .await
            }
            "get_twap_order_history" => {
                params.ensure_allowed(&["market", "limit", "cursor", "startTime", "endTime"])?;
                validate_pagination_and_time(params)?;
                self.private_get(
                    TWAP_HISTORY,
                    params.only(&["market", "limit", "cursor", "startTime", "endTime"]),
                )
                .await
            }
            "get_order" | "cancel_order" | "get_fills_by_order" => {
                params.ensure_allowed(&["orderID"])?;
                let id = params.path_segment("orderID")?;
                let path = path_with_id(ORDERS, id);
                if method_name == "get_order" {
                    self.private_get(&path, Vec::new()).await
                } else if method_name == "cancel_order" {
                    self.private_delete(&path, Vec::new()).await
                } else {
                    self.private_get(&format!("{path}/fills"), Vec::new()).await
                }
            }
            "export_orders_csv" => {
                params.ensure_allowed(&["market", "status", "startTime", "endTime"])?;
                params.ensure_time_order("startTime", "endTime")?;
                self.private_get(
                    &format!("{ORDERS}/csv"),
                    params.only(&["market", "status", "startTime", "endTime"]),
                )
                .await
            }
            "get_fills" => {
                params.ensure_allowed(&["market", "limit", "cursor", "startTime", "endTime"])?;
                validate_pagination_and_time(params)?;
                self.private_get(
                    FILLS,
                    params.only(&["market", "limit", "cursor", "startTime", "endTime"]),
                )
                .await
            }
            "export_fills_csv" => {
                params.ensure_allowed(&["market", "startTime", "endTime"])?;
                params.ensure_time_order("startTime", "endTime")?;
                self.private_get(
                    &format!("{FILLS}/csv"),
                    params.only(&["market", "startTime", "endTime"]),
                )
                .await
            }
            "get_stop_orders" => {
                params.ensure_allowed(&[])?;
                self.private_get(STOP_ORDER, Vec::new()).await
            }
            "set_stop_order" => {
                let body = params.body(
                    &[
                        "market",
                        "positionDirection",
                        "type",
                        "triggerPrice",
                        "quantity",
                        "builderCode",
                    ],
                    &["market", "positionDirection", "type", "triggerPrice"],
                    &[],
                    &[],
                    &["builderCode"],
                )?;
                self.private_post(STOP_ORDER, body).await
            }
            "remove_stop_order" => {
                params.ensure_allowed(&["market", "type"])?;
                params.ensure_required(&["market"])?;
                self.private_delete(STOP_ORDER, params.only(&["market", "type"]))
                    .await
            }
            _ => return Ok(None),
        }?;
        Ok(Some(response))
    }

    fn order_body(&self, params: &OndoParams) -> Result<Value> {
        if params.get("body").is_some() {
            let body = params.body(ORDER_FIELDS, &[], &[], &[], &[])?;
            validate_order_value(&body)?;
            return Ok(body);
        }
        params.ensure_allowed(ORDER_FIELDS)?;
        params.ensure_required(&["market", "side"])?;
        params.optional_one_of("side", &["buy", "sell"])?;
        params.optional_one_of("type", &["limit", "market"])?;
        params.optional_one_of("timeInForce", &["GTC", "IOC"])?;
        params.optional_bool("postOnly")?;
        params.optional_bool("reduceOnly")?;
        match params.get("type").unwrap_or("limit") {
            "limit" => {
                params.ensure_required(&["price", "size"])?;
                if params.get("quoteSize").is_some() {
                    return Err(DcexError::InvalidInput(
                        "Ondo limit orders cannot include quoteSize".to_string(),
                    ));
                }
            }
            "market" => {
                if params.get("price").is_some()
                    || params.get("timeInForce").is_some()
                    || params.get("postOnly").is_some()
                {
                    return Err(DcexError::InvalidInput(
                        "Ondo market orders cannot include price, timeInForce, or postOnly"
                            .to_string(),
                    ));
                }
                let size_count = usize::from(params.get("size").is_some())
                    + usize::from(params.get("quoteSize").is_some());
                if size_count != 1 {
                    return Err(DcexError::InvalidInput(
                        "Ondo market orders require exactly one of size or quoteSize".to_string(),
                    ));
                }
                if params.get("side") == Some("sell") && params.get("quoteSize").is_some() {
                    return Err(DcexError::InvalidInput(
                        "Ondo market sell orders cannot use quoteSize".to_string(),
                    ));
                }
            }
            _ => unreachable!(),
        }
        params.body(
            ORDER_FIELDS,
            &["market", "side"],
            &["postOnly", "reduceOnly"],
            &[],
            &["takeProfit", "stopLoss", "builderCode"],
        )
    }
}

fn validate_order_value(order: &Value) -> Result<()> {
    let object = order.as_object().ok_or_else(|| {
        DcexError::InvalidInput("Ondo order body must be a JSON object".to_string())
    })?;
    for key in object.keys() {
        if !ORDER_FIELDS.contains(&key.as_str()) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Ondo order field: {key}"
            )));
        }
    }
    let string = |key: &str| -> Result<Option<&str>> {
        object
            .get(key)
            .map(|value| {
                value
                    .as_str()
                    .filter(|value| !value.trim().is_empty())
                    .ok_or_else(|| {
                        DcexError::InvalidInput(format!(
                            "Ondo order field {key} must be a nonempty string"
                        ))
                    })
            })
            .transpose()
    };
    string("market")?
        .ok_or_else(|| DcexError::InvalidInput("Ondo order requires market".to_string()))?;
    let side = string("side")?
        .ok_or_else(|| DcexError::InvalidInput("Ondo order requires side".to_string()))?;
    if !matches!(side, "buy" | "sell") {
        return Err(DcexError::InvalidInput(
            "Ondo order side must be buy or sell".to_string(),
        ));
    }
    let kind = string("type")?.unwrap_or("limit");
    if !matches!(kind, "limit" | "market") {
        return Err(DcexError::InvalidInput(
            "Ondo order type must be limit or market".to_string(),
        ));
    }
    let price = string("price")?;
    let size = string("size")?;
    let quote_size = string("quoteSize")?;
    if let Some(time_in_force) = string("timeInForce")? {
        if !matches!(time_in_force, "GTC" | "IOC") {
            return Err(DcexError::InvalidInput(
                "Ondo timeInForce must be GTC or IOC".to_string(),
            ));
        }
    }
    for key in ["postOnly", "reduceOnly"] {
        if object.get(key).is_some_and(|value| !value.is_boolean()) {
            return Err(DcexError::InvalidInput(format!(
                "Ondo order field {key} must be boolean"
            )));
        }
    }
    if kind == "limit" {
        if price.is_none() || size.is_none() || quote_size.is_some() {
            return Err(DcexError::InvalidInput(
                "Ondo limit order requires price and size, but not quoteSize".to_string(),
            ));
        }
    } else if price.is_some()
        || object.contains_key("timeInForce")
        || object.contains_key("postOnly")
        || size.is_some() == quote_size.is_some()
        || (side == "sell" && quote_size.is_some())
    {
        return Err(DcexError::InvalidInput(
            "invalid Ondo market order fields".to_string(),
        ));
    }
    Ok(())
}
