pub(in crate::exchanges::arcus) use std::collections::BTreeMap;

pub(in crate::exchanges::arcus) use ed25519_dalek::Signer;
pub(in crate::exchanges::arcus) use serde_json::{Value, json};

pub(in crate::exchanges::arcus) use super::client::ArcusClient;
pub(in crate::exchanges::arcus) use super::params::{
    compare_decimals, decimal_parts, decimal_product_below, exact_units, required,
};
pub(in crate::exchanges::arcus) use super::signing::{legacy_signing_message, timestamp_ns};
pub(in crate::exchanges::arcus) use crate::http::{HttpMethod, HttpRequest, RequestBody};
pub(in crate::exchanges::arcus) use crate::{DcexError, Result};

/// Fields the signed placeOrder payload is built from; anything else is rejected, not dropped.
pub(in crate::exchanges::arcus) const PLACE_ORDER_KEYS: &[&str] = &[
    "product_symbol",
    "side",
    "price",
    "quantity",
    "order_type",
    "time_in_force",
    "good_til_time",
    "reduce_only",
    "client_order_id",
];
/// Fields the signed modifyOrder payload is built from.
pub(in crate::exchanges::arcus) const MODIFY_ORDER_KEYS: &[&str] = &[
    "product_symbol",
    "side",
    "price",
    "quantity",
    "time_in_force",
    "good_til_time",
    "reduce_only",
    "client_order_id",
    "order_id",
];

