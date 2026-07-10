use std::collections::BTreeMap;
use std::time::{SystemTime, UNIX_EPOCH};

use num_bigint::BigInt;
use num_traits::{One, Signed, ToPrimitive, Zero};
use serde::Deserialize;
use serde_json::{json, Map, Value};
use starknet_crypto::{rfc6979_generate_k, sign, Felt, PoseidonHasher, SignError};

use crate::{DcexError, Result};

use super::params::ExtendedParams;

const DOMAIN_SELECTOR: &str = "0x1ff2f602e42168014d405a94f75e8a93d640751d71d16311266e140d8b0a210";
const ORDER_SELECTOR: &str = "0x36da8d51815527cabfaa9c982f564c80fa7429616739306036f1f9b608dd112";
const SETTLEMENT_EXPIRATION_BUFFER_SECONDS: u64 = 14 * 24 * 60 * 60;
const DEFAULT_ORDER_LIFETIME_MS: u64 = 60 * 60 * 1000;
const DEFAULT_TAKER_FEE: &str = "0.0005";

#[derive(Clone)]
pub struct ExtendedSigningCredentials {
    pub stark_private_key: String,
    pub stark_public_key: String,
    pub vault_number: u32,
}

impl ExtendedSigningCredentials {
    pub fn new(
        stark_private_key: String,
        stark_public_key: String,
        vault_number: u32,
        _client_id: Option<String>,
    ) -> Self {
        Self {
            stark_private_key,
            stark_public_key,
            vault_number,
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
enum OrderSide {
    Buy,
    Sell,
}

impl OrderSide {
    fn parse(value: &str) -> Result<Self> {
        match value.to_ascii_uppercase().as_str() {
            "BUY" => Ok(Self::Buy),
            "SELL" => Ok(Self::Sell),
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported Extended order side: {value}"
            ))),
        }
    }

    const fn as_str(self) -> &'static str {
        match self {
            Self::Buy => "BUY",
            Self::Sell => "SELL",
        }
    }
}

#[derive(Clone, Copy)]
enum DecimalRounding {
    Up,
    Down,
}

#[derive(Clone, Debug, PartialEq, Eq)]
struct ExactDecimal {
    numerator: BigInt,
    scale: u32,
}

impl ExactDecimal {
    fn parse(value: &str, field: &str) -> Result<Self> {
        let trimmed = value.trim();
        if trimmed.is_empty() {
            return Err(DcexError::InvalidInput(format!("{field} cannot be empty")));
        }

        let (mantissa, exponent) = split_decimal_exponent(trimmed, field)?;
        let negative = mantissa.starts_with('-');
        let mantissa = mantissa
            .strip_prefix('+')
            .or_else(|| mantissa.strip_prefix('-'))
            .unwrap_or(mantissa)
            .trim();
        if mantissa.is_empty() {
            return Err(DcexError::InvalidInput(format!("invalid {field}: {value}")));
        }

        let mut split = mantissa.split('.');
        let whole = split.next().unwrap_or_default();
        let fractional = split.next().unwrap_or_default();
        if split.next().is_some()
            || (!whole.chars().all(|ch| ch.is_ascii_digit()))
            || (!fractional.chars().all(|ch| ch.is_ascii_digit()))
            || (whole.is_empty() && fractional.is_empty())
        {
            return Err(DcexError::InvalidInput(format!("invalid {field}: {value}")));
        }

        let mut digits = format!("{whole}{fractional}");
        while digits.len() > 1 && digits.starts_with('0') {
            digits.remove(0);
        }
        if digits.is_empty() {
            digits.push('0');
        }

        let mut numerator = BigInt::parse_bytes(digits.as_bytes(), 10)
            .ok_or_else(|| DcexError::InvalidInput(format!("invalid {field}: {value}")))?;
        if negative {
            numerator = -numerator;
        }

        let mut scale = i64::try_from(fractional.len())
            .map_err(|error| DcexError::InvalidInput(error.to_string()))?
            - i64::from(exponent);
        if scale < 0 {
            numerator *= pow10((-scale) as u32);
            scale = 0;
        }

        Ok(Self {
            numerator,
            scale: u32::try_from(scale)
                .map_err(|error| DcexError::InvalidInput(error.to_string()))?,
        })
    }

