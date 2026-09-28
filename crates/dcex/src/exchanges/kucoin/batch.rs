//! Fund movement and batch request implementations.

mod trade_operations {
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::kucoin::client::{KucoinClient, KucoinMarket};
    use crate::exchanges::kucoin::endpoints::*;
    use crate::exchanges::kucoin::params::{KucoinParams, bool_value, json_value_string};
    use crate::exchanges::kucoin::trade::*;
    use crate::{DcexError, Result};
    use serde_json::{Map, Value};
    impl KucoinClient {
        pub(in crate::exchanges::kucoin) async fn spot_batch_orders_from_params(
            &self,
            params: &KucoinParams,
            type_override: Option<&str>,
        ) -> Result<ValidatedResponse> {
            self.spot_batch_orders_to_path(params, type_override, SPOT_BATCH_ORDERS)
                .await
        }

        pub(in crate::exchanges::kucoin) async fn spot_batch_orders_to_path(
            &self,
            params: &KucoinParams,
            type_override: Option<&str>,
            path: &str,
        ) -> Result<ValidatedResponse> {
            params.ensure_allowed(&["orders"])?;
            let orders = params.json_required("orders")?;
            let orders = orders.as_array().ok_or_else(|| {
                DcexError::InvalidInput("KuCoin orders must be a JSON array.".to_string())
            })?;
            if orders.is_empty() || orders.len() > 20 {
                return Err(DcexError::InvalidInput(
                    "KuCoin batch orders must contain between 1 and 20 orders.".to_string(),
                ));
            }
            let mut order_list = Vec::with_capacity(orders.len());
            for order in orders {
                let mut order = order.as_object().cloned().ok_or_else(|| {
                    DcexError::InvalidInput("KuCoin batch order must be a JSON object.".to_string())
                })?;
                if let Some(order_type) = type_override {
                    order.insert("type".to_string(), Value::String(order_type.to_string()));
                }
                let order_params = KucoinParams::from_pairs(
                    order
                        .iter()
                        .map(|(key, value)| (key.clone(), json_value_string(value)))
                        .collect(),
                );
                validate_spot_order(&order_params, None, None, false)?;
                let symbol = order
                    .remove("symbol")
                    .or_else(|| order.get("product_symbol").cloned());
                order.remove("product_symbol");
                if let Some(symbol) = symbol.map(|value| json_value_string(&value)) {
                    order.insert(
                        "symbol".to_string(),
                        Value::String(self.exchange_symbol(&symbol, false)?),
                    );
                }
                for key in SPOT_ORDER_STRING_KEYS {
                    if let Some(value) = order.get_mut(*key) {
                        *value = Value::String(json_value_string(value));
                    }
                }
                for key in SPOT_ORDER_INTEGER_KEYS {
                    if let Some(value) = order.get_mut(*key) {
                        let parsed = json_value_string(value).parse::<i64>().map_err(|_| {
                            DcexError::InvalidInput(format!(
                                "KuCoin batch order field {key} must be an integer"
                            ))
                        })?;
                        *value = Value::Number(parsed.into());
                    }
                }
                for key in SPOT_ORDER_BOOL_KEYS {
                    if let Some(value) = order.get_mut(*key) {
                        let parsed = bool_value(&json_value_string(value)).ok_or_else(|| {
                            DcexError::InvalidInput(format!(
                                "KuCoin batch order field {key} must be true or false"
                            ))
                        })?;
                        *value = Value::Bool(parsed);
                    }
                }
                order_list.push(Value::Object(order));
            }
            let mut body = Map::new();
            body.insert("orderList".to_string(), Value::Array(order_list));
            self.private_post(KucoinMarket::Spot, path, Value::Object(body))
                .await
        }
    }
}

mod trade_requests {
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::kucoin::client::KucoinClient;

    use crate::exchanges::kucoin::params::KucoinParams;

    use crate::Result;

