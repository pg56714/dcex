//! Wrappers for newly documented routes and explicit incomplete-spec pass-through.
use super::client::BingxClient;

crate::exchanges::impl_exchange_method_wrappers! {
    @extend;
    BingxClient;
    public [
        get_spot_server_time(),
    ];
    private [
        /// API withdrawals and external transfers have no second confirmation; they execute on submit.
        transfer_master_internal(coin => "coin", user_account_type => "userAccountType", user_account => "userAccount", amount => "amount", wallet_type => "walletType"),
        transfer_sub_account_internal(coin => "coin", user_account_type => "userAccountType", user_account => "userAccount", amount => "amount", wallet_type => "walletType"),
        /// API withdrawals and external transfers have no second confirmation; they execute on submit.
        create_withdrawal(coin => "coin", address => "address", amount => "amount", wallet_type => "walletType"),
    ];
}
