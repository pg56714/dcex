use serde_json::{Map, Value};

use super::client::BybitClient;
use super::endpoints::*;
use super::params::{
    insert_optional_bool, insert_optional_i64, insert_optional_string, push_optional,
    require_one_identifier, BybitParams,
};
use crate::common::OrderSide;
use crate::exchange::ValidatedResponse;
use crate::Result;

impl BybitClient {
    pub(super) async fn trade_private_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "place_order" => self.place_order_from_params(params).await,
            "pre_check_order" => self.pre_check_order_from_params(params).await,
            "set_disconnected_cancel_all" => {
                let mut body = Map::new();
                insert_optional_string(&mut body, "product", params.get("product"));
                body.insert(
                    "timeWindow".to_string(),
                    Value::Number(params.i64_required("timeWindow")?.into()),
                );
                self.post_request(DISCONNECTED_CANCEL_ALL, body).await
            }
            "place_market_order" => {
                let mut pairs = params.without(&["orderType"]);
                pairs.push(("orderType".to_string(), "Market".to_string()));
                self.place_order_from_params(&BybitParams::from_pairs(pairs))
                    .await
            }
            "place_market_buy_order" => {
                let mut pairs = params.without(&["side", "orderType"]);
                pairs.push(("side".to_string(), "Buy".to_string()));
                pairs.push(("orderType".to_string(), "Market".to_string()));
                self.place_order_from_params(&BybitParams::from_pairs(pairs))
                    .await
            }
            "place_market_sell_order" => {
                let mut pairs = params.without(&["side", "orderType"]);
                pairs.push(("side".to_string(), "Sell".to_string()));
                pairs.push(("orderType".to_string(), "Market".to_string()));
                self.place_order_from_params(&BybitParams::from_pairs(pairs))
                    .await
            }
            "place_limit_order" => {
                let mut pairs = params.without(&["orderType"]);
                pairs.push(("orderType".to_string(), "Limit".to_string()));
                self.place_order_from_params(&BybitParams::from_pairs(pairs))
                    .await
            }
            "place_limit_buy_order" => {
                let mut pairs = params.without(&["side", "orderType"]);
                pairs.push(("side".to_string(), "Buy".to_string()));
                pairs.push(("orderType".to_string(), "Limit".to_string()));
                self.place_order_from_params(&BybitParams::from_pairs(pairs))
                    .await
            }
            "place_limit_sell_order" => {
                let mut pairs = params.without(&["side", "orderType"]);
                pairs.push(("side".to_string(), "Sell".to_string()));
                pairs.push(("orderType".to_string(), "Limit".to_string()));
                self.place_order_from_params(&BybitParams::from_pairs(pairs))
                    .await
            }
            "place_post_only_limit_order" => {
                let mut pairs = params.without(&["orderType", "timeInForce"]);
                pairs.push(("orderType".to_string(), "Limit".to_string()));
                pairs.push(("timeInForce".to_string(), "PostOnly".to_string()));
                self.place_order_from_params(&BybitParams::from_pairs(pairs))
                    .await
            }
            "place_post_only_limit_buy_order" => {
                let mut pairs = params.without(&["side", "orderType", "timeInForce"]);
                pairs.push(("side".to_string(), "Buy".to_string()));
                pairs.push(("orderType".to_string(), "Limit".to_string()));
                pairs.push(("timeInForce".to_string(), "PostOnly".to_string()));
                self.place_order_from_params(&BybitParams::from_pairs(pairs))
                    .await
            }
            "place_post_only_limit_sell_order" => {
                let mut pairs = params.without(&["side", "orderType", "timeInForce"]);
                pairs.push(("side".to_string(), "Sell".to_string()));
                pairs.push(("orderType".to_string(), "Limit".to_string()));
                pairs.push(("timeInForce".to_string(), "PostOnly".to_string()));
                self.place_order_from_params(&BybitParams::from_pairs(pairs))
                    .await
            }
            "amend_order" => self.amend_order_from_params(params).await,
            "cancel_order" => self.cancel_order_from_params(params).await,
            "get_open_orders" => self.get_open_orders_from_params(params).await,
            "cancel_batch_orders" => self.batch_request(CANCEL_BATCH_ORDERS, params).await,
            "cancel_all_orders" => self.cancel_all_orders_from_params(params).await,
            "get_order_history" => self.get_order_history_from_params(params).await,
            "get_execution_list" => self.get_execution_list_from_params(params).await,
            "place_batch_order" => self.batch_request(BATCH_PLACE_ORDER, params).await,
            "amend_batch_order" => self.batch_request(BATCH_AMEND_ORDER, params).await,
            "get_borrow_quota" => {
                let product_symbol = params.required("product_symbol")?;
                let query = vec![
                    ("category".to_string(), "spot".to_string()),
                    ("symbol".to_string(), self.exchange_symbol(product_symbol)?),
                    (
                        "side".to_string(),
                        OrderSide::parse(params.required("side")?)?
                            .to_exchange("bybit")?
                            .to_string(),
                    ),
                ];
                self.get_request(GET_BORROW_QUOTA, query).await
            }
            "get_vip_margin_data" => {
                self.get_request(VIP_MARGIN_DATA, params.only(&["vipLevel", "currency"]))
                    .await
            }
            "get_collateral" => {
                self.get_request(SPOT_MARGIN_COLLATERAL, params.only(&["currency"]))
                    .await
            }
            "get_historical_interest_rate" => {
                let mut query = vec![(
                    "currency".to_string(),
                    params.required("currency")?.to_string(),
                )];
                push_optional(&mut query, "vipLevel", params.get("vipLevel"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                push_optional(&mut query, "endTime", params.get("endTime"));
                self.get_request(HISTORICAL_INTEREST, query).await
            }
            "get_status_and_leverage" => self.get_request(STATUS_AND_LEVERAGE, Vec::new()).await,
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }

    async fn place_order_from_params(&self, params: &BybitParams) -> Result<ValidatedResponse> {
        self.order_validation_request(params, PLACE_ORDER).await
    }

    async fn pre_check_order_from_params(&self, params: &BybitParams) -> Result<ValidatedResponse> {
        self.order_validation_request(params, ORDER_PRE_CHECK).await
    }

    async fn order_validation_request(
        &self,
        params: &BybitParams,
        endpoint: &str,
    ) -> Result<ValidatedResponse> {
        let body = self.order_body_from_params(params)?;
        self.post_request(endpoint, body).await
    }

    fn order_body_from_params(&self, params: &BybitParams) -> Result<Map<String, Value>> {
        let product_symbol = params.required("product_symbol")?;
        let mut body = Map::new();
        self.insert_symbol_category(&mut body, product_symbol)?;
        body.insert(
            "side".to_string(),
            Value::String(
                OrderSide::parse(params.required("side")?)?
                    .to_exchange("bybit")?
                    .to_string(),
            ),
        );
        body.insert(
            "orderType".to_string(),
            Value::String(params.required("orderType")?.to_string()),
        );
        body.insert(
            "qty".to_string(),
            Value::String(params.required("qty")?.to_string()),
        );
        for key in [
            "price",
            "marketUnit",
            "slippageToleranceType",
            "slippageTolerance",
            "orderFilter",
            "triggerPrice",
            "triggerBy",
            "orderIv",
            "timeInForce",
            "takeProfit",
            "stopLoss",
            "tpTriggerBy",
            "slTriggerBy",
            "tpslMode",
            "tpLimitPrice",
            "slLimitPrice",
            "tpOrderType",
            "slOrderType",
            "orderLinkId",
            "smpType",
            "bboSideType",
        ] {
            insert_optional_string(&mut body, key, params.get(key));
        }
        for key in ["isLeverage", "triggerDirection", "positionIdx", "bboLevel"] {
            insert_optional_i64(&mut body, key, params.get(key))?;
        }
        for key in ["rpiTakerAccess", "reduceOnly", "closeOnTrigger", "mmp"] {
            insert_optional_bool(&mut body, key, params.get(key))?;
        }
        Ok(body)
    }

    async fn amend_order_from_params(&self, params: &BybitParams) -> Result<ValidatedResponse> {
        require_one_identifier(params, &["orderId", "orderLinkId"])?;
        let product_symbol = params.required("product_symbol")?;
        let mut body = Map::new();
        self.insert_symbol_category(&mut body, product_symbol)?;
        for key in [
            "orderId",
            "orderLinkId",
            "orderIv",
            "triggerPrice",
            "qty",
            "price",
            "tpslMode",
            "takeProfit",
            "stopLoss",
            "tpTriggerBy",
            "slTriggerBy",
            "triggerBy",
            "tpLimitPrice",
            "slLimitPrice",
        ] {
            insert_optional_string(&mut body, key, params.get(key));
        }
        self.post_request(AMEND_ORDER, body).await
    }

    async fn cancel_order_from_params(&self, params: &BybitParams) -> Result<ValidatedResponse> {
        require_one_identifier(params, &["orderId", "orderLinkId"])?;
        let product_symbol = params.required("product_symbol")?;
        let mut body = Map::new();
        self.insert_symbol_category(&mut body, product_symbol)?;
        for key in ["orderId", "orderLinkId", "orderFilter"] {
            insert_optional_string(&mut body, key, params.get(key));
        }
        self.post_request(CANCEL_ORDER, body).await
    }

    async fn get_open_orders_from_params(&self, params: &BybitParams) -> Result<ValidatedResponse> {
        let category = params.get("category").unwrap_or("linear");
        let mut query = vec![
            ("category".to_string(), category.to_string()),
            (
                "limit".to_string(),
                params.get("limit").unwrap_or("20").to_string(),
            ),
        ];
        if let Some(product_symbol) = params.get("product_symbol") {
            self.push_symbol_category(&mut query, product_symbol, true)?;
        } else {
            push_optional(&mut query, "baseCoin", params.get("baseCoin"));
            if let Some(settle_coin) = params.get("settleCoin") {
                query.push(("settleCoin".to_string(), settle_coin.to_string()));
            } else if category == "linear" {
                query.push(("settleCoin".to_string(), "USDT".to_string()));
            }
        }
        for key in [
            "orderId",
            "orderLinkId",
            "openOnly",
            "orderFilter",
            "cursor",
        ] {
            push_optional(&mut query, key, params.get(key));
        }
        self.get_request(GET_OPEN_ORDERS, query).await
    }

    async fn cancel_all_orders_from_params(
        &self,
        params: &BybitParams,
    ) -> Result<ValidatedResponse> {
        let body = self.cancel_all_orders_body_from_params(params)?;
        self.post_request(CANCEL_ALL_ORDERS, body).await
    }

    fn cancel_all_orders_body_from_params(
        &self,
        params: &BybitParams,
    ) -> Result<Map<String, Value>> {
        let mut body = Map::new();
        body.insert(
            "category".to_string(),
            Value::String(params.get("category").unwrap_or("linear").to_string()),
        );
        if let Some(product_symbol) = params.get("product_symbol") {
            self.insert_symbol_category(&mut body, product_symbol)?;
        }
        for key in ["baseCoin", "settleCoin", "orderFilter", "stopOrderType"] {
            insert_optional_string(&mut body, key, params.get(key));
        }
        let category = body
            .get("category")
            .and_then(Value::as_str)
            .unwrap_or("linear");
        if ["linear", "inverse"]
            .iter()
            .any(|candidate| category.eq_ignore_ascii_case(candidate))
            && !["symbol", "baseCoin", "settleCoin"]
                .iter()
                .any(|key| body.contains_key(*key))
        {
            return Err(crate::DcexError::InvalidInput(
                "one of product_symbol, baseCoin, settleCoin is required for Bybit linear or inverse cancel-all"
                    .to_string(),
            ));
        }
        Ok(body)
    }

    async fn get_order_history_from_params(
        &self,
        params: &BybitParams,
    ) -> Result<ValidatedResponse> {
        let mut query = vec![(
            "category".to_string(),
            params.get("category").unwrap_or("linear").to_string(),
        )];
        if let Some(product_symbol) = params.get("product_symbol") {
            self.push_symbol_category(&mut query, product_symbol, true)?;
        }
        for key in [
            "baseCoin",
            "settleCoin",
            "orderId",
            "orderLinkId",
            "orderFilter",
            "orderStatus",
            "startTime",
            "endTime",
            "cursor",
            "limit",
        ] {
            push_optional(&mut query, key, params.get(key));
        }
        self.get_request(GET_ORDER_HISTORY, query).await
    }

    async fn get_execution_list_from_params(
        &self,
        params: &BybitParams,
    ) -> Result<ValidatedResponse> {
        let mut query = vec![
            (
                "category".to_string(),
                params.get("category").unwrap_or("linear").to_string(),
            ),
            (
                "limit".to_string(),
                params.get("limit").unwrap_or("50").to_string(),
            ),
        ];
        if let Some(product_symbol) = params.get("product_symbol") {
            self.push_symbol_category(&mut query, product_symbol, true)?;
        }
        for key in [
            "orderId",
            "orderLinkId",
            "baseCoin",
            "settleCoin",
            "startTime",
            "endTime",
            "execType",
            "cursor",
        ] {
            push_optional(&mut query, key, params.get(key));
        }
        self.get_request(GET_EXECUTION_LIST, query).await
    }

    async fn batch_request(&self, path: &str, params: &BybitParams) -> Result<ValidatedResponse> {
        let mut body = Map::new();
        body.insert(
            "category".to_string(),
            Value::String(params.get("category").unwrap_or("linear").to_string()),
        );
        body.insert("request".to_string(), params.json_required("request")?);
        self.post_request(path, body).await
    }
}

#[cfg(test)]
mod tests {
    use std::time::Duration;

