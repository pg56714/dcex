//! Ordinary account, margin trading and market-risk endpoints.
use serde_json::Value;

use super::client::BitgetClient;
use super::params::BitgetParams;
use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

#[path = "risk_endpoints.rs"]
mod endpoints;

pub(super) struct Endpoint {
    path: &'static str,
    post: bool,
    public: bool,
    fields: &'static [&'static str],
    required: &'static [&'static str],
    arrays: &'static [&'static str],
    limit: Option<u64>,
    days: Option<u64>,
}

impl BitgetClient {
    pub(super) async fn risk_request(
        &self,
        name: &str,
        params: &BitgetParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        let Some(endpoint) = endpoints::endpoint(name) else {
            return Ok(None);
        };
        if endpoint.public != public {
            return Ok(None);
        }
        params.ensure_allowed(endpoint.fields, endpoint.fields.contains(&"symbol"))?;
        if params.get("symbol").is_some() && params.get("product_symbol").is_some() {
            return Err(invalid("symbol and product_symbol are mutually exclusive"));
        }
        for key in endpoint.required {
            if *key == "symbol" {
                symbol(params)?;
            } else {
                required(params, key)?;
            }
        }
        for key in endpoint.fields {
            if params.get(key).is_some() {
                required(params, key)?;
            }
        }
        validate(name, params, &endpoint)?;
        if name == "batch_create_classic_sub_accounts" {
            let body: Value = serde_json::from_str(required(params, "accounts")?)
                .map_err(|_| invalid("invalid accounts JSON"))?;
            let accounts = body
                .as_array()
                .ok_or_else(|| invalid("accounts must be an array"))?;
            if accounts.is_empty() || accounts.len() > 5 {
                return Err(invalid("accounts must contain 1..5 entries"));
            }
            let mut seen = std::collections::HashSet::new();
            for account in accounts {
                let object = account
                    .as_object()
                    .ok_or_else(|| invalid("account must be an object"))?;
                if object.keys().any(|k| {
                    ![
                        "subAccountName",
                        "passphrase",
                        "label",
                        "permList",
                        "ipList",
                    ]
                    .contains(&k.as_str())
                }) {
                    return Err(invalid("unknown sub-account field"));
                }
                let name = account["subAccountName"].as_str().unwrap_or_default();
                if name.len() != 8
                    || !name.bytes().all(|c| c.is_ascii_alphabetic())
                    || !seen.insert(name)
                {
                    return Err(invalid(
                        "sub-account names must be unique eight-letter aliases",
                    ));
                }
                validate_passphrase(account["passphrase"].as_str().unwrap_or_default())?;
                let label = account["label"]
                    .as_str()
                    .ok_or_else(|| invalid("label is required"))?;
                if label.is_empty() || label.chars().count() > 20 {
                    return Err(invalid("label must contain 1..20 characters"));
                }
                validate_string_list(
                    &account["permList"],
                    "permList",
                    4,
                    &["read", "spot_trade", "margin_trade", "contract_trade"],
                )?;
                if let Some(ips) = account.get("ipList") {
                    validate_string_list(ips, "ipList", 30, &[])?;
                }
            }
            return self.post_private(endpoint.path, body).await.map(Some);
        }
        let mut pairs = params.only(endpoint.fields);
        if let Some(value) = params.get("product_symbol") {
            pairs.retain(|(key, _)| key != "symbol");
            pairs.push(("symbol".into(), self.exchange_symbol(value)?));
        }
        if !endpoint.post {
            return Ok(Some(if public {
                self.public_get(endpoint.path, pairs).await?
            } else {
                self.get_private(endpoint.path, pairs).await?
            }));
        }
        let mut body = serde_json::Map::new();
        for (key, value) in pairs {
            if name == "move_uta_positions" && key == "positionList" {
                let value: Value = serde_json::from_str(&value)
                    .map_err(|_| invalid("invalid positionList JSON"))?;
                let items = value
                    .as_array()
                    .ok_or_else(|| invalid("positionList must be an array"))?;
                if items.is_empty() || items.len() > 10 {
                    return Err(invalid("positionList must contain 1..10 entries"));
                }
                for item in items {
                    let object = item
                        .as_object()
                        .ok_or_else(|| invalid("position must be an object"))?;
                    if object.len() != 3
                        || object
                            .keys()
                            .any(|k| !["symbol", "side", "qty"].contains(&k.as_str()))
                        || !item["symbol"].as_str().is_some_and(|v| !v.is_empty())
                        || !matches!(item["side"].as_str(), Some("buy" | "sell"))
                        || !item["qty"]
                            .as_str()
                            .and_then(|v| v.parse::<f64>().ok())
                            .is_some_and(|v| v.is_finite() && v > 0.0)
                    {
                        return Err(invalid(
                            "position requires native symbol, buy/sell side and positive decimal qty",
                        ));
                    }
                }
                body.insert(key, value);
            } else if endpoint.arrays.contains(&key.as_str()) {
                let value: Value =
                    serde_json::from_str(&value).map_err(|_| invalid("expected a JSON array"))?;
                let items = value
                    .as_array()
                    .ok_or_else(|| invalid("expected a JSON array"))?;
                if items.is_empty() || items.len() > 100 {
                    return Err(invalid("list must contain 1 to 100 entries"));
                }
                let items = items
                    .iter()
                    .map(|item| {
                        let text = item
                            .as_str()
                            .filter(|text| !text.trim().is_empty())
                            .ok_or_else(|| invalid("list entries must be nonempty strings"))?;
                        Ok(Value::String(if key == "symbolList" {
                            self.exchange_symbol(text)?
                        } else {
                            text.to_string()
                        }))
                    })
                    .collect::<Result<Vec<_>>>()?;
                body.insert(key, Value::Array(items));
            } else {
                body.insert(key, Value::String(value));
            }
        }
        Ok(Some(
            self.post_private(endpoint.path, Value::Object(body))
                .await?,
        ))
    }
}

fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(format!("Bitget: {message}"))
}
fn validate_passphrase(value: &str) -> Result<()> {
    if !(8..=32).contains(&value.len())
        || !value.bytes().all(|b| b.is_ascii_alphanumeric())
        || !value.bytes().any(|b| b.is_ascii_alphabetic())
        || !value.bytes().any(|b| b.is_ascii_digit())
    {
        return Err(invalid("passphrase requires 8..32 letters and digits"));
    }
    Ok(())
}
fn validate_string_list(value: &Value, key: &str, max: usize, choices: &[&str]) -> Result<()> {
    let items = value
        .as_array()
        .ok_or_else(|| invalid(&format!("{key} must be an array")))?;
    let mut seen = std::collections::HashSet::new();
    if items.is_empty() || items.len() > max {
        return Err(invalid(&format!("invalid {key} list length")));
    }
    for item in items {
        let text = item
            .as_str()
            .filter(|s| !s.trim().is_empty())
            .ok_or_else(|| invalid("list entries must be nonempty strings"))?;
        if !seen.insert(text) || (!choices.is_empty() && !choices.contains(&text)) {
            return Err(invalid(&format!("duplicate or unsupported {key}")));
        }
    }
    Ok(())
}
fn required<'a>(params: &'a BitgetParams, key: &str) -> Result<&'a str> {
    params
        .get(key)
        .filter(|value| !value.trim().is_empty())
        .ok_or_else(|| invalid(&format!("{key} is required")))
}
fn symbol(params: &BitgetParams) -> Result<&str> {
    params
        .get("product_symbol")
        .or_else(|| params.get("symbol"))
        .filter(|value| !value.trim().is_empty())
        .ok_or_else(|| invalid("product_symbol or symbol is required"))
}
fn choices(params: &BitgetParams, key: &str, choices: &[&str]) -> Result<()> {
    if params
        .get(key)
        .is_some_and(|value| !choices.contains(&value))
    {
        return Err(invalid(&format!("unsupported {key}")));
    }
    Ok(())
}
fn integer(params: &BitgetParams, key: &str) -> Result<Option<u64>> {
    params
        .get(key)
        .map(|value| {
            value
                .parse()
                .map_err(|_| invalid(&format!("{key} must be an unsigned integer")))
        })
        .transpose()
}
fn positive(params: &BitgetParams, key: &str) -> Result<()> {
    if let Some(value) = params.get(key) {
        let number: f64 = value
            .parse()
            .map_err(|_| invalid(&format!("{key} must be a positive decimal")))?;
        if !number.is_finite() || number <= 0.0 {
            return Err(invalid(&format!("{key} must be a positive decimal")));
        }
    }
    Ok(())
}

