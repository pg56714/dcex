use serde_json::{Map, Number, Value};

use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::MexcClient;
use super::endpoints::*;
use super::params::{
    add_pagination_defaults, require_one_identifier, validate_enum, validate_u64_range, MexcParams,
};
use super::signing::json_value_string;

const SPOT_ORDER_OPTIONAL_KEYS: &[&str] = &[
    "quantity",
    "quoteOrderQty",
    "price",
    "newClientOrderId",
    "stpMode",
    "recvWindow",
];

const CONTRACT_ORDER_KEYS: &[&str] = &[
    "side",
    "type",
    "openType",
    "vol",
    "price",
    "leverage",
    "externalOid",
    "positionId",
    "positionMode",
    "reduceOnly",
    "stopLossPrice",
    "takeProfitPrice",
    "lossTrend",
    "profitTrend",
    "priceProtect",
    "marketCeiling",
    "flashClose",
    "bboTypeNum",
    "stpMode",
];

const CONTRACT_ORDER_NUMBER_KEYS: &[&str] = &[
    "side",
    "type",
    "openType",
    "vol",
    "leverage",
    "positionId",
    "positionMode",
    "lossTrend",
    "profitTrend",
    "priceProtect",
    "bboTypeNum",
    "stpMode",
];

fn required_batch_string<'a>(
    order: &'a Map<String, Value>,
    index: usize,
    key: &str,
) -> Result<&'a str> {
    order
        .get(key)
        .and_then(Value::as_str)
        .filter(|value| !value.is_empty())
        .ok_or_else(|| {
            DcexError::InvalidInput(format!(
                "MEXC Spot batch order at index {index} requires string parameter {key}"
            ))
        })
}

