use serde_json::{Map, Number, Value};

use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::MexcClient;
use super::endpoints::*;
use super::params::{require_one_identifier, MexcParams};
use super::signing::json_value_string;

const SPOT_ORDER_OPTIONAL_KEYS: &[&str] = &[
    "quantity",
    "quoteOrderQty",
    "price",
    "timeInForce",
    "newClientOrderId",
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
                require_one_identifier(&params, &["orderId", "origClientOrderId"])?;
                let mut query = params.only(&["orderId", "origClientOrderId", "recvWindow"]);
                self.push_required_product_symbol(&mut query, params, "")?;
                self.spot_private(HttpMethod::Delete, SPOT_ORDER, query)
                    .await
            }
            "cancel_spot_open_orders" => {
                let mut query = params.only(&["recvWindow"]);
                self.push_required_product_symbol(&mut query, params, "")?;
                self.spot_private(HttpMethod::Delete, SPOT_OPEN_ORDERS, query)
                    .await
            }
            "get_spot_order" => {
                let mut query = params.only(&["orderId", "origClientOrderId", "recvWindow"]);
                self.push_required_product_symbol(&mut query, params, "")?;
                self.spot_private(HttpMethod::Get, SPOT_ORDER, query).await
            }
            "get_spot_open_orders" => {
                let mut query = params.only(&["recvWindow"]);
                self.push_required_product_symbol(&mut query, params, "")?;
                self.spot_private(HttpMethod::Get, SPOT_OPEN_ORDERS, query)
                    .await
            }
            "get_spot_all_orders" => {
                let mut query =
                    params.only(&["orderId", "startTime", "endTime", "limit", "recvWindow"]);
                self.push_required_product_symbol(&mut query, params, "")?;
                self.spot_private(HttpMethod::Get, SPOT_ALL_ORDERS, query)
                    .await
            }
            "get_spot_my_trades" => {
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
                let mut body = params.body(&["externalOid"], &[], &[]);
                self.insert_required_product_symbol(&mut body, params, "_")?;
                self.contract_post_json(CONTRACT_CANCEL_ORDER_WITH_EXTERNAL_ID, Value::Object(body))
                    .await
            }
            "cancel_all_contract_orders" => {
                let mut body = Map::new();
                self.insert_required_product_symbol(&mut body, params, "_")?;
                self.contract_post_json(CONTRACT_CANCEL_ALL_ORDERS, Value::Object(body))
                    .await
            }
            "get_contract_open_orders" => {
                let mut query = params.only(&["page_num", "page_size"]);
                add_pagination_defaults(&mut query);
                self.contract_get(CONTRACT_OPEN_ORDERS, query).await
            }
            "get_contract_history_orders" => {
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
                self.contract_get(CONTRACT_HISTORY_ORDERS, query).await
            }
            "get_contract_order_by_external_id" => {
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
                let order_id = params
                    .required("order_id")
                    .or_else(|_| params.required("orderId"))?;
                let path = CONTRACT_ORDER.replace("{order_id}", order_id);
                self.contract_get(&path, Vec::new()).await
            }
            "get_contract_orders" => {
                let order_ids = joined_order_ids(params.required("order_ids")?)?;
                self.contract_get(
                    CONTRACT_BATCH_QUERY,
                    vec![("order_ids".to_string(), order_ids)],
                )
                .await
            }
            "get_contract_order_deal_details" => {
                let order_id = params
                    .required("order_id")
                    .or_else(|_| params.required("orderId"))?;
                let path = CONTRACT_ORDER_DEAL_DETAILS.replace("{order_id}", order_id);
                self.contract_get(&path, Vec::new()).await
            }
            "get_contract_order_deals" => {
                let mut query = params.only(&["start_time", "end_time", "page_num", "page_size"]);
                self.push_product_symbol(&mut query, params, "_")?;
                self.contract_get(CONTRACT_ORDER_DEALS, query).await
            }
            "get_contract_plan_orders" => {
                let mut query = vec![
                    (
                        "start_time".to_string(),
                        params.required("start_time")?.to_string(),
                    ),
                    (
                        "end_time".to_string(),
                        params.required("end_time")?.to_string(),
                    ),
                ];
                query.extend(params.only(&["states", "side", "page_num", "page_size"]));
                self.push_product_symbol(&mut query, params, "_")?;
                add_pagination_defaults(&mut query);
                self.contract_get(CONTRACT_PLAN_ORDERS, query).await
            }
            "place_contract_plan_order" => {
                let mut body = params.body(
                    &["price", "externalOid", "stopLossPrice", "takeProfitPrice"],
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
                self.insert_required_product_symbol(&mut body, params, "_")?;
                self.contract_post_json(CONTRACT_PLACE_PLAN_ORDER, Value::Object(body))
                    .await
            }
            "cancel_contract_plan_orders" => {
                self.contract_post_json(
                    CONTRACT_CANCEL_PLAN_ORDERS,
                    params.json_required("orders")?,
                )
                .await
            }
            "cancel_all_contract_plan_orders" => {
                let mut body = Map::new();
                self.insert_product_symbol(&mut body, params, "_")?;
                self.contract_post_json(CONTRACT_CANCEL_ALL_PLAN_ORDERS, Value::Object(body))
                    .await
            }
            "get_contract_stop_orders" => {
                let mut query = params.only(&["states", "page_num", "page_size"]);
                self.push_product_symbol(&mut query, params, "_")?;
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
        default_time_in_force: Option<&str>,
    ) -> Result<ValidatedResponse> {
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
        query.push(("side".to_string(), side.to_string()));
        query.push(("type".to_string(), order_type.to_string()));
        query.extend(params.only(SPOT_ORDER_OPTIONAL_KEYS));
        if let Some(time_in_force) = default_time_in_force {
            if !query.iter().any(|(key, _)| key == "timeInForce") {
                query.push(("timeInForce".to_string(), time_in_force.to_string()));
            }
        }
        self.spot_private(HttpMethod::Post, endpoint, query).await
    }

    async fn place_spot_batch_orders_from_params(
        &self,
        params: &MexcParams,
    ) -> Result<ValidatedResponse> {
        let orders = params.json_required("batchOrders")?;
        let Value::Array(mut orders) = orders else {
            return Err(DcexError::InvalidInput(
                "batchOrders must be a JSON array.".to_string(),
            ));
        };
        for order in &mut orders {
            if let Value::Object(order) = order {
                if let Some(product_symbol) = order.remove("product_symbol") {
                    let symbol = self.exchange_symbol(&json_value_string(&product_symbol), "")?;
                    order.insert("symbol".to_string(), Value::String(symbol));
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
        self.contract_post_json(CONTRACT_CREATE_ORDER, Value::Object(body))
            .await
    }

    async fn cancel_contract_orders_from_params(
        &self,
        params: &MexcParams,
    ) -> Result<ValidatedResponse> {
        let orders = params.json_required("orders")?;
        let Value::Array(orders) = orders else {
            return Err(DcexError::InvalidInput(
                "orders must be a JSON array.".to_string(),
            ));
        };
        let order_ids = orders
            .into_iter()
            .map(|order| match order {
                Value::Object(mut object) => object.remove("orderId").unwrap_or(Value::Null),
                value => value,
            })
            .collect();
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

fn add_pagination_defaults(query: &mut Vec<(String, String)>) {
    if !query.iter().any(|(key, _)| key == "page_num") {
        query.push(("page_num".to_string(), "1".to_string()));
    }
    if !query.iter().any(|(key, _)| key == "page_size") {
        query.push(("page_size".to_string(), "20".to_string()));
    }
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
