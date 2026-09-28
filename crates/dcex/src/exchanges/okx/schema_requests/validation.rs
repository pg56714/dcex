//! Endpoint-specific schema constraints.
use super::*;

pub(super) fn validate_json_shape(value: &Value, schema: &Value) -> Result<()> {
    crate::exchanges::schema::validate_with(value, schema, "request", true, true)
}

pub(super) fn validate_additional(name: &str, p: &OkxParams, schema: &Value) -> Result<()> {
    let mut data = serde_json::Map::new();
    for (key, value) in p.without(&[]) {
        let field = &schema["properties"][&key];
        let value = match field["type"].as_str() {
            Some("array" | "object" | "boolean" | "integer") => {
                serde_json::from_str(&value).map_err(|_| invalid("invalid JSON parameter"))?
            }
            _ => Value::String(value),
        };
        validate_json_shape(&value, field)?;
        data.insert(key, value);
    }
    let data = Value::Object(data);
    {
        let key = "lever";
        positive(p, key)?;
    }
    enumeration(p, "acctLv", &["3", "4"])?;
    enumeration(p, "greeksType", &["BS", "PA", "CASH"])?;
    if let Some(value) = p.get("idxVol")
        && !value.parse::<f64>().is_ok_and(|n| {
            n.is_finite()
                && (-0.99..=1.0).contains(&n)
                && ((n * 100.0).round() - n * 100.0).abs() < 1e-9
        })
    {
        return Err(invalid("idxVol must be -0.99..1 in 0.01 steps"));
    }
    for key in ["simPos", "simAsset"] {
        if let Some(items) = data[key].as_array() {
            for item in items {
                for field in if key == "simPos" {
                    &["pos", "avgPx", "lever"][..]
                } else {
                    &["amt"][..]
                } {
                    if let Some(value) = item.get(field)
                        && !value
                            .as_str()
                            .and_then(|v| v.parse::<f64>().ok())
                            .is_some_and(f64::is_finite)
                    {
                        return Err(invalid("simulated amounts must be finite decimal strings"));
                    }
                }
            }
        }
    }
    match name {
        "get_position_margin_graph" => enumeration(p, "type", &["mmr"])?,
        "move_positions" => {
            if p.get("fromAcct") == p.get("toAcct") {
                return Err(invalid("source and destination accounts must differ"));
            }
            let legs = data["legs"]
                .as_array()
                .ok_or_else(|| invalid("legs must be an array"))?;
            if legs.is_empty() {
                return Err(invalid("legs must not be empty"));
            }
            for leg in legs {
                if !matches!(leg["from"]["side"].as_str(), Some("buy" | "sell"))
                    || !leg["from"]["sz"]
                        .as_str()
                        .is_some_and(crate::common::is_positive_plain_decimal)
                {
                    return Err(invalid("invalid source position side or size"));
                }
                if leg["to"].get("tdMode").is_some()
                    && !matches!(leg["to"]["tdMode"].as_str(), Some("cross" | "isolated"))
                {
                    return Err(invalid("invalid destination margin mode"));
                }
            }
        }
        "adjust_demo_balance" => {
            enumeration(p, "type", &["increase", "reduce"])?;
            let items = data["adjustments"]
                .as_array()
                .ok_or_else(|| invalid("adjustments must be an array"))?;
            let mut seen = std::collections::HashSet::new();
            if items.is_empty() {
                return Err(invalid("adjustments must not be empty"));
            }
            for item in items {
                let ccy = item["ccy"].as_str().unwrap_or_default();
                let max = match ccy {
                    "BTC" | "ETH" => 1.0,
                    "USDT" => 5000.0,
                    "OKB" => 100.0,
                    _ => return Err(invalid("unsupported demo currency")),
                };
                if !seen.insert(ccy)
                    || !item["amt"]
                        .as_str()
                        .and_then(|v| v.parse::<f64>().ok())
                        .is_some_and(|v| {
                            v.is_finite()
                                && v >= 0.0
                                && (p.get("type") == Some("reduce") || v <= max)
                        })
                {
                    return Err(invalid("invalid or duplicate demo adjustment"));
                }
            }
        }
        "rfq_create_rfq" | "rfq_execute_quote" => {
            if let Some(legs) = data["legs"].as_array() {
                if legs.is_empty() || legs.len() > 15 {
                    return Err(invalid("RFQ legs must contain 1..15 entries"));
                }
                for leg in legs {
                    if !leg["sz"]
                        .as_str()
                        .is_some_and(crate::common::is_positive_plain_decimal)
                    {
                        return Err(invalid("RFQ leg size must be positive"));
                    }
                    if name == "rfq_create_rfq"
                        && !matches!(leg["side"].as_str(), Some("buy" | "sell"))
                    {
                        return Err(invalid("invalid RFQ leg side"));
                    }
                }
                let priced = legs.iter().filter(|leg| leg.get("lmtPx").is_some()).count();
                if priced != 0 && priced != legs.len() {
                    return Err(invalid("lmtPx must be supplied for every RFQ leg or none"));
                }
            }
            if name == "rfq_create_rfq"
                && data["counterparties"].as_array().is_none_or(Vec::is_empty)
            {
                return Err(invalid("counterparties must not be empty"));
            }
        }
        "rfq_cancel_rfq" => any(p, &["rfqId", "clRfqId"])?,
        "rfq_cancel_batch_rfqs" => {
            any(p, &["rfqIds", "clRfqIds"])?;
            for key in ["rfqIds", "clRfqIds"] {
                if data[key].as_array().is_some_and(Vec::is_empty) {
                    return Err(invalid("RFQ ID list must not be empty"));
                }
            }
        }
        "get_books_rpi" => {
            if p.get("sz")
                .is_some_and(|v| !v.parse::<u64>().is_ok_and(|v| (1..=400).contains(&v)))
            {
                return Err(invalid("RPI depth must be 1..400"));
            }
        }
        "get_insurance_fund" => {
            enumeration(p, "instType", &["MARGIN", "SWAP", "FUTURES", "OPTION"])?;
            enumeration(
                p,
                "type",
                &["liquidation_balance_deposit", "bankruptcy_loss"],
            )?;
            if p.get("instType") != Some("MARGIN") {
                p.required("instFamily")?;
            }
        }
        "get_market_data_history" => {
            enumeration(p, "module", &["1", "2", "3", "4", "5", "11"])?;
            enumeration(p, "dateAggrType", &["daily", "monthly"])?;
            let key = if p.get("instType") == Some("SPOT") {
                "instIdList"
            } else {
                "instFamilyList"
            };
            list_limit(p.required(key)?, 10)?;
            if p.get(key) == Some("ANY")
                && (p.get("dateAggrType") != Some("daily")
                    || matches!(p.get("module"), Some("4" | "5")))
            {
                return Err(invalid(
                    "ANY is not supported for this module or date aggregation",
                ));
            }
            if p.get("module") == Some("3")
                && p.get("dateAggrType") == Some("daily")
                && p.get("instFamilyList") != Some("ANY")
            {
                return Err(invalid("daily funding history requires instFamilyList=ANY"));
            }
        }
        "create_sub_account" => enumeration(p, "type", &["1"])?,
        "create_sub_account_api_key" | "modify_sub_account_api_key" => {
            if let Some(permissions) = p.get("perm")
                && permissions
                    .split(',')
                    .any(|v| !matches!(v, "read_only" | "trade"))
            {
                return Err(invalid("invalid API key permission"));
            }
            if let Some(ips) = p.get("ip") {
                list_limit(ips, 20)?;
            }
        }
        "set_sub_account_transfer_out" => list_limit(p.required("subAcct")?, 20)?,
        _ => {}
    }
    for (begin, end) in [("begin", "end"), ("beginTs", "endTs")] {
        if let (Some(begin), Some(end)) = (p.get(begin), p.get(end)) {
            let begin = begin
                .parse::<u64>()
                .map_err(|_| invalid("invalid begin timestamp"))?;
            let end = end
                .parse::<u64>()
                .map_err(|_| invalid("invalid end timestamp"))?;
            if begin > end {
                return Err(invalid("begin must not exceed end"));
            }
            if name == "get_market_data_history"
                && p.get("dateAggrType") == Some("daily")
                && end - begin > 10 * 86_400_000
            {
                return Err(invalid("daily historical data range exceeds 10 days"));
            }
        }
    }
    for key in ["clientId", "clRfqId"] {
        if p.get(key)
            .is_some_and(|v| v.len() > 32 || !v.bytes().all(|b| b.is_ascii_alphanumeric()))
        {
            return Err(invalid(
                "client IDs must contain 1..32 ASCII alphanumeric characters",
            ));
        }
    }
    Ok(())
}

