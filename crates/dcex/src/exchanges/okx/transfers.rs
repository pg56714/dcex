//! Fund and batch request implementations.

mod dispatch_from_asset {
    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::okx::asset::*;
    use crate::exchanges::okx::client::OkxClient;

    use crate::exchanges::okx::params::{
        OkxParams, insert_optional_bool, insert_optional_string, okx_account_id,
    };
    use serde_json::Value;
    impl OkxClient {
        pub(in crate::exchanges::okx) async fn moved_asset_funds_transfer(
            &self,
            _method_name: &str,
            params: &OkxParams,
        ) -> Result<ValidatedResponse> {
            {
                let mut body = params.required_body(&["ccy", "amt"])?;
                body.insert(
                    "from".to_string(),
                    Value::String(okx_account_id(params.required("from_account")?).to_string()),
                );
                body.insert(
                    "to".to_string(),
                    Value::String(okx_account_id(params.required("to_account")?).to_string()),
                );
                for key in ["type", "subAcct", "clientId"] {
                    insert_optional_string(&mut body, key, params.get(key));
                }
                insert_optional_bool(&mut body, "loanTrans", params.get("loanTrans"))?;
                insert_optional_bool(&mut body, "omitPosRisk", params.get("omitPosRisk"))?;
                self.post_request(ASSET_TRANSFER, Value::Object(body)).await
            }
        }
        pub(in crate::exchanges::okx) async fn moved_asset_get_transfer_state(
            &self,
            _method_name: &str,
            params: &OkxParams,
        ) -> Result<ValidatedResponse> {
            {
                self.get_request(
                    ASSET_TRANSFER_STATE,
                    params.only(&["transId", "clientId", "type"]),
                )
                .await
            }
        }
    }
}

mod dispatch_from_subaccount {
    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::okx::client::OkxClient;
    use crate::exchanges::okx::endpoints::*;
    use crate::exchanges::okx::params::{OkxParams, insert_optional_bool, okx_account_id};

    use serde_json::Value;
    impl OkxClient {
        pub(in crate::exchanges::okx) async fn moved_subaccount_transfer_between_subaccounts(
            &self,
            _method_name: &str,
            params: &OkxParams,
        ) -> Result<ValidatedResponse> {
            {
                let mut body =
                    params.required_body(&["ccy", "amt", "fromSubAccount", "toSubAccount"])?;
                body.insert(
                    "from".to_string(),
                    Value::String(okx_account_id(params.required("from_account")?).to_string()),
                );
                body.insert(
                    "to".to_string(),
                    Value::String(okx_account_id(params.required("to_account")?).to_string()),
                );
                insert_optional_bool(&mut body, "loanTrans", params.get("loanTrans"))?;
                insert_optional_bool(&mut body, "omitPosRisk", params.get("omitPosRisk"))?;
                self.post_request(SUBACCOUNT_TRANSFER, Value::Object(body))
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
    funds_transfer(ccy => "ccy", amt => "amt", from_account => "from_account", to_account => "to_account"),
    transfer_between_subaccounts(ccy => "ccy", amt => "amt", from_account => "from_account", to_account => "to_account", from_subaccount => "fromSubAccount", to_subaccount => "toSubAccount"),
    get_transfer_state()
     ];
    }
}