    impl KucoinClient {
        pub(in crate::exchanges::kucoin) async fn dispatch_place_spot_batch_orders_sync(
            &self,
            _method_name: &str,
            params: &KucoinParams,
        ) -> Result<ValidatedResponse> {
            {
                self.spot_batch_orders_to_path(params, None, "/api/v1/hf/orders/multi/sync")
                    .await
            }
        }
        pub(in crate::exchanges::kucoin) async fn dispatch_place_spot_batch_orders(
            &self,
            _method_name: &str,
            params: &KucoinParams,
        ) -> Result<ValidatedResponse> {
            self.spot_batch_orders_from_params(params, None).await
        }
        pub(in crate::exchanges::kucoin) async fn dispatch_place_spot_batch_limit_orders(
            &self,
            _method_name: &str,
            params: &KucoinParams,
        ) -> Result<ValidatedResponse> {
            {
                self.spot_batch_orders_from_params(params, Some("limit"))
                    .await
            }
        }
        pub(in crate::exchanges::kucoin) async fn dispatch_place_spot_batch_market_orders(
            &self,
            _method_name: &str,
            params: &KucoinParams,
        ) -> Result<ValidatedResponse> {
            {
                self.spot_batch_orders_from_params(params, Some("market"))
                    .await
            }
        }
    }
}

mod uta_requests {
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::kucoin::client::{KucoinClient, KucoinMarket};
    use crate::exchanges::kucoin::endpoints::*;
    use crate::exchanges::kucoin::params::KucoinParams;
    use crate::exchanges::kucoin::uta::*;
    use crate::{DcexError, Result};
    use serde_json::Value;
    impl KucoinClient {
        pub(in crate::exchanges::kucoin) async fn dispatch_batch_cancel_uta_orders(
            &self,
            _method_name: &str,
            params: &KucoinParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&["tradeType", "cancelOrderList"])?;
                validate_trade_type(params)?;
                let mut orders = params.json_required("cancelOrderList")?;
                let items = orders
                    .as_array_mut()
                    .filter(|items| !items.is_empty() && items.len() <= 20)
                    .ok_or_else(|| {
                        DcexError::InvalidInput(
                            "KuCoin UTA batch cancel requires 1 to 20 orders".into(),
                        )
                    })?;
                for item in items {
                    let object = item.as_object_mut().ok_or_else(|| {
                        DcexError::InvalidInput("KuCoin cancel order must be an object".into())
                    })?;
                    if object
                        .keys()
                        .any(|key| !["symbol", "orderId", "clientOid"].contains(&key.as_str()))
                    {
                        return Err(DcexError::InvalidInput(
                            "unsupported KuCoin batch cancel order field".into(),
                        ));
                    }
                    if !["orderId", "clientOid"].iter().any(|key| {
                        object
                            .get(*key)
                            .and_then(Value::as_str)
                            .is_some_and(|v| !v.trim().is_empty())
                    }) {
                        return Err(DcexError::InvalidInput(
                            "KuCoin batch cancel requires orderId or clientOid".into(),
                        ));
                    }
                    for key in ["orderId", "clientOid"] {
                        if object.get(key).is_some_and(|v| !v.is_string()) {
                            return Err(DcexError::InvalidInput(format!(
                                "KuCoin {key} must be a string"
                            )));
                        }
                    }
                    let symbol = object
                        .get("symbol")
                        .and_then(Value::as_str)
                        .filter(|s| !s.trim().is_empty())
                        .ok_or_else(|| {
                            DcexError::InvalidInput("KuCoin batch cancel requires symbol".into())
                        })?;
                    if is_spot_symbol(symbol) == uta_is_futures(params) {
                        return Err(DcexError::InvalidInput(
                            "symbol does not match tradeType".into(),
                        ));
                    }
                    let symbol = self.exchange_symbol(symbol, uta_is_futures(params))?;
                    object.insert("symbol".into(), Value::String(symbol));
                }
                let mut body = params.body(&["tradeType"], &[], &[])?;
                body.insert("cancelOrderList".into(), orders);
                self.private_post(KucoinMarket::Spot, UTA_V2_CANCEL_BATCH, Value::Object(body))
                    .await
            }
        }
    }
}

mod wrappers {
    use crate::exchanges::kucoin::KucoinClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; KucoinClient;
     public [

     ];
     private [
    place_spot_batch_orders_sync(orders => "orders"),
    place_futures_batch_orders(orders => "orders"),
    cancel_futures_batch_orders(),
    set_futures_batch_margin_mode(margin_mode => "marginMode", symbols => "symbols"),
    batch_cancel_uta_orders(trade_type => "tradeType", cancel_order_list => "cancelOrderList"),
    place_spot_batch_limit_orders(orders => "orders"),
    place_spot_batch_market_orders(orders => "orders"),
    place_spot_batch_orders(orders => "orders")
     ];
    }
}
