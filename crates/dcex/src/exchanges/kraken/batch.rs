//! Fund and batch request implementations.

mod trading_controls_requests {
    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::kraken::client::{KrakenAuth, KrakenClient};
    use crate::exchanges::kraken::params::KrakenParams;
    use crate::exchanges::kraken::trading_controls::*;
    use crate::http::HttpMethod;
    use serde_json::json;
    impl KrakenClient {
        pub(in crate::exchanges::kraken) async fn dispatch_manage_futures_batch_orders(
            &self,
            _name: &str,
            params: &KrakenParams,
        ) -> Result<ValidatedResponse> {
            Ok({
                params.ensure_allowed(&["orders", "processBefore"])?;
                let mut orders = array(params, "orders")?;
                if !(1..=500).contains(&orders.len()) {
                    return Err(invalid("batch requires 1..=500 instructions"));
                }
                for order in &mut orders {
                    let object = order
                        .as_object_mut()
                        .ok_or_else(|| invalid("batch instruction must be an object"))?;
                    if let Some(symbol) = object.remove("product_symbol") {
                        if object.contains_key("symbol") {
                            return Err(invalid("use symbol or product_symbol, exclusively"));
                        }
                        let symbol = self.exchange_symbol(
                            symbol
                                .as_str()
                                .ok_or_else(|| invalid("product_symbol must be a string"))?,
                            "PF_",
                        )?;
                        object.insert("symbol".into(), symbol.into());
                    }
                    validate_futures_instruction(order)?;
                }
                let mut payload = vec![("json".into(), json!({"batchOrder":orders}).to_string())];
                if let Some(before) = params.get("processBefore") {
                    if before.is_empty() {
                        return Err(invalid("processBefore cannot be empty"));
                    }
                    payload.push(("processBefore".into(), before.into()));
                }
                self.private_post(
                    KrakenAuth::Futures,
                    "/derivatives/api/v3/batchorder",
                    payload,
                )
                .await?
            })
        }
        pub(in crate::exchanges::kraken) async fn dispatch_place_spot_batch_orders(
            &self,
            _name: &str,
            params: &KrakenParams,
        ) -> Result<ValidatedResponse> {
            Ok({
                params.ensure_allowed(&[
                    "product_symbol",
                    "orders",
                    "validate",
                    "deadline",
                    "asset_class",
                ])?;
                let orders = array(params, "orders")?;
                if !(2..=15).contains(&orders.len()) {
                    return Err(invalid("batch must contain 2..=15 orders"));
                }
                for order in &orders {
                    validate_batch_order(order)?;
                }
                let mut body = json!({"pair":self.exchange_symbol(params.required("product_symbol")?,"")?,"orders":orders});
                if let Some(value) = parse_bool(params, "validate")? {
                    body["validate"] = value.into();
                }
                if let Some(value) = params.get("deadline") {
                    body["deadline"] = value.into();
                }
                let asset = params
                    .get("asset_class")
                    .map(str::to_string)
                    .or(self.spot_asset_class(params.required("product_symbol")?)?);
                if let Some(asset) = asset {
                    if asset != "tokenized_asset" {
                        return Err(invalid("unsupported asset_class"));
                    }
                    body["asset_class"] = asset.into();
                }
                self.request(
                    HttpMethod::Post,
                    KrakenAuth::Spot,
                    "/0/private/AddOrderBatch",
                    vec![],
                    Some(body.to_string().into_bytes()),
                    true,
                )
                .await?
            })
        }
        pub(in crate::exchanges::kraken) async fn dispatch_cancel_spot_batch_orders(
            &self,
            _name: &str,
            params: &KrakenParams,
        ) -> Result<ValidatedResponse> {
            Ok({
                params.ensure_allowed(&["orders", "cl_ord_ids"])?;
                let mut body = json!({});
                let mut count = 0;
                for key in ["orders", "cl_ord_ids"] {
                    if params.get(key).is_some() {
                        let values = array(params, key)?;
                        if values.is_empty() {
                            return Err(invalid("explicit cancellation lists must not be empty"));
                        }
                        for value in &values {
                            if value.as_str().is_none_or(|s| s.is_empty())
                                && !(key == "orders"
                                    && value.as_i64().is_some_and(|v| i32::try_from(v).is_ok()))
                            {
                                return Err(invalid(
                                    "orders require txid strings or int32 userrefs; cl_ord_ids require strings",
                                ));
                            }
                        }
                        count += values.len();
                        body[key] = values.into();
                    }
                }
                if !(1..=50).contains(&count) {
                    return Err(invalid("batch cancellation requires 1..=50 identifiers"));
                }
                self.request(
                    HttpMethod::Post,
                    KrakenAuth::Spot,
                    "/0/private/CancelOrderBatch",
                    vec![],
                    Some(body.to_string().into_bytes()),
                    true,
                )
                .await?
            })
        }
    }
}

mod wrappers {
    use crate::exchanges::kraken::KrakenClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; KrakenClient;
     public [

     ];
     private [
    manage_futures_batch_orders(orders => "orders"),
    place_spot_batch_orders(product_symbol => "product_symbol", orders => "orders"),
    cancel_spot_batch_orders()
     ];
    }
}
