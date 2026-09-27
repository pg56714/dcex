//! Ordinary V5 account, risk, conversion and market endpoints.
use super::{client::BybitClient, params::BybitParams};
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};
use serde_json::{Map, Value};

#[path = "risk_endpoints.rs"]
mod endpoints;
struct RiskEndpoint {
    path: &'static str,
    post: bool,
    public: bool,
    keys: &'static [&'static str],
    required: &'static [&'static str],
    integers: &'static [&'static str],
}

impl BybitClient {
    pub(super) async fn risk_request(
        &self,
        name: &str,
        params: &BybitParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        let Some(endpoint) = endpoints::endpoint(name) else {
            return Ok(None);
        };
        if public != endpoint.public {
            return Ok(None);
        }
        let pairs = params.without(&[]);
        let mut seen = std::collections::HashSet::new();
        for (key, value) in &pairs {
            if !endpoint.keys.contains(&key.as_str())
                || !seen.insert(key)
                || value.trim().is_empty()
            {
                return Err(invalid("unknown, duplicate or empty parameter"));
            }
        }
        for key in endpoint.required {
            if *key == "symbol" {
                params
                    .get("product_symbol")
                    .or(params.get("symbol"))
                    .ok_or_else(|| invalid("symbol is required"))?;
            } else {
                params.required(key)?;
            }
        }
        if params.get("product_symbol").is_some() && params.get("symbol").is_some() {
            return Err(invalid("provide only one symbol parameter"));
        }
        let mut query = params.only(
            &endpoint
                .keys
                .iter()
                .copied()
                .filter(|k| *k != "product_symbol")
                .collect::<Vec<_>>(),
        );
        if let Some(product) = params.get("product_symbol") {
            query.push(("symbol".into(), self.exchange_symbol(product)?));
        }
        for key in endpoint.integers {
            if let Some(v) = params.get(key) {
                v.parse::<u64>()
                    .map_err(|_| invalid("integer parameters must be nonnegative"))?;
            }
        }
        validate(name, params)?;
        let response = if endpoint.post {
            let mut body = Map::new();
            for (key, value) in query {
                let value = if endpoint.integers.contains(&key.as_str()) {
                    Value::from(
                        value
                            .parse::<u64>()
                            .map_err(|_| invalid("invalid integer"))?,
                    )
                } else if matches!(
                    key.as_str(),
                    "request" | "list" | "fromCoinList" | "permissions"
                ) {
                    params.json_required(&key)?
                } else if matches!(key.as_str(), "modifyEnable" | "agree") {
                    Value::Bool(
                        value
                            .parse::<bool>()
                            .map_err(|_| invalid("boolean parameter must be true or false"))?,
                    )
                } else {
                    Value::String(value)
                };
                body.insert(key, value);
            }
            self.post_request(endpoint.path, body).await
        } else {
            self.request(HttpMethod::Get, endpoint.path, query, None, !public)
                .await
        };
        response.map(Some)
    }
}

