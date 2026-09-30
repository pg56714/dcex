use super::HyperliquidClient;

crate::exchanges::impl_exchange_method_wrappers! {
    HyperliquidClient;
    public [
        get_vault_details(vault_address => "vaultAddress"),
        get_delegations(user => "user"),
        get_delegator_summary(user => "user"),
        get_delegator_history(user => "user"),
        get_delegator_rewards(user => "user"),
        get_spot_deploy_state(user => "user"),
        get_outcome_meta(),
        get_settled_outcome(outcome => "outcome"),
        get_outcome_deployer_limits(venue => "venue"),
        get_perp_deploy_auction_status(),
        get_spot_pair_deploy_auction_status(),
        get_perps_at_open_interest_cap(),
        get_perp_dex_limits(dex => "dex"),
        get_perp_dex_status(dex => "dex"),
        get_all_perp_metas(),
        get_perp_annotation(product_symbol => "product_symbol"),
        get_perp_categories(),
        get_perp_concise_annotations(),
        get_token_details(token_id => "tokenId"),
        get_user_dex_abstraction(user => "user"),
        get_user_abstraction(user => "user"),
        get_borrow_lend_user_state(user => "user"),
        get_borrow_lend_reserve_state(token => "token"),
        get_all_borrow_lend_reserve_states(),
        get_predicted_fundings(),
        frontend_open_orders(user => "user"),
        get_futures_fee_rates(user => "user"),
        get_spot_fee_rates(user => "user"),
        clearinghouse_state(user => "user"),
        get_candle_snapshot(
            product_symbol => "product_symbol",
            interval => "interval",
            start_time => "startTime",
            end_time => "endTime"
        ),
        get_funding_rate_history(product_symbol => "product_symbol", start_time => "startTime"),
        get_l2book(product_symbol => "product_symbol"),
        get_meta(),
        get_meta_and_asset_ctxs(),
        get_perp_dexs(),
        get_spot_meta(),
        get_spot_meta_and_asset_ctxs(),
        historical_orders(user => "user"),
        open_orders(user => "user"),
        order_status(user => "user", oid => "oid"),
        portfolio(user => "user"),
        spot_clearinghouse_state(user => "user"),
        subaccounts(user => "user"),
        user_fills(user => "user"),
        user_fills_by_time(user => "user", start_time => "startTime"),
        user_funding(user => "user", start_time => "startTime"),
        user_non_funding_ledger_updates(user => "user", start_time => "startTime"),
        user_rate_limit(user => "user"),
        user_role(user => "user"),
        user_vault_equities(user => "user"),
    ];
    private [
        reserve_request_weight(weight => "weight"),
        set_agent_abstraction(abstraction => "abstraction"),
        set_user_abstraction(
            user => "user",
            abstraction => "abstraction",
            nonce => "nonce",
            signature => "signature",
            signature_chain_id => "signatureChainId"
        ),
        noop(nonce => "nonce"),


        cancel_order(product_symbol => "product_symbol", oid => "oid"),
        cancel_order_by_cloid(product_symbol => "product_symbol", cloid => "cloid"),
        cancel_twap_order(product_symbol => "product_symbol", twap_id => "twap_id"),

        modify_order(
            oid => "oid",
            product_symbol => "product_symbol",
            is_buy => "isBuy",
            price => "price",
            size => "size",
            reduce_only => "reduceOnly"
        ),

        place_future_limit_buy_order(
            product_symbol => "product_symbol",
            price => "price",
            size => "size",
            tif => "tif"
        ),
        place_future_limit_order(
            product_symbol => "product_symbol",
            is_buy => "isBuy",
            price => "price",
            size => "size",
            tif => "tif"
        ),
        place_future_limit_sell_order(
            product_symbol => "product_symbol",
            price => "price",
            size => "size",
            tif => "tif"
        ),
        place_future_market_buy_order(product_symbol => "product_symbol", size => "size"),
        place_future_market_order(
            product_symbol => "product_symbol",
            is_buy => "isBuy",
            size => "size"
        ),
        place_future_market_sell_order(product_symbol => "product_symbol", size => "size"),
        place_order(
            product_symbol => "product_symbol",
            is_buy => "isBuy",
            price => "price",
            size => "size",
            reduce_only => "reduceOnly"
        ),
        place_twap_order(
            product_symbol => "product_symbol",
            is_buy => "isBuy",
            size => "size",
            reduce_only => "reduceOnly",
            minutes => "minutes",
            randomize => "randomize"
        ),
        schedule_cancel(),


        update_isolated_margin(
            product_symbol => "product_symbol",
            is_buy => "isBuy",
            ntli => "ntli"
        ),
        update_leverage(
            product_symbol => "product_symbol",
            is_cross => "isCross",
            leverage => "leverage"
        ),
    ];
}

crate::exchanges::impl_exchange_method_wrappers! {
    @extend;
    HyperliquidClient;
    public [
    ];
    private [

        enable_agent_dex_abstraction(),

        deposit_staking_signed(
            wei => "wei",
            nonce => "nonce",
            signature => "signature",
            signature_chain_id => "signatureChainId"
        ),
        /// API withdrawals and external transfers have no second confirmation; they execute on submit.

        delegate_tokens_signed(
            validator => "validator",
            wei => "wei",
            is_undelegate => "isUndelegate",
            nonce => "nonce",
            signature => "signature",
            signature_chain_id => "signatureChainId"
        ),
        set_user_dex_abstraction_signed(
            user => "user",
            enabled => "enabled",
            nonce => "nonce",
            signature => "signature",
            signature_chain_id => "signatureChainId"
        ),
    ];
}

crate::exchanges::impl_exchange_method_wrappers! {
    @extend;
    HyperliquidClient;
    public [
    ];
    private [
        create_sub_account(account_name => "name"),


    ];
}

crate::exchanges::impl_exchange_method_wrappers! {
    @extend;
    HyperliquidClient;
    public [
    ];
    private [
        approve_agent_signed(
            agent_address => "agentAddress",
            nonce => "nonce",
            signature => "signature",
            signature_chain_id => "signatureChainId"
        ),
    ];
}

crate::exchanges::impl_exchange_method_wrappers! {
    @extend;
    HyperliquidClient;
    public [
        get_all_mids(),
        get_active_asset_data(user => "user", product_symbol => "product_symbol"),
        get_user_twap_slice_fills(user => "user"),
    ];
    private [
    ];
}

impl<'a> crate::exchanges::ExchangeMethodRequest<'a, HyperliquidClient> {
    /// Set the optional name when approving an agent with a wallet signature.
    pub fn agent_name(self, name: impl Into<String>) -> Self {
        self.param("agentName", name.into())
    }
}

crate::exchanges::impl_exchange_method_wrappers! {
    @extend;
    HyperliquidClient;
    public [];
    private [
        borrow_lend_signed(action => "action", nonce => "nonce", signature => "signature"),
    ];
}

crate::exchanges::impl_exchange_method_wrappers! {
    @extend; HyperliquidClient;
    public [get_max_builder_fee(user => "user", builder => "builder"), get_approved_builders(user => "user"), get_referral_state(user => "user")];
    private [



        approve_builder_fee_signed(builder => "builder", max_fee_rate => "maxFeeRate", nonce => "nonce", signature => "signature", signature_chain_id => "signatureChainId"),

    ];
}
