use std::time::Duration;

use serde_json::Value;
use tokio::task::JoinSet;

use crate::common::reverse_decimal_places;
use crate::exchange::{Exchange, ValidatedResponse};
use crate::product_table::MarketInfo;
use crate::{DcexError, Result};

pub(crate) async fn fetch_product_rows(
    exchange: Option<Exchange>,
    timeout: Duration,
) -> Result<Vec<MarketInfo>> {
    if let Some(exchange) = exchange {
        return fetch_exchange_rows(exchange, timeout).await;
    }

    let mut tasks = JoinSet::new();
    for exchange in Exchange::ALL {
        tasks.spawn(async move { fetch_exchange_rows(exchange, timeout).await });
    }

    let mut rows = Vec::new();
    while let Some(result) = tasks.join_next().await {
        if let Ok(Ok(mut exchange_rows)) = result {
            rows.append(&mut exchange_rows);
        }
    }
    if rows.is_empty() {
        Err(DcexError::Runtime(
            "Failed to fetch product tables from any exchange".to_string(),
        ))
    } else {
        Ok(rows)
    }
}

async fn fetch_exchange_rows(exchange: Exchange, timeout: Duration) -> Result<Vec<MarketInfo>> {
    match exchange {
        Exchange::Aster => self::exchanges::fetch_aster(timeout).await,
        Exchange::Backpack => self::exchanges::fetch_backpack(timeout).await,
        Exchange::Binance => self::exchanges::fetch_binance(timeout).await,
        Exchange::BingX => self::exchanges::fetch_bingx(timeout).await,
        Exchange::Bitget => self::exchanges::fetch_bitget(timeout).await,
        Exchange::BitMart => self::exchanges::fetch_bitmart(timeout).await,
        Exchange::BitMEX => self::exchanges::fetch_bitmex(timeout).await,
        Exchange::Bybit => self::exchanges::fetch_bybit(timeout).await,
        Exchange::Extended => self::exchanges::fetch_extended(timeout).await,
        Exchange::GateIo => self::exchanges::fetch_gateio(timeout).await,
        Exchange::Hyperliquid => self::exchanges::fetch_hyperliquid(timeout).await,
        Exchange::KuCoin => self::exchanges::fetch_kucoin(timeout).await,
        Exchange::Kraken => self::exchanges::fetch_kraken(timeout).await,
        Exchange::Lighter => self::exchanges::fetch_lighter(timeout).await,
        Exchange::Mexc => self::exchanges::fetch_mexc(timeout).await,
        Exchange::Okx => self::exchanges::fetch_okx(timeout).await,
    }
}

#[path = "product_table_fetch/exchanges.rs"]
mod exchanges;

#[cfg(test)]
#[path = "product_table_fetch/tests.rs"]
mod tests;

fn response_array<'a>(response: &'a ValidatedResponse, path: &[&str]) -> &'a [Value] {
    let mut value = &response.data;
    for key in path {
        value = value.get(*key).unwrap_or(&Value::Null);
    }
    value_array(Some(value))
}

fn value_array(value: Option<&Value>) -> &[Value] {
    value.and_then(Value::as_array).map_or(&[], Vec::as_slice)
}

fn required_string(value: &Value, key: &str) -> Result<String> {
    value
        .get(key)
        .filter(|value| !value.is_null())
        .map(json_string)
        .ok_or_else(|| DcexError::Decode(format!("missing product table field: {key}")))
}

fn non_empty_string(value: &Value, key: &str) -> Option<String> {
    let value = value.get(key).filter(|value| !value.is_null())?;
    let value = json_string(value);
    (!value.is_empty()).then_some(value)
}

fn value_string(value: &Value, key: &str, default: &str) -> String {
    value
        .get(key)
        .filter(|value| !value.is_null())
        .map_or_else(|| default.to_string(), json_string)
}

fn json_string(value: &Value) -> String {
    match value {
        Value::String(value) => value.clone(),
        _ => value.to_string(),
    }
}

fn value_i32(value: &Value, key: &str, default: i32) -> i32 {
    value
        .get(key)
        .and_then(|value| {
            value
                .as_i64()
                .and_then(|value| i32::try_from(value).ok())
                .or_else(|| value.as_str()?.parse().ok())
        })
        .unwrap_or(default)
}

fn find_filter<'a>(filters: &'a [Value], filter_types: &[&str]) -> &'a Value {
    filters
        .iter()
        .find(|value| {
            value
                .get("filterType")
                .and_then(Value::as_str)
                .is_some_and(|value| filter_types.contains(&value))
        })
        .unwrap_or(&Value::Null)
}

fn split_last(value: &str, separator: char) -> Result<(String, String)> {
    value
        .rsplit_once(separator)
        .map(|(left, right)| (left.to_string(), right.to_string()))
        .ok_or_else(|| DcexError::Decode(format!("invalid exchange symbol: {value}")))
}