pub(super) fn validate(name: &str, p: &OkxParams) -> Result<()> {
    validate_completion(name, p)?;
    if name == "trading_bot_grid_close_position"
        && matches!(p.get("mktClose"), Some("false" | "False"))
    {
        p.required("sz")?;
        p.required("px")?;
    }
    if name == "trading_bot_signal_sub_order" && p.get("ordType") == Some("limit") {
        p.required("px")?;
    }
    if let Some(limit) = p.get("limit") {
        let max = if name == "get_candles_history" {
            300
        } else {
            100
        };
        if !limit.parse::<u64>().is_ok_and(|v| (1..=max).contains(&v)) {
            return Err(invalid("limit is outside the documented range"));
        }
    }
    match name {
        "set_fee_type" => enumeration(p, "feeType", &["0", "1"])?,
        "set_risk_offset_amount" => {
            if !p
                .required("clSpotInUseAmt")?
                .parse::<f64>()
                .is_ok_and(|v| v.is_finite() && v >= 0.0)
            {
                return Err(invalid("risk offset amount must be a nonnegative decimal"));
            }
        }
        "preset_account_level_switch" => {
            enumeration(p, "acctLv", &["2", "3", "4"])?;
            positive(p, "lever")?;
        }
        "precheck_account_level_switch" => enumeration(p, "acctLv", &["1", "2", "3", "4"])?,
        "set_trading_config" => {
            enumeration(p, "type", &["stgyType"])?;
            enumeration(p, "stgyType", &["0", "1"])?;
        }
        "precheck_delta_neutral" => enumeration(p, "stgyType", &["0", "1"])?,
        "set_collateral_assets" => {
            enumeration(p, "type", &["all", "custom"])?;
            if p.get("type") == Some("custom") {
                p.required("ccyList")?;
            }
            if p.get("type") == Some("all") && p.get("ccyList").is_some() {
                return Err(invalid(
                    "ccyList only applies to custom collateral selection",
                ));
            }
        }
        "get_spread_order_history_archive" => {
            enumeration(p, "ordType", &["market", "limit", "post_only", "ioc"])?;
            enumeration(p, "state", &["canceled", "filled"])?;
            enumeration(p, "instType", &["SPOT", "FUTURES", "SWAP"])?;
            if let (Some(begin), Some(end)) = (p.get("begin"), p.get("end"))
                && begin.parse::<u64>().ok() > end.parse::<u64>().ok()
            {
                return Err(invalid("begin must not exceed end"));
            }
        }
        "set_isolated_mode" => {
            enumeration(p, "isoMode", &["auto_transfers_ccy", "automatic"])?;
            enumeration(p, "type", &["MARGIN", "CONTRACTS"])?;
            if p.get("isoMode") == Some("auto_transfers_ccy") && p.get("type") != Some("MARGIN") {
                return Err(invalid("auto_transfers_ccy only applies to MARGIN"));
            }
        }
        "set_account_level" => enumeration(p, "acctLv", &["1", "2", "3", "4"])?,
        "get_pm_position_tiers" => {
            enumeration(p, "instType", &["SWAP", "FUTURES", "OPTION"])?;
            list_limit(p.required("instFamily")?, 5)?;
        }
        "get_collateral_assets" => {
            if let Some(v) = p.get("ccy") {
                list_limit(v, 20)?;
            }
        }
        "get_full_orderbook" => {
            if let Some(v) = p.get("sz")
                && !v.parse::<u64>().is_ok_and(|v| (1..=5000).contains(&v))
            {
                return Err(invalid("book depth must be 1..=5000"));
            }
        }
        "get_trades_history" => {
            enumeration(p, "type", &["1", "2"])?;
            if p.get("type") == Some("2") && p.get("before").is_some() {
                return Err(invalid("before does not support timestamp pagination"));
            }
        }
        "get_candles_history" => enumeration(p, "adjust", &["forward"])?,
        "amend_spread_order" => {
            any(p, &["ordId", "clOrdId"])?;
            any(p, &["newSz", "newPx"])?;
            positive(p, "newSz")?;
            if let Some(price) = p.get("newPx")
                && !price.parse::<f64>().is_ok_and(f64::is_finite)
            {
                return Err(invalid("spread price must be a finite decimal"));
            }
        }
        "convert_contract_coin" => {
            enumeration(p, "type", &["1", "2"])?;
            enumeration(p, "unit", &["coin", "usds"])?;
            enumeration(p, "opType", &["open", "close"])?;
            positive(p, "sz")?;
            positive(p, "px")?;
        }
        "get_index_tickers" => any(p, &["instId", "product_symbol", "quoteCcy"])?,
        "get_convert_currency_pair" => {
            if p.get("fromCcy") == p.get("toCcy") {
                return Err(invalid("conversion currencies must differ"));
            }
        }
        "estimate_convert_quote" | "execute_convert_trade" => {
            enumeration(p, "side", &["buy", "sell"])?;
            if p.get("baseCcy") == p.get("quoteCcy") {
                return Err(invalid("conversion currencies must differ"));
            }
            let (amount, ccy) = if name == "estimate_convert_quote" {
                ("rfqSz", "rfqSzCcy")
            } else {
                ("sz", "szCcy")
            };
            positive(p, amount)?;
            if p.get(ccy) != p.get("baseCcy") && p.get(ccy) != p.get("quoteCcy") {
                return Err(invalid("amount currency must match the requested pair"));
            }
        }
        "get_system_status" => enumeration(
            p,
            "state",
            &["scheduled", "ongoing", "pre_open", "completed", "canceled"],
        )?,
        _ => {}
    }
    enumeration(p, "convertMode", &["0", "1"])?;
    for key in ["reqId", "clQReqId", "clTReqId"] {
        if let Some(v) = p.get(key)
            && (v.len() > 32 || !v.bytes().all(|b| b.is_ascii_alphanumeric()))
        {
            return Err(invalid(
                "client request ID must be alphanumeric and no longer than 32 characters",
            ));
        }
    }
    for key in ["ccyList", "repayCcyList"] {
        if let Some(value) = p.get(key) {
            let values: Vec<String> = serde_json::from_str(value)
                .map_err(|_| invalid("currency list must be an array of strings"))?;
            let mut seen = std::collections::HashSet::new();
            if values.is_empty()
                || values
                    .iter()
                    .any(|v| v.trim().is_empty() || !seen.insert(v))
            {
                return Err(invalid(
                    "currency list must be nonempty with distinct entries",
                ));
            }
        }
    }
    for key in ["begin", "end", "beginId", "endId"] {
        if let Some(v) = p.get(key) {
            v.parse::<u64>()
                .map_err(|_| invalid("timestamp and order IDs must be unsigned integers"))?;
        }
    }
    Ok(())
}
pub(super) fn enumeration(p: &OkxParams, key: &str, values: &[&str]) -> Result<()> {
    if p.get(key).is_some_and(|v| !values.contains(&v)) {
        return Err(invalid(&format!("invalid {key}")));
    }
    Ok(())
}

