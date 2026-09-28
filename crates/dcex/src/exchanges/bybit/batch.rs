//! Fund movement and batch request implementations.

mod from_trade_bybitclient {
    use crate::Result;

    use crate::exchange::ValidatedResponse;
    use crate::exchanges::bybit::client::BybitClient;

    use crate::exchanges::bybit::params::BybitParams;

    use serde_json::{Map, Value};
    impl BybitClient {
        pub(in crate::exchanges::bybit) async fn batch_request(
            &self,
            path: &str,
            params: &BybitParams,
        ) -> Result<ValidatedResponse> {
            let mut body = Map::new();
            body.insert(
                "category".to_string(),
                Value::String(params.get("category").unwrap_or("linear").to_string()),
            );
            body.insert("request".to_string(), params.json_required("request")?);
            self.post_request(path, body).await
        }
    }
}

mod dispatch_from_trade {
    use crate::Result;

    use crate::exchange::ValidatedResponse;
    use crate::exchanges::bybit::client::BybitClient;
    use crate::exchanges::bybit::endpoints::*;
    use crate::exchanges::bybit::params::BybitParams;

    impl BybitClient {
        pub(in crate::exchanges::bybit) async fn moved_trade_cancel_batch_orders(
            &self,
            _method_name: &str,
            params: &BybitParams,
        ) -> Result<ValidatedResponse> {
            self.batch_request(CANCEL_BATCH_ORDERS, params).await
        }
        pub(in crate::exchanges::bybit) async fn moved_trade_place_batch_order(
            &self,
            _method_name: &str,
            params: &BybitParams,
        ) -> Result<ValidatedResponse> {
            self.batch_request(BATCH_PLACE_ORDER, params).await
        }
        pub(in crate::exchanges::bybit) async fn moved_trade_amend_batch_order(
            &self,
            _method_name: &str,
            params: &BybitParams,
        ) -> Result<ValidatedResponse> {
            self.batch_request(BATCH_AMEND_ORDER, params).await
        }
    }
}

mod wrappers_from_wrappers {
    use crate::exchanges::bybit::BybitClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; BybitClient;
     public [

     ];
     private [
    batch_set_collateral_coins(request => "request"),
    amend_batch_order(request => "request"),
    cancel_batch_orders(request => "request"),
    place_batch_order(request => "request")
     ];
    }
}
