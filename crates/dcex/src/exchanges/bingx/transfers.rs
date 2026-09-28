//! Fund and batch request implementations.

mod dispatch_from_account {
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::bingx::account::*;
    use crate::exchanges::bingx::client::BingxClient;

    use crate::Result;
    use crate::exchanges::bingx::params::{
        BingxParams, push_optional, require_pair_or_identifier, validate_positive_number,
        validate_time_range, validate_u64_range,
    };
    impl BingxClient {
        pub(in crate::exchanges::bingx) async fn moved_account_get_transferable_coins(
            &self,
            _method_name: &str,
            params: &BingxParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&["fromAccount", "toAccount", "recvWindow"])?;
                params.required("fromAccount")?;
                params.required("toAccount")?;
                validate_recv_window(params)?;
                self.private_get(
                    TRANSFERABLE_COINS,
                    params.only(&["fromAccount", "toAccount", "recvWindow"]),
                )
                .await
            }
        }
        pub(in crate::exchanges::bingx) async fn moved_account_asset_transfer(
            &self,
            _method_name: &str,
            params: &BingxParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&[
                    "fromAccount",
                    "toAccount",
                    "asset",
                    "amount",
                    "recvWindow",
                ])?;
                params.required("fromAccount")?;
                params.required("toAccount")?;
                params.required("asset")?;
                params.required("amount")?;
                validate_positive_number(params, "amount")?;
                validate_recv_window(params)?;
                self.private_post(
                    ASSET_TRANSFER,
                    params.only(&["fromAccount", "toAccount", "asset", "amount", "recvWindow"]),
                )
                .await
            }
        }
        pub(in crate::exchanges::bingx) async fn moved_account_get_asset_transfer_records(
            &self,
            _method_name: &str,
            params: &BingxParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&[
                    "fromAccount",
                    "toAccount",
                    "transferId",
                    "tranId",
                    "startTime",
                    "endTime",
                    "pageIndex",
                    "pageSize",
                    "recvWindow",
                ])?;
                if params.get("transferId").is_none() && params.get("tranId").is_none() {
                    require_pair_or_identifier(params, "fromAccount", "toAccount", "transferId")?;
                }
                validate_u64_range(params, "pageIndex", 1, u64::MAX)?;
                validate_u64_range(params, "pageSize", 1, 100)?;
                validate_u64_range(params, "transferId", 1, u64::MAX)?;
                validate_u64_range(params, "tranId", 1, u64::MAX)?;
                validate_time_range(params, "startTime", "endTime", None)?;
                validate_recv_window(params)?;
                let mut query = params.only(&[
                    "fromAccount",
                    "toAccount",
                    "transferId",
                    "startTime",
                    "endTime",
                    "pageIndex",
                    "pageSize",
                    "recvWindow",
                ]);
                if !query.iter().any(|(key, _)| key == "transferId") {
                    push_optional(&mut query, "transferId", params.get("tranId"));
                }
                self.private_get(TRANSFER_RECORDS, query).await
            }
        }
        pub(in crate::exchanges::bingx) async fn moved_account_get_subaccount_transfer_history(
            &self,
            _method_name: &str,
            params: &BingxParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&[
                    "uid",
                    "type",
                    "tranId",
                    "startTime",
                    "endTime",
                    "pageId",
                    "pagingSize",
                    "recvWindow",
                ])?;
                params.required("uid")?;
                validate_u64_range(params, "uid", 1, u64::MAX)?;
                validate_u64_range(params, "pageId", 1, u64::MAX)?;
                validate_u64_range(params, "pagingSize", 1, 100)?;
                validate_time_range(params, "startTime", "endTime", None)?;
                validate_recv_window(params)?;
                self.private_get(
                    SUBACCOUNT_TRANSFER_HISTORY,
                    params.only(&[
                        "uid",
                        "type",
                        "tranId",
                        "startTime",
                        "endTime",
                        "pageId",
                        "pagingSize",
                        "recvWindow",
                    ]),
                )
                .await
            }
        }
        pub(in crate::exchanges::bingx) async fn moved_account_get_subaccount_transferable_amounts(
            &self,
            _method_name: &str,
            params: &BingxParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&[
                    "fromUid",
                    "fromAccountType",
                    "toUid",
                    "toAccountType",
                    "recvWindow",
                ])?;
                for key in ["fromUid", "fromAccountType", "toUid", "toAccountType"] {
                    params.required(key)?;
                }
                validate_u64_range(params, "fromUid", 1, u64::MAX)?;
                validate_u64_range(params, "toUid", 1, u64::MAX)?;
                validate_u64_range(params, "fromAccountType", 1, 3)?;
                validate_u64_range(params, "toAccountType", 1, 3)?;
                validate_recv_window(params)?;
                self.private_post(
                    SUBACCOUNT_TRANSFERABLE_AMOUNTS,
                    params.only(&[
                        "fromUid",
                        "fromAccountType",
                        "toUid",
                        "toAccountType",
                        "recvWindow",
                    ]),
                )
                .await
            }
        }
        pub(in crate::exchanges::bingx) async fn moved_account_transfer_subaccount_assets(
            &self,
            _method_name: &str,
            params: &BingxParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&[
                    "assetName",
                    "transferAmount",
                    "fromUid",
                    "fromType",
                    "fromAccountType",
                    "toUid",
                    "toType",
                    "toAccountType",
                    "remark",
                    "recvWindow",
                ])?;
                for key in [
                    "assetName",
                    "transferAmount",
                    "fromUid",
                    "fromType",
                    "fromAccountType",
                    "toUid",
                    "toType",
                    "toAccountType",
                    "remark",
                ] {
                    params.required(key)?;
                }
                validate_positive_number(params, "transferAmount")?;
                validate_u64_range(params, "fromUid", 1, u64::MAX)?;
                validate_u64_range(params, "toUid", 1, u64::MAX)?;
                validate_u64_range(params, "fromType", 1, 2)?;
                validate_u64_range(params, "toType", 1, 2)?;
                validate_u64_range(params, "fromAccountType", 1, 3)?;
                validate_u64_range(params, "toAccountType", 1, 3)?;
                validate_recv_window(params)?;
                self.private_post(
                    SUBACCOUNT_ASSET_TRANSFER,
                    params.only(&[
                        "assetName",
                        "transferAmount",
                        "fromUid",
                        "fromType",
                        "fromAccountType",
                        "toUid",
                        "toType",
                        "toAccountType",
                        "remark",
                        "recvWindow",
                    ]),
                )
                .await
            }
        }
    }
}

mod wrappers_from_wrappers {
    use crate::exchanges::bingx::BingxClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; BingxClient;
     public [

     ];
     private [
    asset_transfer(
                from_account => "fromAccount",
                to_account => "toAccount",
                asset => "asset",
                amount => "amount"
            ),
    get_asset_transfer_records(),
    get_subaccount_transfer_history(uid => "uid"),
    get_subaccount_transferable_amounts(
                from_uid => "fromUid",
                from_account_type => "fromAccountType",
                to_uid => "toUid",
                to_account_type => "toAccountType"
            ),
    get_transferable_coins(from_account => "fromAccount", to_account => "toAccount"),
    transfer_subaccount_assets(
                asset_name => "assetName",
                transfer_amount => "transferAmount",
                from_uid => "fromUid",
                from_type => "fromType",
                from_account_type => "fromAccountType",
                to_uid => "toUid",
                to_type => "toType",
                to_account_type => "toAccountType",
                remark => "remark"
            ),
    set_sub_account_transfer_authorization(
                sub_uids => "subUids",
                transferable => "transferable"
            ),
    get_internal_transfer_records(coin => "coin"),
    get_sub_account_internal_transfer_records(coin => "coin")
     ];
    }
}
