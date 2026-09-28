use super::AsterClient;

crate::exchanges::impl_exchange_method_wrappers! {
    AsterClient;
    public [
    ];
    private [
        noop_spot(nonce => "nonce"),
        noop_futures(nonce => "nonce"),
        guarded_cancel_futures_order(product_symbol => "product_symbol", nonce => "nonce"),
        guarded_cancel_futures_batch_orders(product_symbol => "product_symbol", nonce => "nonce"),
        transfer_sub_account(
            to_account_address => "toAccountAddress",
            asset => "asset",
            amount => "amount",
            kind_type => "kindType"
        ),
        get_spot_account(),
        get_spot_transaction_history(),
        transfer_spot_futures(
            amount => "amount",
            asset => "asset",
            client_tran_id => "clientTranId",
            kind_type => "kindType"
        ),
        get_futures_position_mode(),
        set_futures_position_mode(dual_side_position => "dualSidePosition"),
        get_futures_stp_mode(),
        set_futures_stp_mode(stp_mode => "stpMode"),
        get_futures_multi_assets_mode(),
        set_futures_multi_assets_mode(multi_assets_margin => "multiAssetsMargin"),
        get_futures_balance(),
        get_futures_account(),
        modify_futures_position_margin(
            product_symbol => "product_symbol",
            amount => "amount",
            type_ => "type"
        ),
        get_futures_position_margin_history(product_symbol => "product_symbol"),
        get_futures_position_risk(),
        get_futures_user_trades(product_symbol => "product_symbol"),
        get_futures_income(),
        get_futures_leverage_bracket(),
        get_futures_adl_quantile(),
        get_futures_force_orders(),
        get_spot_commission_rate(product_symbol => "product_symbol"),
        get_futures_commission_rate(product_symbol => "product_symbol"),
        update_futures_mmp(
            product_symbol => "product_symbol",
            window_time_in_milliseconds => "windowTimeInMilliseconds",
            frozen_time_in_milliseconds => "frozenTimeInMilliseconds"
        ),
        get_futures_mmp(),
        delete_futures_mmp(product_symbol => "product_symbol"),
        reset_futures_mmp(product_symbol => "product_symbol"),
        create_spot_listen_key(),
        keep_alive_spot_listen_key(listen_key => "listenKey"),
        close_spot_listen_key(listen_key => "listenKey"),
        create_futures_listen_key(),
        keep_alive_futures_listen_key(),
        close_futures_listen_key(),
        place_spot_order(product_symbol => "product_symbol", side => "side", type_ => "type"),
        cancel_spot_order(product_symbol => "product_symbol"),
        get_spot_order(product_symbol => "product_symbol"),
        get_spot_open_order(product_symbol => "product_symbol"),
        get_spot_open_orders(),
        cancel_all_spot_open_orders(product_symbol => "product_symbol"),
        get_spot_all_orders(product_symbol => "product_symbol"),
        get_spot_user_trades(),
        place_futures_order(product_symbol => "product_symbol", side => "side", type_ => "type"),
        modify_futures_order(
            product_symbol => "product_symbol",
            quantity => "quantity",
            price => "price"
        ),
        place_futures_chase_order(
            product_symbol => "product_symbol",
            side => "side",
            quantity_unit => "quantityUnit",
            quantity => "quantity"
        ),
        place_futures_batch_orders(batch_orders => "batchOrders"),
        modify_futures_batch_orders(batch_orders => "batchOrders"),
        get_futures_order(product_symbol => "product_symbol"),
        cancel_futures_order(product_symbol => "product_symbol"),
        cancel_all_futures_open_orders(product_symbol => "product_symbol"),
        cancel_futures_batch_orders(product_symbol => "product_symbol"),
        set_futures_countdown_cancel_all(
            product_symbol => "product_symbol",
            countdown_time => "countdownTime"
        ),
        get_futures_open_order(product_symbol => "product_symbol"),
        get_futures_open_orders(),
        get_futures_all_orders(product_symbol => "product_symbol"),
        set_futures_leverage(product_symbol => "product_symbol", leverage => "leverage"),
        set_futures_margin_type(product_symbol => "product_symbol", margin_type => "marginType"),
        place_futures_strategy_order(
            strategy_type => "strategyType",
            sub_order_list => "subOrderList"
        ),
        update_futures_strategy_order(
            strategy_id => "strategyId",
            strategy_type => "strategyType",
            sub_order_list => "subOrderList"
        ),
        get_futures_strategy_open_order(strategy_type => "strategyType"),
        get_futures_strategy_history_order(strategy_type => "strategyType"),
    ];
}

