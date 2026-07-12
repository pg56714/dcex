use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::BitgetClient;
use super::endpoints::*;
use super::params::{insert_optional_value, require_one_identifier, BitgetParams};

impl BitgetClient {
    pub(super) async fn trade_private_request(
        &self,
        method_name: &str,
        params: &BitgetParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "place_spot_order" => self.place_spot_order_from_params(params).await,
            "place_spot_market_order" => {
                self.place_spot_order_request(params, None, Some("market"), None)
                    .await
            }
            "place_spot_market_buy_order" => {
                self.place_spot_order_request(params, Some("buy"), Some("market"), None)
                    .await
            }
            "place_spot_market_sell_order" => {
                self.place_spot_order_request(params, Some("sell"), Some("market"), None)
                    .await
            }
            "place_spot_limit_order" => {
                self.place_spot_order_request(params, None, Some("limit"), Some("gtc"))
                    .await
            }
            "place_spot_limit_buy_order" => {
                self.place_spot_order_request(params, Some("buy"), Some("limit"), Some("gtc"))
                    .await
            }
            "place_spot_limit_sell_order" => {
                self.place_spot_order_request(params, Some("sell"), Some("limit"), Some("gtc"))
                    .await
            }
            "place_spot_post_only_limit_order" => {
                self.place_spot_order_request(params, None, Some("limit"), Some("post_only"))
                    .await
            }
            "place_spot_post_only_limit_buy_order" => {
                self.place_spot_order_request(params, Some("buy"), Some("limit"), Some("post_only"))
                    .await
            }
            "place_spot_post_only_limit_sell_order" => {
                self.place_spot_order_request(
                    params,
                    Some("sell"),
                    Some("limit"),
                    Some("post_only"),
                )
                .await
            }
            "place_spot_batch_orders" => self.place_spot_batch_orders_from_params(params).await,
            "cancel_spot_order" => self.cancel_spot_order_from_params(params).await,
            "cancel_spot_batch_orders" => self.cancel_spot_batch_orders_from_params(params).await,
            "get_spot_order" => {
                require_one_identifier(params, &["orderId", "clientOid"])?;
                self.get_private(SPOT_ORDER_INFO, params.only(&["orderId", "clientOid"]))
                    .await
            }
            "get_spot_open_orders" => {
                let mut query = params.only(&["limit", "idLessThan", "startTime", "endTime"]);
                self.push_product_symbol(&mut query, params)?;
                self.get_private(SPOT_UNFILLED_ORDERS, query).await
            }
            "get_spot_history_orders" => {
                let mut query = params.only(&["limit", "idLessThan", "startTime", "endTime"]);
                self.push_product_symbol(&mut query, params)?;
                self.get_private(SPOT_HISTORY_ORDERS, query).await
            }
            "get_spot_fills" => {
                let mut query =
                    params.only(&["orderId", "limit", "idLessThan", "startTime", "endTime"]);
                self.push_product_symbol(&mut query, params)?;
                self.get_private(SPOT_FILLS, query).await
            }
            "place_uta_order" => self.place_uta_order_from_params(params).await,
            "place_uta_batch_orders" => {
                self.post_private(UTA_BATCH_PLACE_ORDER, params.json_required("orderList")?)
                    .await
            }
            "cancel_uta_order" => self.cancel_uta_order_from_params(params).await,
            "cancel_uta_batch_orders" => {
                self.post_private(UTA_BATCH_CANCEL_ORDERS, params.json_required("orderList")?)
                    .await
            }
            "get_uta_order" => {
                require_one_identifier(params, &["orderId", "clientOid"])?;
                self.get_private(UTA_ORDER_DETAIL, params.only(&["orderId", "clientOid"]))
                    .await
            }
            "get_uta_open_orders" => {
                let mut query =
                    params.only(&["category", "startTime", "endTime", "limit", "cursor"]);
                self.push_uta_symbol(&mut query, params)?;
                self.get_private(UTA_PENDING_ORDERS, query).await
            }
            "get_uta_history_orders" => {
                let mut query =
                    params.only(&["category", "startTime", "endTime", "limit", "cursor"]);
                self.push_uta_symbol(&mut query, params)?;
                self.get_private(UTA_HISTORY_ORDERS, query).await
            }
            "get_uta_fills" => {
                self.get_private(
                    UTA_FILLS,
                    params.only(&[
                        "category",
                        "orderId",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
                    ]),
                )
                .await
            }
            "get_uta_positions" => {
                let mut query = params.only(&["category", "posSide"]);
                self.push_uta_symbol(&mut query, params)?;
                self.get_private(UTA_POSITIONS, query).await
            }
            "place_uta_strategy_order" => {
                self.post_private(
                    UTA_PLACE_STRATEGY_ORDER,
                    Value::Object(params.body(&[
                        "category",
                        "symbol",
                        "clientOid",
                        "type",
                        "tpslMode",
                        "qty",
                        "side",
                        "posSide",
                        "reduceOnly",
                        "tpTriggerBy",
                        "slTriggerBy",
                        "takeProfit",
                        "stopLoss",
                        "tpOrderType",
                        "slOrderType",
                        "tpLimitPrice",
                        "slLimitPrice",
                        "triggerBy",
                        "triggerPrice",
                        "triggerOrderType",
                        "triggerOrderPrice",
                    ])),
                )
                .await
            }
            "modify_uta_strategy_order" => {
                self.post_private(
                    UTA_MODIFY_STRATEGY_ORDER,
                    Value::Object(params.body(&[
                        "orderId",
                        "clientOid",
                        "qty",
                        "tpTriggerBy",
                        "slTriggerBy",
                        "takeProfit",
                        "stopLoss",
                        "tpOrderType",
                        "slOrderType",
                        "tpLimitPrice",
                        "slLimitPrice",
                        "triggerBy",
                        "triggerPrice",
                        "triggerOrderType",
                        "triggerOrderPrice",
                    ])),
                )
                .await
            }
            "cancel_uta_strategy_order" => {
                require_one_identifier(params, &["orderId", "clientOid"])?;
                self.post_private(
                    UTA_CANCEL_STRATEGY_ORDER,
                    Value::Object(params.body(&["orderId", "clientOid"])),
                )
                .await
            }
            "get_uta_unfilled_strategy_orders" => {
                self.get_private(
                    UTA_UNFILLED_STRATEGY_ORDERS,
                    params.only(&["category", "type", "symbol", "idLessThan", "limit"]),
                )
                .await
            }
            "get_uta_history_strategy_orders" => {
                self.get_private(
                    UTA_HISTORY_STRATEGY_ORDERS,
                    params.only(&[
                        "category",
                        "type",
                        "symbol",
                        "startTime",
                        "endTime",
                        "idLessThan",
                        "limit",
                    ]),
                )
                .await
            }
            "place_futures_order" => self.place_futures_order_from_params(params).await,
            "place_futures_market_order" => {
                self.place_futures_order_request(params, None, Some("market"), None)
                    .await
            }
            "place_futures_market_buy_order" => {
                self.place_futures_order_request(params, Some("buy"), Some("market"), None)
                    .await
            }
            "place_futures_market_sell_order" => {
                self.place_futures_order_request(params, Some("sell"), Some("market"), None)
                    .await
            }
            "place_futures_limit_order" => {
                self.place_futures_order_request(params, None, Some("limit"), Some("gtc"))
                    .await
            }
            "place_futures_limit_buy_order" => {
                self.place_futures_order_request(params, Some("buy"), Some("limit"), Some("gtc"))
                    .await
            }
            "place_futures_limit_sell_order" => {
                self.place_futures_order_request(params, Some("sell"), Some("limit"), Some("gtc"))
                    .await
            }
            "place_futures_post_only_limit_order" => {
                self.place_futures_order_request(params, None, Some("limit"), Some("post_only"))
                    .await
            }
            "place_futures_post_only_limit_buy_order" => {
                self.place_futures_order_request(
                    params,
                    Some("buy"),
                    Some("limit"),
                    Some("post_only"),
                )
                .await
            }
            "place_futures_post_only_limit_sell_order" => {
                self.place_futures_order_request(
                    params,
                    Some("sell"),
                    Some("limit"),
                    Some("post_only"),
                )
                .await
            }
            "place_futures_batch_orders" => {
                self.place_futures_batch_orders_from_params(params).await
            }
            "cancel_futures_order" => self.cancel_futures_order_from_params(params).await,
            "cancel_futures_batch_orders" => {
                self.cancel_futures_batch_orders_from_params(params).await
            }
            "get_futures_order" => {
                require_one_identifier(params, &["orderId", "clientOid"])?;
                let mut query = params.only(&["productType", "orderId", "clientOid"]);
                self.push_required_product_symbol(&mut query, params)?;
                self.get_private(FUTURES_ORDER_DETAIL, query).await
            }
            "get_futures_open_orders" => {
                let mut query =
                    params.only(&["productType", "orderId", "clientOid", "idLessThan", "limit"]);
                self.push_product_symbol(&mut query, params)?;
                self.get_private(FUTURES_PENDING_ORDERS, query).await
            }
            "get_futures_history_orders" => {
                let mut query =
                    params.only(&["productType", "startTime", "endTime", "idLessThan", "limit"]);
                self.push_product_symbol(&mut query, params)?;
                self.get_private(FUTURES_HISTORY_ORDERS, query).await
            }
            "get_futures_fills" => {
                let mut query = params.only(&[
                    "orderId",
                    "productType",
                    "idLessThan",
                    "startTime",
                    "endTime",
                    "limit",
                ]);
                self.push_product_symbol(&mut query, params)?;
                self.get_private(FUTURES_FILLS, query).await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }

    async fn place_spot_order_from_params(
        &self,
        params: &BitgetParams,
    ) -> Result<ValidatedResponse> {
        self.place_spot_order_request(params, None, None, None)
            .await
    }

    async fn place_spot_order_request(
        &self,
        params: &BitgetParams,
        side: Option<&str>,
        order_type: Option<&str>,
        force: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut body = params.body(&[
            "side",
            "orderType",
            "size",
            "price",
            "force",
            "clientOid",
            "tpslType",
            "stpMode",
        ]);
        self.insert_required_product_symbol(&mut body, params)?;
        if let Some(side) = side {
            body.insert("side".to_string(), Value::String(side.to_string()));
        }
        if let Some(order_type) = order_type {
            body.insert(
                "orderType".to_string(),
                Value::String(order_type.to_string()),
            );
        }
        if let Some(force) = force {
            body.entry("force".to_string())
                .or_insert_with(|| Value::String(force.to_string()));
        }
        self.post_private(SPOT_PLACE_ORDER, Value::Object(body))
            .await
    }

    async fn place_spot_batch_orders_from_params(
        &self,
        params: &BitgetParams,
    ) -> Result<ValidatedResponse> {
        let mut body = params.body(&["batchMode"]);
        self.insert_product_symbol(&mut body, params)?;
        insert_optional_value(&mut body, "orderList", params.json_optional("orderList")?);
        self.post_private(SPOT_BATCH_PLACE_ORDER, Value::Object(body))
            .await
    }

    async fn cancel_spot_order_from_params(
        &self,
        params: &BitgetParams,
    ) -> Result<ValidatedResponse> {
        require_one_identifier(params, &["orderId", "clientOid"])?;
        let mut body = params.body(&["orderId", "clientOid", "tpslType"]);
        self.insert_required_product_symbol(&mut body, params)?;
        self.post_private(SPOT_CANCEL_ORDER, Value::Object(body))
            .await
    }

    async fn cancel_spot_batch_orders_from_params(
        &self,
        params: &BitgetParams,
    ) -> Result<ValidatedResponse> {
        let mut body = params.body(&["batchMode"]);
        self.insert_product_symbol(&mut body, params)?;
        insert_optional_value(&mut body, "orderList", params.json_optional("orderList")?);
        self.post_private(SPOT_BATCH_CANCEL_ORDER, Value::Object(body))
            .await
    }

    async fn place_uta_order_from_params(
        &self,
        params: &BitgetParams,
    ) -> Result<ValidatedResponse> {
        let mut body = params.body(&[
            "category",
            "side",
            "orderType",
            "qty",
            "price",
            "timeInForce",
            "posSide",
            "clientOid",
            "reduceOnly",
            "stpMode",
            "marginMode",
        ]);
        self.insert_uta_symbol(&mut body, params)?;
        self.post_private(UTA_PLACE_ORDER, Value::Object(body))
            .await
    }

    async fn cancel_uta_order_from_params(
        &self,
        params: &BitgetParams,
    ) -> Result<ValidatedResponse> {
        require_one_identifier(params, &["orderId", "clientOid"])?;
        self.post_private(
            UTA_CANCEL_ORDER,
            Value::Object(params.body(&["orderId", "clientOid", "category"])),
        )
        .await
    }

    async fn place_futures_order_from_params(
        &self,
        params: &BitgetParams,
    ) -> Result<ValidatedResponse> {
        self.place_futures_order_request(params, None, None, None)
            .await
    }

    async fn place_futures_order_request(
        &self,
        params: &BitgetParams,
        side: Option<&str>,
        order_type: Option<&str>,
        force: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut body = params.body(&[
            "productType",
            "marginMode",
            "marginCoin",
            "size",
            "price",
            "side",
            "tradeSide",
            "orderType",
            "force",
            "clientOid",
            "reduceOnly",
        ]);
        self.insert_required_product_symbol(&mut body, params)?;
        if let Some(side) = side {
            body.insert("side".to_string(), Value::String(side.to_string()));
        }
        if let Some(order_type) = order_type {
            body.insert(
                "orderType".to_string(),
                Value::String(order_type.to_string()),
            );
        }
        if let Some(force) = force {
            body.entry("force".to_string())
                .or_insert_with(|| Value::String(force.to_string()));
        }
        self.post_private(FUTURES_PLACE_ORDER, Value::Object(body))
            .await
    }

    async fn place_futures_batch_orders_from_params(
        &self,
        params: &BitgetParams,
    ) -> Result<ValidatedResponse> {
        let mut body = params.body(&["productType", "marginMode", "marginCoin"]);
        self.insert_product_symbol(&mut body, params)?;
        insert_optional_value(&mut body, "orderList", params.json_optional("orderList")?);
        self.post_private(FUTURES_BATCH_PLACE_ORDER, Value::Object(body))
            .await
    }

    async fn cancel_futures_order_from_params(
        &self,
        params: &BitgetParams,
    ) -> Result<ValidatedResponse> {
        require_one_identifier(params, &["orderId", "clientOid"])?;
        let mut body = params.body(&["productType", "marginCoin", "orderId", "clientOid"]);
        self.insert_required_product_symbol(&mut body, params)?;
        self.post_private(FUTURES_CANCEL_ORDER, Value::Object(body))
            .await
    }

    async fn cancel_futures_batch_orders_from_params(
        &self,
        params: &BitgetParams,
    ) -> Result<ValidatedResponse> {
        let mut body = params.body(&["productType", "marginCoin"]);
        self.insert_required_product_symbol(&mut body, params)?;
        insert_optional_value(
            &mut body,
            "orderIdList",
            params.json_optional("orderIdList")?,
        );
        self.post_private(FUTURES_BATCH_CANCEL_ORDERS, Value::Object(body))
            .await
    }
}
