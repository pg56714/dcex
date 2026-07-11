use super::client::BitmexClient;

crate::exchanges::impl_exchange_method_wrappers! {
    BitmexClient;
    public [];
    private [
        get_futures_fee_rates(),
        amend_order(),
        cancel_all_orders(),
        set_cancel_all_after(timeout => "timeout"),
        cancel_order(),
        get_executions(),
        get_margin(),
        get_margining_mode(),
        get_order(),
        get_positions(),
        get_trade_history(),
        get_trading_volume(),
        get_wallet_summary(),
        place_limit_buy_order(product_symbol => "product_symbol", order_qty => "orderQty", price => "price"),
        place_limit_order(product_symbol => "product_symbol", side => "side", order_qty => "orderQty", price => "price"),
        place_limit_sell_order(product_symbol => "product_symbol", order_qty => "orderQty", price => "price"),
        place_market_buy_order(product_symbol => "product_symbol", order_qty => "orderQty"),
        place_market_order(product_symbol => "product_symbol", side => "side", order_qty => "orderQty"),
        place_market_sell_order(product_symbol => "product_symbol", order_qty => "orderQty"),
        place_order(product_symbol => "product_symbol", side => "side"),
        place_post_only_buy_order(product_symbol => "product_symbol", order_qty => "orderQty", price => "price"),
        place_post_only_order(product_symbol => "product_symbol", side => "side", order_qty => "orderQty", price => "price"),
        place_post_only_sell_order(product_symbol => "product_symbol", order_qty => "orderQty", price => "price"),
        set_leverage(product_symbol => "product_symbol", leverage => "leverage"),
        set_margining_mode(),
        switch_mode(product_symbol => "product_symbol"),
    ];
}
