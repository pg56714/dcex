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

mod fund_dispatch {

    use crate::exchange::ValidatedResponse;
    use crate::{DcexError, Result};

    use super::super::account::{
        require_enum_field, require_string_fields, validate_account_wallet_key,
    };
    use super::super::client::OndoClient;
    use super::super::params::OndoParams;

    impl OndoClient {
        pub(in crate::exchanges::ondo) async fn dispatch_create_withdrawal(
            &self,
            method_name: &str,
            params: &OndoParams,
        ) -> Result<ValidatedResponse> {
            let sandbox = method_name == "sandbox_withdrawal";
            let required: &[&str] = if sandbox {
                &["customer_withdrawal_id", "symbol", "amount", "from"]
            } else {
                &[
                    "customer_withdrawal_id",
                    "symbol",
                    "network",
                    "amount",
                    "address",
                ]
            };
            let allowed: &[&str] = if sandbox {
                required
            } else {
                &[
                    "customer_withdrawal_id",
                    "symbol",
                    "network",
                    "amount",
                    "address",
                    "from",
                ]
            };
            let body = params.body(allowed, required, &[], &[], &["from"])?;
            require_string_fields(&body, &["customer_withdrawal_id", "symbol", "amount"])?;
            if !body["amount"]
                .as_str()
                .is_some_and(crate::common::is_positive_plain_decimal)
            {
                return Err(DcexError::InvalidInput(
                    "Ondo withdrawal amount must be a positive plain decimal string".into(),
                ));
            }
            if !sandbox {
                require_string_fields(&body, &["address"])?;
                require_enum_field(&body, "network", &["avalanche", "ethereum", "solana"])?;
            }
            if body.get("from").is_some() {
                validate_account_wallet_key(&body, "from")?;
            }
            self.private_post(
                if sandbox {
                    "/v1/sandbox_withdrawal"
                } else {
                    "/v1/withdraw"
                },
                body,
            )
            .await
        }
    }
}
