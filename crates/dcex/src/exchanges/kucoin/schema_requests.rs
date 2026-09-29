//! Schema-driven request validation, encoding and dispatch.
use super::client::{KucoinClient, KucoinMarket};
use super::params::{KucoinParams, bool_value, validate_client_oid, validate_positive_number};
use crate::Result;
use crate::exchange::ValidatedResponse;
use crate::exchanges::kucoin::params::invalid;
use crate::http::HttpMethod;
use serde_json::Value;

#[path = "generated/schema_tables.rs"]
mod endpoints;

pub(super) struct Field {
    key: &'static str,
    kind: char,
    required: bool,
    path: bool,
    choices: &'static [&'static str],
    minimum: Option<i64>,
    maximum: Option<i64>,
}
pub(super) struct Endpoint {
    path: &'static str,
    method: HttpMethod,
    market: KucoinMarket,
    public: bool,
    fields: &'static [Field],
}

impl KucoinClient {
    pub(super) async fn table_request(
        &self,
        name: &str,
        params: &KucoinParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        match crate::exchanges::schema::fund_domain(name) {
            Some(crate::exchanges::schema::FundDomain::Withdrawals) => {
                self.withdrawals_table_request(name, params, public).await
            }
            Some(crate::exchanges::schema::FundDomain::Transfers) => {
                self.transfers_table_request(name, params, public).await
            }
            None => self.table_request_transport(name, params, public).await,
        }
    }

    pub(in crate::exchanges::kucoin) async fn table_request_transport(
        &self,
        name: &str,
        params: &KucoinParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        let Some(endpoint) = endpoints::endpoint(name) else {
            return Ok(None);
        };
        if endpoint.public != public {
            return Ok(None);
        }
        let mut allowed: Vec<_> = endpoint.fields.iter().map(|field| field.key).collect();
        if allowed.contains(&"symbol") {
            allowed.push("product_symbol");
        }
        params.ensure_allowed(&allowed)?;
        let supplied = params.only(&allowed);
        crate::exchanges::input_contracts::pairs("kucoin", name, &supplied)?;
        if supplied
            .iter()
            .map(|(k, _)| k)
            .collect::<std::collections::BTreeSet<_>>()
            .len()
            != supplied.len()
        {
            return Err(invalid("duplicate parameter"));
        }
        if params.get("product_symbol").is_some() && params.get("symbol").is_some() {
            return Err(invalid("provide either symbol or product_symbol"));
        }
        let futures_symbol = endpoint.market == KucoinMarket::Futures
            || params.get("tradeType") == Some("FUTURES")
            || matches!(
                name,
                "get_uta_current_funding_rates"
                    | "get_uta_funding_rate_history"
                    | "get_uta_index_prices"
                    | "get_uta_interest_rate_index"
            );
        let mut path = endpoint.path.to_string();
        let mut query = Vec::new();
        let mut body = serde_json::Map::new();
        for field in endpoint.fields {
            let input = if field.key == "symbol" {
                params.get_any(&["product_symbol", "symbol"])
            } else {
                params.get(field.key)
            };
            let Some(input) = input else {
                if field.required {
                    return Err(invalid(format!("{} is required", field.key)));
                }
                continue;
            };
            if input.trim().is_empty() {
                return Err(invalid(format!("{} must not be empty", field.key)));
            }
            if !field.choices.is_empty() && !field.choices.contains(&input) {
                return Err(invalid(format!("unsupported {}", field.key)));
            }
            if field.kind == 'd' {
                crate::exchanges::schema::encode(field.key, input, "decimal")?;
            }
            let mut text = input.to_string();
            let value = match field.kind {
                'i' => {
                    let number: i64 = input
                        .parse()
                        .map_err(|_| invalid(format!("{} must be an integer", field.key)))?;
                    if field.minimum.is_some_and(|minimum| number < minimum)
                        || field.maximum.is_some_and(|maximum| number > maximum)
                    {
                        return Err(invalid(format!(
                            "{} is outside its documented range",
                            field.key
                        )));
                    }
                    Value::Number(number.into())
                }
                'b' => {
                    let value = bool_value(input).ok_or_else(|| invalid("expected a boolean"))?;
                    text = value.to_string();
                    Value::Bool(value)
                }
                'd' => {
                    validate_positive_number(params, field.key)?;
                    let number: serde_json::Number = serde_json::from_str(input)
                        .map_err(|_| invalid("amount must be a JSON decimal number"))?;
                    Value::Number(number)
                }
                'a' => {
                    let value: Value = serde_json::from_str(input)
                        .map_err(|_| invalid("expected a JSON array"))?;
                    let items = value
                        .as_array()
                        .filter(|a| !a.is_empty())
                        .ok_or_else(|| invalid("array must not be empty"))?;
                    if endpoint.method != HttpMethod::Post {
                        for item in items {
                            let item = item
                                .as_str()
                                .filter(|s| !s.is_empty())
                                .ok_or_else(|| invalid("query arrays require nonempty strings"))?;
                            query.push((field.key.to_string(), item.to_string()));
                        }
                        continue;
                    }
                    value
                }
                _ => {
                    // Native index/mark-price suffixes are not canonical product symbols.
                    if field.key == "symbol"
                        && params.get("product_symbol").is_some()
                        && canonical(input)
                    {
                        text = self.exchange_symbol(input, futures_symbol)?;
                    }
                    if matches!(
                        field.key,
                        "accountSubtype" | "fromAccountTag" | "toAccountTag"
                    ) && canonical(input)
                    {
                        text = self.exchange_symbol(input, false)?;
                    }
                    Value::String(text.clone())
                }
            };
            if field.path {
                let encoded: String =
                    url::form_urlencoded::byte_serialize(text.as_bytes()).collect();
                path = path.replace(&format!("{{{}}}", field.key), &encoded);
            } else if endpoint.method == HttpMethod::Post {
                body.insert(field.key.to_string(), value);
            } else {
                query.push((field.key.to_string(), text));
            }
        }
        validate(name, params)?;
        let response = if endpoint.method == HttpMethod::Post {
            self.private_post(endpoint.market, path, Value::Object(body))
                .await?
        } else {
            self.request(endpoint.method, endpoint.market, path, query, None, !public)
                .await?
        };
        Ok(Some(response))
    }
}

