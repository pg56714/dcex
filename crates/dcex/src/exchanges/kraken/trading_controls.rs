//! Additional batch trading, available balances and margin preferences.
pub(in crate::exchanges::kraken) use super::client::{KrakenAuth, KrakenClient};
pub(in crate::exchanges::kraken) use super::params::KrakenParams;
pub(in crate::exchanges::kraken) use crate::Result;
pub(in crate::exchanges::kraken) use crate::exchange::ValidatedResponse;
pub(in crate::exchanges::kraken) use crate::http::HttpMethod;
pub(in crate::exchanges::kraken) use serde_json::Value;

pub(in crate::exchanges::kraken) use crate::exchanges::kraken::params::invalid;
pub(in crate::exchanges::kraken) fn parse_bool(
    params: &KrakenParams,
    key: &str,
) -> Result<Option<bool>> {
    params
        .get(key)
        .map(|value| {
            value
                .parse::<bool>()
                .map_err(|_| invalid("expected boolean"))
        })
        .transpose()
}
pub(in crate::exchanges::kraken) fn array(params: &KrakenParams, key: &str) -> Result<Vec<Value>> {
    let value: Value =
        serde_json::from_str(params.required(key)?).map_err(|e| invalid(e.to_string()))?;
    value
        .as_array()
        .cloned()
        .ok_or_else(|| invalid("expected JSON array"))
}

impl KrakenClient {
    pub(super) async fn trading_controls_request(
        &self,
        name: &str,
        params: &KrakenParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match name {
            "manage_futures_batch_orders" => {
                self.dispatch_manage_futures_batch_orders(name, params)
                    .await?
            }
            "get_spot_extended_balance" => {
                params.ensure_allowed(&["rebase_multiplier"])?;
                if params
                    .get("rebase_multiplier")
                    .is_some_and(|v| !["base", "rebased"].contains(&v))
                {
                    return Err(invalid("rebase_multiplier must be base or rebased"));
                }
                self.private_post(
                    KrakenAuth::Spot,
                    "/0/private/BalanceEx",
                    params.only(&["rebase_multiplier"]),
                )
                .await?
            }
            "get_futures_leverage_preferences" => {
                params.ensure_allowed(&[])?;
                self.private_get(
                    KrakenAuth::Futures,
                    "/derivatives/api/v3/leveragepreferences",
                    vec![],
                )
                .await?
            }
            "set_futures_leverage_preference" => {
                params.ensure_allowed(&["product_symbol", "margin_mode", "maxLeverage"])?;
                match params.required("margin_mode")? {
                    "cross" if params.get("maxLeverage").is_none() => {}
                    "isolated" if params.get("maxLeverage").is_some() => {}
                    _ => {
                        return Err(invalid(
                            "margin_mode must be cross without maxLeverage, or isolated with maxLeverage",
                        ));
                    }
                }
                let symbol = self.exchange_symbol(params.required("product_symbol")?, "PF_")?;
                let mut query = params.only(&["maxLeverage"]);
                if params
                    .get("maxLeverage")
                    .is_some_and(|v| !v.parse::<f64>().is_ok_and(|v| v.is_finite() && v > 0.0))
                {
                    return Err(invalid("maxLeverage must be positive for isolated margin"));
                }
                query.push(("symbol".into(), symbol));
                self.request(
                    HttpMethod::Put,
                    KrakenAuth::Futures,
                    "/derivatives/api/v3/leveragepreferences",
                    query,
                    None,
                    true,
                )
                .await?
            }
            "place_spot_batch_orders" => {
                self.dispatch_place_spot_batch_orders(name, params).await?
            }
            "cancel_spot_batch_orders" => {
                self.dispatch_cancel_spot_batch_orders(name, params).await?
            }
            _ => return Ok(None),
        };
        Ok(Some(result))
    }
}

