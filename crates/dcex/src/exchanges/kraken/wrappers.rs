use super::client::KrakenClient;

crate::exchanges::impl_exchange_method_wrappers! {
    KrakenClient;
    public [
get_futures_market_analytics(symbol => "symbol",analytics_type => "analytics_type",since => "since",interval => "interval"),
get_futures_ticker(symbol => "symbol"),
get_spot_post_trade_data(),
get_spot_pre_trade_data(symbol => "symbol"),
get_spot_grouped_orderbook(product_symbol => "product_symbol"),
get_spot_maintenance_schedule(),
get_futures_instrument_status(product_symbol => "product_symbol"),
get_futures_instrument_statuses(),
        get_futures_funding_history(product_symbol => "product_symbol"),
        get_futures_instruments(),
        get_futures_kline(product_symbol => "product_symbol", timeframe => "timeframe"),
        get_futures_orderbook(product_symbol => "product_symbol"),
        get_futures_public_trades(product_symbol => "product_symbol"),
        get_futures_tickers(),
        get_server_time(),
        get_spot_system_status(),
        get_spot_assets(),
        get_spot_asset_pairs(),
        get_spot_spread(product_symbol => "product_symbol"),
        get_spot_kline(product_symbol => "product_symbol"),
        get_spot_orderbook(product_symbol => "product_symbol"),
        get_spot_public_trades(product_symbol => "product_symbol"),
        get_spot_ticker(),
    ];
    private [
delete_spot_export_report(id => "id",report_action => "type"),
get_spot_export_status(report => "report"),
request_spot_export_report(report => "report",description => "description"),
simulate_futures_portfolio(portfolio => "json"),
check_futures_api_key(),
get_futures_pnl_preferences(),
set_futures_pnl_preference(symbol => "symbol",pnl_preference => "pnlPreference"),
create_spot_subaccount(username => "username",email => "email"),
get_futures_subaccounts(),
get_spot_api_key_info(),
get_spot_credit_lines(),
get_spot_order_amends(),
get_spot_wallet_accounts(),
get_spot_ledger_entries(ledger_ids => "id"),
get_futures_portfolio_margin_parameters(),
get_futures_unwind_queue(),
get_futures_notifications(),
get_futures_self_trade_strategy(),
set_futures_self_trade_strategy(strategy => "strategy"),
get_futures_trading_instruments(),
get_futures_subaccount_trading_status(subaccount_uid => "subaccountUid"),
set_futures_subaccount_trading_status(subaccount_uid => "subaccountUid",trading_enabled => "tradingEnabled"),
get_spot_trades_info(txid => "txid"),
get_futures_account_log_csv(),
get_futures_account_log(),
get_futures_execution_events(),
get_futures_order_events(),
get_futures_position_events(),
get_futures_trigger_events(),
get_spot_deposit_addresses(asset => "asset",method => "method"),
get_spot_deposit_methods(asset => "asset"),
transfer_spot_sub_account(asset => "asset",amount => "amount",from_account => "from",to_account => "to"),
transfer_futures_sub_account(from_user => "fromUser",to_user => "toUser",from_account => "fromAccount",to_account => "toAccount",unit => "unit",amount => "amount"),
get_spot_deposit_status(),
get_spot_level3_orderbook(product_symbol => "product_symbol"),
        manage_futures_batch_orders(orders => "orders"),
        place_spot_batch_orders(product_symbol => "product_symbol", orders => "orders"),
        cancel_spot_batch_orders(),
        get_spot_extended_balance(),
        get_futures_leverage_preferences(),
        set_futures_leverage_preference(product_symbol => "product_symbol", margin_mode => "margin_mode"),
        cancel_futures_all_orders(),
        cancel_futures_all_orders_after(timeout => "timeout"),
        cancel_futures_order(),
        edit_futures_order(order_id => "orderId"),
        cancel_spot_all_orders(),
        cancel_spot_all_orders_after(timeout => "timeout"),
        cancel_spot_order(),
        amend_spot_order(txid => "txid"),
        futures_wallet_transfer(amount => "amount", from_account => "fromAccount", to_account => "toAccount", unit => "unit"),
        get_futures_accounts(),
        get_futures_fills(),
        get_futures_open_orders(),
        get_futures_open_positions(),
        get_futures_order_status(),
        get_spot_account_balance(),
        get_spot_closed_orders(),
        get_spot_ledgers(),
        get_spot_open_orders(),
        get_spot_open_positions(),
        get_spot_orders(txid => "txid"),
        get_spot_trade_balance(),
        get_spot_trade_history(),
        get_spot_trade_volume(),
        get_spot_websocket_token(),
        get_earn_strategies(),
        get_earn_allocations(),
        allocate_earn_funds(strategy_id => "strategy_id", amount => "amount"),
        deallocate_earn_funds(strategy_id => "strategy_id", amount => "amount"),
        get_earn_allocation_status(strategy_id => "strategy_id"),
        get_earn_deallocation_status(strategy_id => "strategy_id"),
        place_futures_limit_buy_order(product_symbol => "product_symbol", size => "size", price => "price"),
        place_futures_limit_order(product_symbol => "product_symbol", side => "side", size => "size", price => "price"),
        place_futures_limit_sell_order(product_symbol => "product_symbol", size => "size", price => "price"),
        place_futures_market_buy_order(product_symbol => "product_symbol", size => "size"),
        place_futures_market_order(product_symbol => "product_symbol", side => "side", size => "size"),
        place_futures_market_sell_order(product_symbol => "product_symbol", size => "size"),
        place_futures_order(product_symbol => "product_symbol", side => "side", order_type => "orderType", size => "size"),
        place_futures_post_only_limit_buy_order(product_symbol => "product_symbol", size => "size", price => "price"),
        place_futures_post_only_limit_order(product_symbol => "product_symbol", side => "side", size => "size", price => "price"),
        place_futures_post_only_limit_sell_order(product_symbol => "product_symbol", size => "size", price => "price"),
        place_spot_limit_buy_order(product_symbol => "product_symbol", volume => "volume", price => "price"),
        place_spot_limit_order(product_symbol => "product_symbol", side => "side", volume => "volume", price => "price"),
        place_spot_limit_sell_order(product_symbol => "product_symbol", volume => "volume", price => "price"),
        place_spot_market_buy_order(product_symbol => "product_symbol", volume => "volume"),
        place_spot_market_order(product_symbol => "product_symbol", side => "side", volume => "volume"),
        place_spot_market_sell_order(product_symbol => "product_symbol", volume => "volume"),
        place_spot_order(product_symbol => "product_symbol", side => "side", ordertype => "ordertype", volume => "volume"),
        place_spot_post_only_limit_buy_order(product_symbol => "product_symbol", volume => "volume", price => "price"),
        place_spot_post_only_limit_order(product_symbol => "product_symbol", side => "side", volume => "volume", price => "price"),
        place_spot_post_only_limit_sell_order(product_symbol => "product_symbol", volume => "volume", price => "price"),
        wallet_transfer_to_futures(asset => "asset", amount => "amount"),
        /// API withdrawals and external transfers have no second confirmation; they execute on submit.
        withdraw_futures_to_spot_wallet(amount => "amount", currency => "currency"),
    ];
}

