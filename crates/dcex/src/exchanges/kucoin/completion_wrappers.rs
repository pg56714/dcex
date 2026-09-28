//! Wrappers for newly documented routes and explicit incomplete-spec pass-through.
use super::client::KucoinClient;

crate::exchanges::impl_exchange_method_wrappers! {
    @extend;
    KucoinClient;
    public [

    ];
    private [
        /// API withdrawals and external transfers have no second confirmation; they execute on submit.
        create_withdrawal(currency => "currency", amount => "amount", to_address => "toAddress", withdraw_type => "withdrawType"),
        /// API withdrawals and external transfers have no second confirmation; they execute on submit.
        create_uta_withdrawal(currency => "currency", amount => "amount", to_address => "toAddress", withdraw_type => "withdrawType"),
        cancel_withdrawal(withdrawal_id => "withdrawalId"),
        cancel_uta_withdrawal(withdraw_id => "withdrawId"),
        cancel_margin_stop_order_by_id_raw(),
    ];
}