pub(in crate::exchanges::kraken) fn validate_batch_order(value: &Value) -> Result<()> {
    let object = value
        .as_object()
        .ok_or_else(|| invalid("batch order must be an object"))?;
    let allowed = [
        "userref",
        "cl_ord_id",
        "ordertype",
        "type",
        "volume",
        "displayvol",
        "price",
        "price2",
        "trigger",
        "leverage",
        "reduce_only",
        "stptype",
        "oflags",
        "timeinforce",
        "starttm",
        "expiretm",
        "close",
    ];
    if object.keys().any(|key| !allowed.contains(&key.as_str())) {
        return Err(invalid("unsupported batch order field"));
    }
    for key in ["ordertype", "type", "volume"] {
        if value[key].as_str().is_none_or(|s| s.is_empty()) {
            return Err(invalid("ordertype, type and volume are required strings"));
        }
    }
    if !["buy", "sell"].contains(&value["type"].as_str().unwrap()) {
        return Err(invalid("invalid order side"));
    }
    let kind = value["ordertype"].as_str().unwrap();
    if ![
        "market",
        "limit",
        "iceberg",
        "stop-loss",
        "take-profit",
        "stop-loss-limit",
        "take-profit-limit",
        "trailing-stop",
        "trailing-stop-limit",
        "settle-position",
    ]
    .contains(&kind)
    {
        return Err(invalid("unsupported ordertype"));
    }
    let volume = value["volume"]
        .as_str()
        .unwrap()
        .parse::<f64>()
        .map_err(|_| invalid("invalid volume"))?;
    if !volume.is_finite()
        || volume < 0.0
        || volume == 0.0 && value["reduce_only"] != true && kind != "settle-position"
    {
        return Err(invalid("zero volume is reserved for closing margin orders"));
    }
    if object.contains_key("userref") && object.contains_key("cl_ord_id") {
        return Err(invalid("userref and cl_ord_id are mutually exclusive"));
    }
    if object.get("reduce_only").is_some_and(|v| !v.is_boolean()) {
        return Err(invalid("reduce_only must be a JSON boolean"));
    }
    if !["market", "settle-position"].contains(&kind)
        && value["price"].as_str().is_none_or(|s| s.is_empty())
    {
        return Err(invalid("price is required for this order type"));
    }
    if [
        "stop-loss-limit",
        "take-profit-limit",
        "trailing-stop-limit",
    ]
    .contains(&kind)
        && value["price2"].as_str().is_none_or(|s| s.is_empty())
    {
        return Err(invalid("price2 is required"));
    }
    if kind == "iceberg"
        && !value["displayvol"].as_str().is_some_and(|s| {
            s.parse::<f64>()
                .is_ok_and(|v| v.is_finite() && v > 0.0 && v <= volume && v * 15.0 >= volume)
        })
    {
        return Err(invalid("displayvol must be between volume/15 and volume"));
    }
    if value["timeinforce"] == "GTD" && !object.contains_key("expiretm") {
        return Err(invalid("GTD requires expiretm"));
    }
    Ok(())
}