    fn is_positive(&self) -> bool {
        self.numerator > BigInt::zero()
    }

    fn is_negative(&self) -> bool {
        self.numerator < BigInt::zero()
    }

    fn add(&self, other: &Self) -> Self {
        let scale = self.scale.max(other.scale);
        let left = &self.numerator * pow10(scale - self.scale);
        let right = &other.numerator * pow10(scale - other.scale);
        Self {
            numerator: left + right,
            scale,
        }
    }

    fn mul(&self, other: &Self) -> Self {
        Self {
            numerator: &self.numerator * &other.numerator,
            scale: self.scale + other.scale,
        }
    }

    fn to_plain_string(&self) -> String {
        let negative = self.numerator.sign() == num_bigint::Sign::Minus;
        let mut digits = self.numerator.abs().to_string();
        if self.scale == 0 {
            return if negative {
                format!("-{digits}")
            } else {
                digits
            };
        }

        let scale = self.scale as usize;
        if digits.len() <= scale {
            digits = format!("{}{}", "0".repeat(scale - digits.len() + 1), digits);
        }
        let split_at = digits.len() - scale;
        let (whole, fractional) = digits.split_at(split_at);
        let fractional = fractional.trim_end_matches('0');
        let value = if fractional.is_empty() {
            whole.to_string()
        } else {
            format!("{whole}.{fractional}")
        };
        if negative && value != "0" {
            format!("-{value}")
        } else {
            value
        }
    }

    fn to_stark_amount(&self, resolution: u64, rounding: DecimalRounding) -> Result<i64> {
        let amount = self.to_scaled_integer(resolution, rounding)?;
        amount.to_i64().ok_or_else(|| {
            DcexError::InvalidInput("Extended stark amount exceeds i64 range".to_string())
        })
    }

    fn to_stark_fee(&self, resolution: u64) -> Result<u64> {
        let amount = self.to_scaled_integer(resolution, DecimalRounding::Up)?;
        amount.to_u64().ok_or_else(|| {
            DcexError::InvalidInput("Extended fee amount must be non-negative u64".to_string())
        })
    }

    fn to_scaled_integer(&self, resolution: u64, rounding: DecimalRounding) -> Result<BigInt> {
        let numerator = &self.numerator * BigInt::from(resolution);
        let denominator = pow10(self.scale);
        if denominator.is_zero() {
            return Err(DcexError::InvalidInput(
                "invalid decimal denominator".to_string(),
            ));
        }
        let quotient = &numerator / &denominator;
        let remainder = &numerator % &denominator;
        if remainder.is_zero() {
            return Ok(quotient);
        }
        match rounding {
            DecimalRounding::Down => Ok(quotient),
            DecimalRounding::Up => {
                if numerator.sign() == num_bigint::Sign::Minus {
                    Ok(quotient - BigInt::one())
                } else {
                    Ok(quotient + BigInt::one())
                }
            }
        }
    }
}

fn split_decimal_exponent<'a>(value: &'a str, field: &str) -> Result<(&'a str, i32)> {
    let Some(index) = value.find('e').or_else(|| value.find('E')) else {
        return Ok((value, 0));
    };
    let (mantissa, exponent) = value.split_at(index);
    let exponent = &exponent[1..];
    let exponent = exponent
        .parse::<i32>()
        .map_err(|error| DcexError::InvalidInput(format!("invalid {field} exponent: {error}")))?;
    Ok((mantissa, exponent))
}

