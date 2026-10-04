use super::client::BitgetClient;

crate::exchanges::impl_exchange_method_wrappers! {
    BitgetClient;
    public [
        get_classic_margin_currencies(),
        get_classic_auction(product_symbol => "product_symbol"),
        get_classic_vip_fee_rate(),
        get_uta_proof_of_reserves(),
        get_uta_score_weights(),
        get_uta_fee_group(category => "category"),
        get_uta_spot_fund_flow(product_symbol => "product_symbol"),
        get_uta_spot_net_flow(product_symbol => "product_symbol"),
        get_uta_margin_long_short(product_symbol => "product_symbol"),
        get_uta_margin_loan_growth(product_symbol => "product_symbol"),
        get_uta_margin_isolated_borrow(product_symbol => "product_symbol"),
        get_uta_futures_active_buy_sell(product_symbol => "product_symbol"),
        get_uta_futures_long_short(product_symbol => "product_symbol"),
        get_uta_futures_position_long_short(product_symbol => "product_symbol"),
        get_uta_cash_dividend_records(product_symbol => "product_symbol", type_ => "type"),
        get_uta_risk_reserve(category => "category", product_symbol => "product_symbol"),
        get_uta_all_risk_reserves(category => "category"),
        get_uta_hourly_risk_reserve(category => "category", product_symbol => "product_symbol"),
        get_uta_split_records(),
        get_uta_futures_long_short_ratio(product_symbol => "product_symbol"),
        get_uta_spot_whale_flow(product_symbol => "product_symbol"),
        get_server_time(),

        get_futures_trade_history(product_symbol => "product_symbol", product_type => "productType"),
        get_futures_index_candle_history(product_symbol => "product_symbol", product_type => "productType", granularity => "granularity"),
        get_futures_mark_candle_history(product_symbol => "product_symbol", product_type => "productType", granularity => "granularity"),
        get_futures_next_funding_time(product_symbol => "product_symbol", product_type => "productType"),
        get_futures_interest_exchange_rates(),
        get_futures_interest_rate_history(coin => "coin"),
        get_futures_vip_fee_rates(),
        get_uta_funding_rate_history(category => "category", product_symbol => "product_symbol"),
        get_uta_index_components(product_symbol => "product_symbol"),
        get_uta_margin_loan_rates(coin => "coin"),
        get_uta_position_tiers(category => "category"),
        get_uta_open_interest_limit(category => "category"),
        get_uta_discount_rates(),
        get_uta_rpi_orderbook(category => "category", product_symbol => "product_symbol"),
        get_uta_rpi_symbols(),
        get_futures_symbol_price(product_symbol => "product_symbol", product_type => "productType"),
        get_uta_open_interest(category => "category"),
        get_uta_current_funding_rate(),

        get_uta_liquidations(product_symbol => "product_symbol"),
        get_uta_instruments(category => "category"),
        get_uta_tickers(category => "category"),
        get_uta_orderbook(category => "category", product_symbol => "product_symbol"),
        get_uta_public_fills(category => "category", product_symbol => "product_symbol"),
        get_uta_kline(category => "category", product_symbol => "product_symbol", interval => "interval"),
        get_uta_history_kline(category => "category", product_symbol => "product_symbol", interval => "interval"),
        get_reality_stock_info(),
        get_reality_market_states(),
        get_reality_market_calendar(),
        get_spot_coins(),
        get_spot_market_trades(product_symbol => "product_symbol"),
    ];
    private [
        get_uta_deposit_address(coin => "coin"),
        get_uta_sub_deposit_address(sub_uid => "subUid", coin => "coin"),
        get_uta_sub_deposit_records(sub_uid => "subUid", start_time => "startTime", end_time => "endTime"),
        get_uta_rate_limit_quota(category => "category"),
        uta_set_rate_limit_quota(category => "category", uids => "uids", quota => "quota"),
        get_uta_small_assets_history(),
        get_uta_small_assets(),
        convert_uta_small_assets(from_coin_list => "fromCoinList"),
        delete_uta_subaccount(sub_uid => "subUid"),
        uta_freeze_sub(sub_uid => "subUid", operation => "operation"),
        uta_create_sub_api(sub_uid => "subUid", note => "note", type_ => "type", passphrase => "passphrase", permissions => "permissions", ips => "ips"),
        uta_update_sub_api(api_key => "apiKey", passphrase => "passphrase"),
        uta_delete_sub_api(api_key => "apiKey"),
        get_uta_sub_api_list(sub_uid => "subUid"),
        set_uta_fee_deduction(deduct => "deduct"),
        get_uta_fee_deduction(),
        switch_to_classic_account(),
        get_account_switch_status(),
        set_uta_deposit_account(coin => "coin", account_type => "accountType"),
        create_uta_sub_account(username => "username"),
        get_uta_strategy_sub_orders(order_id => "orderId"),
        get_uta_deposit_records(start_time => "startTime", end_time => "endTime"),




        get_uta_sub_accounts(),
        get_uta_sub_account_assets(),











        get_uta_funding_assets(),
        get_uta_funding_records(),
        get_uta_fee_rate(product_symbol => "product_symbol", category => "category"),

        set_uta_collateral_type(collateral_type => "collateralType"),
        get_uta_settings(),
        get_uta_delta_info(),
        get_uta_repayable_coins(),
        get_uta_payment_coins(),
        borrow_uta_asset(coin => "coin", amount => "amount"),
        get_uta_max_borrowable(coin => "coin"),
        get_uta_account_open_interest_limit(product_symbol => "product_symbol", category => "category"),

        get_uta_max_open_available(category => "category", product_symbol => "product_symbol", order_type => "orderType", side => "side"),

        set_uta_repay_mode(repay_mode => "repayMode"),
        get_uta_eligible_discount_rates(),
        get_uta_eligible_loan_info(),
        get_uta_eligible_margin_tiers(),
        get_uta_eligible_symbols(),
        get_uta_convert_records(),
        set_uta_account_mode(mode => "mode"),
        get_uta_adl_rank(),
        modify_uta_order(product_symbol => "product_symbol", category => "category"),
        cancel_uta_orders_by_symbol(category => "category"),
        set_uta_cancel_countdown(countdown => "countdown"),
        close_uta_positions(category => "category"),
        get_uta_position_history(category => "category"),
        adjust_uta_position_margin(category => "category", product_symbol => "product_symbol", pos_side => "posSide", operation => "operation", amount => "amount"),
        get_uta_financial_records(category => "category"),




        cancel_uta_order(),


        get_uta_account_assets(),
        get_reality_orderbook(product_symbol => "product_symbol"),
        get_reality_fills(product_symbol => "product_symbol"),
        get_uta_account_info(),
        get_uta_all_fee_rates(category => "category"),
        get_uta_loan_data(),
        get_crypto_loan_coins(),
        get_crypto_loan_interest(loan_coin => "loanCoin", pledge_coin => "pledgeCoin", daily => "daily", pledge_amount => "pledgeAmount"),
        borrow_crypto_loan(loan_coin => "loanCoin", pledge_coin => "pledgeCoin", daily => "daily"),
        get_crypto_loan_ongoing(),
        get_crypto_loan_borrow_history(start_time => "startTime", end_time => "endTime"),
        repay_crypto_loan(order_id => "orderId", repay_all => "repayAll"),
        get_crypto_loan_repay_history(start_time => "startTime", end_time => "endTime"),
        revise_crypto_loan_pledge(order_id => "orderId", amount => "amount", pledge_coin => "pledgeCoin", revise_type => "reviseType"),
        get_crypto_loan_pledge_history(start_time => "startTime", end_time => "endTime"),
        get_crypto_loan_liquidations(start_time => "startTime", end_time => "endTime"),
        get_crypto_loan_debts(),
        get_elite_earn_products(),
        get_elite_earn_subscription_info(product_id => "productId"),
        subscribe_elite_earn(product_sub_id => "productSubId", amount => "amount"),
        get_elite_earn_subscription_result(order_id => "orderId"),
        get_elite_earn_redemption_info(product_id => "productId"),
        redeem_elite_earn(product_id => "productId", product_sub_id => "productSubId", redeem_type => "redeemType", amount => "amount", receive_account => "receiveAccount"),
        get_elite_earn_assets(),
        get_elite_earn_records(record_type => "type"),
        repay_uta_liability(repayable_coin_list => "repayableCoinList", payment_coin_list => "paymentCoinList"),
        get_uta_collateral_type(),
        get_uta_custom_collateral_coins(),
        get_uta_pre_set_leverage(category => "category", margin_mode => "marginMode"),
        get_uta_fills(),
        get_uta_history_orders(category => "category"),
        get_uta_open_orders(),
        get_uta_order(),
        get_uta_positions(category => "category"),
        place_uta_strategy_order(category => "category", product_symbol => "product_symbol"),
        modify_uta_strategy_order(qty => "qty"),
        cancel_uta_strategy_order(),
        get_uta_unfilled_strategy_orders(category => "category"),
        get_uta_history_strategy_orders(category => "category"),



        place_uta_order(category => "category", product_symbol => "product_symbol", side => "side", order_type => "orderType", qty => "qty"),
        place_reality_order(product_symbol => "product_symbol", side => "side", order_type => "orderType", qty => "qty"),
        cancel_reality_order(product_symbol => "product_symbol"),
        set_uta_hold_mode(hold_mode => "holdMode"),
        set_uta_leverage(category => "category", leverage => "leverage"),

    ];
}

