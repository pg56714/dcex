use std::collections::BTreeMap;

use serde_json::{Map, Value};

use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::{BitmartClient, BitmartMarket};
use super::endpoints::*;
use super::params::{
    insert_optional_integer, insert_optional_string, integer_or_string, BitmartParams,
};

const SPOT_ORDER_KEYS: &[&str] = &["size", "price", "notional", "client_order_id"];
const SPOT_HISTORY_KEYS: &[&str] = &["orderMode", "startTime", "endTime", "limit"];
const CONTRACT_ORDER_STRING_KEYS: &[&str] = &[
    "price",
    "client_order_id",
    "type",
    "leverage",
    "open_type",
    "preset_take_profit_price_type",
    "preset_stop_loss_price_type",
    "preset_take_profit_price",
    "preset_stop_loss_price",
    "stp_mode",
];
const CONTRACT_ORDER_INTEGER_KEYS: &[&str] = &["side", "size", "mode"];

impl BitmartClient {
    pub(super) async fn trade_private_request(
        &self,
        method_name: &str,
        params: &BitmartParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "place_spot_order" => self.spot_order_from_params(params, None, None).await,
            "place_spot_market_order" => {
                self.spot_order_from_params(params, None, Some("market"))
                    .await
            }
            "place_spot_market_buy_order" => {
                self.spot_order_from_params(params, Some("buy"), Some("market"))
                    .await
            }
            "place_spot_market_sell_order" => {
                self.spot_order_from_params(params, Some("sell"), Some("market"))
                    .await
            }
            "place_spot_limit_order" => {
                self.spot_order_from_params(params, None, Some("limit"))
                    .await
            }
            "place_spot_limit_buy_order" => {
                self.spot_order_from_params(params, Some("buy"), Some("limit"))
                    .await
            }
            "place_spot_limit_sell_order" => {
                self.spot_order_from_params(params, Some("sell"), Some("limit"))
                    .await
            }
            "place_spot_post_only_limit_order" => {
                self.spot_order_from_params(params, None, Some("limit_maker"))
                    .await
            }
            "place_spot_post_only_limit_buy_order" => {
                self.spot_order_from_params(params, Some("buy"), Some("limit_maker"))
                    .await
            }
            "place_spot_post_only_limit_sell_order" | "place_post_only_limit_sell_order" => {
                self.spot_order_from_params(params, Some("sell"), Some("limit_maker"))
                    .await
            }
            "cancel_spot_order" => {
                let mut body = Map::new();
                self.insert_required_symbol(&mut body, params, true)?;
                insert_optional_integer(&mut body, "order_id", params.get("order_id"));
                insert_optional_string(&mut body, "client_order_id", params.get("client_order_id"));
                self.post_private(BitmartMarket::Spot, SPOT_CANCEL_ORDER, Value::Object(body))
                    .await
            }
            "cancel_spot_all_order" => {
                let mut body = Map::new();
                self.insert_optional_symbol(&mut body, params, true)?;
                insert_optional_string(&mut body, "side", params.get("side"));
                self.post_private(
                    BitmartMarket::Spot,
                    SPOT_CANCEL_ALL_ORDERS,
                    Value::Object(body),
                )
                .await
            }
            "get_spot_order_by_order_id" => {
                let mut body = params.body(&["orderId", "queryState"]);
                if !body.contains_key("orderId") {
                    body.insert(
                        "orderId".to_string(),
                        Value::String(params.required("order_id")?.to_string()),
                    );
                }
                self.post_private(
                    BitmartMarket::Spot,
                    SPOT_QUERY_ORDER_BY_ID,
                    Value::Object(body),
                )
                .await
            }
            "get_spot_order_by_order_client_id" => {
                let mut body = params.body(&["clientOrderId", "queryState"]);
                if !body.contains_key("clientOrderId") {
                    body.insert(
                        "clientOrderId".to_string(),
                        Value::String(params.required("client_order_id")?.to_string()),
                    );
                }
                self.post_private(
                    BitmartMarket::Spot,
                    SPOT_QUERY_ORDER_BY_CLIENT_ID,
                    Value::Object(body),
                )
                .await
            }
            "get_spot_open_orders" => self.spot_history_request(SPOT_OPEN_ORDERS, params).await,
            "get_spot_account_orders" => {
                self.spot_history_request(SPOT_ACCOUNT_ORDERS, params).await
            }
            "get_spot_account_trade_list" => {
                self.spot_history_request(SPOT_ACCOUNT_TRADE_LIST, params)
                    .await
            }
            "get_spot_order_trade_list" => {
                self.post_private(
                    BitmartMarket::Spot,
                    SPOT_ORDER_TRADE_LIST,
                    Value::Object(params.body(&["orderId"])),
                )
                .await
            }
            "submit_spot_algo_order" => {
                self.spot_algo_request(SPOT_ALGO_SUBMIT_ORDER, params, true)
                    .await
            }
            "cancel_spot_algo_order" => {
                self.spot_algo_request(SPOT_ALGO_CANCEL_ORDER, params, false)
                    .await
            }
            "cancel_all_spot_algo_orders" => {
                self.spot_algo_request(SPOT_ALGO_CANCEL_ALL, params, false)
                    .await
            }
            "get_spot_algo_order" => self.spot_algo_request(SPOT_ALGO_ORDER, params, false).await,
            "get_spot_algo_order_by_client_id" => {
                self.spot_algo_request(SPOT_ALGO_CLIENT_ORDER, params, false)
                    .await
            }
            "get_spot_open_algo_orders" => {
                self.spot_algo_request(SPOT_ALGO_OPEN_ORDERS, params, false)
                    .await
            }
            "place_contract_order" => {
                self.contract_order_from_params(params, None, None, None)
                    .await
            }
            "place_contract_market_order" => {
                self.contract_order_from_params(params, None, Some("market"), None)
                    .await
            }
            "place_contract_market_buy_order" => {
                self.contract_reverse_order(params, 2, 1, true).await
            }
            "place_contract_market_sell_order" => {
                self.contract_reverse_order(params, 1, 4, true).await
            }
            "place_contract_limit_order" => {
                self.contract_order_from_params(params, None, Some("limit"), None)
                    .await
            }
            "place_contract_post_only_order" => {
                self.contract_order_from_params(params, None, Some("limit"), Some(4))
                    .await
            }
            "place_contract_post_only_buy_order" => {
                self.contract_reverse_order(params, 2, 1, false).await
            }
            "place_contract_post_only_sell_order" => {
                self.contract_reverse_order(params, 1, 4, false).await
            }
            "modify_limit_order" => {
                let mut body = Map::new();
                self.insert_required_symbol(&mut body, params, false)?;
                insert_optional_integer(&mut body, "order_id", params.get("order_id"));
                insert_optional_string(&mut body, "client_order_id", params.get("client_order_id"));
                insert_optional_string(&mut body, "price", params.get("price"));
                insert_optional_integer(&mut body, "size", params.get("size"));
                self.post_private(
                    BitmartMarket::Futures,
                    FUTURES_MODIFY_LIMIT_ORDER,
                    Value::Object(body),
                )
                .await
            }
            "cancel_contract_order" => {
                let body = self.contract_cancel_order_body_from_params(params)?;
                self.post_private(
                    BitmartMarket::Futures,
                    FUTURES_CANCEL_ORDER,
                    Value::Object(body),
                )
                .await
            }
            "cancel_all_contract_order" => {
                let mut body = Map::new();
                self.insert_required_symbol(&mut body, params, false)?;
                self.post_private(
                    BitmartMarket::Futures,
                    FUTURES_CANCEL_ALL_ORDERS,
                    Value::Object(body),
                )
                .await
            }
            "transfer_contract" => {
                let mut body = Map::new();
                body.insert("currency".to_string(), Value::String("USDT".to_string()));
                body.insert(
                    "amount".to_string(),
                    Value::String(params.required("amount")?.to_string()),
                );
                body.insert(
                    "type".to_string(),
                    Value::String(params.required("type")?.to_string()),
                );
                self.post_private(
                    BitmartMarket::Futures,
                    FUTURES_TRANSFER,
                    Value::Object(body),
                )
                .await
            }
            "submit_leverage" => {
                let mut body = Map::new();
                self.insert_required_symbol(&mut body, params, false)?;
                insert_optional_string(&mut body, "leverage", params.get("leverage"));
                insert_optional_string(&mut body, "open_type", params.get("open_type"));
                self.post_private(
                    BitmartMarket::Futures,
                    FUTURES_SUBMIT_LEVERAGE,
                    Value::Object(body),
                )
                .await
            }
            "get_contract_order_detail" => {
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params, false)?;
                query.push((
                    "order_id".to_string(),
                    params.required("order_id")?.to_string(),
                ));
                self.get_private(BitmartMarket::Futures, FUTURES_ORDER_DETAIL, query)
                    .await
            }
            "get_contract_order_history" => {
                let mut query = params.only(&["start_time", "end_time"]);
                self.push_required_symbol(&mut query, params, false)?;
                self.get_private(BitmartMarket::Futures, FUTURES_ORDER_HISTORY, query)
                    .await
            }
            "get_contract_open_order" => {
                let mut query = params.only(&["type", "order_state", "limit"]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.get_private(BitmartMarket::Futures, FUTURES_OPEN_ORDERS, query)
                    .await
            }
            "get_contract_position" => {
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params, false)?;
                self.get_private(BitmartMarket::Futures, FUTURES_POSITION, query)
                    .await
            }
            "get_contract_trade" => {
                let mut query = params.only(&["start_time", "end_time"]);
                self.push_required_symbol(&mut query, params, false)?;
                self.get_private(BitmartMarket::Futures, FUTURES_ORDER_TRADE, query)
                    .await
            }
            "get_contract_transaction_history" => {
                let mut query = params.only(&["flow_type", "start_time", "end_time", "page_size"]);
                self.push_optional_symbol(&mut query, params, false)?;
                self.get_private(BitmartMarket::Futures, FUTURES_TRANSACTION_HISTORY, query)
                    .await
            }
            "get_contract_transfer_list" => {
                let mut body = params.body(&["page", "limit", "currency"]);
                insert_optional_string(&mut body, "time_start", params.get("time_start"));
                insert_optional_string(&mut body, "time_end", params.get("time_end"));
                self.post_private(
                    BitmartMarket::Futures,
                    FUTURES_TRANSFER_LIST,
                    Value::Object(body),
                )
                .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }

    async fn spot_order_from_params(
        &self,
        params: &BitmartParams,
        side_override: Option<&str>,
        type_override: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let body = self.spot_order_body_from_params(params, side_override, type_override)?;
        self.post_private(BitmartMarket::Spot, SPOT_SUBMIT_ORDER, Value::Object(body))
            .await
    }

    async fn spot_algo_request(
        &self,
        path: &str,
        params: &BitmartParams,
        require_symbol: bool,
    ) -> Result<ValidatedResponse> {
        let mut body = params.body_all();
        body.remove("product_symbol");
        if require_symbol {
            self.insert_required_symbol(&mut body, params, true)?;
        } else {
            self.insert_optional_symbol(&mut body, params, true)?;
        }
        self.post_private(BitmartMarket::Spot, path, Value::Object(body))
            .await
    }

    pub(super) fn spot_order_body_from_params(
        &self,
        params: &BitmartParams,
        side_override: Option<&str>,
        type_override: Option<&str>,
    ) -> Result<Map<String, Value>> {
        let mut body = Map::new();
        self.insert_required_symbol(&mut body, params, true)?;
        let side = match side_override {
            Some(side) => side,
            None => params.required("side")?,
        };
        let order_type = match type_override {
            Some(order_type) => order_type,
            None => params.required("type")?,
        };
        body.insert("side".to_string(), Value::String(side.to_lowercase()));
        body.insert("type".to_string(), Value::String(order_type.to_string()));
        for key in SPOT_ORDER_KEYS {
            insert_optional_string(&mut body, key, params.get(key));
        }
        Ok(body)
    }