impl MexcClient {
    pub(super) async fn trade_private_request(
        &self,
        method_name: &str,
        params: &MexcParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "test_spot_order" => {
                self.spot_order_from_params(SPOT_TEST_ORDER, params, None, None, None)
                    .await
            }
            "place_spot_order" => {
                self.spot_order_from_params(SPOT_ORDER, params, None, None, None)
                    .await
            }
            "place_spot_limit_order" => {
                self.spot_order_from_params(SPOT_ORDER, params, None, Some("LIMIT"), Some("GTC"))
                    .await
            }
            "place_spot_limit_buy_order" => {
                self.spot_order_from_params(
                    SPOT_ORDER,
                    params,
                    Some("BUY"),
                    Some("LIMIT"),
                    Some("GTC"),
                )
                .await
            }
            "place_spot_limit_sell_order" => {
                self.spot_order_from_params(
                    SPOT_ORDER,
                    params,
                    Some("SELL"),
                    Some("LIMIT"),
                    Some("GTC"),
                )
                .await
            }
            "place_spot_post_only_limit_order" => {
                self.spot_order_from_params(SPOT_ORDER, params, None, Some("LIMIT_MAKER"), None)
                    .await
            }
            "place_spot_post_only_limit_buy_order" => {
                self.spot_order_from_params(
                    SPOT_ORDER,
                    params,
                    Some("BUY"),
                    Some("LIMIT_MAKER"),
                    None,
                )
                .await
            }
            "place_spot_post_only_limit_sell_order" => {
                self.spot_order_from_params(
                    SPOT_ORDER,
                    params,
                    Some("SELL"),
                    Some("LIMIT_MAKER"),
                    None,
                )
                .await
            }
            "place_spot_market_order" => {
                self.spot_order_from_params(SPOT_ORDER, params, None, Some("MARKET"), None)
                    .await
            }
            "place_spot_market_buy_order" => {
                self.spot_order_from_params(SPOT_ORDER, params, Some("BUY"), Some("MARKET"), None)
                    .await
            }
            "place_spot_market_sell_order" => {
                self.spot_order_from_params(SPOT_ORDER, params, Some("SELL"), Some("MARKET"), None)
                    .await
            }
            "place_spot_batch_orders" => self.place_spot_batch_orders_from_params(params).await,
            "cancel_spot_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "orderId",
                    "origClientOrderId",
                    "newClientOrderId",
                    "recvWindow",
                ])?;
                require_one_identifier(params, &["orderId", "origClientOrderId"])?;
                let mut query = params.only(&[
                    "orderId",
                    "origClientOrderId",
                    "newClientOrderId",
                    "recvWindow",
                ]);
                self.push_required_product_symbol(&mut query, params, "")?;
                self.spot_private(HttpMethod::Delete, SPOT_ORDER, query)
                    .await
            }
            "cancel_spot_open_orders" => {
                params.ensure_allowed(&["product_symbol", "symbol", "recvWindow"])?;
                let mut query = params.only(&["recvWindow"]);
                self.push_required_product_symbol(&mut query, params, "")?;
                self.spot_private(HttpMethod::Delete, SPOT_OPEN_ORDERS, query)
                    .await
            }
            "get_spot_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "orderId",
                    "origClientOrderId",
                    "recvWindow",
                ])?;
                require_one_identifier(params, &["orderId", "origClientOrderId"])?;
                let mut query = params.only(&["orderId", "origClientOrderId", "recvWindow"]);
                self.push_product_symbol(&mut query, params, "")?;
                self.spot_private(HttpMethod::Get, SPOT_ORDER, query).await
            }
            "get_spot_open_orders" => {
                params.ensure_allowed(&["product_symbol", "symbol", "recvWindow"])?;
                let mut query = params.only(&["recvWindow"]);
                self.push_product_symbol(&mut query, params, "")?;
                self.spot_private(HttpMethod::Get, SPOT_OPEN_ORDERS, query)
                    .await
            }
            "get_spot_all_orders" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ])?;
                validate_u64_range(params, "limit", 1, 1_000)?;
                let mut query = params.only(&["startTime", "endTime", "limit", "recvWindow"]);
                self.push_required_product_symbol(&mut query, params, "")?;
                self.spot_private(HttpMethod::Get, SPOT_ALL_ORDERS, query)
                    .await
            }
            "get_spot_my_trades" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "orderId",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ])?;
                validate_u64_range(params, "limit", 1, 100)?;
                let mut query =
                    params.only(&["orderId", "startTime", "endTime", "limit", "recvWindow"]);
                self.push_required_product_symbol(&mut query, params, "")?;
                self.spot_private(HttpMethod::Get, SPOT_MY_TRADES, query)
                    .await
            }
            "place_contract_order" => self.contract_order_from_params(params, None, None).await,
            "place_contract_limit_order" => {
                self.contract_order_from_params(params, None, Some(1)).await
            }
            "place_contract_limit_buy_order" => {
                self.contract_order_from_params(params, Some(1), Some(1))
                    .await
            }
            "place_contract_limit_sell_order" => {
                self.contract_order_from_params(params, Some(3), Some(1))
                    .await
            }
            "place_contract_post_only_order" => {
                self.contract_order_from_params(params, None, Some(2)).await
            }
            "place_contract_post_only_buy_order" => {
                self.contract_order_from_params(params, Some(1), Some(2))
                    .await
            }
            "place_contract_post_only_sell_order" => {
                self.contract_order_from_params(params, Some(3), Some(2))
                    .await
            }
            "place_contract_market_order" => {
                self.contract_order_from_params(params, None, Some(5)).await
            }
            "place_contract_market_buy_order" => {
                self.contract_order_from_params(params, Some(1), Some(5))
                    .await
            }
            "place_contract_market_sell_order" => {
                self.contract_order_from_params(params, Some(3), Some(5))
                    .await
            }
            "cancel_contract_orders" => self.cancel_contract_orders_from_params(params).await,
            "cancel_contract_order" => {
                params.ensure_allowed(&["order_id", "orderId"])?;
                let order_id = params
                    .required("order_id")
                    .or_else(|_| params.required("orderId"))?;
                self.contract_post_json(
                    CONTRACT_CANCEL_ORDERS,
                    Value::Array(vec![Value::String(order_id.to_string())]),
                )
                .await
            }
            "cancel_contract_order_with_external_id" => {
                params.ensure_allowed(&["product_symbol", "symbol", "externalOid"])?;
                let mut body = params.body(&["externalOid"], &[], &[]);
                params.required("externalOid")?;
                self.insert_required_product_symbol(&mut body, params, "_")?;
                self.contract_post_json(
                    CONTRACT_CANCEL_ORDER_WITH_EXTERNAL_ID,
                    Value::Array(vec![Value::Object(body)]),
                )
                .await
            }
            "cancel_all_contract_orders" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut body = Map::new();
                self.insert_product_symbol(&mut body, params, "_")?;
                if !body.contains_key("symbol") {
                    body.insert("symbol".to_string(), Value::String(String::new()));
                }
                self.contract_post_json(CONTRACT_CANCEL_ALL_ORDERS, Value::Object(body))
                    .await
            }
            "get_contract_open_orders" => {
                params.ensure_allowed(&["product_symbol", "symbol", "page_num", "page_size"])?;
                validate_u64_range(params, "page_num", 1, u64::MAX)?;
                validate_u64_range(params, "page_size", 1, 100)?;
                let mut query = params.only(&["page_num", "page_size"]);
                let path =
                    if params.get("product_symbol").is_some() || params.get("symbol").is_some() {
                        format!(
                            "{CONTRACT_OPEN_ORDERS}/{}",
                            self.required_contract_symbol(params)?
                        )
                    } else {
                        CONTRACT_OPEN_ORDERS.to_string()
                    };
                add_pagination_defaults(&mut query);
                self.contract_get(&path, query).await
            }
            "get_contract_history_orders" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "states",
                    "category",
                    "start_time",
                    "end_time",
                    "page_num",
                    "page_size",
                    "orderId",
                ])?;
                validate_u64_range(params, "page_num", 1, u64::MAX)?;
                validate_u64_range(params, "page_size", 1, 100)?;
                let mut query = params.only(&[
                    "states",
                    "category",
                    "start_time",
                    "end_time",
                    "page_num",
                    "page_size",
                    "orderId",
                ]);
                self.push_product_symbol(&mut query, params, "_")?;
                add_pagination_defaults(&mut query);
                self.contract_get(CONTRACT_HISTORY_ORDERS, query).await
            }
            "get_contract_order_by_external_id" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "external_oid",
                    "externalOid",
                ])?;
                let symbol = self.required_contract_symbol(params)?;
                let external_oid = params
                    .required("external_oid")
                    .or_else(|_| params.required("externalOid"))?;
                let path = CONTRACT_EXTERNAL_ORDER
                    .replace("{symbol}", &symbol)
                    .replace("{external_oid}", external_oid);
                self.contract_get(&path, Vec::new()).await
            }
            "get_contract_order" => {
                params.ensure_allowed(&["order_id", "orderId"])?;
                let order_id = params
                    .required("order_id")
                    .or_else(|_| params.required("orderId"))?;
                let path = CONTRACT_ORDER.replace("{order_id}", order_id);
                self.contract_get(&path, Vec::new()).await
            }
            "get_contract_orders" => {
                params.ensure_allowed(&["order_ids"])?;
                let order_ids = joined_order_ids(params.required("order_ids")?)?;
                if order_ids.split(',').count() > 50 {
                    return Err(DcexError::InvalidInput(
                        "MEXC batch order query supports at most 50 order IDs".to_string(),
                    ));
                }
                self.contract_get(
                    CONTRACT_BATCH_QUERY,
                    vec![("order_ids".to_string(), order_ids)],
                )
                .await
            }
            "get_contract_order_deal_details" => {
                params.ensure_allowed(&["order_id", "orderId"])?;
                let order_id = params
                    .required("order_id")
                    .or_else(|_| params.required("orderId"))?;
                let path = CONTRACT_ORDER_DEAL_DETAILS.replace("{order_id}", order_id);
                self.contract_get(&path, Vec::new()).await
            }
            "get_contract_order_deals" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "start_time",
                    "end_time",
                    "page_num",
                    "page_size",
                ])?;
                validate_u64_range(params, "page_num", 1, u64::MAX)?;
                validate_u64_range(params, "page_size", 1, 1_000)?;
                let mut query = params.only(&["start_time", "end_time", "page_num", "page_size"]);
                self.push_required_product_symbol(&mut query, params, "_")?;
                add_pagination_defaults(&mut query);
                self.contract_get(CONTRACT_ORDER_DEALS, query).await
            }
            "get_contract_plan_orders" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "states",
                    "side",
                    "start_time",
                    "end_time",
                    "page_num",
                    "page_size",
                ])?;
                validate_u64_range(params, "page_num", 1, u64::MAX)?;
                validate_u64_range(params, "page_size", 1, 100)?;
                let mut query = params.only(&[
                    "states",
                    "side",
                    "start_time",
                    "end_time",
                    "page_num",
                    "page_size",
                ]);
                self.push_product_symbol(&mut query, params, "_")?;
                add_pagination_defaults(&mut query);
                self.contract_get(CONTRACT_PLAN_ORDERS, query).await
            }
            "place_contract_plan_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "price",
                    "vol",
                    "leverage",
                    "side",
                    "openType",
                    "triggerPrice",
                    "triggerType",
                    "executeCycle",
                    "orderType",
                    "trend",
                    "externalOid",
                    "priceProtect",
                    "positionMode",
                    "lossTrend",
                    "profitTrend",
                    "stopLossPrice",
                    "takeProfitPrice",
                    "reduceOnly",
                ])?;
                let mut body = params.body(
                    &[
                        "price",
                        "vol",
                        "leverage",
                        "side",
                        "openType",
                        "triggerPrice",
                        "triggerType",
                        "executeCycle",
                        "orderType",
                        "trend",
                        "externalOid",
                        "priceProtect",
                        "positionMode",
                        "lossTrend",
                        "profitTrend",
                        "stopLossPrice",
                        "takeProfitPrice",
                        "reduceOnly",
                    ],
                    &[
                        "vol",
                        "leverage",
                        "side",
                        "openType",
                        "triggerPrice",
                        "triggerType",
                        "executeCycle",
                        "orderType",
                        "trend",
                        "priceProtect",
                        "positionMode",
                        "lossTrend",
                        "profitTrend",
                    ],
                    &["reduceOnly"],
                );
                for key in [
                    "vol",
                    "leverage",
                    "side",
                    "openType",
                    "triggerPrice",
                    "triggerType",
                    "executeCycle",
                    "orderType",
                    "trend",
                ] {
                    params.required(key)?;
                }
                self.insert_required_product_symbol(&mut body, params, "_")?;
                self.contract_post_json(CONTRACT_PLACE_PLAN_ORDER, Value::Object(body))
                    .await
            }
            "cancel_contract_plan_orders" => {
                params.ensure_allowed(&["orders"])?;
                let orders = params.json_required("orders")?;
                let Value::Array(ref values) = orders else {
                    return Err(DcexError::InvalidInput(
                        "MEXC plan orders must be a JSON array".to_string(),
                    ));
                };
                if values.is_empty() || values.len() > 50 {
                    return Err(DcexError::InvalidInput(
                        "MEXC plan order cancellation requires 1 to 50 orders".to_string(),
                    ));
                }
                self.contract_post_json(CONTRACT_CANCEL_PLAN_ORDERS, orders)
                    .await
            }
            "cancel_all_contract_plan_orders" => {
                params.ensure_allowed(&["product_symbol", "symbol"])?;
                let mut body = Map::new();
                self.insert_product_symbol(&mut body, params, "_")?;
                self.contract_post_json(CONTRACT_CANCEL_ALL_PLAN_ORDERS, Value::Object(body))
                    .await
            }
            "get_contract_stop_orders" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "is_finished",
                    "state",
                    "type",
                    "start_time",
                    "end_time",
                    "page_num",
                    "page_size",
                ])?;
                validate_enum(params, "is_finished", &["0", "1"])?;
                validate_enum(params, "state", &["1", "2", "3", "4", "5"])?;
                validate_enum(params, "type", &["1", "2"])?;
                validate_u64_range(params, "page_num", 1, u64::MAX)?;
                validate_u64_range(params, "page_size", 1, 100)?;
                let mut query = params.only(&[
                    "is_finished",
                    "state",
                    "type",
                    "start_time",
                    "end_time",
                    "page_num",
                    "page_size",
                ]);
                self.push_product_symbol(&mut query, params, "_")?;
                add_pagination_defaults(&mut query);
                self.contract_get(CONTRACT_STOP_ORDERS, query).await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }

    async fn spot_order_from_params(
        &self,
        endpoint: &str,
        params: &MexcParams,
        side_override: Option<&str>,
        type_override: Option<&str>,
        _default_time_in_force: Option<&str>,
    ) -> Result<ValidatedResponse> {
        params.ensure_allowed(&[
            "product_symbol",
            "symbol",
            "side",
            "type",
            "quantity",
            "quoteOrderQty",
            "price",
            "newClientOrderId",
            "stpMode",
            "recvWindow",
        ])?;
        let mut query = Vec::new();
        self.push_required_product_symbol(&mut query, params, "")?;
        let side = match side_override {
            Some(side) => side,
            None => params.required("side")?,
        };
        let order_type = match type_override {
            Some(order_type) => order_type,
            None => params.required("type")?,
        };
        if !matches!(side, "BUY" | "SELL") {
            return Err(DcexError::InvalidInput(format!(
                "unsupported MEXC Spot order side: {side}"
            )));
        }
        if !matches!(
            order_type,
            "LIMIT" | "MARKET" | "LIMIT_MAKER" | "IMMEDIATE_OR_CANCEL" | "FILL_OR_KILL"
        ) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported MEXC Spot order type: {order_type}"
            )));
        }
        match order_type {
            "MARKET" => {
                if params.get("quantity").is_none() && params.get("quoteOrderQty").is_none() {
                    return Err(DcexError::InvalidInput(
                        "MEXC Spot MARKET orders require quantity or quoteOrderQty".to_string(),
                    ));
                }
            }
            _ => {
                params.required("quantity")?;
                params.required("price")?;
            }
        }
        validate_enum(
            params,
            "stpMode",
            &["", "CANCEL_MAKER", "CANCEL_TAKER", "CANCEL_BOTH"],
        )?;
        validate_u64_range(params, "recvWindow", 1, 60_000)?;
        query.push(("side".to_string(), side.to_string()));
        query.push(("type".to_string(), order_type.to_string()));
        query.extend(params.only(SPOT_ORDER_OPTIONAL_KEYS));
        self.spot_private(HttpMethod::Post, endpoint, query).await
    }

    async fn place_spot_batch_orders_from_params(
        &self,
        params: &MexcParams,
    ) -> Result<ValidatedResponse> {
        params.ensure_allowed(&["batchOrders", "recvWindow"])?;
        validate_u64_range(params, "recvWindow", 1, 60_000)?;
        let orders = params.json_required("batchOrders")?;
        let Value::Array(mut orders) = orders else {
            return Err(DcexError::InvalidInput(
                "batchOrders must be a JSON array.".to_string(),
            ));
        };
        if orders.is_empty() || orders.len() > 20 {
            return Err(DcexError::InvalidInput(
                "MEXC Spot batch orders require 1 to 20 orders".to_string(),
            ));
        }
        let mut batch_symbol: Option<String> = None;
        for (index, order) in orders.iter_mut().enumerate() {
            let Value::Object(order) = order else {
                return Err(DcexError::InvalidInput(format!(
                    "MEXC Spot batch order at index {index} must be a JSON object"
                )));
            };
            const ALLOWED_KEYS: &[&str] = &[
                "product_symbol",
                "symbol",
                "side",
                "type",
                "quantity",
                "quoteOrderQty",
                "price",
                "newClientOrderId",
                "stpMode",
            ];
            if let Some(key) = order
                .keys()
                .find(|key| !ALLOWED_KEYS.contains(&key.as_str()))
            {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported MEXC Spot batch order parameter: {key}"
                )));
            }
            if order.contains_key("product_symbol") && order.contains_key("symbol") {
                return Err(DcexError::InvalidInput(format!(
                    "MEXC Spot batch order at index {index} cannot include both product_symbol and symbol"
                )));
            }
            if let Some(product_symbol) = order.remove("product_symbol") {
                let symbol = self.exchange_symbol(&json_value_string(&product_symbol), "")?;
                order.insert("symbol".to_string(), Value::String(symbol));
            }
            let symbol = required_batch_string(order, index, "symbol")?;
            if batch_symbol
                .as_ref()
                .is_some_and(|expected| expected != symbol)
            {
                return Err(DcexError::InvalidInput(
                    "MEXC Spot batch orders must use the same symbol".to_string(),
                ));
            }
            batch_symbol.get_or_insert_with(|| symbol.to_string());

            let side = required_batch_string(order, index, "side")?;
            if !matches!(side, "BUY" | "SELL") {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported MEXC Spot batch order side: {side}"
                )));
            }
            let order_type = required_batch_string(order, index, "type")?;
            if !matches!(
                order_type,
                "LIMIT" | "MARKET" | "LIMIT_MAKER" | "IMMEDIATE_OR_CANCEL" | "FILL_OR_KILL"
            ) {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported MEXC Spot batch order type: {order_type}"
                )));
            }
            match order_type {
                "MARKET" => {
                    if !order.contains_key("quantity") && !order.contains_key("quoteOrderQty") {
                        return Err(DcexError::InvalidInput(format!(
                            "MEXC Spot MARKET batch order at index {index} requires quantity or quoteOrderQty"
                        )));
                    }
                }
                _ => {
                    for key in ["quantity", "price"] {
                        if !order.contains_key(key) {
                            return Err(DcexError::InvalidInput(format!(
                                "MEXC Spot batch order at index {index} requires {key}"
                            )));
                        }
                    }
                }
            }
            if let Some(stp_mode) = order.get("stpMode").map(json_value_string) {
                if !matches!(
                    stp_mode.as_str(),
                    "CANCEL_MAKER" | "CANCEL_TAKER" | "CANCEL_BOTH"
                ) {
                    return Err(DcexError::InvalidInput(format!(
                        "unsupported MEXC Spot batch order stpMode: {stp_mode}"
                    )));
                }
            }
        }
        let mut query = vec![(
            "batchOrders".to_string(),
            serde_json::to_string(&orders).map_err(|error| DcexError::Decode(error.to_string()))?,
        )];
        query.extend(params.only(&["recvWindow"]));
        self.spot_private(HttpMethod::Post, SPOT_BATCH_ORDERS, query)
            .await
    }

    async fn contract_order_from_params(
        &self,
        params: &MexcParams,
        side_override: Option<i64>,
        type_override: Option<i64>,
    ) -> Result<ValidatedResponse> {
        params.ensure_allowed(&[
            "product_symbol",
            "symbol",
            "side",
            "type",
            "openType",
            "vol",
            "price",
            "leverage",
            "externalOid",
            "positionId",
            "positionMode",
            "reduceOnly",
            "stopLossPrice",
            "takeProfitPrice",
            "lossTrend",
            "profitTrend",
            "priceProtect",
            "marketCeiling",
            "flashClose",
            "bboTypeNum",
            "stpMode",
        ])?;
        for key in ["openType", "vol"] {
            params.required(key)?;
        }
        let side = side_override
            .map(|value| value.to_string())
            .or_else(|| params.get("side").map(ToString::to_string))
            .ok_or_else(|| {
                DcexError::InvalidInput("missing required parameter: side".to_string())
            })?;
        let order_type = type_override
            .map(|value| value.to_string())
            .or_else(|| params.get("type").map(ToString::to_string))
            .ok_or_else(|| {
                DcexError::InvalidInput("missing required parameter: type".to_string())
            })?;
        if !["1", "2", "3", "4"].contains(&side.as_str()) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported MEXC Contract order side: {side}"
            )));
        }
        if !["1", "2", "3", "4", "5"].contains(&order_type.as_str()) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported MEXC Contract order type: {order_type}"
            )));
        }
        validate_enum(params, "openType", &["1", "2"])?;
        validate_enum(params, "positionMode", &["1", "2"])?;
        validate_enum(params, "lossTrend", &["1", "2", "3"])?;
        validate_enum(params, "profitTrend", &["1", "2", "3"])?;
        validate_enum(params, "priceProtect", &["0", "1"])?;
        validate_enum(params, "bboTypeNum", &["0", "1", "2", "3", "4"])?;
        validate_enum(params, "stpMode", &["0", "1", "2", "3"])?;
        if matches!(side.as_str(), "1" | "3") {
            params.required("leverage")?;
        }
        if order_type != "5" {
            params.required("price")?;
        }
        let mut body = params.body(
            CONTRACT_ORDER_KEYS,
            CONTRACT_ORDER_NUMBER_KEYS,
            &["reduceOnly", "marketCeiling", "flashClose"],
        );
        self.insert_required_product_symbol(&mut body, params, "_")?;
        if let Some(side) = side_override {
            body.insert("side".to_string(), Value::Number(Number::from(side)));
        }
        if let Some(order_type) = type_override {
            body.insert("type".to_string(), Value::Number(Number::from(order_type)));
        }
        if order_type == "5" && !body.contains_key("price") {
            body.insert("price".to_string(), Value::String("0".to_string()));
        }
        self.contract_post_json(CONTRACT_CREATE_ORDER, Value::Object(body))
            .await
    }

    async fn cancel_contract_orders_from_params(
        &self,
        params: &MexcParams,
    ) -> Result<ValidatedResponse> {
        params.ensure_allowed(&["orders"])?;
        let orders = params.json_required("orders")?;
        let Value::Array(orders) = orders else {
            return Err(DcexError::InvalidInput(
                "orders must be a JSON array.".to_string(),
            ));
        };
        if orders.is_empty() || orders.len() > 50 {
            return Err(DcexError::InvalidInput(
                "MEXC Contract cancellation requires 1 to 50 order IDs".to_string(),
            ));
        }
        let mut order_ids = Vec::with_capacity(orders.len());
        for (index, order) in orders.into_iter().enumerate() {
            let order_id = match order {
                Value::Object(mut object) => {
                    if object.len() != 1 || !object.contains_key("orderId") {
                        return Err(DcexError::InvalidInput(format!(
                            "MEXC Contract cancellation object at index {index} must contain only orderId"
                        )));
                    }
                    object.remove("orderId").expect("validated")
                }
                Value::String(_) | Value::Number(_) => order,
                _ => {
                    return Err(DcexError::InvalidInput(format!(
                        "MEXC Contract cancellation order ID at index {index} must be a string or integer"
                    )));
                }
            };
            order_ids.push(order_id);
        }
        self.contract_post_json(CONTRACT_CANCEL_ORDERS, Value::Array(order_ids))
            .await
    }

    fn required_contract_symbol(&self, params: &MexcParams) -> Result<String> {
        if let Some(symbol) = params.get("symbol") {
            return self.exchange_symbol(symbol, "_");
        }
        self.exchange_symbol(params.required("product_symbol")?, "_")
    }
}

