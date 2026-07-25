use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::BingxClient;
use super::endpoints::*;
use super::params::{
    batch_orders_query, bool_or_string, comma_list, normalize_side, push_optional,
    python_list_string, require_one_identifier, validate_bool, validate_client_id, validate_enum,
    validate_json_object, validate_page_window, validate_positive_number, validate_time_range,
    validate_u64_range, BingxParams,
};

const SPOT_ORDER_TYPES: &[&str] = &[
    "MARKET",
    "LIMIT",
    "TAKE_STOP_LIMIT",
    "TAKE_STOP_MARKET",
    "TRIGGER_LIMIT",
    "TRIGGER_MARKET",
];
const SWAP_ORDER_TYPES: &[&str] = &[
    "MARKET",
    "LIMIT",
    "STOP_MARKET",
    "STOP",
    "TAKE_PROFIT_MARKET",
    "TAKE_PROFIT",
    "TRAILING_STOP_MARKET",
    "TRAILING_TP_SL",
    "TRIGGER_LIMIT",
    "TRIGGER_MARKET",
];
const TIME_IN_FORCE_VALUES: &[&str] = &["GTC", "IOC", "FOK", "PostOnly"];

const SPOT_ORDER_OPTIONAL_KEYS: &[&str] = &[
    "timeInForce",
    "quantity",
    "quoteOrderQty",
    "price",
    "stopPrice",
    "newClientOrderId",
    "recvWindow",
];

const SWAP_ORDER_OPTIONAL_KEYS: &[&str] = &[
    "positionSide",
    "reduceOnly",
    "price",
    "quantity",
    "quoteOrderQty",
    "stopPrice",
    "priceRate",
    "stopLoss",
    "takeProfit",
    "workingType",
    "clientOrderId",
    "recvWindow",
    "timeInForce",
    "closePosition",
    "activationPrice",
    "stopGuaranteed",
    "positionId",
];

const SWAP_REPLACE_OPTIONAL_KEYS: &[&str] = &[
    "reduceOnly",
    "price",
    "quantity",
    "quoteOrderQty",
    "cancelRestrictions",
    "stopPrice",
    "priceRate",
    "workingType",
    "stopLoss",
    "takeProfit",
    "clientOrderId",
    "closePosition",
    "activationPrice",
    "stopGuaranteed",
    "timeInForce",
    "positionId",
    "recvWindow",
];

