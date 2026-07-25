use serde_json::{Map, Value};

use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::{KucoinClient, KucoinMarket};
use super::endpoints::*;
use super::params::{
    bool_value, generate_client_oid, insert_required_string, insert_truthy_bool, json_value_string,
    require_exactly_one, validate_client_oid, validate_enum, validate_positive_number,
    validate_positive_u64, validate_text_length, validate_time_range, validate_u64_range,
    KucoinParams,
};

const SPOT_ORDER_STRING_KEYS: &[&str] = &[
    "size",
    "funds",
    "price",
    "clientOid",
    "stp",
    "tags",
    "remark",
    "timeInForce",
    "visibleSize",
];
const SPOT_ORDER_INTEGER_KEYS: &[&str] = &["cancelAfter", "allowMaxTimeWindow", "clientTimestamp"];
const SPOT_ORDER_BOOL_KEYS: &[&str] = &["postOnly", "hidden", "iceberg"];
const SPOT_TRADE_HISTORY_KEYS: &[&str] = &[
    "orderId", "side", "type", "lastId", "startAt", "endAt", "limit",
];
const FUTURES_ORDER_STRING_KEYS: &[&str] = &[
    "price",
    "qty",
    "valueQty",
    "clientOid",
    "marginMode",
    "positionSide",
    "timeInForce",
    "stop",
    "stopPriceType",
    "stopPrice",
    "stp",
    "remark",
    "visibleSize",
];
const FUTURES_ORDER_INTEGER_KEYS: &[&str] = &["leverage"];
const FUTURES_ORDER_BOOL_KEYS: &[&str] = &[
    "postOnly",
    "reduceOnly",
    "closeOrder",
    "forceHold",
    "hidden",
    "iceberg",
];
const FUTURES_ORDER_LIST_KEYS: &[&str] = &[
    "status",
    "side",
    "type",
    "startAt",
    "endAt",
    "currentPage",
    "pageSize",
];
const FUTURES_TRADE_HISTORY_KEYS: &[&str] = &[
    "orderId",
    "side",
    "type",
    "tradeTypes",
    "startAt",
    "endAt",
    "currentPage",
    "pageSize",
];

