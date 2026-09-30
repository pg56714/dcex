//! Fund and batch request implementations.

mod account_requests {
    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::kraken::account::*;
    use crate::exchanges::kraken::client::{KrakenAuth, KrakenClient};

    use crate::exchanges::kraken::params::{KrakenParams, push_optional};
    impl KrakenClient {
        pub(in crate::exchanges::kraken) async fn dispatch_wallet_transfer_to_futures(
            &self,
            _method_name: &str,
            params: &KrakenParams,
        ) -> Result<ValidatedResponse> {
            {
                params.required("asset")?;
                params.required("amount")?;
                params.required("to")?;
                if params.get("from").or_else(|| params.get("from_")).is_none() {
                    return Err(crate::DcexError::InvalidInput(
                        "missing required parameter: from".to_string(),
                    ));
                }
                let mut query = params.only(&["asset", "to", "amount"]);
                push_optional(
                    &mut query,
                    "from",
                    params.get("from").or_else(|| params.get("from_")),
                );
                self.private_post(KrakenAuth::Spot, SPOT_WALLET_TRANSFER, query)
                    .await
            }
        }
        pub(in crate::exchanges::kraken) async fn dispatch_futures_wallet_transfer(
            &self,
            _method_name: &str,
            params: &KrakenParams,
        ) -> Result<ValidatedResponse> {
            {
                for key in ["amount", "fromAccount", "toAccount", "unit"] {
                    params.required(key)?;
                }
                let mut query = params.only(&["amount", "fromAccount", "toAccount"]);
                push_lowercase(&mut query, "unit", params.get("unit"));
                self.private_post(KrakenAuth::Futures, FUTURES_TRANSFER, query)
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
    futures_wallet_transfer(amount => "amount", from_account => "fromAccount", to_account => "toAccount", unit => "unit"),
    wallet_transfer_to_futures(asset => "asset", amount => "amount")
     ];
    }
}

impl super::client::KrakenClient {
    pub(in crate::exchanges::kraken) async fn transfers_table_request(
        &self,
        name: &str,
        params: &super::params::KrakenParams,
        public: bool,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        self.table_request_transport(name, params, public).await
    }
}

impl super::client::KrakenClient {
    pub(in crate::exchanges::kraken) async fn transfers_field_schema_request(
        &self,
        name: &str,
        params: &super::params::KrakenParams,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        self.field_schema_request_transport(name, params).await
    }
}