crate::exchanges::impl_exchange_method_wrappers! {
    @extend;
    AsterClient;
    public [
        get_asset_logos(),
    ];
    private [
        exchange_futures_assets(),
        trigger_futures_asset_exchange(),
        get_sub_accounts(),
        get_direct_announcements(),
        get_direct_announcement(id => "id"),
        create_sub_account_signed(
            sub_account_name => "subAccountName",
            sub_source_addr => "subSourceAddr",
            nonce => "nonce",
            user => "user",
            signer => "signer",
            child_signature => "childSignature",
            signature => "signature"
        ),
        update_sub_account_signed(
            sub_source_addr => "subSourceAddr",
            nonce => "nonce",
            user => "user",
            signer => "signer",
            signature => "signature"
        ),
        bind_sub_account_signed(
            child_address => "childAddress",
            name => "name",
            nonce => "nonce",
            user => "user",
            child_signature => "childSignature",
            signature => "signature"
        ),
        register_agent_signed(
            user => "user",
            nonce => "nonce",
            agent_name => "agentName",
            agent_address => "agentAddress",
            expired => "expired",
            signature_chain_id => "signatureChainId",
            can_spot_trade => "canSpotTrade",
            can_perp_trade => "canPerpTrade",
            can_withdraw => "canWithdraw",
            signature => "signature"
        ),
    ];
}

crate::exchanges::impl_exchange_method_wrappers! {
    @extend;
    AsterClient;
    public [
        get_prediction_ping(),
        get_prediction_time(),
        get_prediction_exchange_info(),
        get_prediction_depth(symbol => "symbol"),
        get_prediction_trades(symbol => "symbol"),
        get_prediction_historical_trades(symbol => "symbol"),
        get_prediction_agg_trades(symbol => "symbol"),
        get_prediction_klines(symbol => "symbol", interval => "interval"),
        get_prediction_ticker_24hr(),
        get_prediction_ticker_price(),
        get_prediction_ticker_book_ticker(),
    ];
    private [
        get_prediction_commission_rate(symbol => "symbol"),
        create_prediction_order(symbol => "symbol", side => "side", type_ => "type"),
        cancel_prediction_order(symbol => "symbol"),
        get_prediction_order(symbol => "symbol"),
        get_prediction_open_order(symbol => "symbol"),
        get_prediction_open_orders(),
        get_prediction_all_orders(symbol => "symbol"),
        create_prediction_asset_wallet_transfer(
            amount => "amount",
            asset => "asset",
            client_tran_id => "clientTranId",
            kind_type => "kindType"
        ),
        create_prediction_mint(symbol => "symbol", quantity => "quantity"),
        create_prediction_burn(symbol => "symbol", quantity => "quantity"),
        create_prediction_split(event => "event", symbol => "symbol", quantity => "quantity"),
        create_prediction_merge(event => "event", quantity => "quantity"),
        get_prediction_positions(),
        get_prediction_position_histories(),
        get_prediction_settlement_histories(),
        get_prediction_account(),
        get_prediction_user_trades(),
        create_prediction_listen_key(),
        update_prediction_listen_key(listen_key => "listenKey"),
        cancel_prediction_listen_key(listen_key => "listenKey"),
    ];
}

crate::exchanges::impl_exchange_method_wrappers! {
    @extend;
    AsterClient;
    public [
    ];
    private [
        get_asset_migration_history(batch_id => "batchId"),
    ];
}

mod business_methods {
    use crate::exchanges::aster::client::AsterClient;

    crate::exchanges::impl_exchange_method_wrappers! {
        @extend;
        AsterClient;
        public [
            get_chain_locked_aster(),
            get_chain_withdraw_fee(chain_id => "chainId", asset => "asset"),
            get_announcement(id => "id"),
            search_announcements(page => "page", size => "size"),
            get_futures_market_klines(symbol => "symbol"),
            get_spot_optimized_ticker_24hr(),
        ];
        private [
            place_spot_batch_orders_raw(),
            cancel_spot_batch_orders_raw(),
            noop_prediction(nonce => "nonce"),
            get_builder_user_accounts(),
            get_builder_user_open_orders(),
            get_builder_user_balances(),
            get_builder_user_position_risk(),
            get_builder_user_commission_rates(symbol => "symbol"),
            get_builder_user_trades(),
            get_builder_user_all_orders(),
            get_builder_approved_users(),
            /// API withdrawals and external transfers have no second confirmation; they execute on submit.
            withdraw_spot_signed(chain_id => "chainId", asset => "asset", amount => "amount", fee => "fee", receiver => "receiver", user_nonce => "userNonce", user_signature => "userSignature"),
            /// API withdrawals and external transfers have no second confirmation; they execute on submit.
            withdraw_spot_solana_signed(chain_id => "chainId", asset => "asset", amount => "amount", fee => "fee", receiver => "receiver"),
            /// API withdrawals and external transfers have no second confirmation; they execute on submit.
            withdraw_futures_signed(chain_id => "chainId", asset => "asset", amount => "amount", fee => "fee", receiver => "receiver", user_nonce => "userNonce", user_signature => "userSignature"),
            /// API withdrawals and external transfers have no second confirmation; they execute on submit.
            withdraw_futures_solana_signed(chain_id => "chainId", asset => "asset", amount => "amount", fee => "fee", receiver => "receiver"),
        ];
    }
}