impl KucoinClient {
    pub(super) async fn trade_private_request(
        &self,
        method_name: &str,
        params: &KucoinParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "place_spot_order" => self.spot_order_from_params(params, None, None, false).await,
            "place_spot_market_order" => {
                self.spot_order_from_params(params, None, Some("market"), false)
                    .await
            }
            "place_spot_market_buy_order" => {
                self.spot_order_from_params(params, Some("buy"), Some("market"), false)
                    .await
            }
            "place_spot_market_sell_order" => {
                self.spot_order_from_params(params, Some("sell"), Some("market"), false)
                    .await
            }
            "place_spot_limit_order" => {
                self.spot_order_from_params(params, None, Some("limit"), false)
                    .await
            }
            "place_spot_limit_buy_order" => {
                self.spot_order_from_params(params, Some("buy"), Some("limit"), false)
                    .await
            }
            "place_spot_limit_sell_order" => {
                self.spot_order_from_params(params, Some("sell"), Some("limit"), false)
                    .await
            }
            "place_spot_post_only_limit_order" => {
                self.spot_order_from_params(params, None, Some("limit"), true)
                    .await
            }
            "place_spot_post_only_limit_buy_order" => {
                self.spot_order_from_params(params, Some("buy"), Some("limit"), true)
                    .await
            }
            "place_spot_post_only_limit_sell_order" => {
                self.spot_order_from_params(params, Some("sell"), Some("limit"), true)
                    .await
            }
            "place_spot_batch_orders" => self.spot_batch_orders_from_params(params, None).await,
            "place_spot_batch_limit_orders" => {
                self.spot_batch_orders_from_params(params, Some("limit"))
                    .await
            }
            "place_spot_batch_market_orders" => {
                self.spot_batch_orders_from_params(params, Some("market"))
                    .await
            }
            "cancel_spot_order" => {
                params.ensure_allowed(&["orderId", "product_symbol", "symbol"])?;
                let order_id = params.required("orderId")?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params, false)?;
                self.private_delete(
                    KucoinMarket::Spot,
                    SPOT_CANCEL_ORDER.replace("{orderId}", order_id),
                    query,
                )
                .await
            }
            "cancel_spot_all_orders_by_symbol" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params, false)?;
                self.private_delete(KucoinMarket::Spot, SPOT_CANCEL_ALL_ORDERS_BY_SYMBOL, query)
                    .await
            }
            "cancel_spot_all_orders" => {
                params.ensure_allowed(&[])?;
                self.private_delete(KucoinMarket::Spot, SPOT_CANCEL_ALL_ORDERS, Vec::new())
                    .await
            }
            "get_spot_open_orders" => {
                params.ensure_allowed(&["product_symbol", "symbol", "pageNum", "pageSize"])?;
                params.required_any(&["product_symbol", "symbol"])?;
                validate_u64_range(params, "pageNum", 1, u64::MAX)?;
                validate_u64_range(params, "pageSize", 1, 50)?;
                let mut query = params.only(&["pageNum", "pageSize"]);
                self.push_required_symbol(&mut query, params, false)?;
                self.private_get(KucoinMarket::Spot, SPOT_OPEN_ORDERS, query)
                    .await
            }
            "get_spot_trade_history" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "orderId",
                    "side",
                    "type",
                    "lastId",
                    "startAt",
                    "endAt",
                    "limit",
                ])?;
                params.required_any(&["product_symbol", "symbol"])?;
                validate_enum(params, "side", &["buy", "sell"])?;
                validate_enum(params, "type", &["limit", "market"])?;
                validate_u64_range(params, "lastId", 0, u64::MAX)?;
                validate_u64_range(params, "limit", 1, 100)?;
                validate_time_range(params, "startAt", "endAt", Some(7 * 24 * 60 * 60 * 1000))?;
                let mut query = params.only(SPOT_TRADE_HISTORY_KEYS);
                self.push_required_symbol(&mut query, params, false)?;
                self.private_get(KucoinMarket::Spot, SPOT_TRADE_HISTORY, query)
                    .await
            }
            "place_futures_order" => {
                self.futures_order_from_params(params, None, None, false)
                    .await
            }
            "place_futures_market_order" => {
                self.futures_order_from_params(params, None, Some("market"), false)
                    .await
            }
            "place_futures_market_buy_order" => {
                self.futures_order_from_params(params, Some("buy"), Some("market"), false)
                    .await
            }
            "place_futures_market_sell_order" => {
                self.futures_order_from_params(params, Some("sell"), Some("market"), false)
                    .await
            }
            "place_futures_limit_order" => {
                self.futures_order_from_params(params, None, Some("limit"), false)
                    .await
            }
            "place_futures_limit_buy_order" => {
                self.futures_order_from_params(params, Some("buy"), Some("limit"), false)
                    .await
            }
            "place_futures_limit_sell_order" => {
                self.futures_order_from_params(params, Some("sell"), Some("limit"), false)
                    .await
            }
            "place_futures_post_only_limit_order" => {
                self.futures_order_from_params(params, None, Some("limit"), true)
                    .await
            }
            "place_futures_post_only_limit_buy_order" => {
                self.futures_order_from_params(params, Some("buy"), Some("limit"), true)
                    .await
            }
            "place_futures_post_only_limit_sell_order" => {
                self.futures_order_from_params(params, Some("sell"), Some("limit"), true)
                    .await
            }
            "get_futures_order_list" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "status",
                    "side",
                    "type",
                    "startAt",
                    "endAt",
                    "currentPage",
                    "pageSize",
                ])?;
                validate_enum(params, "status", &["active", "done"])?;
                validate_enum(params, "side", &["buy", "sell"])?;
                validate_enum(
                    params,
                    "type",
                    &[
                        "limit",
                        "market",
                        "limit_stop",
                        "market_stop",
                        "oco_limit",
                        "oco_stop",
                    ],
                )?;
                validate_u64_range(params, "currentPage", 1, u64::MAX)?;
                validate_u64_range(params, "pageSize", 1, 1000)?;
                validate_time_range(params, "startAt", "endAt", Some(7 * 24 * 60 * 60 * 1000))?;
                let mut query = params.only(FUTURES_ORDER_LIST_KEYS);
                self.push_optional_symbol(&mut query, params, true)?;
                self.private_get(KucoinMarket::Futures, FUTURES_ORDER_LIST, query)
                    .await
            }
            "get_futures_order" => {
                params.ensure_allowed(&["orderId"])?;
                let order_id = params.required("orderId")?;
                self.private_get(
                    KucoinMarket::Futures,
                    FUTURES_ORDER.replace("{orderId}", order_id),
                    Vec::new(),
                )
                .await
            }
            "get_futures_order_by_client_oid" => {
                params.ensure_allowed(&["clientOid"])?;
                let query = vec![(
                    "clientOid".to_string(),
                    params.required("clientOid")?.to_string(),
                )];
                self.private_get(KucoinMarket::Futures, FUTURES_ORDER_BY_CLIENT_OID, query)
                    .await
            }
            "cancel_futures_order" => {
                params.ensure_allowed(&["orderId"])?;
                let order_id = params.required("orderId")?;
                self.private_delete(
                    KucoinMarket::Futures,
                    FUTURES_CANCEL_ORDER.replace("{orderId}", order_id),
                    Vec::new(),
                )
                .await
            }
            "cancel_futures_order_by_client_oid" => {
                params.ensure_allowed(&["clientOid", "product_symbol", "symbol"])?;
                let client_oid = params.required("clientOid")?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params, true)?;
                self.private_delete(
                    KucoinMarket::Futures,
                    FUTURES_CANCEL_ORDER_BY_CLIENT_OID.replace("{clientOid}", client_oid),
                    query,
                )
                .await
            }
            "cancel_futures_all_orders" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params, true)?;
                self.private_delete(KucoinMarket::Futures, FUTURES_CANCEL_ALL_ORDERS, query)
                    .await
            }
            "get_futures_open_order_value" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params, true)?;
                self.private_get(KucoinMarket::Futures, FUTURES_OPEN_ORDER_VALUE, query)
                    .await
            }
            "get_futures_trade_history" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "orderId",
                    "side",
                    "type",
                    "tradeTypes",
                    "startAt",
                    "endAt",
                    "currentPage",
                    "pageSize",
                ])?;
                validate_enum(params, "side", &["buy", "sell"])?;
                validate_enum(
                    params,
                    "type",
                    &["limit", "market", "limit_stop", "market_stop"],
                )?;
                validate_u64_range(params, "currentPage", 1, u64::MAX)?;
                validate_u64_range(params, "pageSize", 1, 1000)?;
                validate_time_range(params, "startAt", "endAt", Some(7 * 24 * 60 * 60 * 1000))?;
                let mut query = params.only(FUTURES_TRADE_HISTORY_KEYS);
                self.push_optional_symbol(&mut query, params, true)?;
                self.private_get(KucoinMarket::Futures, FUTURES_TRADE_HISTORY, query)
                    .await
            }
            "get_futures_recent_trade_history" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params, true)?;
                self.private_get(KucoinMarket::Futures, FUTURES_RECENT_TRADE_HISTORY, query)
                    .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }

    async fn spot_order_from_params(
        &self,
        params: &KucoinParams,
        side_override: Option<&str>,
        type_override: Option<&str>,
        post_only: bool,
    ) -> Result<ValidatedResponse> {
        validate_spot_order(params, side_override, type_override, post_only)?;
        let mut body = params.body(
            SPOT_ORDER_STRING_KEYS,
            SPOT_ORDER_INTEGER_KEYS,
            SPOT_ORDER_BOOL_KEYS,
        )?;
        self.insert_required_body_symbol(&mut body, params, false)?;
        let side = match side_override {
            Some(side) => side,
            None => params.required("side")?,
        };
        let order_type = match type_override {
            Some(order_type) => order_type,
            None => params.required("type")?,
        };
        insert_required_string(&mut body, "side", side);
        insert_required_string(&mut body, "type", order_type);
        insert_truthy_bool(&mut body, "postOnly", post_only);
        self.private_post(KucoinMarket::Spot, SPOT_PLACE_ORDER, Value::Object(body))
            .await
    }

    async fn spot_batch_orders_from_params(
        &self,
        params: &KucoinParams,
        type_override: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let orders = params.json_required("orders")?;
        let orders = orders.as_array().ok_or_else(|| {
            DcexError::InvalidInput("KuCoin orders must be a JSON array.".to_string())
        })?;
        if orders.is_empty() || orders.len() > 20 {
            return Err(DcexError::InvalidInput(
                "KuCoin batch orders must contain between 1 and 20 orders.".to_string(),
            ));
        }
        let mut order_list = Vec::with_capacity(orders.len());
        for order in orders {
            let mut order = order.as_object().cloned().ok_or_else(|| {
                DcexError::InvalidInput("KuCoin batch order must be a JSON object.".to_string())
            })?;
            if let Some(order_type) = type_override {
                order.insert("type".to_string(), Value::String(order_type.to_string()));
            }
            let order_params = KucoinParams::from_pairs(
                order
                    .iter()
                    .map(|(key, value)| (key.clone(), json_value_string(value)))
                    .collect(),
            );
            validate_spot_order(&order_params, None, None, false)?;
            let symbol = order
                .remove("symbol")
                .or_else(|| order.get("product_symbol").cloned());
            order.remove("product_symbol");
            if let Some(symbol) = symbol.map(|value| json_value_string(&value)) {
                order.insert(
                    "symbol".to_string(),
                    Value::String(self.exchange_symbol(&symbol, false)?),
                );
            }
            for key in SPOT_ORDER_STRING_KEYS {
                if let Some(value) = order.get_mut(*key) {
                    *value = Value::String(json_value_string(value));
                }
            }
            for key in SPOT_ORDER_INTEGER_KEYS {
                if let Some(value) = order.get_mut(*key) {
                    let parsed = json_value_string(value).parse::<i64>().map_err(|_| {
                        DcexError::InvalidInput(format!(
                            "KuCoin batch order field {key} must be an integer"
                        ))
                    })?;
                    *value = Value::Number(parsed.into());
                }
            }
            for key in SPOT_ORDER_BOOL_KEYS {
                if let Some(value) = order.get_mut(*key) {
                    let parsed = bool_value(&json_value_string(value)).ok_or_else(|| {
                        DcexError::InvalidInput(format!(
                            "KuCoin batch order field {key} must be true or false"
                        ))
                    })?;
                    *value = Value::Bool(parsed);
                }
            }
            order_list.push(Value::Object(order));
        }
        let mut body = Map::new();
        body.insert("orderList".to_string(), Value::Array(order_list));
        self.private_post(KucoinMarket::Spot, SPOT_BATCH_ORDERS, Value::Object(body))
            .await
    }

    async fn futures_order_from_params(
        &self,
        params: &KucoinParams,
        side_override: Option<&str>,
        type_override: Option<&str>,
        post_only: bool,
    ) -> Result<ValidatedResponse> {
        let close_order = bool_param(params, "closeOrder")?.unwrap_or(false);
        validate_futures_order(params, side_override, type_override, post_only, close_order)?;
        let mut body = params.body(
            FUTURES_ORDER_STRING_KEYS,
            FUTURES_ORDER_INTEGER_KEYS,
            FUTURES_ORDER_BOOL_KEYS,
        )?;
        self.insert_required_body_symbol(&mut body, params, true)?;
        let client_oid = params
            .get("clientOid")
            .map(str::to_string)
            .unwrap_or_else(generate_client_oid);
        insert_required_string(&mut body, "clientOid", &client_oid);
        let order_type = match type_override {
            Some(order_type) => order_type,
            None => params.get("type").unwrap_or("limit"),
        };
        if !close_order {
            let side = match side_override {
                Some(side) => side,
                None => params.required("side")?,
            };
            insert_required_string(&mut body, "side", side);
            if let Some(size) = params.get("size") {
                let size = size.parse::<u64>().map_err(|_| {
                    DcexError::InvalidInput(
                        "KuCoin parameter size must be a positive integer".to_string(),
                    )
                })?;
                body.insert("size".to_string(), Value::Number(size.into()));
            }
        }
        insert_required_string(&mut body, "type", order_type);
        insert_truthy_bool(&mut body, "postOnly", post_only);
        self.private_post(
            KucoinMarket::Futures,
            FUTURES_PLACE_ORDER,
            Value::Object(body),
        )
        .await
    }

    fn insert_required_body_symbol(
        &self,
        body: &mut Map<String, Value>,
        params: &KucoinParams,
        futures: bool,
    ) -> Result<()> {
        body.insert(
            "symbol".to_string(),
            Value::String(
                self.exchange_symbol(params.required_any(&["product_symbol", "symbol"])?, futures)?,
            ),
        );
        Ok(())
    }
}