impl BingxClient {
    pub(super) async fn trade_private_request(
        &self,
        method_name: &str,
        params: &BingxParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "place_spot_order" => self.spot_order_from_params(params, None, None, None).await,
            "place_spot_market_buy_order" => {
                self.spot_order_from_params(params, Some("BUY"), Some("MARKET"), None)
                    .await
            }
            "place_spot_market_sell_order" => {
                self.spot_order_from_params(params, Some("SELL"), Some("MARKET"), None)
                    .await
            }
            "place_spot_limit_order" => {
                self.spot_order_from_params(params, None, Some("LIMIT"), None)
                    .await
            }
            "place_spot_limit_buy_order" => {
                self.spot_order_from_params(params, Some("BUY"), Some("LIMIT"), None)
                    .await
            }
            "place_spot_limit_sell_order" => {
                self.spot_order_from_params(params, Some("SELL"), Some("LIMIT"), None)
                    .await
            }
            "place_spot_post_only_order" => {
                self.spot_order_from_params(params, None, Some("LIMIT"), Some("PostOnly"))
                    .await
            }
            "place_spot_post_only_buy_order" => {
                self.spot_order_from_params(params, Some("BUY"), Some("LIMIT"), Some("PostOnly"))
                    .await
            }
            "place_spot_post_only_sell_order" => {
                self.spot_order_from_params(params, Some("SELL"), Some("LIMIT"), Some("PostOnly"))
                    .await
            }
            "place_spot_batch_order" => {
                params.ensure_allowed(&["data", "sync", "recvWindow"])?;
                validate_bool(params, "sync")?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = vec![(
                    "data".to_string(),
                    batch_orders_query(params.required("data")?)?,
                )];
                push_optional(&mut query, "sync", params.get("sync"));
                push_optional(&mut query, "recvWindow", params.get("recvWindow"));
                self.private_post(SPOT_PLACE_BATCH_ORDER, query).await
            }
            "cancel_spot_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "orderId",
                    "clientOrderID",
                    "clientOrderId",
                    "cancelRestrictions",
                    "recvWindow",
                ])?;
                require_one_identifier(params, &["orderId", "clientOrderID", "clientOrderId"])?;
                validate_client_id(params, "clientOrderID", false)?;
                validate_client_id(params, "clientOrderId", false)?;
                validate_enum(
                    params,
                    "cancelRestrictions",
                    &["NEW", "PENDING", "PARTIALLY_FILLED"],
                )?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = params.only(&[
                    "orderId",
                    "clientOrderID",
                    "cancelRestrictions",
                    "recvWindow",
                ]);
                push_parameter_alias(&mut query, params, "clientOrderID", "clientOrderId");
                self.push_required_symbol(&mut query, params)?;
                self.private_post(SPOT_CANCEL_ORDER, query).await
            }
            "cancel_spot_batch_orders" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "orderIds",
                    "clientOrderIDs",
                    "process",
                    "recvWindow",
                ])?;
                params.required("orderIds")?;
                validate_enum(params, "process", &["0", "1"])?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params)?;
                query.push((
                    "orderIds".to_string(),
                    comma_list(params.required("orderIds")?),
                ));
                push_optional(&mut query, "process", params.get("process"));
                if let Some(value) = params.get("clientOrderIDs") {
                    query.push(("clientOrderIDs".to_string(), comma_list(value)));
                }
                push_optional(&mut query, "recvWindow", params.get("recvWindow"));
                self.private_post(SPOT_CANCEL_BATCH_ORDERS, query).await
            }
            "cancel_spot_open_orders" => {
                params.ensure_allowed(&["product_symbol", "symbol", "recvWindow"])?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = params.only(&["recvWindow"]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_post(SPOT_CANCEL_OPEN_ORDERS, query).await
            }
            "get_spot_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "orderId",
                    "clientOrderID",
                    "clientOrderId",
                    "recvWindow",
                ])?;
                require_one_identifier(params, &["orderId", "clientOrderID", "clientOrderId"])?;
                validate_client_id(params, "clientOrderID", false)?;
                validate_client_id(params, "clientOrderId", false)?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = params.only(&["orderId", "clientOrderID", "recvWindow"]);
                push_parameter_alias(&mut query, params, "clientOrderID", "clientOrderId");
                self.push_required_symbol(&mut query, params)?;
                self.private_get(SPOT_QUERY_ORDER, query).await
            }
            "get_spot_open_orders" => {
                params.ensure_allowed(&["product_symbol", "symbol", "recvWindow"])?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = params.only(&["recvWindow"]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_get(SPOT_QUERY_OPEN_ORDERS, query).await
            }
            "get_spot_order_history" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "orderId",
                    "startTime",
                    "endTime",
                    "pageIndex",
                    "pageSize",
                    "status",
                    "type_",
                    "recvWindow",
                ])?;
                validate_u64_range(params, "pageIndex", 1, 10_000)?;
                validate_u64_range(params, "pageSize", 1, 100)?;
                validate_u64_range(params, "orderId", 1, u64::MAX)?;
                validate_time_range(params, "startTime", "endTime", None)?;
                validate_page_window(params, "pageIndex", "pageSize", 1, 100, 10_000)?;
                validate_enum(params, "status", &["FILLED", "CANCELED", "FAILED"])?;
                validate_enum(params, "type_", SPOT_ORDER_TYPES)?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = params.only(&[
                    "orderId",
                    "startTime",
                    "endTime",
                    "pageIndex",
                    "pageSize",
                    "status",
                    "type",
                    "recvWindow",
                ]);
                push_parameter_alias(&mut query, params, "type", "type_");
                self.push_optional_symbol(&mut query, params)?;
                if !query.iter().any(|(key, _)| key == "pageIndex") {
                    query.push(("pageIndex".to_string(), "1".to_string()));
                }
                if !query.iter().any(|(key, _)| key == "pageSize") {
                    query.push(("pageSize".to_string(), "100".to_string()));
                }
                self.private_get(SPOT_QUERY_ORDER_HISTORY, query).await
            }
            "get_spot_my_trades" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "orderId",
                    "startTime",
                    "endTime",
                    "fromId",
                    "limit",
                    "recvWindow",
                ])?;
                validate_u64_range(params, "limit", 1, 1000)?;
                validate_u64_range(params, "orderId", 1, u64::MAX)?;
                validate_u64_range(params, "fromId", 0, u64::MAX)?;
                validate_time_range(params, "startTime", "endTime", None)?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = params.only(&[
                    "orderId",
                    "startTime",
                    "endTime",
                    "fromId",
                    "limit",
                    "recvWindow",
                ]);
                self.push_required_symbol(&mut query, params)?;
                self.private_get(SPOT_QUERY_MY_TRADES, query).await
            }
            "get_spot_commission_rate" => {
                params.ensure_allowed(&["product_symbol", "symbol", "recvWindow"])?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = params.only(&["recvWindow"]);
                self.push_required_symbol(&mut query, params)?;
                self.private_get(SPOT_COMMISSION_RATE, query).await
            }
            "place_swap_order" => {
                self.swap_order_from_params(params, SWAP_PLACE_ORDER, None)
                    .await
            }
            "test_swap_order" => {
                self.swap_order_from_params(params, SWAP_TEST_ORDER, None)
                    .await
            }
            "place_swap_market_order" => {
                self.swap_order_from_params(
                    params,
                    SWAP_PLACE_ORDER,
                    Some(SwapOrderDefaults {
                        side: None,
                        order_type: Some("MARKET"),
                        position_side: None,
                        time_in_force: None,
                    }),
                )
                .await
            }
            "place_swap_market_buy_order" => {
                self.swap_order_from_params(
                    params,
                    SWAP_PLACE_ORDER,
                    Some(SwapOrderDefaults {
                        side: Some("BUY"),
                        order_type: Some("MARKET"),
                        position_side: Some("LONG"),
                        time_in_force: None,
                    }),
                )
                .await
            }
            "place_swap_market_sell_order" => {
                self.swap_order_from_params(
                    params,
                    SWAP_PLACE_ORDER,
                    Some(SwapOrderDefaults {
                        side: Some("SELL"),
                        order_type: Some("MARKET"),
                        position_side: Some("SHORT"),
                        time_in_force: None,
                    }),
                )
                .await
            }
            "place_swap_limit_order" => {
                self.swap_order_from_params(
                    params,
                    SWAP_PLACE_ORDER,
                    Some(SwapOrderDefaults {
                        side: None,
                        order_type: Some("LIMIT"),
                        position_side: None,
                        time_in_force: Some("GTC"),
                    }),
                )
                .await
            }
            "place_swap_limit_buy_order" => {
                self.swap_order_from_params(
                    params,
                    SWAP_PLACE_ORDER,
                    Some(SwapOrderDefaults {
                        side: Some("BUY"),
                        order_type: Some("LIMIT"),
                        position_side: Some("LONG"),
                        time_in_force: Some("GTC"),
                    }),
                )
                .await
            }
            "place_swap_limit_sell_order" => {
                self.swap_order_from_params(
                    params,
                    SWAP_PLACE_ORDER,
                    Some(SwapOrderDefaults {
                        side: Some("SELL"),
                        order_type: Some("LIMIT"),
                        position_side: Some("SHORT"),
                        time_in_force: Some("GTC"),
                    }),
                )
                .await
            }
            "place_swap_post_only_order" => {
                self.swap_order_from_params(
                    params,
                    SWAP_PLACE_ORDER,
                    Some(SwapOrderDefaults {
                        side: None,
                        order_type: Some("LIMIT"),
                        position_side: None,
                        time_in_force: Some("PostOnly"),
                    }),
                )
                .await
            }
            "place_swap_post_only_buy_order" => {
                self.swap_order_from_params(
                    params,
                    SWAP_PLACE_ORDER,
                    Some(SwapOrderDefaults {
                        side: Some("BUY"),
                        order_type: Some("LIMIT"),
                        position_side: Some("LONG"),
                        time_in_force: Some("PostOnly"),
                    }),
                )
                .await
            }
            "place_swap_post_only_sell_order" => {
                self.swap_order_from_params(
                    params,
                    SWAP_PLACE_ORDER,
                    Some(SwapOrderDefaults {
                        side: Some("SELL"),
                        order_type: Some("LIMIT"),
                        position_side: Some("SHORT"),
                        time_in_force: Some("PostOnly"),
                    }),
                )
                .await
            }
            "place_swap_batch_order" => {
                params.ensure_allowed(&["batchOrders", "recvWindow"])?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = vec![(
                    "batchOrders".to_string(),
                    batch_orders_query(params.required("batchOrders")?)?,
                )];
                push_optional(&mut query, "recvWindow", params.get("recvWindow"));
                self.private_post(SWAP_PLACE_BATCH_ORDER, query).await
            }
            "cancel_swap_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "orderId",
                    "clientOrderId",
                    "recvWindow",
                ])?;
                require_one_identifier(params, &["orderId", "clientOrderId"])?;
                validate_client_id(params, "clientOrderId", false)?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = params.only(&["orderId", "clientOrderId", "recvWindow"]);
                self.push_required_symbol(&mut query, params)?;
                self.private_delete(SWAP_PLACE_ORDER, query).await
            }
            "cancel_swap_batch_order" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "orderIdList",
                    "clientOrderIdList",
                    "recvWindow",
                ])?;
                require_one_identifier(params, &["orderIdList", "clientOrderIdList"])?;
                validate_list_size(params, "orderIdList", 10)?;
                validate_list_size(params, "clientOrderIdList", 10)?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params)?;
                if let Some(value) = params.get("orderIdList") {
                    query.push(("orderIdList".to_string(), python_list_string(value)));
                }
                if let Some(value) = params.get("clientOrderIdList") {
                    query.push(("clientOrderIdList".to_string(), python_list_string(value)));
                }
                push_optional(&mut query, "recvWindow", params.get("recvWindow"));
                self.private_delete(SWAP_CANCEL_BATCH_ORDER, query).await
            }
            "cancel_swap_all_orders" => {
                params.ensure_allowed(&["product_symbol", "symbol", "type_", "recvWindow"])?;
                validate_enum(params, "type_", SWAP_ORDER_TYPES)?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = params.only(&["type_", "recvWindow"]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_delete(SWAP_CANCEL_ALL_OPEN_ORDERS, query)
                    .await
            }
            "replace_swap_order" => self.replace_swap_order_from_params(params).await,
            "close_swap_position" => {
                params.ensure_allowed(&["positionId", "recvWindow"])?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = vec![(
                    "positionId".to_string(),
                    params.required("positionId")?.to_string(),
                )];
                push_optional(&mut query, "recvWindow", params.get("recvWindow"));
                self.private_post(SWAP_CLOSE_POSITION, query).await
            }
            "close_swap_all_positions" => {
                params.ensure_allowed(&["product_symbol", "symbol", "recvWindow"])?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params)?;
                push_optional(&mut query, "recvWindow", params.get("recvWindow"));
                self.private_post(SWAP_CLOSE_ALL_POSITIONS, query).await
            }
            "get_order_detail" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "orderId",
                    "clientOrderId",
                    "recvWindow",
                ])?;
                require_one_identifier(params, &["orderId", "clientOrderId"])?;
                validate_client_id(params, "clientOrderId", false)?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = params.only(&["orderId", "clientOrderId", "recvWindow"]);
                self.push_required_symbol(&mut query, params)?;
                self.private_get(SWAP_PLACE_ORDER, query).await
            }
            "get_open_orders" => {
                params.ensure_allowed(&["product_symbol", "symbol", "type_", "recvWindow"])?;
                validate_enum(params, "type_", SWAP_ORDER_TYPES)?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = params.only(&["type_", "recvWindow"]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_get(SWAP_QUERY_ALL_OPEN_ORDERS, query).await
            }
            "get_order_history" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "currency",
                    "orderId",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ])?;
                validate_enum(params, "currency", &["USDT", "USDC"])?;
                validate_u64_range(params, "limit", 1, 1000)?;
                validate_u64_range(params, "orderId", 1, u64::MAX)?;
                validate_time_range(
                    params,
                    "startTime",
                    "endTime",
                    Some(7 * 24 * 60 * 60 * 1000),
                )?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = params.only(&[
                    "currency",
                    "orderId",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_get(SWAP_QUERY_ORDER_HISTORY, query).await
            }
            "change_margin_type" => {
                params.ensure_allowed(&["product_symbol", "symbol", "marginType", "recvWindow"])?;
                params.required("marginType")?;
                validate_enum(
                    params,
                    "marginType",
                    &["ISOLATED", "CROSSED", "SEPARATE_ISOLATED"],
                )?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = params.only(&["marginType", "recvWindow"]);
                self.push_required_symbol(&mut query, params)?;
                self.private_post(SWAP_CHANGE_MARGIN_TYPE, query).await
            }
            "get_margin_type" => {
                params.ensure_allowed(&["product_symbol", "symbol", "recvWindow"])?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params)?;
                push_optional(&mut query, "recvWindow", params.get("recvWindow"));
                self.private_get(SWAP_CHANGE_MARGIN_TYPE, query).await
            }
            "set_leverage" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "side",
                    "leverage",
                    "recvWindow",
                ])?;
                params.required("side")?;
                params.required("leverage")?;
                validate_enum(params, "side", &["LONG", "SHORT", "BOTH"])?;
                validate_u64_range(params, "leverage", 1, u64::MAX)?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = params.only(&["side", "leverage", "recvWindow"]);
                self.push_required_symbol(&mut query, params)?;
                self.private_post(SWAP_SET_LEVERAGE, query).await
            }
            "get_leverage" => {
                params.ensure_allowed(&["product_symbol", "symbol", "recvWindow"])?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params)?;
                push_optional(&mut query, "recvWindow", params.get("recvWindow"));
                self.private_get(SWAP_SET_LEVERAGE, query).await
            }
            "set_position_mode" => {
                params.ensure_allowed(&["dualSidePosition", "recvWindow"])?;
                validate_bool(params, "dualSidePosition")?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = vec![(
                    "dualSidePosition".to_string(),
                    params.required("dualSidePosition")?.to_string(),
                )];
                push_optional(&mut query, "recvWindow", params.get("recvWindow"));
                self.private_post(SWAP_SET_POSITION_MODE, query).await
            }
            "get_position_mode" => {
                params.ensure_allowed(&["recvWindow"])?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                self.private_get(SWAP_SET_POSITION_MODE, params.only(&["recvWindow"]))
                    .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }

    async fn spot_order_from_params(
        &self,
        params: &BingxParams,
        side_override: Option<&str>,
        type_override: Option<&str>,
        time_in_force_override: Option<&str>,
    ) -> Result<ValidatedResponse> {
        params.ensure_allowed(&[
            "product_symbol",
            "symbol",
            "side",
            "type_",
            "timeInForce",
            "quantity",
            "quoteOrderQty",
            "price",
            "stopPrice",
            "newClientOrderId",
            "clientOrderId",
            "recvWindow",
        ])?;
        let mut query = params.only(SPOT_ORDER_OPTIONAL_KEYS);
        push_parameter_alias(&mut query, params, "newClientOrderId", "clientOrderId");
        self.push_required_symbol(&mut query, params)?;
        let side = match side_override {
            Some(side) => side.to_string(),
            None => normalize_side(params.required("side")?)?,
        };
        let order_type = match type_override {
            Some(order_type) => order_type,
            None => params.required("type_")?,
        };
        validate_spot_order(params, order_type)?;
        query.push(("side".to_string(), side));
        query.push(("type".to_string(), order_type.to_string()));
        if let Some(time_in_force) = time_in_force_override {
            if !query.iter().any(|(key, _)| key == "timeInForce") {
                query.push(("timeInForce".to_string(), time_in_force.to_string()));
            }
        }
        self.private_post(SPOT_PLACE_ORDER, query).await
    }

    async fn swap_order_from_params(
        &self,
        params: &BingxParams,
        endpoint: &str,
        defaults: Option<SwapOrderDefaults<'_>>,
    ) -> Result<ValidatedResponse> {
        params.ensure_allowed(&[
            "product_symbol",
            "symbol",
            "side",
            "type_",
            "positionSide",
            "reduceOnly",
            "price",
            "quantity",
            "quoteOrderQty",
            "stopPrice",
            "priceRate",
            "stopLoss",
            "takeProfit",
            "workingType",
            "clientOrderId",
            "recvWindow",
            "timeInForce",
            "closePosition",
            "activationPrice",
            "stopGuaranteed",
            "positionId",
        ])?;
        let defaults = defaults.unwrap_or_default();
        let mut query = params.only(SWAP_ORDER_OPTIONAL_KEYS);
        self.push_required_symbol(&mut query, params)?;
        let order_type = match defaults.order_type {
            Some(order_type) => order_type,
            None => params.required("type_")?,
        };
        let side = match defaults.side {
            Some(side) => side.to_string(),
            None => normalize_side(params.required("side")?)?,
        };
        validate_swap_order(params, order_type)?;
        query.push(("type".to_string(), order_type.to_string()));
        query.push(("side".to_string(), side));
        if let Some(position_side) = defaults.position_side {
            if !query.iter().any(|(key, _)| key == "positionSide") {
                query.push(("positionSide".to_string(), position_side.to_string()));
            }
        }
        if let Some(time_in_force) = defaults.time_in_force {
            if !query.iter().any(|(key, _)| key == "timeInForce") {
                query.push(("timeInForce".to_string(), time_in_force.to_string()));
            }
        }
        normalize_bool_fields(&mut query);
        self.private_post(endpoint, query).await
    }

    async fn replace_swap_order_from_params(
        &self,
        params: &BingxParams,
    ) -> Result<ValidatedResponse> {
        params.ensure_allowed(&[
            "product_symbol",
            "symbol",
            "orderId",
            "cancelOrderId",
            "cancelClientOrderId",
            "cancelReplaceMode",
            "type_",
            "side",
            "positionSide",
            "reduceOnly",
            "price",
            "quantity",
            "quoteOrderQty",
            "cancelRestrictions",
            "stopPrice",
            "priceRate",
            "workingType",
            "stopLoss",
            "takeProfit",
            "clientOrderId",
            "closePosition",
            "activationPrice",
            "stopGuaranteed",
            "timeInForce",
            "positionId",
            "recvWindow",
        ])?;
        require_one_identifier(params, &["cancelOrderId", "cancelClientOrderId", "orderId"])?;
        validate_enum(
            params,
            "cancelReplaceMode",
            &["STOP_ON_FAILURE", "ALLOW_FAILURE"],
        )?;
        validate_enum(
            params,
            "cancelRestrictions",
            &["ONLY_NEW", "ONLY_PENDING", "ONLY_PARTIALLY_FILLED"],
        )?;
        validate_client_id(params, "cancelClientOrderId", false)?;
        validate_swap_order(params, params.required("type_")?)?;
        let mut query = params.only(SWAP_REPLACE_OPTIONAL_KEYS);
        self.push_required_symbol(&mut query, params)?;
        query.push((
            "cancelReplaceMode".to_string(),
            params.required("cancelReplaceMode")?.to_string(),
        ));
        query.push(("type".to_string(), params.required("type_")?.to_string()));
        query.push((
            "side".to_string(),
            normalize_side(params.required("side")?)?,
        ));
        query.push((
            "positionSide".to_string(),
            params.required("positionSide")?.to_string(),
        ));
        if let Some(value) = params.get("cancelClientOrderId") {
            query.push(("cancelClientOrderId".to_string(), value.to_string()));
        }
        if let Some(value) = params.get("cancelOrderId") {
            query.push(("cancelOrderId".to_string(), value.to_string()));
        } else if params.get("cancelClientOrderId").is_none() {
            query.push((
                "cancelOrderId".to_string(),
                params.required("orderId")?.to_string(),
            ));
        }
        normalize_bool_fields(&mut query);
        self.private_post(SWAP_REPLACE_ORDER, query).await
    }
}

