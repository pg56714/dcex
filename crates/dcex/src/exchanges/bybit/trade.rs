use serde_json::{Map, Value};

use super::client::BybitClient;
use super::endpoints::*;
use super::params::{insert_optional_string, push_optional, BybitParams};
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
            "place_order" => self.place_order_from_params(&params).await,
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
            "amend_order" => self.amend_order_from_params(&params).await,
            "cancel_order" => self.cancel_order_from_params(&params).await,
            "get_open_orders" => self.get_open_orders_from_params(&params).await,
            "cancel_batch_orders" => self.batch_request(CANCEL_BATCH_ORDERS, &params).await,
            "cancel_all_orders" => self.cancel_all_orders_from_params(&params).await,
            "get_order_history" => self.get_order_history_from_params(&params).await,
            "get_execution_list" => self.get_execution_list_from_params(&params).await,
            "place_batch_order" => self.batch_request(BATCH_PLACE_ORDER, &params).await,
            "amend_batch_order" => self.batch_request(BATCH_AMEND_ORDER, &params).await,
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
            "isLeverage",
            "marketUnit",
            "triggerDirection",
            "orderFilter",
            "triggerPrice",
            "triggerBy",
            "orderIv",
            "timeInForce",
            "takeProfit",
            "stopLoss",
            "tpTriggerBy",
            "slTriggerBy",
            "reduceOnly",
            "closeOnTrigger",
            "tpslMode",
            "tpLimitPrice",
            "slLimitPrice",
            "tpOrderType",
            "slOrderType",
            "positionIdx",
        ] {
            insert_optional_string(&mut body, key, params.get(key));
        }
        self.post_request(PLACE_ORDER, body).await
    }

    async fn amend_order_from_params(&self, params: &BybitParams) -> Result<ValidatedResponse> {
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
        let product_symbol = params.required("product_symbol")?;
        let mut body = Map::new();
        self.insert_symbol_category(&mut body, product_symbol)?;
        insert_optional_string(&mut body, "orderId", params.get("orderId"));
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
        self.get_request(GET_OPEN_ORDERS, query).await
    }

    async fn cancel_all_orders_from_params(
        &self,
        params: &BybitParams,
    ) -> Result<ValidatedResponse> {
        let mut body = Map::new();
        body.insert(
            "category".to_string(),
            Value::String(params.get("category").unwrap_or("linear").to_string()),
        );
        if let Some(product_symbol) = params.get("product_symbol") {
            self.insert_symbol_category(&mut body, product_symbol)?;
        }
        self.post_request(CANCEL_ALL_ORDERS, body).await
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
        push_optional(&mut query, "orderId", params.get("orderId"));
        push_optional(&mut query, "startTime", params.get("startTime"));
        push_optional(&mut query, "cursor", params.get("cursor"));
        push_optional(&mut query, "limit", params.get("limit"));
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
        push_optional(&mut query, "startTime", params.get("startTime"));
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