fn pow10(exp: u32) -> BigInt {
    let mut value = BigInt::one();
    for _ in 0..exp {
        value *= 10u8;
    }
    value
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(super) struct ExtendedMarket {
    name: String,
    l2_config: ExtendedL2Config,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
struct ExtendedL2Config {
    collateral_id: String,
    collateral_resolution: u64,
    synthetic_id: String,
    synthetic_resolution: u64,
}

#[derive(Clone, Debug)]
pub(super) struct ExtendedSignedOrder {
    pub body: Value,
    pub order_hash: Felt,
}

pub(super) fn build_signed_order(
    params: &ExtendedParams,
    market: ExtendedMarket,
    credentials: &ExtendedSigningCredentials,
) -> Result<ExtendedSignedOrder> {
    let spec = ExtendedOrderSpec::from_params(params, market.name)?;
    spec.validate()?;

    let private_key = parse_felt_hex(&credentials.stark_private_key, "stark_private_key")?;
    let public_key = parse_felt_hex(&credentials.stark_public_key, "stark_public_key")?;
    let base_asset_id = parse_felt_hex(&market.l2_config.synthetic_id, "synthetic asset id")?;
    let quote_asset_id = parse_felt_hex(&market.l2_config.collateral_id, "collateral asset id")?;
    let fee_asset_id = quote_asset_id;

    let collateral_amount = spec.synthetic_amount.mul(&spec.price);
    let builder_fee = spec.builder_fee.clone().unwrap_or_else(ExactDecimal::zero);
    let total_fee = spec.taker_fee.add(&builder_fee);
    let fee_amount = total_fee.mul(&collateral_amount);

    let rounding = match spec.side {
        OrderSide::Buy => DecimalRounding::Up,
        OrderSide::Sell => DecimalRounding::Down,
    };
    let mut stark_synthetic_amount = spec
        .synthetic_amount
        .to_stark_amount(market.l2_config.synthetic_resolution, rounding)?;
    let mut stark_collateral_amount =
        collateral_amount.to_stark_amount(market.l2_config.collateral_resolution, rounding)?;
    let stark_fee_amount = fee_amount.to_stark_fee(market.l2_config.collateral_resolution)?;

    match spec.side {
        OrderSide::Buy => stark_collateral_amount = -stark_collateral_amount,
        OrderSide::Sell => stark_synthetic_amount = -stark_synthetic_amount,
    }

    let settlement_expiration = settlement_expiration_seconds(spec.expiry_epoch_millis);
    let order_hash = order_message_hash(OrderHashInput {
        position_id: credentials.vault_number,
        base_asset_id,
        base_amount: stark_synthetic_amount,
        quote_asset_id,
        quote_amount: stark_collateral_amount,
        fee_asset_id,
        fee_amount: stark_fee_amount,
        expiration: settlement_expiration,
        salt: spec.nonce,
        user_public_key: public_key,
        domain: StarknetDomain::mainnet(),
    })?;
    let signature = sign_message(&private_key, &order_hash)?;

    let mut body = Map::new();
    body.insert(
        "id".to_string(),
        Value::String(spec.external_id.unwrap_or_else(|| order_hash.to_string())),
    );
    body.insert("market".to_string(), Value::String(spec.market));
    body.insert("type".to_string(), Value::String(spec.order_type));
    body.insert(
        "side".to_string(),
        Value::String(spec.side.as_str().to_string()),
    );
    body.insert(
        "qty".to_string(),
        Value::String(spec.synthetic_amount.to_plain_string()),
    );
    body.insert(
        "price".to_string(),
        Value::String(spec.price.to_plain_string()),
    );
    body.insert("reduceOnly".to_string(), Value::Bool(spec.reduce_only));
    body.insert("postOnly".to_string(), Value::Bool(spec.post_only));
    body.insert(
        "timeInForce".to_string(),
        Value::String(spec.time_in_force.to_string()),
    );
    body.insert(
        "expiryEpochMillis".to_string(),
        Value::Number(serde_json::Number::from(spec.expiry_epoch_millis)),
    );
    body.insert(
        "fee".to_string(),
        Value::String(spec.taker_fee.to_plain_string()),
    );
    body.insert("nonce".to_string(), Value::String(spec.nonce.to_string()));
    body.insert(
        "selfTradeProtectionLevel".to_string(),
        Value::String(spec.self_trade_protection_level),
    );
    body.insert(
        "settlement".to_string(),
        json!({
            "signature": {
                "r": signature.r.to_hex_string(),
                "s": signature.s.to_hex_string(),
            },
            "starkKey": public_key.to_hex_string(),
            "collateralPosition": credentials.vault_number.to_string(),
        }),
    );
    body.insert(
        "debuggingAmounts".to_string(),
        json!({
            "collateralAmount": stark_collateral_amount.to_string(),
            "feeAmount": stark_fee_amount.to_string(),
            "syntheticAmount": stark_synthetic_amount.to_string(),
        }),
    );
    if let Some(builder_fee) = spec.builder_fee {
        body.insert(
            "builderFee".to_string(),
            Value::String(builder_fee.to_plain_string()),
        );
    }
    if let Some(builder_id) = spec.builder_id {
        body.insert(
            "builderId".to_string(),
            Value::Number(serde_json::Number::from(builder_id)),
        );
    }
    Ok(ExtendedSignedOrder {
        body: Value::Object(body),
        order_hash,
    })
}

impl ExactDecimal {
    fn zero() -> Self {
        Self {
            numerator: BigInt::zero(),
            scale: 0,
        }
    }
}

struct ExtendedOrderSpec {
    market: String,
    order_type: String,
    side: OrderSide,
    synthetic_amount: ExactDecimal,
    price: ExactDecimal,
    post_only: bool,
    time_in_force: String,
    expiry_epoch_millis: u64,
    taker_fee: ExactDecimal,
    self_trade_protection_level: String,
    nonce: u64,
    external_id: Option<String>,
    builder_fee: Option<ExactDecimal>,
    builder_id: Option<u64>,
    reduce_only: bool,
}

impl ExtendedOrderSpec {
    fn from_params(params: &ExtendedParams, market: String) -> Result<Self> {
        let order_type = params
            .first(&["type", "order_type", "orderType"])
            .unwrap_or("LIMIT")
            .to_ascii_uppercase();
        let side = OrderSide::parse(params.first_required(&["side"])?)?;
        let qty = params.first_required(&["qty", "quantity", "amount", "amount_of_synthetic"])?;
        let price = params.first_required(&["price"])?;
        let taker_fee = params
            .first(&["fee", "taker_fee", "takerFee"])
            .unwrap_or(DEFAULT_TAKER_FEE);
        let builder_fee = params
            .first(&["builder_fee", "builderFee"])
            .map(|value| ExactDecimal::parse(value, "builder_fee"))
            .transpose()?;
        let builder_id = params
            .first(&["builder_id", "builderId"])
            .map(|value| parse_u64(value, "builder_id"))
            .transpose()?;
        Ok(Self {
            market,
            order_type,
            side,
            synthetic_amount: ExactDecimal::parse(qty, "qty")?,
            price: ExactDecimal::parse(price, "price")?,
            post_only: parse_bool(params.first(&["post_only", "postOnly"]).unwrap_or("false"))?,
            time_in_force: params
                .first(&["time_in_force", "timeInForce"])
                .unwrap_or("GTT")
                .to_ascii_uppercase(),
            expiry_epoch_millis: params
                .first(&["expiry_epoch_millis", "expiryEpochMillis", "expire_time_ms"])
                .map(|value| parse_u64(value, "expiry_epoch_millis"))
                .transpose()?
                .unwrap_or(now_ms()? + DEFAULT_ORDER_LIFETIME_MS),
            taker_fee: ExactDecimal::parse(taker_fee, "fee")?,
            self_trade_protection_level: params
                .first(&["self_trade_protection_level", "selfTradeProtectionLevel"])
                .unwrap_or("ACCOUNT")
                .to_ascii_uppercase(),
            nonce: params
                .first(&["nonce"])
                .map(|value| parse_u64(value, "nonce"))
                .transpose()?
                .unwrap_or(random_nonce()?),
            external_id: params
                .first(&["id", "external_id", "externalId", "order_external_id"])
                .map(ToString::to_string),
            builder_fee,
            builder_id,
            reduce_only: parse_bool(
                params
                    .first(&["reduce_only", "reduceOnly"])
                    .unwrap_or("false"),
            )?,
        })
    }

    fn validate(&self) -> Result<()> {
        if self.order_type != "LIMIT" {
            return Err(DcexError::InvalidInput(
                "Extended automatic order signing currently supports LIMIT orders only".to_string(),
            ));
        }
        if !self.synthetic_amount.is_positive() {
            return Err(DcexError::InvalidInput(
                "Extended qty must be positive".to_string(),
            ));
        }
        if self.price.is_negative() {
            return Err(DcexError::InvalidInput(
                "Extended price must be non-negative".to_string(),
            ));
        }
        if self.taker_fee.is_negative() {
            return Err(DcexError::InvalidInput(
                "Extended fee must be non-negative".to_string(),
            ));
        }
        if !matches!(self.time_in_force.as_str(), "GTT" | "IOC" | "FOK") {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Extended time_in_force: {}",
                self.time_in_force
            )));
        }
        if !matches!(
            self.self_trade_protection_level.as_str(),
            "DISABLED" | "ACCOUNT" | "CLIENT"
        ) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Extended self_trade_protection_level: {}",
                self.self_trade_protection_level
            )));
        }
        Ok(())
    }
}

