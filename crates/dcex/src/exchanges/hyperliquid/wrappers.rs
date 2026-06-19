use super::HyperliquidClient;

crate::exchanges::impl_exchange_method_wrappers! {
    HyperliquidClient;
    public [
        clearinghouse_state,
        get_candle_snapshot,
        get_funding_rate_history,
        get_l2book,
        get_meta,
        get_meta_and_asset_ctxs,
        get_spot_meta,
        get_spot_meta_and_asset_ctxs,
        historical_orders,
        open_orders,
        order_status,
        portfolio,
        spot_clearinghouse_state,
        subaccounts,
        user_fills,
        user_rate_limit,
        user_role,
        user_vault_equities
    ];
    private [
        cancel_order,
        cancel_order_by_cloid,
        cancel_twap_order,
        modify_batch_orders,
        modify_order,
        place_future_limit_buy_order,
        place_future_limit_order,
        place_future_limit_sell_order,
        place_future_market_buy_order,
        place_future_market_order,
        place_future_market_sell_order,
        place_order,
        place_twap_order,
        schedule_cancel,
        update_isolate_margin,
        update_leverage
    ];
}