fn canonical(symbol: &str) -> bool {
    symbol.ends_with("-SPOT") || symbol.ends_with("-SWAP") || symbol.ends_with("-PERP")
}

fn validate(name: &str, params: &KucoinParams) -> Result<()> {
    if matches!(name, "get_convert_quote" | "get_convert_limit_quote")
        && params.get("fromCurrencySize").is_some() == params.get("toCurrencySize").is_some()
    {
        return Err(invalid("exactly one source or target amount is required"));
    }
    if matches!(
        name,
        "get_convert_order_detail"
            | "get_convert_limit_order_detail"
            | "cancel_convert_limit_order"
    ) {
        params.required_any(&["orderId", "clientOrderId"])?;
    }
    if let Some(id) = params.get("clientOrderId")
        && (id.len() > 40
            || !id
                .bytes()
                .all(|b| b.is_ascii_alphanumeric() || matches!(b, b'_' | b'-')))
    {
        return Err(invalid(
            "clientOrderId must contain at most 40 letters, digits, underscores or hyphens",
        ));
    }
    if let (Some(from), Some(to)) = (params.get("fromCurrency"), params.get("toCurrency"))
        && from == to
    {
        return Err(invalid("conversion currencies must differ"));
    }
    if name == "set_uta_rate_limit" {
        let value = params.json_required("list")?;
        let items = value
            .as_array()
            .filter(|a| !a.is_empty())
            .ok_or_else(|| invalid("list must be a nonempty array"))?;
        let mut seen = std::collections::BTreeSet::new();
        for item in items {
            let item = item
                .as_object()
                .filter(|o| o.len() == 2)
                .ok_or_else(|| invalid("rate entry requires uid and rate"))?;
            let uid = item
                .get("uid")
                .and_then(Value::as_str)
                .filter(|s| !s.is_empty())
                .ok_or_else(|| invalid("uid must be a nonempty string"))?;
            if !seen.insert(uid)
                || item
                    .get("rate")
                    .and_then(Value::as_u64)
                    .is_none_or(|n| n == 0)
            {
                return Err(invalid(
                    "rate must be a positive integer and uid must be unique",
                ));
            }
        }
    }
    if name == "add_uta_sub_account" {
        let password = params.required("password")?;
        if !(7..=24).contains(&password.len())
            || !password.bytes().all(|b| b.is_ascii_alphanumeric())
            || !password.bytes().any(|b| b.is_ascii_alphabetic())
            || !password.bytes().any(|b| b.is_ascii_digit())
        {
            return Err(invalid("password requires 7..24 letters and digits"));
        }
        let sub = params.required("subName")?;
        if !(7..=32).contains(&sub.chars().count())
            || sub.chars().any(char::is_whitespace)
            || !sub.bytes().any(|b| b.is_ascii_alphabetic())
            || !sub.bytes().any(|b| b.is_ascii_digit())
        {
            return Err(invalid(
                "subName requires 7..32 characters, including letters and digits, without spaces",
            ));
        }
        if params
            .required("access")?
            .split(',')
            .any(|v| !matches!(v, "Spot" | "Futures" | "Margin"))
        {
            return Err(invalid("access supports Spot, Futures and Margin"));
        }
    }
    if name.contains("sub_account_api") {
        if let Some(pass) = params.get("passphrase")
            && (!(7..=32).contains(&pass.chars().count()) || pass.chars().any(char::is_whitespace))
        {
            return Err(invalid(
                "passphrase requires 7..32 characters without spaces",
            ));
        }
        if params.get("remark").is_some_and(|s| s.chars().count() > 24) {
            return Err(invalid("remark must not exceed 24 characters"));
        }
        if let Some(ips) = params.get("ipWhitelist")
            && (ips.split(',').count() > 20
                || ips
                    .split(',')
                    .any(|ip| ip.parse::<std::net::IpAddr>().is_err()))
        {
            return Err(invalid(
                "ipWhitelist requires at most 20 valid IP addresses",
            ));
        }
    }
    for (start_key, end_key) in [("startAt", "endAt"), ("startTime", "endTime")] {
        let start = params
            .get(start_key)
            .map(|v| {
                v.parse::<u64>()
                    .map_err(|_| invalid("start time must be a nonnegative integer"))
            })
            .transpose()?;
        let end = params
            .get(end_key)
            .map(|v| {
                v.parse::<u64>()
                    .map_err(|_| invalid("end time must be a nonnegative integer"))
            })
            .transpose()?;
        if let (Some(start), Some(end)) = (start, end)
            && start > end
        {
            return Err(invalid("start time must not exceed end time"));
        }
    }
    if name == "get_uta_account_ledgers" {
        let maximum = match params.get("accountType") {
            Some("UNIFIED" | "SPOT") => 200,
            Some("FUTURES") => 100,
            _ => 500,
        };
        if let Some(size) = params.get("pageSize") {
            let size: u64 = size
                .parse()
                .map_err(|_| invalid("pageSize must be an integer"))?;
            if size == 0 || size > maximum {
                return Err(invalid("pageSize exceeds this account type's limit"));
            }
        }
    }
    if matches!(
        name,
        "get_spot_account_ledgers"
            | "get_spot_hf_account_ledgers"
            | "get_margin_hf_account_ledgers"
    ) && params
        .get("currency")
        .is_some_and(|v| v.split(',').count() > 10 || v.split(',').any(|v| v.trim().is_empty()))
    {
        return Err(invalid("currency accepts at most 10 nonempty codes"));
    }
    if name == "get_uta_klines" {
        if params.get("tradeType") == Some("SPOT")
            && params.get("klineType").is_some_and(|kind| kind != "TRADE")
        {
            return Err(invalid("spot klines only support TRADE"));
        }
        if params.get("tradeType") == Some("FUTURES")
            && matches!(params.get("interval"), Some("6hour" | "3day"))
        {
            return Err(invalid("interval is not supported for futures"));
        }
    }
    if name == "get_uta_orderbook"
        && params.get("rpiFilter").is_some()
        && params.get("tradeType") != Some("FUTURES")
    {
        return Err(invalid("rpiFilter requires FUTURES"));
    }
    if name == "get_uta_transfer_quota" && params.get("accountType") == Some("ISOLATED") {
        params.required_any(&["product_symbol", "symbol"])?;
    }
    if name == "get_classic_account_balances_v2" && params.get("accountType") == Some("ISOLATED") {
        params.required("accountSubtype")?;
    }
    if name == "get_margin_currency_risk_limits" {
        if params
            .get("isIsolated")
            .and_then(bool_value)
            .unwrap_or(false)
        {
            params.required_any(&["product_symbol", "symbol"])?;
        } else {
            params.required("currency")?;
        }
    }
    if name == "transfer_uta_accounts" {
        validate_positive_number(params, "amount")?;
        validate_client_oid(params, "clientOid")?;
        match params.get("transferType") {
            Some("PARENT_TO_SUB") => {
                params.required("toUid")?;
            }
            Some("SUB_TO_PARENT") => {
                params.required("fromUid")?;
            }
            Some("SUB_TO_SUB") => {
                params.required("fromUid")?;
                params.required("toUid")?;
            }
            _ => {}
        }
        for (kind, tag) in [
            ("fromAccountType", "fromAccountTag"),
            ("toAccountType", "toAccountTag"),
        ] {
            if params.get(kind) == Some("ISOLATED") && params.get(tag) == Some("DEFAULT") {
                return Err(invalid("isolated account tags require the trading pair"));
            }
        }
    }
    Ok(())
}

mod request_tables;
