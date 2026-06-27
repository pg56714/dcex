use super::HyperliquidClient;

crate::exchanges::impl_exchange_method_wrappers! {
    HyperliquidClient;
    public [
        clearinghouse_state(user => "user") => clearinghouse_state_with,
        get_candle_snapshot(product_symbol => "product_symbol", interval => "interval", start_time => "startTime") => get_candle_snapshot_with,
        get_funding_rate_history(product_symbol => "product_symbol", start_time => "startTime") => get_funding_rate_history_with,
        get_l2book(product_symbol => "product_symbol") => get_l2book_with,
        get_meta() => get_meta_with,
        get_meta_and_asset_ctxs() => get_meta_and_asset_ctxs_with,
        get_spot_meta() => get_spot_meta_with,
        get_spot_meta_and_asset_ctxs() => get_spot_meta_and_asset_ctxs_with,
        historical_orders(user => "user") => historical_orders_with,
        open_orders(user => "user") => open_orders_with,
        order_status(user => "user", oid => "oid") => order_status_with,
        portfolio(user => "user") => portfolio_with,
        spot_clearinghouse_state(user => "user") => spot_clearinghouse_state_with,
        subaccounts(user => "user") => subaccounts_with,
        user_fills(user => "user") => user_fills_with,
        user_rate_limit(user => "user") => user_rate_limit_with,
        user_role(user => "user") => user_role_with,
        user_vault_equities(user => "user") => user_vault_equities_with
    ];
    private [
        cancel_order(product_symbol => "product_symbol", oid => "oid") => cancel_order_with,
        cancel_order_by_cloid(product_symbol => "product_symbol", cloid => "cloid") => cancel_order_by_cloid_with,
        cancel_twap_order(product_symbol => "product_symbol", twap_id => "twap_id") => cancel_twap_order_with,
        modify_batch_orders(modifies => "modifies") => modify_batch_orders_with,
        modify_order(oid => "oid", product_symbol => "product_symbol", is_buy => "isBuy", price => "price", size => "size", reduce_only => "reduceOnly") => modify_order_with,
        place_future_limit_buy_order(product_symbol => "product_symbol", price => "price", size => "size", tif => "tif") => place_future_limit_buy_order_with,
        place_future_limit_order(product_symbol => "product_symbol", is_buy => "isBuy", price => "price", size => "size", tif => "tif") => place_future_limit_order_with,
        place_future_limit_sell_order(product_symbol => "product_symbol", price => "price", size => "size", tif => "tif") => place_future_limit_sell_order_with,
        place_future_market_buy_order(product_symbol => "product_symbol", size => "size") => place_future_market_buy_order_with,
        place_future_market_order(product_symbol => "product_symbol", is_buy => "isBuy", size => "size") => place_future_market_order_with,
        place_future_market_sell_order(product_symbol => "product_symbol", size => "size") => place_future_market_sell_order_with,
        place_order(product_symbol => "product_symbol", is_buy => "isBuy", price => "price", size => "size", reduce_only => "reduceOnly") => place_order_with,
        place_twap_order(product_symbol => "product_symbol", is_buy => "isBuy", size => "size", reduce_only => "reduceOnly", minutes => "minutes", randomize => "randomize") => place_twap_order_with,
        schedule_cancel() => schedule_cancel_with,
        update_isolate_margin(product_symbol => "product_symbol", is_buy => "isBuy", ntli => "ntli") => update_isolate_margin_with,
        update_leverage(product_symbol => "product_symbol", is_cross => "isCross", leverage => "leverage") => update_leverage_with
    ];
}
