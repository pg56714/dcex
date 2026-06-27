use std::collections::HashMap;
use std::future::{Future, IntoFuture};
use std::sync::OnceLock;
use std::time::{SystemTime, UNIX_EPOCH};

use dcex::exchange::{Exchange, ValidatedResponse};
use dcex::product_table::{ProductTable, TradingDetails};
use dcex::{DcexError, Result};
use serde_json::Value;
use tokio::time::{sleep, Duration};

pub(crate) const BTC_USDT_SPOT: &str = "BTC-USDT-SPOT";
pub(crate) const BTC_USDT_SWAP: &str = "BTC-USDT-SWAP";
pub(crate) const BTC_USD_SWAP: &str = "BTC-USD-SWAP";
pub(crate) const DOGE_USDT_SPOT: &str = "DOGE-USDT-SPOT";
pub(crate) const DOGE_USDT_SWAP: &str = "DOGE-USDT-SWAP";
pub(crate) const XBT_USDT_SWAP: &str = "XBT-USDT-SWAP";

pub(crate) type Params = Vec<(String, String)>;

pub(crate) fn params(values: &[(&str, &str)]) -> Params {
    values
        .iter()
        .map(|(key, value)| ((*key).to_string(), (*value).to_string()))
        .collect()
}

pub(crate) fn push(params: &mut Params, key: &str, value: impl Into<String>) {
    params.push((key.to_string(), value.into()));
}

pub(crate) async fn exchange_method_request<C>(
    client: &C,
    method_name: &'static str,
    params: Params,
) -> Result<ValidatedResponse>
where
    C: dcex::exchanges::ExchangeMethodRequestClient + Sync,
{
    match client
        .public_request_boxed(method_name, params.clone())
        .await
    {
        Ok(response) => Ok(response),
        Err(DcexError::InvalidInput(message)) if message.contains("unsupported") => {
            client.private_request_boxed(method_name, params).await
        }
        Err(error) => Err(error),
    }
}

pub(crate) fn live_trading_enabled() -> bool {
    env_value("RUN_LIVE_TRADING_TESTS").as_deref() == Some("1")
}

pub(crate) fn require_live_trading() -> bool {
    if live_trading_enabled() {
        true
    } else {
        eprintln!("skipping live stateful trading test; set RUN_LIVE_TRADING_TESTS=1");
        false
    }
}

pub(crate) fn require_env(names: &[&str]) -> Option<Vec<String>> {
    let mut values = Vec::with_capacity(names.len());
    let mut missing = Vec::new();
    for name in names {
        match env_value(name) {
            Some(value) => values.push(value),
            None => missing.push(*name),
        }
    }
    if missing.is_empty() {
        Some(values)
    } else {
        eprintln!(
            "skipping live stateful trading test; missing {}",
            missing.join(", ")
        );
        None
    }
}

pub(crate) fn unique_client_id(prefix: &str) -> String {
    format!("{prefix}{}", now_ms())
}

pub(crate) fn assert_success(response: &ValidatedResponse) {
    assert!((200..300).contains(&response.status), "{response:?}");
    assert!(!response.data.is_null(), "{response:?}");
}

pub(crate) fn require_order_id(data: &Value, keys: &[&str]) -> Result<String> {
    find_string(data, keys).ok_or_else(|| {
        DcexError::Decode(format!(
            "order response did not contain any of these ids {keys:?}: {data}"
        ))
    })
}

pub(crate) fn find_string(data: &Value, keys: &[&str]) -> Option<String> {
    match data {
        Value::Object(object) => {
            for key in keys {
                if let Some(value) = object.get(*key).and_then(first_scalar_string) {
                    return Some(value);
                }
            }
            object.values().find_map(|value| find_string(value, keys))
        }
        Value::Array(values) => values.iter().find_map(|value| find_string(value, keys)),
        _ => None,
    }
}

pub(crate) fn find_f64(data: &Value, keys: &[&str]) -> Option<f64> {
    match data {
        Value::Object(object) => {
            for key in keys {
                if let Some(value) = object.get(*key).and_then(value_as_f64) {
                    return Some(value);
                }
            }
            object.values().find_map(|value| find_f64(value, keys))
        }
        Value::Array(values) => values.iter().find_map(|value| find_f64(value, keys)),
        _ => None,
    }
}