fn validate_spot_order(
    params: &KucoinParams,
    side_override: Option<&str>,
    type_override: Option<&str>,
    force_post_only: bool,
) -> Result<()> {
    params.ensure_allowed(&[
        "product_symbol",
        "symbol",
        "side",
        "type",
        "size",
        "funds",
        "price",
        "clientOid",
        "stp",
        "tags",
        "remark",
        "timeInForce",
        "cancelAfter",
        "postOnly",
        "hidden",
        "iceberg",
        "visibleSize",
        "allowMaxTimeWindow",
        "clientTimestamp",
    ])?;
    params.required_any(&["product_symbol", "symbol"])?;
    let side = side_override.unwrap_or(params.required("side")?);
    if !matches!(side, "buy" | "sell") {
        return Err(DcexError::InvalidInput(format!(
            "unsupported KuCoin side: {side}"
        )));
    }
    let order_type = type_override.unwrap_or(params.required("type")?);
    if !matches!(order_type, "limit" | "market") {
        return Err(DcexError::InvalidInput(format!(
            "unsupported KuCoin type: {order_type}"
        )));
    }
    validate_enum(params, "stp", &["DC", "CO", "CN", "CB"])?;
    validate_enum(params, "timeInForce", &["GTC", "GTT", "IOC", "FOK"])?;
    validate_client_oid(params, "clientOid")?;
    validate_text_length(params, "tags", 20, true)?;
    validate_text_length(params, "remark", 20, true)?;
    for key in ["size", "funds", "price", "visibleSize"] {
        validate_positive_number(params, key)?;
    }
    for key in ["postOnly", "hidden", "iceberg"] {
        bool_param(params, key)?;
    }
    validate_u64_range(params, "cancelAfter", 1, 2_591_999)?;
    validate_positive_u64(params, "allowMaxTimeWindow")?;
    validate_positive_u64(params, "clientTimestamp")?;
    if params.get("allowMaxTimeWindow").is_some() {
        params.required("clientTimestamp")?;
    }

    let post_only = force_post_only || bool_param(params, "postOnly")?.unwrap_or(false);
    let hidden = bool_param(params, "hidden")?.unwrap_or(false);
    let iceberg = bool_param(params, "iceberg")?.unwrap_or(false);
    match order_type {
        "limit" => {
            params.required("price")?;
            params.required("size")?;
            if params.get("funds").is_some() {
                return Err(DcexError::InvalidInput(
                    "KuCoin limit orders do not support funds".to_string(),
                ));
            }
            if params.get("cancelAfter").is_some()
                && params.get("timeInForce").unwrap_or("GTC") != "GTT"
            {
                return Err(DcexError::InvalidInput(
                    "KuCoin cancelAfter requires timeInForce=GTT".to_string(),
                ));
            }
            if post_only && matches!(params.get("timeInForce"), Some("IOC" | "FOK")) {
                return Err(DcexError::InvalidInput(
                    "KuCoin postOnly is incompatible with IOC and FOK".to_string(),
                ));
            }
            if post_only && (hidden || iceberg) {
                return Err(DcexError::InvalidInput(
                    "KuCoin postOnly is incompatible with hidden and iceberg".to_string(),
                ));
            }
            if params.get("visibleSize").is_some() && !iceberg {
                return Err(DcexError::InvalidInput(
                    "KuCoin visibleSize requires iceberg=true".to_string(),
                ));
            }
        }
        "market" => {
            require_exactly_one(params, &["size", "funds"])?;
            if [
                "price",
                "timeInForce",
                "cancelAfter",
                "postOnly",
                "hidden",
                "iceberg",
                "visibleSize",
            ]
            .iter()
            .any(|key| params.get(key).is_some())
                || force_post_only
            {
                return Err(DcexError::InvalidInput(
                    "KuCoin market orders include unsupported limit-order fields".to_string(),
                ));
            }
        }
        _ => unreachable!(),
    }
    Ok(())
}