fn validate(name: &str, params: &BitgetParams, endpoint: &Endpoint) -> Result<()> {
    if endpoint.path.contains("rate-limit-quota") {
        choices(params, "category", &["spot", "futures"])?;
        if params
            .get("quota")
            .is_some_and(|v| !v.parse::<u64>().is_ok_and(|n| n > 0))
        {
            return Err(invalid("quota must be a positive integer"));
        }
    }
    if name == "move_uta_positions" {
        choices(params, "category", &["USDT-FUTURES", "USDC-FUTURES"])?;
        if params.get("fromUid") == params.get("toUid") {
            return Err(invalid("source and target accounts must differ"));
        }
    }
    if endpoint.path.ends_with("/quoted-price")
        && params.get("fromCoinSize").is_some() == params.get("toCoinSize").is_some()
    {
        return Err(invalid("provide exactly one conversion amount"));
    }
    if endpoint.path.contains("/convert/") {
        for key in ["fromCoinSize", "toCoinSize", "cnvtPrice"] {
            positive(params, key)?;
        }
        if params.get("fromCoin").is_some() && params.get("fromCoin") == params.get("toCoin") {
            return Err(invalid("conversion coins must differ"));
        }
    }
    if name.starts_with("uta_") || name.starts_with("classic_") {
        if let Some(value) = params.get("passphrase") {
            validate_passphrase(value)?;
        }
        if name == "uta_freeze_sub" {
            choices(params, "operation", &["freeze", "unfreeze"])?;
        }
        if name.contains("sub_api") {
            choices(params, "type", &["read_only", "read_write"])?;
        }
        if name.contains("virtual_subaccount") {
            choices(params, "status", &["normal", "freeze"])?;
        }
    }
    for (key, max, choices) in [
        ("permissions", 2, &["uta_mgt", "uta_trade"][..]),
        (
            "permList",
            4,
            &["read", "spot_trade", "margin_trade", "contract_trade"][..],
        ),
        ("ips", 30, &[][..]),
        ("ipList", 30, &[][..]),
        ("uids", 50, &[][..]),
    ] {
        if endpoint.arrays.contains(&key) {
            if let Some(value) = params.get(key) {
                let value: Value =
                    serde_json::from_str(value).map_err(|_| invalid("invalid list JSON"))?;
                validate_string_list(&value, key, max, choices)?;
            }
        }
    }
    if name == "classic_create_virtual_subaccount" {
        let names: Vec<String> = serde_json::from_str(required(params, "subAccountList")?)
            .map_err(|_| invalid("subAccountList must be a string array"))?;
        if names
            .iter()
            .any(|v| v.len() != 8 || !v.bytes().all(|c| c.is_ascii_alphabetic()))
        {
            return Err(invalid(
                "virtual aliases must contain eight English letters",
            ));
        }
    }
    choices(params, "deduct", &["on", "off"])?;
    if name == "create_uta_sub_account" {
        let username = required(params, "username")?;
        if username.len() > 20 || !username.bytes().all(|b| b.is_ascii_lowercase()) {
            return Err(invalid("username must contain 1..20 lowercase letters"));
        }
        if params.get("note").is_some_and(|s| s.chars().count() > 50) {
            return Err(invalid("note must not exceed 50 characters"));
        }
        choices(params, "accountMode", &["classic", "unified"])?;
    }
    if name == "set_uta_deposit_account" {
        choices(params, "accountType", &["funding", "unified", "otc"])?;
    }
    if name == "set_spot_deposit_account" {
        choices(
            params,
            "accountType",
            &[
                "spot",
                "funding",
                "coin-futures",
                "usdt-futures",
                "usdc-futures",
            ],
        )?;
    }
    if name == "get_uta_cash_dividend_records" {
        choices(params, "type", &["pending", "paid"])?;
    }
    if name == "get_uta_futures_long_short_ratio" {
        choices(
            params,
            "period",
            &["5m", "15m", "30m", "1h", "2h", "4h", "6h", "12h", "1d"],
        )?;
    }
    if name.contains("risk_reserve") {
        choices(
            params,
            "category",
            &["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"],
        )?;
        if endpoint.fields.contains(&"marginCoin") && params.get("category") == Some("COIN-FUTURES")
        {
            required(params, "marginCoin")?;
        }
    }
    if name.ends_with("margin_liquidation_orders") {
        choices(params, "type", &["swap", "place_order"])?;
    }
    if matches!(
        name,
        "get_deposit_address" | "get_sub_account_deposit_address"
    ) && params.get("size").is_some_and(|s| {
        !s.parse::<f64>()
            .is_ok_and(|n| n.is_finite() && (0.000001..=0.001).contains(&n))
    }) {
        return Err(invalid("Lightning size must be between 0.000001 and 0.001"));
    }
    for (key, values) in [
        (
            "productType",
            &["USDT-FUTURES", "USDC-FUTURES", "COIN-FUTURES"][..],
        ),
        (
            "category",
            &[
                "SPOT",
                "MARGIN",
                "USDT-FUTURES",
                "USDC-FUTURES",
                "COIN-FUTURES",
            ][..],
        ),
        ("orderType", &["limit", "market"][..]),
        ("side", &["buy", "sell"][..]),
        ("posSide", &["long", "short"][..]),
        ("holdSide", &["long", "short"][..]),
        ("autoMargin", &["on", "off"][..]),
        ("assetMode", &["single", "union"][..]),
        (
            "loanType",
            &["normal", "autoLoan", "autoRepay", "autoLoanAndRepay"][..],
        ),
        ("force", &["gtc", "post_only", "fok", "ioc"][..]),
        (
            "stpMode",
            &["none", "cancel_taker", "cancel_maker", "cancel_both"][..],
        ),
        ("collateralType", &["mainstream", "all", "custom"][..]),
        ("allowCashplus", &["yes", "no"][..]),
        ("autoBorrow", &["yes", "no"][..]),
        ("allowBorrow", &["yes", "no"][..]),
        ("role", &["initiator", "receiver"][..]),
        ("repayMode", &["auto", "manual"][..]),
    ] {
        if key != "category" || !endpoint.path.contains("rate-limit-quota") {
            choices(params, key, values)?;
        }
    }
    for key in [
        "price",
        "size",
        "openAmount",
        "openPrice",
        "leverage",
        "amount",
        "borrowAmount",
        "repayAmount",
        "baseSize",
        "quoteSize",
    ] {
        positive(params, key)?;
    }
    for key in ["limit", "pageSize", "pageNum"] {
        if let Some(value) = integer(params, key)? {
            if value == 0
                || (key != "pageNum" && endpoint.limit.is_some_and(|maximum| value > maximum))
            {
                return Err(invalid(&format!("{key} is outside the documented range")));
            }
        }
    }
    let start = integer(params, "startTime")?;
    let end = integer(params, "endTime")?;
    if let (Some(start), Some(end)) = (start, end) {
        if end < start
            || endpoint
                .days
                .is_some_and(|days| end - start > days * 86_400_000)
        {
            return Err(invalid("time range exceeds the documented bounds"));
        }
    }
    if name == "get_futures_liquidation_price" || name == "get_futures_max_open_quantity" {
        if params.get("orderType") == Some("limit") {
            required(params, "openPrice")?;
        }
    }
    if name == "get_uta_max_open_available" && params.get("orderType") == Some("limit") {
        required(params, "price")?;
    }
    if name == "set_uta_collateral_type" && params.get("collateralType") == Some("custom") {
        required(params, "collateralCoins")?;
    }
    if name == "set_uta_account_mode" {
        choices(params, "mode", &["basic", "advanced", "isolated"])?;
        choices(params, "deltaSwitch", &["yes", "no"])?;
        if params.get("deltaSwitch").is_some() && params.get("mode") != Some("advanced") {
            return Err(invalid("deltaSwitch requires advanced mode"));
        }
    }
    if name == "get_all_trade_rates" {
        choices(params, "businessType", &["mix", "spot", "margin"])?;
    }
    if name == "transfer_spot_sub_account" {
        for key in ["fromType", "toType"] {
            choices(
                params,
                key,
                &[
                    "spot",
                    "p2p",
                    "coin_futures",
                    "usdt_futures",
                    "usdc_futures",
                    "crossed_margin",
                    "isolated_margin",
                ],
            )?;
            if params.get(key) == Some("isolated_margin") {
                symbol(params)?;
            }
        }
    }
    if name.starts_with("transfer_uta_") || name == "get_uta_transferable_coins" {
        for key in ["fromType", "toType"] {
            let types: &[&str] = if name == "transfer_uta_sub_to_master" {
                if key == "fromType" {
                    &["spot", "uta"]
                } else {
                    &["spot", "p2p", "uta"]
                }
            } else if name == "transfer_uta_sub_account" {
                &[
                    "spot",
                    "p2p",
                    "coin_futures",
                    "usdt_futures",
                    "usdc_futures",
                    "crossed_margin",
                    "uta",
                ]
            } else {
                &[
                    "spot",
                    "p2p",
                    "coin_futures",
                    "usdt_futures",
                    "usdc_futures",
                    "crossed_margin",
                    "isolated_margin",
                    "uta",
                ]
            };
            choices(params, key, types)?;
            if name == "transfer_uta_account" && params.get(key) == Some("isolated_margin") {
                symbol(params)?;
            }
        }
        if params
            .get("clientOid")
            .is_some_and(|value| value.len() > 64)
        {
            return Err(invalid("clientOid allows at most 64 characters"));
        }
    }
    if name.contains("_margin_") {
        for key in ["borrowAmount", "repayAmount"] {
            if let Some(value) = params.get(key) {
                if value.matches('.').count() > 1
                    || !value.chars().all(|c| c.is_ascii_digit() || c == '.')
                    || value
                        .split_once('.')
                        .is_some_and(|(_, decimals)| decimals.len() > 8)
                {
                    return Err(invalid(
                        "borrowAmount and repayAmount allow at most 8 decimal places",
                    ));
                }
            }
        }
        if name.starts_with("place_") && name.ends_with("_order") {
            if params.get("orderType") == Some("limit") {
                required(params, "price")?;
                required(params, "baseSize")?;
            } else if params.get("side") == Some("buy") {
                required(params, "quoteSize")?;
            } else {
                required(params, "baseSize")?;
            }
        }
        if name.starts_with("cancel_")
            && !["orderId", "clientOid"]
                .iter()
                .any(|key| params.get(key).is_some_and(|v| !v.is_empty()))
        {
            return Err(invalid("orderId or clientOid is required"));
        }
    }
    Ok(())
}

pub(super) fn validate_margin_order_fields(params: &BitgetParams) -> Result<()> {
    let endpoint = endpoints::endpoint("place_cross_margin_order").expect("margin order metadata");
    params.ensure_allowed(endpoint.fields, true)?;
    for key in endpoint.required {
        if *key == "symbol" {
            symbol(params)?;
        } else {
            required(params, key)?;
        }
    }
    validate("place_cross_margin_order", params, &endpoint)
}