pub(crate) fn asset_amount(data: &Value, asset: &str, amount_keys: &[&str]) -> f64 {
    match data {
        Value::Object(object) => {
            let matches_asset = object
                .get("asset")
                .or_else(|| object.get("ccy"))
                .or_else(|| object.get("coin"))
                .or_else(|| object.get("currency"))
                .or_else(|| object.get("marginCoin"))
                .and_then(Value::as_str)
                == Some(asset);
            if matches_asset {
                for key in amount_keys {
                    if let Some(value) = object.get(*key).and_then(value_as_f64) {
                        return value;
                    }
                }
            }
            object
                .values()
                .map(|value| asset_amount(value, asset, amount_keys))
                .find(|value| *value > 0.0)
                .unwrap_or(0.0)
        }
        Value::Array(values) => values
            .iter()
            .map(|value| asset_amount(value, asset, amount_keys))
            .find(|value| *value > 0.0)
            .unwrap_or(0.0),
        _ => 0.0,
    }
}

pub(crate) fn parse_positive(value: &str, field: &str) -> Result<f64> {
    positive_decimal(value, field)
}

pub(crate) fn format_transfer_amount(value: f64) -> String {
    format_transfer_amount_ceil(value, 6)
}

pub(crate) fn format_transfer_amount_ceil(value: f64, decimals: usize) -> String {
    let multiplier = 10_f64.powi(decimals as i32);
    let value = (value * multiplier).ceil() / multiplier;
    format!("{value:.decimals$}")
        .trim_end_matches('0')
        .trim_end_matches('.')
        .to_string()
}

pub(crate) fn first_bid_price(data: &Value) -> Result<f64> {
    first_book_price(data, &["bids", "b", "levels"], Some("Buy"))
}

pub(crate) async fn fetch_trading_details(
    exchange: Exchange,
    exchange_name: &str,
    product_symbol: &str,
) -> Result<TradingDetails> {
    ProductTable::fetch(Some(exchange), std::time::Duration::from_secs(20))
        .await?
        .get_trading_details(exchange_name, product_symbol)
}

pub(crate) fn post_only_buy_price(data: &Value, details: &TradingDetails) -> Result<String> {
    price_below_market(first_bid_price(data)?, details, 0.95)
}

pub(crate) fn price_below_market(
    price: f64,
    details: &TradingDetails,
    multiplier: f64,
) -> Result<String> {
    let price_step = positive_decimal(&details.price_precision, "price_precision")?;
    let price = round_down_to_step(price * multiplier, price_step);
    format_step_decimal(price, price_step)
}

pub(crate) fn minimum_order_quantity(price: &str, details: &TradingDetails) -> Result<String> {
    minimum_order_quantity_with_step(price, details, None)
}

pub(crate) fn order_notional(
    price: impl Into<f64>,
    quantity: &str,
    details: &TradingDetails,
) -> Result<f64> {
    let price = price.into();
    if !price.is_finite() || price <= 0.0 {
        return Err(DcexError::Decode(format!("invalid price: {price}")));
    }
    let quantity = positive_decimal(quantity, "quantity")?;
    let size_per_contract = non_negative_decimal(&details.size_per_contract, "size_per_contract")?;
    let size_per_contract = if size_per_contract > 0.0 {
        size_per_contract
    } else {
        1.0
    };
    Ok(price * quantity * size_per_contract)
}

pub(crate) fn leveraged_margin_required(
    price: impl Into<f64>,
    quantity: &str,
    details: &TradingDetails,
    leverage: f64,
) -> Result<f64> {
    if !leverage.is_finite() || leverage <= 0.0 {
        return Err(DcexError::Decode(format!("invalid leverage: {leverage}")));
    }
    Ok(order_notional(price, quantity, details)? / leverage * 1.25)
}

pub(crate) fn minimum_order_quantity_with_step(
    price: &str,
    details: &TradingDetails,
    step_override: Option<&str>,
) -> Result<String> {
    let price = positive_decimal(price, "price")?;
    let min_size = non_negative_decimal(&details.min_size, "min_size")?;
    let min_notional = non_negative_decimal(&details.min_notional, "min_notional")?;
    let size_step = step_override
        .map(|value| positive_decimal(value, "size_step"))
        .unwrap_or_else(|| positive_decimal(&details.size_precision, "size_precision"))?;
    let min_notional_size = if min_notional > 0.0 {
        min_notional * 1.01 / price
    } else {
        0.0
    };
    let quantity = round_up_to_step(min_size.max(min_notional_size), size_step);
    format_step_decimal(quantity, size_step)
}

pub(crate) fn bitget_unified_account_error(error: &DcexError) -> bool {
    let message = error.to_string();
    message.contains("40085") || message.contains("Unified Account mode")
}

pub(crate) fn account_restriction(error: &DcexError, patterns: &[&str]) -> bool {
    let message = error.to_string().to_lowercase();
    patterns
        .iter()
        .any(|pattern| message.contains(&pattern.to_lowercase()))
}

