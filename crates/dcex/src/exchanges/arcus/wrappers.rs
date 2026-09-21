//! Typed Rust entry points over the named Arcus REST routes.

use super::{ArcusClient, ArcusSpotClient};

crate::exchanges::impl_exchange_method_wrappers! {
    ArcusClient;
    public [
        get_markets(), get_spot_assets(), get_fee_tiers(),
        get_account(), get_bbo(market => "market"),
        get_l2_orderbook(market => "market"), get_positions(),
        get_open_orders(), get_order_status(order_id => "order_id"),
        get_fills(), get_transfer_updates(), get_leverages()
    ];
    private [
        cancel_all_orders(), set_leverage(product_symbol => "product_symbol", leverage => "leverage"),
        submit_internal_transfer(signed_transfer_json => "signed_transfer_json"),
        place_order(product_symbol => "product_symbol", side => "side", price => "price", quantity => "quantity"),
        cancel_order(product_symbol => "product_symbol", order_id => "order_id")
    ];
}

crate::exchanges::impl_exchange_method_wrappers! {
    ArcusSpotClient;
    public [
        health(), get_tokens(),
        get_price(sell_token => "sellToken", buy_token => "buyToken", sell_amount => "sellAmount"),
        get_quote(sell_token => "sellToken", buy_token => "buyToken", sell_amount => "sellAmount", taker => "taker")
    ];
    private [];
}

impl ArcusSpotClient {
    /// Query a submitted quote by its transaction/quote ID on the Arcus venue.
    pub fn get_status(
        &self,
        id: impl ToString,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::public(
            self,
            "get_status",
            vec![
                ("venue".into(), "arcus".into()),
                ("id".into(), id.to_string()),
            ],
        )
    }
}
