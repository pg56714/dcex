//! Schema-driven request validation, encoding and dispatch.
use super::client::{BinanceClient, BinanceMarket};
use super::params::PublicParams;
#[path = "generated/schema_tables.rs"]
mod endpoints;
use crate::Result;
use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use endpoints::ENDPOINTS;

pub(super) struct Field {
    pub key: &'static str,
    pub kind: char,
    pub required: bool,
    pub choices: &'static [&'static str],
}
pub(super) struct Endpoint {
    pub name: &'static str,
    pub market: BinanceMarket,
    pub symbol_market: BinanceMarket,
    pub method: HttpMethod,
    pub path: &'static str,
    pub public: bool,
    pub api_key: bool,
    pub allowed: &'static [&'static str],
    pub fields: &'static [Field],
}
use crate::exchanges::binance::params::invalid;

impl BinanceClient {
    pub(super) async fn table_request(
        &self,
        name: &str,
        params: &PublicParams,
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

    pub(in crate::exchanges::binance) async fn table_request_transport(
        &self,
        name: &str,
        params: &PublicParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        let Some(endpoint) = ENDPOINTS
            .iter()
            .find(|e| e.name == name && e.public == public)
        else {
            return Ok(None);
        };
        params.ensure_allowed(endpoint.allowed)?;
        crate::exchanges::input_contracts::pairs("binance", name, &params.0)?;
        let singleton_keys: Vec<_> = params
            .0
            .iter()
            .filter(|(k, _)| !(name == "wallet_dust_transfer" && k == "asset"))
            .map(|(k, _)| k)
            .collect();
        let keys: std::collections::BTreeSet<_> = singleton_keys.iter().collect();
        if keys.len() != singleton_keys.len() {
            return Err(invalid("duplicate parameter"));
        }
        if params.get("product_symbol").is_some() && params.get("symbol").is_some() {
            return Err(invalid("use product_symbol or symbol, exclusively"));
        }
        let mut query = Vec::new();
        for field in endpoint.fields {
            if name == "wallet_dust_transfer" && field.key == "asset" {
                let assets: Vec<_> = params.0.iter().filter(|(key, _)| key == "asset").collect();
                if assets.is_empty() || assets.iter().any(|(_, value)| value.trim().is_empty()) {
                    return Err(invalid("asset must contain at least one nonempty asset"));
                }
                query.push((
                    "asset".into(),
                    assets
                        .into_iter()
                        .map(|(_, value)| value.as_str())
                        .collect::<Vec<_>>()
                        .join(","),
                ));
                continue;
            }
            let canonical = if field.key == "symbol" {
                params.get("product_symbol")
            } else {
                None
            };
            let Some(value) = canonical.or_else(|| params.get(field.key)) else {
                if field.required {
                    return Err(invalid(format!("{} is required", field.key)));
                }
                continue;
            };
            if value.trim().is_empty() {
                return Err(invalid(format!("{} cannot be empty", field.key)));
            }
            if !field.choices.is_empty() && !field.choices.contains(&value) {
                return Err(invalid(format!("invalid {}", field.key)));
            }
            if field.kind == 'd' {
                crate::exchanges::schema::encode(field.key, value, "decimal")?;
            }
            match field.kind {
                'i' => {
                    value.parse::<u64>().map_err(|_| {
                        invalid(format!("{} must be a nonnegative integer", field.key))
                    })?;
                }
                'd' => {
                    if !crate::common::is_positive_plain_decimal(value) {
                        return Err(invalid(format!("{} must be positive", field.key)));
                    }
                }
                'b' => {
                    value
                        .parse::<bool>()
                        .map_err(|_| invalid(format!("{} must be true or false", field.key)))?;
                }
                'j' => {
                    let items: Vec<serde_json::Value> = serde_json::from_str(value)
                        .map_err(|_| invalid("orderArgs must be a JSON array"))?;
                    if items.is_empty() || items.len() > 10 {
                        return Err(invalid("orderArgs must contain 1..10 positions"));
                    }
                    for (index, item) in items.iter().enumerate() {
                        let object = item
                            .as_object()
                            .ok_or_else(|| invalid("position must be an object"))?;
                        if object.len() != 3
                            || !object.keys().all(|k| {
                                matches!(k.as_str(), "symbol" | "quantity" | "positionSide")
                            })
                        {
                            return Err(invalid(
                                "position requires symbol, quantity and positionSide",
                            ));
                        }
                        let symbol = item["symbol"]
                            .as_str()
                            .filter(|s| {
                                !s.is_empty()
                                    && s.bytes().all(|b| b.is_ascii_alphanumeric() || b == b'-')
                            })
                            .ok_or_else(|| invalid("invalid position symbol"))?;
                        let quantity = item["quantity"]
                            .as_str()
                            .filter(|s| crate::common::is_positive_plain_decimal(s))
                            .ok_or_else(|| invalid("quantity must be a positive decimal string"))?;
                        let side = item["positionSide"]
                            .as_str()
                            .filter(|s| ["BOTH", "LONG", "SHORT"].contains(s))
                            .ok_or_else(|| invalid("invalid positionSide"))?;
                        for (key, value) in [
                            ("symbol", symbol),
                            ("quantity", quantity),
                            ("positionSide", side),
                        ] {
                            query.push((format!("orderArgs[{index}].{key}"), value.to_string()));
                        }
                    }
                    continue;
                }
                'a' => {
                    let values: Vec<String> = serde_json::from_str(value)
                        .map_err(|_| invalid("symbols must be a JSON string array"))?;
                    if values.is_empty() || values.iter().any(|s| s.trim().is_empty()) {
                        return Err(invalid("symbols must not be empty"));
                    }
                }
                _ => {}
            }
            let value = if let Some(canonical) = canonical {
                self.exchange_symbol_for(canonical, endpoint.symbol_market)?
            } else if field.key == "symbol" {
                self.exchange_symbol_for(value, endpoint.symbol_market)?
            } else {
                value.to_string()
            };
            if field.key == "symbol"
                && endpoint.symbol_market == BinanceMarket::CoinFutures
                && !value
                    .bytes()
                    .all(|b| b.is_ascii_uppercase() || b.is_ascii_digit() || b == b'_')
            {
                return Err(invalid(
                    "COIN-M requires a native symbol such as BTCUSD_PERP",
                ));
            }
            query.push((field.key.to_string(), value));
        }
        validate(endpoint, params)?;
        let response = if endpoint.api_key {
            self.api_key_request(endpoint.method, endpoint.market, endpoint.path, query)
                .await?
        } else {
            self.request(
                endpoint.method,
                endpoint.market,
                endpoint.path,
                query,
                !public,
            )
            .await?
        };
        Ok(Some(response))
    }
}

fn validate(endpoint: &Endpoint, p: &PublicParams) -> Result<()> {
    super::order_lists::validate(endpoint.path, p)?;
    p.ensure_time_order("startTime", "endTime")?;
    for key in ["limit", "size", "current", "page"] {
        if p.u64(key)? == Some(0) {
            return Err(invalid(format!("{key} must be positive")));
        }
    }
    if let Some(value) = p.get("recvWindow")
        && (!value
            .parse::<f64>()
            .is_ok_and(|n| n.is_finite() && n > 0.0 && n <= 60_000.0)
            || value
                .split_once('.')
                .is_some_and(|(_, fraction)| fraction.len() > 3))
    {
        return Err(invalid(
            "recvWindow must be at most 60000 milliseconds with up to three decimals",
        ));
    }
    if endpoint.name == "set_options_cancel_countdown" {
        let countdown = p
            .u64("countdownTime")?
            .ok_or_else(|| invalid("countdownTime is required"))?;
        if countdown != 0 && countdown < 5000 {
            return Err(invalid(
                "countdownTime must be 0 or at least 5000 milliseconds",
            ));
        }
    }
    if endpoint.name == "send_options_cancel_heartbeat" {
        let value = p.required("underlyings")?;
        if value.split(',').any(|s| {
            s.is_empty()
                || !s
                    .bytes()
                    .all(|b| b.is_ascii_uppercase() || b.is_ascii_digit())
        }) {
            return Err(invalid(
                "underlyings must be comma-separated native asset symbols",
            ));
        }
    }
    if endpoint.name == "set_options_mmp_config" {
        p.optional_u64_range("windowTimeInMilliseconds", 0, 5000)?;
        for key in ["qtyLimit", "deltaLimit"] {
            if !crate::common::is_positive_plain_decimal(p.required(key)?) {
                return Err(invalid(format!(
                    "{key} must be a positive plain decimal string"
                )));
            }
        }
    }
    let path = endpoint.path;
    if path.ends_with("/capital/deposit/subAddress")
        && p.get("network") == Some("LIGHTNING")
        && p.get("amount").is_none()
    {
        return Err(invalid("amount is required for LIGHTNING deposits"));
    }
    if path.ends_with("/sub-account/subAccountApi") && endpoint.method == HttpMethod::Post {
        match p.get("status") {
            Some("1") => {}
            Some("2") if p.get("ipAddress").is_some() => {}
            Some("3") if p.get("thirdPartyName").is_some() => {}
            _ => {
                return Err(invalid(
                    "status must be 1, 2 with ipAddress, or 3 with thirdPartyName",
                ));
            }
        }
    }

    if path.starts_with("/sapi/v1/algo/") {
        if endpoint.method == HttpMethod::Delete
            && p.get("algoId").is_none()
            && p.get("clientAlgoId").is_none()
        {
            return Err(invalid("algoId or clientAlgoId is required"));
        }
        if let Some(duration) = p.u64("duration")?
            && path.contains("/futures/")
            && !(300..=86_400).contains(&duration)
        {
            return Err(invalid("futures TWAP duration must be 300..86400 seconds"));
        }
        if p.get("positionSide")
            .is_some_and(|s| matches!(s, "LONG" | "SHORT"))
            && p.get("reduceOnly").is_some()
        {
            return Err(invalid("reduceOnly cannot be supplied in hedge mode"));
        }
        if p.u64("pageSize")? == Some(0) {
            return Err(invalid("pageSize must be positive"));
        }
    }
    if (path.ends_with("/openOrder") || path.ends_with("/orderAmendment"))
        && p.get("orderId").is_none()
        && p.get("origClientOrderId").is_none()
    {
        return Err(invalid("orderId or origClientOrderId is required"));
    }
    if path.ends_with("/convert/getQuote") {
        if p.get("fromAmount").is_some() == p.get("toAmount").is_some() {
            return Err(invalid(
                "exactly one of fromAmount and toAmount is required",
            ));
        }
        p.optional_one_of("validTime", &["10s"])?;
        if p.get("fromAsset") == p.get("toAsset") {
            return Err(invalid("conversion assets must differ"));
        }
    }
    if path.ends_with("/convert/orderStatus")
        && p.get("orderId").is_none()
        && p.get("quoteId").is_none()
    {
        return Err(invalid("orderId or quoteId is required"));
    }
    if path.ends_with("/manual-liquidation") && p.get("type") == Some("ISOLATED") {
        p.required("symbol")?;
    }
    if path.ends_with("/max-leverage") {
        p.optional_one_of("maxLeverage", &["3", "5", "10", "20"])?;
    }
    if path == "/sapi/v1/margin/myPreventedMatches" {
        if p.get("orderId").is_some() == p.get("preventedMatchId").is_some() {
            return Err(invalid(
                "exactly one of orderId and preventedMatchId is required",
            ));
        }
        if p.get("fromPreventedMatchId").is_some() && p.get("orderId").is_none() {
            return Err(invalid("fromPreventedMatchId requires orderId"));
        }
    }
    if path.ends_with("/feeBurn") {
        p.optional_one_of("feeBurn", &["true", "false"])?;
    }
    if path == "/sapi/v1/bnbBurn" && endpoint.method == HttpMethod::Post {
        if p.get("spotBNBBurn").is_none() && p.get("interestBNBBurn").is_none() {
            return Err(invalid("spotBNBBurn or interestBNBBurn is required"));
        }
        p.optional_one_of("spotBNBBurn", &["true", "false"])?;
        p.optional_one_of("interestBNBBurn", &["true", "false"])?;
    }
    if path == "/sapi/v1/capital/deposit/credit-apply"
        && p.get("depositId").is_none()
        && p.get("txId").is_none()
    {
        return Err(invalid("depositId or txId is required"));
    }
    if path.starts_with("/sapi/v1/asset/dust") {
        p.optional_one_of("accountType", &["SPOT", "MARGIN"])?;
    }
    if path.starts_with("/api/v3/sor/order") {
        if p.get("type") == Some("LIMIT") {
            p.required("price")?;
            p.required("timeInForce")?;
        }
        if p.get("icebergQty").is_some() && p.get("timeInForce") != Some("GTC") {
            return Err(invalid("icebergQty requires GTC"));
        }
        if p.u64("strategyType")?.is_some_and(|n| n < 1_000_000) {
            return Err(invalid("strategyType must be at least 1000000"));
        }
    }
    let symbol = p.get("product_symbol").or_else(|| p.get("symbol"));
    if symbol.is_some() && (p.get("symbols").is_some() || p.get("pair").is_some()) {
        return Err(invalid("symbol cannot be combined with symbols or pair"));
    }
    if path.ends_with("/multiAssetsMargin") {
        p.optional_one_of("multiAssetsMargin", &["true", "false"])?;
    }
    if path.ends_with("/positionMargin") {
        p.optional_one_of("type", &["1", "2"])?;
        p.optional_one_of("positionSide", &["BOTH", "LONG", "SHORT"])?;
    }
    if path.ends_with("/aggTrades") && endpoint.market != BinanceMarket::Spot {
        if p.get("fromId").is_some() && (p.get("startTime").is_some() || p.get("endTime").is_some())
        {
            return Err(invalid(
                "aggregate trades require fromId or time filters, exclusively",
            ));
        }
        if let (Some(start), Some(end)) = (p.u64("startTime")?, p.u64("endTime")?)
            && end - start >= 3_600_000
        {
            return Err(invalid(
                "aggregate trade time range must be less than one hour",
            ));
        }
    }
    let max_days = match path {
        "/papi/v1/cm/income"
        | "/dapi/v1/continuousKlines"
        | "/dapi/v1/indexPriceKlines"
        | "/dapi/v1/markPriceKlines" => Some(200),
        "/papi/v1/margin/marginInterestHistory"
        | "/papi/v1/margin/marginLoan"
        | "/papi/v1/margin/repayLoan" => Some(30),
        "/sapi/v1/margin/capital-flow" => Some(7),
        _ => None,
    };
    if let (Some(days), Some(start), Some(end)) = (max_days, p.u64("startTime")?, p.u64("endTime")?)
        && end - start > days * 86_400_000
    {
        return Err(invalid(
            "time range exceeds this endpoint's documented limit",
        ));
    }
    if path == "/sapi/v1/capital/deposit/hisrec"
        && let (Some(start), Some(end)) = (p.u64("startTime")?, p.u64("endTime")?)
        && end - start >= 90 * 86_400_000
    {
        return Err(invalid("deposit history range must be less than 90 days"));
    }
    if path == "/sapi/v1/capital/deposit/address" && p.get("network") == Some("LIGHTNING") {
        p.required("amount")?;
    }
    if matches!(
        path,
        "/papi/v1/margin/marginLoan" | "/papi/v1/margin/repayLoan"
    ) && p.get("txId").is_none()
        && p.get("startTime").is_none()
    {
        return Err(invalid("txId or startTime is required"));
    }
    if matches!(
        path,
        "/sapi/v1/margin/orderList"
            | "/sapi/v1/margin/allOrderList"
            | "/sapi/v1/margin/openOrderList"
    ) && p.get("isIsolated") == Some("TRUE")
        && symbol.is_none()
    {
        return Err(invalid("isolated order-list requests require symbol"));
    }
    if path == "/sapi/v1/margin/orderList" {
        let client_key = if endpoint.method == HttpMethod::Delete {
            "listClientOrderId"
        } else {
            "origClientOrderId"
        };
        if p.get("orderListId").is_none() && p.get(client_key).is_none() {
            return Err(invalid(format!("orderListId or {client_key} is required")));
        }
    }
    if path == "/sapi/v1/margin/allOrderList"
        && p.get("fromId").is_some()
        && (p.get("startTime").is_some() || p.get("endTime").is_some())
    {
        return Err(invalid("fromId cannot be combined with time filters"));
    }
    Ok(())
}

mod field_schemas;

mod request_tables;
