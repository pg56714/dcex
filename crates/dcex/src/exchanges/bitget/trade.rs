use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::BitgetClient;
use super::endpoints::*;
use super::params::{insert_optional_value, require_one_identifier, BitgetParams};

const SPOT_ORDER_KEYS: &[&str] = &[
    "side",
    "orderType",
    "size",
    "price",
    "force",
    "clientOid",
    "triggerPrice",
    "tpslType",
    "requestTime",
    "receiveWindow",
    "stpMode",
    "presetTakeProfitPrice",
    "executeTakeProfitPrice",
    "presetStopLossPrice",
    "executeStopLossPrice",
];

const UTA_ORDER_KEYS: &[&str] = &[
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
    "tpTriggerBy",
    "slTriggerBy",
    "takeProfit",
    "stopLoss",
    "tpOrderType",
    "slOrderType",
    "tpLimitPrice",
    "slLimitPrice",
];

const FUTURES_ORDER_KEYS: &[&str] = &[
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
    "presetStopSurplusPrice",
    "presetStopLossPrice",
    "presetStopSurplusExecutePrice",
    "presetStopLossExecutePrice",
    "stpMode",
];

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
                self.get_private(
                    SPOT_ORDER_INFO,
                    params.only(&["orderId", "clientOid", "requestTime", "receiveWindow"]),
                )
                .await
            }
            "get_spot_open_orders" => {
                let mut query = params.only(&[
                    "limit",
                    "idLessThan",
                    "startTime",
                    "endTime",
                    "orderId",
                    "tpslType",
                    "requestTime",
                    "receiveWindow",
                ]);
                self.push_product_symbol(&mut query, params)?;
                self.get_private(SPOT_UNFILLED_ORDERS, query).await
            }
            "get_spot_history_orders" => {
                let mut query = params.only(&[
                    "limit",
                    "idLessThan",
                    "startTime",
                    "endTime",
                    "orderId",
                    "tpslType",
                    "requestTime",
                    "receiveWindow",
                ]);
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
                params.required("category")?;
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
                params.required("category")?;
                let mut query = params.only(&["category", "posSide"]);
                self.push_uta_symbol(&mut query, params)?;
                self.get_private(UTA_POSITIONS, query).await
            }
            "place_uta_strategy_order" => {
                params.required("category")?;
                require_uta_symbol(params)?;
                let mut body = params.body(&[
                    "category",
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
                ]);
                self.insert_required_product_symbol(&mut body, params)?;
                self.post_private(UTA_PLACE_STRATEGY_ORDER, Value::Object(body))
                    .await
            }
            "modify_uta_strategy_order" => {
                params.required("orderId")?;
                params.required("qty")?;
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
                params.required("orderId")?;
                self.post_private(
                    UTA_CANCEL_STRATEGY_ORDER,
                    Value::Object(params.body(&["orderId", "clientOid"])),
                )
                .await
            }
            "get_uta_unfilled_strategy_orders" => {
                params.required("category")?;
                self.get_private(
                    UTA_UNFILLED_STRATEGY_ORDERS,
                    params.only(&["category", "type"]),
                )
                .await
            }
            "get_uta_history_strategy_orders" => {
                params.required("category")?;
                self.get_private(
                    UTA_HISTORY_STRATEGY_ORDERS,
                    params.only(&[
                        "category",
                        "type",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
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
                params.required("productType")?;
                require_one_identifier(params, &["orderId", "clientOid"])?;
                let mut query = params.only(&["productType", "orderId", "clientOid"]);
                self.push_required_product_symbol(&mut query, params)?;
                self.get_private(FUTURES_ORDER_DETAIL, query).await
            }
            "get_futures_open_orders" => {
                params.required("productType")?;
                let mut query = params.only(&[
                    "productType",
                    "orderId",
                    "clientOid",
                    "status",
                    "idLessThan",
                    "startTime",
                    "endTime",
                    "limit",
                ]);
                self.push_product_symbol(&mut query, params)?;
                self.get_private(FUTURES_PENDING_ORDERS, query).await
            }
            "get_futures_history_orders" => {
                params.required("productType")?;
                let mut query = params.only(&[
                    "productType",
                    "orderId",
                    "clientOid",
                    "idLessThan",
                    "orderSource",
                    "startTime",
                    "endTime",
                    "limit",
                ]);
                self.push_product_symbol(&mut query, params)?;
                self.get_private(FUTURES_HISTORY_ORDERS, query).await
            }
            "get_futures_fills" => {
                params.required("productType")?;
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
        params.required("size")?;
        let mut body = params.body(SPOT_ORDER_KEYS);
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
        let effective_order_type =
            body.get("orderType")
                .and_then(Value::as_str)
                .ok_or_else(|| {
                    crate::DcexError::InvalidInput(
                        "missing required parameter: orderType".to_string(),
                    )
                })?;
        if effective_order_type != "market" && force.is_none() && params.get("force").is_none() {
            return Err(crate::DcexError::InvalidInput(
                "missing required parameter: force".to_string(),
            ));
        }
        if side.is_none() {
            params.required("side")?;
        }
        if order_type.is_none() {
            params.required("orderType")?;
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
        insert_optional_value(
            &mut body,
            "orderList",
            Some(params.json_required("orderList")?),
        );
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
        insert_optional_value(
            &mut body,
            "orderList",
            Some(params.json_required("orderList")?),
        );
        self.post_private(SPOT_BATCH_CANCEL_ORDER, Value::Object(body))
            .await
    }

    async fn place_uta_order_from_params(
        &self,
        params: &BitgetParams,
    ) -> Result<ValidatedResponse> {
        let mut body = params.body(UTA_ORDER_KEYS);
        for key in ["category", "side", "orderType", "qty"] {
            params.required(key)?;
        }
        require_uta_symbol(params)?;
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
        let mut body = params.body(FUTURES_ORDER_KEYS);
        params.required("size")?;
        self.insert_required_product_symbol(&mut body, params)?;
        body.entry("productType".to_string())
            .or_insert_with(|| Value::String("USDT-FUTURES".to_string()));
        body.entry("marginMode".to_string())
            .or_insert_with(|| Value::String("crossed".to_string()));
        body.entry("marginCoin".to_string())
            .or_insert_with(|| Value::String("USDT".to_string()));
        if let Some(side) = side {
            body.insert("side".to_string(), Value::String(side.to_string()));
        }
        if let Some(order_type) = order_type {
            body.insert(
                "orderType".to_string(),
                Value::String(order_type.to_string()),
            );
        }
        if side.is_none() {
            params.required("side")?;
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
        for key in ["productType", "marginMode", "marginCoin"] {
            params.required(key)?;
        }
        self.insert_required_product_symbol(&mut body, params)?;
        insert_optional_value(
            &mut body,
            "orderList",
            Some(params.json_required("orderList")?),
        );
        self.post_private(FUTURES_BATCH_PLACE_ORDER, Value::Object(body))
            .await
    }

    async fn cancel_futures_order_from_params(
        &self,
        params: &BitgetParams,
    ) -> Result<ValidatedResponse> {
        require_one_identifier(params, &["orderId", "clientOid"])?;
        params.required("productType")?;
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
        params.required("productType")?;
        self.insert_product_symbol(&mut body, params)?;
        insert_optional_value(
            &mut body,
            "orderIdList",
            params.json_optional("orderIdList")?,
        );
        self.post_private(FUTURES_BATCH_CANCEL_ORDERS, Value::Object(body))
            .await
    }
}

fn require_uta_symbol(params: &BitgetParams) -> Result<()> {
    require_one_identifier(params, &["product_symbol", "symbol"])
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn preserves_uta_protection_fields() {
        let params = BitgetParams::from_pairs(vec![
            ("takeProfit".to_string(), "110".to_string()),
            ("stopLoss".to_string(), "90".to_string()),
            ("tpOrderType".to_string(), "limit".to_string()),
            ("slLimitPrice".to_string(), "89".to_string()),
        ]);
        let body = params.body(UTA_ORDER_KEYS);
        assert!(body.contains_key("takeProfit"));
        assert!(body.contains_key("stopLoss"));
        assert!(body.contains_key("tpOrderType"));
        assert!(body.contains_key("slLimitPrice"));
    }

    #[test]
    fn preserves_classic_futures_protection_fields() {
        let params = BitgetParams::from_pairs(vec![
            ("presetStopSurplusPrice".to_string(), "110".to_string()),
            ("presetStopLossExecutePrice".to_string(), "89".to_string()),
            ("stpMode".to_string(), "cancel_taker".to_string()),
        ]);
        let body = params.body(FUTURES_ORDER_KEYS);
        assert!(body.contains_key("presetStopSurplusPrice"));
        assert!(body.contains_key("presetStopLossExecutePrice"));
        assert!(body.contains_key("stpMode"));
    }
}
