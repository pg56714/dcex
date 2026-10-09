//! Fund and batch request implementations.

mod asset_requests {
    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::okx::client::OkxClient;
    use crate::exchanges::okx::funding::*;

    use crate::exchanges::okx::params::{
        OkxParams, insert_optional_bool, insert_optional_string, okx_account_id,
    };
    use serde_json::Value;
    impl OkxClient {
        pub(in crate::exchanges::okx) async fn dispatch_funds_transfer(
            &self,
            _method_name: &str,
            params: &OkxParams,
        ) -> Result<ValidatedResponse> {
            params.ensure_allowed(&[
                "ccy",
                "amt",
                "loanTrans",
                "omitPosRisk",
                "from",
                "to",
                "type",
                "subAcct",
                "clientId",
            ])?;
            {
                let mut body = params.required_body(&["ccy", "amt"])?;
                for key in ["from", "to"] {
                    body.insert(key.to_string(), Value::String(okx_account_id(params, key)?));
                }
                for key in ["type", "subAcct", "clientId"] {
                    insert_optional_string(&mut body, key, params.get(key));
                }
                insert_optional_bool(&mut body, "loanTrans", params.get("loanTrans"))?;
                insert_optional_bool(&mut body, "omitPosRisk", params.get("omitPosRisk"))?;
                self.post_request(ASSET_TRANSFER, Value::Object(body)).await
            }
        }
        pub(in crate::exchanges::okx) async fn dispatch_get_transfer_state(
            &self,
            _method_name: &str,
            params: &OkxParams,
        ) -> Result<ValidatedResponse> {
            params.ensure_allowed(&["transId", "clientId", "type"])?;
            if params.get("transId").is_none() && params.get("clientId").is_none() {
                return Err(crate::DcexError::InvalidInput(
                    "OKX: one of transId, clientId is required".to_string(),
                ));
            }
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

mod subaccount_requests {
    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::okx::client::OkxClient;
    use crate::exchanges::okx::endpoints::*;
    use crate::exchanges::okx::params::{OkxParams, insert_optional_bool, okx_account_id};

    use serde_json::Value;
    impl OkxClient {
        pub(in crate::exchanges::okx) async fn dispatch_transfer_between_subaccounts(
            &self,
            _method_name: &str,
            params: &OkxParams,
        ) -> Result<ValidatedResponse> {
            params.ensure_allowed(&[
                "ccy",
                "amt",
                "fromSubAccount",
                "toSubAccount",
                "loanTrans",
                "omitPosRisk",
                "from",
                "to",
            ])?;
            {
                let mut body =
                    params.required_body(&["ccy", "amt", "fromSubAccount", "toSubAccount"])?;
                for key in ["from", "to"] {
                    body.insert(key.to_string(), Value::String(okx_account_id(params, key)?));
                }
                insert_optional_bool(&mut body, "loanTrans", params.get("loanTrans"))?;
                insert_optional_bool(&mut body, "omitPosRisk", params.get("omitPosRisk"))?;
                self.post_request(SUBACCOUNT_TRANSFER, Value::Object(body))
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
    funds_transfer(ccy => "ccy", amt => "amt", from_account => "from", to_account => "to"),
    transfer_between_subaccounts(ccy => "ccy", amt => "amt", from_account => "from", to_account => "to", from_subaccount => "fromSubAccount", to_subaccount => "toSubAccount"),
    get_transfer_state()
     ];
    }
}

impl super::client::OkxClient {
    pub(in crate::exchanges::okx) async fn transfers_table_request(
        &self,
        name: &str,
        p: &super::params::OkxParams,
        public: bool,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        self.table_request_transport(name, p, public).await
    }
}