#[derive(Clone, Copy, Default)]
struct SwapOrderDefaults<'a> {
    side: Option<&'a str>,
    order_type: Option<&'a str>,
    position_side: Option<&'a str>,
    time_in_force: Option<&'a str>,
}

fn normalize_bool_fields(query: &mut [(String, String)]) {
    for (key, value) in query {
        if matches!(
            key.as_str(),
            "reduceOnly" | "closePosition" | "stopGuaranteed"
        ) {
            *value = bool_or_string(value);
        }
    }
}

fn validate_spot_order(params: &BingxParams, order_type: &str) -> Result<()> {
    if !SPOT_ORDER_TYPES.contains(&order_type) {
        return Err(crate::DcexError::InvalidInput(format!(
            "unsupported BingX type: {order_type}"
        )));
    }
    validate_enum(params, "timeInForce", TIME_IN_FORCE_VALUES)?;
    validate_client_id(params, "newClientOrderId", true)?;
    validate_client_id(params, "clientOrderId", true)?;
    validate_u64_range(params, "recvWindow", 1, 5000)?;
    for key in ["quantity", "quoteOrderQty", "price", "stopPrice"] {
        validate_positive_number(params, key)?;
    }
    if params.get("quantity").is_none() && params.get("quoteOrderQty").is_none() {
        return Err(crate::DcexError::InvalidInput(
            "one of quantity, quoteOrderQty is required".to_string(),
        ));
    }
    if matches!(
        order_type,
        "TAKE_STOP_LIMIT" | "TAKE_STOP_MARKET" | "TRIGGER_LIMIT" | "TRIGGER_MARKET"
    ) {
        params.required("stopPrice")?;
    }
    if matches!(order_type, "LIMIT" | "TAKE_STOP_LIMIT" | "TRIGGER_LIMIT") {
        params.required("price")?;
    }
    Ok(())
}

