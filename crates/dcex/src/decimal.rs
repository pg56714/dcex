//! Decimal utilities.
use crate::{DcexError, Result};

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

pub(crate) fn is_positive_plain_decimal(value: &str) -> bool {
    let mut parts = value.split('.');
    let whole = parts.next().unwrap_or_default();
    let fraction = parts.next();
    !whole.is_empty()
        && whole.bytes().all(|b| b.is_ascii_digit())
        && fraction.is_none_or(|part| !part.is_empty() && part.bytes().all(|b| b.is_ascii_digit()))
        && parts.next().is_none()
        && value.bytes().any(|b| matches!(b, b'1'..=b'9'))
}

#[cfg(test)]
mod plain_decimal_tests {
    use super::is_positive_plain_decimal;
    #[test]
    fn rejects_exponents_without_losing_tiny_values_or_precision() {
        for value in [
            "1e-3", "1E3", "NaN", "inf", " 1", "1 ", "+1", "-1", ".1", "1.", "0", "0.00", "1.2.3",
        ] {
            assert!(!is_positive_plain_decimal(value), "{value}");
        }
        for value in ["1", "00.1", "123456789012345678901234567890.1234567890"] {
            assert!(is_positive_plain_decimal(value), "{value}");
        }
        assert!(is_positive_plain_decimal(&format!(
            "0.{}1",
            "0".repeat(400)
        )));
    }
}
