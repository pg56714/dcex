//! Fund and batch request implementations.

mod asset_requests {
    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::bybit::client::BybitClient;
    use crate::exchanges::bybit::funding::*;

    use crate::exchanges::bybit::params::BybitParams;

    impl BybitClient {
        pub(in crate::exchanges::bybit) async fn dispatch_get_withdrawable_amount(
            &self,
            _method_name: &str,
            params: &BybitParams,
        ) -> Result<ValidatedResponse> {
            {
                self.get_request(
                    GET_WITHDRAWABLE_AMOUNT,
                    vec![("coin".to_string(), params.required("coin")?.to_string())],
                )
                .await
            }
        }
    }
}

mod wrappers {
    use crate::exchanges::bybit::BybitClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; BybitClient;
     public [

     ];
     private [
    get_withdrawable_amount(coin => "coin")
     ];
    }
}
