//! Arcus perpetuals REST API and the separate spot RFQ router.

pub use spot::ArcusSpotClient;

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
            "get_service_info" => "/",
            "health" => "/health",
            "get_time" => "/v1/time",
            "get_markets" => "/v1/markets",
            "get_fee_tiers" => "/v1/feetiers",
            "get_commission_rates" => "/v1/commissionrates",
            "get_spot_assets" => "/v1/spotAssets",
            "get_compliance" => "/v1/compliance",
            "get_bbo" => "/v1/bbo",
            "get_l2_orderbook" => "/v1/l2OrderBook",
            "get_mid_prices" => "/v1/mids",
            "get_live_prices" => "/v1/prices",
            "get_trades" => "/v1/trades",
            "get_trade" => "/v1/trade",
            "get_candles" => "/v1/candles",
            "get_account" => "/v1/account",
            "get_account_stats" => "/v1/account/stats",
            "get_positions" => "/v1/positions",
            "get_leverages" => "/v1/leverages",
            "get_open_orders" => "/v1/openOrders",
            "get_order_history" => "/v1/orders",
            "get_order_status" => "/v1/order",
            "get_fills" => "/v1/fills",
            "get_fill" => "/v1/fill",
            "get_transfer_updates" => "/v1/accountTransferUpdates",
            "get_funding" => "/v1/funding",
            "get_interest" => "/v1/interest",
            "get_funding_rates" => "/v1/fundingRates",
            "get_portfolio_history" => "/v1/portfolio",
            "get_rate_limit" => "/v1/rateLimit",
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
            if order_id.is_empty()
                || !order_id
                    .bytes()
                    .all(|byte| byte.is_ascii_alphanumeric() || byte == b'-')
            {
                return Err(DcexError::InvalidInput("invalid Arcus order ID".into()));
            }
            format!("{path}/{order_id}")
        } else if matches!(method_name, "get_trade" | "get_fill") {
            let trade_id = required(&params, "trade_id")?;
            if trade_id.is_empty()
                || !trade_id
                    .bytes()
                    .all(|byte| byte.is_ascii_alphanumeric() || byte == b'-')
            {
                return Err(DcexError::InvalidInput("invalid Arcus trade ID".into()));
            }
            format!("{path}/{trade_id}")
        } else {
            path.to_string()
        };
        if matches!(method_name, "get_bbo" | "get_l2_orderbook") {
            params.remove("market");
        } else if method_name == "get_order_status" {
            params.remove("order_id");
        } else if matches!(method_name, "get_trade" | "get_fill") {
            params.remove("trade_id");
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
        if method_name == "submit_internal_transfer" {
            return self.submit_internal_transfer(params).await;
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

    async fn submit_internal_transfer(
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

fn legacy_signing_message(
    timestamp: u64,
    action: &str,
    body: &BTreeMap<String, Value>,
) -> Result<Vec<u8>> {
    let canonical_body =
        serde_json::to_string(body).map_err(|error| DcexError::Decode(error.to_string()))?;
    Ok(format!("{timestamp}{action}{canonical_body}").into_bytes())
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

    #[test]
    fn legacy_signing_message_sorts_json_keys() {
        let mut body = BTreeMap::new();
        body.insert("marketId".to_string(), json!(7));
        body.insert("address".to_string(), json!("0xabc"));
        body.insert("accountIndex".to_string(), json!(0));
        assert_eq!(
            legacy_signing_message(123, "cancelAllOrders", &body).unwrap(),
            br#"123cancelAllOrders{"accountIndex":0,"address":"0xabc","marketId":7}"#
        );
    }
}

mod spot {
    //! Arcus spot RFQ router. Trade signing uses an EVM wallet, not the perps API key.

    use std::collections::BTreeMap;
    use std::time::Duration;

    use serde_json::Value;

    use crate::exchange::ValidatedResponse;
    use crate::http::{AsyncHttpClient, HttpMethod, HttpRequest};
    use crate::{DcexError, Result};

    const MAINNET_URL: &str = "https://router.spot.arcus.xyz";
    const TESTNET_URL: &str = "https://router.spot.testnet.arcus.xyz";

    #[derive(Clone)]
    pub struct ArcusSpotClient {
        transport: AsyncHttpClient,
        base_url: String,
        chain_id: u64,
        api_key: Option<String>,
    }

    impl ArcusSpotClient {
        pub fn new(api_key: Option<String>, testnet: bool, timeout: Duration) -> Result<Self> {
            Ok(Self {
                transport: AsyncHttpClient::new(timeout)?,
                base_url: if testnet { TESTNET_URL } else { MAINNET_URL }.into(),
                chain_id: if testnet { 46630 } else { 4663 },
                api_key,
            })
        }

        pub fn with_base_url(mut self, base_url: String) -> Result<Self> {
            let url = url::Url::parse(&base_url)
                .map_err(|_| DcexError::InvalidInput("invalid Arcus spot router URL".into()))?;
            if !matches!(url.scheme(), "https" | "http") {
                return Err(DcexError::InvalidInput(
                    "Arcus spot router URL must use HTTP(S)".into(),
                ));
            }
            self.base_url = base_url
                .trim_end_matches('/')
                .trim_end_matches("/v1")
                .into();
            Ok(self)
        }

        pub fn chain_id(&self) -> u64 {
            self.chain_id
        }

        pub async fn public_request(
            &self,
            method_name: &str,
            params: Vec<(String, String)>,
        ) -> Result<ValidatedResponse> {
            let values: BTreeMap<_, _> = params.into_iter().collect();
            let (path, query) = match method_name {
                "health" => {
                    ensure_allowed(&values, &[])?;
                    ("/health", Vec::new())
                }
                "get_tokens" => {
                    ensure_allowed(&values, &[])?;
                    ("/v1/tokens", Vec::new())
                }
                "get_price" | "get_quote" => {
                    let allowed = if method_name == "get_quote" {
                        &[
                            "chainId",
                            "sellToken",
                            "buyToken",
                            "sellAmount",
                            "taker",
                            "slippageBps",
                            "allowWrapped",
                        ][..]
                    } else {
                        &["chainId", "sellToken", "buyToken", "sellAmount"][..]
                    };
                    ensure_allowed(&values, allowed)?;
                    let sell = required(&values, "sellToken")?;
                    let buy = required(&values, "buyToken")?;
                    validate_address(sell)?;
                    validate_address(buy)?;
                    if sell.eq_ignore_ascii_case(buy) {
                        return Err(DcexError::InvalidInput(
                            "Arcus spot sellToken and buyToken must differ".into(),
                        ));
                    }
                    validate_positive_atoms(required(&values, "sellAmount")?)?;
                    if method_name == "get_quote" {
                        validate_address(required(&values, "taker")?)?;
                        if let Some(slippage) = values.get("slippageBps") {
                            let bps = slippage.parse::<u16>().map_err(|_| {
                                DcexError::InvalidInput("invalid Arcus spot slippageBps".into())
                            })?;
                            if bps > 10_000 {
                                return Err(DcexError::InvalidInput(
                                    "Arcus spot slippageBps must be at most 10000".into(),
                                ));
                            }
                        }
                        if values
                            .get("allowWrapped")
                            .is_some_and(|v| v != "true" && v != "false")
                        {
                            return Err(DcexError::InvalidInput(
                                "Arcus spot allowWrapped must be true or false".into(),
                            ));
                        }
                    }
                    (
                        if method_name == "get_quote" {
                            "/v1/quote"
                        } else {
                            "/v1/price"
                        },
                        self.query(values)?,
                    )
                }
                "get_status" => {
                    ensure_allowed(&values, &["venue", "id", "chainId"])?;
                    if required(&values, "venue")? != "arcus" {
                        return Err(DcexError::InvalidInput(
                            "Arcus spot status venue must be arcus".into(),
                        ));
                    }
                    validate_hex(required(&values, "id")?, 32)?;
                    ("/v1/status", self.query(values)?)
                }
                _ => {
                    return Err(DcexError::InvalidInput(format!(
                        "unknown Arcus spot public method: {method_name}"
                    )))
                }
            };
            let mut request = HttpRequest::new(HttpMethod::Get, &self.base_url, path);
            request.query = query;
            self.execute(request).await
        }

        pub async fn submit_signed_quote(&self, signed_quote: Value) -> Result<ValidatedResponse> {
            let object = signed_quote.as_object().ok_or_else(|| {
                DcexError::InvalidInput("Arcus spot signed quote must be a JSON object".into())
            })?;
            if object.get("venue").and_then(Value::as_str) != Some("arcus") {
                return Err(DcexError::InvalidInput(
                    "Arcus spot signed quote venue must be arcus".into(),
                ));
            }
            if object.get("chainId").and_then(Value::as_u64) != Some(self.chain_id) {
                return Err(DcexError::InvalidInput(
                    "Arcus spot signed quote chainId does not match selected network".into(),
                ));
            }
            let taker = object.get("taker").and_then(Value::as_str).ok_or_else(|| {
                DcexError::InvalidInput("Arcus spot signed quote taker is required".into())
            })?;
            validate_address(taker)?;
            let signature = object
                .get("signature")
                .and_then(Value::as_str)
                .ok_or_else(|| {
                    DcexError::InvalidInput("Arcus spot wallet signature is required".into())
                })?;
            validate_hex(signature, 65)?;
            let typed_data = object.get("typedData").ok_or_else(|| {
                DcexError::InvalidInput("Arcus spot typedData is required".into())
            })?;
            if !typed_data.is_object()
                || typed_data["domain"]["chainId"].as_u64() != Some(self.chain_id)
                || typed_data["primaryType"].as_str() != Some("PermitWitnessTransferFrom")
            {
                return Err(DcexError::InvalidInput(
                "Arcus spot typedData must match the selected network and PermitWitnessTransferFrom"
                    .into(),
            ));
            }
            let request =
                HttpRequest::new(HttpMethod::Post, &self.base_url, "/v1/submit").json(signed_quote);
            self.execute(request).await
        }

        pub async fn private_request(
            &self,
            method_name: &str,
            params: Vec<(String, String)>,
        ) -> Result<ValidatedResponse> {
            if method_name != "submit_signed_quote" {
                return Err(DcexError::InvalidInput(format!(
                    "unknown Arcus spot private method: {method_name}"
                )));
            }
            let values: BTreeMap<_, _> = params.into_iter().collect();
            ensure_allowed(&values, &["signed_quote_json"])?;
            let signed_quote = serde_json::from_str(required(&values, "signed_quote_json")?)
                .map_err(|error| {
                    DcexError::InvalidInput(format!("invalid signed quote JSON: {error}"))
                })?;
            self.submit_signed_quote(signed_quote).await
        }

        fn query(&self, mut values: BTreeMap<String, String>) -> Result<Vec<(String, String)>> {
            if let Some(chain_id) = values.get("chainId") {
                if chain_id.parse::<u64>().ok() != Some(self.chain_id) {
                    return Err(DcexError::InvalidInput(
                        "Arcus spot chainId does not match selected network".into(),
                    ));
                }
            } else {
                values.insert("chainId".into(), self.chain_id.to_string());
            }
            Ok(values.into_iter().collect())
        }

        async fn execute(&self, mut request: HttpRequest) -> Result<ValidatedResponse> {
            if let Some(api_key) = &self.api_key {
                request = request.header("X-Api-Key", api_key);
            }
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

    fn ensure_allowed(values: &BTreeMap<String, String>, allowed: &[&str]) -> Result<()> {
        if let Some(key) = values.keys().find(|key| !allowed.contains(&key.as_str())) {
            return Err(DcexError::InvalidInput(format!(
                "unknown Arcus spot parameter: {key}"
            )));
        }
        Ok(())
    }

    fn required<'a>(values: &'a BTreeMap<String, String>, key: &str) -> Result<&'a str> {
        values
            .get(key)
            .map(String::as_str)
            .filter(|s| !s.is_empty())
            .ok_or_else(|| DcexError::InvalidInput(format!("Arcus spot {key} is required")))
    }

    fn validate_address(value: &str) -> Result<()> {
        validate_hex(value, 20)
    }

    fn validate_hex(value: &str, bytes: usize) -> Result<()> {
        if value.len() != bytes * 2 + 2
            || !value.starts_with("0x")
            || !value[2..].bytes().all(|c| c.is_ascii_hexdigit())
        {
            return Err(DcexError::InvalidInput(format!(
                "Arcus spot expected a {bytes}-byte 0x-prefixed hex value"
            )));
        }
        Ok(())
    }

    fn validate_positive_atoms(value: &str) -> Result<()> {
        if value.starts_with('0')
            || !value.bytes().all(|c| c.is_ascii_digit())
            || value.parse::<u128>().is_err()
        {
            return Err(DcexError::InvalidInput(
                "Arcus spot sellAmount must be a positive integer in token atoms".into(),
            ));
        }
        Ok(())
    }

    #[cfg(test)]
    mod tests {
        use super::*;

        #[test]
        fn validates_spot_addresses_and_atomic_amounts() {
            assert!(validate_address(&format!("0x{}", "ab".repeat(20))).is_ok());
            assert!(validate_address("BTC-USD").is_err());
            assert!(validate_positive_atoms("1000000").is_ok());
            assert!(validate_positive_atoms("0").is_err());
            assert!(validate_positive_atoms("1.5").is_err());
        }
    }
}
