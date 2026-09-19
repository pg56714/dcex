use super::OndoClient;

crate::exchanges::impl_exchange_method_wrappers! {
    OndoClient;
    public [
        get_status(), hello(), ping(), get_markets(),
        get_trades(market => "market"), get_recent_trades(market => "market"),
        get_order_book_depth(market => "market"), get_depth(market => "market"),
        get_symbol_info(),
        get_price_history(symbol => "symbol", resolution => "resolution", from_time => "from", to_time => "to"),
        get_funding_rates(market => "market"), get_funding_rate_history(market => "market"),
        get_mark_prices(), get_open_interest(), get_volume(), get_contracts()
    ];
    private [
        get_account(), get_open_order_counts(), get_deposits(),
        get_deposit(deposit_id => "depositID"), get_withdrawals(),
        get_withdrawal_limits(), get_withdrawal(withdrawal_id => "withdrawalID"),
        get_deposit_addresses(coins => "coins"),
        export_deposits_csv(), export_withdrawals_csv(),
        get_address_book(), list_api_keys(), get_positions(), get_balance(),
        get_address_book_challenge(wallet_address => "walletAddress", chain_id => "chainId", withdrawal_address => "withdrawalAddress"),
        complete_address_book_challenge(id => "id", signature => "signature"),
        sandbox_deposit(amount => "amount", symbol => "symbol", deposit_destination => "deposit_destination", chain_id => "chain_id"),
        provision_deposit_address(network => "network", symbol => "symbol", deposit_destination => "deposit_destination"),
        get_withdrawal_status(),
        edit_address_book_entry(withdrawal_address => "withdrawalAddress"),
        remove_address_book_entry(withdrawal_address => "withdrawalAddress"),
        create_api_key(name => "name", scopes => "scopes"),
        delete_api_key(api_key_id => "apiKeyID"),
        set_api_key_ip_whitelist(api_key_id => "apiKeyID", ip => "ip"),
        remove_api_key_ip_whitelist(api_key_id => "apiKeyID", ip => "ip"),
        get_klines(market => "market", resolution => "resolution", from_time => "from", to_time => "to"),
        get_candles(market => "market", resolution => "resolution", from_time => "from", to_time => "to"),
        get_funding_fee_payments(), get_order_summaries(),
        get_max_order_size(market => "market"), get_liquidation_history(),
        get_leverage(), set_leverage(market => "market", leverage => "leverage"),
        get_portfolio_summary(), get_portfolio_summary_graph(),
        get_orders(), get_open_orders(), place_order(market => "market", side => "side"),
        cancel_all_orders(), cancel_open_orders(),
        place_batch_orders(orders => "orders"), batch_cancel_orders(order_ids => "orderIDs"),
        place_twap_order(market => "market", side => "side", size => "size", running_time => "runningTime", frequency => "frequency"),
        get_twap_order(order_id => "orderID"), cancel_twap_order(order_id => "orderID"),
        get_twap_order_fills(order_id => "orderID"), get_running_twap_orders(),
        get_twap_order_history(), get_order(order_id => "orderID"),
        cancel_order(order_id => "orderID"), export_orders_csv(),
        get_fills(), get_fills_by_order(order_id => "orderID"),
        export_fills_csv(), get_stop_orders(),
        set_stop_order(market => "market", position_direction => "positionDirection", stop_type => "type", trigger_price => "triggerPrice"),
        remove_stop_order(market => "market")
    ];
}
