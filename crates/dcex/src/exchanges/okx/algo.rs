//! Standalone algo order lifecycle and isolated position margin.
use serde_json::{Map, Value};

use super::client::OkxClient;
use super::params::{OkxParams, insert_optional_bool};
use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

const ORDER_TYPES: &[&str] = &[
    "conditional",
    "oco",
    "chase",
    "trigger",
    "move_order_stop",
    "twap",
    "smart_iceberg",
];
const PLACE_STRINGS: &[&str] = &[
    "tdMode",
    "ccy",
    "side",
    "posSide",
    "ordType",
    "sz",
    "tag",
    "tgtCcy",
    "algoClOrdId",
    "closeFraction",
    "tradeQuoteCcy",
    "tpTriggerPx",
    "tpTriggerPxType",
    "tpOrdPx",
    "tpOrdKind",
    "slTriggerPx",
    "slTriggerPxType",
    "slOrdPx",
    "chaseType",
    "chaseVal",
    "maxChaseType",
    "maxChaseVal",
    "triggerPx",
    "orderPx",
    "advanceOrdType",
    "triggerPxType",
    "callbackRatio",
    "callbackSpread",
    "activePx",
    "pxVar",
    "pxSpread",
    "szLimit",
    "pxLimit",
    "timeInterval",
    "lmtOrderNumber",
    "aggressiveness",
];
const AMEND_STRINGS: &[&str] = &[
    "algoId",
    "algoClOrdId",
    "reqId",
    "newSz",
    "newTpTriggerPx",
    "newTpOrdPx",
    "newSlTriggerPx",
    "newSlOrdPx",
    "newTpTriggerPxType",
    "newSlTriggerPxType",
    "newTriggerPx",
    "newOrdPx",
    "newTriggerPxType",
];

