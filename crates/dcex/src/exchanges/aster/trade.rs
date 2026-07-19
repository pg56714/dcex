use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::{AsterClient, AsterMarket};
use super::endpoints::*;
use super::params::AsterParams;

const FUTURES_ORDER_KEYS: &[&str] = &[
    "positionSide",
    "type",
    "timeInForce",
    "quantity",
    "reduceOnly",
    "price",
    "newClientOrderId",
    "stopPrice",
    "closePosition",
    "activationPrice",
    "callbackRate",
    "workingType",
    "priceProtect",
    "newOrderRespType",
    "pegPriceType",
    "pegOffset",
    "stpMode",
];

impl AsterClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = AsterParams::from_pairs(params);
        if let Some(response) = self.account_private_request(method_name, &params).await? {
            return Ok(response);
        }
        if let Some(response) = self.trade_private_request(method_name, &params).await? {
            return Ok(response);
        }
        Err(DcexError::InvalidInput(format!(
            "unsupported Aster private method: {method_name}"
        )))
    }

    pub(super) async fn trade_private_request(
        &self,
        method_name: &str,
        params: &AsterParams,
    ) -> Result<Option<ValidatedResponse>> {
        let response = match method_name {
            "place_spot_order" => {
                let mut query = params.only(&[
                    "type",
                    "timeInForce",
                    "quantity",
                    "quoteOrderQty",
                    "price",
                    "newClientOrderId",
                    "stopPrice",
                ]);
                self.push_required_symbol(&mut query, params)?;
                self.push_required_side(&mut query, params)?;
                self.signed(HttpMethod::Post, AsterMarket::Spot, SPOT_ORDER, query)
                    .await
            }
            "cancel_spot_order" => {
                ensure_order_lookup(params)?;
                let mut query = params.only(&["orderId", "origClientOrderId"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(HttpMethod::Delete, AsterMarket::Spot, SPOT_ORDER, query)
                    .await
            }
            "get_spot_order" => {
                ensure_order_lookup(params)?;
                let mut query = params.only(&["orderId", "origClientOrderId"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(HttpMethod::Get, AsterMarket::Spot, SPOT_ORDER, query)
                    .await
            }
            "get_spot_open_order" => {
                ensure_order_lookup(params)?;
                let mut query = params.only(&["orderId", "origClientOrderId"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(HttpMethod::Get, AsterMarket::Spot, SPOT_OPEN_ORDER, query)
                    .await
            }
            "get_spot_open_orders" => {
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params)?;
                self.signed(HttpMethod::Get, AsterMarket::Spot, SPOT_OPEN_ORDERS, query)
                    .await
            }
            "cancel_all_spot_open_orders" => {
                let mut query = params.only(&["orderIdList", "origClientOrderIdList"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Delete,
                    AsterMarket::Spot,
                    SPOT_ALL_OPEN_ORDERS,
                    query,
                )
                .await
            }
            "get_spot_all_orders" => {
                let mut query = params.only(&["orderId", "startTime", "endTime", "limit"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(HttpMethod::Get, AsterMarket::Spot, SPOT_ALL_ORDERS, query)
                    .await
            }
            "get_spot_user_trades" => {
                let mut query =
                    params.only(&["orderId", "startTime", "endTime", "fromId", "limit"]);
                self.push_optional_symbol(&mut query, params)?;
                self.signed(HttpMethod::Get, AsterMarket::Spot, SPOT_USER_TRADES, query)
                    .await
            }
            "place_futures_order" => {
                let mut query = params.only(FUTURES_ORDER_KEYS);
                self.push_required_symbol(&mut query, params)?;
                self.push_required_side(&mut query, params)?;
                self.signed(HttpMethod::Post, AsterMarket::Futures, FUTURES_ORDER, query)
                    .await
            }
            "modify_futures_order" => {
                ensure_order_lookup(params)?;
                let mut query = params.only(&["orderId", "origClientOrderId", "quantity", "price"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(HttpMethod::Put, AsterMarket::Futures, FUTURES_ORDER, query)
                    .await
            }
            "place_futures_chase_order" => {
                let mut query = params.only(&[
                    "positionSide",
                    "quantityUnit",
                    "quantity",
                    "reduceOnly",
                    "chaseOffset",
                    "chaseOffsetType",
                    "maxChaseOffset",
                    "maxChaseOffsetType",
                    "priceLimit",
                    "timeInForce",
                    "clientStrategyId",
                ]);
                self.push_required_symbol(&mut query, params)?;
                self.push_required_side(&mut query, params)?;
                self.signed(HttpMethod::Post, AsterMarket::Futures, FUTURES_CHASE, query)
                    .await
            }
            "place_futures_batch_orders" => {
                self.signed(
                    HttpMethod::Post,
                    AsterMarket::Futures,
                    FUTURES_BATCH_ORDERS,
                    vec![(
                        "batchOrders".to_string(),
                        self.resolve_order_array(params, "batchOrders")?,
                    )],
                )
                .await
            }
            "get_futures_order" => {
                ensure_order_lookup(params)?;
                let mut query = params.only(&["orderId", "origClientOrderId"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(HttpMethod::Get, AsterMarket::Futures, FUTURES_ORDER, query)
                    .await
            }
            "cancel_futures_order" => {
                ensure_order_lookup(params)?;
                let mut query = params.only(&["orderId", "origClientOrderId"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Delete,
                    AsterMarket::Futures,
                    FUTURES_ORDER,
                    query,
                )
                .await
            }
            "cancel_all_futures_open_orders" => {
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Delete,
                    AsterMarket::Futures,
                    FUTURES_ALL_OPEN_ORDERS,
                    query,
                )
                .await
            }
            "cancel_futures_batch_orders" => {
                let mut query = params.only(&["orderIdList", "origClientOrderIdList"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Delete,
                    AsterMarket::Futures,
                    FUTURES_BATCH_ORDERS,
                    query,
                )
                .await
            }
            "set_futures_countdown_cancel_all" => {
                let mut query = params.only(&["countdownTime"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Post,
                    AsterMarket::Futures,
                    FUTURES_COUNTDOWN_CANCEL_ALL,
                    query,
                )
                .await
            }
            "get_futures_open_order" => {
                ensure_order_lookup(params)?;
                let mut query = params.only(&["orderId", "origClientOrderId"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_OPEN_ORDER,
                    query,
                )
                .await
            }
            "get_futures_open_orders" => {
                let mut query = Vec::new();
                self.push_optional_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_OPEN_ORDERS,
                    query,
                )
                .await
            }
            "get_futures_all_orders" => {
                let mut query = params.only(&["orderId", "startTime", "endTime", "limit"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_ALL_ORDERS,
                    query,
                )
                .await
            }
            "set_futures_leverage" => {
                let mut query = params.only(&["leverage"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Post,
                    AsterMarket::Futures,
                    FUTURES_LEVERAGE,
                    query,
                )
                .await
            }
            "set_futures_margin_type" => {
                let mut query = params.only(&["marginType"]);
                self.push_required_symbol(&mut query, params)?;
                self.signed(
                    HttpMethod::Post,
                    AsterMarket::Futures,
                    FUTURES_MARGIN_TYPE,
                    query,
                )
                .await
            }
            "place_futures_strategy_order" => {
                self.strategy_order(
                    HttpMethod::Post,
                    FUTURES_PLACE_STRATEGY_ORDER,
                    params,
                    "clientStrategyId",
                )
                .await
            }
            "update_futures_strategy_order" => {
                self.strategy_order(
                    HttpMethod::Post,
                    FUTURES_UPDATE_STRATEGY_ORDER,
                    params,
                    "strategyId",
                )
                .await
            }
            "get_futures_strategy_open_order" => {
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_STRATEGY_OPEN_ORDER,
                    params.only(&["strategyId", "clientStrategyId", "strategyType"]),
                )
                .await
            }
            "get_futures_strategy_history_order" => {
                self.signed(
                    HttpMethod::Get,
                    AsterMarket::Futures,
                    FUTURES_STRATEGY_HISTORY_ORDER,
                    params.only(&[
                        "strategyId",
                        "clientStrategyId",
                        "strategyType",
                        "startTime",
                        "endTime",
                        "limit",
                    ]),
                )
                .await
            }
            _ => return Ok(None),
        }?;
        Ok(Some(response))
    }

    fn push_required_side(
        &self,
        query: &mut Vec<(String, String)>,
        params: &AsterParams,
    ) -> Result<()> {
        query.push((
            "side".to_string(),
            params.required("side")?.to_ascii_uppercase(),
        ));
        Ok(())
    }

    pub(super) fn resolve_order_array(&self, params: &AsterParams, key: &str) -> Result<String> {
        let mut value = params.json_required(key)?;
        let Value::Array(orders) = &mut value else {
            return Err(DcexError::InvalidInput(format!(
                "Aster {key} must be a JSON array."
            )));
        };
        for order in orders {
            self.resolve_order_object(order)?;
        }
        Ok(value.to_string())
    }

    fn resolve_order_object(&self, value: &mut Value) -> Result<()> {
        let Value::Object(order) = value else {
            return Err(DcexError::InvalidInput(
                "Aster order payload must be a JSON object.".to_string(),
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
        } else if let Some(symbol) = order
            .get("symbol")
            .and_then(Value::as_str)
            .filter(|symbol| symbol.contains('-'))
            .map(str::to_string)
        {
            order.insert(
                "symbol".to_string(),
                Value::String(self.exchange_symbol(&symbol)?),
            );
        }
        if let Some(side) = order
            .get("side")
            .and_then(Value::as_str)
            .map(str::to_ascii_uppercase)
        {
            order.insert("side".to_string(), Value::String(side));
        }
        Ok(())
    }

    async fn strategy_order(
        &self,
        method: HttpMethod,
        path: &str,
        params: &AsterParams,
        id_key: &str,
    ) -> Result<ValidatedResponse> {
        let mut query = params.only(&[id_key, "strategyType"]);
        query.push((
            "subOrderList".to_string(),
            self.resolve_order_array(params, "subOrderList")?,
        ));
        self.signed(method, AsterMarket::Futures, path, query).await
    }
}

fn ensure_order_lookup(params: &AsterParams) -> Result<()> {
    if params.get("orderId").is_none() && params.get("origClientOrderId").is_none() {
        return Err(DcexError::InvalidInput(
            "Specify orderId or origClientOrderId.".to_string(),
        ));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn preserves_bbo_peg_fields() {
        let params = AsterParams::from_pairs(vec![
            ("pegPriceType".to_string(), "QUEUE_1".to_string()),
            ("pegOffset".to_string(), "-0.5".to_string()),
        ]);
        let query = params.only(FUTURES_ORDER_KEYS);
        assert!(query.contains(&("pegPriceType".to_string(), "QUEUE_1".to_string())));
        assert!(query.contains(&("pegOffset".to_string(), "-0.5".to_string())));
    }
}
