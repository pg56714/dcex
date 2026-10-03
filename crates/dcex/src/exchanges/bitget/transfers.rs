//! Fund and batch request implementations.

mod wrappers {
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
    get_uta_max_transferable(coin => "coin"),
    get_uta_transferable_coins(from_type => "fromType", to_type => "toType"),
    get_uta_position_transfer_history(category => "category")
     ];
    }
}

impl super::client::BitgetClient {
    pub(in crate::exchanges::bitget) async fn transfers_table_request(
        &self,
        name: &str,
        params: &super::params::BitgetParams,
        public: bool,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        self.table_request_transport(name, params, public).await
    }
}

impl super::client::BitgetClient {
    pub(in crate::exchanges::bitget) async fn transfers_catalog_request(
        &self,
        name: &str,
        p: &super::params::BitgetParams,
        public: bool,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        self.catalog_request_transport(name, p, public).await
    }
}
