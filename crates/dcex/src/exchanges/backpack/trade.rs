use std::collections::BTreeMap;

use serde_json::{Map, Value};

use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::BackpackClient;
use super::endpoints::*;
use super::params::{
    insert_optional_integer, insert_optional_string, insert_required_string, BackpackParams,
};

const ORDER_STRING_KEYS: &[&str] = &[
    "side",
    "orderType",
    "quantity",
    "price",
    "quoteQuantity",
    "timeInForce",
    "selfTradePrevention",
    "stopLossLimitPrice",
    "stopLossTriggerBy",
    "stopLossTriggerPrice",
    "takeProfitLimitPrice",
    "takeProfitTriggerBy",
    "takeProfitTriggerPrice",
    "triggerBy",
    "triggerPrice",
    "triggerQuantity",
    "slippageTolerance",
    "slippageToleranceType",
];
const ORDER_INTEGER_KEYS: &[&str] = &["clientId"];
const ORDER_BOOL_KEYS: &[&str] = &[
    "postOnly",
    "reduceOnly",
    "autoBorrow",
    "autoBorrowRepay",
    "autoLend",
    "autoLendRedeem",
];

impl BackpackClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = BackpackParams::from_pairs(params);
        if let Some(response) = self.account_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.rfq_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.trade_private_request(method_name, &params).await? {
            return Ok(response);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported Backpack private method: {method_name}"
        )))
    }

    pub(super) async fn trade_private_request(
        &self,
        method_name: &str,
        params: &BackpackParams,
    ) -> Result<Option<ValidatedResponse>> {
        if !matches!(
            method_name,
            "get_open_order"
                | "place_order"
                | "place_market_order"
                | "place_limit_order"
                | "cancel_order"
                | "place_batch_orders"
                | "get_open_orders"
                | "cancel_open_orders"
                | "get_fill_history"
                | "get_order_history"
                | "get_open_positions"
                | "get_funding_payments"
                | "get_position_history"
        ) {
            return Ok(None);
        }
        self.validate_trade_params(method_name, params)?;
        let response = match method_name {
            "get_open_order" => {
                self.ensure_order_lookup(params)?;
                let mut query = params.only(&["orderId", "clientId"]);
                self.push_required_symbol(&mut query, params)?;
                self.private_get(ORDER, query, "orderQuery").await
            }
            "place_order" => {
                self.private_post_value_with_headers(
                    ORDER,
                    Value::Object(self.order_body(params, None)?),
                    "orderExecute",
                    order_headers(params, true),
                )
                .await
            }
            "place_market_order" => {
                self.private_post_value_with_headers(
                    ORDER,
                    Value::Object(self.order_body(params, Some("Market"))?),
                    "orderExecute",
                    order_headers(params, true),
                )
                .await
            }
            "place_limit_order" => {
                let mut body = self.order_body(params, Some("Limit"))?;
                if !body.contains_key("timeInForce") {
                    insert_required_string(&mut body, "timeInForce", "GTC");
                }
                self.private_post_value_with_headers(
                    ORDER,
                    Value::Object(body),
                    "orderExecute",
                    order_headers(params, true),
                )
                .await
            }
            "cancel_order" => {
                self.ensure_order_lookup(params)?;
                let mut body = Map::new();
                self.insert_required_symbol(&mut body, params)?;
                insert_optional_string(&mut body, "orderId", params.get("orderId"));
                insert_optional_integer(&mut body, "clientId", params.get("clientId"));
                self.private_delete_value(ORDER, Value::Object(body), "orderCancel")
                    .await
            }
            "place_batch_orders" => {
                self.private_post_value_with_headers(
                    ORDERS,
                    self.batch_orders_body(params)?,
                    "orderExecute",
                    order_headers(params, false),
                )
                .await
            }
            "get_open_orders" => {
                let mut query = params.only(&["marketType"]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_get(ORDERS, query, "orderQueryAll").await
            }
            "cancel_open_orders" => {
                let mut body = Map::new();
                self.insert_required_symbol(&mut body, params)?;
                insert_optional_string(&mut body, "orderType", params.get("orderType"));
                self.private_delete_value(ORDERS, Value::Object(body), "orderCancelAll")
                    .await
            }
            "get_fill_history" => {
                let mut query = params.only(&[
                    "orderId",
                    "strategyId",
                    "from",
                    "to",
                    "limit",
                    "offset",
                    "fillType",
                    "marketType",
                    "assetClass",
                    "sortDirection",
                ]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_get(FILLS, query, "fillHistoryQueryAll").await
            }
            "get_order_history" => {
                let mut query = params.only(&[
                    "orderId",
                    "strategyId",
                    "limit",
                    "offset",
                    "marketType",
                    "sortDirection",
                ]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_get(ORDER_HISTORY, query, "orderHistoryQueryAll")
                    .await
            }
            "get_open_positions" => {
                let mut query = params.only(&["marketType"]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_get(POSITION, query, "positionQuery").await
            }
            "get_funding_payments" => {
                let mut query = params.only(&["subaccountId", "limit", "offset", "sortDirection"]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_get(FUNDING, query, "fundingHistoryQueryAll")
                    .await
            }
            "get_position_history" => {
                let mut query =
                    params.only(&["state", "marketType", "limit", "offset", "sortDirection"]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_get(POSITION_HISTORY, query, "positionHistoryQueryAll")
                    .await
            }
            _ => return Ok(None),
        }?;
        Ok(Some(response))
    }

    fn validate_trade_params(&self, method_name: &str, params: &BackpackParams) -> Result<()> {
        const MARKET_TYPES: &[&str] = &["SPOT", "PERP", "IPERP", "DATED", "PREDICTION", "RFQ"];
        match method_name {
            "get_open_order" | "cancel_order" => {
                params.ensure_allowed(&["product_symbol", "symbol", "orderId", "clientId"], &[])?;
                super::market::validate_symbol_selector(params, true)?;
                params.ensure_exactly_one(&["orderId", "clientId"])?;
                params.optional_u64_range("clientId", 0, u32::MAX.into())
            }
            "place_order" => self.validate_order_params(params, None),
            "place_market_order" => self.validate_order_params(params, Some("Market")),
            "place_limit_order" => self.validate_order_params(params, Some("Limit")),
            "place_batch_orders" => {
                params.ensure_allowed(&["orders", "brokerId"], &[])?;
                params.optional_u64_range("brokerId", 0, u16::MAX.into())?;
                let orders = params.json_required("orders")?;
                let Value::Array(orders) = orders else {
                    return Err(DcexError::InvalidInput(
                        "Backpack batch orders must be a JSON array.".to_string(),
                    ));
                };
                if orders.is_empty() || orders.len() > 50 {
                    return Err(DcexError::InvalidInput(
                        "Backpack batch orders must contain between 1 and 50 orders".to_string(),
                    ));
                }
                for order in orders {
                    let Value::Object(order) = order else {
                        return Err(DcexError::InvalidInput(
                            "Backpack batch order must be a JSON object.".to_string(),
                        ));
                    };
                    let order = BackpackParams::from_json_object(&order)?;
                    self.validate_order_params(&order, None)?;
                }
                Ok(())
            }
            "get_open_orders" => {
                params.ensure_allowed(&["product_symbol", "symbol", "marketType"], &[])?;
                super::market::validate_symbol_selector(params, false)?;
                params.optional_one_of("marketType", MARKET_TYPES)
            }
            "cancel_open_orders" => {
                params.ensure_allowed(&["product_symbol", "symbol", "orderType"], &[])?;
                super::market::validate_symbol_selector(params, true)?;
                params.optional_one_of("orderType", &["RestingLimitOrder", "ConditionalOrder"])
            }
            "get_fill_history" => {
                params.ensure_allowed(
                    &[
                        "product_symbol",
                        "symbol",
                        "orderId",
                        "strategyId",
                        "from",
                        "to",
                        "limit",
                        "offset",
                        "fillType",
                        "marketType",
                        "assetClass",
                        "sortDirection",
                    ],
                    &["marketType"],
                )?;
                super::market::validate_symbol_selector(params, false)?;
                params.ensure_time_order("from", "to")?;
                params.optional_one_of(
                    "fillType",
                    &[
                        "User",
                        "BookLiquidation",
                        "Adl",
                        "Backstop",
                        "Liquidation",
                        "AllLiquidation",
                        "CollateralConversion",
                        "CollateralConversionAndSpotLiquidation",
                    ],
                )?;
                params.values_one_of("marketType", MARKET_TYPES)?;
                params.optional_one_of("assetClass", &["CRYPTO", "STOCK"])?;
                validate_history_params(params)
            }
            "get_order_history" => {
                params.ensure_allowed(
                    &[
                        "product_symbol",
                        "symbol",
                        "orderId",
                        "strategyId",
                        "limit",
                        "offset",
                        "marketType",
                        "sortDirection",
                    ],
                    &["marketType"],
                )?;
                super::market::validate_symbol_selector(params, false)?;
                params.values_one_of("marketType", MARKET_TYPES)?;
                validate_history_params(params)
            }
            "get_open_positions" => {
                params.ensure_allowed(&["product_symbol", "symbol", "marketType"], &[])?;
                super::market::validate_symbol_selector(params, false)?;
                params.optional_one_of("marketType", MARKET_TYPES)
            }
            "get_funding_payments" => {
                params.ensure_allowed(
                    &[
                        "product_symbol",
                        "symbol",
                        "subaccountId",
                        "limit",
                        "offset",
                        "sortDirection",
                    ],
                    &[],
                )?;
                super::market::validate_symbol_selector(params, false)?;
                params.optional_u64_range("subaccountId", 0, u16::MAX.into())?;
                validate_history_params(params)
            }
            "get_position_history" => {
                params.ensure_allowed(
                    &[
                        "product_symbol",
                        "symbol",
                        "state",
                        "marketType",
                        "limit",
                        "offset",
                        "sortDirection",
                    ],
                    &["marketType"],
                )?;
                super::market::validate_symbol_selector(params, false)?;
                params.optional_one_of("state", &["Open", "Closed"])?;
                params.values_one_of("marketType", MARKET_TYPES)?;
                validate_history_params(params)
            }
            _ => Ok(()),
        }
    }

    fn validate_order_params(
        &self,
        params: &BackpackParams,
        order_type_override: Option<&str>,
    ) -> Result<()> {
        let mut allowed = vec!["product_symbol", "symbol"];
        allowed.extend(
            ORDER_STRING_KEYS
                .iter()
                .copied()
                .filter(|key| order_type_override.is_none() || *key != "orderType"),
        );
        allowed.extend(ORDER_INTEGER_KEYS);
        allowed.extend(ORDER_BOOL_KEYS);
        allowed.extend(["brokerId", "brokerKey"]);
        params.ensure_allowed(&allowed, &[])?;
        super::market::validate_symbol_selector(params, true)?;
        params.required("side")?;
        params.optional_one_of("side", &["Bid", "Ask"])?;
        let order_type = if let Some(order_type) = order_type_override {
            order_type
        } else {
            params.required("orderType")?
        };
        if !matches!(order_type, "Market" | "Limit") {
            return Err(DcexError::InvalidInput(format!(
                "invalid Backpack orderType: {order_type}"
            )));
        }
        params.optional_u64_range("clientId", 0, u32::MAX.into())?;
        params.optional_u64_range("brokerId", 0, u16::MAX.into())?;
        for key in ORDER_BOOL_KEYS {
            params.optional_bool(key)?;
        }
        params.optional_one_of("timeInForce", &["GTC", "IOC", "FOK"])?;
        params.optional_one_of(
            "selfTradePrevention",
            &["RejectTaker", "RejectMaker", "RejectBoth"],
        )?;
        for key in ["stopLossTriggerBy", "takeProfitTriggerBy", "triggerBy"] {
            params.optional_one_of(key, &["MarkPrice", "LastPrice", "IndexPrice"])?;
        }
        params.optional_one_of("slippageToleranceType", &["TickSize", "Percent"])?;
        match order_type {
            "Market" => {
                params.ensure_exactly_one(&["quantity", "quoteQuantity"])?;
                if params.get("price").is_some() || params.bool("postOnly") == Some(true) {
                    return Err(DcexError::InvalidInput(
                        "Backpack market orders cannot include price or enable postOnly"
                            .to_string(),
                    ));
                }
            }
            "Limit" => {
                params.required("quantity")?;
                params.required("price")?;
                if params.get("quoteQuantity").is_some() {
                    return Err(DcexError::InvalidInput(
                        "Backpack limit orders cannot include quoteQuantity".to_string(),
                    ));
                }
            }
            _ => unreachable!(),
        }
        Ok(())
    }

    fn order_body(
        &self,
        params: &BackpackParams,
        order_type_override: Option<&str>,
    ) -> Result<Map<String, Value>> {
        let mut body = params.body(ORDER_STRING_KEYS, ORDER_INTEGER_KEYS, ORDER_BOOL_KEYS);
        self.insert_required_symbol(&mut body, params)?;
        if let Some(order_type) = order_type_override {
            insert_required_string(&mut body, "orderType", order_type);
        }
        Ok(body)
    }

    pub(super) fn batch_orders_body(&self, params: &BackpackParams) -> Result<Value> {
        let mut orders = params.json_required("orders")?;
        let Value::Array(items) = &mut orders else {
            return Err(DcexError::InvalidInput(
                "Backpack batch orders must be a JSON array.".to_string(),
            ));
        };
        for item in items {
            let Value::Object(order) = item else {
                return Err(DcexError::InvalidInput(
                    "Backpack batch order must be a JSON object.".to_string(),
                ));
            };
            if let Some(product_symbol) = order
                .remove("product_symbol")
                .and_then(|value| value.as_str().map(str::to_string))
            {
                order.insert(
                    "symbol".to_string(),
                    Value::String(self.exchange_symbol(&product_symbol)?),
                );
            }
        }
        Ok(orders)
    }

    fn ensure_order_lookup(&self, params: &BackpackParams) -> Result<()> {
        params.ensure_exactly_one(&["orderId", "clientId"])
    }

    fn insert_required_symbol(
        &self,
        body: &mut Map<String, Value>,
        params: &BackpackParams,
    ) -> Result<()> {
        let symbol = params.required_any(&["product_symbol", "symbol"])?;
        body.insert(
            "symbol".to_string(),
            Value::String(self.exchange_symbol(symbol)?),
        );
        Ok(())
    }
}

fn validate_history_params(params: &BackpackParams) -> Result<()> {
    params.optional_u64_range("limit", 1, 1_000)?;
    params.optional_u64_range("offset", 0, u64::MAX)?;
    params.optional_one_of("sortDirection", &["Asc", "Desc"])
}

fn order_headers(params: &BackpackParams, include_key: bool) -> BTreeMap<String, String> {
    let mut headers = BTreeMap::new();
    if let Some(broker_id) = params.get("brokerId") {
        headers.insert("X-Broker-ID".to_string(), broker_id.to_string());
    }
    if include_key {
        if let Some(broker_key) = params.get("brokerKey") {
            headers.insert("X-Broker-Key".to_string(), broker_key.to_string());
        }
    }
    headers
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn preserves_trigger_protection_and_slippage_fields() {
        let params = BackpackParams::from_pairs(vec![
            ("stopLossTriggerPrice".to_string(), "90".to_string()),
            ("takeProfitLimitPrice".to_string(), "110".to_string()),
            ("triggerQuantity".to_string(), "1".to_string()),
            ("slippageTolerance".to_string(), "0.5".to_string()),
        ]);
        let body = params.body(ORDER_STRING_KEYS, ORDER_INTEGER_KEYS, ORDER_BOOL_KEYS);
        assert!(body.contains_key("stopLossTriggerPrice"));
        assert!(body.contains_key("takeProfitLimitPrice"));
        assert!(body.contains_key("triggerQuantity"));
        assert!(body.contains_key("slippageTolerance"));
    }

    #[test]
    fn validates_current_order_combinations_before_transport() {
        let client =
            BackpackClient::public(5_000, std::time::Duration::from_secs(1)).expect("client");
        let market = BackpackParams::from_pairs(vec![
            ("product_symbol".to_string(), "BTC-USDC-SPOT".to_string()),
            ("side".to_string(), "Bid".to_string()),
            ("quantity".to_string(), "1".to_string()),
        ]);
        client
            .validate_order_params(&market, Some("Market"))
            .expect("valid market order");

        let conflicting_type = BackpackParams::from_pairs(vec![
            ("product_symbol".to_string(), "BTC-USDC-SPOT".to_string()),
            ("side".to_string(), "Bid".to_string()),
            ("orderType".to_string(), "Limit".to_string()),
            ("quantity".to_string(), "1".to_string()),
        ]);
        assert!(client
            .validate_order_params(&conflicting_type, Some("Market"))
            .is_err());

        let market_with_true_post_only = BackpackParams::from_pairs(vec![
            ("product_symbol".to_string(), "BTC-USDC-SPOT".to_string()),
            ("side".to_string(), "Bid".to_string()),
            ("quantity".to_string(), "1".to_string()),
            ("postOnly".to_string(), "True".to_string()),
        ]);
        assert!(client
            .validate_order_params(&market_with_true_post_only, Some("Market"))
            .is_err());

        let broker_params = BackpackParams::from_pairs(vec![
            ("brokerId".to_string(), "42".to_string()),
            ("brokerKey".to_string(), "broker-secret".to_string()),
        ]);
        let headers = order_headers(&broker_params, true);
        assert_eq!(headers.get("X-Broker-ID").map(String::as_str), Some("42"));
        assert_eq!(
            headers.get("X-Broker-Key").map(String::as_str),
            Some("broker-secret")
        );
    }
}