pub(crate) fn contains_non_empty_array(data: &Value, keys: &[&str]) -> bool {
    match data {
        Value::Object(object) => {
            for key in keys {
                if object
                    .get(*key)
                    .and_then(Value::as_array)
                    .is_some_and(|values| !values.is_empty())
                {
                    return true;
                }
            }
            object
                .values()
                .any(|value| contains_non_empty_array(value, keys))
        }
        Value::Array(values) => !values.is_empty(),
        _ => false,
    }
}

pub(crate) fn sum_abs_values(data: &Value, keys: &[&str]) -> f64 {
    match data {
        Value::Object(object) => {
            let own = keys
                .iter()
                .filter_map(|key| object.get(*key))
                .filter_map(value_as_f64)
                .map(f64::abs)
                .sum::<f64>();
            own + object
                .values()
                .map(|value| sum_abs_values(value, keys))
                .sum::<f64>()
        }
        Value::Array(values) => values
            .iter()
            .map(|value| sum_abs_values(value, keys))
            .sum::<f64>(),
        _ => 0.0,
    }
}

pub(crate) fn sum_abs_values_for_symbols(
    data: &Value,
    symbol_keys: &[&str],
    symbols: &[&str],
    value_keys: &[&str],
) -> f64 {
    match data {
        Value::Object(object) => {
            let own = if object_matches_symbol(object, symbol_keys, symbols) {
                value_keys
                    .iter()
                    .filter_map(|key| object.get(*key))
                    .filter_map(value_as_f64)
                    .map(f64::abs)
                    .sum::<f64>()
            } else {
                0.0
            };
            own + object
                .values()
                .map(|value| sum_abs_values_for_symbols(value, symbol_keys, symbols, value_keys))
                .sum::<f64>()
        }
        Value::Array(values) => values
            .iter()
            .map(|value| sum_abs_values_for_symbols(value, symbol_keys, symbols, value_keys))
            .sum::<f64>(),
        _ => 0.0,
    }
}

pub(crate) async fn wait_for_positive_position<F, Fut>(mut read: F) -> Result<f64>
where
    F: FnMut() -> Fut,
    Fut: Future<Output = Result<f64>>,
{
    let mut latest = read().await?;
    for _ in 0..10 {
        if latest > 0.0 {
            return Ok(latest);
        }
        sleep(Duration::from_secs(1)).await;
        latest = read().await?;
    }
    Ok(latest)
}

pub(crate) async fn wait_for_flat_position<F, Fut>(mut read: F) -> Result<f64>
where
    F: FnMut() -> Fut,
    Fut: Future<Output = Result<f64>>,
{
    let mut latest = read().await?;
    for _ in 0..10 {
        if latest.abs() <= 1e-12 {
            return Ok(latest);
        }
        sleep(Duration::from_secs(1)).await;
        latest = read().await?;
    }
    Ok(latest)
}

pub(crate) async fn wait_for_non_empty_records<F, Fut>(mut read: F, keys: &[&str]) -> Result<bool>
where
    F: FnMut() -> Fut,
    Fut: IntoFuture<Output = Result<ValidatedResponse>>,
{
    let mut response = read().into_future().await?;
    for _ in 0..10 {
        if contains_non_empty_array(&response.data, keys) {
            return Ok(true);
        }
        sleep(Duration::from_secs(1)).await;
        response = read().into_future().await?;
    }
    Ok(false)
}

fn first_book_price(data: &Value, array_keys: &[&str], object_side: Option<&str>) -> Result<f64> {
    first_book_price_value(data, array_keys, object_side).ok_or_else(|| {
        DcexError::Decode(format!(
            "orderbook response did not contain a usable price for keys {array_keys:?}: {data}"
        ))
    })
}

fn round_down_to_step(value: f64, step: f64) -> f64 {
    (value / step).floor() * step
}

fn round_up_to_step(value: f64, step: f64) -> f64 {
    (value / step).ceil() * step
}

fn format_step_decimal(value: f64, step: f64) -> Result<String> {
    if !value.is_finite() || value <= 0.0 {
        return Err(DcexError::Decode(format!("invalid decimal value: {value}")));
    }
    let decimals = decimals_for_step(step);
    Ok(format!("{value:.decimals$}"))
}

fn decimals_for_step(step: f64) -> usize {
    if step >= 1.0 {
        return 0;
    }
    let mut decimals = 0;
    let mut scaled = step;
    while decimals < 12 && (scaled - scaled.round()).abs() > 1e-10 {
        scaled *= 10.0;
        decimals += 1;
    }
    decimals
}