crate::exchanges::impl_exchange_method_wrappers! { @extend; BitgetClient; public []; private [move_uta_positions(from_uid => "fromUid", to_uid => "toUid", category => "category", position_list => "positionList")]; }

crate::exchanges::impl_exchange_method_wrappers! { @extend; BitgetClient; public [
get_classic_earn_loan_public_coin_infos(),
get_classic_earn_loan_public_hour_interest(loan_coin => "loanCoin",pledge_coin => "pledgeCoin",daily => "daily",pledge_amount => "pledgeAmount"),
]; private [
get_uta_account_max_withdrawal(coin => "coin"),
get_uta_account_withdrawal_records(start_time => "startTime",end_time => "endTime"),
get_uta_account_withdraw_address(),
uta_trade_grid_add_investment(category => "category",bot_id => "botId",coin => "coin",size => "size",funds_source => "fundsSource"),
get_uta_trade_grid_bot_detail(bot_id => "botId"),
uta_trade_grid_close_bot(bot_id => "botId"),
uta_trade_grid_create_bot(category => "category",symbol => "symbol",max_price => "maxPrice",min_price => "minPrice",grid_num => "gridNum",grid_order_mode => "gridOrderMode",investment_amount => "investmentAmount",funds_source => "fundsSource",slippage => "slippage",auto_transfer_profits => "autoTransferProfits"),
uta_trade_grid_create_neutral_bot(category => "category",symbol => "symbol",max_price => "maxPrice",min_price => "minPrice",grid_num => "gridNum",grid_order_mode => "gridOrderMode",funds_source => "fundsSource"),
get_uta_trade_grid_list_details(category => "category",bot_id => "botId"),
uta_trade_grid_modify_bot(bot_id => "botId"),
uta_trade_grid_modify_grid_interval(category => "category",bot_id => "botId",max_price => "maxPrice",min_price => "minPrice",grid_num => "gridNum"),
uta_trade_grid_modify_neutral_bot(bot_id => "botId",category => "category"),
uta_trade_grid_modify_neutral_grid_interval(category => "category",bot_id => "botId",max_price => "maxPrice",min_price => "minPrice",grid_num => "gridNum"),
get_uta_trade_grid_neutral_bot_detail(bot_id => "botId"),
get_uta_trade_grid_neutral_list_details(category => "category",bot_id => "botId"),
uta_trade_grid_validate_neutral(category => "category",symbol => "symbol",max_price => "maxPrice",min_price => "minPrice",grid_num => "gridNum",grid_order_mode => "gridOrderMode"),
uta_trade_grid_validate(category => "category",symbol => "symbol",max_price => "maxPrice",min_price => "minPrice",grid_num => "gridNum",grid_order_mode => "gridOrderMode",investment_amount => "investmentAmount",auto_transfer_profits => "autoTransferProfits"),
]; }

crate::exchanges::impl_exchange_method_wrappers! { @extend; BitgetClient; public [
get_reality_company_overview(code => "code"),
get_reality_valuation_indicators(code => "code"),
get_reality_earnings_forecast(code => "code"),
get_reality_suspension_resumption_info(code => "code"),
get_reality_dividends(code => "code"),
get_reality_share_capital_change(code => "code"),
get_reality_inner_trades(code => "code"),
get_reality_executive_shareholdings(code => "code"),
get_reality_sharehold_detail(code => "code"),
]; private [

]; }

mod business_methods {
    use crate::exchanges::bitget::client::BitgetClient;

    crate::exchanges::impl_exchange_method_wrappers! {
        @extend; BitgetClient; public []; private [
            create_uta_agent_sub_account(username => "username", passphrase => "passphrase"),
            /// API withdrawals and external transfers have no second confirmation; they execute on submit.
            create_uta_withdrawal(coin => "coin", transfer_type => "transferType", address => "address", size => "size"),
            cancel_uta_withdrawal(),
        ];
    }
}
