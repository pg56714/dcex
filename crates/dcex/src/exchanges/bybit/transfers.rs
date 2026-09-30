//! Fund and batch request implementations.

mod account_requests {
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::bybit::account::*;
    use crate::exchanges::bybit::client::BybitClient;

    use crate::exchanges::bybit::params::BybitParams;
    use crate::{DcexError, Result};

    impl BybitClient {
        pub(in crate::exchanges::bybit) async fn dispatch_get_transferable_amount(
            &self,
            _method_name: &str,
            params: &BybitParams,
        ) -> Result<ValidatedResponse> {
            {
                let coins = params.required("coins")?;
                if coins.is_empty() {
                    return Err(DcexError::InvalidInput(
                        "coins must contain at least one coin.".to_string(),
                    ));
                }
                let count = coins.split(',').filter(|coin| !coin.is_empty()).count();
                if count > 20 {
                    return Err(DcexError::InvalidInput(
                        "coins must contain no more than 20 coins.".to_string(),
                    ));
                }
                self.get_request(
                    GET_TRANSFERABLE_AMOUNT,
                    vec![("coinName".to_string(), coins.to_string())],
                )
                .await
            }
        }
    }
}

mod asset_requests {
    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::bybit::client::BybitClient;
    use crate::exchanges::bybit::funding::*;

    use crate::exchanges::bybit::params::{
        BybitParams, generate_transfer_id, push_optional, string_body,
    };
    use serde_json::Value;
    impl BybitClient {
        pub(in crate::exchanges::bybit) async fn dispatch_get_internal_transfer_records(
            &self,
            _method_name: &str,
            params: &BybitParams,
        ) -> Result<ValidatedResponse> {
            {
                let mut query = vec![(
                    "limit".to_string(),
                    params.get("limit").unwrap_or("20").to_string(),
                )];
                push_optional(&mut query, "transferId", params.get("transferId"));
                push_optional(&mut query, "coin", params.get("coin"));
                push_optional(&mut query, "status", params.get("status"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                push_optional(&mut query, "endTime", params.get("endTime"));
                push_optional(&mut query, "cursor", params.get("cursor"));
                self.get_request(GET_INTERNAL_TRANSFER_RECORDS, query).await
            }
        }
        pub(in crate::exchanges::bybit) async fn dispatch_get_transferable_coin(
            &self,
            _method_name: &str,
            params: &BybitParams,
        ) -> Result<ValidatedResponse> {
            {
                let query = vec![
                    (
                        "fromAccountType".to_string(),
                        params.required("fromAccountType")?.to_string(),
                    ),
                    (
                        "toAccountType".to_string(),
                        params.required("toAccountType")?.to_string(),
                    ),
                ];
                self.get_request(GET_TRANSFERABLE_COIN, query).await
            }
        }
        pub(in crate::exchanges::bybit) async fn dispatch_create_internal_transfer(
            &self,
            _method_name: &str,
            params: &BybitParams,
        ) -> Result<ValidatedResponse> {
            {
                let mut body = string_body(&[
                    ("coin", params.required("coin")?),
                    ("amount", params.required("amount")?),
                    ("fromAccountType", params.required("fromAccountType")?),
                    ("toAccountType", params.required("toAccountType")?),
                ]);
                let transfer_id = params
                    .get("transferId")
                    .map(str::to_string)
                    .unwrap_or_else(generate_transfer_id);
                body.insert("transferId".to_string(), Value::String(transfer_id));
                self.post_request(CREATE_INTERNAL_TRANSFER, body).await
            }
        }
        pub(in crate::exchanges::bybit) async fn dispatch_create_universal_transfer(
            &self,
            _method_name: &str,
            params: &BybitParams,
        ) -> Result<ValidatedResponse> {
            {
                let mut body = string_body(&[
                    ("coin", params.required("coin")?),
                    ("amount", params.required("amount")?),
                    ("fromMemberId", params.required("fromMemberId")?),
                    ("toMemberId", params.required("toMemberId")?),
                    ("fromAccountType", params.required("fromAccountType")?),
                    ("toAccountType", params.required("toAccountType")?),
                ]);
                let transfer_id = params
                    .get("transferId")
                    .map(str::to_string)
                    .unwrap_or_else(generate_transfer_id);
                body.insert("transferId".to_string(), Value::String(transfer_id));
                self.post_request(CREATE_UNIVERSAL_TRANSFER, body).await
            }
        }
        pub(in crate::exchanges::bybit) async fn dispatch_get_universal_transfer_records(
            &self,
            _method_name: &str,
            params: &BybitParams,
        ) -> Result<ValidatedResponse> {
            {
                let mut query = vec![(
                    "limit".to_string(),
                    params.get("limit").unwrap_or("20").to_string(),
                )];
                push_optional(&mut query, "transferId", params.get("transferId"));
                push_optional(&mut query, "coin", params.get("coin"));
                push_optional(&mut query, "status", params.get("status"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                push_optional(&mut query, "endTime", params.get("endTime"));
                push_optional(&mut query, "fromMemberId", params.get("fromMemberId"));
                push_optional(&mut query, "toMemberId", params.get("toMemberId"));
                push_optional(&mut query, "cursor", params.get("cursor"));
                self.get_request(GET_UNIVERSAL_TRANSFER_RECORDS, query)
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
    create_internal_transfer(coin => "coin", amount => "amount", from_account_type => "fromAccountType", to_account_type => "toAccountType"),
    create_universal_transfer(coin => "coin", amount => "amount", from_member_id => "fromMemberId", to_member_id => "toMemberId", from_account_type => "fromAccountType", to_account_type => "toAccountType"),
    get_internal_transfer_records(),
    get_transferable_amount(coins => "coins"),
    get_transferable_coin(from_account_type => "fromAccountType", to_account_type => "toAccountType"),
    get_universal_transfer_records()
     ];
    }
}

impl super::client::BybitClient {
    pub(in crate::exchanges::bybit) async fn transfers_table_request(
        &self,
        name: &str,
        params: &super::params::BybitParams,
        public: bool,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        self.table_request_transport(name, params, public).await
    }
}

impl super::client::BybitClient {
    pub(in crate::exchanges::bybit) async fn transfers_field_schema_request(
        &self,
        name: &str,
        params: &super::params::BybitParams,
        public: bool,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        self.field_schema_request_transport(name, params, public)
            .await
    }
}
