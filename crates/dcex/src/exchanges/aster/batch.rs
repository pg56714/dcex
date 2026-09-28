//! Fund movement and batch request implementations.

mod trade_operations {

    use crate::exchanges::aster::client::AsterClient;

    use crate::exchanges::aster::params::AsterParams;
    use crate::exchanges::aster::trade::*;

    use crate::{DcexError, Result};
    use serde_json::Value;
    impl AsterClient {
        pub(in crate::exchanges::aster) fn resolve_batch_orders(
            &self,
            params: &AsterParams,
        ) -> Result<String> {
            let mut value = params.json_required("batchOrders")?;
            let Value::Array(orders) = &mut value else {
                return Err(DcexError::InvalidInput(
                    "Aster batchOrders must be a JSON array.".to_string(),
                ));
            };
            if orders.is_empty() || orders.len() > 5 {
                return Err(DcexError::InvalidInput(
                    "Aster batchOrders must contain between 1 and 5 orders.".to_string(),
                ));
            }
            for order in orders {
                self.resolve_order_object(order)?;
                let Value::Object(order) = order else {
                    unreachable!("resolve_order_object validated object")
                };
                let order = AsterParams::from_json_object(order)?;
                order.ensure_allowed(BATCH_ORDER_KEYS, &[])?;
                validate_symbol_alias(&order, true)?;
                validate_futures_order(&order, true)?;
            }
            Ok(value.to_string())
        }

        pub(in crate::exchanges::aster) fn resolve_batch_amendments(
            &self,
            params: &AsterParams,
        ) -> Result<String> {
            let mut value = params.json_required("batchOrders")?;
            let Value::Array(orders) = &mut value else {
                return Err(DcexError::InvalidInput(
                    "Aster batchOrders must be a JSON array".into(),
                ));
            };
            if orders.is_empty() || orders.len() > 5 {
                return Err(DcexError::InvalidInput(
                    "Aster batch amendments must contain between 1 and 5 orders".into(),
                ));
            }
            for order in orders {
                self.resolve_order_object(order)?;
                let Value::Object(order) = order else {
                    unreachable!("resolve_order_object validated object")
                };
                let order = AsterParams::from_json_object(order)?;
                order.ensure_allowed(
                    &[
                        "symbol",
                        "orderId",
                        "origClientOrderId",
                        "side",
                        "quantity",
                        "price",
                    ],
                    &[],
                )?;
                order.required("symbol")?;
                ensure_order_lookup(&order)?;
                order.u64("orderId")?;
                order.optional_one_of("side", &["BUY", "SELL"])?;
                order.required_positive_decimal("quantity")?;
                order.required_positive_decimal("price")?;
            }
            Ok(value.to_string())
        }
    }
}

mod wrappers {
    use crate::exchanges::aster::AsterClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; AsterClient;
     public [

     ];
     private [
    guarded_cancel_futures_batch_orders(product_symbol => "product_symbol", nonce => "nonce"),
    place_futures_batch_orders(batch_orders => "batchOrders"),
    modify_futures_batch_orders(batch_orders => "batchOrders"),
    cancel_futures_batch_orders(product_symbol => "product_symbol")
     ];
    }
}
