//! Fund and batch request implementations.

mod dispatch_from_account {
    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::bitget::account::*;
    use crate::exchanges::bitget::client::BitgetClient;

    use crate::exchanges::bitget::params::BitgetParams;
    use serde_json::Value;
    impl BitgetClient {
        pub(in crate::exchanges::bitget) async fn moved_account_transfer(
            &self,
            _method_name: &str,
            params: &BitgetParams,
        ) -> Result<ValidatedResponse> {
            {
                for key in ["coin", "amount", "fromType", "toType"] {
                    params.required(key)?;
                }
                if matches!(params.get("fromType"), Some("isolated_margin"))
                    || matches!(params.get("toType"), Some("isolated_margin"))
                {
                    params.required("symbol")?;
                }
                self.post_private(
                    SPOT_ACCOUNT_TRANSFER,
                    Value::Object(params.body(&[
                        "coin",
                        "amount",
                        "fromType",
                        "toType",
                        "symbol",
                        "clientOid",
                    ])),
                )
                .await
            }
        }
        pub(in crate::exchanges::bitget) async fn moved_account_get_transfer_records(
            &self,
            _method_name: &str,
            params: &BitgetParams,
        ) -> Result<ValidatedResponse> {
            {
                params.required("coin")?;
                self.get_private(
                    SPOT_ACCOUNT_TRANSFER_RECORDS,
                    params.only(&[
                        "coin",
                        "fromType",
                        "startTime",
                        "endTime",
                        "clientOid",
                        "pageNum",
                        "limit",
                        "idLessThan",
                    ]),
                )
                .await
            }
        }
        pub(in crate::exchanges::bitget) async fn moved_account_get_transferable_coins(
            &self,
            _method_name: &str,
            params: &BitgetParams,
        ) -> Result<ValidatedResponse> {
            {
                params.required("fromType")?;
                params.required("toType")?;
                self.get_private(
                    SPOT_ACCOUNT_TRANSFER_COIN_INFO,
                    params.only(&["fromType", "toType"]),
                )
                .await
            }
        }
    }
}

mod wrappers_from_wrappers {
    use crate::exchanges::bitget::BitgetClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; BitgetClient;
     public [

     ];
     private [
    transfer_uta_account(from_type => "fromType", to_type => "toType", amount => "amount", coin => "coin"),
    transfer_uta_sub_to_master(from_type => "fromType", to_type => "toType", amount => "amount", coin => "coin"),
    transfer_uta_sub_account(from_type => "fromType", to_type => "toType", amount => "amount", coin => "coin", from_user_id => "fromUserId", to_user_id => "toUserId", client_oid => "clientOid"),
    get_uta_sub_account_transfer_records(),
    get_futures_union_transfer_limits(coin => "coin"),
    get_spot_sub_account_transfer_records(),
    transfer_spot_sub_account(from_type => "fromType", to_type => "toType", amount => "amount", coin => "coin", from_user_id => "fromUserId", to_user_id => "toUserId"),
    get_cross_margin_max_transferable(coin => "coin"),
    get_isolated_margin_max_transferable(product_symbol => "product_symbol"),
    get_uta_max_transferable(coin => "coin"),
    get_uta_transferable_coins(from_type => "fromType", to_type => "toType"),
    get_uta_position_transfer_history(category => "category"),
    get_transfer_records(coin => "coin"),
    get_transferable_coins(from_type => "fromType", to_type => "toType"),
    transfer(coin => "coin", amount => "amount", from_type => "fromType", to_type => "toType")
     ];
    }
}