fn validate(name: &str, p: &BybitParams) -> Result<()> {
    if name == "submit_deposit_information" {
        let questionnaire = p.required("questionnaire")?;
        if questionnaire.len() > 16_384
            || !serde_json::from_str::<Value>(questionnaire).is_ok_and(|v| v.is_object())
        {
            return Err(invalid(
                "questionnaire must be a JSON object string of at most 16384 bytes",
            ));
        }
    }
    if name == "set_api_rate_limits" {
        let value = p.json_required("list")?;
        let items = value
            .as_array()
            .filter(|v| !v.is_empty())
            .ok_or_else(|| invalid("list must be a nonempty array"))?;
        for item in items {
            if item.as_object().is_none_or(|v| {
                v.len() != 3
                    || v.keys()
                        .any(|k| !matches!(k.as_str(), "uids" | "bizType" | "rate"))
            }) || !item["uids"]
                .as_str()
                .is_some_and(|s| !s.is_empty() && s.split(',').all(|v| v.parse::<u64>().is_ok()))
                || !item["bizType"]
                    .as_str()
                    .is_some_and(|s| ["SPOT", "DERIVATIVES", "OPTIONS"].contains(&s))
                || !item["rate"].as_u64().is_some_and(|n| n > 0)
            {
                return Err(invalid(
                    "rate limit entries require UIDs, bizType and a positive integer rate",
                ));
            }
        }
    }
    for key in ["page", "index", "size", "pageSize"] {
        if let Some(v) = p.get(key) {
            if !v
                .parse::<u64>()
                .is_ok_and(|n| n > 0 && (!matches!(key, "size" | "pageSize") || n <= 100))
            {
                return Err(invalid("invalid pagination value"));
            }
        }
    }
    if name == "get_fee_group_info" && p.required("productType")? != "contract" {
        return Err(invalid("productType must be contract"));
    }
    if name == "get_option_base_coins"
        && p.get("underlyingType").is_some_and(|v| {
            v.split(',')
                .any(|v| !matches!(v, "0" | "1" | "2" | "3" | "4"))
        })
    {
        return Err(invalid("invalid underlyingType"));
    }
    if matches!(
        name,
        "get_small_balance_coins" | "request_small_balance_quote"
    ) && p.required("accountType")? != "eb_convert_uta"
    {
        return Err(invalid("small balance conversion requires eb_convert_uta"));
    }
    if name == "request_small_balance_quote" {
        if !matches!(p.required("toCoin")?, "MNT" | "USDT" | "USDC") {
            return Err(invalid("toCoin must be MNT, USDT or USDC"));
        }
        let value = p.json_required("fromCoinList")?;
        let coins = value
            .as_array()
            .filter(|v| !v.is_empty() && v.len() <= 20)
            .ok_or_else(|| invalid("fromCoinList requires 1..20 coins"))?;
        let mut seen = std::collections::HashSet::new();
        for coin in coins {
            let coin = coin
                .as_str()
                .filter(|v| !v.is_empty() && *v == v.to_uppercase())
                .ok_or_else(|| invalid("coins must be uppercase strings"))?;
            if !seen.insert(coin) || Some(coin) == p.get("toCoin") {
                return Err(invalid("duplicate source coin or source equals target"));
            }
        }
    }
    if let Some(value) = p.get("permissions") {
        let value: Value =
            serde_json::from_str(value).map_err(|_| invalid("permissions must be an object"))?;
        let obj = value
            .as_object()
            .filter(|v| !v.is_empty())
            .ok_or_else(|| invalid("permissions must be a nonempty object"))?;
        for value in obj.values() {
            if !value
                .as_array()
                .is_some_and(|a| a.iter().all(|v| v.as_str().is_some_and(|s| !s.is_empty())))
            {
                return Err(invalid("permission values must be string arrays"));
            }
        }
    }
    for key in ["readOnly", "frozen", "switch"] {
        if p.get(key).is_some_and(|v| !matches!(v, "0" | "1")) {
            return Err(invalid("invalid binary setting"));
        }
    }
    if name == "create_sub_account" {
        let username = p.required("username")?;
        if !(6..=16).contains(&username.len())
            || !username.bytes().all(|b| b.is_ascii_alphanumeric())
            || !username.bytes().any(|b| b.is_ascii_alphabetic())
            || !username.bytes().any(|b| b.is_ascii_digit())
        {
            return Err(invalid("username requires 6..16 letters and digits"));
        }
        if !matches!(p.required("memberType")?, "1" | "6") {
            return Err(invalid("memberType must be 1 or 6"));
        }
        if let Some(password) = p.get("password") {
            if !(8..=30).contains(&password.len())
                || !password.bytes().any(|b| b.is_ascii_uppercase())
                || !password.bytes().any(|b| b.is_ascii_lowercase())
                || !password.bytes().any(|b| b.is_ascii_digit())
            {
                return Err(invalid(
                    "password requires 8..30 characters with upper/lowercase letters and digits",
                ));
            }
        }
    }
    if name == "sign_trading_agreement"
        && (p.get("agree") != Some("true") || !matches!(p.get("categoryV2"), Some("1" | "2")))
    {
        return Err(invalid(
            "agreement requires agree=true and categoryV2=1 or 2",
        ));
    }
    if name == "get_pre_upgrade_order_history" {
        if p.get("startTime").is_some() != p.get("endTime").is_some() {
            return Err(invalid("startTime and endTime must be supplied together"));
        }
        if p.get("category") == Some("spot") && p.get("orderStatus").is_some() {
            return Err(invalid(
                "orderStatus is not supported for pre-upgrade spot history",
            ));
        }
    }
    if let Some(category) = p.get("category") {
        let categories: &[&str] = match name {
            "get_account_instruments"
            | "get_full_orderbook"
            | "get_rpi_orderbook"
            | "set_price_limit_behavior" => &["spot", "linear", "inverse"],
            "get_closed_option_positions" => &["option"],
            "get_option_delivery_prices" | "get_pre_upgrade_delivery_records" => &["option"],
            "get_pre_upgrade_executions" | "get_pre_upgrade_order_history" => {
                &["spot", "linear", "inverse", "option"]
            }
            "get_pre_upgrade_transaction_log" => &["linear", "option"],
            "get_pre_upgrade_settlement_records" => &["linear"],
            "get_move_position_history" => &["spot", "linear", "inverse", "option"],
            "get_delivery_records" => &["linear", "inverse", "option"],
            "get_settlement_records" => &["linear"],
            _ => &["linear", "inverse"],
        };
        if !categories.contains(&category) {
            return Err(invalid("unsupported category"));
        }
    }
    if let Some(limit) = p.get("limit") {
        let max = match name {
            "get_all_api_rate_limits" => 1000,
            "get_account_instruments" | "get_move_position_history" => 200,
            "get_funding_account_history"
            | "get_closed_option_positions"
            | "get_convert_history"
            | "get_pre_upgrade_closed_pnl"
            | "get_pre_upgrade_executions" => 100,
            "get_sub_account_api_keys" => 20,
            "get_announcements" => u64::MAX,
            _ => 50,
        };
        if !limit.parse::<u64>().is_ok_and(|n| (1..=max).contains(&n)) {
            return Err(invalid("limit is outside the documented range"));
        }
    }
    if let (Some(start), Some(end)) = (p.get("startTime"), p.get("endTime")) {
        let start = start
            .parse::<u64>()
            .map_err(|_| invalid("invalid startTime"))?;
        let end = end.parse::<u64>().map_err(|_| invalid("invalid endTime"))?;
        if start > end
            || matches!(name, "get_delivery_records" | "get_settlement_records")
                && end - start > 30 * 86_400_000
        {
            return Err(invalid("invalid history time range"));
        }
        if matches!(
            name,
            "get_closed_option_positions" | "get_move_position_history"
        ) && end - start > 7 * 86_400_000
        {
            return Err(invalid("history time range must not exceed seven days"));
        }
        if name.starts_with("get_pre_upgrade_") && end - start > 7 * 86_400_000 {
            return Err(invalid(
                "pre-upgrade history range must not exceed seven days",
            ));
        }
    }
    if name == "set_delta_mode" && !matches!(p.get("deltaEnable"), Some("0" | "1")) {
        return Err(invalid("deltaEnable must be 0 or 1"));
    }
    if name == "set_spot_hedging" && !matches!(p.get("setHedgingMode"), Some("ON" | "OFF")) {
        return Err(invalid("setHedgingMode must be ON or OFF"));
    }
    if name == "get_move_position_history"
        && p.get("status")
            .is_some_and(|v| !matches!(v, "Processing" | "Filled" | "Rejected"))
    {
        return Err(invalid("invalid move position status"));
    }
    if name == "move_positions" {
        if p.required("fromUid")? == p.required("toUid")? {
            return Err(invalid("fromUid and toUid must differ"));
        }
        let value = p.json_required("list")?;
        let legs = value
            .as_array()
            .filter(|v| !v.is_empty() && v.len() <= 25)
            .ok_or_else(|| invalid("move positions requires 1..25 legs"))?;
        for leg in legs {
            let obj = leg.as_object().filter(|v| v.len() == 5).ok_or_else(|| {
                invalid("each leg requires category, symbol, price, side and qty")
            })?;
            if !obj
                .get("category")
                .and_then(Value::as_str)
                .is_some_and(|v| matches!(v, "spot" | "linear" | "inverse" | "option"))
                || !obj
                    .get("side")
                    .and_then(Value::as_str)
                    .is_some_and(|v| matches!(v, "Buy" | "Sell"))
            {
                return Err(invalid("invalid move leg category or side"));
            }
            if !obj
                .get("symbol")
                .and_then(Value::as_str)
                .is_some_and(|v| !v.is_empty() && v == v.to_uppercase())
            {
                return Err(invalid("move leg symbol must be uppercase"));
            }
            for key in ["price", "qty"] {
                if !obj
                    .get(key)
                    .and_then(Value::as_str)
                    .and_then(|v| v.parse::<f64>().ok())
                    .is_some_and(|v| v.is_finite() && v > 0.0)
                {
                    return Err(invalid(
                        "move leg price and qty must be positive decimal strings",
                    ));
                }
            }
        }
    }
    if name == "get_funding_account_history" {
        match (p.get("createTimeFrom"), p.get("createTimeTo")) {
            (Some(start), Some(end)) => {
                let start = start
                    .parse::<u64>()
                    .map_err(|_| invalid("invalid createTimeFrom seconds"))?;
                let end = end
                    .parse::<u64>()
                    .map_err(|_| invalid("invalid createTimeTo seconds"))?;
                if start > end || end - start > 7 * 86_400 {
                    return Err(invalid("funding history range must not exceed seven days"));
                }
            }
            (None, None) => {}
            _ => {
                return Err(invalid(
                    "createTimeFrom and createTimeTo must be provided together",
                ));
            }
        }
    }
    if name == "set_collateral_coin" {
        validate_collateral(p.required("coin")?, p.required("collateralSwitch")?)?;
    }
    if name == "batch_set_collateral_coins" {
        let value = p.json_required("request")?;
        let items = value
            .as_array()
            .filter(|v| !v.is_empty())
            .ok_or_else(|| invalid("request must be a nonempty array"))?;
        let mut coins = std::collections::HashSet::new();
        for item in items {
            let o = item
                .as_object()
                .filter(|o| o.len() == 2)
                .ok_or_else(|| invalid("each request requires coin and collateralSwitch"))?;
            let coin = o
                .get("coin")
                .and_then(Value::as_str)
                .ok_or_else(|| invalid("coin is required"))?;
            let switch = o
                .get("collateralSwitch")
                .and_then(Value::as_str)
                .ok_or_else(|| invalid("collateralSwitch is required"))?;
            validate_collateral(coin, switch)?;
            if !coins.insert(coin) {
                return Err(invalid("duplicate collateral coin"));
            }
        }
    }
    if name == "request_convert_quote" {
        if p.required("requestCoin")? != p.required("fromCoin")?
            || p.required("fromCoin")? == p.required("toCoin")?
        {
            return Err(invalid(
                "requestCoin must equal fromCoin, and toCoin must differ",
            ));
        }
        if !p
            .required("requestAmount")?
            .parse::<f64>()
            .is_ok_and(|n| n.is_finite() && n > 0.0)
        {
            return Err(invalid("requestAmount must be positive"));
        }
        for key in ["fromCoinType", "toCoinType"] {
            if p.get(key).is_some_and(|v| v != "crypto") {
                return Err(invalid("coin type must be crypto"));
            }
        }
        if p.get("requestId").is_some_and(|v| v.len() > 36) {
            return Err(invalid("requestId must not exceed 36 characters"));
        }
    }
    Ok(())
}

