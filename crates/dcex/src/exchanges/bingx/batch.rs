//! Fund and batch request implementations.

mod trade_requests {
    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::bingx::client::BingxClient;
    use crate::exchanges::bingx::endpoints::*;
    use crate::exchanges::bingx::params::{
        BingxParams, batch_orders_query, comma_list, push_optional, python_list_string,
        require_one_identifier, validate_bool, validate_enum, validate_u64_range,
    };
    use crate::exchanges::bingx::trade::*;
    impl BingxClient {
        pub(in crate::exchanges::bingx) async fn dispatch_place_spot_batch_order(
            &self,
            _method_name: &str,
            params: &BingxParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&["data", "sync", "recvWindow"])?;
                validate_bool(params, "sync")?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = vec![(
                    "data".to_string(),
                    batch_orders_query(params.required("data")?)?,
                )];
                push_optional(&mut query, "sync", params.get("sync"));
                push_optional(&mut query, "recvWindow", params.get("recvWindow"));
                self.private_post(SPOT_PLACE_BATCH_ORDER, query).await
            }
        }
        pub(in crate::exchanges::bingx) async fn dispatch_cancel_spot_batch_orders(
            &self,
            _method_name: &str,
            params: &BingxParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "orderIds",
                    "clientOrderIDs",
                    "process",
                    "recvWindow",
                ])?;
                params.required("orderIds")?;
                validate_enum(params, "process", &["0", "1"])?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params)?;
                query.push((
                    "orderIds".to_string(),
                    comma_list(params.required("orderIds")?),
                ));
                push_optional(&mut query, "process", params.get("process"));
                if let Some(value) = params.get("clientOrderIDs") {
                    query.push(("clientOrderIDs".to_string(), comma_list(value)));
                }
                push_optional(&mut query, "recvWindow", params.get("recvWindow"));
                self.private_post(SPOT_CANCEL_BATCH_ORDERS, query).await
            }
        }
        pub(in crate::exchanges::bingx) async fn dispatch_place_swap_batch_order(
            &self,
            _method_name: &str,
            params: &BingxParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&["batchOrders", "recvWindow"])?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = vec![(
                    "batchOrders".to_string(),
                    batch_orders_query(params.required("batchOrders")?)?,
                )];
                push_optional(&mut query, "recvWindow", params.get("recvWindow"));
                self.private_post(SWAP_PLACE_BATCH_ORDER, query).await
            }
        }
        pub(in crate::exchanges::bingx) async fn dispatch_cancel_swap_batch_order(
            &self,
            _method_name: &str,
            params: &BingxParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "orderIdList",
                    "clientOrderIdList",
                    "recvWindow",
                ])?;
                require_one_identifier(params, &["orderIdList", "clientOrderIdList"])?;
                validate_list_size(params, "orderIdList", 10)?;
                validate_list_size(params, "clientOrderIdList", 10)?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let mut query = Vec::new();
                self.push_required_symbol(&mut query, params)?;
                if let Some(value) = params.get("orderIdList") {
                    query.push(("orderIdList".to_string(), python_list_string(value)));
                }
                if let Some(value) = params.get("clientOrderIdList") {
                    let ids: Vec<String> = serde_json::from_str(value).map_err(|_| {
                        crate::exchanges::bingx::params::invalid(
                            "clientOrderIdList must be a JSON array of strings",
                        )
                    })?;
                    query.push((
                        "clientOrderIdList".to_string(),
                        serde_json::to_string(&ids).expect("string array"),
                    ));
                }
                push_optional(&mut query, "recvWindow", params.get("recvWindow"));
                self.private_delete(SWAP_CANCEL_BATCH_ORDER, query).await
            }
        }
        pub(in crate::exchanges::bingx) async fn dispatch_replace_swap_batch_orders(
            &self,
            _method_name: &str,
            params: &BingxParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&["batchOrders", "recvWindow"])?;
                validate_u64_range(params, "recvWindow", 1, 5000)?;
                let orders: serde_json::Value =
                    serde_json::from_str(params.required("batchOrders")?).map_err(|_| {
                        crate::DcexError::InvalidInput("invalid batchOrders JSON".into())
                    })?;
                let orders = orders.as_array().filter(|v| !v.is_empty()).ok_or_else(|| {
                    crate::DcexError::InvalidInput("batchOrders requires a nonempty array".into())
                })?;
                let mut normalized = Vec::new();
                for order in orders {
                    let object = order.as_object().ok_or_else(|| {
                        crate::DcexError::InvalidInput("batch order must be an object".into())
                    })?;
                    if object.contains_key("recvWindow") || object.contains_key("timestamp") {
                        return Err(crate::DcexError::InvalidInput(
                            "batch timing belongs on the outer request".into(),
                        ));
                    }
                    let pairs = object
                        .iter()
                        .map(|(k, v)| {
                            (
                                if k == "type" {
                                    "type".into()
                                } else {
                                    k.clone()
                                },
                                v.as_str()
                                    .map(str::to_string)
                                    .unwrap_or_else(|| v.to_string()),
                            )
                        })
                        .collect();
                    let query = self.swap_replacement_query(&BingxParams::from_pairs(pairs))?;
                    let mut output = serde_json::Map::new();
                    for (k, v) in query {
                        let value = if [
                            "quantity",
                            "quoteOrderQty",
                            "price",
                            "stopPrice",
                            "priceRate",
                            "activationPrice",
                        ]
                        .contains(&k.as_str())
                        {
                            serde_json::from_str::<serde_json::Number>(&v)
                                .map(serde_json::Value::Number)
                                .map_err(|_| {
                                    crate::DcexError::InvalidInput(
                                        "batch prices and quantities must be JSON numbers".into(),
                                    )
                                })?
                        } else {
                            serde_json::Value::String(v)
                        };
                        output.insert(k, value);
                    }
                    normalized.push(serde_json::Value::Object(output));
                }
                let mut query = vec![(
                    "batchOrders".into(),
                    serde_json::to_string(&normalized)
                        .map_err(|e| crate::DcexError::Decode(e.to_string()))?,
                )];
                push_optional(&mut query, "recvWindow", params.get("recvWindow"));
                self.private_post("/openApi/swap/v1/trade/batchCancelReplace", query)
                    .await
            }
        }
    }
}

mod wrappers {
    use crate::exchanges::bingx::BingxClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; BingxClient;
     public [

     ];
     private [
    replace_swap_batch_orders(orders => "batchOrders"),
    cancel_spot_batch_orders(product_symbol => "product_symbol", order_ids => "orderIds"),
    cancel_swap_batch_order(product_symbol => "product_symbol"),
    place_spot_batch_order(data => "data"),
    place_swap_batch_order(batch_orders => "batchOrders")
     ];
    }
}
