//! Transfers requests.

mod wrappers {
    use crate::exchanges::lighter::LighterClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; LighterClient;
     public [

     ];
     private [
    get_transfer_fee_info(),
    get_transfer_history()
     ];
    }
}
