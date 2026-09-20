//! Arcus perpetuals REST API. Spot RFQ uses a separate router and is not an
//! order-book market.

use std::collections::BTreeMap;
use std::time::{Duration, SystemTime, UNIX_EPOCH};

use ed25519_dalek::{Signer, SigningKey};
use serde_json::{json, Value};

use crate::exchange::ValidatedResponse;
use crate::http::{AsyncHttpClient, HttpMethod, HttpRequest};
use crate::{DcexError, Result};

const MAINNET_URL: &str = "https://api.arcus.xyz";
const TESTNET_URL: &str = "https://api.testnet.arcus.xyz";

#[derive(Clone)]
pub struct ArcusClient {
    transport: AsyncHttpClient,
    base_url: String,
    address: Option<String>,
    account_index: u8,
    signing_key: Option<SigningKey>,
    api_key: Option<String>,
}

impl ArcusClient {
    pub fn new(
        api_key: Option<String>,
        api_secret: Option<String>,
        address: Option<String>,
        account_index: u8,
        testnet: bool,
        timeout: Duration,
    ) -> Result<Self> {
        if account_index > 9 {
            return Err(DcexError::InvalidInput(
                "Arcus account_index must be 0–9".into(),
            ));
        }
        let signing_key = api_secret
            .as_deref()
            .map(|secret| {
                let bytes = hex::decode(secret.trim_start_matches("0x"))
                    .map_err(|_| DcexError::InvalidInput("invalid Arcus API secret hex".into()))?;
                let bytes: [u8; 32] = bytes.try_into().map_err(|_| {
                    DcexError::InvalidInput("Arcus API secret must be 32 bytes".into())
                })?;
                Ok(SigningKey::from_bytes(&bytes))
            })
            .transpose()?;
        let derived_key = signing_key
            .as_ref()
            .map(|key| hex::encode(key.verifying_key().to_bytes()));
        if let (Some(configured), Some(derived)) = (&api_key, &derived_key) {
            if !configured.eq_ignore_ascii_case(derived) {
                return Err(DcexError::InvalidInput(
                    "Arcus API key does not match signing key".into(),
                ));
            }
        }
        let api_key = derived_key.or(api_key);
        let address = address
            .map(|address| {
                let address = address.to_ascii_lowercase();
                if address.len() == 42
                    && address.starts_with("0x")
                    && address[2..].bytes().all(|byte| byte.is_ascii_hexdigit())
                {
                    Ok(address)
                } else {
                    Err(DcexError::InvalidInput(
                        "invalid Arcus wallet address".into(),
                    ))
                }
            })
            .transpose()?;
        Ok(Self {
            transport: AsyncHttpClient::new(timeout)?,
            base_url: if testnet { TESTNET_URL } else { MAINNET_URL }.into(),
            address,
            account_index,
            signing_key,
            api_key,
        })
    }

    pub fn public(timeout: Duration) -> Result<Self> {
        Self::new(None, None, None, 0, false, timeout)
    }

