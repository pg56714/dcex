use super::client::MexcClient;

crate::exchanges::impl_exchange_method_wrappers! {
    MexcClient;
    public [
        get_contract_deals(product_symbol => "product_symbol"),
        get_contract_depth(product_symbol => "product_symbol"),
        get_contract_depth_commits(product_symbol => "product_symbol", limit => "limit"),
        get_contract_details(),
        get_all_contract_details(),
        get_contract_fair_price(product_symbol => "product_symbol"),
        get_contract_fair_price_kline(product_symbol => "product_symbol"),
        get_contract_funding_rate(product_symbol => "product_symbol"),
        get_contract_funding_rate_history(product_symbol => "product_symbol"),
        get_contract_index_price(product_symbol => "product_symbol"),
        get_contract_index_price_kline(product_symbol => "product_symbol"),
        get_contract_kline(product_symbol => "product_symbol"),
        get_contract_risk_reverse(product_symbol => "product_symbol"),
        get_contract_risk_reverse_history(product_symbol => "product_symbol"),
        get_contract_ticker(),
        get_contract_time(),
        get_spot_agg_trades(product_symbol => "product_symbol"),
        get_spot_avg_price(product_symbol => "product_symbol"),
        get_spot_book_ticker(),
        get_spot_default_symbols(),
        get_spot_exchange_info(),
        get_spot_klines(product_symbol => "product_symbol", interval => "interval"),
        get_spot_orderbook(product_symbol => "product_symbol"),
        get_spot_recent_trades(product_symbol => "product_symbol"),
        get_spot_ticker_24hr(),
        get_spot_ticker_price(),
        get_spot_time(),
        ping(),
    ];
    private [
cancel_contract_batch_orders_by_external_id(orders => "orders"),
get_contract_batch_orders_by_external_id(orders => "orders"),
get_contract_closed_orders(product_symbol => "product_symbol"),
get_contract_fee_details(product_symbol => "product_symbol"),
get_contract_30_day_fee_statistics(),
        cancel_spot_all_orders(),
        get_contract_open_stop_orders(),
        cancel_all_contract_orders(),
        amend_contract_limit_order(order_id => "orderId", price => "price", vol => "vol"),
        chase_contract_limit_order(order_id => "orderId"),
        get_contract_open_order_count(),
        reverse_contract_position(product_symbol => "product_symbol", position_id => "positionId", vol => "vol"),
        close_all_contract_positions(),
        place_contract_trailing_order(product_symbol => "product_symbol", leverage => "leverage", side => "side", vol => "vol", open_type => "openType", trend => "trend", back_type => "backType", back_value => "backValue", position_mode => "positionMode"),
        cancel_contract_trailing_order(),
        amend_contract_trailing_order(product_symbol => "product_symbol", track_order_id => "trackOrderId", trend => "trend", back_type => "backType", back_value => "backValue", vol => "vol"),
        get_contract_trailing_orders(states => "states"),
        amend_contract_plan_order(product_symbol => "product_symbol", order_id => "orderId", trigger_price => "triggerPrice", price => "price", order_type => "orderType", trigger_type => "triggerType", trend => "trend", from => "from"),
        place_contract_position_tpsl(loss_trend => "lossTrend", profit_trend => "profitTrend", position_id => "positionId", vol => "vol"),
        cancel_contract_tpsl_orders(orders => "orders"),
        cancel_all_contract_tpsl_orders(),
        amend_contract_limit_tpsl(order_id => "orderId"),
        amend_contract_tpsl_order(stop_plan_order_id => "stopPlanOrderId"),
        amend_contract_plan_tpsl(product_symbol => "product_symbol", order_id => "orderId"),
        cancel_contract_order(order_id => "order_id"),
        cancel_contract_order_with_external_id(product_symbol => "product_symbol", external_oid => "externalOid"),
        cancel_contract_orders(orders => "orders"),
        cancel_spot_open_orders(product_symbol => "product_symbol"),
        cancel_spot_order(product_symbol => "product_symbol"),
        change_contract_leverage(leverage => "leverage"),
        change_contract_margin(position_id => "positionId", amount => "amount", type_ => "type"),
        change_contract_auto_add_margin(position_id => "positionId", is_enabled => "isEnabled"),
        change_contract_position_mode(position_mode => "positionMode"),
        change_contract_multi_asset_mode(is_multi_asset_mode => "isMultiAssetMode"),
        get_contract_asset(currency => "currency"),
        get_contract_assets(),
        get_contract_funding_records(),
        get_contract_history_orders(),
        get_contract_history_positions(),
        get_contract_leverage(product_symbol => "product_symbol"),
        get_contract_open_orders(),
        get_contract_open_positions(),
        get_contract_order(order_id => "order_id"),
        get_contract_order_by_external_id(product_symbol => "product_symbol", external_oid => "external_oid"),
        get_contract_order_deal_details(order_id => "order_id"),
        get_contract_order_deals(product_symbol => "product_symbol"),
        get_contract_orders(order_ids => "order_ids"),
        get_contract_plan_orders(),
        place_contract_plan_order(product_symbol => "product_symbol", vol => "vol", leverage => "leverage", side => "side", open_type => "openType", trigger_price => "triggerPrice", trigger_type => "triggerType", execute_cycle => "executeCycle", order_type => "orderType", trend => "trend"),
        cancel_contract_plan_orders(orders => "orders"),
        cancel_all_contract_plan_orders(),
        get_contract_position_mode(),
        get_contract_risk_limits(),
        get_contract_stop_orders(),
        get_contract_trading_fee_rate(),

        get_currency_info(),
        get_deposit_address(coin => "coin"),
        get_deposit_history(),

        get_kyc_status(),
        get_spot_account(),
        get_spot_all_orders(product_symbol => "product_symbol"),
        get_spot_mx_deduct_status(),
        get_spot_my_trades(product_symbol => "product_symbol"),
        get_spot_open_orders(),
        get_spot_order(),
        get_spot_self_symbols(),
        get_spot_symbol_commission(product_symbol => "product_symbol"),
        get_subaccount_asset(sub_account => "subAccount", account_type => "accountType"),

        get_subaccounts(),



        place_contract_limit_buy_order(product_symbol => "product_symbol", price => "price", vol => "vol", open_type => "openType"),
        place_contract_limit_order(product_symbol => "product_symbol", side => "side", price => "price", vol => "vol", open_type => "openType"),
        place_contract_limit_sell_order(product_symbol => "product_symbol", price => "price", vol => "vol", open_type => "openType"),
        place_contract_market_buy_order(product_symbol => "product_symbol", vol => "vol", open_type => "openType"),
        place_contract_market_order(product_symbol => "product_symbol", side => "side", vol => "vol", open_type => "openType"),
        place_contract_market_sell_order(product_symbol => "product_symbol", vol => "vol", open_type => "openType"),
        place_contract_order(product_symbol => "product_symbol", side => "side", type_ => "type", open_type => "openType", vol => "vol"),
        place_contract_post_only_buy_order(product_symbol => "product_symbol", price => "price", vol => "vol", open_type => "openType"),
        place_contract_post_only_order(product_symbol => "product_symbol", side => "side", price => "price", vol => "vol", open_type => "openType"),
        place_contract_post_only_sell_order(product_symbol => "product_symbol", price => "price", vol => "vol", open_type => "openType"),

        place_spot_limit_buy_order(product_symbol => "product_symbol", quantity => "quantity", price => "price"),
        place_spot_limit_order(product_symbol => "product_symbol", side => "side", quantity => "quantity", price => "price"),
        place_spot_limit_sell_order(product_symbol => "product_symbol", quantity => "quantity", price => "price"),
        place_spot_market_buy_order(product_symbol => "product_symbol", quote_order_qty => "quoteOrderQty"),
        place_spot_market_order(product_symbol => "product_symbol", side => "side"),
        place_spot_market_sell_order(product_symbol => "product_symbol", quantity => "quantity"),
        place_spot_order(product_symbol => "product_symbol", side => "side", type_ => "type"),
        place_spot_post_only_limit_buy_order(product_symbol => "product_symbol", quantity => "quantity", price => "price"),
        place_spot_post_only_limit_order(product_symbol => "product_symbol", side => "side", quantity => "quantity", price => "price"),
        place_spot_post_only_limit_sell_order(product_symbol => "product_symbol", quantity => "quantity", price => "price"),
        set_spot_mx_deduct(mx_deduct_enable => "mxDeductEnable"),
        test_spot_order(product_symbol => "product_symbol", side => "side", type_ => "type"),


    ];
}

