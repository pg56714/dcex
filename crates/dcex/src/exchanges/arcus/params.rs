use std::collections::BTreeMap;

use crate::{DcexError, Result};

pub(super) fn required<'a>(params: &'a BTreeMap<String, String>, key: &str) -> Result<&'a str> {
    params
        .get(key)
        .map(String::as_str)
        .filter(|value| !value.is_empty())
        .ok_or_else(|| DcexError::InvalidInput(format!("Arcus {key} is required")))
}

pub(super) fn decimal_parts(value: &str) -> Result<(u128, u32)> {
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

pub(super) fn scaled(value: &str, scale: u32) -> Result<u128> {
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

pub(super) fn exact_units(value: &str, unit: &str) -> Result<u64> {
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

pub(super) fn compare_decimals(left: &str, right: &str) -> Result<i8> {
    let scale = decimal_parts(left)?.1.max(decimal_parts(right)?.1);
    Ok(match scaled(left, scale)?.cmp(&scaled(right, scale)?) {
        std::cmp::Ordering::Less => -1,
        std::cmp::Ordering::Equal => 0,
        std::cmp::Ordering::Greater => 1,
    })
}

pub(super) fn decimal_product_below(price: &str, quantity: &str, minimum: &str) -> Result<bool> {
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
