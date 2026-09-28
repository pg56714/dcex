use super::client::BitgetClient;

crate::exchanges::impl_exchange_method_wrappers! {
    @extend; BitgetClient; public []; private [
        /// API withdrawals and external transfers have no second confirmation; they execute on submit.
        create_spot_withdrawal(coin => "coin", transfer_type => "transferType", address => "address", size => "size"),
        cancel_spot_withdrawal(order_id => "orderId"),
        create_uta_agent_sub_account(username => "username", passphrase => "passphrase"),
        create_classic_agent_sub_account(username => "username", passphrase => "passphrase"),
        /// API withdrawals and external transfers have no second confirmation; they execute on submit.
        create_uta_withdrawal(coin => "coin", transfer_type => "transferType", address => "address", size => "size"),
        cancel_uta_withdrawal(),
    ];
}