pub(in crate::exchanges::kraken) fn validate_futures_instruction(value: &Value) -> Result<()> {
    let object = value
        .as_object()
        .ok_or_else(|| invalid("instruction must be an object"))?;
    let order = value["order"]
        .as_str()
        .ok_or_else(|| invalid("order instruction is required"))?;
    let allowed: &[&str] = match order {
        "send" => &[
            "order",
            "order_tag",
            "orderType",
            "symbol",
            "side",
            "size",
            "limitPrice",
            "stopPrice",
            "cliOrdId",
            "triggerSignal",
            "reduceOnly",
            "trailingStopMaxDeviation",
            "trailingStopDeviationUnit",
        ],
        "edit" => &[
            "order",
            "order_id",
            "cliOrdId",
            "size",
            "limitPrice",
            "stopPrice",
            "trailingStopMaxDeviation",
            "trailingStopDeviationUnit",
            "qtyMode",
        ],
        "cancel" => &["order", "order_id", "cliOrdId"],
        _ => return Err(invalid("order must be send, edit or cancel")),
    };
    if object.keys().any(|k| !allowed.contains(&k.as_str())) {
        return Err(invalid("unsupported batch instruction field"));
    }
    for k in [
        "size",
        "limitPrice",
        "stopPrice",
        "trailingStopMaxDeviation",
    ] {
        if let Some(v) = object.get(k)
            && !v.as_f64().is_some_and(|v| v.is_finite() && v > 0.0)
        {
            return Err(invalid(
                "batch price and size fields require positive JSON numbers",
            ));
        }
    }
    for k in [
        "order_tag",
        "orderType",
        "symbol",
        "side",
        "cliOrdId",
        "order_id",
        "triggerSignal",
        "trailingStopDeviationUnit",
        "qtyMode",
    ] {
        if let Some(v) = object.get(k)
            && v.as_str().is_none_or(|v| v.trim().is_empty())
        {
            return Err(invalid(
                "batch identifiers and enums must be nonempty strings",
            ));
        }
    }
    if value
        .get("cliOrdId")
        .and_then(Value::as_str)
        .is_some_and(|v| v.len() > 100)
    {
        return Err(invalid("cliOrdId exceeds 100 characters"));
    }
    if object.get("reduceOnly").is_some_and(|v| !v.is_boolean()) {
        return Err(invalid("reduceOnly must be a JSON boolean"));
    }
    for (k, allowed) in [
        ("side", &["buy", "sell"][..]),
        (
            "orderType",
            &[
                "lmt",
                "post",
                "ioc",
                "mkt",
                "stp",
                "take_profit",
                "trailing_stop",
                "fok",
            ][..],
        ),
        ("triggerSignal", &["mark", "index", "last"][..]),
        (
            "trailingStopDeviationUnit",
            &["PERCENT", "QUOTE_CURRENCY"][..],
        ),
        ("qtyMode", &["ABSOLUTE", "RELATIVE"][..]),
    ] {
        if let Some(v) = object.get(k)
            && !v.as_str().is_some_and(|v| allowed.contains(&v))
        {
            return Err(invalid("unsupported batch enum"));
        }
    }
    if order == "send" {
        for k in ["symbol", "order_tag", "side", "size", "orderType"] {
            if !object.contains_key(k) {
                return Err(invalid("send instruction is missing a required field"));
            }
        }
        match value["orderType"].as_str().unwrap_or_default() {
            "lmt" | "post" | "ioc" | "fok" => {
                if !object.contains_key("limitPrice") {
                    return Err(invalid("limit order requires limitPrice"));
                }
            }
            "stp" | "take_profit" => {
                if !object.contains_key("stopPrice")
                    || (value["orderType"] == "stp" && !object.contains_key("limitPrice"))
                {
                    return Err(invalid(
                        "conditional batch order requires stopPrice; stp also requires limitPrice",
                    ));
                }
            }
            "trailing_stop" => {
                if !object.contains_key("trailingStopMaxDeviation")
                    || !object.contains_key("trailingStopDeviationUnit")
                    || object.contains_key("limitPrice")
                    || object.contains_key("stopPrice")
                {
                    return Err(invalid(
                        "trailing_stop requires deviation fields and no explicit prices",
                    ));
                }
            }
            _ => {}
        }
    } else {
        if object.contains_key("order_id") == object.contains_key("cliOrdId") {
            return Err(invalid("provide exactly one of order_id and cliOrdId"));
        }
        if order == "edit"
            && ![
                "size",
                "limitPrice",
                "stopPrice",
                "trailingStopMaxDeviation",
                "trailingStopDeviationUnit",
            ]
            .iter()
            .any(|k| object.contains_key(*k))
        {
            return Err(invalid("edit requires at least one change"));
        }
    }
    if value["trailingStopDeviationUnit"] == "PERCENT"
        && !value["trailingStopMaxDeviation"]
            .as_f64()
            .is_some_and(|v| (0.1..=50.0).contains(&v))
    {
        return Err(invalid("trailing percentage must be 0.1..=50"));
    }
    Ok(())
}