crate::exchanges::impl_exchange_method_wrappers! { @extend; MexcClient; public [
get_spot_offline_symbols(),
get_announcements(),
get_contract_supported_currencies(),
]; private [
get_uid(),
get_api_key_info(access_key => "accessKey"),
set_api_key_ip_whitelist(api_key => "apiKey",ip_whitelist => "ipWhiteList"),
get_convertible_assets(),
convert_dust(assets => "asset"),
get_dust_conversion_history(),
create_sub_account(sub_account => "subAccount",note => "note"),
get_contract_profit_rate(period_type => "type"),
get_contract_fee_deduction_config(),
get_contract_fee_discount_config(),
get_contract_discount_usage(),
]; }

crate::exchanges::impl_exchange_method_wrappers! { @extend; MexcClient; public []; private [
get_stp_strategy_group(trade_group_name => "tradeGroupName"),
remove_stp_strategy_group_members(uid => "uid",trade_group_id => "tradeGroupId"),
get_withdrawal_addresses(),
delete_stp_strategy_group(trade_group_id => "tradeGroupId"),
create_stp_strategy_group(trade_group_name => "tradeGroupName"),
add_stp_strategy_group_members(uid => "uid",trade_group_id => "tradeGroupId"),
]; }

crate::exchanges::impl_exchange_method_wrappers! {@extend;MexcClient;public [];private [delete_sub_account_api_key(sub_account => "subAccount",api_key => "apiKey"),
create_sub_account_api_key(sub_account => "subAccount",note => "note",permissions => "permissions"),
get_sub_account_api_keys(sub_account => "subAccount"),];}

