//! Conditional requirements for OPO/OTO and their OCO variants.
use super::params::PublicParams;
use crate::{DcexError, Result};
fn invalid(message: impl std::fmt::Display) -> DcexError {
    DcexError::InvalidInput(format!("Binance order list: {message}"))
}

pub(super) fn validate(path: &str, p: &PublicParams) -> Result<()> {
    if !matches!(
        path,
        "/api/v3/orderList/oco"
            | "/api/v3/orderList/oto"
            | "/api/v3/orderList/otoco"
            | "/api/v3/orderList/opo"
            | "/api/v3/orderList/opoco"
            | "/sapi/v1/margin/order/oco"
            | "/sapi/v1/margin/order/oto"
            | "/sapi/v1/margin/order/otoco"
    ) {
        return Ok(());
    }
    let mut ids = std::collections::BTreeSet::new();
    for (key, value) in &p.0 {
        if key.ends_with("ClientOrderId") && !ids.insert(value) {
            return Err(invalid(
                "client order identifiers must be distinct across the list",
            ));
        }
        if key.ends_with("StrategyType") && value.parse::<u64>().map_err(invalid)? < 1_000_000 {
            return Err(invalid("strategy types below 1000000 are reserved"));
        }
        if key.ends_with("TrailingDelta") && value.parse::<u64>().map_err(invalid)? == 0 {
            return Err(invalid("trailing delta must be a positive integer"));
        }
        if key.ends_with("PegOffsetValue") && value.parse::<u64>().map_err(invalid)? > 100 {
            return Err(invalid("peg offset must not exceed 100"));
        }
    }
    if path == "/sapi/v1/margin/order/oco" {
        if p.get("stopLimitPrice").is_some() {
            p.required("stopLimitTimeInForce")?;
        }
        if p.get("stopIcebergQty").is_some()
            && (p.get("stopLimitPrice").is_none() || p.get("stopLimitTimeInForce") != Some("GTC"))
        {
            return Err(invalid("stop iceberg requires a GTC stop limit order"));
        }
        let price = p.required("price")?.parse::<f64>().map_err(invalid)?;
        let stop = p.required("stopPrice")?.parse::<f64>().map_err(invalid)?;
        if p.get("side") == Some("SELL") && price <= stop
            || p.get("side") == Some("BUY") && price >= stop
        {
            return Err(invalid(
                "OCO limit and trigger prices have the wrong ordering for the side",
            ));
        }
        for key in ["limitIcebergQty", "stopIcebergQty"] {
            if let Some(value) = p.get(key) {
                if value.parse::<f64>().map_err(invalid)?
                    > p.required("quantity")?.parse::<f64>().map_err(invalid)?
                {
                    return Err(invalid("iceberg quantity exceeds order quantity"));
                }
            }
        }
        return Ok(());
    }
    if path.starts_with("/api/v3/orderList/op")
        && (p.get("workingSide") != Some("BUY") || p.get("pendingSide") != Some("SELL"))
    {
        return Err(invalid("OPO requires working BUY and pending SELL"));
    }
    for prefix in [
        "working",
        "pending",
        "pendingAbove",
        "pendingBelow",
        "above",
        "below",
    ] {
        let type_key = format!("{prefix}Type");
        let Some(kind) = p.get(&type_key) else {
            continue;
        };
        let price = format!("{prefix}Price");
        let tif = format!("{prefix}TimeInForce");
        let stop = format!("{prefix}StopPrice");
        let delta = format!("{prefix}TrailingDelta");
        let peg = format!("{prefix}PegPriceType");
        let offset_type = format!("{prefix}PegOffsetType");
        let offset_value = format!("{prefix}PegOffsetValue");
        let iceberg = format!("{prefix}IcebergQty");
        if matches!(
            kind,
            "LIMIT" | "LIMIT_MAKER" | "STOP_LOSS_LIMIT" | "TAKE_PROFIT_LIMIT"
        ) && p.get(&price).is_none()
            && p.get(&peg).is_none()
        {
            return Err(invalid(format!(
                "{price} is required without a pegged price"
            )));
        }
        if matches!(kind, "LIMIT" | "STOP_LOSS_LIMIT" | "TAKE_PROFIT_LIMIT") {
            p.required(&tif)?;
        }
        if matches!(
            kind,
            "STOP_LOSS" | "STOP_LOSS_LIMIT" | "TAKE_PROFIT" | "TAKE_PROFIT_LIMIT"
        ) && p.get(&stop).is_none()
            && p.get(&delta).is_none()
        {
            return Err(invalid(format!("{stop} or {delta} is required")));
        }
        if path.starts_with("/sapi/") && p.get(&delta).is_some() {
            p.required(&price)?;
        }
        if let Some(value) = p.get(&iceberg) {
            if p.get(&tif) != Some("GTC") && !(path.starts_with("/api/") && kind == "LIMIT_MAKER") {
                return Err(invalid(format!("{iceberg} requires GTC")));
            }
            if let Some(quantity) = p.get(&format!("{prefix}Quantity")) {
                if value.parse::<f64>().map_err(invalid)?
                    > quantity.parse::<f64>().map_err(invalid)?
                {
                    return Err(invalid("iceberg quantity exceeds order quantity"));
                }
            }
        }
        if p.get(&offset_type).is_some() != p.get(&offset_value).is_some()
            || p.get(&offset_value).is_some() && p.get(&peg).is_none()
        {
            return Err(invalid(
                "peg offsets require a peg price type and both offset fields",
            ));
        }
    }
    Ok(())
}
