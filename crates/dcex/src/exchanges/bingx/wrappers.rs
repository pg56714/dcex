use super::client::BingxClient;

crate::exchanges::impl_exchange_method_wrappers! {
    BingxClient;
    public [
        get_swap_server_time(),
        get_swap_price_ticker(),
        get_coin_swap_contracts(),
        get_coin_swap_orderbook(product_symbol => "product_symbol"),
        get_coin_swap_kline(product_symbol => "product_symbol", interval => "interval"),
        get_coin_swap_premium_index(),
        get_coin_swap_open_interest(),
        get_coin_swap_ticker(),
        get_spot_historical_kline(product_symbol => "product_symbol", interval => "interval"),
        get_kline(product_symbol => "product_symbol", interval => "interval"),
        get_mark_price_kline(product_symbol => "product_symbol", interval => "interval"),
        get_open_interest(product_symbol => "product_symbol"),
        get_orderbook(product_symbol => "product_symbol"),
        get_public_trades(product_symbol => "product_symbol"),
        get_spot_book_ticker(product_symbol => "product_symbol"),
        get_spot_instrument_info(),
        get_spot_kline(product_symbol => "product_symbol", interval => "interval"),
        get_spot_kline_v2(product_symbol => "product_symbol", interval => "interval"),
        get_spot_orderbook(product_symbol => "product_symbol"),
        get_spot_orderbook_v2(product_symbol => "product_symbol"),
        get_spot_price_ticker(product_symbol => "product_symbol"),
        get_spot_public_trades(product_symbol => "product_symbol"),
        get_spot_ticker(),
        get_swap_instrument_info(),
        get_ticker(),
        get_swap_premium_index(),
        get_swap_funding_rate(),
        get_swap_book_ticker(product_symbol => "product_symbol"),
        get_swap_trading_rules(product_symbol => "product_symbol"),
    ];
    private [
        replace_swap_batch_orders(orders => "batchOrders"),
        place_coin_swap_order(product_symbol => "product_symbol", side => "side", type_ => "type_"),
        cancel_coin_swap_order(product_symbol => "product_symbol"),
        cancel_coin_swap_all_orders(),
        close_coin_swap_all_positions(),
        get_coin_swap_open_orders(),
        get_coin_swap_order(product_symbol => "product_symbol"),
        get_coin_swap_order_history(limit => "limit"),
        get_coin_swap_fills(order_id => "orderId"),
        get_coin_swap_force_orders(),
        get_coin_swap_leverage(product_symbol => "product_symbol"),
        set_coin_swap_leverage(
            product_symbol => "product_symbol",
            side => "side",
            leverage => "leverage"
        ),
        get_coin_swap_margin_type(product_symbol => "product_symbol"),
        set_coin_swap_margin_type(product_symbol => "product_symbol", margin_type => "marginType"),
        adjust_coin_swap_position_margin(
            product_symbol => "product_symbol",
            position_side => "positionSide",
            amount => "amount",
            type_ => "type_"
        ),
        get_coin_swap_commission_rate(),
        get_coin_swap_balance(),
        get_coin_swap_positions(),
        place_spot_oco(
            product_symbol => "product_symbol",
            side => "side",
            quantity => "quantity",
            limit_price => "limitPrice",
            trigger_price => "triggerPrice",
            order_price => "orderPrice"
        ),
        cancel_spot_oco(),
        get_spot_oco(),
        get_spot_open_oco(page_index => "pageIndex", page_size => "pageSize"),
        get_spot_oco_history(page_index => "pageIndex", page_size => "pageSize"),
        get_deposit_history(),
        set_swap_cancel_all_after(type_ => "type_", time_out => "timeOut"),
        get_swap_open_order(product_symbol => "product_symbol"),
        get_swap_force_orders(),
        get_swap_trade_fills(
            trading_unit => "tradingUnit",
            start_ts => "startTs",
            end_ts => "endTs"
        ),
        adjust_swap_position_margin(
            product_symbol => "product_symbol",
            amount => "amount",
            type_ => "type_"
        ),
        amend_swap_order(product_symbol => "product_symbol", quantity => "quantity"),
        place_swap_twap_order(
            product_symbol => "product_symbol",
            side => "side",
            position_side => "positionSide",
            price_type => "priceType",
            price_variance => "priceVariance",
            trigger_price => "triggerPrice",
            interval => "interval",
            amount_per_order => "amountPerOrder",
            total_amount => "totalAmount"
        ),
        cancel_swap_twap_order(main_order_id => "mainOrderId"),
        get_swap_open_twap_orders(),
        get_swap_twap_order_history(
            page_index => "pageIndex",
            page_size => "pageSize",
            start_time => "startTime",
            end_time => "endTime"
        ),
        get_swap_twap_order(main_order_id => "mainOrderId"),
        get_swap_asset_mode(),
        set_swap_asset_mode(asset_mode => "assetMode"),
        get_swap_multi_asset_rules(),
        get_swap_margin_assets(),
        get_swap_full_orders(limit => "limit"),
        get_swap_fill_history(
            product_symbol => "product_symbol",
            start_ts => "startTs",
            end_ts => "endTs"
        ),
        get_swap_position_history(
            product_symbol => "product_symbol",
            start_ts => "startTs",
            end_ts => "endTs"
        ),
        get_swap_margin_history(
            product_symbol => "product_symbol",
            position_id => "positionId",
            start_time => "startTime",
            end_time => "endTime",
            page_index => "pageIndex",
            page_size => "pageSize"
        ),
        get_swap_maintenance_margin_ratios(product_symbol => "product_symbol"),
        set_swap_auto_add_margin(
            product_symbol => "product_symbol",
            position_id => "positionId",
            function_switch => "functionSwitch"
        ),
        asset_transfer(
            from_account => "fromAccount",
            to_account => "toAccount",
            asset => "asset",
            amount => "amount"
        ),
        cancel_spot_batch_orders(product_symbol => "product_symbol", order_ids => "orderIds"),
        cancel_spot_open_orders(),
        set_spot_cancel_all_after(type_ => "type_"),
        cancel_spot_order(product_symbol => "product_symbol"),
        cancel_swap_all_orders(),
        cancel_swap_batch_order(product_symbol => "product_symbol"),
        cancel_swap_order(product_symbol => "product_symbol"),
        change_margin_type(product_symbol => "product_symbol", margin_type => "marginType"),
        close_swap_all_positions(),
        close_swap_position(position_id => "positionId"),
        close_listen_key(listen_key => "listen_key"),
        get_account_balance(),
        get_account_uid(),
        get_all_account_balance(),
        get_api_key_info(uid => "uid"),
        get_asset_transfer_records(),
        get_fund_account_balance(),
        get_fund_flow(),
        get_leverage(product_symbol => "product_symbol"),
        get_listen_key(),
        get_margin_type(product_symbol => "product_symbol"),
        get_open_orders(),
        get_open_positions(),
        get_order_detail(product_symbol => "product_symbol"),
        get_order_history(),
        get_position_mode(),
        get_spot_account_balance(),
        get_spot_commission_rate(product_symbol => "product_symbol"),
        get_spot_my_trades(product_symbol => "product_symbol"),
        get_spot_open_orders(),
        get_spot_order(product_symbol => "product_symbol"),
        get_spot_order_history(),
        get_subaccount_all_account_balance(page_index => "pageIndex", page_size => "pageSize"),
        get_subaccount_assets(sub_uid => "subUid"),
        get_subaccount_transfer_history(uid => "uid"),
        get_subaccount_transferable_amounts(
            from_uid => "fromUid",
            from_account_type => "fromAccountType",
            to_uid => "toUid",
            to_account_type => "toAccountType"
        ),
        get_subaccounts(page => "page", limit => "limit"),
        get_swap_account_balance(),
        get_swap_commission_rate(),
        get_transferable_coins(from_account => "fromAccount", to_account => "toAccount"),
        keep_alive_listen_key(listen_key => "listen_key"),
        place_spot_batch_order(data => "data"),
        replace_spot_order(
            product_symbol => "product_symbol",
            cancel_replace_mode => "cancelReplaceMode",
            side => "side",
            type_ => "type_"
        ),
        place_spot_limit_buy_order(
            product_symbol => "product_symbol",
            quantity => "quantity",
            price => "price"
        ),
        place_spot_limit_order(
            product_symbol => "product_symbol",
            side => "side",
            quantity => "quantity",
            price => "price"
        ),
        place_spot_limit_sell_order(
            product_symbol => "product_symbol",
            quantity => "quantity",
            price => "price"
        ),
        place_spot_market_buy_order(
            product_symbol => "product_symbol",
            quote_order_qty => "quoteOrderQty"
        ),
        place_spot_market_sell_order(product_symbol => "product_symbol", quantity => "quantity"),
        place_spot_order(product_symbol => "product_symbol", side => "side", type_ => "type_"),
        place_spot_post_only_buy_order(
            product_symbol => "product_symbol",
            quantity => "quantity",
            price => "price"
        ),
        place_spot_post_only_order(
            product_symbol => "product_symbol",
            side => "side",
            quantity => "quantity",
            price => "price"
        ),
        place_spot_post_only_sell_order(
            product_symbol => "product_symbol",
            quantity => "quantity",
            price => "price"
        ),
        place_swap_batch_order(batch_orders => "batchOrders"),
        place_swap_limit_buy_order(
            product_symbol => "product_symbol",
            quantity => "quantity",
            price => "price"
        ),
        place_swap_limit_order(
            product_symbol => "product_symbol",
            side => "side",
            quantity => "quantity",
            price => "price"
        ),
        place_swap_limit_sell_order(
            product_symbol => "product_symbol",
            quantity => "quantity",
            price => "price"
        ),
        place_swap_market_buy_order(product_symbol => "product_symbol", quantity => "quantity"),
        place_swap_market_order(
            product_symbol => "product_symbol",
            side => "side",
            quantity => "quantity"
        ),
        place_swap_market_sell_order(product_symbol => "product_symbol", quantity => "quantity"),
        place_swap_order(product_symbol => "product_symbol", type_ => "type_", side => "side"),
        place_swap_post_only_buy_order(
            product_symbol => "product_symbol",
            quantity => "quantity",
            price => "price"
        ),
        place_swap_post_only_order(
            product_symbol => "product_symbol",
            side => "side",
            quantity => "quantity",
            price => "price"
        ),
        place_swap_post_only_sell_order(
            product_symbol => "product_symbol",
            quantity => "quantity",
            price => "price"
        ),
        replace_swap_order(
            product_symbol => "product_symbol",
            cancel_replace_mode => "cancelReplaceMode",
            type_ => "type_",
            side => "side",
            position_side => "positionSide"
        ),
        set_leverage(product_symbol => "product_symbol", side => "side", leverage => "leverage"),
        set_position_mode(dual_side_position => "dualSidePosition"),
        test_swap_order(product_symbol => "product_symbol", type_ => "type_", side => "side"),
        transfer_subaccount_assets(
            asset_name => "assetName",
            transfer_amount => "transferAmount",
            from_uid => "fromUid",
            from_type => "fromType",
            from_account_type => "fromAccountType",
            to_uid => "toUid",
            to_type => "toType",
            to_account_type => "toAccountType",
            remark => "remark"
        ),
    ];
}

