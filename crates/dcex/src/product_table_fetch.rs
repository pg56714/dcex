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
    use self::exchanges as fetch;
    use crate::exchanges::{
        arcus::ArcusClient, aster::AsterClient, backpack::BackpackClient, binance::BinanceClient,
        bingx::BingxClient, bitget::BitgetClient, bybit::BybitClient, extended::ExtendedClient,
        hyperliquid::HyperliquidClient, kraken::KrakenClient, kucoin::KucoinClient,
        mexc::MexcClient, okx::OkxClient, ondo::OndoClient,
    };
    match exchange {
        Exchange::Arcus => fetch::fetch_arcus(&ArcusClient::public(timeout)?).await,
        Exchange::Aster => fetch::fetch_aster(&AsterClient::public(timeout)?).await,
        Exchange::Backpack => fetch::fetch_backpack(&BackpackClient::public(5_000, timeout)?).await,
        Exchange::Binance => {
            // The Equity metadata endpoint requires an API key even though it is unsigned.
            let equity = match std::env::var("BINANCE_API_KEY") {
                Ok(api_key) if !api_key.is_empty() => {
                    Some(BinanceClient::new(Some(api_key), None, timeout)?)
                }
                _ => None,
            };
            fetch::fetch_binance(&BinanceClient::public(timeout)?, equity.as_ref()).await
        }
        Exchange::BingX => fetch::fetch_bingx(&BingxClient::public(timeout)?).await,
        Exchange::Bitget => fetch::fetch_bitget(&BitgetClient::public(timeout)?).await,
        Exchange::Bybit => fetch::fetch_bybit(&BybitClient::public(5_000, false, timeout)?).await,
        Exchange::Extended => fetch::fetch_extended(&ExtendedClient::public(timeout)?).await,
        Exchange::Hyperliquid => {
            fetch::fetch_hyperliquid(&HyperliquidClient::public(false, timeout)?).await
        }
        Exchange::KuCoin => fetch::fetch_kucoin(&KucoinClient::public(timeout)?).await,
        Exchange::Kraken => fetch::fetch_kraken(&KrakenClient::public(timeout)?).await,
        Exchange::Lighter => fetch::fetch_lighter(timeout).await,
        Exchange::Mexc => fetch::fetch_mexc(&MexcClient::public(timeout)?).await,
        Exchange::Okx => fetch::fetch_okx(&OkxClient::public(timeout)?).await,
        Exchange::Ondo => fetch::fetch_ondo(&OndoClient::public(timeout)?).await,
    }
}

#[path = "product_table_fetch/exchanges.rs"]
mod exchanges;

#[cfg(test)]
pub(crate) use self::exchanges::kraken_spot_rows;

#[cfg(test)]
#[path = "product_table_fetch/fetch_tests.rs"]
mod fetch_tests;
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
    optional_i32(value, key).unwrap_or(default)
}

