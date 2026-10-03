//! Fund movement and batch request implementations.

mod trade_requests {
    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::bitget::client::BitgetClient;
    use crate::exchanges::bitget::endpoints::*;
    use crate::exchanges::bitget::params::BitgetParams;

    impl BitgetClient {
        pub(in crate::exchanges::bitget) async fn dispatch_place_uta_batch_orders(
            &self,
            _method_name: &str,
            params: &BitgetParams,
        ) -> Result<ValidatedResponse> {
            {
                self.post_private(
                    UTA_BATCH_PLACE_ORDER,
                    self.normalize_batch_symbols(params.json_required("orderList")?)?,
                )
                .await
            }
        }
        pub(in crate::exchanges::bitget) async fn dispatch_cancel_uta_batch_orders(
            &self,
            _method_name: &str,
            params: &BitgetParams,
        ) -> Result<ValidatedResponse> {
            {
                self.post_private(
                    UTA_BATCH_CANCEL_ORDERS,
                    self.normalize_batch_symbols(params.json_required("orderList")?)?,
                )
                .await
            }
        }
    }
}

mod controls {
    // Batch trading bodies verified against official request examples.
    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::bitget::{client::BitgetClient, params::BitgetParams};
    use serde_json::Value;
    use std::collections::HashSet;

    impl BitgetClient {
        pub(in crate::exchanges::bitget) async fn batch_controls_request(
            &self,
            name: &str,
            params: &BitgetParams,
        ) -> Result<Option<ValidatedResponse>> {
            if name != "modify_uta_batch_orders" {
                return Ok(None);
            }
            params.ensure_allowed(&["orders"], false)?;
            let mut value = params.json_required("orders")?;
            let items = value
                .as_array_mut()
                .ok_or_else(|| invalid("batch must be an array"))?;
            if items.is_empty() || items.len() > 20 {
                return Err(invalid("batch size exceeds the documented bounds"));
            }
            let mut category = None;
            let mut seen = HashSet::new();
            for value in items {
                let object = value
                    .as_object_mut()
                    .ok_or_else(|| invalid("batch entries must be objects"))?;
                if let Some(product) = object.remove("product_symbol") {
                    if object.contains_key("symbol") {
                        return Err(invalid("provide either symbol or product_symbol"));
                    }
                    object.insert(
                        "symbol".into(),
                        Value::String(
                            self.exchange_symbol_category(
                                product
                                    .as_str()
                                    .ok_or_else(|| invalid("product_symbol must be text"))?,
                                object.get("category").and_then(Value::as_str),
                            )?,
                        ),
                    );
                } else if let Some(symbol) = object
                    .get("symbol")
                    .and_then(Value::as_str)
                    .map(str::to_string)
                {
                    object.insert(
                        "symbol".into(),
                        Value::String(self.exchange_symbol_category(
                            &symbol,
                            object.get("category").and_then(Value::as_str),
                        )?),
                    );
                }
                let mut pairs = Vec::new();
                for (key, value) in object.iter() {
                    let text = if key == "requestId" {
                        let id = value
                            .as_u64()
                            .filter(|id| *id <= 999_999_999_999_999_999)
                            .ok_or_else(|| {
                                invalid("requestId must be a number of at most 18 digits")
                            })?;
                        id.to_string()
                    } else {
                        value
                            .as_str()
                            .filter(|v| !v.trim().is_empty())
                            .ok_or_else(|| invalid("order fields must be nonempty strings"))?
                            .to_string()
                    };
                    pairs.push((key.clone(), text));
                }
                let entry = BitgetParams::from_pairs(pairs);
                entry.ensure_allowed(
                    &[
                        "symbol",
                        "category",
                        "orderId",
                        "clientOid",
                        "requestId",
                        "qty",
                        "price",
                        "autoCancel",
                        "pxAmendType",
                    ],
                    false,
                )?;
                let symbol = required(&entry, "symbol")?;
                let this_category = required(&entry, "category")?;
                if ![
                    "SPOT",
                    "MARGIN",
                    "USDT-FUTURES",
                    "COIN-FUTURES",
                    "USDC-FUTURES",
                ]
                .contains(&this_category)
                {
                    return Err(invalid("unsupported category"));
                }
                if category
                    .as_deref()
                    .is_some_and(|expected| expected != this_category)
                {
                    return Err(invalid("all orders must use the same category"));
                }
                category = Some(this_category.to_string());
                let id = identifier(&entry)?;
                if !seen.insert((symbol.to_string(), id)) {
                    return Err(invalid("an order may appear only once per batch"));
                }
                if entry.get("qty").is_none() && entry.get("price").is_none() {
                    return Err(invalid("qty or price is required for amendment"));
                }
                if let Some(id) = entry.get("clientOid")
                    && (id.len() > 32
                        || !id.chars().all(|c| {
                            c.is_ascii_alphanumeric() || matches!(c, '.' | ':' | '/' | '_' | '-')
                        }))
                {
                    return Err(invalid("invalid clientOid"));
                }
                crate::exchanges::bitget::trading_controls::validate("modify_uta_order", &entry)?;
            }
            Ok(Some(
                self.post_private("/api/v3/trade/batch-modify-order", value)
                    .await?,
            ))
        }
    }

    use crate::exchanges::bitget::params::schema_invalid as invalid;
    use crate::exchanges::bitget::params::schema_required as required;
    fn identifier(params: &BitgetParams) -> Result<(bool, String)> {
        if let Some(value) = params.get("orderId") {
            return Ok((true, value.to_string()));
        }
        Ok((false, required(params, "clientOid")?.to_string()))
    }
}

mod wrappers {
    use crate::exchanges::bitget::BitgetClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; BitgetClient;
     public [

     ];
     private [
    modify_uta_batch_orders(orders => "orders"),
    cancel_uta_batch_orders(order_list => "orderList"),
    place_uta_batch_orders(order_list => "orderList")
     ];
    }
}