fn validate_collateral(coin: &str, switch: &str) -> Result<()> {
    if coin.is_empty()
        || coin != coin.to_uppercase()
        || matches!(coin, "USDT" | "USDC")
        || !matches!(switch, "ON" | "OFF")
    {
        return Err(invalid(
            "collateral coin must be uppercase and configurable; switch must be ON/OFF",
        ));
    }
    Ok(())
}
fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(format!("Bybit: {message}"))
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn rejects_invalid_collateral_and_history_intervals() {
        for (name, pairs) in [
            (
                "set_collateral_coin",
                vec![("coin", "USDT"), ("collateralSwitch", "OFF")],
            ),
            (
                "batch_set_collateral_coins",
                vec![(
                    "request",
                    r#"[{"coin":"BTC","collateralSwitch":"ON"},{"coin":"BTC","collateralSwitch":"OFF"}]"#,
                )],
            ),
            (
                "get_funding_account_history",
                vec![("createTimeFrom", "1700000000")],
            ),
            (
                "get_funding_account_history",
                vec![
                    ("createTimeFrom", "1700000000"),
                    ("createTimeTo", "1700604801"),
                ],
            ),
            ("get_account_instruments", vec![("limit", "201")]),
        ] {
            let params = BybitParams::from_pairs(
                pairs
                    .into_iter()
                    .map(|(k, v)| (k.into(), v.into()))
                    .collect(),
            );
            assert!(validate(name, &params).is_err(), "{name}");
        }
    }
}
