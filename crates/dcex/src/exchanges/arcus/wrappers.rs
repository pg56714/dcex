//! Typed Rust entry points over the named Arcus REST routes.

use super::{ArcusClient, ArcusSpotClient};

crate::exchanges::impl_exchange_method_wrappers! {
    ArcusClient;
    public [
        get_api_keys(),
        get_trade(trade_id => "trade_id", market => "market"),
        get_account_stats(),
        get_mid_prices(),
        get_compliance(),
        get_rate_limit(),
        get_time(),
        get_fill(trade_id => "trade_id"),
        get_funding(),
        get_interest(),
        get_live_prices(),
        get_funding_rates(market => "market"),
        get_candles(market => "market", timeframe => "timeframe", end_time => "to"),
        get_order_history(),
        get_portfolio_history(),
        get_trades(market => "market"),
        get_spot_fills(),
        get_spot_positions(),
        health(),
        get_service_info(),
        get_leaderboard(),

        get_markets(), get_spot_assets(), get_fee_tiers(),
        get_account(), get_bbo(market => "market"),
        get_l2_orderbook(market => "market"), get_positions(),
        get_open_orders(), get_order_status(order_id => "order_id"),
        get_fills(), get_transfer_updates(), get_leverages()
    ];
    private [
        create_api_key_signed(body => "body"), revoke_api_key_signed(body => "body"),
        cancel_all_orders(), set_leverage(product_symbol => "product_symbol", leverage => "leverage"),
        schedule_cancel(time => "time"), disarm_scheduled_cancel(),
        adjust_isolated_margin(product_symbol => "product_symbol", amount => "amount"),
        submit_internal_transfer(signed_transfer_json => "signed_transfer_json"),
        place_order(product_symbol => "product_symbol", side => "side", price => "price", quantity => "quantity"),
        modify_order(product_symbol => "product_symbol", side => "side", price => "price", quantity => "quantity", order_id => "order_id", good_til_time => "good_til_time", time_in_force => "time_in_force", reduce_only => "reduce_only"),
        cancel_order(product_symbol => "product_symbol", order_id => "order_id"),
        batch_place_orders(orders => "orders"),
        batch_cancel_orders(cancels => "cancels"),
        batch_modify_orders(modifies => "modifies")
    ];
}

crate::exchanges::impl_exchange_method_wrappers! {
    ArcusSpotClient;
    public [
        health(), get_tokens(),
        get_price(sell_token => "sellToken", buy_token => "buyToken", sell_amount => "sellAmount"),
        get_quote(sell_token => "sellToken", buy_token => "buyToken", sell_amount => "sellAmount", taker => "taker"),
        get_native_balance(), get_balances(), get_block_number(),
        get_token_balance(token => "token"), get_allowance(token => "token"),
        get_transaction_receipt(tx_hash => "tx_hash"),
        get_trade_history(from_block => "from_block")
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

crate::exchanges::impl_exchange_method_wrappers! { @extend; ArcusClient; public [
get_market_metadata(), get_market_overview(), get_spot_market_overview(),
get_metadata_candles(market => "market", timeframe => "timeframe", to => "to"), get_user_preferences()
]; private [upsert_user_preferences(preferences => "preferences"), delete_user_preference_signed(key => "key", timestamp => "timestamp", signature => "signature")]; }
