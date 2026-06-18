use super::client::BitmexClient;

crate::exchanges::impl_exchange_method_wrappers! {
    BitmexClient;
    public [];
    private [
        amend_order,
        cancel_all_orders,
        cancel_order,
        get_executions,
        get_margin,
        get_margining_mode,
        get_order,
        get_positions,
        get_trade_history,
        get_trading_volume,
        get_wallet_summary,
        place_limit_buy_order,
        place_limit_order,
        place_limit_sell_order,
        place_market_buy_order,
        place_market_order,
        place_market_sell_order,
        place_order,
        place_post_only_buy_order,
        place_post_only_order,
        place_post_only_sell_order,
        set_leverage,
        set_margining_mode,
        switch_mode,
    ];
}