    pub(super) fn contract_cancel_order_body_from_params(
        &self,
        params: &BitmartParams,
    ) -> Result<Map<String, Value>> {
        let mut body = Map::new();
        self.insert_required_symbol(&mut body, params, false)?;
        insert_optional_string(&mut body, "order_id", params.get("order_id"));
        insert_optional_string(&mut body, "client_order_id", params.get("client_order_id"));
        Ok(body)
    }

    async fn spot_history_request(
        &self,
        path: &str,
        params: &BitmartParams,
    ) -> Result<ValidatedResponse> {
        let mut body = params.body(SPOT_HISTORY_KEYS);
        self.insert_optional_symbol(&mut body, params, true)?;
        self.post_private(BitmartMarket::Spot, path, Value::Object(body))
            .await
    }

    async fn contract_order_from_params(
        &self,
        params: &BitmartParams,
        side_override: Option<i64>,
        type_override: Option<&str>,
        mode_override: Option<i64>,
    ) -> Result<ValidatedResponse> {
        let mut body = Map::new();
        self.insert_required_symbol(&mut body, params, false)?;
        let side = match side_override {
            Some(value) => Value::Number(value.into()),
            None => integer_or_string(params.required("side")?),
        };
        body.insert("side".to_string(), side);
        body.insert(
            "size".to_string(),
            integer_or_string(params.required("size")?),
        );
        if let Some(type_override) = type_override {
            body.insert("type".to_string(), Value::String(type_override.to_string()));
        }
        for key in CONTRACT_ORDER_STRING_KEYS {
            if *key != "type" || type_override.is_none() {
                insert_optional_string(&mut body, key, params.get(key));
            }
        }
        for key in CONTRACT_ORDER_INTEGER_KEYS {
            if *key != "side" && *key != "size" {
                insert_optional_integer(&mut body, key, params.get(key));
            }
        }
        if let Some(mode) = mode_override {
            body.insert("mode".to_string(), Value::Number(mode.into()));
        }
        self.post_private(
            BitmartMarket::Futures,
            FUTURES_SUBMIT_ORDER,
            Value::Object(body),
        )
        .await
    }

