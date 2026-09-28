//! Additional classic and UTA trading and risk endpoints.
use super::client::BitgetClient;
use super::params::BitgetParams;
use crate::Result;
use crate::exchange::ValidatedResponse;
use serde_json::Value;
type TradingRoute<'a> = (
    &'a str,
    &'a str,
    bool,
    &'a [&'a str],
    &'a [&'a str],
    &'a [&'a str],
    &'a [&'a str],
);

impl BitgetClient {
    pub(super) async fn trading_controls_request(
        &self,
        name: &str,
        params: &BitgetParams,
        public: bool,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, method, is_public, fields, required, arrays, numbers): TradingRoute<'_> =
            match name {
                "modify_futures_tpsl_order" => (
                    "/api/v2/mix/order/modify-tpsl-order",
                    "POST",
                    false,
                    &[
                        "marginCoin",
                        "productType",
                        "symbol",
                        "triggerPrice",
                        "size",
                        "orderId",
                        "clientOid",
                        "triggerType",
                        "executePrice",
                        "rangeRate",
                    ],
                    &[
                        "marginCoin",
                        "productType",
                        "symbol",
                        "triggerPrice",
                        "size",
                    ],
                    &[],
                    &[],
                ),
                "place_futures_plan_order" => (
                    "/api/v2/mix/order/place-plan-order",
                    "POST",
                    false,
                    &[
                        "planType",
                        "symbol",
                        "productType",
                        "marginMode",
                        "marginCoin",
                        "size",
                        "triggerPrice",
                        "triggerType",
                        "side",
                        "orderType",
                        "price",
                        "callbackRatio",
                        "tradeSide",
                        "clientOid",
                        "reduceOnly",
                        "stopSurplusTriggerPrice",
                        "stopSurplusExecutePrice",
                        "stopSurplusTriggerType",
                        "stopLossTriggerPrice",
                        "stopLossExecutePrice",
                        "stopLossTriggerType",
                        "stpMode",
                    ],
                    &[
                        "planType",
                        "symbol",
                        "productType",
                        "marginMode",
                        "marginCoin",
                        "size",
                        "triggerPrice",
                        "triggerType",
                        "side",
                        "orderType",
                    ],
                    &[],
                    &[],
                ),
                "place_futures_position_tpsl" => (
                    "/api/v2/mix/order/place-pos-tpsl",
                    "POST",
                    false,
                    &[
                        "marginCoin",
                        "productType",
                        "symbol",
                        "holdSide",
                        "stopSurplusTriggerPrice",
                        "stopSurplusSize",
                        "stopSurplusTriggerType",
                        "stopSurplusExecutePrice",
                        "stopLossTriggerPrice",
                        "stopLossSize",
                        "stopLossTriggerType",
                        "stopLossExecutePrice",
                        "stpMode",
                        "stopSurplusClientOid",
                        "stopLossClientOid",
                    ],
                    &["marginCoin", "productType", "symbol", "holdSide"],
                    &[],
                    &[],
                ),
                "place_futures_tpsl_order" => (
                    "/api/v2/mix/order/place-tpsl-order",
                    "POST",
                    false,
                    &[
                        "marginCoin",
                        "productType",
                        "symbol",
                        "planType",
                        "triggerPrice",
                        "holdSide",
                        "size",
                        "triggerType",
                        "executePrice",
                        "rangeRate",
                        "clientOid",
                        "stpMode",
                    ],
                    &[
                        "marginCoin",
                        "productType",
                        "symbol",
                        "planType",
                        "triggerPrice",
                        "holdSide",
                    ],
                    &[],
                    &[],
                ),
                "get_futures_plan_sub_order" => (
                    "/api/v2/mix/order/plan-sub-order",
                    "GET",
                    false,
                    &["planType", "planOrderId", "productType"],
                    &["planType", "planOrderId", "productType"],
                    &[],
                    &[],
                ),
                "modify_futures_plan_order" => (
                    "/api/v2/mix/order/modify-plan-order",
                    "POST",
                    false,
                    &[
                        "productType",
                        "orderId",
                        "clientOid",
                        "newSize",
                        "newPrice",
                        "newCallbackRatio",
                        "newTriggerPrice",
                        "newTriggerType",
                        "newStopSurplusTriggerPrice",
                        "newStopSurplusExecutePrice",
                        "newStopSurplusTriggerType",
                        "newStopLossTriggerPrice",
                        "newStopLossExecutePrice",
                        "newStopLossTriggerType",
                    ],
                    &["productType"],
                    &[],
                    &[],
                ),
                "cancel_futures_plan_orders" => (
                    "/api/v2/mix/order/cancel-plan-order",
                    "POST",
                    false,
                    &[
                        "productType",
                        "orderIdList",
                        "symbol",
                        "marginCoin",
                        "planType",
                    ],
                    &["productType"],
                    &["orderIdList"],
                    &[],
                ),
                "get_pending_futures_plan_orders" => (
                    "/api/v2/mix/order/orders-plan-pending",
                    "GET",
                    false,
                    &[
                        "planType",
                        "productType",
                        "orderId",
                        "clientOid",
                        "symbol",
                        "idLessThan",
                        "startTime",
                        "endTime",
                        "limit",
                    ],
                    &["planType", "productType"],
                    &[],
                    &[],
                ),
                "get_futures_plan_order_history" => (
                    "/api/v2/mix/order/orders-plan-history",
                    "GET",
                    false,
                    &[
                        "planType",
                        "productType",
                        "orderId",
                        "clientOid",
                        "planStatus",
                        "symbol",
                        "idLessThan",
                        "startTime",
                        "endTime",
                        "limit",
                    ],
                    &["planType", "productType"],
                    &[],
                    &[],
                ),
                "place_spot_plan_order" => (
                    "/api/v2/spot/trade/place-plan-order",
                    "POST",
                    false,
                    &[
                        "symbol",
                        "side",
                        "triggerPrice",
                        "orderType",
                        "size",
                        "triggerType",
                        "executePrice",
                        "planType",
                        "clientOid",
                        "stpMode",
                    ],
                    &[
                        "symbol",
                        "side",
                        "triggerPrice",
                        "orderType",
                        "size",
                        "triggerType",
                    ],
                    &[],
                    &[],
                ),
                "modify_spot_plan_order" => (
                    "/api/v2/spot/trade/modify-plan-order",
                    "POST",
                    false,
                    &[
                        "triggerPrice",
                        "orderType",
                        "size",
                        "orderId",
                        "clientOid",
                        "executePrice",
                    ],
                    &["triggerPrice", "orderType", "size"],
                    &[],
                    &[],
                ),
                "cancel_spot_plan_order" => (
                    "/api/v2/spot/trade/cancel-plan-order",
                    "POST",
                    false,
                    &["orderId", "clientOid"],
                    &[],
                    &[],
                    &[],
                ),
                "cancel_spot_plan_orders" => (
                    "/api/v2/spot/trade/batch-cancel-plan-order",
                    "POST",
                    false,
                    &["symbolList"],
                    &[],
                    &["symbolList"],
                    &[],
                ),
                "get_pending_spot_plan_orders" => (
                    "/api/v2/spot/trade/current-plan-order",
                    "GET",
                    false,
                    &["symbol", "limit", "idLessThan", "startTime", "endTime"],
                    &[],
                    &[],
                    &[],
                ),
                "get_spot_plan_order_history" => (
                    "/api/v2/spot/trade/history-plan-order",
                    "GET",
                    false,
                    &["symbol", "startTime", "endTime", "idLessThan", "limit"],
                    &[],
                    &[],
                    &[],
                ),
                "get_spot_plan_sub_order" => (
                    "/api/v2/spot/trade/plan-sub-order",
                    "GET",
                    false,
                    &["planOrderId"],
                    &["planOrderId"],
                    &[],
                    &[],
                ),
                "modify_futures_order" => (
                    "/api/v2/mix/order/modify-order",
                    "POST",
                    false,
                    &[
                        "symbol",
                        "productType",
                        "newClientOid",
                        "orderId",
                        "clientOid",
                        "newSize",
                        "newPrice",
                        "newPresetStopSurplusPrice",
                        "newPresetStopLossPrice",
                    ],
                    &["symbol", "productType", "newClientOid"],
                    &[],
                    &[],
                ),
                "close_futures_positions" => (
                    "/api/v2/mix/order/close-positions",
                    "POST",
                    false,
                    &["productType", "symbol", "holdSide"],
                    &["productType"],
                    &[],
                    &[],
                ),
                "cancel_all_futures_orders" => (
                    "/api/v2/mix/order/cancel-all-orders",
                    "POST",
                    false,
                    &["productType", "marginCoin", "requestTime", "receiveWindow"],
                    &["productType"],
                    &[],
                    &[],
                ),
                "cancel_spot_orders_by_symbol" => (
                    "/api/v2/spot/trade/cancel-symbol-order",
                    "POST",
                    false,
                    &["symbol"],
                    &["symbol"],
                    &[],
                    &[],
                ),
                "cancel_replace_spot_order" => (
                    "/api/v2/spot/trade/cancel-replace-order",
                    "POST",
                    false,
                    &[
                        "symbol",
                        "price",
                        "size",
                        "clientOid",
                        "orderId",
                        "newClientOid",
                        "presetTakeProfitPrice",
                        "executeTakeProfitPrice",
                        "presetStopLossPrice",
                        "executeStopLossPrice",
                    ],
                    &["symbol", "price", "size"],
                    &[],
                    &[],
                ),
                "adjust_futures_position_margin" => (
                    "/api/v2/mix/account/set-margin",
                    "POST",
                    false,
                    &["symbol", "productType", "marginCoin", "holdSide", "amount"],
                    &["symbol", "productType", "marginCoin", "holdSide", "amount"],
                    &[],
                    &[],
                ),
                "get_futures_symbol_price" => (
                    "/api/v2/mix/market/symbol-price",
                    "GET",
                    true,
                    &["symbol", "productType"],
                    &["symbol", "productType"],
                    &[],
                    &[],
                ),
                "modify_uta_order" => (
                    "/api/v3/trade/modify-order",
                    "POST",
                    false,
                    &[
                        "orderId",
                        "clientOid",
                        "qty",
                        "price",
                        "requestId",
                        "autoCancel",
                        "symbol",
                        "category",
                        "tpTriggerBy",
                        "slTriggerBy",
                        "takeProfit",
                        "stopLoss",
                        "tpOrderType",
                        "slOrderType",
                        "tpLimitPrice",
                        "slLimitPrice",
                        "pxAmendType",
                    ],
                    &["symbol", "category"],
                    &[],
                    &["requestId"],
                ),
                "cancel_uta_orders_by_symbol" => (
                    "/api/v3/trade/cancel-symbol-order",
                    "POST",
                    false,
                    &["category", "symbol"],
                    &["category"],
                    &[],
                    &[],
                ),
                "set_uta_cancel_countdown" => (
                    "/api/v3/trade/countdown-cancel-all",
                    "POST",
                    false,
                    &["countdown"],
                    &["countdown"],
                    &[],
                    &[],
                ),
                "close_uta_positions" => (
                    "/api/v3/trade/close-positions",
                    "POST",
                    false,
                    &["category", "symbol", "posSide"],
                    &["category"],
                    &[],
                    &[],
                ),
                "get_uta_position_history" => (
                    "/api/v3/position/history-position",
                    "GET",
                    false,
                    &[
                        "category",
                        "symbol",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
                    ],
                    &["category"],
                    &[],
                    &[],
                ),
                "adjust_uta_position_margin" => (
                    "/api/v3/account/set-margin",
                    "POST",
                    false,
                    &["category", "symbol", "posSide", "operation", "amount"],
                    &["category", "symbol", "posSide", "operation", "amount"],
                    &[],
                    &[],
                ),
                "get_uta_financial_records" => (
                    "/api/v3/account/financial-records",
                    "GET",
                    false,
                    &[
                        "category",
                        "coin",
                        "type",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
                    ],
                    &["category"],
                    &[],
                    &[],
                ),
                "get_uta_open_interest" => (
                    "/api/v3/market/open-interest",
                    "GET",
                    true,
                    &["category", "symbol"],
                    &["category"],
                    &[],
                    &[],
                ),
                "get_uta_current_funding_rate" => (
                    "/api/v3/market/current-fund-rate",
                    "GET",
                    true,
                    &["category", "symbol"],
                    &[],
                    &[],
                    &[],
                ),
                _ => return Ok(None),
            };
        if public != is_public {
            return Ok(None);
        }
        params.ensure_allowed(fields, fields.contains(&"symbol"))?;
        for key in required {
            if *key == "symbol" {
                params
                    .get("symbol")
                    .or_else(|| params.get("product_symbol"))
                    .ok_or_else(|| invalid("product_symbol or symbol is required"))?;
            } else if name == "modify_futures_tpsl_order" && *key == "size" {
                params.required(key)?;
            } else {
                nonempty(params, key)?;
            }
        }
        validate(name, params)?;
        if method == "GET" {
            let mut query = params.only(fields);
            if let Some(symbol) = params.get("product_symbol") {
                query.retain(|(key, _)| key != "symbol");
                query.push(("symbol".into(), self.exchange_symbol(symbol)?));
            }
            return Ok(Some(if public {
                self.public_get(path, query).await?
            } else {
                self.get_private(path, query).await?
            }));
        }
        let mut body = params.body(fields);
        if let Some(symbol) = params.get("product_symbol") {
            body.insert(
                "symbol".into(),
                Value::String(self.exchange_symbol(symbol)?),
            );
        }
        for key in arrays {
            if let Some(value) = params.json_optional(key)? {
                let items = value
                    .as_array()
                    .ok_or_else(|| invalid("expected a JSON array"))?;
                if items.is_empty() {
                    return Err(invalid(
                        "an explicitly provided cancellation list must not be empty",
                    ));
                }
                if *key == "symbolList" {
                    let mut symbols = Vec::new();
                    for item in items {
                        let symbol = item
                            .as_str()
                            .filter(|s| !s.trim().is_empty())
                            .ok_or_else(|| invalid("symbolList requires nonempty strings"))?;
                        symbols.push(Value::String(self.exchange_symbol(symbol)?));
                    }
                    body.insert((*key).into(), Value::Array(symbols));
                } else {
                    for item in items {
                        let object = item
                            .as_object()
                            .ok_or_else(|| invalid("orderIdList requires objects"))?;
                        if !["orderId", "clientOid"].iter().any(|key| {
                            object
                                .get(*key)
                                .and_then(Value::as_str)
                                .is_some_and(|s| !s.is_empty())
                        }) {
                            return Err(invalid("each cancellation requires orderId or clientOid"));
                        }
                    }
                    body.insert((*key).into(), value);
                }
            }
        }
        for key in numbers {
            if let Some(value) = params.get(key) {
                let number = value
                    .parse::<u64>()
                    .map_err(|_| invalid("requestId must be an integer"))?;
                if number > 999_999_999_999_999_999 {
                    return Err(invalid("requestId must have at most 18 digits"));
                }
                body.insert((*key).into(), Value::Number(number.into()));
            }
        }
        Ok(Some(self.post_private(path, Value::Object(body)).await?))
    }
}

