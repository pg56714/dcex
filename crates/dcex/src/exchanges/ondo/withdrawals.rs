//! Withdrawals requests.

mod wrappers_from_wrappers {
    use crate::exchanges::ondo::OndoClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; OndoClient;
     public [

     ];
     private [

            /// API withdrawals and external transfers have no second confirmation; they execute on submit.
    create_withdrawal(customer_withdrawal_id => "customer_withdrawal_id", symbol => "symbol", network => "network", amount => "amount", address => "address"),
    sandbox_withdrawal(customer_withdrawal_id => "customer_withdrawal_id", symbol => "symbol", amount => "amount", from_account => "from"),
    get_withdrawal_limits(),
    get_withdrawal_status()
     ];
    }
}
