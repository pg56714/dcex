use super::BackpackClient;
crate::exchanges::impl_exchange_method_wrappers! {
    @extend;
    BackpackClient;
    public [];
    private [
        submit_rfq_quote(rfq_id => "rfqId", bid_price => "bidPrice", ask_price => "askPrice"),
        /// API withdrawals and external transfers have no second confirmation; they execute on submit.
        create_withdrawal(address => "address", blockchain => "blockchain", quantity => "quantity", symbol => "symbol"),
    ];
}