use crate::exchanges::bitget::params::invalid;
fn enum_value(params: &BitgetParams, key: &str, choices: &[&str]) -> Result<()> {
    if params.get(key).is_some_and(|v| !choices.contains(&v)) {
        return Err(invalid(&format!("unsupported {key}")));
    }
    Ok(())
}
fn positive(params: &BitgetParams, key: &str, zero: bool) -> Result<()> {
    if let Some(value) = params.get(key).filter(|v| !v.is_empty())
        && !value
            .parse::<f64>()
            .is_ok_and(|v| v.is_finite() && (v > 0.0 || zero && v == 0.0))
    {
        return Err(invalid(&format!("invalid {key}")));
    }
    Ok(())
}
fn nonempty<'a>(params: &'a BitgetParams, key: &str) -> Result<&'a str> {
    params
        .get(key)
        .filter(|v| !v.trim().is_empty())
        .ok_or_else(|| invalid(&format!("{key} must not be empty")))
}
fn id(params: &BitgetParams) -> Result<()> {
    if !["orderId", "clientOid"]
        .iter()
        .any(|key| params.get(key).is_some_and(|v| !v.trim().is_empty()))
    {
        return Err(invalid("orderId or clientOid is required"));
    }
    Ok(())
}
pub(super) fn validate(name: &str, params: &BitgetParams) -> Result<()> {
    enum_value(
        params,
        "productType",
        &["USDT-FUTURES", "COIN-FUTURES", "USDC-FUTURES"],
    )?;
    enum_value(
        params,
        "category",
        &[
            "SPOT",
            "MARGIN",
            "USDT-FUTURES",
            "COIN-FUTURES",
            "USDC-FUTURES",
            "OTHER",
        ],
    )?;
    enum_value(params, "side", &["buy", "sell"])?;
    enum_value(params, "orderType", &["limit", "market"])?;
    enum_value(params, "marginMode", &["crossed", "isolated"])?;
    enum_value(params, "tradeSide", &["open", "close"])?;
    enum_value(params, "holdSide", &["long", "short", "buy", "sell"])?;
    enum_value(params, "posSide", &["long", "short"])?;
    enum_value(params, "reduceOnly", &["yes", "no"])?;
    enum_value(params, "autoCancel", &["yes", "no"])?;
    enum_value(params, "pxAmendType", &["yes", "no"])?;
    enum_value(
        params,
        "stpMode",
        &["none", "cancel_taker", "cancel_maker", "cancel_both"],
    )?;
    for key in [
        "triggerType",
        "stopSurplusTriggerType",
        "stopLossTriggerType",
        "newTriggerType",
        "newStopSurplusTriggerType",
        "newStopLossTriggerType",
    ] {
        enum_value(params, key, &["fill_price", "mark_price"])?;
    }
    for key in ["tpTriggerBy", "slTriggerBy"] {
        enum_value(params, key, &["market", "mark"])?;
    }
    for key in ["tpOrderType", "slOrderType"] {
        enum_value(params, key, &["limit", "market"])?;
    }
    for key in [
        "size",
        "qty",
        "price",
        "newSize",
        "newPrice",
        "triggerPrice",
        "newTriggerPrice",
        "stopSurplusSize",
        "stopLossSize",
    ] {
        positive(params, key, false)?;
    }
    for key in [
        "executePrice",
        "stopSurplusExecutePrice",
        "stopLossExecutePrice",
        "stopSurplusTriggerPrice",
        "stopLossTriggerPrice",
        "newPresetStopSurplusPrice",
        "newPresetStopLossPrice",
        "newStopSurplusTriggerPrice",
        "newStopLossTriggerPrice",
        "newStopSurplusExecutePrice",
        "newStopLossExecutePrice",
        "takeProfit",
        "stopLoss",
        "tpLimitPrice",
        "slLimitPrice",
    ] {
        positive(params, key, true)?;
    }
    for key in ["startTime", "endTime", "limit"] {
        if let Some(value) = params.get(key) {
            value
                .parse::<u64>()
                .map_err(|_| invalid(&format!("{key} must be an integer")))?;
        }
    }
    if let Some(limit) = params.get("limit")
        && !(1..=100).contains(&limit.parse::<u64>().unwrap())
    {
        return Err(invalid("limit must be 1..=100"));
    }
    if let (Some(start), Some(end)) = (params.get("startTime"), params.get("endTime")) {
        let (start, end) = (start.parse::<u64>().unwrap(), end.parse::<u64>().unwrap());
        let days = if ["get_uta_financial_records", "get_uta_position_history"].contains(&name) {
            30
        } else {
            90
        };
        if start > end || end - start > days * 86_400_000 {
            return Err(invalid("invalid query time range"));
        }
    }
    // https://www.bitget.com/docs/catalog/classic-contract-trade/classic-contract-trade#modify-order
    if name == "modify_futures_order"
        && params.get("newSize").is_some() != params.get("newPrice").is_some()
    {
        return Err(invalid("newSize and newPrice must be supplied together"));
    }
    match name {
        "modify_futures_order"
        | "modify_futures_plan_order"
        | "modify_futures_tpsl_order"
        | "modify_spot_plan_order"
        | "cancel_spot_plan_order"
        | "cancel_replace_spot_order"
        | "modify_uta_order" => {
            id(params)?;
        }
        _ => {}
    }
    if [
        "close_uta_positions",
        "get_uta_position_history",
        "adjust_uta_position_margin",
        "get_uta_open_interest",
        "get_uta_current_funding_rate",
    ]
    .contains(&name)
    {
        enum_value(
            params,
            "category",
            &["USDT-FUTURES", "COIN-FUTURES", "USDC-FUTURES"],
        )?;
    }
    match name {
        "set_uta_cancel_countdown" => {
            let value = params
                .required("countdown")?
                .parse::<u32>()
                .map_err(|_| invalid("countdown must be an integer"))?;
            if value != 0 && !(5..=60).contains(&value) {
                return Err(invalid("countdown must be 0 or 5..=60 seconds"));
            }
        }
        "adjust_futures_position_margin" => {
            if !params
                .required("amount")?
                .parse::<f64>()
                .is_ok_and(|v| v.is_finite() && v != 0.0)
            {
                return Err(invalid("amount must be a nonzero signed margin amount"));
            }
            enum_value(params, "holdSide", &["long", "short"])?;
        }
        "adjust_uta_position_margin" => {
            enum_value(params, "operation", &["add", "remove"])?;
            positive(params, "amount", false)?;
        }
        "place_futures_plan_order" => {
            enum_value(params, "planType", &["normal_plan", "track_plan"])?;
            if params.get("planType") == Some("track_plan") {
                if params.get("orderType") != Some("market")
                    || params.get("price").is_some_and(|v| !v.is_empty())
                {
                    return Err(invalid("trailing plan requires market order and no price"));
                }
                params.required("callbackRatio")?;
            } else if params.get("orderType") == Some("limit") {
                nonempty(params, "price")?;
            } else if params.get("price").is_some_and(|v| !v.is_empty()) {
                return Err(invalid("market plan must not include price"));
            }
            for prefix in ["stopSurplus", "stopLoss"] {
                let key = format!("{prefix}TriggerPrice");
                if params.get(&key).is_some_and(|v| !v.is_empty() && v != "0") {
                    let trigger = format!("{prefix}TriggerType");
                    params.required(&trigger)?;
                    if params.get("planType") == Some("track_plan") {
                        enum_value(params, &trigger, &["fill_price"])?;
                        let value = params
                            .required(&key)?
                            .parse::<f64>()
                            .map_err(|_| invalid("invalid trailing TP/SL percentage"))?;
                        if !(0.01..=999.99).contains(&value) {
                            return Err(invalid("trailing TP/SL percentage must be 0.01..=999.99"));
                        }
                    }
                }
                if params.get("planType") == Some("track_plan")
                    && params
                        .get(&format!("{prefix}ExecutePrice"))
                        .is_some_and(|v| !v.is_empty())
                {
                    return Err(invalid(
                        "trailing plans must not include TP/SL execute prices",
                    ));
                }
            }
        }
        "place_futures_tpsl_order" => {
            enum_value(
                params,
                "planType",
                &[
                    "profit_plan",
                    "loss_plan",
                    "moving_plan",
                    "pos_profit",
                    "pos_loss",
                ],
            )?;
            if ["profit_plan", "loss_plan", "moving_plan"].contains(&params.required("planType")?) {
                nonempty(params, "size")?;
            }
            if params.get("planType") == Some("moving_plan") {
                params.required("rangeRate")?;
                if params.get("executePrice").is_some_and(|v| !v.is_empty()) {
                    return Err(invalid("moving_plan uses market execution only"));
                }
            }
        }
        "place_futures_position_tpsl" => {
            if params.get("stopSurplusTriggerPrice").is_none()
                && params.get("stopLossTriggerPrice").is_none()
            {
                return Err(invalid("a TP or SL trigger is required"));
            }
        }
        "place_spot_plan_order" | "modify_spot_plan_order" => {
            enum_value(params, "planType", &["amount", "total"])?;
            if params.get("orderType") == Some("limit") {
                nonempty(params, "executePrice")?;
                positive(params, "executePrice", false)?;
            }
        }
        "get_uta_current_funding_rate" => {
            if params.get("category").is_none()
                && params
                    .get("product_symbol")
                    .or_else(|| params.get("symbol"))
                    .is_none()
            {
                return Err(invalid("category or symbol is required"));
            }
        }
        "modify_uta_order" => {
            if params.get("qty").is_none() && params.get("price").is_none() {
                return Err(invalid("qty or price is required"));
            }
        }
        _ => {}
    }
    positive(params, "rangeRate", false)?;
    for key in ["callbackRatio", "newCallbackRatio"] {
        if let Some(value) = params.get(key).filter(|s| !s.is_empty())
            && !value.parse::<f64>().is_ok_and(|v| v > 0.0 && v <= 10.0)
        {
            return Err(invalid("callback ratio must be > 0 and <= 10"));
        }
    }
    Ok(())
}