fn now_ms() -> Result<u64> {
    let duration = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|error| DcexError::Runtime(error.to_string()))?;
    u64::try_from(duration.as_millis()).map_err(|error| DcexError::Runtime(error.to_string()))
}

fn random_nonce() -> Result<u64> {
    let mut bytes = [0u8; 4];
    getrandom::getrandom(&mut bytes).map_err(|error| DcexError::Runtime(error.to_string()))?;
    Ok(u32::from_be_bytes(bytes).into())
}

fn parse_bool(value: &str) -> Result<bool> {
    match value.to_ascii_lowercase().as_str() {
        "true" | "1" | "yes" => Ok(true),
        "false" | "0" | "no" => Ok(false),
        _ => Err(DcexError::InvalidInput(format!(
            "invalid boolean value: {value}"
        ))),
    }
}

fn parse_u64(value: &str, field: &str) -> Result<u64> {
    value
        .parse::<u64>()
        .map_err(|error| DcexError::InvalidInput(format!("invalid {field}: {error}")))
}

fn parse_felt_hex(value: &str, field: &str) -> Result<Felt> {
    Felt::from_hex(value)
        .map_err(|error| DcexError::InvalidInput(format!("invalid {field}: {error}")))
}

fn felt_short_string(value: &str) -> Result<Felt> {
    if !value.is_ascii() || value.len() > 31 {
        return Err(DcexError::InvalidInput(format!(
            "invalid Starknet short string: {value}"
        )));
    }
    let mut bytes = [0u8; 32];
    bytes[32 - value.len()..].copy_from_slice(value.as_bytes());
    Ok(Felt::from_bytes_be(&bytes))
}