impl OkxClient {
    pub(super) async fn algo_private_request(
        &self,
        name: &str,
        params: &OkxParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match name {
            "place_algo_order" => {
                let mut allowed = PLACE_STRINGS.to_vec();
                allowed.extend([
                    "product_symbol",
                    "instId",
                    "reduceOnly",
                    "cxlOnClosePos",
                    "attachAlgoOrds",
                    "advChaseParams",
                    "triggerParams",
                ]);
                allowed_params(params, &allowed)?;
                for key in ["tdMode", "side", "ordType"] {
                    params.required(key)?;
                }
                enumeration(
                    params,
                    "tdMode",
                    &["cross", "isolated", "cash", "spot_isolated"],
                )?;
                enumeration(params, "side", &["buy", "sell"])?;
                enumeration(params, "posSide", &["net", "long", "short"])?;
                enumeration(params, "ordType", ORDER_TYPES)?;
                enumeration(params, "tgtCcy", &["base_ccy", "quote_ccy"])?;
                let order_type = params.required("ordType")?;
                exactly_one(params, "sz", "closeFraction")?;
                number(params, "sz", false, false)?;
                if params.get("closeFraction").is_some() {
                    if params.get("closeFraction") != Some("1")
                        || !["conditional", "oco"].contains(&order_type)
                    {
                        return Err(invalid(
                            "closeFraction must be 1 for conditional or oco orders",
                        ));
                    }
                    if params.get("posSide").unwrap_or("net") == "net"
                        && params.get("reduceOnly") != Some("true")
                    {
                        return Err(invalid(
                            "closeFraction in net mode requires reduceOnly=true",
                        ));
                    }
                    for key in ["tpOrdPx", "slOrdPx"] {
                        if params.get(key).is_some_and(|price| price != "-1") {
                            return Err(invalid("closeFraction requires market TP/SL prices (-1)"));
                        }
                    }
                }
                for key in ["tpTriggerPxType", "slTriggerPxType", "triggerPxType"] {
                    enumeration(params, key, &["last", "index", "mark"])?;
                }
                let mut body = params.body(PLACE_STRINGS);
                match order_type {
                    "conditional" | "oco" => {
                        enumeration(params, "tpOrdKind", &["condition", "limit"])?;
                        if params.get("tpOrdKind") == Some("limit") {
                            params.required("tpOrdPx")?;
                        } else {
                            paired(params, "tpTriggerPx", "tpOrdPx")?;
                        }
                        paired(params, "slTriggerPx", "slOrdPx")?;
                        if params.get("tpOrdPx").is_none() && params.get("slOrdPx").is_none() {
                            return Err(invalid("TP or SL parameters are required"));
                        }
                        if order_type == "oco"
                            && (params.get("tpOrdPx").is_none() || params.get("slOrdPx").is_none())
                        {
                            return Err(invalid("OCO requires both TP and SL"));
                        }
                    }
                    "trigger" => {
                        params.required("triggerPx")?;
                        enumeration(params, "advanceOrdType", &["fok", "ioc", "chase"])?;
                        if params.get("advanceOrdType") == Some("chase") {
                            params.required("advChaseParams")?;
                            if params.get("orderPx").is_some()
                                || params.get("attachAlgoOrds").is_some()
                            {
                                return Err(invalid(
                                    "trigger chase does not accept orderPx or attachAlgoOrds",
                                ));
                            }
                        } else {
                            params.required("orderPx")?;
                        }
                    }
                    "move_order_stop" => {
                        exactly_one(params, "callbackRatio", "callbackSpread")?;
                    }
                    "chase" => {
                        enumeration(params, "chaseType", &["distance", "ratio"])?;
                        enumeration(params, "maxChaseType", &["distance", "ratio"])?;
                        paired(params, "maxChaseType", "maxChaseVal")?;
                    }
                    "twap" => {
                        exactly_one(params, "pxVar", "pxSpread")?;
                        for key in ["szLimit", "pxLimit", "timeInterval"] {
                            params.required(key)?;
                        }
                    }
                    "smart_iceberg" => {
                        for key in ["szLimit", "lmtOrderNumber", "aggressiveness"] {
                            params.required(key)?;
                        }
                        enumeration(
                            params,
                            "aggressiveness",
                            &["radical", "mid", "conservative"],
                        )?;
                    }
                    _ => unreachable!(),
                }
                for key in [
                    "tpTriggerPx",
                    "slTriggerPx",
                    "triggerPx",
                    "callbackRatio",
                    "callbackSpread",
                    "activePx",
                    "szLimit",
                    "timeInterval",
                    "lmtOrderNumber",
                    "maxChaseVal",
                ] {
                    number(params, key, false, false)?;
                }
                for key in ["tpOrdPx", "slOrdPx", "orderPx"] {
                    number(params, key, false, true)?;
                }
                for key in ["chaseVal", "pxLimit", "pxSpread"] {
                    number(params, key, true, false)?;
                }
                if let Some(value) = params.get("pxVar") {
                    if !value
                        .parse::<f64>()
                        .is_ok_and(|v| (0.0001..=0.01).contains(&v))
                    {
                        return Err(invalid("pxVar must be 0.0001..=0.01"));
                    }
                }
                if params.get("cxlOnClosePos") == Some("true")
                    && params.get("reduceOnly") != Some("true")
                {
                    return Err(invalid("cxlOnClosePos requires reduceOnly=true"));
                }
                for key in ["reduceOnly", "cxlOnClosePos"] {
                    insert_optional_bool(&mut body, key, params.get(key))?;
                }
                insert_arrays(
                    &mut body,
                    params,
                    &["attachAlgoOrds", "advChaseParams", "triggerParams"],
                )?;
                self.algo_inst_id(&mut body, params)?;
                self.post_request("/api/v5/trade/order-algo", Value::Object(body))
                    .await
            }
            "amend_algo_order" => {
                let mut allowed = AMEND_STRINGS.to_vec();
                allowed.extend([
                    "product_symbol",
                    "instId",
                    "cxlOnFail",
                    "attachAlgoOrds",
                    "advChaseParams",
                ]);
                allowed_params(params, &allowed)?;
                identifier(params)?;
                if AMEND_STRINGS[3..]
                    .iter()
                    .all(|key| params.get(key).is_none())
                    && params.get("attachAlgoOrds").is_none()
                    && params.get("advChaseParams").is_none()
                {
                    return Err(invalid("at least one algo amendment is required"));
                }
                number(params, "newSz", false, false)?;
                for key in ["newTpTriggerPx", "newSlTriggerPx", "newTriggerPx"] {
                    number(params, key, key != "newTriggerPx", false)?;
                }
                for key in ["newTpOrdPx", "newSlOrdPx", "newOrdPx"] {
                    number(params, key, key != "newOrdPx", true)?;
                }
                for key in [
                    "newTpTriggerPxType",
                    "newSlTriggerPxType",
                    "newTriggerPxType",
                ] {
                    enumeration(params, key, &["last", "index", "mark"])?;
                }
                let mut body = params.body(AMEND_STRINGS);
                self.algo_inst_id(&mut body, params)?;
                insert_optional_bool(&mut body, "cxlOnFail", params.get("cxlOnFail"))?;
                insert_arrays(&mut body, params, &["attachAlgoOrds", "advChaseParams"])?;
                self.post_request("/api/v5/trade/amend-algos", Value::Object(body))
                    .await
            }
            "cancel_algo_orders" => {
                allowed_params(params, &["orders"])?;
                let mut orders = params.json_required("orders")?;
                let array = orders
                    .as_array_mut()
                    .filter(|items| (1..=10).contains(&items.len()))
                    .ok_or_else(|| invalid("cancel_algo_orders requires 1 to 10 orders"))?;
                for order in array {
                    let object = order
                        .as_object_mut()
                        .ok_or_else(|| invalid("cancel order must be an object"))?;
                    if object.keys().any(|key| {
                        !["instId", "product_symbol", "algoId", "algoClOrdId"]
                            .contains(&key.as_str())
                    }) {
                        return Err(invalid("unsupported cancel algo field"));
                    }
                    if object
                        .values()
                        .any(|v| !v.as_str().is_some_and(|s| !s.trim().is_empty()))
                    {
                        return Err(invalid("cancel algo fields must be nonempty strings"));
                    }
                    if !object.contains_key("algoId") && !object.contains_key("algoClOrdId") {
                        return Err(invalid("algoId or algoClOrdId is required"));
                    }
                    let symbol = object
                        .remove("product_symbol")
                        .or_else(|| object.remove("instId"))
                        .ok_or_else(|| invalid("instId is required"))?;
                    object.insert(
                        "instId".into(),
                        Value::String(self.exchange_symbol(symbol.as_str().unwrap())?),
                    );
                }
                self.post_request("/api/v5/trade/cancel-algos", orders)
                    .await
            }
            "get_algo_order" | "get_pending_algo_orders" | "get_algo_order_history" => {
                let detail = name == "get_algo_order";
                let history = name == "get_algo_order_history";
                let allowed: &[&str] = if detail {
                    &["algoId", "algoClOrdId"]
                } else if history {
                    &[
                        "ordType",
                        "state",
                        "algoId",
                        "instType",
                        "instId",
                        "product_symbol",
                        "after",
                        "before",
                        "limit",
                    ]
                } else {
                    &[
                        "ordType",
                        "algoId",
                        "instType",
                        "instId",
                        "product_symbol",
                        "after",
                        "before",
                        "limit",
                    ]
                };
                allowed_params(params, allowed)?;
                if detail {
                    identifier(params)?;
                } else {
                    let kind = params.required("ordType")?;
                    if !ORDER_TYPES.contains(&kind)
                        && !["iceberg", "conditional,oco", "oco,conditional"].contains(&kind)
                    {
                        return Err(invalid("unsupported ordType"));
                    }
                    enumeration(params, "instType", &["SPOT", "SWAP", "FUTURES", "MARGIN"])?;
                    enumeration(params, "state", &["effective", "canceled", "order_failed"])?;
                    if history && params.get("state").is_none() && params.get("algoId").is_none() {
                        return Err(invalid("state or algoId is required"));
                    }
                    if params
                        .get("limit")
                        .is_some_and(|v| !v.parse::<u16>().is_ok_and(|v| (1..=100).contains(&v)))
                    {
                        return Err(invalid("limit must be 1..=100"));
                    }
                }
                let mut query = params.without(&["product_symbol", "instId"]);
                if let Some(symbol) = params
                    .get("product_symbol")
                    .or_else(|| params.get("instId"))
                {
                    query.push(("instId".into(), self.exchange_symbol(symbol)?));
                }
                self.get_request(
                    if detail {
                        "/api/v5/trade/order-algo"
                    } else if history {
                        "/api/v5/trade/orders-algo-history"
                    } else {
                        "/api/v5/trade/orders-algo-pending"
                    },
                    query,
                )
                .await
            }
            "adjust_position_margin" => {
                allowed_params(
                    params,
                    &["product_symbol", "instId", "posSide", "type", "amt", "ccy"],
                )?;
                for key in ["posSide", "type", "amt"] {
                    params.required(key)?;
                }
                enumeration(params, "posSide", &["net", "long", "short"])?;
                enumeration(params, "type", &["add", "reduce"])?;
                number(params, "amt", false, false)?;
                let mut body = params.body(&["posSide", "type", "amt", "ccy"]);
                self.algo_inst_id(&mut body, params)?;
                self.post_request(
                    "/api/v5/account/position/margin-balance",
                    Value::Object(body),
                )
                .await
            }
            _ => return Ok(None),
        };
        result.map(Some)
    }
    fn algo_inst_id(&self, body: &mut Map<String, Value>, params: &OkxParams) -> Result<()> {
        let symbol = params
            .get("product_symbol")
            .or_else(|| params.get("instId"))
            .ok_or_else(|| invalid("product_symbol or instId is required"))?;
        body.insert(
            "instId".into(),
            Value::String(self.exchange_symbol(symbol)?),
        );
        Ok(())
    }
}

fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(message.into())
}
fn allowed_params(params: &OkxParams, allowed: &[&str]) -> Result<()> {
    if !params.without(allowed).is_empty() {
        return Err(invalid("unsupported algo parameter"));
    }
    if params
        .only(allowed)
        .iter()
        .any(|(_, value)| value.trim().is_empty())
    {
        return Err(invalid("algo parameters must not be empty"));
    }
    Ok(())
}
fn identifier(params: &OkxParams) -> Result<()> {
    if params.get("algoId").is_none() && params.get("algoClOrdId").is_none() {
        return Err(invalid("algoId or algoClOrdId is required"));
    }
    Ok(())
}
fn enumeration(params: &OkxParams, key: &str, choices: &[&str]) -> Result<()> {
    if params.get(key).is_some_and(|v| !choices.contains(&v)) {
        return Err(invalid(&format!("unsupported {key}")));
    }
    Ok(())
}
fn exactly_one(params: &OkxParams, first: &str, second: &str) -> Result<()> {
    if params.get(first).is_some() == params.get(second).is_some() {
        return Err(invalid(&format!(
            "exactly one of {first} or {second} is required"
        )));
    }
    Ok(())
}
fn paired(params: &OkxParams, first: &str, second: &str) -> Result<()> {
    if params.get(first).is_some() != params.get(second).is_some() {
        return Err(invalid(&format!(
            "{first} and {second} must be provided together"
        )));
    }
    Ok(())
}
fn number(params: &OkxParams, key: &str, zero: bool, market: bool) -> Result<()> {
    if let Some(value) = params.get(key) {
        if !value
            .parse::<f64>()
            .is_ok_and(|v| v.is_finite() && (v > 0.0 || zero && v == 0.0 || market && v == -1.0))
        {
            return Err(invalid(&format!("invalid {key}")));
        }
    }
    Ok(())
}
fn insert_arrays(body: &mut Map<String, Value>, params: &OkxParams, fields: &[&str]) -> Result<()> {
    for key in fields {
        if let Some(array) = params.json_optional(key)? {
            if !array
                .as_array()
                .is_some_and(|items| items.iter().all(Value::is_object))
            {
                return Err(invalid(&format!("{key} must be an array of objects")));
            }
            body.insert((*key).into(), array);
        }
    }
    Ok(())
}
