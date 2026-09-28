//! Withdrawals requests.

mod wrappers {
    use crate::exchanges::ondo::OndoClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; OndoClient;
     public [

     ];
     private [

            /// API withdrawals and external transfers have no second confirmation; they execute on submit.
    create_withdrawal(customer_withdrawal_id => "customer_withdrawal_id", symbol => "symbol", network => "network", amount => "amount", address => "address"),
    sandbox_withdrawal(customer_withdrawal_id => "customer_withdrawal_id", symbol => "symbol", amount => "amount", from_account => "from"),
    get_withdrawal_limits(),
    get_withdrawal_status()
     ];
    }
}

mod account_requests {
    use crate::exchanges::ondo::{
        account::optional_string_field,
        client::OndoClient,
        endpoints::{WITHDRAWAL_STATUS, WITHDRAWALS},
        params::{OndoParams, path_with_id},
    };
    use crate::{DcexError, Result, exchange::ValidatedResponse};
    impl OndoClient {
        pub(in crate::exchanges::ondo) async fn get_withdrawal_status_request(
            &self,
            params: &OndoParams,
        ) -> Result<ValidatedResponse> {
            let body = params.body(
                &["withdrawal_id", "customer_withdrawal_id"],
                &[],
                &[],
                &[],
                &[],
            )?;
            let count = ["withdrawal_id", "customer_withdrawal_id"]
                .iter()
                .filter(|key| body.get(**key).is_some())
                .count();
            if count != 1 {
                return Err(DcexError::InvalidInput(
                        "Ondo withdrawal status requires exactly one of withdrawal_id or customer_withdrawal_id"
                            .to_string(),
                    ));
            }
            for key in ["withdrawal_id", "customer_withdrawal_id"] {
                optional_string_field(&body, key)?;
            }
            self.private_post(WITHDRAWAL_STATUS, body).await
        }
        pub(in crate::exchanges::ondo) async fn get_withdrawal_request(
            &self,
            params: &OndoParams,
        ) -> Result<ValidatedResponse> {
            params.ensure_allowed(&["withdrawalID"])?;
            let id = params.path_segment("withdrawalID")?;
            self.private_get(&path_with_id(WITHDRAWALS, id), Vec::new())
                .await
        }
    }
}
