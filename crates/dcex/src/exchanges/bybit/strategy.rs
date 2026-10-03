//! Exchange-managed TWAP, chase, iceberg and POV strategies.
use serde_json::{Map, Value};

use super::client::BybitClient;
use super::params::{BybitParams, insert_optional_bool, insert_optional_i64};
use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

const CATEGORIES: &[&str] = &[
    "UTA_USDT",
    "UTA_USDC",
    "UTA_SPOT",
    "UTA_INVERSE",
    "UTA_INVERSE_FUTURE",
    "UTA_USDT_FUTURE",
];
const TYPES: &[&str] = &["twap", "chaseOrder", "iceberg", "pov"];
const STRINGS: &[&str] = &[
    "category",
    "side",
    "strategyType",
    "size",
    "positionValue",
    "triggerPrice",
    "maxChasePrice",
    "chaseDistance",
    "subSize",
    "subPositionValue",
    "limitPrice",
];
const INTEGERS: &[&str] = &[
    "duration",
    "interval",
    "positionIdx",
    "leverageType",
    "chasePercentE4",
    "orderCount",
    "postOnly",
];
const BOOLEANS: &[&str] = &["reduceOnly", "isRandom"];

impl BybitClient {
    fn strategy_exchange_symbol(&self, symbol: &str, category: Option<&str>) -> Result<String> {
        if let Some((native, _)) = self.loaded_strategy_symbol(symbol, category)? {
            return Ok(native);
        }
        self.exchange_symbol(symbol)
    }

    fn strategy_category(&self, symbol: &str, requested: Option<&str>) -> Result<String> {
        if let Some((_, category)) = self.loaded_strategy_symbol(symbol, requested)? {
            return Ok(category);
        }
        let parts: Vec<_> = symbol.split('-').collect();
        if parts.len() == 1 {
            let category =
                requested.ok_or_else(|| invalid("category is required for native symbols"))?;
            return Ok(category.into());
        }
        let market = self.category_for_product_symbol(symbol, "linear")?;
        let derived = match (market.as_str(), parts.as_slice()) {
            ("spot", [_, _, "SPOT"]) => "UTA_SPOT",
            ("inverse", [_, "USD", "SWAP"]) => "UTA_INVERSE",
            ("inverse", [_, "USD", _, "SWAP"]) => "UTA_INVERSE_FUTURE",
            ("linear", [_, "USDT", "SWAP"]) => "UTA_USDT",
            ("linear", [_, "USDC", "SWAP"]) => "UTA_USDC",
            ("linear", [_, "USDT", _, "SWAP"]) => "UTA_USDT_FUTURE",
            _ => return Err(invalid("unsupported strategy product symbol/category")),
        };
        if requested.is_some_and(|category| category != derived) {
            return Err(invalid("category does not match product_symbol"));
        }
        Ok(derived.into())
    }