fn optional_i32(value: &Value, key: &str) -> Option<i32> {
    value.get(key).and_then(|value| {
        value
            .as_i64()
            .and_then(|value| i32::try_from(value).ok())
            .or_else(|| value.as_str()?.parse().ok())
    })
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

/// Step for a count of decimal places (`N` -> `10^-N`, so 0 -> "1"); "0" (unknown) when the
/// count is absent or invalid.
fn decimal_precision_or_zero(decimal_places: Option<i32>) -> String {
    match decimal_places {
        Some(places) if places >= 0 => decimal_precision(places),
        _ => "0".to_string(),
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
    if first.is_empty() { second } else { first }
}

fn binance_product_symbol(base: &str, quote: &str, symbol: &str, spot: bool) -> String {
    if spot {
        return format!("{base}-{quote}-SPOT");
    }
    // Delivery contracts carry their YYMMDD expiry after `_` (for example BTCUSDT_261225).
    symbol.split_once('_').map_or_else(
        || format!("{base}-{quote}-SWAP"),
        |(_, expiry)| format!("{base}-{quote}-{expiry}-FUTURES"),
    )
}

/// Dated futures share one canonical form, `BASE-QUOTE-YYMMDD-FUTURES`, with the date taken
/// from the exchange's delivery timestamp (milliseconds, UTC).
fn delivery_date(market: &Value, key: &str) -> Result<String> {
    let timestamp_ms = market
        .get(key)
        .and_then(|value| value.as_u64().or_else(|| value.as_str()?.parse().ok()))
        .filter(|timestamp_ms| *timestamp_ms > 0)
        .ok_or_else(|| DcexError::Decode(format!("dated futures market lacks {key}")))?;
    yymmdd(&crate::time::format_timestamp_iso(timestamp_ms))
}

/// `YYMMDD` from an ISO-8601 date such as `2026-12-25T08:00:00.000Z`.
fn yymmdd(iso: &str) -> Result<String> {
    let bytes = iso.as_bytes();
    let digits = |range: std::ops::Range<usize>| bytes[range].iter().all(u8::is_ascii_digit);
    if bytes.len() < 10
        || bytes[4] != b'-'
        || bytes[7] != b'-'
        || !digits(0..4)
        || !digits(5..7)
        || !digits(8..10)
    {
        return Err(DcexError::Decode(format!("invalid delivery date: {iso}")));
    }
    Ok(format!("{}{}{}", &iso[2..4], &iso[5..7], &iso[8..10]))
}

fn canonical_market_pair(
    market: &Value,
    display_key: &str,
    exchange_symbol: &str,
) -> Result<(String, String)> {
    if let Some(display_symbol) = non_empty_string(market, display_key)
        && let Ok(pair) = split_last(&display_symbol, '-')
    {
        return Ok(pair);
    }
    split_last(exchange_symbol, '-')
}

fn binance_product_type(contract_type: &str) -> &'static str {
    if contract_type == "PERPETUAL" || contract_type == "TRADIFI_PERPETUAL" {
        "swap"
    } else {
        "futures"
    }
}

fn bybit_product_symbol(
    market: &Value,
    base: &str,
    quote: &str,
    product_type: &str,
) -> Result<String> {
    Ok(match product_type {
        "spot" => format!("{base}-{quote}-SPOT"),
        "futures" => format!(
            "{base}-{quote}-{}-FUTURES",
            delivery_date(market, "deliveryTime")?
        ),
        _ => format!("{base}-{quote}-SWAP"),
    })
}

fn bybit_product_type(category: &str, contract_type: &str) -> &'static str {
    if category == "spot" {
        "spot"
    } else if contract_type.ends_with("Futures") {
        "futures"
    } else {
        "swap"
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
        "XDG" | "XXDG" => Some("DOGE"),
        "XETH" => Some("ETH"),
        "XLTC" => Some("LTC"),
        "XXRP" => Some("XRP"),
        "XXLM" => Some("XLM"),
        "XXMR" => Some("XMR"),
        "XETC" => Some("ETC"),
        "XREP" => Some("REP"),
        "XZEC" => Some("ZEC"),
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
    value.to_string()
}

fn normalize_kraken_spot_currency(value: &str, tokenized_asset: bool) -> String {
    if tokenized_asset {
        value.to_string()
    } else {
        normalize_kraken_currency(value)
    }
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
) -> Result<(String, String)> {
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
        // Fixed-maturity symbols end in their YYMMDD expiry (FI_XBTUSD_261225); otherwise the
        // ISO `lastTradingTime` supplies it.
        let expiry = match parts
            .get(2)
            .filter(|value| value.len() == 6 && value.bytes().all(|byte| byte.is_ascii_digit()))
        {
            Some(expiry) => expiry.to_string(),
            None => yymmdd(&value_string(market, "lastTradingTime", ""))?,
        };
        return Ok((
            format!("{base}-{quote}-{expiry}{inverse}-FUTURES"),
            "futures".to_string(),
        ));
    }
    Ok((format!("{base}-{quote}{inverse}-SWAP"), "swap".to_string()))
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
