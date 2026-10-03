pub(in crate::exchanges::bitget) use serde_json::Value;

pub(in crate::exchanges::bitget) use crate::Result;
pub(in crate::exchanges::bitget) use crate::exchange::ValidatedResponse;

pub(in crate::exchanges::bitget) use super::client::BitgetClient;
pub(in crate::exchanges::bitget) use super::endpoints::*;
pub(in crate::exchanges::bitget) use super::params::{BitgetParams, require_one_identifier};

pub(in crate::exchanges::bitget) const UTA_ORDER_KEYS: &[&str] = &[
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

impl BitgetClient {
    pub(super) async fn trade_private_request(
        &self,
        method_name: &str,
        params: &BitgetParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "place_uta_order" => self.place_uta_order_from_params(params).await,
            "place_reality_order" => self.place_reality_order_from_params(params).await,
            "place_uta_batch_orders" => {
                self.dispatch_place_uta_batch_orders(method_name, params)
                    .await
            }
            "cancel_uta_order" => self.cancel_uta_order_from_params(params).await,
            "cancel_reality_order" => self.cancel_reality_order_from_params(params).await,
            "cancel_uta_batch_orders" => {
                self.dispatch_cancel_uta_batch_orders(method_name, params)
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

            _ => return Ok(None),
        };
        Ok(Some(result?))
    }

    pub(in crate::exchanges::bitget) async fn place_uta_order_from_params(
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

    pub(in crate::exchanges::bitget) async fn cancel_uta_order_from_params(
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

    pub(in crate::exchanges::bitget) async fn place_reality_order_from_params(
        &self,
        params: &BitgetParams,
    ) -> Result<ValidatedResponse> {
        for key in ["side", "orderType", "qty"] {
            params.required(key)?;
        }
        require_uta_symbol(params)?;
        let mut body = params.body(&["category", "side", "orderType", "qty", "price", "clientOid"]);
        self.insert_uta_symbol(&mut body, params)?;
        self.post_private(REALITY_PLACE_ORDER, Value::Object(body))
            .await
    }

    pub(in crate::exchanges::bitget) async fn cancel_reality_order_from_params(
        &self,
        params: &BitgetParams,
    ) -> Result<ValidatedResponse> {
        require_uta_symbol(params)?;
        require_one_identifier(params, &["orderId", "clientOid"])?;
        let mut body = params.body(&["category", "orderId", "clientOid"]);
        self.insert_uta_symbol(&mut body, params)?;
        self.post_private(REALITY_CANCEL_ORDER, Value::Object(body))
            .await
    }
}

pub(in crate::exchanges::bitget) fn require_uta_symbol(params: &BitgetParams) -> Result<()> {
    require_one_identifier(params, &["product_symbol", "symbol"])
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    pub(in crate::exchanges::bitget) fn preserves_uta_protection_fields() {
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
}
