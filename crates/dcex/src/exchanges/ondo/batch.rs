//! Batch requests.

mod wrappers {
    use crate::exchanges::ondo::OndoClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; OndoClient;
     public [

     ];
     private [
    place_batch_orders(orders => "orders")
     ];
    }
}
