//! Fund movement and batch request implementations.

mod from_trade_mexcclient {
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::mexc::client::MexcClient;
    use crate::exchanges::mexc::endpoints::*;
    use crate::exchanges::mexc::params::{MexcParams, validate_u64_range};
    use crate::exchanges::mexc::signing::json_value_string;
    use crate::exchanges::mexc::trade::*;
    use crate::http::HttpMethod;
    use crate::{DcexError, Result};
    use serde_json::Value;
    impl MexcClient {
        pub(in crate::exchanges::mexc) async fn place_spot_batch_orders_from_params(
            &self,
            params: &MexcParams,
        ) -> Result<ValidatedResponse> {
            params.ensure_allowed(&["batchOrders", "recvWindow"])?;
            validate_u64_range(params, "recvWindow", 1, 60_000)?;
            let orders = params.json_required("batchOrders")?;
            let Value::Array(mut orders) = orders else {
                return Err(DcexError::InvalidInput(
                    "batchOrders must be a JSON array.".to_string(),
                ));
            };
            if orders.is_empty() || orders.len() > 20 {
                return Err(DcexError::InvalidInput(
                    "MEXC Spot batch orders require 1 to 20 orders".to_string(),
                ));
            }
            let mut batch_symbol: Option<String> = None;
            for (index, order) in orders.iter_mut().enumerate() {
                let Value::Object(order) = order else {
                    return Err(DcexError::InvalidInput(format!(
                        "MEXC Spot batch order at index {index} must be a JSON object"
                    )));
                };
                const ALLOWED_KEYS: &[&str] = &[
                    "product_symbol",
                    "symbol",
                    "side",
                    "type",
                    "quantity",
                    "quoteOrderQty",
                    "price",
                    "newClientOrderId",
                    "stpMode",
                ];
                if let Some(key) = order
                    .keys()
                    .find(|key| !ALLOWED_KEYS.contains(&key.as_str()))
                {
                    return Err(DcexError::InvalidInput(format!(
                        "unsupported MEXC Spot batch order parameter: {key}"
                    )));
                }
                if order.contains_key("product_symbol") && order.contains_key("symbol") {
                    return Err(DcexError::InvalidInput(format!(
                        "MEXC Spot batch order at index {index} cannot include both product_symbol and symbol"
                    )));
                }
                if let Some(product_symbol) = order.remove("product_symbol") {
                    let symbol = self.exchange_symbol(&json_value_string(&product_symbol), "")?;
                    order.insert("symbol".to_string(), Value::String(symbol));
                }
                let symbol = required_batch_string(order, index, "symbol")?;
                if batch_symbol
                    .as_ref()
                    .is_some_and(|expected| expected != symbol)
                {
                    return Err(DcexError::InvalidInput(
                        "MEXC Spot batch orders must use the same symbol".to_string(),
                    ));
                }
                batch_symbol.get_or_insert_with(|| symbol.to_string());

                let side = required_batch_string(order, index, "side")?;
                if !matches!(side, "BUY" | "SELL") {
                    return Err(DcexError::InvalidInput(format!(
                        "unsupported MEXC Spot batch order side: {side}"
                    )));
                }
                let order_type = required_batch_string(order, index, "type")?;
                if !matches!(
                    order_type,
                    "LIMIT" | "MARKET" | "LIMIT_MAKER" | "IMMEDIATE_OR_CANCEL" | "FILL_OR_KILL"
                ) {
                    return Err(DcexError::InvalidInput(format!(
                        "unsupported MEXC Spot batch order type: {order_type}"
                    )));
                }
                match order_type {
                    "MARKET" => {
                        if !order.contains_key("quantity") && !order.contains_key("quoteOrderQty") {
                            return Err(DcexError::InvalidInput(format!(
                                "MEXC Spot MARKET batch order at index {index} requires quantity or quoteOrderQty"
                            )));
                        }
                    }
                    _ => {
                        for key in ["quantity", "price"] {
                            if !order.contains_key(key) {
                                return Err(DcexError::InvalidInput(format!(
                                    "MEXC Spot batch order at index {index} requires {key}"
                                )));
                            }
                        }
                    }
                }
                if let Some(stp_mode) = order.get("stpMode").map(json_value_string)
                    && !matches!(
                        stp_mode.as_str(),
                        "CANCEL_MAKER" | "CANCEL_TAKER" | "CANCEL_BOTH"
                    )
                {
                    return Err(DcexError::InvalidInput(format!(
                        "unsupported MEXC Spot batch order stpMode: {stp_mode}"
                    )));
                }
            }
            let mut query = vec![(
                "batchOrders".to_string(),
                serde_json::to_string(&orders)
                    .map_err(|error| DcexError::Decode(error.to_string()))?,
            )];
            query.extend(params.only(&["recvWindow"]));
            self.spot_private(HttpMethod::Post, SPOT_BATCH_ORDERS, query)
                .await
        }
    }
}

