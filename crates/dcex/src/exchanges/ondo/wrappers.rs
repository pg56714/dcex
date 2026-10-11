use super::OndoClient;

crate::exchanges::impl_exchange_method_wrappers! {
    OndoClient;
    public [
        get_login_challenge(wallet_address => "walletAddress", chain_id => "chainId"),
        complete_login_challenge(id => "id", signature => "signature"),
        get_status(), hello(), get_markets(),
        get_spot_depth(market => "market"), get_spot_trades(market => "market"),
        get_spot_symbol_info(), get_spot_ticker(),
        get_spot_price_history(symbol => "symbol", resolution => "resolution", to_time => "to"),
        get_trades(market => "market"),
        get_depth(market => "market"),
        get_symbol_info(),
        get_price_history(symbol => "symbol", resolution => "resolution", from_time => "from", to_time => "to"),
        get_funding_rates(market => "market"), get_funding_rate_history(market => "market"),
        get_mark_prices(), get_open_interest(), get_volume(), get_contracts()
    ];
    private [

        get_account(), get_open_order_counts(), get_deposits(),
        get_deposit(deposit_id => "depositID"), get_withdrawals(),
get_withdrawal(withdrawal_id => "withdrawalID"),
        get_deposit_addresses(coins => "coins"),
        export_deposits_csv(), export_withdrawals_csv(),
        get_address_book(), get_positions(), get_balance(),
        get_address_book_challenge(wallet_address => "walletAddress", chain_id => "chainId", withdrawal_address => "withdrawalAddress"),
        complete_address_book_challenge(id => "id", signature => "signature"),
        sandbox_deposit(amount => "amount", symbol => "symbol", deposit_destination => "deposit_destination", chain_id => "chain_id"),
        provision_deposit_address(network => "network", symbol => "symbol", deposit_destination => "deposit_destination"),

        edit_address_book_entry(withdrawal_address => "withdrawalAddress"),
        remove_address_book_entry(withdrawal_address => "withdrawalAddress"),
        get_klines(market => "market", resolution => "resolution", from_time => "from", to_time => "to"),
        get_candles(market => "market", resolution => "resolution", from_time => "from", to_time => "to"),
        get_funding_fee_payments(), get_order_summaries(),
        get_max_order_size(market => "market"), get_liquidation_history(),
        get_leverage(), set_leverage(market => "market", leverage => "leverage"),
        get_portfolio_summary(), get_portfolio_summary_graph(),
        get_orders(), get_open_orders(), place_order(market => "market", side => "side"),
        cancel_all_orders(), cancel_open_orders(),
batch_cancel_orders(order_ids => "orderIDs"),
        place_twap_order(market => "market", side => "side", size => "size", running_time => "runningTime", frequency => "frequency"),
        get_twap_order(order_id => "orderID"), cancel_twap_order(order_id => "orderID"),
        get_twap_order_fills(order_id => "orderID"), get_running_twap_orders(),
        get_twap_order_history(), get_order(order_id => "orderID"),
        cancel_order(order_id => "orderID"), export_orders_csv(),
        get_fills(), get_fills_by_order(order_id => "orderID"),
        export_fills_csv(), get_stop_orders(),
        set_stop_order(market => "market", position_direction => "positionDirection", stop_type => "type", trigger_price => "triggerPrice"),
        remove_stop_order(market => "market"),
        place_spot_order(market => "market", side => "side", size => "size"),
        place_spot_order_delayed(market => "market", side => "side", size => "size"),
        place_spot_batch_orders(orders => "orders"),
        place_spot_batch_orders_delayed(orders => "orders"),
        cancel_spot_batch_orders(order_ids => "orderIDs"),
        get_spot_orders(), cancel_spot_orders(),
        get_spot_order(order_id => "orderID"), cancel_spot_order(order_id => "orderID"),
        get_spot_order_fills(order_id => "orderID"), get_spot_fills(),
        export_spot_orders_csv(), export_spot_fills_csv(),
        get_spot_candles(market => "market", resolution => "resolution", to_time => "to"),
        get_spot_balances(), get_spot_transfers(),
        create_spot_transfer(from_wallet => "from", to_wallet => "to", symbol => "symbol", amount => "amount"),
        get_builder_code_stats(start_time => "startTime"), get_builder_code_fills()
    ];
}
