//! Fund and batch request implementations.

mod account_requests {
    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::okx::account::*;
    use crate::exchanges::okx::client::OkxClient;

    use crate::exchanges::okx::params::{OkxParams, push_optional_owned};

    impl OkxClient {
        pub(in crate::exchanges::okx) async fn dispatch_get_max_withdrawal(
            &self,
            _method_name: &str,
            params: &OkxParams,
        ) -> Result<ValidatedResponse> {
            params.ensure_allowed(&["ccy"])?;
            {
                let mut query = Vec::new();
                push_optional_owned(&mut query, "ccy", params.csv("ccy")?);
                self.get_request(ACCOUNT_MAX_WITHDRAWAL, query).await
            }
        }
    }
}

mod asset_requests {
    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::okx::client::OkxClient;
    use crate::exchanges::okx::funding::*;

    use crate::exchanges::okx::params::{OkxParams, validate_deposit_withdraw_status};

    impl OkxClient {
        pub(in crate::exchanges::okx) async fn dispatch_get_deposit_withdraw_status(
            &self,
            _method_name: &str,
            params: &OkxParams,
        ) -> Result<ValidatedResponse> {
            params.ensure_allowed(&["wdId", "txId", "ccy", "to", "chain"])?;
            {
                validate_deposit_withdraw_status(params)?;
                self.get_request(
                    ASSET_DEPOSIT_WITHDRAW_STATUS,
                    params.only(&["wdId", "txId", "ccy", "to", "chain"]),
                )
                .await
            }
        }
    }
}

mod wrappers {
    use crate::exchanges::okx::OkxClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; OkxClient;
     public [

     ];
     private [
    get_deposit_withdraw_status(),
    get_max_withdrawal()
     ];
    }
}

impl super::client::OkxClient {
    pub(in crate::exchanges::okx) async fn withdrawals_table_request(
        &self,
        name: &str,
        p: &super::params::OkxParams,
        public: bool,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        self.table_request_transport(name, p, public).await
    }
}