mod dispatch_from_trade {
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::mexc::client::MexcClient;

    use crate::exchanges::mexc::params::MexcParams;

    use crate::{DcexError, Result};
    use serde_json::Value;
    impl MexcClient {
        pub(in crate::exchanges::mexc) async fn moved_trade_cancel_contract_batch_orders_by_external_id(
            &self,
            method_name: &str,
            params: &MexcParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&["orders"])?;
                let mut orders = params.json_required("orders")?;
                let items = orders
                    .as_array_mut()
                    .filter(|v| !v.is_empty())
                    .ok_or_else(|| {
                        DcexError::InvalidInput("orders requires a nonempty JSON array".into())
                    })?;
                let mut seen = std::collections::HashSet::new();
                for item in items {
                    let object = item
                        .as_object_mut()
                        .ok_or_else(|| DcexError::InvalidInput("order must be an object".into()))?;
                    if object.keys().any(|key| {
                        !["product_symbol", "symbol", "externalOid"].contains(&key.as_str())
                    }) || object.contains_key("symbol") && object.contains_key("product_symbol")
                    {
                        return Err(DcexError::InvalidInput(
                            "invalid external order fields".into(),
                        ));
                    }
                    let raw = object
                        .remove("product_symbol")
                        .or_else(|| object.remove("symbol"))
                        .ok_or_else(|| DcexError::InvalidInput("symbol is required".into()))?;
                    let symbol =
                        raw.as_str()
                            .filter(|s| !s.trim().is_empty())
                            .ok_or_else(|| {
                                DcexError::InvalidInput("symbol must be a nonempty string".into())
                            })?;
                    let symbol = self.exchange_symbol(symbol, "_")?;
                    let id = object
                        .get("externalOid")
                        .and_then(Value::as_str)
                        .filter(|s| !s.trim().is_empty())
                        .ok_or_else(|| {
                            DcexError::InvalidInput("externalOid must be a nonempty string".into())
                        })?;
                    if !seen.insert((symbol.clone(), id.to_string())) {
                        return Err(DcexError::InvalidInput(
                            "duplicate external order identifier".into(),
                        ));
                    }
                    object.insert("symbol".into(), symbol.into());
                }
                self.contract_post_json(
                    if method_name.starts_with("cancel_") {
                        "/api/v1/private/order/batch_cancel_with_external"
                    } else {
                        "/api/v1/private/order/batch_query_with_external"
                    },
                    orders,
                )
                .await
            }
        }
        pub(in crate::exchanges::mexc) async fn moved_trade_place_spot_batch_orders(
            &self,
            _method_name: &str,
            params: &MexcParams,
        ) -> Result<ValidatedResponse> {
            self.place_spot_batch_orders_from_params(params).await
        }
    }
}

mod wrappers_from_wrappers {
    use crate::exchanges::mexc::MexcClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; MexcClient;
     public [

     ];
     private [
    place_spot_batch_orders(batch_orders => "batchOrders")
     ];
    }
}