    use super::*;
    use crate::DcexError;

    fn client() -> BybitClient {
        BybitClient::public(5_000, false, Duration::from_secs(1)).expect("client")
    }

    #[test]
    fn linear_cancel_all_requires_a_scope() {
        let error = client()
            .cancel_all_orders_body_from_params(&BybitParams::from_pairs(Vec::new()))
            .expect_err("missing scope must fail");

        assert_eq!(
            error,
            DcexError::InvalidInput(
                "one of product_symbol, baseCoin, settleCoin is required for Bybit linear or inverse cancel-all"
                    .to_string()
            )
        );
    }

    #[test]
    fn cancel_all_forwards_official_scope_and_filter_fields() {
        let body = client()
            .cancel_all_orders_body_from_params(&BybitParams::from_pairs(vec![
                ("category".to_string(), "linear".to_string()),
                ("settleCoin".to_string(), "USDT".to_string()),
                ("orderFilter".to_string(), "Order".to_string()),
            ]))
            .expect("body");

        assert_eq!(
            body.get("settleCoin"),
            Some(&Value::String("USDT".to_string()))
        );
        assert_eq!(
            body.get("orderFilter"),
            Some(&Value::String("Order".to_string()))
        );
    }

    #[test]
    fn cancel_all_infers_inverse_category_from_symbol() {
        let body = client()
            .cancel_all_orders_body_from_params(&BybitParams::from_pairs(vec![(
                "product_symbol".to_string(),
                "BTC-USD-SWAP".to_string(),
            )]))
            .expect("body");

        assert_eq!(
            body.get("category"),
            Some(&Value::String("inverse".to_string()))
        );
        assert_eq!(
            body.get("symbol"),
            Some(&Value::String("BTCUSD".to_string()))
        );
    }

