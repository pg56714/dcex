use serde_json::{Map, Value};

use crate::common::OrderSide;
use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::OkxClient;
use super::endpoints::*;
use super::params::{
    insert_optional_bool, insert_optional_string, push_optional, require_one, OkxParams,
};

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
                let orders = params.json_required("orders")?;
                validate_batch_order_slippage(&orders)?;
                self.post_request(TRADE_BATCH_ORDERS, orders).await
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
                insert_optional_string(&mut body, "clOrdId", params.get("clOrdId"));
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
        self.order_validation_request(params, TRADE_ORDER, false)
            .await
    }

    async fn pre_check_order_from_params(&self, params: &OkxParams) -> Result<ValidatedResponse> {
        self.order_validation_request(params, TRADE_ORDER_PRECHECK, true)
            .await
    }

    async fn order_validation_request(
        &self,
        params: &OkxParams,
        endpoint: &str,
        pre_check: bool,
    ) -> Result<ValidatedResponse> {
        let body = self.order_body_from_params(params, pre_check)?;
        self.post_request(endpoint, Value::Object(body)).await
    }

    fn order_body_from_params(
        &self,
        params: &OkxParams,
        pre_check: bool,
    ) -> Result<Map<String, Value>> {
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
        let string_keys: &[&str] = if pre_check {
            &["posSide", "px", "outcome", "tgtCcy"]
        } else {
            &[
                "ccy",
                "clOrdId",
                "posSide",
                "px",
                "speedBump",
                "outcome",
                "pxUsd",
                "pxVol",
                "tgtCcy",
                "pxAmendType",
                "tradeQuoteCcy",
                "slippagePct",
                "stpMode",
                "tag",
            ]
        };
        for key in string_keys {
            insert_optional_string(&mut body, key, params.get(key));
        }
        insert_optional_bool(&mut body, "reduceOnly", params.get("reduceOnly"))?;
        if !pre_check {
            insert_optional_bool(&mut body, "banAmend", params.get("banAmend"))?;
            insert_optional_bool(
                &mut body,
                "isElpTakerAccess",
                params.get("isElpTakerAccess"),
            )?;
        }
        if let Some(value) = params.json_optional("attachAlgoOrds")? {
            body.insert("attachAlgoOrds".to_string(), value);
        }
        validate_slippage_pct(&body)?;
        Ok(body)
    }

    async fn cancel_order_from_params(&self, params: &OkxParams) -> Result<ValidatedResponse> {
        require_one(params, &["ordId", "clOrdId"])?;
        let mut body = Map::new();
        self.insert_required_inst_id(&mut body, params)?;
        insert_optional_string(&mut body, "ordId", params.get("ordId"));
        insert_optional_string(&mut body, "clOrdId", params.get("clOrdId"));
        self.post_request(TRADE_CANCEL_ORDER, Value::Object(body))
            .await
    }

    async fn cancel_all_orders_from_params(&self, params: &OkxParams) -> Result<ValidatedResponse> {
        const PAGE_SIZE: usize = 100;
        const CANCEL_BATCH_SIZE: usize = 20;

        let selected_inst_id = params
            .get("product_symbol")
            .map(|symbol| self.exchange_symbol(symbol))
            .transpose()?;
        let mut base_pairs = params.without(&["after", "before", "limit"]);
        base_pairs.push(("limit".to_string(), PAGE_SIZE.to_string()));
        let mut cursor: Option<String> = None;
        let mut cancel_rows = Vec::new();

        let mut response = loop {
            let mut page_pairs = base_pairs.clone();
            if let Some(cursor) = cursor.as_deref() {
                page_pairs.push(("after".to_string(), cursor.to_string()));
            }
            let response = self
                .get_order_list_from_params(&OkxParams::from_pairs(page_pairs))
                .await?;
            let rows = response
                .data
                .get("data")
                .and_then(Value::as_array)
                .cloned()
                .unwrap_or_default();
            let next_cursor = rows
                .last()
                .and_then(Value::as_object)
                .and_then(|order| order.get("ordId"))
                .and_then(Value::as_str)
                .map(str::to_string);

            cancel_rows.extend(
                rows.iter()
                    .filter_map(Value::as_object)
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
                    }),
            );

            if rows.len() < PAGE_SIZE || next_cursor.is_none() || next_cursor == cursor {
                break response;
            }
            cursor = next_cursor;
        };

        if cancel_rows.is_empty() {
            return Ok(response);
        }

        let mut cancellation_results = Vec::new();
        for chunk in cancel_rows.chunks(CANCEL_BATCH_SIZE) {
            let batch_response = self
                .post_request(TRADE_CANCEL_BATCH_ORDERS, Value::Array(chunk.to_vec()))
                .await?;
            if let Some(rows) = batch_response.data.get("data").and_then(Value::as_array) {
                cancellation_results.extend(rows.iter().cloned());
            }
            response.status = batch_response.status;
            response.headers = batch_response.headers;
        }
        response.data = serde_json::json!({
            "code": "0",
            "msg": "",
            "data": cancellation_results,
        });
        Ok(response)
    }

    async fn amend_order_from_params(&self, params: &OkxParams) -> Result<ValidatedResponse> {
        require_one(params, &["ordId", "clOrdId"])?;
        require_one(
            params,
            &[
                "newSz",
                "newPx",
                "speedBump",
                "newPxUsd",
                "newPxVol",
                "attachAlgoOrds",
            ],
        )?;
        let mut body = Map::new();
        self.insert_required_inst_id(&mut body, params)?;
        for key in [
            "ordId",
            "clOrdId",
            "newSz",
            "newPx",
            "speedBump",
            "newPxUsd",
            "newPxVol",
            "pxAmendType",
            "reqId",
        ] {
            insert_optional_string(&mut body, key, params.get(key));
        }
        insert_optional_bool(&mut body, "cxlOnFail", params.get("cxlOnFail"))?;
        if let Some(value) = params.json_optional("attachAlgoOrds")? {
            body.insert("attachAlgoOrds".to_string(), value);
        }
        self.post_request(TRADE_AMEND_ORDER, Value::Object(body))
            .await
    }

    async fn get_order_lookup(&self, path: &str, params: &OkxParams) -> Result<ValidatedResponse> {
        require_one(params, &["ordId", "clOrdId"])?;
        let mut query = Vec::new();
        self.push_required_inst_id(&mut query, params)?;
        push_optional(&mut query, "ordId", params.get("ordId"));
        push_optional(&mut query, "clOrdId", params.get("clOrdId"));
        self.get_request(path, query).await
    }

    async fn get_order_list_from_params(&self, params: &OkxParams) -> Result<ValidatedResponse> {
        let mut query = params.only(&[
            "instType",
            "instFamily",
            "ordType",
            "state",
            "after",
            "before",
            "limit",
        ]);
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
            "instFamily",
            "ordType",
            "state",
            "category",
            "after",
            "before",
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
            "instFamily",
            "ordId",
            "subType",
            "after",
            "before",
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

fn validate_batch_order_slippage(orders: &Value) -> Result<()> {
    let orders = orders
        .as_array()
        .ok_or_else(|| DcexError::InvalidInput("OKX orders must be a JSON array".to_string()))?;
    for order in orders {
        let order = order.as_object().ok_or_else(|| {
            DcexError::InvalidInput("each OKX batch order must be a JSON object".to_string())
        })?;
        validate_slippage_pct(order)?;
    }
    Ok(())
}

fn validate_slippage_pct(order: &Map<String, Value>) -> Result<()> {
    let Some(value) = order.get("slippagePct") else {
        return Ok(());
    };
    let value = value
        .as_str()
        .ok_or_else(|| DcexError::InvalidInput("OKX slippagePct must be a string".to_string()))?;
    if value.is_empty() {
        return Ok(());
    }
    let mut parts = value.split('.');
    let whole = parts.next().unwrap_or_default();
    let fractional = parts.next();
    if whole.is_empty()
        || !whole.chars().all(|character| character.is_ascii_digit())
        || fractional.is_some_and(|digits| {
            digits.is_empty()
                || digits.len() > 4
                || !digits.chars().all(|character| character.is_ascii_digit())
        })
        || parts.next().is_some()
    {
        return Err(DcexError::InvalidInput(
            "OKX slippagePct must be a decimal with at most four fractional digits".to_string(),
        ));
    }
    let parsed = value
        .parse::<f64>()
        .map_err(|error| DcexError::InvalidInput(format!("invalid OKX slippagePct: {error}")))?;
    if !parsed.is_finite() || !(0.0..=0.05).contains(&parsed) {
        return Err(DcexError::InvalidInput(
            "OKX slippagePct must be between 0 and 0.05 inclusive".to_string(),
        ));
    }
    let inst_id = order
        .get("instId")
        .and_then(Value::as_str)
        .unwrap_or_default();
    if inst_id.split('-').count() != 2
        || order.get("ordType").and_then(Value::as_str) != Some("market")
    {
        return Err(DcexError::InvalidInput(
            "OKX slippagePct is only supported for spot and spot-margin market orders".to_string(),
        ));
    }
    let expected_tgt_ccy = match order.get("side").and_then(Value::as_str) {
        Some("buy") => "base_ccy",
        Some("sell") => "quote_ccy",
        _ => {
            return Err(DcexError::InvalidInput(
                "OKX slippagePct requires side buy or sell".to_string(),
            ));
        }
    };
    if order.get("tgtCcy").and_then(Value::as_str) != Some(expected_tgt_ccy) {
        return Err(DcexError::InvalidInput(format!(
            "OKX slippagePct requires tgtCcy={expected_tgt_ccy} for this side"
        )));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use std::time::Duration;

    use serde_json::json;

    use super::*;

    fn client() -> OkxClient {
        OkxClient::public(Duration::from_secs(1)).expect("client")
    }

    #[test]
    fn place_order_body_preserves_boolean_and_array_json_types() {
        let params = OkxParams::from_pairs(vec![
            ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
            ("tdMode".to_string(), "cross".to_string()),
            ("side".to_string(), "buy".to_string()),
            ("ordType".to_string(), "limit".to_string()),
            ("sz".to_string(), "1".to_string()),
            ("reduceOnly".to_string(), "true".to_string()),
            ("banAmend".to_string(), "false".to_string()),
            ("isElpTakerAccess".to_string(), "true".to_string()),
            (
                "attachAlgoOrds".to_string(),
                r#"[{"tpTriggerPx":"110","tpOrdPx":"109"}]"#.to_string(),
            ),
        ]);

        let body = client()
            .order_body_from_params(&params, false)
            .expect("body");
        assert_eq!(body["reduceOnly"], Value::Bool(true));
        assert_eq!(body["banAmend"], Value::Bool(false));
        assert_eq!(body["isElpTakerAccess"], Value::Bool(true));
        assert_eq!(
            body["attachAlgoOrds"],
            json!([{"tpTriggerPx": "110", "tpOrdPx": "109"}])
        );
    }

    #[test]
    fn precheck_body_drops_place_only_fields() {
        let params = OkxParams::from_pairs(vec![
            ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
            ("tdMode".to_string(), "cross".to_string()),
            ("side".to_string(), "buy".to_string()),
            ("ordType".to_string(), "limit".to_string()),
            ("sz".to_string(), "1".to_string()),
            ("px".to_string(), "100".to_string()),
            ("outcome".to_string(), "yes".to_string()),
            ("clOrdId".to_string(), "not-valid-for-precheck".to_string()),
            ("stpMode".to_string(), "cancel_maker".to_string()),
        ]);

        let body = client()
            .order_body_from_params(&params, true)
            .expect("body");
        assert_eq!(body["outcome"], "yes");
        assert!(!body.contains_key("clOrdId"));
        assert!(!body.contains_key("stpMode"));
    }
}
