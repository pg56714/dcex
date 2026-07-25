use serde_json::{Map, Value};

use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::BitmexClient;
use super::endpoints::*;
use super::params::{
    json_or_string, validate_bool, validate_comma_separated_enum, validate_enum, validate_i64,
    validate_json_object, validate_number, validate_u64_range, BitmexParams,
};

const SIDES: &[&str] = &["Buy", "Sell"];
const ORDER_TYPES: &[&str] = &[
    "Limit",
    "Market",
    "Stop",
    "StopLimit",
    "MarketIfTouched",
    "LimitIfTouched",
    "Block",
    "Pegged",
    "MarketWithLeftOverAsLimit",
];
const TIME_IN_FORCE: &[&str] = &[
    "FillOrKill",
    "ImmediateOrCancel",
    "Day",
    "GoodTillCancel",
    "AtTheClose",
];
const PEG_PRICE_TYPES: &[&str] = &[
    "MarketPeg",
    "PrimaryPeg",
    "TrailingStopPeg",
    "MidPricePeg",
    "LastPeg",
];
const EXEC_INST: &[&str] = &[
    "ParticipateDoNotInitiate",
    "PostOnly",
    "PostOnlyReprice",
    "DMMReprice",
    "AllOrNone",
    "MarkPrice",
    "IndexPrice",
    "LastPrice",
    "Close",
    "ReduceOnly",
    "Fixed",
    "LastWithinMark",
];
const POOLS: &[&str] = &["Primary", "Secondary", "Aggregated"];
const STRATEGIES: &[&str] = &["OneWay", "Long", "Short"];

const ORDER_STRING_KEYS: &[&str] = &[
    "side",
    "ordType",
    "clOrdID",
    "clOrdLinkID",
    "contingencyType",
    "execInst",
    "pegPriceType",
    "timeInForce",
    "text",
    "expiryTime",
    "pool",
    "strategy",
];
const ORDER_NUMBER_KEYS: &[&str] = &[
    "orderQty",
    "price",
    "stopPx",
    "displayQty",
    "pegOffsetValue",
    "targetAccountId",
    "maxSlippagePct",
];
const AMEND_STRING_KEYS: &[&str] = &["orderID", "origClOrdID", "clOrdID", "text", "expiryTime"];
const AMEND_NUMBER_KEYS: &[&str] = &[
    "leavesQty",
    "orderQty",
    "price",
    "stopPx",
    "pegOffsetValue",
    "targetAccountId",
    "maxSlippagePct",
];
const CANCEL_STRING_KEYS: &[&str] = &["text"];
const CANCEL_NUMBER_KEYS: &[&str] = &["targetAccountId"];
const CANCEL_JSON_KEYS: &[&str] = &["orderID", "clOrdID"];
const CANCEL_ALL_STRING_KEYS: &[&str] = &["text"];
const CANCEL_ALL_NUMBER_KEYS: &[&str] = &["targetAccountId"];
const CANCEL_ALL_JSON_KEYS: &[&str] = &["filter", "targetAccountIds"];
const QUERY_ORDER_KEYS: &[&str] = &[
    "targetAccountId",
    "pool",
    "filter",
    "columns",
    "count",
    "start",
    "reverse",
    "startTime",
    "endTime",
    "targetAccountIds",
    "targetAccountIds[]",
];

const ORDER_ALLOWED_KEYS: &[&str] = &[
    "product_symbol",
    "symbol",
    "side",
    "ordType",
    "clOrdID",
    "clOrdLinkID",
    "contingencyType",
    "execInst",
    "pegPriceType",
    "timeInForce",
    "text",
    "expiryTime",
    "pool",
    "strategy",
    "orderQty",
    "price",
    "stopPx",
    "displayQty",
    "pegOffsetValue",
    "targetAccountId",
    "maxSlippagePct",
];