fn validate_swap_order(params: &BingxParams, order_type: &str) -> Result<()> {
    if !SWAP_ORDER_TYPES.contains(&order_type) {
        return Err(crate::DcexError::InvalidInput(format!(
            "unsupported BingX type: {order_type}"
        )));
    }
    validate_enum(params, "positionSide", &["BOTH", "LONG", "SHORT"])?;
    validate_enum(params, "timeInForce", TIME_IN_FORCE_VALUES)?;
    validate_enum(
        params,
        "workingType",
        &["MARK_PRICE", "CONTRACT_PRICE", "INDEX_PRICE"],
    )?;
    validate_enum(
        params,
        "stopGuaranteed",
        &["true", "false", "True", "False", "cutfee"],
    )?;
    validate_bool(params, "reduceOnly")?;
    validate_bool(params, "closePosition")?;
    validate_client_id(params, "clientOrderId", false)?;
    validate_json_object(params, "stopLoss")?;
    validate_json_object(params, "takeProfit")?;
    validate_u64_range(params, "recvWindow", 1, 5000)?;
    validate_u64_range(params, "positionId", 1, u64::MAX)?;
    for key in [
        "quantity",
        "quoteOrderQty",
        "price",
        "stopPrice",
        "priceRate",
        "activationPrice",
    ] {
        validate_positive_number(params, key)?;
    }
    if let Some(price_rate) = params.get("priceRate") {
        if price_rate.parse::<f64>().is_ok_and(|value| value > 1.0) {
            return Err(crate::DcexError::InvalidInput(
                "BingX parameter priceRate must not exceed 1".to_string(),
            ));
        }
    }
    let close_position = params
        .get("closePosition")
        .is_some_and(|value| value.eq_ignore_ascii_case("true"));
    if close_position {
        if params.get("quantity").is_some() || params.get("quoteOrderQty").is_some() {
            return Err(crate::DcexError::InvalidInput(
                "BingX closePosition cannot be used with quantity or quoteOrderQty".to_string(),
            ));
        }
        if !matches!(order_type, "STOP_MARKET" | "TAKE_PROFIT_MARKET") {
            return Err(crate::DcexError::InvalidInput(
                "BingX closePosition only supports STOP_MARKET or TAKE_PROFIT_MARKET".to_string(),
            ));
        }
    } else if params.get("quantity").is_none() && params.get("quoteOrderQty").is_none() {
        return Err(crate::DcexError::InvalidInput(
            "one of quantity, quoteOrderQty is required".to_string(),
        ));
    }
    if matches!(
        order_type,
        "STOP_MARKET"
            | "STOP"
            | "TAKE_PROFIT_MARKET"
            | "TAKE_PROFIT"
            | "TRIGGER_LIMIT"
            | "TRIGGER_MARKET"
    ) {
        params.required("stopPrice")?;
    }
    if matches!(
        order_type,
        "LIMIT" | "STOP" | "TAKE_PROFIT" | "TRIGGER_LIMIT"
    ) {
        params.required("price")?;
    }
    if matches!(order_type, "TRAILING_STOP_MARKET" | "TRAILING_TP_SL") {
        params.required("priceRate")?;
    }
    if params.get("reduceOnly").is_some()
        && matches!(params.get("positionSide"), Some("LONG" | "SHORT"))
    {
        return Err(crate::DcexError::InvalidInput(
            "BingX reduceOnly is not accepted in hedge mode".to_string(),
        ));
    }
    Ok(())
}

