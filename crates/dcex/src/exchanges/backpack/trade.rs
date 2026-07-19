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
        let response = match method_name {
            "get_open_order" => {
                self.ensure_order_lookup(params)?;
                let mut query = params.only(&["orderId", "clientId"]);
                self.push_required_symbol(&mut query, params)?;
                self.private_get(ORDER, query, "orderQuery").await
            }
            "place_order" => {
                self.private_post_value(
                    ORDER,
                    Value::Object(self.order_body(params, None)?),
                    "orderExecute",
                )
                .await
            }
            "place_market_order" => {
                self.private_post_value(
                    ORDER,
                    Value::Object(self.order_body(params, Some("Market"))?),
                    "orderExecute",
                )
                .await
            }
            "place_limit_order" => {
                let mut body = self.order_body(params, Some("Limit"))?;
                if !body.contains_key("timeInForce") {
                    insert_required_string(&mut body, "timeInForce", "GTC");
                }
                self.private_post_value(ORDER, Value::Object(body), "orderExecute")
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
                self.private_post_value(ORDERS, self.batch_orders_body(params)?, "orderExecute")
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
                let mut query =
                    params.only(&["orderId", "limit", "offset", "marketType", "sortDirection"]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_get(FILLS, query, "fillHistoryQueryAll").await
            }
            "get_order_history" => {
                let mut query =
                    params.only(&["orderId", "limit", "offset", "marketType", "sortDirection"]);
                self.push_optional_symbol(&mut query, params)?;
                self.private_get(ORDER_HISTORY, query, "orderHistoryQueryAll")
                    .await
            }
            "get_open_positions" => {
                let mut query = Vec::new();
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
        if params.get("orderId").is_none() && params.get("clientId").is_none() {
            return Err(DcexError::InvalidInput(
                "Specify orderId or clientId.".to_string(),
            ));
        }
        Ok(())
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
}
