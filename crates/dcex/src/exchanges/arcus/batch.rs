//! Fund movement and batch request implementations.

mod trade_operations {

    use crate::exchanges::arcus::client::ArcusClient;
    use crate::exchanges::arcus::params::required;
    use crate::exchanges::arcus::signing::timestamp_ns;

    use crate::http::{HttpMethod, HttpRequest};
    use crate::{DcexError, Result};

    use serde_json::{Value, json};
    use std::collections::BTreeMap;
    impl ArcusClient {
        pub(in crate::exchanges::arcus) async fn batch_order_request(
            &self,
            method_name: &str,
            params: Vec<(String, String)>,
        ) -> Result<HttpRequest> {
            let address = self.address.as_deref().ok_or_else(|| {
                DcexError::InvalidInput("Arcus wallet address is required for trading".into())
            })?;
            let values: BTreeMap<_, _> = params.into_iter().collect();
            let (field, single_method, path) = match method_name {
                "batch_place_orders" => ("orders", "place_order", "/v1/batchPlaceOrders"),
                "batch_cancel_orders" => ("cancels", "cancel_order", "/v1/batchCancelOrders"),
                "batch_modify_orders" => ("modifies", "modify_order", "/v1/batchModifyOrders"),
                _ => unreachable!("batch dispatch is restricted"),
            };
            if values.keys().any(|key| {
                key != field && !(method_name == "batch_place_orders" && key == "grouping")
            }) {
                return Err(DcexError::InvalidInput(format!(
                    "unknown Arcus {method_name} parameter"
                )));
            }
            let raw: Value = serde_json::from_str(required(&values, field)?).map_err(|error| {
                DcexError::InvalidInput(format!("invalid Arcus {field} JSON: {error}"))
            })?;
            let items = raw.as_array().ok_or_else(|| {
                DcexError::InvalidInput(format!("Arcus {field} must be a JSON array"))
            })?;
            if items.is_empty() || items.len() > 100 {
                return Err(DcexError::InvalidInput(format!(
                    "Arcus {field} must contain between 1 and 100 items"
                )));
            }
            let grouping = values.get("grouping").map(String::as_str);
            if let Some(grouping) = grouping {
                if !["partialTpsl", "positionTpsl", "entryTpsl"].contains(&grouping) {
                    return Err(DcexError::InvalidInput("unsupported Arcus grouping".into()));
                }
                let entry = usize::from(grouping == "entryTpsl");
                if !(1 + entry..=2 + entry).contains(&items.len()) {
                    return Err(DcexError::InvalidInput(
                        "Arcus grouping requires one or two TPSL legs and optional entry".into(),
                    ));
                }
                let mut kinds = std::collections::BTreeSet::new();
                for (index, item) in items.iter().enumerate() {
                    if entry == 1 && index == 0 {
                        if item.get("tpsl_type").is_some() {
                            return Err(DcexError::InvalidInput(
                                "Arcus entry must precede TPSL children".into(),
                            ));
                        }
                    } else {
                        let kind =
                            item.get("tpsl_type")
                                .and_then(Value::as_str)
                                .ok_or_else(|| {
                                    DcexError::InvalidInput(
                                        "Arcus TPSL leg requires tpsl_type".into(),
                                    )
                                })?;
                        if !kinds.insert(kind) {
                            return Err(DcexError::InvalidInput(
                                "Arcus TPSL legs must have distinct trigger types".into(),
                            ));
                        }
                    }
                }
            } else if items
                .iter()
                .any(|item| item.get("tpsl_type").is_some() || item.get("stop_price").is_some())
            {
                return Err(DcexError::InvalidInput(
                    "Arcus TPSL orders require grouping".into(),
                ));
            }
            let timestamp = timestamp_ns()?;
            let mut signed_items = Vec::with_capacity(items.len());
            let mut first_signature = None;
            for item in items {
                let object = item.as_object().ok_or_else(|| {
                    DcexError::InvalidInput(format!("Arcus {field} item must be an object"))
                })?;
                let mut order = BTreeMap::new();
                for (key, value) in object {
                    let scalar = match value {
                        Value::String(value) => value.clone(),
                        Value::Number(value) => value.to_string(),
                        Value::Bool(value) => value.to_string(),
                        _ => {
                            return Err(DcexError::InvalidInput(format!(
                                "Arcus {field} field {key} must be a scalar"
                            )));
                        }
                    };
                    order.insert(key.clone(), scalar);
                }
                let (_, mut body, signature) = self
                    .signed_order_payload(
                        single_method,
                        &order,
                        timestamp,
                        grouping == Some("positionTpsl"),
                    )
                    .await?;
                body["signature"] = json!(signature);
                if first_signature.is_none() {
                    first_signature = Some(signature);
                }
                signed_items.push(body);
            }
            let mut batch_body = serde_json::Map::new();
            batch_body.insert(field.to_string(), json!(signed_items));
            if let Some(grouping) = grouping {
                batch_body.insert("grouping".into(), json!(grouping));
            }
            let request = HttpRequest::new(HttpMethod::Post, &self.base_url, path)
                .query("address", address)
                .header("X-API-Key", self.api_key.clone().unwrap_or_default())
                .header("X-Timestamp", timestamp.to_string())
                .header("X-Signature", first_signature.expect("nonempty batch"))
                .json(Value::Object(batch_body));
            Ok(request)
        }
    }
}

mod wrappers {
    use crate::exchanges::arcus::ArcusClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; ArcusClient;
     public [

     ];
     private [
    batch_place_orders(orders => "orders"),
    batch_cancel_orders(cancels => "cancels"),
    batch_modify_orders(modifies => "modifies")
     ];
    }
}