impl BitmexClient {
    pub(super) async fn trade_private_request(
        &self,
        method_name: &str,
        params: &BitmexParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "place_order" => self.order_from_params(params, None, None, None).await,
            "place_market_order" => {
                self.order_from_params(params, None, Some("Market"), None)
                    .await
            }
            "place_market_buy_order" => {
                self.order_from_params(params, Some("Buy"), Some("Market"), None)
                    .await
            }
            "place_market_sell_order" => {
                self.order_from_params(params, Some("Sell"), Some("Market"), None)
                    .await
            }
            "place_limit_order" => {
                self.order_from_params(
                    params,
                    None,
                    Some("Limit"),
                    Some(("timeInForce", "GoodTillCancel")),
                )
                .await
            }
            "place_limit_buy_order" => {
                self.order_from_params(
                    params,
                    Some("Buy"),
                    Some("Limit"),
                    Some(("timeInForce", "GoodTillCancel")),
                )
                .await
            }
            "place_limit_sell_order" => {
                self.order_from_params(
                    params,
                    Some("Sell"),
                    Some("Limit"),
                    Some(("timeInForce", "GoodTillCancel")),
                )
                .await
            }
            "place_post_only_order" => {
                self.order_from_params(
                    params,
                    None,
                    Some("Limit"),
                    Some(("execInst", "ParticipateDoNotInitiate")),
                )
                .await
            }
            "place_post_only_buy_order" => {
                self.order_from_params(
                    params,
                    Some("Buy"),
                    Some("Limit"),
                    Some(("execInst", "ParticipateDoNotInitiate")),
                )
                .await
            }
            "place_post_only_sell_order" => {
                self.order_from_params(
                    params,
                    Some("Sell"),
                    Some("Limit"),
                    Some(("execInst", "ParticipateDoNotInitiate")),
                )
                .await
            }
            "amend_order" => {
                let body = self.amend_order_body_from_params(params)?;
                self.private_json(HttpMethod::Put, AMEND_ORDER, Value::Object(body))
                    .await
            }
            "cancel_order" => {
                let body = self.cancel_order_body_from_params(params)?;
                self.private_json(HttpMethod::Delete, CANCEL_ORDER, Value::Object(body))
                    .await
            }
            "cancel_all_orders" => {
                let body = self.cancel_all_orders_body_from_params(params)?;
                self.private_json(HttpMethod::Delete, CANCEL_ALL_ORDERS, Value::Object(body))
                    .await
            }
            "set_cancel_all_after" => {
                params.ensure_allowed(&["timeout", "targetAccountId"])?;
                params.required("timeout")?;
                validate_u64_range(params, "timeout", 0, 86_400_000)?;
                validate_i64(params, "targetAccountId")?;
                let body = params.body(&[], &["timeout", "targetAccountId"], &[], &[]);
                self.private_json(HttpMethod::Post, CANCEL_ALL_AFTER, Value::Object(body))
                    .await
            }
            "get_order" => {
                let mut allowed = QUERY_ORDER_KEYS.to_vec();
                allowed.extend(["product_symbol", "symbol"]);
                params.ensure_allowed(&allowed)?;
                validate_json_object(params, "filter")?;
                validate_enum(params, "pool", POOLS)?;
                validate_u64_range(params, "count", 0, 500)?;
                validate_u64_range(params, "start", 0, i32::MAX as u64)?;
                validate_bool(params, "reverse")?;
                validate_i64(params, "targetAccountId")?;
                let mut query = params.only(QUERY_ORDER_KEYS);
                self.push_product_symbol(&mut query, params)?;
                self.get_private(QUERY_ORDER, query).await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }

    async fn order_from_params(
        &self,
        params: &BitmexParams,
        side_override: Option<&str>,
        ord_type_override: Option<&str>,
        default_pair: Option<(&str, &str)>,
    ) -> Result<ValidatedResponse> {
        let body =
            self.order_body_from_params(params, side_override, ord_type_override, default_pair)?;
        self.private_json(HttpMethod::Post, PLACE_ORDER, Value::Object(body))
            .await
    }

    pub(super) fn order_body_from_params(
        &self,
        params: &BitmexParams,
        side_override: Option<&str>,
        ord_type_override: Option<&str>,
        default_pair: Option<(&str, &str)>,
    ) -> Result<Map<String, Value>> {
        params.ensure_allowed(ORDER_ALLOWED_KEYS)?;
        self.validate_order_params(params)?;
        let mut body = params.body(ORDER_STRING_KEYS, ORDER_NUMBER_KEYS, &[], &[]);
        self.insert_required_product_symbol(&mut body, params)?;
        if let Some(side) = side_override {
            body.insert("side".to_string(), Value::String(side.to_string()));
        }
        if let Some(ord_type) = ord_type_override {
            body.insert("ordType".to_string(), Value::String(ord_type.to_string()));
        } else if !body.contains_key("ordType") {
            let inferred_order_type = if body.contains_key("pegPriceType") {
                Some("Pegged")
            } else if body.contains_key("price") && body.contains_key("stopPx") {
                Some("StopLimit")
            } else if body.contains_key("stopPx") {
                Some("Stop")
            } else if body.contains_key("price") {
                Some("Limit")
            } else {
                None
            };
            if let Some(order_type) = inferred_order_type {
                body.insert("ordType".to_string(), Value::String(order_type.to_string()));
            }
        }
        if let Some((key, value)) = default_pair {
            body.entry(key.to_string())
                .or_insert_with(|| Value::String(value.to_string()));
        }
        validate_order_requirements(&body)?;
        Ok(body)
    }

    pub(super) fn amend_order_body_from_params(
        &self,
        params: &BitmexParams,
    ) -> Result<Map<String, Value>> {
        let mut allowed = AMEND_STRING_KEYS.to_vec();
        allowed.extend(AMEND_NUMBER_KEYS);
        allowed.extend(["product_symbol", "symbol"]);
        params.ensure_allowed(&allowed)?;
        if params.get("orderID").is_none() && params.get("origClOrdID").is_none() {
            return Err(DcexError::InvalidInput(
                "Either orderID or origClOrdID must be provided".to_string(),
            ));
        }
        if params.get("clOrdID").is_some() && params.get("origClOrdID").is_none() {
            return Err(DcexError::InvalidInput(
                "BitMEX clOrdID amendment requires origClOrdID".to_string(),
            ));
        }
        if ["leavesQty", "orderQty"]
            .iter()
            .filter(|key| params.get(key).is_some())
            .count()
            > 1
        {
            return Err(DcexError::InvalidInput(
                "BitMEX amend_order accepts only one quantity field".to_string(),
            ));
        }
        validate_client_order_id(params.get("clOrdID"))?;
        for key in AMEND_NUMBER_KEYS {
            if matches!(*key, "leavesQty" | "orderQty" | "targetAccountId") {
                validate_i64(params, key)?;
            } else {
                validate_number(params, key)?;
            }
        }
        let mut body = params.body(AMEND_STRING_KEYS, AMEND_NUMBER_KEYS, &[], &[]);
        self.insert_product_symbol(&mut body, params)?;
        Ok(body)
    }

    pub(super) fn cancel_order_body_from_params(
        &self,
        params: &BitmexParams,
    ) -> Result<Map<String, Value>> {
        params.ensure_allowed(&["orderID", "clOrdID", "targetAccountId", "text"])?;
        if params.get("orderID").is_none() && params.get("clOrdID").is_none() {
            return Err(DcexError::InvalidInput(
                "Either orderID or clOrdID must be provided".to_string(),
            ));
        }
        validate_i64(params, "targetAccountId")?;
        let mut body = params.body(CANCEL_STRING_KEYS, CANCEL_NUMBER_KEYS, &[], &[]);
        for key in CANCEL_JSON_KEYS {
            if let Some(value) = params.get(key) {
                body.insert((*key).to_string(), identifier_array(key, value)?);
            }
        }
        Ok(body)
    }

    pub(super) fn cancel_all_orders_body_from_params(
        &self,
        params: &BitmexParams,
    ) -> Result<Map<String, Value>> {
        params.ensure_allowed(&[
            "product_symbol",
            "symbol",
            "filter",
            "targetAccountId",
            "targetAccountIds",
            "text",
        ])?;
        validate_json_object(params, "filter")?;
        validate_i64(params, "targetAccountId")?;
        let mut body = params.body(
            CANCEL_ALL_STRING_KEYS,
            CANCEL_ALL_NUMBER_KEYS,
            &[],
            CANCEL_ALL_JSON_KEYS,
        );
        if let Some(value) = params.get("targetAccountIds") {
            body.insert(
                "targetAccountIds".to_string(),
                identifier_array("targetAccountIds", value)?,
            );
        }
        self.insert_product_symbol(&mut body, params)?;
        Ok(body)
    }

    fn validate_order_params(&self, params: &BitmexParams) -> Result<()> {
        validate_enum(params, "side", SIDES)?;
        validate_enum(params, "ordType", ORDER_TYPES)?;
        validate_enum(
            params,
            "contingencyType",
            &["OneCancelsTheOther", "OneTriggersTheOther"],
        )?;
        validate_comma_separated_enum(params, "execInst", EXEC_INST)?;
        validate_enum(params, "pegPriceType", PEG_PRICE_TYPES)?;
        validate_enum(params, "timeInForce", TIME_IN_FORCE)?;
        validate_enum(params, "pool", POOLS)?;
        validate_enum(params, "strategy", STRATEGIES)?;
        validate_client_order_id(params.get("clOrdID"))?;
        if params.get("contingencyType").is_some() && params.get("clOrdLinkID").is_none() {
            return Err(DcexError::InvalidInput(
                "BitMEX contingencyType requires clOrdLinkID".to_string(),
            ));
        }
        for key in ORDER_NUMBER_KEYS {
            if matches!(*key, "orderQty" | "displayQty" | "targetAccountId") {
                validate_i64(params, key)?;
            } else {
                validate_number(params, key)?;
            }
        }
        Ok(())
    }
}

fn validate_client_order_id(value: Option<&str>) -> Result<()> {
    if value.is_some_and(|value| value.len() > 36) {
        return Err(DcexError::InvalidInput(
            "BitMEX clOrdID cannot exceed 36 characters".to_string(),
        ));
    }
    Ok(())
}

fn identifier_array(key: &str, value: &str) -> Result<Value> {
    let parsed = json_or_string(value);
    let values = match parsed {
        Value::Array(values) => values,
        Value::String(value) if !value.trim().is_empty() => vec![Value::String(value)],
        _ => {
            return Err(DcexError::InvalidInput(format!(
                "BitMEX parameter {key} must contain one or more string identifiers"
            )));
        }
    };
    if values.is_empty()
        || values
            .iter()
            .any(|value| !value.as_str().is_some_and(|value| !value.trim().is_empty()))
    {
        return Err(DcexError::InvalidInput(format!(
            "BitMEX parameter {key} must contain one or more string identifiers"
        )));
    }
    Ok(Value::Array(values))
}

fn validate_order_requirements(body: &Map<String, Value>) -> Result<()> {
    let order_type = body.get("ordType").and_then(Value::as_str);
    let exec_inst = body.get("execInst").and_then(Value::as_str).unwrap_or("");
    let close_order = exec_inst
        .split(',')
        .map(str::trim)
        .any(|item| item == "Close");
    let require = |key: &str| {
        if body.contains_key(key) {
            Ok(())
        } else {
            Err(DcexError::InvalidInput(format!(
                "BitMEX {order_type:?} order requires {key}"
            )))
        }
    };

    match order_type {
        Some("Limit") => {
            require("orderQty")?;
            require("price")?;
        }
        Some("Stop") | Some("MarketIfTouched") => {
            if !close_order {
                require("orderQty")?;
            }
            require("stopPx")?;
        }
        Some("StopLimit") | Some("LimitIfTouched") => {
            if !close_order {
                require("orderQty")?;
            }
            require("stopPx")?;
            require("price")?;
        }
        Some("Pegged") => {
            require("pegPriceType")?;
            require("pegOffsetValue")?;
            if !exec_inst
                .split(',')
                .map(str::trim)
                .any(|item| item == "Fixed")
            {
                return Err(DcexError::InvalidInput(
                    "BitMEX Pegged order requires execInst=Fixed".to_string(),
                ));
            }
        }
        Some("Market") | Some("Block") | Some("MarketWithLeftOverAsLimit") | None => {}
        Some(value) => {
            return Err(DcexError::InvalidInput(format!(
                "unsupported BitMEX ordType: {value}"
            )));
        }
    }

    if body.get("pool").and_then(Value::as_str) == Some("Secondary")
        && !exec_inst.split(',').map(str::trim).any(|item| {
            matches!(
                item,
                "ParticipateDoNotInitiate" | "PostOnly" | "PostOnlyReprice"
            )
        })
    {
        return Err(DcexError::InvalidInput(
            "BitMEX Secondary pool orders require a passive execInst".to_string(),
        ));
    }
    if exec_inst
        .split(',')
        .map(str::trim)
        .any(|item| item == "AllOrNone")
        && body.get("displayQty").and_then(Value::as_i64) != Some(0)
    {
        return Err(DcexError::InvalidInput(
            "BitMEX AllOrNone orders require displayQty=0".to_string(),
        ));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;
    use std::time::Duration;

    #[test]
    fn preserves_v2_order_expiry_and_slippage_fields() {
        let params = BitmexParams::from_pairs(vec![
            (
                "expiryTime".to_string(),
                "2026-11-05T00:00:00.555Z".to_string(),
            ),
            ("maxSlippagePct".to_string(), "1.5".to_string()),
        ]);
        let body = params.body(ORDER_STRING_KEYS, ORDER_NUMBER_KEYS, &[], &[]);
        assert!(body.contains_key("expiryTime"));
        assert_eq!(body.get("maxSlippagePct"), Some(&Value::from(1.5)));
    }

    #[test]
    fn infers_stop_limit_and_enforces_conditional_fields() {
        let client = BitmexClient::public(Duration::from_secs(1)).expect("client");
        let valid = BitmexParams::from_pairs(vec![
            ("product_symbol".to_string(), "XBT-USD-SWAP".to_string()),
            ("orderQty".to_string(), "10".to_string()),
            ("price".to_string(), "90000".to_string()),
            ("stopPx".to_string(), "91000".to_string()),
        ]);
        let body = client
            .order_body_from_params(&valid, None, None, None)
            .expect("stop limit");
        assert_eq!(body.get("ordType"), Some(&Value::from("StopLimit")));

        let invalid = BitmexParams::from_pairs(vec![
            ("product_symbol".to_string(), "XBT-USD-SWAP".to_string()),
            ("ordType".to_string(), "Limit".to_string()),
            ("price".to_string(), "90000".to_string()),
        ]);
        assert!(client
            .order_body_from_params(&invalid, None, None, None)
            .is_err());
    }

    #[test]
    fn secondary_pool_requires_passive_execution_instruction() {
        let client = BitmexClient::public(Duration::from_secs(1)).expect("client");
        let invalid = BitmexParams::from_pairs(vec![
            ("product_symbol".to_string(), "XBT-USD-SWAP".to_string()),
            ("orderQty".to_string(), "10".to_string()),
            ("price".to_string(), "90000".to_string()),
            ("pool".to_string(), "Secondary".to_string()),
        ]);
        assert!(client
            .order_body_from_params(&invalid, None, None, None)
            .is_err());

        let valid = BitmexParams::from_pairs(vec![
            ("product_symbol".to_string(), "XBT-USD-SWAP".to_string()),
            ("orderQty".to_string(), "10".to_string()),
            ("price".to_string(), "90000".to_string()),
            ("pool".to_string(), "Secondary".to_string()),
            ("execInst".to_string(), "PostOnlyReprice".to_string()),
        ]);
        assert!(client
            .order_body_from_params(&valid, None, None, None)
            .is_ok());
    }

    #[test]
    fn normalizes_single_cancel_identifier_to_array() {
        let client = BitmexClient::public(Duration::from_secs(1)).expect("client");
        let params =
            BitmexParams::from_pairs(vec![("clOrdID".to_string(), "client-order-1".to_string())]);
        let body = client
            .cancel_order_body_from_params(&params)
            .expect("cancel body");
        assert_eq!(body.get("clOrdID"), Some(&json!(["client-order-1"])));
    }
}