#[derive(Clone, Copy)]
struct StarknetDomain {
    name: &'static str,
    version: &'static str,
    chain_id: &'static str,
    revision: u32,
}

impl StarknetDomain {
    const fn mainnet() -> Self {
        Self {
            name: "Perpetuals",
            version: "v0",
            chain_id: "SN_MAIN",
            revision: 1,
        }
    }

    #[cfg(test)]
    const fn sepolia() -> Self {
        Self {
            name: "Perpetuals",
            version: "v0",
            chain_id: "SN_SEPOLIA",
            revision: 1,
        }
    }

    fn hash(self) -> Result<Felt> {
        let mut hasher = PoseidonHasher::new();
        hasher.update(parse_felt_hex(DOMAIN_SELECTOR, "domain selector")?);
        hasher.update(felt_short_string(self.name)?);
        hasher.update(felt_short_string(self.version)?);
        hasher.update(felt_short_string(self.chain_id)?);
        hasher.update(Felt::from(self.revision));
        Ok(hasher.finalize())
    }
}

struct OrderHashInput {
    position_id: u32,
    base_asset_id: Felt,
    base_amount: i64,
    quote_asset_id: Felt,
    quote_amount: i64,
    fee_asset_id: Felt,
    fee_amount: u64,
    expiration: u64,
    salt: u64,
    user_public_key: Felt,
    domain: StarknetDomain,
}