pub(super) fn validate_completion(name: &str, p: &OkxParams) -> Result<()> {
    let integer = |key: &str, maximum: u64| -> Result<()> {
        if let Some(raw) = p.get(key)
            && !raw.parse::<u64>().is_ok_and(|n| n <= maximum)
        {
            return Err(invalid(&format!(
                "{key} must be an integer in 0..{maximum}"
            )));
        }
        Ok(())
    };
    match name {
        "reset_mmp" | "mass_cancel_options_orders" => {
            enumeration(p, "instType", &["OPTION"])?;
            integer("lockInterval", 10000)?;
        }
        "set_mmp_config" => {
            integer("timeInterval", u64::MAX)?;
            integer("frozenInterval", u64::MAX)?;
            if !p
                .get("qtyLimit")
                .is_some_and(crate::common::is_positive_plain_decimal)
            {
                return Err(invalid("qtyLimit must be a positive plain decimal string"));
            }
        }
        "set_rfq_mmp_config" => {
            integer("timeInterval", 600000)?;
            integer("frozenInterval", u64::MAX)?;
            integer("countLimit", u64::MAX)?;
        }
        "set_rfq_cancel_all_after" => {
            let n = p
                .required("timeOut")?
                .parse::<u64>()
                .map_err(|_| invalid("invalid timeOut"))?;
            if n != 0 && !(10..=120).contains(&n) {
                return Err(invalid("timeOut must be 0 or 10..120 seconds"));
            }
        }
        "cancel_rfq_quote" => any(p, &["quoteId", "clQuoteId"])?,
        "cancel_rfq_batch_quotes" => {
            any(p, &["quoteIds", "clQuoteIds"])?;
            for key in ["quoteIds", "clQuoteIds"] {
                if let Some(raw) = p.get(key) {
                    let ids: Vec<String> = serde_json::from_str(raw)
                        .map_err(|_| invalid("quote IDs must be a string array"))?;
                    if ids.is_empty() || ids.iter().any(|s| s.trim().is_empty()) {
                        return Err(invalid("quote IDs must not be empty"));
                    }
                }
            }
        }
        "create_rfq_quote" => {
            enumeration(p, "quoteSide", &["buy", "sell"])?;
            if let Some(raw) = p.get("expiresIn")
                && !raw.parse::<u64>().is_ok_and(|n| (10..=120).contains(&n))
            {
                return Err(invalid("expiresIn must be 10..120 seconds"));
            }
            let legs: Value =
                serde_json::from_str(p.required("legs")?).map_err(|_| invalid("invalid legs"))?;
            let legs = legs
                .as_array()
                .filter(|a| !a.is_empty())
                .ok_or_else(|| invalid("legs must be a nonempty array"))?;
            for leg in legs {
                if !matches!(leg["side"].as_str(), Some("buy" | "sell")) {
                    return Err(invalid("leg.side must be buy or sell"));
                }
                if !leg["sz"]
                    .as_str()
                    .is_some_and(crate::common::is_positive_plain_decimal)
                {
                    return Err(invalid("leg.sz must be a positive plain decimal string"));
                }
            }
        }
        "set_rfq_maker_instrument_settings" => {
            enumeration(p, "instType", &["SPOT", "SWAP", "FUTURES", "OPTION"])?;
            let items: Value = serde_json::from_str(p.required("data")?)
                .map_err(|_| invalid("invalid maker settings data"))?;
            for item in items
                .as_array()
                .ok_or_else(|| invalid("data must be an array"))?
            {
                let key = if p.get("instType") == Some("SPOT") {
                    "instId"
                } else {
                    "instFamily"
                };
                if item[key].as_str().is_none_or(|s| s.trim().is_empty()) {
                    return Err(invalid(&format!("data item requires {key}")));
                }
            }
        }
        "create_withdrawal" | "create_fiat_withdrawal" => {
            let amount = p.required("amt")?;
            if !crate::common::is_positive_plain_decimal(amount) {
                return Err(invalid("amt must be a positive plain decimal string"));
            }
            if name == "create_fiat_withdrawal" {
                if amount
                    .split_once('.')
                    .is_some_and(|(_, decimal)| decimal.len() > 2)
                {
                    return Err(invalid("fiat amt supports at most two decimal places"));
                }
                enumeration(
                    p,
                    "paymentMethod",
                    &[
                        "TR_BANKS", "PIX", "SEPA", "XPULSE", "NPP", "US_WIRE", "SG_FAST",
                    ],
                )?;
            } else {
                enumeration(p, "dest", &["3", "4"])?;
                enumeration(p, "toAddrType", &["1", "2"])?;
                if p.get("toAddrType") == Some("2") && p.get("dest") != Some("3") {
                    return Err(invalid("toAddrType=2 requires dest=3"));
                }
                if let Some(raw) = p.get("rcvrInfo") {
                    let info: Value =
                        serde_json::from_str(raw).map_err(|_| invalid("invalid rcvrInfo"))?;
                    if !matches!(info["walletType"].as_str(), Some("exchange" | "private")) {
                        return Err(invalid("invalid rcvrInfo.walletType"));
                    }
                    if info["walletType"] == "exchange"
                        && info["exchId"].as_str().is_none_or(|s| s.trim().is_empty())
                    {
                        return Err(invalid("exchange wallet requires exchId"));
                    }
                }
            }
        }
        "get_glp_historical_performance" => {
            enumeration(p, "program", &["SPOT", "PERP", "FUT_NTO"])?
        }
        "get_mm_instrument_types" => enumeration(p, "instType", &["SPOT", "SWAP"])?,
        _ => {}
    }
    if name.starts_with("get_affiliate_") {
        if p.get("periodType") == Some("custom") {
            if name == "get_affiliate_invitee_detail" {
                return Err(invalid("custom period is unsupported for invitee detail"));
            }
            p.required("begin")?;
            p.required("end")?;
        }
        if p.get("joinTimeBegin").is_some() != p.get("joinTimeEnd").is_some() {
            return Err(invalid(
                "joinTimeBegin and joinTimeEnd must be provided together",
            ));
        }
    }
    Ok(())
}
pub(super) fn positive(p: &OkxParams, key: &str) -> Result<()> {
    if let Some(value) = p.get(key) {
        crate::exchanges::schema::encode(key, value, "decimal")?;
    }
    Ok(())
}

