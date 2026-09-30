use super::client::ExtendedClient;

crate::exchanges::impl_exchange_method_wrappers!(
    ExtendedClient;
    public [
get_interest_rate_curves_history(interval => "interval"),
get_latest_interest_rate_curve(),
        get_markets(),
        get_assets(),
        get_asset_index_price(asset => "asset"),
        get_market_statistics(market => "market"),
        get_order_book(market => "market"),
        get_trades(market => "market"),
        get_candles(
            market => "market",
            interval => "interval",
            limit => "limit"
        ),
        get_funding(
            market => "market",
            start_time => "startTime",
            end_time => "endTime"
        ),
        get_open_interest(
            market => "market",
            interval => "interval",
            start_time => "startTime",
            end_time => "endTime"
        )
    ];
    private [
        /// API withdrawals and external transfers have no second confirmation; they execute on submit.
        create_withdrawal_signed(body => "body"),
        get_affiliate_data(), get_referral_status(), get_referral_links(),
        get_referral_dashboard(period => "period"),
        use_referral_code(code => "code"),
        create_referral_code(id => "id"), update_referral_code(id => "id"),
get_account_equity_history(account_id => "accountId",interval => "interval"),
get_account_pnl_history(account_id => "accountId",interval => "interval",pnl_type => "pnlType"),
get_account_pnl_percentage_history(account_id => "accountId",interval => "interval",pnl_type => "pnlType"),
get_cumulative_account_pnl_history(account_id => "accountId",interval => "interval",pnl_type => "pnlType"),
get_cumulative_account_pnl_percentage_history(account_id => "accountId",interval => "interval",pnl_type => "pnlType"),
get_account_vault_equity_history(account_id => "accountId",interval => "interval"),
get_account_max_drawdown_history(account_id => "accountId",interval => "interval"),
get_account_funding_chart(account_id => "accountId",interval => "interval"),
get_account_portfolio_summary(account_id => "accountId",interval => "interval"),
get_account_performance(account_id => "accountId",interval => "interval"),
get_account_funding_stats(account_id => "accountId",interval => "interval"),
get_account_funding_history(account_id => "accountId",interval => "interval"),
get_interest_key_metrics(account_id => "accountId"),
get_interest_daily_metrics(account_id => "accountId",interval => "interval"),
get_interest_payment_chart(account_id => "accountId",interval => "interval"),
get_interest_payments_history(account_id => "accountId",interval => "interval"),
        get_account_details(),
        get_sub_accounts(),
        get_balance(),
        get_asset_operations(),
        get_account_health(account_id => "accountId"),
        submit_internal_transfer(body => "body"),
        get_spot_balances(),
        get_positions(),
        get_positions_history(),
        get_open_orders(),
        get_orders_history(),
        get_order(id => "id"),
        get_order_by_external_id(external_id => "externalId"),
        get_trades_history(),
        get_funding_payments(start_time => "startTime"),
        get_leverage(),
        update_leverage(market => "market", leverage => "leverage"),
        get_fees(),
        get_rebates(),
        get_builder_dashboard(),
        get_builder_trades(),
        get_bridge_config(),
        commit_bridge_quote(quote_id => "id"),
        get_bridge_quote(
            chain_in => "chainIn",
            chain_out => "chainOut",
            amount => "amount"
        ),
        place_order(body => "body"),
        place_rfq_order(body => "body"),
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

crate::exchanges::impl_exchange_method_wrappers! { @extend; ExtendedClient; public [get_vault_performance(interval => "interval"),get_vault_summary()]; private [get_earned_points(),get_points_leaderboard_stats()]; }
