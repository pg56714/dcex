//! Fund and batch request implementations.

mod dispatch_from_account {
    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::okx::account::*;
    use crate::exchanges::okx::client::OkxClient;

    use crate::exchanges::okx::params::{OkxParams, push_optional_owned};

    impl OkxClient {
        pub(in crate::exchanges::okx) async fn moved_account_get_max_withdrawal(
            &self,
            _method_name: &str,
            params: &OkxParams,
        ) -> Result<ValidatedResponse> {
            {
                let mut query = Vec::new();
                push_optional_owned(&mut query, "ccy", params.csv("ccy")?);
                self.get_request(ACCOUNT_MAX_WITHDRAWAL, query).await
            }
        }
    }
}

mod dispatch_from_asset {
    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::okx::asset::*;
    use crate::exchanges::okx::client::OkxClient;

    use crate::exchanges::okx::params::{OkxParams, validate_deposit_withdraw_status};

    impl OkxClient {
        pub(in crate::exchanges::okx) async fn moved_asset_get_deposit_withdraw_status(
            &self,
            _method_name: &str,
            params: &OkxParams,
        ) -> Result<ValidatedResponse> {
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

mod wrappers_from_wrappers {
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