    async fn contract_reverse_order(
        &self,
        params: &BitmartParams,
        close_position_type: i64,
        open_side: i64,
        market_order: bool,
    ) -> Result<ValidatedResponse> {
        let product_symbol = params.required("product_symbol")?;
        let requested_size = params.required("size")?.parse::<i64>().map_err(|error| {
            DcexError::InvalidInput(format!("invalid BitMart contract size: {error}"))
        })?;
        let close_size = self
            .contract_position_size(product_symbol, close_position_type)
            .await?;
        if close_size == 0 {
            return self
                .contract_order_from_params(
                    params,
                    Some(open_side),
                    Some(if market_order { "market" } else { "limit" }),
                    if market_order { None } else { Some(4) },
                )
                .await;
        }
        let close_side = if close_position_type == 2 { 2 } else { 3 };
        let excess_size = requested_size - close_size;
        if excess_size <= 0 {
            return self
                .contract_order_with_side_and_size(params, close_side, requested_size, market_order)
                .await;
        }
        let close = self
            .contract_order_with_side_and_size(params, close_side, close_size, market_order)
            .await?;
        let open = self
            .contract_order_with_side_and_size(params, open_side, excess_size, market_order)
            .await?;
        Ok(ValidatedResponse {
            status: open.status,
            headers: open.headers.clone(),
            data: Value::Array(vec![close.data, open.data]),
        })
    }

    async fn contract_order_with_side_and_size(
        &self,
        params: &BitmartParams,
        side: i64,
        size: i64,
        market_order: bool,
    ) -> Result<ValidatedResponse> {
        let mut pairs = params.only(&[
            "product_symbol",
            "price",
            "client_order_id",
            "leverage",
            "open_type",
            "mode",
            "preset_take_profit_price_type",
            "preset_stop_loss_price_type",
            "preset_take_profit_price",
            "preset_stop_loss_price",
            "stp_mode",
        ]);
        pairs.push(("side".to_string(), side.to_string()));
        pairs.push(("size".to_string(), size.to_string()));
        self.contract_order_from_params(
            &BitmartParams::from_pairs(pairs),
            None,
            Some(if market_order { "market" } else { "limit" }),
            if market_order { None } else { Some(4) },
        )
        .await
    }

    async fn contract_position_size(
        &self,
        product_symbol: &str,
        position_type: i64,
    ) -> Result<i64> {
        let query = vec![(
            "symbol".to_string(),
            self.exchange_symbol(product_symbol, false)?,
        )];
        let response = self
            .get_private(BitmartMarket::Futures, FUTURES_POSITION, query)
            .await?;
        let positions = response
            .data
            .as_object()
            .and_then(|object| object.get("data"))
            .and_then(Value::as_array)
            .cloned()
            .unwrap_or_default();
        Ok(positions
            .iter()
            .filter(|position| {
                position
                    .get("position_type")
                    .and_then(value_to_i64)
                    .is_some_and(|value| value == position_type)
            })
            .filter_map(|position| position.get("current_amount").and_then(value_to_i64))
            .sum())
    }

    fn push_required_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &BitmartParams,
        spot: bool,
    ) -> Result<()> {
        query.push((
            "symbol".to_string(),
            self.exchange_symbol(params.required("product_symbol")?, spot)?,
        ));
        Ok(())
    }

    fn push_optional_symbol(
        &self,
        query: &mut Vec<(String, String)>,
        params: &BitmartParams,
        spot: bool,
    ) -> Result<()> {
        if let Some(product_symbol) = params.get("product_symbol") {
            query.push((
                "symbol".to_string(),
                self.exchange_symbol(product_symbol, spot)?,
            ));
        }
        Ok(())
    }

    pub(super) fn insert_required_symbol(
        &self,
        body: &mut Map<String, Value>,
        params: &BitmartParams,
        spot: bool,
    ) -> Result<()> {
        body.insert(
            "symbol".to_string(),
            Value::String(self.exchange_symbol(params.required("product_symbol")?, spot)?),
        );
        Ok(())
    }

    fn insert_optional_symbol(
        &self,
        body: &mut Map<String, Value>,
        params: &BitmartParams,
        spot: bool,
    ) -> Result<()> {
        if let Some(product_symbol) = params.get("product_symbol") {
            body.insert(
                "symbol".to_string(),
                Value::String(self.exchange_symbol(product_symbol, spot)?),
            );
        }
        Ok(())
    }
}

fn value_to_i64(value: &Value) -> Option<i64> {
    match value {
        Value::Number(value) => value.as_i64(),
        Value::String(value) => value.parse().ok(),
        _ => None,
    }
}

#[allow(dead_code)]
fn empty_headers() -> BTreeMap<String, String> {
    BTreeMap::new()
}