pub(super) fn any(p: &OkxParams, keys: &[&str]) -> Result<()> {
    if keys.iter().all(|k| p.get(k).is_none()) {
        return Err(invalid(&format!("one of {} is required", keys.join(", "))));
    }
    Ok(())
}
pub(super) fn list_limit(value: &str, max: usize) -> Result<()> {
    let values: Vec<_> = value.split(',').collect();
    if values.len() > max || values.iter().any(|v| v.trim().is_empty()) {
        return Err(invalid("currency/instrument list is empty or too long"));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    fn params(pairs: &[(&str, &str)]) -> OkxParams {
        OkxParams::from_pairs(
            pairs
                .iter()
                .map(|(k, v)| (k.to_string(), v.to_string()))
                .collect(),
        )
    }
    #[test]
    fn spread_prices_are_signed_but_sizes_are_positive() {
        validate(
            "amend_spread_order",
            &params(&[("ordId", "1"), ("newPx", "-2.5")]),
        )
        .unwrap();
        assert!(
            validate(
                "amend_spread_order",
                &params(&[("ordId", "1"), ("newSz", "-1")])
            )
            .is_err()
        );
    }
    #[test]
    fn rejects_invalid_market_pagination_and_modes() {
        assert!(validate("get_full_orderbook", &params(&[("sz", "5001")])).is_err());
        assert!(
            validate(
                "get_trades_history",
                &params(&[("type", "2"), ("before", "100")])
            )
            .is_err()
        );
        assert!(
            validate(
                "set_isolated_mode",
                &params(&[("isoMode", "auto_transfers_ccy"), ("type", "CONTRACTS")])
            )
            .is_err()
        );
    }
}
