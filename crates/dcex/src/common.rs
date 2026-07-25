use std::sync::LazyLock;

use regex::{Captures, Regex};

use crate::exchange::unix_timestamp_ms;
use crate::exchange::Exchange;
use crate::{DcexError, Result};

static URL_PATTERN: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r#"(?i)(?:https?:/{1,2}|//)[^\s<>'"]+"#).expect("valid URL sanitization regex")
});
static BEARER_TOKEN_PATTERN: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]+").expect("valid bearer token regex")
});
static AUTHORIZATION_PATTERN: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r#"(?ix)
        ["']?\bauthorization\b["']?
        \s*[:=]\s*
        (?:
            '[^']*'
            |
            "[^"]*"
            |
            (?:basic|bearer|digest)\s+[^,\s;}\]]+
            |
            [^,\s;}\]]+
        )
        "#,
    )
    .expect("valid authorization regex")
});
static SENSITIVE_ASSIGNMENT_PATTERN: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r#"(?ix)
        ["']?
        \b(?:
            api[_-]?(?:key|secret)
            |
            access[_-]?key
            |
            secret[_-]?key
            |
            signature
            |
            secret
            |
            passphrase
            |
            password
            |
            authorization
            |
            token
        )\b
        ["']?
        \s*[:=]\s*
        (?:
            '[^']*'
            |
            "[^"]*"
            |
            [^,\s&}\]]+
        )
        "#,
    )
    .expect("valid sensitive assignment regex")
});

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum OrderSide {
    Buy,
    Sell,
}

impl OrderSide {
    pub fn parse(value: &str) -> Result<Self> {
        match value.trim().to_ascii_lowercase().as_str() {
            "buy" => Ok(Self::Buy),
            "sell" => Ok(Self::Sell),
            _ => Err(DcexError::InvalidInput(format!(
                "Unknown order side: {value:?}"
            ))),
        }
    }

    pub const fn is_buy(self) -> bool {
        matches!(self, Self::Buy)
    }

    pub fn to_exchange(self, exchange: &str) -> Result<&'static str> {
        let exchange = exchange.to_ascii_lowercase();
        if matches!(exchange.as_str(), "hyperliquid" | "lighter") {
            return Err(DcexError::InvalidInput(format!(
                "{exchange} expresses side as a boolean; use OrderSide.is_buy() instead"
            )));
        }
        let value = match (self, exchange.as_str()) {
            (Self::Buy, "aster" | "binance" | "bingx" | "mexc") => "BUY",
            (Self::Sell, "aster" | "binance" | "bingx" | "mexc") => "SELL",
            (Self::Buy, "backpack") => "Bid",
            (Self::Sell, "backpack") => "Ask",
            (Self::Buy, "bybit") => "Buy",
            (Self::Sell, "bybit") => "Sell",
            (Self::Buy, "extended") => "BUY",
            (Self::Sell, "extended") => "SELL",
            (Self::Buy, "okx" | "bitget" | "kucoin" | "kraken") => "buy",
            (Self::Sell, "okx" | "bitget" | "kucoin" | "kraken") => "sell",
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "No OrderSide mapping for exchange: {exchange:?}"
                )));
            }
        };
        Ok(value)
    }
}

pub fn exchange_names() -> Vec<&'static str> {
    Exchange::ALL.into_iter().map(Exchange::as_str).collect()
}

pub fn generate_timestamp_ms() -> Result<u64> {
    unix_timestamp_ms()
}

pub fn generate_timestamp_iso() -> Result<String> {
    generate_timestamp_ms().map(format_timestamp_iso)
}

pub fn format_timestamp_iso(timestamp_ms: u64) -> String {
    let days = timestamp_ms / 86_400_000;
    let day_ms = timestamp_ms % 86_400_000;
    let (year, month, day) = civil_from_days(days as i64);
    let hour = day_ms / 3_600_000;
    let minute = day_ms % 3_600_000 / 60_000;
    let second = day_ms % 60_000 / 1_000;
    let millisecond = day_ms % 1_000;
    format!("{year:04}-{month:02}-{day:02}T{hour:02}:{minute:02}:{second:02}.{millisecond:03}Z")
}

