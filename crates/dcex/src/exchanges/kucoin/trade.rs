use serde_json::{Map, Value};

use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::{KucoinClient, KucoinMarket};
use super::endpoints::*;
use super::params::{
    insert_required_integer, insert_required_string, insert_truthy_bool, json_value_string,
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
const SPOT_TRADE_HISTORY_KEYS: &[&str] = &["orderId", "startAt", "endAt", "limit"];
const FUTURES_ORDER_STRING_KEYS: &[&str] = &[
    "price",
    "clientOid",
    "marginMode",
    "positionSide",
    "timeInForce",
    "stop",
    "stopPriceType",
    "stopPrice",
    "stp",
    "remark",
    "tags",
];
const FUTURES_ORDER_INTEGER_KEYS: &[&str] = &["leverage", "visibleSize"];
const FUTURES_ORDER_BOOL_KEYS: &[&str] =
    &["postOnly", "reduceOnly", "closeOrder", "hidden", "iceberg"];
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
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params, false)?;
                self.private_delete(KucoinMarket::Spot, SPOT_CANCEL_ALL_ORDERS_BY_SYMBOL, query)
                    .await
            }
            "cancel_spot_all_orders" => {
                self.private_delete(KucoinMarket::Spot, SPOT_CANCEL_ALL_ORDERS, Vec::new())
                    .await
            }
            "get_spot_open_orders" => {
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params, false)?;
                self.private_get(KucoinMarket::Spot, SPOT_OPEN_ORDERS, query)
                    .await
            }
            "get_spot_trade_history" => {
                let mut query = params.only(SPOT_TRADE_HISTORY_KEYS);
                self.push_optional_symbol(&mut query, params, false)?;
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
                let mut query = params.only(FUTURES_ORDER_LIST_KEYS);
                self.push_optional_symbol(&mut query, params, true)?;
                self.private_get(KucoinMarket::Futures, FUTURES_ORDER_LIST, query)
                    .await
            }
            "get_futures_order" => {
                let order_id = params.required("orderId")?;
                self.private_get(
                    KucoinMarket::Futures,
                    FUTURES_ORDER.replace("{orderId}", order_id),
                    Vec::new(),
                )
                .await
            }
            "get_futures_order_by_client_oid" => {
                let mut query = vec![(
                    "clientOid".to_string(),
                    params.required("clientOid")?.to_string(),
                )];
                self.push_optional_symbol(&mut query, params, true)?;
                self.private_get(KucoinMarket::Futures, FUTURES_ORDER_BY_CLIENT_OID, query)
                    .await
            }
            "cancel_futures_order" => {
                let order_id = params.required("orderId")?;
                self.private_delete(
                    KucoinMarket::Futures,
                    FUTURES_CANCEL_ORDER.replace("{orderId}", order_id),
                    Vec::new(),
                )
                .await
            }
            "cancel_futures_order_by_client_oid" => {
                let client_oid = params.required("clientOid")?;
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params, true)?;
                self.private_delete(
                    KucoinMarket::Futures,
                    FUTURES_CANCEL_ORDER_BY_CLIENT_OID.replace("{clientOid}", client_oid),
                    query,
                )
                .await
            }
            "cancel_futures_all_orders" => {
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params, true)?;
                self.private_delete(KucoinMarket::Futures, FUTURES_CANCEL_ALL_ORDERS, query)
                    .await
            }
            "get_futures_open_order_value" => {
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params, true)?;
                self.private_get(KucoinMarket::Futures, FUTURES_OPEN_ORDER_VALUE, query)
                    .await
            }
            "get_futures_trade_history" => {
                let mut query = params.only(FUTURES_TRADE_HISTORY_KEYS);
                self.push_optional_symbol(&mut query, params, true)?;
                self.private_get(KucoinMarket::Futures, FUTURES_TRADE_HISTORY, query)
                    .await
            }
            "get_futures_recent_trade_history" => {
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
        let mut body = params.body(
            SPOT_ORDER_STRING_KEYS,
            SPOT_ORDER_INTEGER_KEYS,
            SPOT_ORDER_BOOL_KEYS,
        );
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
        let mut order_list = Vec::with_capacity(orders.len());
        for order in orders {
            let mut order = order.as_object().cloned().ok_or_else(|| {
                DcexError::InvalidInput("KuCoin batch order must be a JSON object.".to_string())
            })?;
            if let Some(symbol) = order
                .remove("symbol")
                .or_else(|| order.remove("product_symbol"))
                .map(|value| json_value_string(&value))
            {
                order.insert(
                    "symbol".to_string(),
                    Value::String(self.exchange_symbol(&symbol, false)?),
                );
            }
            if let Some(order_type) = type_override {
                order.insert("type".to_string(), Value::String(order_type.to_string()));
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
        let mut body = params.body(
            FUTURES_ORDER_STRING_KEYS,
            FUTURES_ORDER_INTEGER_KEYS,
            FUTURES_ORDER_BOOL_KEYS,
        );
        self.insert_required_body_symbol(&mut body, params, true)?;
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
        insert_required_integer(&mut body, "size", params.required("size")?);
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
