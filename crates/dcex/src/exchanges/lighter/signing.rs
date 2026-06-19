use std::collections::BTreeMap;
use std::time::{SystemTime, UNIX_EPOCH};

use serde_json::Value;

use crate::lighter::{
    auth_token, private_key_from_bytes, public_key_bytes, sign_transaction_payload,
};
use crate::{DcexError, Result};

const DEFAULT_TX_EXPIRY_MS: u64 = 590_000;
const DEFAULT_ORDER_EXPIRY_MS: u64 = 28 * 24 * 60 * 60 * 1000;

pub(super) fn chain_id(base_url: &str) -> u64 {
    if base_url.contains("mainnet") || base_url.contains("api") {
        304
    } else {
        300
    }
}

pub(super) fn normalize_private_key(private_key: &str) -> Result<[u8; 40]> {
    let normalized = private_key.strip_prefix("0x").unwrap_or(private_key);
    let bytes = hex::decode(normalized).map_err(|error| {
        DcexError::InvalidInput(format!(
            "Lighter API private key must be hexadecimal: {error}"
        ))
    })?;
    if bytes.len() != 40 {
        return Err(DcexError::InvalidInput(
            "Lighter API private key must contain exactly 40 bytes.".to_string(),
        ));
    }
    private_key_from_bytes(&bytes)?;
    let mut result = [0u8; 40];
    result.copy_from_slice(&bytes);
    Ok(result)
}

pub(super) fn private_key_for(
    keys: &BTreeMap<u64, [u8; 40]>,
    api_key_index: u64,
) -> Result<&[u8; 40]> {
    if api_key_index == 255 {
        if keys.len() != 1 {
            return Err(DcexError::InvalidInput(
                "Lighter API key index is ambiguous.".to_string(),
            ));
        }
        return keys.values().next().ok_or_else(|| {
            DcexError::InvalidInput("missing Lighter API private key.".to_string())
        });
    }
    keys.get(&api_key_index).ok_or_else(|| {
        DcexError::InvalidInput(format!(
            "Lighter API key index {api_key_index} is not configured."
        ))
    })
}

pub(super) fn public_key_hex(private_key: &[u8; 40]) -> Result<String> {
    let scalar = private_key_from_bytes(private_key)?;
    Ok(hex::encode(public_key_bytes(&scalar)?))
}

pub(super) fn create_auth_token(
    account_index: u64,
    api_key_index: u64,
    private_key: &[u8; 40],
    deadline: Option<u64>,
) -> Result<String> {
    let deadline = deadline.unwrap_or(600);
    let timestamp = unix_timestamp_secs()?;
    let expiry = deadline + timestamp;
    auth_token(
        expiry,
        account_index,
        api_key_index,
        private_key,
        &random_scalar_bytes()?,
    )
}

pub(super) fn expiry_ms() -> Result<u64> {
    Ok(unix_timestamp_ms()? + DEFAULT_TX_EXPIRY_MS)
}

pub(super) fn order_expiry_ms() -> Result<u64> {
    Ok(unix_timestamp_ms()? + DEFAULT_ORDER_EXPIRY_MS)
}

pub(super) fn attributes(
    integrator_account_index: u64,
    integrator_taker_fee: u64,
    integrator_maker_fee: u64,
    skip_nonce: u64,
    cancel_all_market_index: u64,
) -> Vec<(u64, u64)> {
    let mut result = Vec::new();
    if integrator_account_index != 0 {
        result.push((1, integrator_account_index));
    }
    if integrator_taker_fee != 0 {
        result.push((2, integrator_taker_fee));
    }
    if integrator_maker_fee != 0 {
        result.push((3, integrator_maker_fee));
    }
    if skip_nonce == 1 {
        result.push((4, 1));
    }
    if cancel_all_market_index != 255 {
        result.push((5, cancel_all_market_index));
    }
    result
}

pub(super) fn sign_payload(
    tx_type: u64,
    values: Vec<i128>,
    payload: Value,
    attributes: Vec<(u64, u64)>,
    private_key: &[u8; 40],
) -> Result<(u64, String, String)> {
    let payload_json =
        serde_json::to_vec(&payload).map_err(|error| DcexError::Decode(error.to_string()))?;
    let (tx_info, tx_hash) = sign_transaction_payload(
        &values,
        &attributes,
        &payload_json,
        private_key,
        &random_scalar_bytes()?,
    )?;
    let tx_info =
        String::from_utf8(tx_info).map_err(|error| DcexError::Decode(error.to_string()))?;
    Ok((tx_type, tx_info, hex::encode(tx_hash)))
}

pub(super) fn encode_params(params: &[(String, String)]) -> String {
    url::form_urlencoded::Serializer::new(String::new())
        .extend_pairs(
            params
                .iter()
                .map(|(key, value)| (key.as_str(), value.as_str())),
        )
        .finish()
}

pub(super) const fn http_method_name(method: crate::http::HttpMethod) -> &'static str {
    match method {
        crate::http::HttpMethod::Delete => "DELETE",
        crate::http::HttpMethod::Get => "GET",
        crate::http::HttpMethod::Patch => "PATCH",
        crate::http::HttpMethod::Post => "POST",
        crate::http::HttpMethod::Put => "PUT",
    }
}

pub(super) fn json_value_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.clone(),
        _ => value.to_string(),
    }
}

fn random_scalar_bytes() -> Result<[u8; 40]> {
    for _ in 0..8 {
        let mut bytes = [0u8; 40];
        getrandom::getrandom(&mut bytes).map_err(|error| DcexError::Runtime(error.to_string()))?;
        if crate::lighter::scalar_from_bytes(&bytes, "Lighter nonce scalar").is_ok() {
            return Ok(bytes);
        }
    }
    Err(DcexError::Runtime(
        "failed to generate a valid Lighter nonce scalar".to_string(),
    ))
}

fn unix_timestamp_ms() -> Result<u64> {
    let duration = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|error| DcexError::Runtime(error.to_string()))?;
    u64::try_from(duration.as_millis()).map_err(|error| DcexError::Runtime(error.to_string()))
}

fn unix_timestamp_secs() -> Result<u64> {
    let duration = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map_err(|error| DcexError::Runtime(error.to_string()))?;
    Ok(duration.as_secs())
}
