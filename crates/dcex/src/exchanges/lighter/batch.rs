//! Batch requests.

mod wrappers_from_wrappers {
    use crate::exchanges::lighter::LighterClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; LighterClient;
     public [

     ];
     private [
    send_tx_batch(tx_types => "tx_types", tx_infos => "tx_infos")
     ];
    }
}
