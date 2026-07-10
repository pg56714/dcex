use super::client::ExtendedClient;

crate::exchanges::impl_exchange_method_wrappers!(
    ExtendedClient;
    public [
        get_markets(),
        get_assets(),
        get_asset_index_price(asset => "asset"),
        get_market_statistics(market => "market"),
        get_order_book(market => "market"),
        get_trades(market => "market"),
        get_candles(market => "market"),
        get_funding(market => "market"),
        get_open_interest(market => "market")
    ];
    private [
        get_account_details(),
        get_sub_accounts(),
        get_balance(),
        get_spot_balances(),
        get_positions(),
        get_positions_history(),
        get_open_orders(),
        get_orders_history(),
        get_order(id => "id"),
        get_order_by_external_id(external_id => "externalId"),
        get_orders_by_external_id(external_id => "externalId"),
        get_trades_history(),
        get_funding_payments(),
        get_leverage(),
        get_fees(),
        place_order(body => "body"),
        place_limit_order(
            market => "market",
            side => "side",
            qty => "qty",
            price => "price"
        ),
        sign_create_order(
            market => "market",
            side => "side",
            qty => "qty",
            price => "price"
        ),
        cancel_order(id => "id"),
        cancel_order_by_external_id(external_id => "externalId"),
        mass_cancel(body => "body"),
        set_deadmanswitch(countdown_time => "countdownTime")
    ];
);