fn validate_futures_order(
    params: &KucoinParams,
    side_override: Option<&str>,
    type_override: Option<&str>,
    force_post_only: bool,
    close_order: bool,
) -> Result<()> {
    params.ensure_allowed(&[
        "product_symbol",
        "symbol",
        "side",
        "type",
        "size",
        "qty",
        "valueQty",
        "price",
        "clientOid",
        "leverage",
        "marginMode",
        "positionSide",
        "timeInForce",
        "postOnly",
        "reduceOnly",
        "closeOrder",
        "forceHold",
        "hidden",
        "iceberg",
        "visibleSize",
        "stop",
        "stopPriceType",
        "stopPrice",
        "stp",
        "remark",
    ])?;
    params.required_any(&["product_symbol", "symbol"])?;
    validate_client_oid(params, "clientOid")?;
    validate_text_length(params, "remark", 100, false)?;
    validate_enum(params, "marginMode", &["ISOLATED", "CROSS"])?;
    validate_enum(params, "positionSide", &["BOTH", "LONG", "SHORT"])?;
    validate_enum(params, "timeInForce", &["GTC", "IOC", "RPI"])?;
    validate_enum(params, "stop", &["down", "up"])?;
    validate_enum(params, "stopPriceType", &["TP", "MP", "IP"])?;
    validate_enum(params, "stp", &["CN", "CO", "CB"])?;
    validate_positive_u64(params, "size")?;
    validate_positive_u64(params, "leverage")?;
    for key in ["qty", "valueQty", "price", "visibleSize", "stopPrice"] {
        validate_positive_number(params, key)?;
    }
    for key in [
        "postOnly",
        "reduceOnly",
        "closeOrder",
        "forceHold",
        "hidden",
        "iceberg",
    ] {
        bool_param(params, key)?;
    }

    let order_type = type_override.unwrap_or(params.get("type").unwrap_or("limit"));
    if !matches!(order_type, "limit" | "market") {
        return Err(DcexError::InvalidInput(format!(
            "unsupported KuCoin type: {order_type}"
        )));
    }
    let post_only = force_post_only || bool_param(params, "postOnly")?.unwrap_or(false);
    let hidden = bool_param(params, "hidden")?.unwrap_or(false);
    let iceberg = bool_param(params, "iceberg")?.unwrap_or(false);

    if close_order {
        if side_override.is_some()
            || ["side", "size", "qty", "valueQty", "leverage"]
                .iter()
                .any(|key| params.get(key).is_some())
        {
            return Err(DcexError::InvalidInput(
                "KuCoin closeOrder requires side, size, qty, valueQty, and leverage to be omitted"
                    .to_string(),
            ));
        }
    } else {
        let side = side_override.unwrap_or(params.required("side")?);
        if !matches!(side, "buy" | "sell") {
            return Err(DcexError::InvalidInput(format!(
                "unsupported KuCoin side: {side}"
            )));
        }
        require_exactly_one(params, &["size", "qty", "valueQty"])?;
    }

    if order_type == "limit" {
        params.required("price")?;
        if post_only && params.get("timeInForce") == Some("IOC") {
            return Err(DcexError::InvalidInput(
                "KuCoin postOnly is incompatible with IOC".to_string(),
            ));
        }
        if post_only && (hidden || iceberg) {
            return Err(DcexError::InvalidInput(
                "KuCoin postOnly is incompatible with hidden and iceberg".to_string(),
            ));
        }
        if params.get("visibleSize").is_some() && !iceberg {
            return Err(DcexError::InvalidInput(
                "KuCoin visibleSize requires iceberg=true".to_string(),
            ));
        }
        if iceberg && params.get("size").is_none() {
            return Err(DcexError::InvalidInput(
                "KuCoin iceberg orders require quantity in size lots".to_string(),
            ));
        }
    } else if params.get("price").is_some()
        || params.get("timeInForce").is_some()
        || post_only
        || hidden
        || iceberg
        || params.get("visibleSize").is_some()
    {
        return Err(DcexError::InvalidInput(
            "KuCoin market orders include unsupported limit-order fields".to_string(),
        ));
    }

    let stop_fields = ["stop", "stopPriceType", "stopPrice"];
    let stop_count = stop_fields
        .iter()
        .filter(|key| params.get(key).is_some())
        .count();
    if stop_count != 0 && stop_count != stop_fields.len() {
        return Err(DcexError::InvalidInput(
            "KuCoin stop, stopPriceType, and stopPrice must be provided together".to_string(),
        ));
    }
    Ok(())
}

fn bool_param(params: &KucoinParams, key: &str) -> Result<Option<bool>> {
    params
        .get(key)
        .map(|value| {
            bool_value(value).ok_or_else(|| {
                DcexError::InvalidInput(format!("KuCoin parameter {key} must be true or false"))
            })
        })
        .transpose()
}
