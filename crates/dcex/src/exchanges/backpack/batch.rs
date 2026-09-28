//! Fund movement and batch request implementations.

mod from_trade_backpackclient {

    use crate::exchanges::backpack::client::BackpackClient;

    use crate::exchanges::backpack::params::BackpackParams;

    use crate::{DcexError, Result};
    use serde_json::Value;

    impl BackpackClient {
        pub(in crate::exchanges::backpack) fn batch_orders_body(
            &self,
            params: &BackpackParams,
        ) -> Result<Value> {
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
    }
}

mod wrappers_from_wrappers {
    use crate::exchanges::backpack::BackpackClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; BackpackClient;
     public [

     ];
     private [
    place_batch_orders(orders => "orders")
     ];
    }
}