fn order_message_hash(input: OrderHashInput) -> Result<Felt> {
    let mut order_hasher = PoseidonHasher::new();
    order_hasher.update(parse_felt_hex(ORDER_SELECTOR, "order selector")?);
    order_hasher.update(Felt::from(input.position_id));
    order_hasher.update(input.base_asset_id);
    order_hasher.update(Felt::from(input.base_amount));
    order_hasher.update(input.quote_asset_id);
    order_hasher.update(Felt::from(input.quote_amount));
    order_hasher.update(input.fee_asset_id);
    order_hasher.update(Felt::from(input.fee_amount));
    order_hasher.update(Felt::from(input.expiration));
    order_hasher.update(Felt::from(input.salt));
    let order_hash = order_hasher.finalize();

    let mut message_hasher = PoseidonHasher::new();
    message_hasher.update(felt_short_string("StarkNet Message")?);
    message_hasher.update(input.domain.hash()?);
    message_hasher.update(input.user_public_key);
    message_hasher.update(order_hash);
    Ok(message_hasher.finalize())
}

struct StarkSignature {
    r: Felt,
    s: Felt,
}

fn sign_message(private_key: &Felt, message_hash: &Felt) -> Result<StarkSignature> {
    let mut seed = None;
    loop {
        let k = rfc6979_generate_k(message_hash, private_key, seed.as_ref());
        match sign(private_key, message_hash, &k) {
            Ok(signature) => {
                return Ok(StarkSignature {
                    r: signature.r,
                    s: signature.s,
                })
            }
            Err(SignError::InvalidMessageHash) => {
                return Err(DcexError::InvalidInput(
                    "Extended message hash is outside the Stark signing range".to_string(),
                ))
            }
            Err(SignError::InvalidK) => {
                seed = Some(seed.map_or(Felt::ONE, |previous| previous + Felt::ONE));
            }
        }
    }
}

fn settlement_expiration_seconds(expiry_epoch_millis: u64) -> u64 {
    expiry_epoch_millis.div_ceil(1000) + SETTLEMENT_EXPIRATION_BUFFER_SECONDS
}

pub(super) fn extract_market_from_response(
    data: &Value,
    market_name: &str,
) -> Result<ExtendedMarket> {
    let markets = data
        .get("data")
        .and_then(Value::as_array)
        .or_else(|| data.as_array())
        .ok_or_else(|| {
            DcexError::Decode("Extended markets response did not contain a data array".to_string())
        })?;
    let market = markets
        .iter()
        .find(|market| market.get("name").and_then(Value::as_str) == Some(market_name))
        .or_else(|| markets.first())
        .ok_or_else(|| {
            DcexError::InvalidInput(format!("Extended market not found: {market_name}"))
        })?;
    serde_json::from_value(market.clone())
        .map_err(|error| DcexError::Decode(format!("invalid Extended market schema: {error}")))
}

pub(super) fn extract_market_from_param(
    params: &ExtendedParams,
    market_name: &str,
) -> Result<Option<ExtendedMarket>> {
    let Some(market_json) = params.first(&["market_json", "marketJson"]) else {
        return Ok(None);
    };
    let value = serde_json::from_str::<Value>(market_json)
        .map_err(|error| DcexError::InvalidInput(format!("invalid market_json: {error}")))?;
    if value.get("data").is_some() || value.as_array().is_some() {
        return extract_market_from_response(&value, market_name).map(Some);
    }
    serde_json::from_value(value)
        .map(Some)
        .map_err(|error| DcexError::InvalidInput(format!("invalid market_json: {error}")))
}