    #[test]
    fn order_body_preserves_official_json_types_and_current_fields() {
        let body = client()
            .order_body_from_params(&BybitParams::from_pairs(vec![
                ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
                ("side".to_string(), "Buy".to_string()),
                ("orderType".to_string(), "Market".to_string()),
                ("qty".to_string(), "1".to_string()),
                ("isLeverage".to_string(), "1".to_string()),
                ("positionIdx".to_string(), "2".to_string()),
                ("bboLevel".to_string(), "3".to_string()),
                ("reduceOnly".to_string(), "true".to_string()),
                ("closeOnTrigger".to_string(), "false".to_string()),
                ("rpiTakerAccess".to_string(), "true".to_string()),
                ("mmp".to_string(), "false".to_string()),
                ("orderLinkId".to_string(), "client-order".to_string()),
                ("smpType".to_string(), "CancelMaker".to_string()),
                ("slippageToleranceType".to_string(), "Percent".to_string()),
                ("slippageTolerance".to_string(), "0.5".to_string()),
                ("bboSideType".to_string(), "Queue".to_string()),
            ]))
            .expect("body");

        assert_eq!(body.get("isLeverage"), Some(&Value::Number(1.into())));
        assert_eq!(body.get("positionIdx"), Some(&Value::Number(2.into())));
        assert_eq!(body.get("bboLevel"), Some(&Value::Number(3.into())));
        assert_eq!(body.get("reduceOnly"), Some(&Value::Bool(true)));
        assert_eq!(body.get("closeOnTrigger"), Some(&Value::Bool(false)));
        assert_eq!(body.get("rpiTakerAccess"), Some(&Value::Bool(true)));
        assert_eq!(body.get("mmp"), Some(&Value::Bool(false)));
        assert_eq!(
            body.get("orderLinkId"),
            Some(&Value::String("client-order".to_string()))
        );
        assert_eq!(
            body.get("slippageToleranceType"),
            Some(&Value::String("Percent".to_string()))
        );
    }
}
