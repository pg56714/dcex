use super::client::BitmexClient;

crate::exchanges::impl_exchange_method_wrappers! {
    BitmexClient;
    public [];
    private [
        amend_order() => amend_order_with,
        cancel_all_orders() => cancel_all_orders_with,
        cancel_order() => cancel_order_with,
        get_executions() => get_executions_with,
        get_margin() => get_margin_with,
        get_margining_mode() => get_margining_mode_with,
        get_order() => get_order_with,
        get_positions() => get_positions_with,
        get_trade_history() => get_trade_history_with,
        get_trading_volume() => get_trading_volume_with,
        get_wallet_summary() => get_wallet_summary_with,
        place_limit_buy_order(product_symbol => "product_symbol", order_qty => "orderQty", price => "price") => place_limit_buy_order_with,
        place_limit_order(product_symbol => "product_symbol", side => "side", order_qty => "orderQty", price => "price") => place_limit_order_with,
        place_limit_sell_order(product_symbol => "product_symbol", order_qty => "orderQty", price => "price") => place_limit_sell_order_with,
        place_market_buy_order(product_symbol => "product_symbol", order_qty => "orderQty") => place_market_buy_order_with,
        place_market_order(product_symbol => "product_symbol", side => "side", order_qty => "orderQty") => place_market_order_with,
        place_market_sell_order(product_symbol => "product_symbol", order_qty => "orderQty") => place_market_sell_order_with,
        place_order(product_symbol => "product_symbol", side => "side") => place_order_with,
        place_post_only_buy_order(product_symbol => "product_symbol", order_qty => "orderQty", price => "price") => place_post_only_buy_order_with,
        place_post_only_order(product_symbol => "product_symbol", side => "side", order_qty => "orderQty", price => "price") => place_post_only_order_with,
        place_post_only_sell_order(product_symbol => "product_symbol", order_qty => "orderQty", price => "price") => place_post_only_sell_order_with,
        set_leverage(product_symbol => "product_symbol", leverage => "leverage") => set_leverage_with,
        set_margining_mode() => set_margining_mode_with,
        switch_mode(product_symbol => "product_symbol") => switch_mode_with,
    ];
}
