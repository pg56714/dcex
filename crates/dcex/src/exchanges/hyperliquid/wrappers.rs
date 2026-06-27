use super::HyperliquidClient;

crate::exchanges::impl_exchange_method_wrappers! {
    HyperliquidClient;
    public [
        clearinghouse_state(user => "user"),
        get_candle_snapshot(product_symbol => "product_symbol", interval => "interval", start_time => "startTime"),
        get_funding_rate_history(product_symbol => "product_symbol", start_time => "startTime"),
        get_l2book(product_symbol => "product_symbol"),
        get_meta(),
        get_meta_and_asset_ctxs(),
        get_spot_meta(),
        get_spot_meta_and_asset_ctxs(),
        historical_orders(user => "user"),
        open_orders(user => "user"),
        order_status(user => "user", oid => "oid"),
        portfolio(user => "user"),
        spot_clearinghouse_state(user => "user"),
        subaccounts(user => "user"),
        user_fills(user => "user"),
        user_rate_limit(user => "user"),
        user_role(user => "user"),
        user_vault_equities(user => "user")
    ];
    private [
        cancel_order(product_symbol => "product_symbol", oid => "oid"),
        cancel_order_by_cloid(product_symbol => "product_symbol", cloid => "cloid"),
        cancel_twap_order(product_symbol => "product_symbol", twap_id => "twap_id"),
        modify_batch_orders(modifies => "modifies"),
        modify_order(oid => "oid", product_symbol => "product_symbol", is_buy => "isBuy", price => "price", size => "size", reduce_only => "reduceOnly"),
        place_future_limit_buy_order(product_symbol => "product_symbol", price => "price", size => "size", tif => "tif"),
        place_future_limit_order(product_symbol => "product_symbol", is_buy => "isBuy", price => "price", size => "size", tif => "tif"),
        place_future_limit_sell_order(product_symbol => "product_symbol", price => "price", size => "size", tif => "tif"),
        place_future_market_buy_order(product_symbol => "product_symbol", size => "size"),
        place_future_market_order(product_symbol => "product_symbol", is_buy => "isBuy", size => "size"),
        place_future_market_sell_order(product_symbol => "product_symbol", size => "size"),
        place_order(product_symbol => "product_symbol", is_buy => "isBuy", price => "price", size => "size", reduce_only => "reduceOnly"),
        place_twap_order(product_symbol => "product_symbol", is_buy => "isBuy", size => "size", reduce_only => "reduceOnly", minutes => "minutes", randomize => "randomize"),
        schedule_cancel(),
        update_isolate_margin(product_symbol => "product_symbol", is_buy => "isBuy", ntli => "ntli"),
        update_leverage(product_symbol => "product_symbol", is_cross => "isCross", leverage => "leverage")
    ];
}