crate::exchanges::impl_exchange_method_wrappers! {@extend;MexcClient;public [];private [create_deposit_address(coin => "coin",network => "network")];}

crate::exchanges::impl_exchange_method_wrappers! {@extend;MexcClient;public [];private [create_spot_listen_key()];}

crate::exchanges::impl_exchange_method_wrappers! {@extend;MexcClient;public [];private [get_spot_listen_keys()];}

crate::exchanges::impl_exchange_method_wrappers! {@extend;MexcClient;public [];private [keep_alive_spot_listen_key(listen_key => "listenKey")];}

crate::exchanges::impl_exchange_method_wrappers! {@extend;MexcClient;public [];private [close_spot_listen_key(listen_key => "listenKey")];}

mod business_methods {
    use crate::exchanges::mexc::client::MexcClient;

    crate::exchanges::impl_exchange_method_wrappers! {
        @extend;
        MexcClient;
        public [];
        private [
            create_contract_stp_group(config_name => "configName", blacklist => "blacklist"),
            delete_contract_stp_group(config_name => "configName"),
            get_current_contract_stp_group(),
            get_contract_stp_groups(),
            update_contract_stp_group(config_name => "configName", blacklist => "blacklist"),
            get_rebate_affiliate_campaign(),
            get_rebate_affiliate_commission_detail(),
            get_rebate_affiliate_commission(start_time => "startTime", end_time => "endTime"),
            get_rebate_affiliate_referral(),
            get_rebate_affiliate_withdraw(),
            get_rebate_affiliate_list(member_info => "memberInfo"),
            get_rebate_tax_query(),
            get_rebate_detail(),
            get_rebate_detail_kickback(),
            get_rebate_affiliate_subaffiliates(),
            get_rebate_refer_code(),
            cancel_spot_withdrawal(id => "id"),
            /// API withdrawals and external transfers have no second confirmation; they execute on submit.
            transfer_spot_internal(to_account_type => "toAccountType", to_account => "toAccount", asset => "asset", amount => "amount"),
            /// API withdrawals and external transfers have no second confirmation; they execute on submit.
            create_spot_withdrawal(coin => "coin", address => "address", amount => "amount"),
            /// API withdrawals and external transfers have no second confirmation; they execute on submit.
            create_spot_withdrawal_legacy(coin => "coin", address => "address", amount => "amount"),
            place_contract_batch_orders(orders => "orders"),
        ];
    }
}