    pub fn with_base_url(mut self, base_url: String) -> Result<Self> {
        let url = url::Url::parse(&base_url)
            .map_err(|_| DcexError::InvalidInput("invalid Arcus base URL".into()))?;
        if !matches!(url.scheme(), "https" | "http") {
            return Err(DcexError::InvalidInput(
                "Arcus base URL must use HTTP(S)".into(),
            ));
        }
        self.base_url = base_url;
        Ok(self)
    }

    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let mut params: BTreeMap<_, _> = params.into_iter().collect();
        let path = match method_name {
            "get_markets" => "/v1/markets",
            "get_bbo" => "/v1/bbo",
            "get_l2_orderbook" => "/v1/l2OrderBook",
            "get_mid_prices" => "/v1/mids",
            "get_live_prices" => "/v1/prices",
            "get_trades" => "/v1/trades",
            "get_candles" => "/v1/candles",
            "get_account" => "/v1/account",
            "get_positions" => "/v1/positions",
            "get_open_orders" => "/v1/openOrders",
            "get_order_history" => "/v1/orders",
            "get_order_status" => "/v1/order",
            "get_fills" => "/v1/fills",
            "get_spot_positions" => "/v1/spotPositions",
            "get_spot_fills" => "/v1/spotFills",
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unknown Arcus public method: {method_name}"
                )))
            }
        };
        let path = if matches!(method_name, "get_bbo" | "get_l2_orderbook") {
            let market = required(&params, "market")?;
            if market.is_empty()
                || !market
                    .bytes()
                    .all(|byte| byte.is_ascii_alphanumeric() || byte == b'-')
            {
                return Err(DcexError::InvalidInput(
                    "Arcus market path must be a market display name".into(),
                ));
            }
            format!("{path}/{market}")
        } else if method_name == "get_order_status" {
            let order_id = required(&params, "order_id")?;
            if !order_id
                .bytes()
                .all(|byte| byte.is_ascii_alphanumeric() || byte == b'-')
            {
                return Err(DcexError::InvalidInput("invalid Arcus order ID".into()));
            }
            format!("{path}/{order_id}")
        } else {
            path.to_string()
        };
        if matches!(method_name, "get_bbo" | "get_l2_orderbook") {
            params.remove("market");
        } else if method_name == "get_order_status" {
            params.remove("order_id");
        }
        let mut request = HttpRequest::new(HttpMethod::Get, &self.base_url, path);
        request.query = params.into_iter().collect();
        if let Some(api_key) = &self.api_key {
            request = request.header("X-API-Key", api_key);
        }
        self.execute(request).await
    }

    pub async fn private_request(
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
            "place_order" => {
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
                let time_in_force = values
                    .get("time_in_force")
                    .map(String::as_str)
                    .unwrap_or("GTT")
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
                if order_type == "MARKET" && tif != 2 {
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
                let good_til_time = values
                    .get("good_til_time")
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
                canonical.insert("op", json!(1));
                canonical.insert("p", json!(price_ticks));
                canonical.insert("q", json!(quantity_quantums));
                canonical.insert("r", json!(u8::from(reduce_only)));
                canonical.insert("s", json!(side_number));
                canonical.insert("t", json!(tif));
                let mut body = json!({
                    "address": address, "accountIndex": self.account_index, "marketId": market_id,
                    "orderSide": side, "orderType": order_type, "quantity": quantity,
                    "price": price, "timeInForce": time_in_force,
                    "goodTilTime": good_til_time.to_string(), "timestamp": timestamp,
                    "reduceOnly": reduce_only,
                });
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
                ("/v1/placeOrder", body)
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

    async fn market_info(&self, product_symbol: &str) -> Result<Value> {
        let response = self.public_request("get_markets", vec![]).await?;
        response.data["markets"]
            .as_array()
            .and_then(|markets| {
                markets.iter().find(|market| {
                    let id_match = market["marketId"]
                        .as_u64()
                        .is_some_and(|id| id.to_string() == product_symbol);
                    let symbol_match = market["marketDisplayName"].as_str().is_some_and(|symbol| {
                        symbol == product_symbol || format!("{symbol}-SWAP") == product_symbol
                    });
                    id_match || symbol_match
                })
            })
            .cloned()
            .ok_or_else(|| {
                DcexError::InvalidInput(format!("unknown Arcus market: {product_symbol}"))
            })
    }

    async fn execute(&self, request: HttpRequest) -> Result<ValidatedResponse> {
        let response = self.transport.execute(request).await?;
        response.ensure_success()?;
        let data = response.json()?;
        Ok(ValidatedResponse {
            status: response.status,
            headers: response.headers,
            data,
        })
    }
}

fn required<'a>(params: &'a BTreeMap<String, String>, key: &str) -> Result<&'a str> {
    params
        .get(key)
        .map(String::as_str)
        .filter(|value| !value.is_empty())
        .ok_or_else(|| DcexError::InvalidInput(format!("Arcus {key} is required")))
}

fn timestamp_ns() -> Result<u64> {
    let elapsed = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|error| DcexError::Runtime(error.to_string()))?;
    u64::try_from(elapsed.as_nanos())
        .map_err(|_| DcexError::Runtime("Arcus timestamp overflow".into()))
}