crate::exchanges::impl_exchange_method_wrappers! {
    @extend;
    BingxClient;
    public [
        get_spot_historical_trades(product_symbol => "product_symbol"),
        get_swap_historical_trades(product_symbol => "product_symbol"),
    ];
    private [
        get_coin_network_config(),
        get_deposit_addresses(coin => "coin"),
        get_deposit_risk_records(),
        reverse_swap_position(type_ => "type_", product_symbol => "product_symbol"),
        adjust_simulated_trading_balance(),
        get_standard_futures_positions(),
        get_standard_futures_orders(product_symbol => "product_symbol"),
        get_standard_futures_balance(),
        get_api_permissions(),
        create_sub_account(sub_account_string => "subAccountString"),
        set_sub_account_frozen(sub_uid => "subUid", freeze => "freeze"),
        create_sub_account_api_key(
            sub_uid => "subUid",
            note => "note",
            permissions => "permissions"
        ),
        modify_sub_account_api_key(
            sub_uid => "subUid",
            api_key => "apiKey",
            note => "note",
            permissions => "permissions"
        ),
        delete_sub_account_api_key(sub_uid => "subUid", api_key => "apiKey"),
        set_sub_account_transfer_authorization(
            sub_uids => "subUids",
            transferable => "transferable"
        ),
        get_sub_account_deposit_addresses(coin => "coin", sub_uid => "subUid"),
        get_sub_account_deposit_history(),
        get_api_restrictions(),
        create_sub_account_deposit_address(
            coin => "coin",
            sub_uid => "subUid",
            network => "network",
            wallet_type => "walletType"
        ),
    ];
}

crate::exchanges::impl_exchange_method_wrappers! {
    @extend;
    BingxClient;
    public [
    ];
    private [
        get_withdrawal_history(),
        get_internal_transfer_records(coin => "coin"),
        get_sub_account_internal_transfer_records(coin => "coin"),
    ];
}

mod business_methods {
    use crate::exchanges::bingx::client::BingxClient;

    crate::exchanges::impl_exchange_method_wrappers! {
        @extend;
        BingxClient;
        public [
            get_spot_server_time(),
        ];
        private [
            /// API withdrawals and external transfers have no second confirmation; they execute on submit.
            transfer_master_internal(coin => "coin", user_account_type => "userAccountType", user_account => "userAccount", amount => "amount", wallet_type => "walletType"),
            transfer_sub_account_internal(coin => "coin", user_account_type => "userAccountType", user_account => "userAccount", amount => "amount", wallet_type => "walletType"),
            /// API withdrawals and external transfers have no second confirmation; they execute on submit.
            create_withdrawal(coin => "coin", address => "address", amount => "amount", wallet_type => "walletType"),
        ];
    }
}
