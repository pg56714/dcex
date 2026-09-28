//! Fund and batch request implementations.

mod account_requests {
    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::kraken::account::*;
    use crate::exchanges::kraken::client::{KrakenAuth, KrakenClient};

    use crate::exchanges::kraken::params::KrakenParams;
    impl KrakenClient {
        pub(in crate::exchanges::kraken) async fn dispatch_withdraw_futures_to_spot_wallet(
            &self,
            _method_name: &str,
            params: &KrakenParams,
        ) -> Result<ValidatedResponse> {
            {
                params.required("amount")?;
                params.required("currency")?;
                let mut query = params.only(&["amount", "sourceWallet"]);
                push_lowercase(&mut query, "currency", params.get("currency"));
                self.private_post(KrakenAuth::Futures, FUTURES_WITHDRAWAL, query)
                    .await
            }
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

            /// API withdrawals and external transfers have no second confirmation; they execute on submit.
    withdraw_futures_to_spot_wallet(amount => "amount", currency => "currency")
     ];
    }
}
