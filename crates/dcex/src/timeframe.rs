//! Timeframe utilities.
use crate::{DcexError, Result};

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

fn unsupported_timeframe() -> DcexError {
    DcexError::InvalidInput("timeframe not supported".to_string())
}