pub fn get_decimal_places(value: f64) -> Result<u32> {
    if !value.is_finite() {
        return Err(DcexError::InvalidInput("value must be finite".to_string()));
    }
    let value = value.abs();
    if value == 0.0 || value.fract() == 0.0 {
        return Ok(0);
    }
    let rendered = value.to_string();
    if let Some((mantissa, exponent)) = rendered
        .split_once('e')
        .or_else(|| rendered.split_once('E'))
    {
        let exponent = exponent.parse::<i32>().map_err(|error| {
            DcexError::InvalidInput(format!("invalid decimal exponent: {error}"))
        })?;
        let decimals = mantissa.split_once('.').map_or(0, |(_, fraction)| {
            fraction.trim_end_matches('0').len() as i32
        });
        return Ok(decimals.saturating_sub(exponent).max(0) as u32);
    }
    Ok(rendered.split_once('.').map_or(0, |(_, fraction)| {
        fraction.trim_end_matches('0').len() as u32
    }))
}

pub fn reverse_decimal_places(decimal_places: i32) -> f64 {
    10_f64.powi(-decimal_places)
}

pub fn bybit_convert_timeframe(timeframe: &str) -> Result<&'static str> {
    match timeframe {
        "1m" => Ok("1"),
        "3m" => Ok("3"),
        "5m" => Ok("5"),
        "15m" => Ok("15"),
        "30m" => Ok("30"),
        "1h" => Ok("60"),
        "2h" => Ok("120"),
        "4h" => Ok("240"),
        "6h" => Ok("360"),
        "12h" => Ok("720"),
        "1d" => Ok("D"),
        "1w" => Ok("W"),
        "1M" => Ok("M"),
        _ => Err(unsupported_timeframe()),
    }
}

pub fn kucoin_convert_timeframe(timeframe: &str) -> Result<&'static str> {
    match timeframe {
        "1m" => Ok("1min"),
        "3m" => Ok("3min"),
        "5m" => Ok("5min"),
        "15m" => Ok("15min"),
        "30m" => Ok("30min"),
        "1h" => Ok("1hour"),
        "2h" => Ok("2hour"),
        "4h" => Ok("4hour"),
        "6h" => Ok("6hour"),
        "8h" => Ok("8hour"),
        "12h" => Ok("12hour"),
        "1d" => Ok("1day"),
        "1w" => Ok("1week"),
        "1M" => Ok("1month"),
        _ => Err(unsupported_timeframe()),
    }
}

pub fn address_to_bytes(address: &str) -> Result<Vec<u8>> {
    let address = address.strip_prefix("0x").unwrap_or(address);
    hex::decode(address)
        .map_err(|error| DcexError::InvalidInput(format!("invalid hexadecimal address: {error}")))
}

pub fn sanitize_url(url: &str) -> String {
    let value = url.split_whitespace().next().unwrap_or_default();
    if value.is_empty() {
        return String::new();
    }

    if value.starts_with("//") {
        return sanitize_absolute_url(&format!("https:{value}"))
            .map(|safe| safe.trim_start_matches("https:").to_string())
            .unwrap_or_else(|| "<redacted-url>".to_string());
    }

    if value
        .get(..5)
        .is_some_and(|prefix| prefix.eq_ignore_ascii_case("http:"))
        || value
            .get(..6)
            .is_some_and(|prefix| prefix.eq_ignore_ascii_case("https:"))
    {
        return sanitize_absolute_url(value).unwrap_or_else(|| "<redacted-url>".to_string());
    }

    value
        .split_once('?')
        .map_or(value, |(path, _)| path)
        .split_once('#')
        .map_or_else(
            || value.split_once('?').map_or(value, |(path, _)| path),
            |(path, _)| path,
        )
        .to_string()
}