fn decimal_parts(value: &str) -> Result<(u128, u32)> {
    let (whole, fraction) = value.split_once('.').unwrap_or((value, ""));
    if whole.is_empty()
        || !whole.bytes().all(|byte| byte.is_ascii_digit())
        || !fraction.bytes().all(|byte| byte.is_ascii_digit())
    {
        return Err(DcexError::InvalidInput(format!(
            "invalid Arcus decimal: {value}"
        )));
    }
    let digits = format!("{whole}{fraction}");
    let integer = digits
        .parse::<u128>()
        .map_err(|_| DcexError::InvalidInput("Arcus decimal is too large".into()))?;
    Ok((integer, fraction.len() as u32))
}

fn scaled(value: &str, scale: u32) -> Result<u128> {
    let (integer, places) = decimal_parts(value)?;
    if places > scale {
        let divisor = 10u128
            .checked_pow(places - scale)
            .ok_or_else(|| DcexError::InvalidInput("Arcus decimal precision overflow".into()))?;
        if integer % divisor != 0 {
            return Err(DcexError::InvalidInput(
                "Arcus decimal is not aligned".into(),
            ));
        }
        Ok(integer / divisor)
    } else {
        integer
            .checked_mul(10u128.checked_pow(scale - places).ok_or_else(|| {
                DcexError::InvalidInput("Arcus decimal precision overflow".into())
            })?)
            .ok_or_else(|| DcexError::InvalidInput("Arcus decimal overflow".into()))
    }
}

fn exact_units(value: &str, unit: &str) -> Result<u64> {
    let scale = decimal_parts(value)?.1.max(decimal_parts(unit)?.1);
    let value = scaled(value, scale)?;
    let unit = scaled(unit, scale)?;
    if unit == 0 || value == 0 || value % unit != 0 {
        return Err(DcexError::InvalidInput(
            "Arcus price/quantity is not a positive multiple of market tick/step".into(),
        ));
    }
    u64::try_from(value / unit)
        .map_err(|_| DcexError::InvalidInput("Arcus tick/quantum overflow".into()))
}

fn compare_decimals(left: &str, right: &str) -> Result<i8> {
    let scale = decimal_parts(left)?.1.max(decimal_parts(right)?.1);
    Ok(match scaled(left, scale)?.cmp(&scaled(right, scale)?) {
        std::cmp::Ordering::Less => -1,
        std::cmp::Ordering::Equal => 0,
        std::cmp::Ordering::Greater => 1,
    })
}

fn decimal_product_below(price: &str, quantity: &str, minimum: &str) -> Result<bool> {
    let (price_int, price_scale) = decimal_parts(price)?;
    let (quantity_int, quantity_scale) = decimal_parts(quantity)?;
    let product = price_int
        .checked_mul(quantity_int)
        .ok_or_else(|| DcexError::InvalidInput("Arcus notional overflow".into()))?;
    let product_scale = price_scale + quantity_scale;
    let (minimum_int, minimum_scale) = decimal_parts(minimum)?;
    let scale = product_scale.max(minimum_scale);
    let product = product
        .checked_mul(
            10u128
                .checked_pow(scale - product_scale)
                .ok_or_else(|| DcexError::InvalidInput("Arcus notional overflow".into()))?,
        )
        .ok_or_else(|| DcexError::InvalidInput("Arcus notional overflow".into()))?;
    let minimum = minimum_int
        .checked_mul(
            10u128
                .checked_pow(scale - minimum_scale)
                .ok_or_else(|| DcexError::InvalidInput("Arcus notional overflow".into()))?,
        )
        .ok_or_else(|| DcexError::InvalidInput("Arcus notional overflow".into()))?;
    Ok(product < minimum)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn decimal_to_engine_units_is_exact() {
        assert_eq!(exact_units("0.001", "0.0001").unwrap(), 10);
        assert!(exact_units("0.0015", "0.001").is_err());
        assert!(decimal_product_below("100", "0.01", "5").unwrap());
    }

    #[test]
    fn secret_must_match_public_key() {
        let secret = "00".repeat(32);
        assert!(ArcusClient::new(
            Some("ff".repeat(32)),
            Some(secret),
            None,
            0,
            true,
            Duration::from_secs(1)
        )
        .is_err());
    }
}
