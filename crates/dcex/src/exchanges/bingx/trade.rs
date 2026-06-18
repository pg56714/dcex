use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::BingxClient;
use super::endpoints::*;
use super::params::{
    batch_orders_query, bool_or_string, comma_list, normalize_side, push_optional,
    python_list_string, BingxParams,
};

const SPOT_ORDER_OPTIONAL_KEYS: &[&str] = &[
    "timeInForce",
    "quantity",
    "quoteOrderQty",
    "price",
    "clientOrderId",
    "recvWindow",
];

const SWAP_ORDER_OPTIONAL_KEYS: &[&str] = &[
    "positionSide",
    "reduceOnly",
    "price",
    "quantity",
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
                self.spot_order_from_params(params, None, Some("LIMIT"), Some("POC"))
                    .await
            }
            "place_spot_post_only_buy_order" => {
                self.spot_order_from_params(params, Some("BUY"), Some("LIMIT"), Some("POC"))
                    .await
            }
            "place_spot_post_only_sell_order" => {
                self.spot_order_from_params(params, Some("SELL"), Some("LIMIT"), Some("POC"))
                    .await
            }
            "place_spot_batch_order" => {
                let query = vec![(
                    "data".to_string(),
                    batch_orders_query(params.required("data")?)?,
                )];
                self.private_post(SPOT_PLACE_BATCH_ORDER, query).await
            }
            "cancel_spot_order" => {
                let mut query = params.only(&["orderId", "clientOrderId", "recvWindow"]);
                self.push_required_symbol(&mut query, params)?;
                self.private_post(SPOT_CANCEL_ORDER, query).await
            }
            "cancel_spot_batch_orders" => {
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params)?;
                query.push((
                    "orderIds".to_string(),
                    comma_list(params.required("orderIds")?),
                ));
                push_optional(&mut query, "process", params.get("process"));
                push_optional(&mut query, "recvWindow", params.get("recvWindow"));
                self.private_post(SPOT_CANCEL_BATCH_ORDERS, query).await
            }
            "cancel_spot_open_orders" => {
                let mut query = params.only(&["recvWindow"]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_post(SPOT_CANCEL_OPEN_ORDERS, query).await
            }
            "get_spot_order" => {
                let mut query = params.only(&["orderId", "clientOrderId", "recvWindow"]);
                self.push_required_symbol(&mut query, params)?;
                self.private_get(SPOT_QUERY_ORDER, query).await
            }
            "get_spot_open_orders" => {
                let mut query = params.only(&["recvWindow"]);
                self.push_required_symbol(&mut query, params)?;
                self.private_get(SPOT_QUERY_OPEN_ORDERS, query).await
            }
            "get_spot_order_history" => {
                let mut query = params.only(&[
                    "orderId",
                    "startTime",
                    "endTime",
                    "pageIndex",
                    "pageSize",
                    "recvWindow",
                ]);
                self.push_required_symbol(&mut query, params)?;
                if !query.iter().any(|(key, _)| key == "pageIndex") {
                    query.push(("pageIndex".to_string(), "1".to_string()));
                }
                if !query.iter().any(|(key, _)| key == "pageSize") {
                    query.push(("pageSize".to_string(), "100".to_string()));
                }
                self.private_get(SPOT_QUERY_ORDER_HISTORY, query).await
            }
            "get_spot_my_trades" => {
                let mut query =
                    params.only(&["orderId", "startTime", "endTime", "limit", "recvWindow"]);
                self.push_required_symbol(&mut query, params)?;
                self.private_get(SPOT_QUERY_MY_TRADES, query).await
            }
            "get_spot_commission_rate" => {
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
                let query = vec![(
                    "batchOrders".to_string(),
                    batch_orders_query(params.required("batchOrders")?)?,
                )];
                self.private_post(SWAP_PLACE_BATCH_ORDER, query).await
            }
            "cancel_swap_order" => {
                let mut query = params.only(&["orderId", "clientOrderId", "recvWindow"]);
                self.push_required_symbol(&mut query, params)?;
                self.private_delete(SWAP_PLACE_ORDER, query).await
            }
            "cancel_swap_batch_order" => {
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params)?;
                if let Some(value) = params.get("orderIdList") {
                    query.push(("orderIdList".to_string(), python_list_string(value)));
                }
                if let Some(value) = params.get("clientOrderIdList") {
                    query.push(("clientOrderIdList".to_string(), python_list_string(value)));
                }
                self.private_delete(SWAP_CANCEL_BATCH_ORDER, query).await
            }
            "cancel_swap_all_orders" => {
                let mut query = params.only(&["type_"]);
                self.push_required_symbol(&mut query, params)?;
                self.private_delete(SWAP_CANCEL_ALL_OPEN_ORDERS, query)
                    .await
            }
            "replace_swap_order" => self.replace_swap_order_from_params(params).await,
            "close_swap_position" => {
                self.private_post(
                    SWAP_CLOSE_POSITION,
                    vec![(
                        "positionId".to_string(),
                        params.required("positionId")?.to_string(),
                    )],
                )
                .await
            }
            "close_swap_all_positions" => {
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params)?;
                self.private_post(SWAP_CLOSE_ALL_POSITIONS, query).await
            }
            "get_order_detail" => {
                let mut query = params.only(&["orderId", "clientOrderId"]);
                self.push_required_symbol(&mut query, params)?;
                self.private_get(SWAP_PLACE_ORDER, query).await
            }
            "get_open_orders" => {
                let mut query = params.only(&["type_"]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_get(SWAP_QUERY_ALL_OPEN_ORDERS, query).await
            }
            "get_order_history" => {
                let mut query =
                    params.only(&["currency", "orderId", "startTime", "endTime", "limit"]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_get(SWAP_QUERY_ORDER_HISTORY, query).await
            }
            "change_margin_type" => {
                let mut query = params.only(&["marginType"]);
                self.push_required_symbol(&mut query, params)?;
                self.private_post(SWAP_CHANGE_MARGIN_TYPE, query).await
            }
            "get_margin_type" => {
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params)?;
                self.private_get(SWAP_CHANGE_MARGIN_TYPE, query).await
            }
            "set_leverage" => {
                let mut query = params.only(&["side", "leverage"]);
                self.push_required_symbol(&mut query, params)?;
                self.private_post(SWAP_SET_LEVERAGE, query).await
            }
            "get_leverage" => {
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params)?;
                self.private_get(SWAP_SET_LEVERAGE, query).await
            }
            "set_position_mode" => {
                self.private_post(
                    SWAP_SET_POSITION_MODE,
                    vec![(
                        "dualSidePosition".to_string(),
                        params.required("dualSidePosition")?.to_string(),
                    )],
                )
                .await
            }
            "get_position_mode" => self.private_get(SWAP_SET_POSITION_MODE, Vec::new()).await,
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
        let mut query = params.only(SPOT_ORDER_OPTIONAL_KEYS);
        self.push_required_symbol(&mut query, params)?;
        let side = match side_override {
            Some(side) => side.to_string(),
            None => normalize_side(params.required("side")?)?,
        };
        let order_type = match type_override {
            Some(order_type) => order_type,
            None => params.required("type_")?,
        };
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