impl ArcusClient {
    /// Builds a signed WebSocket trading frame using the same validation and signing as REST.
    /// May fetch market metadata, but never submits the trading request.
    pub async fn sign_websocket_request(
        &self,
        id: u64,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<Value> {
        let request = self.build_private_request(method_name, params).await?;
        let RequestBody::Json(mut payload) = request.body else {
            return Err(DcexError::Decode(
                "Arcus signed request must have a JSON body".into(),
            ));
        };
        // REST carries address in the URL; the WebSocket payload carries it in the body.
        payload["address"] = json!(
            self.address
                .as_deref()
                .ok_or_else(|| DcexError::InvalidInput("Arcus address is required".into()))?
        );
        Ok(json!({"type":"post","id":id,"request":{
            "type":request.path.trim_start_matches("/v1/"),"payload":payload,
            "apiKey":request.headers["X-API-Key"],"timestamp":request.headers["X-Timestamp"],"signature":request.headers["X-Signature"]
        }}))
    }

    pub(in crate::exchanges::arcus) async fn build_private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<HttpRequest> {
        if method_name == "place_order"
            && params
                .iter()
                .any(|(key, _)| matches!(key.as_str(), "tpsl_type" | "stop_price"))
        {
            return Err(DcexError::InvalidInput(
                "Arcus TP/SL orders require batch_place_orders and its grouping field".into(),
            ));
        }
        let allowed: &[&str] = match method_name {
            "place_order" => PLACE_ORDER_KEYS,
            "modify_order" => MODIFY_ORDER_KEYS,
            "cancel_order" => &["product_symbol", "order_id"],
            _ => &[],
        };
        if !allowed.is_empty()
            && let Some((key, _)) = params
                .iter()
                .find(|(key, _)| !allowed.contains(&key.as_str()))
        {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Arcus {method_name} parameter: {key}"
            )));
        }
        if matches!(
            method_name,
            "cancel_all_orders"
                | "set_leverage"
                | "schedule_cancel"
                | "disarm_scheduled_cancel"
                | "adjust_isolated_margin"
        ) {
            return self.legacy_private_request(method_name, params).await;
        }
        if matches!(
            method_name,
            "batch_place_orders" | "batch_cancel_orders" | "batch_modify_orders"
        ) {
            return self.batch_order_request(method_name, params).await;
        }
        let address = self.address.as_deref().ok_or_else(|| {
            DcexError::InvalidInput("Arcus wallet address is required for trading".into())
        })?;
        let timestamp = timestamp_ns()?;
        let values: BTreeMap<_, _> = params.into_iter().collect();
        let (path, body, signature) = self
            .signed_order_payload(method_name, &values, timestamp, false)
            .await?;
        let mut request = HttpRequest::new(HttpMethod::Post, &self.base_url, path)
            .query("address", address)
            .json(body);
        request
            .headers
            .insert("X-API-Key".into(), self.api_key.clone().unwrap_or_default());
        request
            .headers
            .insert("X-Timestamp".into(), timestamp.to_string());
        request.headers.insert("X-Signature".into(), signature);
        Ok(request)
    }

    pub(in crate::exchanges::arcus) async fn signed_order_payload(
        &self,
        method_name: &str,
        values: &BTreeMap<String, String>,
        timestamp: u64,
        position_tpsl: bool,
    ) -> Result<(&'static str, Value, String)> {
        let address = self.address.as_deref().ok_or_else(|| {
            DcexError::InvalidInput("Arcus wallet address is required for trading".into())
        })?;
        let key = self.signing_key.as_ref().ok_or_else(|| {
            DcexError::InvalidInput("Arcus API signing key is required for trading".into())
        })?;
        let market = required(values, "product_symbol")?;
        let market_info = self.market_info(market).await?;
        let market_id = market_info["marketId"]
            .as_u64()
            .ok_or_else(|| DcexError::Decode("Arcus marketId is missing".into()))?;
        let mut canonical = BTreeMap::new();
        canonical.insert("ad", json!(address.to_ascii_lowercase()));
        canonical.insert("ai", json!(self.account_index));
        canonical.insert("ct", json!(timestamp));
        canonical.insert("m", json!(market_id));
        canonical.insert("v", json!(1));
        let (path, body) = match method_name {
            "place_order" | "modify_order" => {
                let is_modify = method_name == "modify_order";
                let tpsl = values.get("tpsl_type").map(String::as_str);
                if tpsl.is_some_and(|kind| !["STOP_LOSS", "TAKE_PROFIT"].contains(&kind)) {
                    return Err(DcexError::InvalidInput("invalid Arcus tpsl_type".into()));
                }
                if values.contains_key("stop_price") != tpsl.is_some() {
                    return Err(DcexError::InvalidInput(
                        "Arcus tpsl_type and stop_price must be supplied together".into(),
                    ));
                }
                let side = required(values, "side")?.to_ascii_uppercase();
                let side_number = match side.as_str() {
                    "BUY" => 0,
                    "SELL" => 1,
                    _ => {
                        return Err(DcexError::InvalidInput(
                            "Arcus side must be BUY or SELL".into(),
                        ));
                    }
                };
                let order_type = values
                    .get("order_type")
                    .map(String::as_str)
                    .unwrap_or("LIMIT")
                    .to_ascii_uppercase();
                if !matches!(order_type.as_str(), "LIMIT" | "MARKET") {
                    return Err(DcexError::InvalidInput(
                        "Arcus supports LIMIT or MARKET orders".into(),
                    ));
                }
                let time_in_force = if is_modify {
                    required(values, "time_in_force")?
                } else {
                    values
                        .get("time_in_force")
                        .map(String::as_str)
                        .unwrap_or("GTT")
                }
                .to_ascii_uppercase();
                let tif = match time_in_force.as_str() {
                    "GTT" => 0,
                    "FOK" => 1,
                    "IOC" => 2,
                    "ALO" => 3,
                    _ => {
                        return Err(DcexError::InvalidInput(
                            "unsupported Arcus time in force".into(),
                        ));
                    }
                };
                if !is_modify && order_type == "MARKET" && tif != 2 {
                    return Err(DcexError::InvalidInput(
                        "Arcus MARKET orders require IOC".into(),
                    ));
                }
                let price = required(values, "price")?;
                let quantity = required(values, "quantity")?;
                let tick = market_info["tickSize"]
                    .as_str()
                    .ok_or_else(|| DcexError::Decode("Arcus tickSize is missing".into()))?;
                let step = market_info["stepSize"]
                    .as_str()
                    .ok_or_else(|| DcexError::Decode("Arcus stepSize is missing".into()))?;
                let price_ticks = exact_units(price, tick)?;
                let quantity_quantums = if position_tpsl {
                    if compare_decimals(quantity, "0")? != 0 {
                        return Err(DcexError::InvalidInput(
                            "Arcus positionTpsl requires quantity zero".into(),
                        ));
                    }
                    0
                } else {
                    exact_units(quantity, step)?
                };
                if let Some(min_size) = market_info["minOrderSize"].as_str()
                    && !position_tpsl
                    && compare_decimals(quantity, min_size)? < 0
                {
                    return Err(DcexError::InvalidInput(
                        "Arcus quantity is below minOrderSize".into(),
                    ));
                }
                if let Some(max_size) = market_info["maxOrderSize"].as_str()
                    && compare_decimals(quantity, max_size)? > 0
                {
                    return Err(DcexError::InvalidInput(
                        "Arcus quantity exceeds maxOrderSize".into(),
                    ));
                }
                if let Some(min_notional) = market_info["minOrderNotional"].as_str()
                    && !position_tpsl
                    && decimal_product_below(price, quantity, min_notional)?
                {
                    return Err(DcexError::InvalidInput(
                        "Arcus order is below minOrderNotional".into(),
                    ));
                }
                let good_til_time = if is_modify {
                    Some(required(values, "good_til_time")?)
                } else {
                    values.get("good_til_time").map(String::as_str)
                }
                .map(|value| {
                    value
                        .parse::<u64>()
                        .map_err(|_| DcexError::InvalidInput("invalid good_til_time".into()))
                })
                .transpose()?
                .unwrap_or(timestamp / 1_000 + 40 * 86_400 * 1_000_000);
                if good_til_time < timestamp / 1_000 + 31 * 86_400 * 1_000_000 {
                    return Err(DcexError::InvalidInput(
                        "Arcus good_til_time must be at least one month ahead".into(),
                    ));
                }
                let reduce_only = match values.get("reduce_only").map(String::as_str) {
                    None if is_modify => {
                        return Err(DcexError::InvalidInput(
                            "Arcus modify_order requires reduce_only".into(),
                        ));
                    }
                    None | Some("false") => false,
                    Some("true") => true,
                    _ => {
                        return Err(DcexError::InvalidInput(
                            "Arcus reduce_only must be true or false".into(),
                        ));
                    }
                };
                let good_til_ns = good_til_time.checked_mul(1_000).ok_or_else(|| {
                    DcexError::InvalidInput("Arcus good_til_time overflow".into())
                })?;
                canonical.insert("g", json!(good_til_ns));
                canonical.insert(
                    "op",
                    json!(if is_modify {
                        3
                    } else if tpsl.is_some() {
                        4
                    } else {
                        1
                    }),
                );
                canonical.insert("p", json!(price_ticks));
                canonical.insert("q", json!(quantity_quantums));
                canonical.insert("r", json!(u8::from(reduce_only)));
                canonical.insert("s", json!(side_number));
                canonical.insert("t", json!(tif));
                let mut body = if is_modify {
                    json!({
                        "address": address, "accountIndex": self.account_index, "marketId": market_id,
                        "side": side, "quantity": quantity, "price": price,
                        "timeInForce": time_in_force, "goodTilTime": good_til_time.to_string(),
                        "clientTime": timestamp.to_string(), "reduceOnly": reduce_only,
                    })
                } else {
                    json!({
                        "address": address, "accountIndex": self.account_index, "marketId": market_id,
                        "orderSide": side, "orderType": order_type, "quantity": quantity,
                        "price": price, "timeInForce": time_in_force,
                        "goodTilTime": good_til_time.to_string(), "timestamp": timestamp,
                        "reduceOnly": reduce_only,
                    })
                };
                if let Some(kind) = tpsl {
                    if !reduce_only {
                        return Err(DcexError::InvalidInput(
                            "Arcus TPSL legs require reduce_only=true".into(),
                        ));
                    }
                    let stop = required(values, "stop_price")?;
                    exact_units(stop, tick)?;
                    body["tpslType"] = json!(kind);
                    body["stopPrice"] = json!(stop);
                }
                if let Some(client_id) = values.get("client_order_id") {
                    if client_id.is_empty()
                        || client_id.len() > 36
                        || !client_id.bytes().all(|byte| {
                            byte.is_ascii_alphanumeric() || byte == b'-' || byte == b'_'
                        })
                    {
                        return Err(DcexError::InvalidInput(
                            "invalid Arcus client_order_id".into(),
                        ));
                    }
                    canonical.insert("c", json!(client_id));
                    body["clientId"] = json!(client_id);
                }
                if is_modify {
                    let order_id = values.get("order_id");
                    let client_id = values.get("client_order_id");
                    if order_id.is_some() == client_id.is_some() {
                        return Err(DcexError::InvalidInput(
                            "Arcus modify_order requires exactly one of order_id or client_order_id".into(),
                        ));
                    }
                    if let Some(order_id) = order_id {
                        if order_id.is_empty() {
                            return Err(DcexError::InvalidInput("Arcus order_id is empty".into()));
                        }
                        canonical.insert("id", json!(order_id));
                        body["orderId"] = json!(order_id);
                    }
                    ("/v1/modifyOrder", body)
                } else {
                    ("/v1/placeOrder", body)
                }
            }
            "cancel_order" => {
                let order_id = required(values, "order_id")?;
                canonical.insert("id", json!(order_id));
                canonical.insert("op", json!(2));
                (
                    "/v1/cancelOrder",
                    json!({
                        "address": address, "accountIndex": self.account_index,
                        "marketId": market_id, "kind": "orderId",
                        "orderId": order_id, "timestamp": timestamp,
                    }),
                )
            }
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unknown Arcus private method: {method_name}"
                )));
            }
        };
        let message =
            serde_json::to_vec(&canonical).map_err(|error| DcexError::Decode(error.to_string()))?;
        let signature = hex::encode(key.sign(&message).to_bytes());
        Ok((path, body, signature))
    }
}
