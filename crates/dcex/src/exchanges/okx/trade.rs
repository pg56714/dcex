use serde_json::{Map, Value};

use crate::common::OrderSide;
use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::OkxClient;
use super::endpoints::*;
use super::params::{insert_optional_bool, insert_optional_string, push_optional, OkxParams};

impl OkxClient {
    pub(super) async fn trade_private_request(
        &self,
        method_name: &str,
        params: &OkxParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "place_order" => self.place_order_from_params(params).await,
            "pre_check_order" => self.pre_check_order_from_params(params).await,
            "set_cancel_all_after" => {
                let mut body = Map::new();
                body.insert(
                    "timeOut".to_string(),
                    Value::String(params.required("timeOut")?.to_string()),
                );
                insert_optional_string(&mut body, "tag", params.get("tag"));
                self.post_request(TRADE_CANCEL_ALL_AFTER, Value::Object(body))
                    .await
            }
            "place_batch_orders" => {
                self.post_request(TRADE_BATCH_ORDERS, params.json_required("orders")?)
                    .await
            }
            "place_market_order" => {
                let mut pairs = params.without(&["ordType"]);
                pairs.push(("ordType".to_string(), "market".to_string()));
                self.place_order_from_params(&OkxParams::from_pairs(pairs))
                    .await
            }
            "place_market_buy_order" => {
                let mut pairs = params.without(&["side", "ordType"]);
                pairs.push(("side".to_string(), "buy".to_string()));
                pairs.push(("ordType".to_string(), "market".to_string()));
                self.place_order_from_params(&OkxParams::from_pairs(pairs))
                    .await
            }
            "place_market_sell_order" => {
                let mut pairs = params.without(&["side", "ordType"]);
                pairs.push(("side".to_string(), "sell".to_string()));
                pairs.push(("ordType".to_string(), "market".to_string()));
                self.place_order_from_params(&OkxParams::from_pairs(pairs))
                    .await
            }
            "place_limit_order" => {
                let mut pairs = params.without(&["ordType"]);
                pairs.push(("ordType".to_string(), "limit".to_string()));
                self.place_order_from_params(&OkxParams::from_pairs(pairs))
                    .await
            }
            "place_limit_buy_order" => {
                let mut pairs = params.without(&["side", "ordType"]);
                pairs.push(("side".to_string(), "buy".to_string()));
                pairs.push(("ordType".to_string(), "limit".to_string()));
                self.place_order_from_params(&OkxParams::from_pairs(pairs))
                    .await
            }
            "place_limit_sell_order" => {
                let mut pairs = params.without(&["side", "ordType"]);
                pairs.push(("side".to_string(), "sell".to_string()));
                pairs.push(("ordType".to_string(), "limit".to_string()));
                self.place_order_from_params(&OkxParams::from_pairs(pairs))
                    .await
            }
            "place_post_only_limit_order" => {
                let mut pairs = params.without(&["ordType"]);
                pairs.push(("ordType".to_string(), "post_only".to_string()));
                self.place_order_from_params(&OkxParams::from_pairs(pairs))
                    .await
            }
            "place_post_only_limit_buy_order" => {
                let mut pairs = params.without(&["side", "ordType"]);
                pairs.push(("side".to_string(), "buy".to_string()));
                pairs.push(("ordType".to_string(), "post_only".to_string()));
                self.place_order_from_params(&OkxParams::from_pairs(pairs))
                    .await
            }
            "place_post_only_limit_sell_order" => {
                let mut pairs = params.without(&["side", "ordType"]);
                pairs.push(("side".to_string(), "sell".to_string()));
                pairs.push(("ordType".to_string(), "post_only".to_string()));
                self.place_order_from_params(&OkxParams::from_pairs(pairs))
                    .await
            }
            "cancel_order" => self.cancel_order_from_params(params).await,
            "cancel_batch_orders" => {
                self.post_request(TRADE_CANCEL_BATCH_ORDERS, params.json_required("orders")?)
                    .await
            }
            "cancel_all_orders" => self.cancel_all_orders_from_params(params).await,
            "amend_order" => self.amend_order_from_params(params).await,
            "amend_multiple_orders" => {
                self.post_request(TRADE_AMEND_BATCH_ORDERS, params.json_required("orders")?)
                    .await
            }
            "close_positions" => {
                let mut body = params.required_body(&["mgnMode"])?;
                self.insert_required_inst_id(&mut body, params)?;
                insert_optional_string(&mut body, "posSide", params.get("posSide"));
                insert_optional_bool(&mut body, "autoCxl", params.get("autoCxl"))?;
                insert_optional_string(&mut body, "ccy", params.get("ccy"));
                insert_optional_string(&mut body, "tag", params.get("tag"));
                self.post_request(TRADE_CLOSE_POSITION, Value::Object(body))
                    .await
            }
            "get_order" => self.get_order_lookup(TRADE_ORDER, params).await,
            "get_order_list" => self.get_order_list_from_params(params).await,
            "get_orders_history" => {
                self.get_order_history_request(TRADE_ORDERS_HISTORY, params, true)
                    .await
            }
            "get_orders_history_archive" => {
                self.get_order_history_request(TRADE_ORDERS_HISTORY_ARCHIVE, params, true)
                    .await
            }
            "get_fills" => self.get_fills_request(TRADE_FILLS, params, false).await,
            "get_fills_history" => {
                self.get_fills_request(TRADE_FILLS_HISTORY, params, true)
                    .await
            }
            "get_account_rate_limit" => {
                self.get_request(TRADE_ACCOUNT_RATE_LIMIT, Vec::new()).await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}

impl OkxClient {
    async fn place_order_from_params(&self, params: &OkxParams) -> Result<ValidatedResponse> {
        self.order_validation_request(params, TRADE_ORDER).await
    }

    async fn pre_check_order_from_params(&self, params: &OkxParams) -> Result<ValidatedResponse> {
        self.order_validation_request(params, TRADE_ORDER_PRECHECK)
            .await
    }

    async fn order_validation_request(
        &self,
        params: &OkxParams,
        endpoint: &str,
    ) -> Result<ValidatedResponse> {
        let mut body = params.required_body(&["tdMode", "ordType", "sz"])?;
        self.insert_required_inst_id(&mut body, params)?;
        body.insert(
            "side".to_string(),
            Value::String(
                OrderSide::parse(params.required("side")?)?
                    .to_exchange("okx")?
                    .to_string(),
            ),
        );
        for key in [
            "ccy",
            "clOrdId",
            "posSide",
            "px",
            "pxUsd",
            "pxVol",
            "reduceOnly",
            "tgtCcy",
            "banAmend",
            "quickMgnType",
            "stpId",
            "stpMode",
            "tag",
        ] {
            insert_optional_string(&mut body, key, params.get(key));
        }
        self.post_request(endpoint, Value::Object(body)).await
    }

    async fn cancel_order_from_params(&self, params: &OkxParams) -> Result<ValidatedResponse> {
        let mut body = Map::new();
        self.insert_required_inst_id(&mut body, params)?;
        insert_optional_string(&mut body, "ordId", params.get("ordId"));
        insert_optional_string(&mut body, "clOrdId", params.get("clOrdId"));
        self.post_request(TRADE_CANCEL_ORDER, Value::Object(body))
            .await
    }

    async fn cancel_all_orders_from_params(&self, params: &OkxParams) -> Result<ValidatedResponse> {
        let orders = self.get_order_list_from_params(params).await?;
        let selected_inst_id = params
            .get("product_symbol")
            .map(|symbol| self.exchange_symbol(symbol))
            .transpose()?;
        let body = orders
            .data
            .get("data")
            .and_then(Value::as_array)
            .map(|orders| {
                orders
                    .iter()
                    .filter_map(|order| order.as_object())
                    .filter(|order| {
                        selected_inst_id.as_ref().is_none_or(|inst_id| {
                            order.get("instId").and_then(Value::as_str) == Some(inst_id.as_str())
                        })
                    })
                    .map(|order| {
                        let mut row = Map::new();
                        for key in ["instId", "ordId", "clOrdId"] {
                            if let Some(value) = order.get(key).and_then(Value::as_str) {
                                row.insert(key.to_string(), Value::String(value.to_string()));
                            }
                        }
                        Value::Object(row)
                    })
                    .collect::<Vec<_>>()
            })
            .unwrap_or_default();
        self.post_request(TRADE_CANCEL_BATCH_ORDERS, Value::Array(body))
            .await
    }

    async fn amend_order_from_params(&self, params: &OkxParams) -> Result<ValidatedResponse> {
        let mut body = Map::new();
        self.insert_required_inst_id(&mut body, params)?;
        for key in [
            "ordId",
            "clOrdId",
            "newSz",
            "newPx",
            "newPxUsd",
            "newPxVol",
            "cxlOnFail",
            "reqId",
        ] {
            insert_optional_string(&mut body, key, params.get(key));
        }
        self.post_request(TRADE_AMEND_ORDER, Value::Object(body))
            .await
    }

    async fn get_order_lookup(&self, path: &str, params: &OkxParams) -> Result<ValidatedResponse> {
        let mut query = Vec::new();
        self.push_required_inst_id(&mut query, params)?;
        push_optional(&mut query, "ordId", params.get("ordId"));
        push_optional(&mut query, "clOrdId", params.get("clOrdId"));
        self.get_request(path, query).await
    }

    async fn get_order_list_from_params(&self, params: &OkxParams) -> Result<ValidatedResponse> {
        let mut query =
            params.only(&["instType", "uly", "instFamily", "ordType", "state", "limit"]);
        self.push_inst_id(&mut query, params, "product_symbol")?;
        self.get_request(TRADE_ORDERS_PENDING, query).await
    }

    async fn get_order_history_request(
        &self,
        path: &str,
        params: &OkxParams,
        require_inst_type: bool,
    ) -> Result<ValidatedResponse> {
        let mut query = if require_inst_type {
            params.required_only(&["instType"])?
        } else {
            Vec::new()
        };
        for key in [
            "uly",
            "instFamily",
            "ordType",
            "state",
            "category",
            "begin",
            "end",
            "limit",
        ] {
            push_optional(&mut query, key, params.get(key));
        }
        self.push_inst_id(&mut query, params, "product_symbol")?;
        self.get_request(path, query).await
    }

    async fn get_fills_request(
        &self,
        path: &str,
        params: &OkxParams,
        require_inst_type: bool,
    ) -> Result<ValidatedResponse> {
        let mut query = if require_inst_type {
            params.required_only(&["instType"])?
        } else {
            Vec::new()
        };
        for key in [
            "instType",
            "uly",
            "instFamily",
            "ordId",
            "subType",
            "begin",
            "end",
            "limit",
        ] {
            if !require_inst_type || key != "instType" {
                push_optional(&mut query, key, params.get(key));
            }
        }
        self.push_inst_id(&mut query, params, "product_symbol")?;
        self.get_request(path, query).await
    }
}