fn validate_list_size(params: &BingxParams, key: &str, maximum: usize) -> Result<()> {
    let Some(value) = params.get(key) else {
        return Ok(());
    };
    let count = if let Ok(serde_json::Value::Array(values)) = serde_json::from_str(value) {
        values.len()
    } else {
        value
            .split(',')
            .filter(|item| !item.trim().is_empty())
            .count()
    };
    if (1..=maximum).contains(&count) {
        return Ok(());
    }
    Err(crate::DcexError::InvalidInput(format!(
        "BingX parameter {key} must contain between 1 and {maximum} identifiers"
    )))
}

fn push_parameter_alias(
    query: &mut Vec<(String, String)>,
    params: &BingxParams,
    official_key: &str,
    legacy_key: &str,
) {
    if query.iter().any(|(key, _)| key == official_key) {
        return;
    }
    push_optional(query, official_key, params.get(legacy_key));
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn preserves_spot_trigger_and_official_client_id() {
        let params = BingxParams::from_pairs(vec![
            ("stopPrice".to_string(), "90".to_string()),
            ("newClientOrderId".to_string(), "new-id".to_string()),
        ]);
        let query = params.only(SPOT_ORDER_OPTIONAL_KEYS);
        assert!(query.contains(&("stopPrice".to_string(), "90".to_string())));
        assert!(query.contains(&("newClientOrderId".to_string(), "new-id".to_string())));
    }

    #[test]
    fn maps_legacy_client_id_to_official_key() {
        let params =
            BingxParams::from_pairs(vec![("clientOrderId".to_string(), "legacy-id".to_string())]);
        let mut query = Vec::new();
        push_parameter_alias(&mut query, &params, "clientOrderID", "clientOrderId");
        assert_eq!(
            query,
            vec![("clientOrderID".to_string(), "legacy-id".to_string())]
        );
    }

    #[test]
    fn maps_python_order_type_alias_to_official_key() {
        let params = BingxParams::from_pairs(vec![("type_".to_string(), "LIMIT".to_string())]);
        let mut query = Vec::new();
        push_parameter_alias(&mut query, &params, "type", "type_");
        assert_eq!(query, vec![("type".to_string(), "LIMIT".to_string())]);
    }
}