crate::exchanges::impl_exchange_method_wrappers! {@extend;KrakenClient;public [];private [get_withdrawal_addresses(),
get_withdrawal_information(asset => "asset",key => "key",amount => "amount"),
get_withdrawal_methods(),
get_withdrawal_status(),];}

crate::exchanges::impl_exchange_method_wrappers! {@extend;KrakenClient;public [];private [edit_spot_order(pair => "pair",txid => "txid")];}

crate::exchanges::impl_exchange_method_wrappers! {@extend;KrakenClient;public [get_futures_chart_types()];private [];}

crate::exchanges::impl_exchange_method_wrappers! {@extend;KrakenClient;public [get_futures_chart_markets(tick_type => "tick_type")];private [];}

crate::exchanges::impl_exchange_method_wrappers! {@extend;KrakenClient;public [get_futures_chart_resolutions(tick_type => "tick_type",symbol => "symbol")];private [];}

crate::exchanges::impl_exchange_method_wrappers! {@extend;KrakenClient;public [get_futures_market_executions(tradeable => "tradeable")];private [];}

crate::exchanges::impl_exchange_method_wrappers! {@extend;KrakenClient;public [get_futures_market_orders(tradeable => "tradeable")];private [];}

crate::exchanges::impl_exchange_method_wrappers! {@extend;KrakenClient;public [get_futures_market_price(tradeable => "tradeable")];private [];}

crate::exchanges::impl_exchange_method_wrappers! {@extend;KrakenClient;public [get_futures_liquidity_pool_statistics(since => "since",interval => "interval")];private [];}

mod business_methods {
    use crate::exchanges::kraken::KrakenClient;
    crate::exchanges::impl_exchange_method_wrappers! {
        @extend; KrakenClient; public []; private [
            get_affiliate_daily_activity(),
            add_assignment_program(contract_type => "contractType", accept_long => "acceptLong", accept_short => "acceptShort", time_frame => "timeFrame", enabled => "enabled"),
            delete_assignment_program(assignment_id => "id"),
            get_assignment_program_history(),
            get_assignment_program_current(),
            calculate_funding_fees(method_id => "method_id", amount => "amount"),
            claim_funding_deposit_address(body => "body"),
            create_funding_address(body => "body"),
            /// API withdrawals and external transfers have no second confirmation; they execute on submit.
            create_funding_withdrawal(body => "body"),
            delete_funding_address(address_id => "id"),
            get_funding_addresses(),
            get_funding_assets(direction => "direction"),
            get_funding_deposit_addresses(),
            get_funding_deposit_limits(asset_class => "asset_class", asset => "asset"),
            get_funding_deposits(),
            get_funding_methods(direction => "direction"),
            get_funding_networks(),
            get_funding_withdrawal_limits(asset_class => "asset_class", asset => "asset"),
            get_funding_withdrawals(),
            update_funding_address(address_id => "id", body => "body"),
            cancel_spot_withdrawal(asset => "asset", refid => "refid"),
            /// API withdrawals and external transfers have no second confirmation; they execute on submit.
            create_spot_withdrawal(asset => "asset", key => "key", amount => "amount"),
            accept_rfq_offer(rfq_uid => "rfqUid"),
            cancel_user_rfq(rfq_uid => "rfqUid"),
            cancel_rfq_offer(rfq_uid => "rfqUid"),
            create_user_rfq(request => "json"),
            get_open_rfqs(),
            get_closed_rfq_offers(),
            get_open_rfq_offers(),
            get_open_rfqs_for_account(),
            place_rfq_offer(rfq_uid => "rfqUid"),
            get_rfq(rfq_uid => "rfqUid"),
            delete_rfq_assignment_max_leverage(),
            get_rfq_assignment_max_leverage(),
            update_rfq_assignment_max_leverage(max_leverage => "maxLeverage"),
        ];
    }
}
