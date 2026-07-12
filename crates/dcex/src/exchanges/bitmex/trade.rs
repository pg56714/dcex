use serde_json::{Map, Value};

use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::BitmexClient;
use super::endpoints::*;
use super::params::BitmexParams;

const ORDER_STRING_KEYS: &[&str] = &[
    "side",
    "ordType",
    "clOrdID",
    "clOrdLinkID",
    "contingencyType",
    "execInst",
    "pegPriceType",
    "timeInForce",
    "text",
];
const ORDER_NUMBER_KEYS: &[&str] = &[
    "orderQty",
    "price",
    "stopPx",
    "displayQty",
    "pegOffsetValue",
    "targetAccountId",
];
const AMEND_STRING_KEYS: &[&str] = &["orderID", "origClOrdID", "clOrdID", "text"];
const AMEND_NUMBER_KEYS: &[&str] = &[
    "leavesQty",
    "orderQty",
    "price",
    "stopPx",
    "pegOffsetValue",
    "targetAccountId",
];
const CANCEL_STRING_KEYS: &[&str] = &["text"];
const CANCEL_NUMBER_KEYS: &[&str] = &["targetAccountId"];
const CANCEL_JSON_KEYS: &[&str] = &["orderID", "clOrdID"];
const CANCEL_ALL_STRING_KEYS: &[&str] = &["filter", "text"];
const CANCEL_ALL_NUMBER_KEYS: &[&str] = &["targetAccountId"];
const CANCEL_ALL_JSON_KEYS: &[&str] = &["targetAccountIds"];
const QUERY_ORDER_KEYS: &[&str] = &[
    "targetAccountId",
    "filter",
    "columns",
    "count",
    "start",
    "reverse",
    "startTime",
    "endTime",
    "targetAccountIds",
    "targetAccountIds[]",
];

impl BitmexClient {
    pub(super) async fn trade_private_request(
        &self,
        method_name: &str,
        params: &BitmexParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "place_order" => self.order_from_params(params, None, None, None).await,
            "place_market_order" => {
                self.order_from_params(params, None, Some("Market"), None)
                    .await
            }
            "place_market_buy_order" => {
                self.order_from_params(params, Some("Buy"), Some("Market"), None)
                    .await
            }
            "place_market_sell_order" => {
                self.order_from_params(params, Some("Sell"), Some("Market"), None)
                    .await
            }
            "place_limit_order" => {
                self.order_from_params(
                    params,
                    None,
                    Some("Limit"),
                    Some(("timeInForce", "GoodTillCancel")),
                )
                .await
            }
            "place_limit_buy_order" => {
                self.order_from_params(
                    params,
                    Some("Buy"),
                    Some("Limit"),
                    Some(("timeInForce", "GoodTillCancel")),
                )
                .await
            }
            "place_limit_sell_order" => {
                self.order_from_params(
                    params,
                    Some("Sell"),
                    Some("Limit"),
                    Some(("timeInForce", "GoodTillCancel")),
                )
                .await
            }
            "place_post_only_order" => {
                self.order_from_params(
                    params,
                    None,
                    Some("Limit"),
                    Some(("execInst", "ParticipateDoNotInitiate")),
                )
                .await
            }
            "place_post_only_buy_order" => {
                self.order_from_params(
                    params,
                    Some("Buy"),
                    Some("Limit"),
                    Some(("execInst", "ParticipateDoNotInitiate")),
                )
                .await
            }
            "place_post_only_sell_order" => {
                self.order_from_params(
                    params,
                    Some("Sell"),
                    Some("Limit"),
                    Some(("execInst", "ParticipateDoNotInitiate")),
                )
                .await
            }
            "amend_order" => {
                let body = self.amend_order_body_from_params(params)?;
                self.private_json(HttpMethod::Put, AMEND_ORDER, Value::Object(body))
                    .await
            }
            "cancel_order" => {
                let body = self.cancel_order_body_from_params(params);
                self.private_json(HttpMethod::Delete, CANCEL_ORDER, Value::Object(body))
                    .await
            }
            "cancel_all_orders" => {
                let body = self.cancel_all_orders_body_from_params(params)?;
                self.private_json(HttpMethod::Delete, CANCEL_ALL_ORDERS, Value::Object(body))
                    .await
            }
            "set_cancel_all_after" => {
                let body = params.body(&[], &["timeout", "targetAccountId"], &[], &[]);
                self.private_json(HttpMethod::Post, CANCEL_ALL_AFTER, Value::Object(body))
                    .await
            }
            "get_order" => {
                let mut query = params.only(QUERY_ORDER_KEYS);
                self.push_product_symbol(&mut query, params)?;
                self.get_private(QUERY_ORDER, query).await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }

    async fn order_from_params(
        &self,
        params: &BitmexParams,
        side_override: Option<&str>,
        ord_type_override: Option<&str>,
        default_pair: Option<(&str, &str)>,
    ) -> Result<ValidatedResponse> {
        let body =
            self.order_body_from_params(params, side_override, ord_type_override, default_pair)?;
        self.private_json(HttpMethod::Post, PLACE_ORDER, Value::Object(body))
            .await
    }

    pub(super) fn order_body_from_params(
        &self,
        params: &BitmexParams,
        side_override: Option<&str>,
        ord_type_override: Option<&str>,
        default_pair: Option<(&str, &str)>,
    ) -> Result<Map<String, Value>> {
        let mut body = params.body(ORDER_STRING_KEYS, ORDER_NUMBER_KEYS, &[], &[]);
        self.insert_required_product_symbol(&mut body, params)?;
        if let Some(side) = side_override {
            body.insert("side".to_string(), Value::String(side.to_string()));
        }
        if let Some(ord_type) = ord_type_override {
            body.insert("ordType".to_string(), Value::String(ord_type.to_string()));
        } else if !body.contains_key("ordType") {
            body.insert("ordType".to_string(), Value::String("Limit".to_string()));
        }
        if let Some((key, value)) = default_pair {
            body.entry(key.to_string())
                .or_insert_with(|| Value::String(value.to_string()));
        }
        Ok(body)
    }

    pub(super) fn amend_order_body_from_params(
        &self,
        params: &BitmexParams,
    ) -> Result<Map<String, Value>> {
        if params.get("orderID").is_none() && params.get("origClOrdID").is_none() {
            return Err(DcexError::InvalidInput(
                "Either orderID or origClOrdID must be provided".to_string(),
            ));
        }
        let mut body = params.body(AMEND_STRING_KEYS, AMEND_NUMBER_KEYS, &[], &[]);
        self.insert_product_symbol(&mut body, params)?;
        Ok(body)
    }

    pub(super) fn cancel_order_body_from_params(
        &self,
        params: &BitmexParams,
    ) -> Map<String, Value> {
        params.body(
            CANCEL_STRING_KEYS,
            CANCEL_NUMBER_KEYS,
            &[],
            CANCEL_JSON_KEYS,
        )
    }

    pub(super) fn cancel_all_orders_body_from_params(
        &self,
        params: &BitmexParams,
    ) -> Result<Map<String, Value>> {
        let mut body = params.body(
            CANCEL_ALL_STRING_KEYS,
            CANCEL_ALL_NUMBER_KEYS,
            &[],
            CANCEL_ALL_JSON_KEYS,
        );
        self.insert_product_symbol(&mut body, params)?;
        Ok(body)
    }
}