    pub(super) async fn strategy_private_request(
        &self,
        name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match name {
            "create_strategy" => {
                let mut allowed = [STRINGS, INTEGERS, BOOLEANS].concat();
                allowed.extend(["product_symbol", "symbol", "povParams", "maker_only"]);
                ensure_allowed(params, &allowed)?;
                let symbol = params
                    .get("product_symbol")
                    .or_else(|| params.get("symbol"))
                    .ok_or_else(|| invalid("product_symbol or symbol is required"))?;
                if params.get("product_symbol").is_some() && params.get("symbol").is_some() {
                    return Err(invalid("provide only one symbol parameter"));
                }
                let category = self.strategy_category(symbol, params.get("category"))?;
                let mut normalized = params.without(&["category", "maker_only"]);
                normalized.push(("category".into(), category));
                if let Some(maker_only) = params.get("maker_only") {
                    if params.get("postOnly").is_some() {
                        return Err(invalid(
                            "maker_only and deprecated postOnly are mutually exclusive",
                        ));
                    }
                    let value = match maker_only {
                        "true" => "0",
                        "false" => "1",
                        _ => return Err(invalid("maker_only must be boolean")),
                    };
                    normalized.push(("postOnly".into(), value.into()));
                }
                let normalized = BybitParams::from_pairs(normalized);
                let params = &normalized;
                required_enum(params, "category", CATEGORIES)?;
                if params.get("chaseDistance").is_some() && params.get("chasePercentE4").is_some() {
                    return Err(invalid(
                        "chaseDistance and chasePercentE4 are mutually exclusive",
                    ));
                }
                if ["subSize", "subPositionValue", "orderCount"]
                    .iter()
                    .filter(|key| params.get(key).is_some())
                    .count()
                    > 1
                {
                    return Err(invalid(
                        "subSize, subPositionValue and orderCount are mutually exclusive",
                    ));
                }
                required_enum(params, "side", &["Buy", "Sell"])?;
                required_enum(params, "strategyType", TYPES)?;
                let strategy = params.required("strategyType")?;
                let has_size = params.get("size").is_some();
                let has_value = params.get("positionValue").is_some();
                if has_size && has_value || strategy != "pov" && !has_size && !has_value {
                    return Err(invalid("provide exactly one of size or positionValue"));
                }
                for key in [
                    "size",
                    "positionValue",
                    "subSize",
                    "subPositionValue",
                    "triggerPrice",
                    "maxChasePrice",
                    "limitPrice",
                ] {
                    if let Some(value) = params.get(key) {
                        positive(value, key)?;
                    }
                }
                range(params, "positionIdx", 0, 2)?;
                range(params, "leverageType", 0, 1)?;
                if params.get("leverageType").is_some()
                    && params.get("category") != Some("UTA_SPOT")
                {
                    return Err(invalid("leverageType is only supported for UTA_SPOT"));
                }
                match strategy {
                    "twap" => {
                        params.required("duration")?;
                        range(params, "duration", 300, 86_400)?;
                        let interval = params
                            .get("interval")
                            .unwrap_or("30")
                            .parse::<i64>()
                            .map_err(|_| invalid("invalid interval"))?;
                        if ![5, 10, 15, 30, 60, 120].contains(&interval)
                            || params.i64_required("duration")? % interval != 0
                        {
                            return Err(invalid(
                                "TWAP duration must be divisible by an allowed interval",
                            ));
                        }
                    }
                    "chaseOrder" => {
                        range(params, "chasePercentE4", 0, 500)?;
                    }
                    "iceberg" => {
                        range(params, "orderCount", 1, 200)?;
                        range(params, "postOnly", 0, 1)?;
                        range(params, "chasePercentE4", 0, 100)?;
                        if ["subSize", "subPositionValue", "orderCount"]
                            .iter()
                            .all(|key| params.get(key).is_none())
                        {
                            return Err(invalid(
                                "iceberg requires subSize, subPositionValue or orderCount",
                            ));
                        }
                    }
                    "pov" => {
                        range(params, "duration", 900, 86_400)?;
                        if let Some(interval) = params.get("interval") {
                            let interval = interval
                                .parse::<i64>()
                                .map_err(|_| invalid("invalid interval"))?;
                            if interval != 0 && !(5..=3600).contains(&interval) {
                                return Err(invalid("POV interval must be 0 or 5..=3600"));
                            }
                        }
                        if !has_size
                            && !has_value
                            && params.get("duration").is_none()
                            && params.get("interval") != Some("0")
                        {
                            return Err(invalid(
                                "POV requires a size, value, duration or one-time stop condition",
                            ));
                        }
                        validate_pov(&params.json_required("povParams")?)?;
                    }
                    _ => unreachable!(),
                }
                let specific: &[&str] = match strategy {
                    "twap" => &[
                        "duration",
                        "interval",
                        "isRandom",
                        "triggerPrice",
                        "maxChasePrice",
                        "chaseDistance",
                        "chasePercentE4",
                    ],
                    "chaseOrder" => &[
                        "chaseDistance",
                        "chasePercentE4",
                        "triggerPrice",
                        "maxChasePrice",
                    ],
                    "iceberg" => &[
                        "subSize",
                        "subPositionValue",
                        "orderCount",
                        "postOnly",
                        "maxChasePrice",
                        "limitPrice",
                        "chaseDistance",
                        "chasePercentE4",
                    ],
                    _ => &["duration", "interval", "povParams"],
                };
                let common = [
                    "category",
                    "side",
                    "strategyType",
                    "size",
                    "positionValue",
                    "reduceOnly",
                    "positionIdx",
                    "leverageType",
                    "symbol",
                    "product_symbol",
                ];
                ensure_allowed(params, &[&common[..], specific].concat())?;
                let mut body = Map::new();
                for key in STRINGS {
                    if let Some(value) = params.get(key) {
                        body.insert((*key).into(), Value::String(value.into()));
                    }
                }
                for key in INTEGERS {
                    insert_optional_i64(&mut body, key, params.get(key))?;
                }
                for key in BOOLEANS {
                    insert_optional_bool(&mut body, key, params.get(key))?;
                }
                if strategy == "pov" {
                    body.insert("povParams".into(), params.json_required("povParams")?);
                }
                let symbol = params
                    .get("product_symbol")
                    .or_else(|| params.get("symbol"))
                    .ok_or_else(|| invalid("product_symbol or symbol is required"))?;
                body.insert(
                    "symbol".into(),
                    Value::String(self.strategy_exchange_symbol(symbol, params.get("category"))?),
                );
                self.post_request("/v5/strategy/create", body).await
            }
            "stop_strategy" => {
                ensure_allowed(params, &["strategyId"])?;
                let id = params.required("strategyId")?;
                self.post_request(
                    "/v5/strategy/stop",
                    Map::from_iter([("strategyId".into(), Value::String(id.into()))]),
                )
                .await
            }
            "get_strategy_list" | "get_strategy_orders" => {
                let orders = name == "get_strategy_orders";
                let mut allowed = vec![
                    "strategyId",
                    "symbol",
                    "product_symbol",
                    "status",
                    "strategyType",
                    "beginTimeE0",
                    "endTimeE0",
                    "pageSize",
                    "cursor",
                ];
                if orders {
                    params.required("strategyId")?;
                } else {
                    allowed.push("category");
                }
                ensure_allowed(params, &allowed)?;
                if params.get("strategyType").is_some() {
                    required_enum(params, "strategyType", TYPES)?;
                }
                if params.get("category").is_some() {
                    let mut categories = CATEGORIES.to_vec();
                    categories.push("UTA_USDC_FUTURE");
                    required_enum(params, "category", &categories)?;
                }
                if params.get("status").is_some() {
                    required_enum(
                        params,
                        "status",
                        if orders {
                            &["2", "3", "4", "5", "6", "7"]
                        } else {
                            &["2", "3", "4", "5", "6"]
                        },
                    )?;
                }
                range(params, "pageSize", 1, if orders { i64::MAX } else { 50 })?;
                range(params, "beginTimeE0", 0, i64::MAX)?;
                range(params, "endTimeE0", 0, i64::MAX)?;
                if params.get("beginTimeE0").is_some()
                    && params.get("endTimeE0").is_some()
                    && params.i64_required("beginTimeE0")? > params.i64_required("endTimeE0")?
                {
                    return Err(invalid("beginTimeE0 must not exceed endTimeE0"));
                }
                let mut query = params.without(&["product_symbol", "symbol"]);
                if let Some(symbol) = params
                    .get("product_symbol")
                    .or_else(|| params.get("symbol"))
                {
                    query.push((
                        "symbol".into(),
                        self.strategy_exchange_symbol(symbol, params.get("category"))?,
                    ));
                }
                self.get_request(
                    if orders {
                        "/v5/strategy/order-list"
                    } else {
                        "/v5/strategy/list"
                    },
                    query,
                )
                .await
            }
            _ => return Ok(None),
        };
        result.map(Some)
    }
}

fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(message.into())
}
fn ensure_allowed(params: &BybitParams, keys: &[&str]) -> Result<()> {
    if let Some((key, _)) = params.without(keys).first() {
        return Err(invalid(&format!("unsupported strategy parameter: {key}")));
    }
    if params
        .only(keys)
        .iter()
        .any(|(_, value)| value.trim().is_empty())
    {
        return Err(invalid("strategy parameters must not be empty"));
    }
    Ok(())
}
fn required_enum(params: &BybitParams, key: &str, values: &[&str]) -> Result<()> {
    if !values.contains(&params.required(key)?) {
        return Err(invalid(&format!("unsupported {key}")));
    }
    Ok(())
}
fn range(params: &BybitParams, key: &str, min: i64, max: i64) -> Result<()> {
    if params.get(key).is_some() && !(min..=max).contains(&params.i64_required(key)?) {
        return Err(invalid(&format!("{key} must be {min}..={max}")));
    }
    Ok(())
}
fn positive(value: &str, key: &str) -> Result<()> {
    if !value.parse::<f64>().is_ok_and(|v| v.is_finite() && v > 0.0) {
        return Err(invalid(&format!("{key} must be positive")));
    }
    Ok(())
}
fn validate_pov(value: &Value) -> Result<()> {
    let object = value
        .as_object()
        .ok_or_else(|| invalid("povParams must be an object"))?;
    if object.keys().any(|key| {
        ![
            "mode",
            "participationRate",
            "referenceWindow",
            "depthReference",
        ]
        .contains(&key.as_str())
    }) {
        return Err(invalid("unsupported povParams field"));
    }
    let rate = object
        .get("participationRate")
        .and_then(Value::as_str)
        .ok_or_else(|| invalid("participationRate must be a decimal string"))?;
    if !rate
        .parse::<f64>()
        .is_ok_and(|n| (1.0..=100.0).contains(&n))
        || rate
            .split_once('.')
            .is_some_and(|(_, digits)| digits.len() > 1)
    {
        return Err(invalid(
            "participationRate must be 1..=100 with at most one decimal",
        ));
    }
    match object.get("mode").and_then(Value::as_str) {
        Some("TradedVolume") => {
            let window = object
                .get("referenceWindow")
                .and_then(Value::as_str)
                .and_then(|s| s.parse::<u64>().ok());
            if !window.is_some_and(|v| (60..=14_400).contains(&v)) {
                return Err(invalid(
                    "referenceWindow must be a string integer from 60 to 14400",
                ));
            }
        }
        Some("OppositeSideLiquidity" | "SameSideLiquidity") => {
            if !object
                .get("depthReference")
                .and_then(Value::as_u64)
                .is_some_and(|v| (1..=10).contains(&v))
            {
                return Err(invalid("depthReference must be an integer from 1 to 10"));
            }
        }
        _ => return Err(invalid("unsupported POV mode")),
    }
    Ok(())
}