pub(super) fn signed_order_response(
    body: Value,
    order_hash: Felt,
) -> crate::exchange::ValidatedResponse {
    let mut data = BTreeMap::new();
    data.insert("order".to_string(), body);
    data.insert(
        "orderHash".to_string(),
        Value::String(order_hash.to_hex_string()),
    );
    crate::exchange::ValidatedResponse {
        status: 200,
        headers: BTreeMap::new(),
        data: Value::Object(data.into_iter().collect()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn order_hash_matches_official_extended_wrapper_vector() {
        let hash = order_message_hash(OrderHashInput {
            position_id: 100,
            base_asset_id: Felt::from_hex("0x2").unwrap(),
            base_amount: 100,
            quote_asset_id: Felt::from_hex("0x1").unwrap(),
            quote_amount: -156,
            fee_asset_id: Felt::from_hex("0x1").unwrap(),
            fee_amount: 74,
            expiration: 100,
            salt: 123,
            user_public_key: Felt::from_hex(
                "0x5d05989e9302dcebc74e241001e3e3ac3f4402ccf2f8e6f74b034b07ad6a904",
            )
            .unwrap(),
            domain: StarknetDomain::sepolia(),
        })
        .unwrap();
        assert_eq!(
            hash.to_hex_string(),
            "0x4de4c009e0d0c5a70a7da0e2039fb2b99f376d53496f89d9f437e736add6b48"
        );
    }

    #[test]
    fn signing_matches_official_fast_stark_crypto_vector() {
        let private_key = Felt::from_hex("0x1").unwrap();
        let message_hash =
            Felt::from_hex("0x601f8326b07c24fe84e95c907716fb28d44cae361ba1dd929d82194e35cda92")
                .unwrap();
        let signature = sign_message(&private_key, &message_hash).unwrap();
        assert_eq!(
            signature.r.to_string(),
            "54861078609021383253612575671190510658994141728029508858322475140179578468"
        );
        assert_eq!(
            signature.s.to_string(),
            "3076762545522358157564775888110062390454599173866418717941719399328521581938"
        );
    }

    #[test]
    fn signed_order_body_uses_official_json_shape() {
        let market = ExtendedMarket {
            name: "BTC-USD".to_string(),
            l2_config: ExtendedL2Config {
                collateral_id: "0x555344430000000000000000000000".to_string(),
                collateral_resolution: 1_000_000,
                synthetic_id: "0x4254432d31300000000000000000000".to_string(),
                synthetic_resolution: 100_000_000,
            },
        };
        let params = ExtendedParams::from_pairs(vec![
            ("side".to_string(), "BUY".to_string()),
            ("qty".to_string(), "0.001".to_string()),
            ("price".to_string(), "10000".to_string()),
            ("post_only".to_string(), "true".to_string()),
            (
                "expiry_epoch_millis".to_string(),
                "1800000000000".to_string(),
            ),
            ("nonce".to_string(), "123456".to_string()),
        ]);
        let order = build_signed_order(
            &params,
            market,
            &ExtendedSigningCredentials::new(
                "0x1".to_string(),
                "0x1ef15c18599971b7beced415a40f0c7deacfd9b0d1819e03d723d8bc943cfca".to_string(),
                391345,
                None,
            ),
        )
        .unwrap();
        assert_eq!(order.body["market"], "BTC-USD");
        assert_eq!(order.body["type"], "LIMIT");
        assert_eq!(order.body["side"], "BUY");
        assert_eq!(order.body["qty"], "0.001");
        assert_eq!(order.body["price"], "10000");
        assert_eq!(order.body["postOnly"], true);
        assert_eq!(order.body["timeInForce"], "GTT");
        assert_eq!(order.body["settlement"]["collateralPosition"], "391345");
        assert!(order.body["settlement"]["signature"]["r"]
            .as_str()
            .unwrap()
            .starts_with("0x"));
    }
}
