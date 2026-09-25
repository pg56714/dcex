use std::collections::BTreeMap;

use ed25519_dalek::Signer;
use serde_json::{json, Value};

use super::client::ArcusClient;
use super::params::{compare_decimals, decimal_product_below, exact_units, required};
use super::signing::{legacy_signing_message, timestamp_ns};
use crate::exchange::ValidatedResponse;
use crate::http::{HttpMethod, HttpRequest};
use crate::{DcexError, Result};

impl ArcusClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        if method_name == "submit_internal_transfer" {
            return self.submit_internal_transfer_request(params).await;
        }
        if matches!(method_name, "cancel_all_orders" | "set_leverage") {
            return self.legacy_private_request(method_name, params).await;
        }
        let address = self.address.as_deref().ok_or_else(|| {
            DcexError::InvalidInput("Arcus wallet address is required for trading".into())
        })?;
        let key = self.signing_key.as_ref().ok_or_else(|| {
            DcexError::InvalidInput("Arcus API signing key is required for trading".into())
        })?;
        let timestamp = timestamp_ns()?;
        let values: BTreeMap<_, _> = params.into_iter().collect();
        let market = required(&values, "product_symbol")?;
        let market_info = self.market_info(market).await?;
        let market_id = market_info["marketId"]
            .as_u64()
            .ok_or_else(|| DcexError::Decode("Arcus marketId is missing".into()))?;
        let mut canonical = BTreeMap::new();
        canonical.insert("ad", json!(address));
        canonical.insert("ai", json!(self.account_index));
        canonical.insert("ct", json!(timestamp));
        canonical.insert("m", json!(market_id));
        canonical.insert("v", json!(1));
        let (path, body) = match method_name {
            "place_order" | "modify_order" => {
                let is_modify = method_name == "modify_order";
                if is_modify && values.contains_key("order_type") {
                    return Err(DcexError::InvalidInput(
                        "Arcus modify_order does not accept order_type".into(),
                    ));
                }
                let side = required(&values, "side")?.to_ascii_uppercase();
                let side_number = match side.as_str() {
                    "BUY" => 0,
                    "SELL" => 1,
                    _ => {
                        return Err(DcexError::InvalidInput(
                            "Arcus side must be BUY or SELL".into(),
                        ))
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
                    required(&values, "time_in_force")?
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
                        ))
                    }
                };
                if !is_modify && order_type == "MARKET" && tif != 2 {
                    return Err(DcexError::InvalidInput(
                        "Arcus MARKET orders require IOC".into(),
                    ));
                }
                let price = required(&values, "price")?;
                let quantity = required(&values, "quantity")?;
                let tick = market_info["tickSize"]
                    .as_str()
                    .ok_or_else(|| DcexError::Decode("Arcus tickSize is missing".into()))?;
                let step = market_info["stepSize"]
                    .as_str()
                    .ok_or_else(|| DcexError::Decode("Arcus stepSize is missing".into()))?;
                let price_ticks = exact_units(price, tick)?;
                let quantity_quantums = exact_units(quantity, step)?;
                if let Some(min_size) = market_info["minOrderSize"].as_str() {
                    if compare_decimals(quantity, min_size)? < 0 {
                        return Err(DcexError::InvalidInput(
                            "Arcus quantity is below minOrderSize".into(),
                        ));
                    }
                }
                if let Some(max_size) = market_info["maxOrderSize"].as_str() {
                    if compare_decimals(quantity, max_size)? > 0 {
                        return Err(DcexError::InvalidInput(
                            "Arcus quantity exceeds maxOrderSize".into(),
                        ));
                    }
                }
                if let Some(min_notional) = market_info["minOrderNotional"].as_str() {
                    if decimal_product_below(price, quantity, min_notional)? {
                        return Err(DcexError::InvalidInput(
                            "Arcus order is below minOrderNotional".into(),
                        ));
                    }
                }
                let good_til_time = if is_modify {
                    Some(required(&values, "good_til_time")?)
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
                        ))
                    }
                    None | Some("false") => false,
                    Some("true") => true,
                    _ => {
                        return Err(DcexError::InvalidInput(
                            "Arcus reduce_only must be true or false".into(),
                        ))
                    }
                };
                let good_til_ns = good_til_time.checked_mul(1_000).ok_or_else(|| {
                    DcexError::InvalidInput("Arcus good_til_time overflow".into())
                })?;
                canonical.insert("g", json!(good_til_ns));
                canonical.insert("op", json!(if is_modify { 3 } else { 1 }));
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
                let order_id = required(&values, "order_id")?;
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
                )))
            }
        };
        let message =
            serde_json::to_vec(&canonical).map_err(|error| DcexError::Decode(error.to_string()))?;
        let signature = hex::encode(key.sign(&message).to_bytes());
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
        self.execute(request).await
    }

    async fn submit_internal_transfer_request(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let values: BTreeMap<_, _> = params.into_iter().collect();
        if values.keys().any(|key| key != "signed_transfer_json") {
            return Err(DcexError::InvalidInput(
                "unknown Arcus internal transfer parameter".into(),
            ));
        }
        let body: Value = serde_json::from_str(required(&values, "signed_transfer_json")?)
            .map_err(|error| DcexError::InvalidInput(format!("invalid transfer JSON: {error}")))?;
        let object = body.as_object().ok_or_else(|| {
            DcexError::InvalidInput("Arcus internal transfer must be an object".into())
        })?;
        let transfer_address = object
            .get("ethereumAddress")
            .and_then(Value::as_str)
            .ok_or_else(|| {
                DcexError::InvalidInput("transfer ethereumAddress is required".into())
            })?;
        if transfer_address.len() != 42
            || !transfer_address.starts_with("0x")
            || !transfer_address[2..]
                .bytes()
                .all(|byte| byte.is_ascii_hexdigit())
        {
            return Err(DcexError::InvalidInput(
                "invalid transfer ethereumAddress".into(),
            ));
        }
        if self
            .address
            .as_deref()
            .is_some_and(|address| !address.eq_ignore_ascii_case(transfer_address))
        {
            return Err(DcexError::InvalidInput(
                "transfer ethereumAddress does not match configured wallet".into(),
            ));
        }
        let from = object
            .get("fromAccountIndex")
            .and_then(Value::as_u64)
            .ok_or_else(|| DcexError::InvalidInput("fromAccountIndex is required".into()))?;
        let to = object
            .get("toAccountIndex")
            .and_then(Value::as_u64)
            .ok_or_else(|| DcexError::InvalidInput("toAccountIndex is required".into()))?;
        if from > 9 || to > 9 || from == to {
            return Err(DcexError::InvalidInput(
                "transfer account indexes must differ and be 0..=9".into(),
            ));
        }
        let amount = object
            .get("amount")
            .and_then(Value::as_str)
            .ok_or_else(|| DcexError::InvalidInput("transfer amount is required".into()))?;
        if amount.is_empty() || !amount.bytes().all(|byte| byte.is_ascii_digit()) {
            return Err(DcexError::InvalidInput(
                "transfer amount must be decimal quote quantums".into(),
            ));
        }
        let amount = amount
            .parse::<i64>()
            .map_err(|_| DcexError::InvalidInput("invalid transfer amount".into()))?;
        if amount <= 0 {
            return Err(DcexError::InvalidInput(
                "transfer amount must be positive quote quantums".into(),
            ));
        }
        let nonce = object
            .get("nonce")
            .and_then(Value::as_str)
            .ok_or_else(|| DcexError::InvalidInput("transfer nonce is required".into()))?;
        if nonce.is_empty() || nonce.len() > 64 {
            return Err(DcexError::InvalidInput(
                "transfer nonce must be 1..=64 characters".into(),
            ));
        }
        let signature = object
            .get("signature")
            .and_then(Value::as_object)
            .ok_or_else(|| DcexError::InvalidInput("transfer signature is required".into()))?;
        for component in ["r", "s"] {
            let valid = signature
                .get(component)
                .and_then(Value::as_str)
                .is_some_and(|value| {
                    value.len() == 66
                        && value.starts_with("0x")
                        && value[2..].bytes().all(|byte| byte.is_ascii_hexdigit())
                });
            if !valid {
                return Err(DcexError::InvalidInput(format!(
                    "transfer signature {component} must be 32-byte hex"
                )));
            }
        }
        if !matches!(
            signature.get("v").and_then(Value::as_str),
            Some("0x1b" | "0x1c")
        ) {
            return Err(DcexError::InvalidInput(
                "transfer signature v must be 0x1b or 0x1c".into(),
            ));
        }
        self.execute(HttpRequest::new(HttpMethod::Post, &self.base_url, "/v1/transfer").json(body))
            .await
    }

    async fn legacy_private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let address = self.address.as_deref().ok_or_else(|| {
            DcexError::InvalidInput("Arcus wallet address is required for trading".into())
        })?;
        let key = self.signing_key.as_ref().ok_or_else(|| {
            DcexError::InvalidInput("Arcus API signing key is required for trading".into())
        })?;
        let values: BTreeMap<_, _> = params.into_iter().collect();
        let mut body: BTreeMap<String, Value> = BTreeMap::new();
        body.insert("address".into(), json!(address));
        body.insert("accountIndex".into(), json!(self.account_index));
        let (action, path) = match method_name {
            "cancel_all_orders" => {
                if let Some(market) = values.get("product_symbol") {
                    let info = self.market_info(market).await?;
                    let market_id = info["marketId"]
                        .as_u64()
                        .ok_or_else(|| DcexError::Decode("Arcus marketId is missing".into()))?;
                    body.insert("marketId".into(), json!(market_id));
                }
                if let Some(valid_until) = values.get("valid_until") {
                    let millis = valid_until.parse::<u64>().map_err(|_| {
                        DcexError::InvalidInput("invalid Arcus valid_until epoch ms".into())
                    })?;
                    body.insert("validUntil".into(), json!(millis));
                }
                if values
                    .keys()
                    .any(|key| key != "product_symbol" && key != "valid_until")
                {
                    return Err(DcexError::InvalidInput(
                        "unknown Arcus cancel_all_orders parameter".into(),
                    ));
                }
                ("cancelAllOrders", "/v1/cancelAllOrders")
            }
            "set_leverage" => {
                if values
                    .keys()
                    .any(|key| key != "product_symbol" && key != "leverage" && key != "isolated")
                {
                    return Err(DcexError::InvalidInput(
                        "unknown Arcus set_leverage parameter".into(),
                    ));
                }
                let info = self
                    .market_info(required(&values, "product_symbol")?)
                    .await?;
                let market_id = info["marketId"]
                    .as_u64()
                    .ok_or_else(|| DcexError::Decode("Arcus marketId is missing".into()))?;
                let leverage = required(&values, "leverage")?
                    .parse::<u16>()
                    .map_err(|_| DcexError::InvalidInput("invalid Arcus leverage".into()))?;
                if !(1..=1000).contains(&leverage) {
                    return Err(DcexError::InvalidInput(
                        "Arcus leverage must be in 1..=1000".into(),
                    ));
                }
                body.insert("marketId".into(), json!(market_id));
                body.insert("leverage".into(), json!(leverage));
                if let Some(isolated) = values.get("isolated") {
                    let enabled = match isolated.as_str() {
                        "true" => true,
                        "false" => false,
                        _ => {
                            return Err(DcexError::InvalidInput(
                                "Arcus isolated must be true or false".into(),
                            ))
                        }
                    };
                    body.insert("isolated".into(), json!(enabled));
                }
                ("setLeverage", "/v1/setLeverage")
            }
            _ => unreachable!("legacy method dispatch is restricted"),
        };
        let timestamp = timestamp_ns()?;
        let message = legacy_signing_message(timestamp, action, &body)?;
        let signature = hex::encode(key.sign(&message).to_bytes());
        let request = HttpRequest::new(HttpMethod::Post, &self.base_url, path)
            .query("address", address)
            .header("X-API-Key", self.api_key.clone().unwrap_or_default())
            .header("X-Timestamp", timestamp.to_string())
            .header("X-Signature", signature)
            .json(json!(body));
        self.execute(request).await
    }
}
