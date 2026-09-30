//! Fund and batch request implementations.

mod account_requests {
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::mexc::account::*;
    use crate::exchanges::mexc::client::MexcClient;

    use crate::Result;
    use crate::exchanges::mexc::params::{
        MexcParams, add_pagination_defaults, validate_enum, validate_u64_range,
    };
    use crate::http::HttpMethod;

    impl MexcClient {
        pub(in crate::exchanges::mexc) async fn dispatch_transfer_subaccount_assets(
            &self,
            _method_name: &str,
            params: &MexcParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&[
                    "fromAccount",
                    "toAccount",
                    "fromAccountType",
                    "toAccountType",
                    "asset",
                    "amount",
                    "recvWindow",
                ])?;
                for key in ["fromAccountType", "toAccountType", "asset", "amount"] {
                    params.required(key)?;
                }
                validate_enum(params, "fromAccountType", &["SPOT", "FUTURES"])?;
                validate_enum(params, "toAccountType", &["SPOT", "FUTURES"])?;
                self.spot_private(
                    HttpMethod::Post,
                    SPOT_SUBACCOUNT_UNIVERSAL_TRANSFER,
                    params.only(&[
                        "fromAccount",
                        "toAccount",
                        "fromAccountType",
                        "toAccountType",
                        "asset",
                        "amount",
                        "recvWindow",
                    ]),
                )
                .await
            }
        }
        pub(in crate::exchanges::mexc) async fn dispatch_get_subaccount_transfer_history(
            &self,
            _method_name: &str,
            params: &MexcParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&[
                    "fromAccount",
                    "toAccount",
                    "fromAccountType",
                    "toAccountType",
                    "startTime",
                    "endTime",
                    "page",
                    "limit",
                    "recvWindow",
                ])?;
                params.required("fromAccountType")?;
                params.required("toAccountType")?;
                validate_enum(params, "fromAccountType", &["SPOT", "FUTURES"])?;
                validate_enum(params, "toAccountType", &["SPOT", "FUTURES"])?;
                validate_u64_range(params, "page", 1, u64::MAX)?;
                validate_u64_range(params, "limit", 1, 500)?;
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_SUBACCOUNT_UNIVERSAL_TRANSFER,
                    params.only(&[
                        "fromAccount",
                        "toAccount",
                        "fromAccountType",
                        "toAccountType",
                        "startTime",
                        "endTime",
                        "page",
                        "limit",
                        "recvWindow",
                    ]),
                )
                .await
            }
        }
        pub(in crate::exchanges::mexc) async fn dispatch_user_universal_transfer(
            &self,
            _method_name: &str,
            params: &MexcParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&[
                    "fromAccountType",
                    "toAccountType",
                    "asset",
                    "amount",
                    "recvWindow",
                ])?;
                for key in ["fromAccountType", "toAccountType", "asset", "amount"] {
                    params.required(key)?;
                }
                validate_enum(params, "fromAccountType", &["SPOT", "FUTURES"])?;
                validate_enum(params, "toAccountType", &["SPOT", "FUTURES"])?;
                self.spot_private(
                    HttpMethod::Post,
                    SPOT_USER_UNIVERSAL_TRANSFER,
                    params.only(&[
                        "fromAccountType",
                        "toAccountType",
                        "asset",
                        "amount",
                        "recvWindow",
                    ]),
                )
                .await
            }
        }
        pub(in crate::exchanges::mexc) async fn dispatch_get_user_universal_transfer_history(
            &self,
            _method_name: &str,
            params: &MexcParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&[
                    "fromAccountType",
                    "toAccountType",
                    "startTime",
                    "endTime",
                    "page",
                    "size",
                    "recvWindow",
                ])?;
                params.required("fromAccountType")?;
                params.required("toAccountType")?;
                validate_enum(params, "fromAccountType", &["SPOT", "FUTURES"])?;
                validate_enum(params, "toAccountType", &["SPOT", "FUTURES"])?;
                validate_u64_range(params, "page", 1, u64::MAX)?;
                validate_u64_range(params, "size", 1, 100)?;
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_USER_UNIVERSAL_TRANSFER,
                    params.only(&[
                        "fromAccountType",
                        "toAccountType",
                        "startTime",
                        "endTime",
                        "page",
                        "size",
                        "recvWindow",
                    ]),
                )
                .await
            }
        }
        pub(in crate::exchanges::mexc) async fn dispatch_get_user_universal_transfer_by_id(
            &self,
            _method_name: &str,
            params: &MexcParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&["tranId", "recvWindow"])?;
                params.required("tranId")?;
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_USER_UNIVERSAL_TRANSFER_BY_ID,
                    params.only(&["tranId", "recvWindow"]),
                )
                .await
            }
        }
        pub(in crate::exchanges::mexc) async fn dispatch_get_internal_transfer_history(
            &self,
            _method_name: &str,
            params: &MexcParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&[
                    "tranId",
                    "startTime",
                    "endTime",
                    "page",
                    "limit",
                    "recvWindow",
                ])?;
                validate_u64_range(params, "page", 1, u64::MAX)?;
                validate_u64_range(params, "limit", 1, u64::MAX)?;
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_INTERNAL_TRANSFER_HISTORY,
                    params.only(&[
                        "tranId",
                        "startTime",
                        "endTime",
                        "page",
                        "limit",
                        "recvWindow",
                    ]),
                )
                .await
            }
        }
        pub(in crate::exchanges::mexc) async fn dispatch_get_contract_transfer_records(
            &self,
            _method_name: &str,
            params: &MexcParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&["currency", "state", "type", "page_num", "page_size"])?;
                validate_enum(params, "state", &["WAIT", "SUCCESS", "FAILED"])?;
                validate_enum(params, "type", &["IN", "OUT"])?;
                validate_u64_range(params, "page_num", 1, u64::MAX)?;
                validate_u64_range(params, "page_size", 1, 100)?;
                let mut query =
                    params.only(&["currency", "state", "type", "page_num", "page_size"]);
                add_pagination_defaults(&mut query);
                self.contract_get(CONTRACT_TRANSFER_RECORDS, query).await
            }
        }
    }
}

mod wrappers {
    use crate::exchanges::mexc::MexcClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; MexcClient;
     public [

     ];
     private [
    get_contract_transfer_records(),
    get_internal_transfer_history(),
    get_subaccount_transfer_history(from_account_type => "fromAccountType", to_account_type => "toAccountType"),
    get_user_universal_transfer_by_id(tran_id => "tranId"),
    get_user_universal_transfer_history(from_account_type => "fromAccountType", to_account_type => "toAccountType"),
    transfer_subaccount_assets(from_account_type => "fromAccountType", to_account_type => "toAccountType", asset => "asset", amount => "amount"),
    user_universal_transfer(from_account_type => "fromAccountType", to_account_type => "toAccountType", asset => "asset", amount => "amount")
     ];
    }
}

impl super::client::MexcClient {
    pub(in crate::exchanges::mexc) async fn transfers_field_schema_request(
        &self,
        name: &str,
        p: &super::params::MexcParams,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        self.field_schema_request_transport(name, p).await
    }
}