fn joined_order_ids(value: &str) -> Result<String> {
    if let Ok(Value::Array(values)) = serde_json::from_str::<Value>(value) {
        return Ok(values
            .iter()
            .map(json_value_string)
            .collect::<Vec<_>>()
            .join(","));
    }
    Ok(value.to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn preserves_current_contract_order_fields() {
        let params = MexcParams::from_pairs(vec![
            ("positionId".to_string(), "7".to_string()),
            ("lossTrend".to_string(), "2".to_string()),
            ("marketCeiling".to_string(), "true".to_string()),
            ("bboTypeNum".to_string(), "1".to_string()),
            ("stpMode".to_string(), "3".to_string()),
        ]);
        let body = params.body(
            CONTRACT_ORDER_KEYS,
            CONTRACT_ORDER_NUMBER_KEYS,
            &["reduceOnly", "marketCeiling", "flashClose"],
        );
        assert_eq!(body.get("positionId"), Some(&Value::from(7)));
        assert_eq!(body.get("marketCeiling"), Some(&Value::Bool(true)));
        assert!(body.contains_key("lossTrend"));
        assert!(body.contains_key("bboTypeNum"));
        assert!(body.contains_key("stpMode"));
    }

    #[test]
    fn uses_current_futures_order_paths() {
        assert_eq!(
            CONTRACT_OPEN_ORDERS,
            "/api/v1/private/order/list/open_orders"
        );
        assert_eq!(
            CONTRACT_PLACE_PLAN_ORDER,
            "/api/v1/private/planorder/place/v2"
        );
    }

    #[test]
    fn supplies_required_pagination_defaults() {
        let mut query = Vec::new();
        add_pagination_defaults(&mut query);
        assert_eq!(
            query,
            vec![
                ("page_num".to_string(), "1".to_string()),
                ("page_size".to_string(), "20".to_string()),
            ]
        );
    }
}