fn decimal_precision(decimal_places: i32) -> String {
    match decimal_places {
        i32::MIN..=-1 => 10_i128
            .checked_pow(decimal_places.unsigned_abs())
            .map_or_else(
                || reverse_decimal_places(decimal_places).to_string(),
                |value| value.to_string(),
            ),
        0 => "1".to_string(),
        1..=4 => format!(
            "0.{}1",
            "0".repeat(usize::try_from(decimal_places - 1).expect("positive precision"))
        ),
        _ => format!("1e-{decimal_places:02}"),
    }
}

fn decimal_precision_or_zero(decimal_places: i32) -> String {
    if decimal_places > 0 {
        decimal_precision(decimal_places)
    } else {
        "0".to_string()
    }
}

fn python_float_string(value: &str) -> String {
    value.parse::<f64>().map_or_else(
        |_| value.to_string(),
        |value| {
            if value.fract() == 0.0 {
                format!("{value:.1}")
            } else {
                value.to_string()
            }
        },
    )
}

fn first_non_empty(first: String, second: String) -> String {
    if first.is_empty() {
        second
    } else {
        first
    }
}

fn binance_product_symbol(base: &str, quote: &str, symbol: &str, spot: bool) -> String {
    if spot {
        return format!("{base}-{quote}-SPOT");
    }
    symbol.split_once('_').map_or_else(
        || format!("{base}-{quote}-SWAP"),
        |(_, expiry)| format!("{base}-{quote}-{expiry}-SWAP"),
    )
}

fn bitmex_product_symbol(typ: &str, symbol: &str, base: &str, quote: &str) -> String {
    match typ {
        "IFXXXP" => format!("{base}-{quote}-SPOT"),
        "FFWCSX" => format!("{base}-{quote}-SWAP"),
        "FFCCSX" => {
            let pair = format!("{base}{quote}");
            let expiry = symbol
                .strip_prefix(&pair)
                .or_else(|| symbol.strip_prefix(base))
                .unwrap_or(symbol);
            format!("{base}-{quote}-{expiry}-SWAP")
        }
        _ => symbol.to_string(),
    }
}

fn bybit_product_symbol(
    category: &str,
    base: &mut String,
    quote: &str,
    symbol: &str,
    parts: &[&str],
) -> String {
    if category == "spot" {
        return format!("{base}-{quote}-SPOT");
    }
    if let Some(expiry) = parts.get(1) {
        if category == "inverse" {
            *base = parts[0].to_string();
        }
        format!("{base}-{quote}-{expiry}-SWAP")
    } else {
        let _ = symbol;
        format!("{base}-{quote}-SWAP")
    }
}

fn normalize_kucoin_currency(value: &str) -> String {
    if value == "XBT" {
        "BTC".to_string()
    } else {
        value.to_string()
    }
}

fn normalize_kraken_currency(value: &str) -> String {
    let alias = match value {
        "XXBT" | "XBT" => Some("BTC"),
        "XDG" => Some("DOGE"),
        "ZUSD" => Some("USD"),
        "ZEUR" => Some("EUR"),
        "ZGBP" => Some("GBP"),
        "ZJPY" => Some("JPY"),
        "ZCAD" => Some("CAD"),
        "ZAUD" => Some("AUD"),
        _ => None,
    };
    if let Some(alias) = alias {
        return alias.to_string();
    }
    if value.len() > 3 && (value.starts_with('X') || value.starts_with('Z')) {
        return normalize_kraken_currency(&value[1..]);
    }
    value.to_string()
}

fn kraken_size_precision(market: &Value) -> String {
    let precision = value_i32(market, "contractValueTradePrecision", 0);
    if precision > 0 {
        decimal_precision(precision)
    } else {
        "1".to_string()
    }
}

fn kraken_futures_product(
    symbol: &str,
    base: &str,
    quote: &str,
    instrument_type: &str,
    market: &Value,
) -> (String, String) {
    let parts = symbol.split('_').collect::<Vec<_>>();
    let inverse = if instrument_type == "futures_inverse" {
        "-INVERSE"
    } else {
        ""
    };
    let last_trading_time = market
        .get("lastTradingTime")
        .is_some_and(|value| !value.is_null() && value != "" && value != false);
    if last_trading_time {
        if let Some(expiry) = parts.get(2).filter(|value| !value.is_empty()) {
            return (
                format!("{base}-{quote}-{expiry}{inverse}-SWAP"),
                "futures".to_string(),
            );
        }
        return (
            format!("{base}-{quote}{inverse}-SWAP"),
            "futures".to_string(),
        );
    }
    (format!("{base}-{quote}{inverse}-SWAP"), "swap".to_string())
}

fn lighter_precision(market: &Value, key: &str, fallback: &str) -> String {
    let decimals = market
        .get(key)
        .or_else(|| market.get(fallback))
        .and_then(|value| {
            value
                .as_i64()
                .and_then(|value| i32::try_from(value).ok())
                .or_else(|| value.as_str()?.parse().ok())
        })
        .unwrap_or(0);
    decimal_precision(decimals)
}
