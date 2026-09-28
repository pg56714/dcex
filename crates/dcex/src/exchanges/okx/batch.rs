//! Fund and batch request implementations.

mod dispatch_from_trade {

    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::okx::client::OkxClient;
    use crate::exchanges::okx::endpoints::*;
    use crate::exchanges::okx::params::OkxParams;
    use crate::exchanges::okx::trade::*;

    impl OkxClient {
        pub(in crate::exchanges::okx) async fn moved_trade_place_batch_orders(
            &self,
            _method_name: &str,
            params: &OkxParams,
        ) -> Result<ValidatedResponse> {
            {
                let orders = params.json_required("orders")?;
                validate_batch_order_slippage(&orders)?;
                self.post_request(TRADE_BATCH_ORDERS, orders).await
            }
        }
        pub(in crate::exchanges::okx) async fn moved_trade_cancel_batch_orders(
            &self,
            _method_name: &str,
            params: &OkxParams,
        ) -> Result<ValidatedResponse> {
            {
                self.post_request(TRADE_CANCEL_BATCH_ORDERS, params.json_required("orders")?)
                    .await
            }
        }
    }
}

mod wrappers_from_wrappers {
    use crate::exchanges::okx::OkxClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; OkxClient;
     public [

     ];
     private [
    cancel_batch_orders(orders => "orders"),
    place_batch_orders(orders => "orders")
     ];
    }
}
