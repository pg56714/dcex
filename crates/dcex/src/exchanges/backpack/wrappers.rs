use super::BackpackClient;

crate::exchanges::impl_exchange_method_wrappers! {
    BackpackClient;
    public [
        get_assets(),
        get_collateral(),
        get_borrow_lend_markets(),
        get_borrow_lend_market_history(interval => "interval"),
        get_borrow_lend_apy(),
        get_borrow_lend_liquidation_price(borrow => "borrow"),
        get_markets(),
        get_market(product_symbol => "product_symbol"),
        get_order_book_depth(product_symbol => "product_symbol"),
        get_market_sessions(),
        get_market_holidays(),
        get_securities(),
        get_rfq_constraints(product_symbol => "product_symbol", session_name => "sessionName"),
        get_mark_prices(),
        get_open_interest(),
        get_funding_rates(product_symbol => "product_symbol"),
        get_klines(product_symbol => "product_symbol", interval => "interval", start_time => "startTime"),
        get_ticker(product_symbol => "product_symbol"),
        get_tickers(),
        get_status(),
        ping(),
        get_time(),
        get_wallets(),
        get_recent_trades(product_symbol => "product_symbol"),
        get_historical_trades(product_symbol => "product_symbol")
    ];
    private [
        create_strategy(product_symbol => "product_symbol", side => "side", strategy_type => "strategyType"),
        get_open_strategy(product_symbol => "product_symbol"),
        cancel_strategy(product_symbol => "product_symbol"),
        get_open_strategies(),
        cancel_open_strategies(),
        get_strategy_history(),
        get_account(),
        update_account(),
        get_max_borrow_quantity(symbol => "symbol"),
        get_max_order_quantity(symbol => "symbol", side => "side"),
        get_max_withdrawal_quantity(symbol => "symbol"),
        get_borrow_lend_positions(),
        get_borrow_history(),
        get_interest_history(),
        get_borrow_position_history(),
        get_balances(),
        convert_dust(symbol => "symbol"),
        get_private_collateral(),
        get_deposits(),
        get_deposit_address(blockchain => "blockchain"),
        get_withdrawals(),
        get_dust_conversion_history(),
        get_settlement_history(),
        get_open_order(product_symbol => "product_symbol"),
        place_order(product_symbol => "product_symbol", side => "side", order_type => "orderType"),
        place_market_order(product_symbol => "product_symbol", side => "side"),
        place_limit_order(product_symbol => "product_symbol", side => "side", quantity => "quantity", price => "price"),
        cancel_order(product_symbol => "product_symbol"),
        place_batch_orders(orders => "orders"),
        get_open_orders(),
        cancel_open_orders(),
        get_fill_history(),
        get_order_history(),
        get_open_positions(),
        get_funding_payments(),
        get_position_history()
    ];
}

crate::exchanges::impl_exchange_method_wrappers! { @extend; BackpackClient; public [
get_prediction_events(),
get_prediction_tags(),
get_vaults(),
get_vault_history(interval => "interval"),
]; private [
vault_mint(vault_id => "vaultId",symbol => "symbol",quantity => "quantity"),
vault_redeem(vault_id => "vaultId"),
vault_redeem_cancel(vault_id => "vaultId"),
get_vault_pending_redeems(vault_id => "vaultId"),
get_vault_nav(),
]; }

crate::exchanges::impl_exchange_method_wrappers! {@extend;BackpackClient;public [];private [execute_borrow_lend(quantity => "quantity",side => "side",symbol => "symbol")];}