pub fn sanitize_request(request: &str) -> String {
    let request_line = request
        .split_once(" | ")
        .map_or(request, |(summary, _)| summary)
        .trim();
    let mut parts = request_line.split_whitespace();
    let Some(method) = parts.next() else {
        return "<redacted>".to_string();
    };
    let method = method.to_ascii_uppercase();
    if !matches!(
        method.as_str(),
        "DELETE" | "GET" | "HEAD" | "OPTIONS" | "PATCH" | "POST" | "PUT"
    ) {
        return "<redacted>".to_string();
    }
    let Some(url) = parts.next() else {
        return "<redacted>".to_string();
    };
    let safe_url = sanitize_url(url);
    if safe_url.is_empty() {
        "<redacted>".to_string()
    } else {
        format!("{method} {safe_url}")
    }
}

pub fn sanitize_message(message: &str) -> String {
    let sanitized = URL_PATTERN.replace_all(message, |captures: &Captures<'_>| {
        let matched_url = captures.get(0).expect("whole URL match").as_str();
        let trimmed = matched_url.trim_end_matches(['.', ',', ';', ':', '!', '?', ')', ']', '}']);
        let trailing = &matched_url[trimmed.len()..];
        format!("{}{trailing}", sanitize_url(trimmed))
    });
    let sanitized = AUTHORIZATION_PATTERN.replace_all(&sanitized, "<redacted>");
    let sanitized = BEARER_TOKEN_PATTERN.replace_all(&sanitized, "<redacted>");
    SENSITIVE_ASSIGNMENT_PATTERN
        .replace_all(&sanitized, "<redacted>")
        .into_owned()
}

fn sanitize_absolute_url(value: &str) -> Option<String> {
    let parsed = url::Url::parse(value).ok()?;
    if !matches!(parsed.scheme(), "http" | "https") {
        return None;
    }
    let host = parsed.host_str()?;
    let mut safe = format!("{}://{}", parsed.scheme(), host);
    if let Some(port) = parsed.port() {
        safe.push(':');
        safe.push_str(&port.to_string());
    }
    safe.push_str(parsed.path());
    Some(safe)
}

fn unsupported_timeframe() -> DcexError {
    DcexError::InvalidInput("timeframe not supported".to_string())
}

fn civil_from_days(days_since_unix_epoch: i64) -> (i64, i64, i64) {
    let days = days_since_unix_epoch + 719_468;
    let era = if days >= 0 { days } else { days - 146_096 } / 146_097;
    let day_of_era = days - era * 146_097;
    let year_of_era =
        (day_of_era - day_of_era / 1_460 + day_of_era / 36_524 - day_of_era / 146_096) / 365;
    let mut year = year_of_era + era * 400;
    let day_of_year = day_of_era - (365 * year_of_era + year_of_era / 4 - year_of_era / 100);
    let month_prime = (5 * day_of_year + 2) / 153;
    let day = day_of_year - (153 * month_prime + 2) / 5 + 1;
    let month = month_prime + if month_prime < 10 { 3 } else { -9 };
    year += i64::from(month <= 2);
    (year, month, day)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn order_side_matches_python_mapping() {
        assert_eq!(
            OrderSide::parse(" buy ")
                .expect("side")
                .to_exchange("bybit")
                .expect("mapping"),
            "Buy"
        );
        assert!(OrderSide::Sell.to_exchange("hyperliquid").is_err());
    }

    #[test]
    fn decimal_helpers_match_python_behavior() {
        assert_eq!(get_decimal_places(0.001).expect("places"), 3);
        assert_eq!(get_decimal_places(1e-7).expect("places"), 7);
        assert_eq!(get_decimal_places(1.0).expect("places"), 0);
        assert_eq!(reverse_decimal_places(3), 0.001);
    }

    #[test]
    fn timestamp_format_matches_python_iso_shape() {
        assert_eq!(format_timestamp_iso(0), "1970-01-01T00:00:00.000Z");
        assert_eq!(
            format_timestamp_iso(1_700_000_000_123),
            "2023-11-14T22:13:20.123Z"
        );
    }

    #[test]
    fn request_sanitization_removes_credentials() {
        assert_eq!(
            sanitize_request(
                "POST https://user:password@api.example.com/order?signature=secret | Body: x"
            ),
            "POST https://api.example.com/order"
        );
        let message = sanitize_message(
            "failed for https://api.example.com/order?signature=url-secret with api_key=private",
        );
        assert_eq!(
            message,
            "failed for https://api.example.com/order with <redacted>"
        );
    }
}