fn positive_decimal(value: &str, field: &str) -> Result<f64> {
    let parsed = non_negative_decimal(value, field)?;
    if parsed <= 0.0 {
        return Err(DcexError::Decode(format!(
            "{field} must be positive: {value}"
        )));
    }
    Ok(parsed)
}

fn non_negative_decimal(value: &str, field: &str) -> Result<f64> {
    let parsed = value
        .parse::<f64>()
        .map_err(|error| DcexError::Decode(format!("invalid {field} {value}: {error}")))?;
    if !parsed.is_finite() || parsed < 0.0 {
        return Err(DcexError::Decode(format!(
            "{field} must be non-negative: {value}"
        )));
    }
    Ok(parsed)
}

fn first_book_price_value(
    data: &Value,
    array_keys: &[&str],
    object_side: Option<&str>,
) -> Option<f64> {
    match data {
        Value::Object(object) => {
            for key in array_keys {
                if let Some(price) = object.get(*key).and_then(first_price_in_array) {
                    return Some(price);
                }
            }
            if let Some(side) = object_side {
                let object_side = object
                    .get("side")
                    .or_else(|| object.get("Side"))
                    .and_then(Value::as_str);
                if object_side == Some(side) {
                    return object
                        .get("price")
                        .or_else(|| object.get("Price"))
                        .and_then(value_as_f64);
                }
            }
            object
                .values()
                .find_map(|value| first_book_price_value(value, array_keys, object_side))
        }
        Value::Array(values) => {
            if let Some(price) = first_price_in_array(data) {
                return Some(price);
            }
            values
                .iter()
                .find_map(|value| first_book_price_value(value, array_keys, object_side))
        }
        _ => None,
    }
}

fn first_price_in_array(data: &Value) -> Option<f64> {
    let rows = data.as_array()?;
    let first = rows.first()?;
    match first {
        Value::Array(values) => values.first().and_then(|value| match value {
            Value::Array(_) | Value::Object(_) => first_price_in_array(value),
            _ => value_as_f64(value),
        }),
        Value::Object(object) => object
            .get("price")
            .or_else(|| object.get("p"))
            .or_else(|| object.get("px"))
            .or_else(|| object.get("Price"))
            .and_then(value_as_f64),
        _ => value_as_f64(first),
    }
}

fn value_as_f64(value: &Value) -> Option<f64> {
    match value {
        Value::Number(number) => number.as_f64(),
        Value::String(value) => value.parse().ok(),
        _ => None,
    }
}

fn object_matches_symbol(
    object: &serde_json::Map<String, Value>,
    symbol_keys: &[&str],
    symbols: &[&str],
) -> bool {
    symbol_keys.iter().any(|key| {
        object
            .get(*key)
            .and_then(value_to_string)
            .is_some_and(|value| symbols.iter().any(|symbol| symbol == &value))
    })
}

fn value_to_string(value: &Value) -> Option<String> {
    match value {
        Value::String(value) if !value.is_empty() => Some(value.clone()),
        Value::Number(value) => Some(value.to_string()),
        _ => None,
    }
}

fn first_scalar_string(value: &Value) -> Option<String> {
    value_to_string(value).or_else(|| match value {
        Value::Array(values) => values.iter().find_map(first_scalar_string),
        Value::Object(object) => object.values().find_map(first_scalar_string),
        _ => None,
    })
}

fn env_value(name: &str) -> Option<String> {
    std::env::var(name)
        .ok()
        .filter(|value| !value.is_empty())
        .or_else(|| dotenv_values().get(name).cloned())
}

fn dotenv_values() -> &'static HashMap<String, String> {
    static VALUES: OnceLock<HashMap<String, String>> = OnceLock::new();
    VALUES.get_or_init(|| {
        let contents = std::env::current_dir()
            .ok()
            .and_then(|directory| {
                directory
                    .ancestors()
                    .map(|ancestor| ancestor.join(".env"))
                    .find_map(|path| std::fs::read_to_string(path).ok())
            })
            .unwrap_or_default();
        contents
            .lines()
            .filter_map(|line| {
                let line = line.trim();
                if line.is_empty() || line.starts_with('#') {
                    return None;
                }
                let (key, value) = line.split_once('=')?;
                let value = value.trim().trim_matches('"').trim_matches('\'');
                Some((key.trim().to_string(), value.to_string()))
            })
            .collect()
    })
}

fn now_ms() -> u128 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .expect("system clock should be after unix epoch")
        .as_millis()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn first_bid_price_reads_hyperliquid_levels() {
        let data = serde_json::json!({
            "levels": [
                [{"px": "63567.0", "sz": "1"}],
                [{"px": "63568.0", "sz": "1"}]
            ]
        });

        assert_eq!(first_bid_price(&data).expect("bid"), 63567.0);
    }
}
