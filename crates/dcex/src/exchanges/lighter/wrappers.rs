use crate::Result;

use super::{LighterClient, LighterSignedTransaction};

crate::exchanges::impl_exchange_method_wrappers! {
    LighterClient;
    public [
        get_account(by => "by", value => "value"),
        get_account_metadata(by => "by", value => "value"),
        get_accounts_by_l1_address(l1_address => "l1_address"),
        get_announcement(),
        get_api_keys(account_index => "account_index"),
        get_asset_details(),
        get_candles(market_id => "market_id", resolution => "resolution", start_timestamp => "start_timestamp", end_timestamp => "end_timestamp", count_back => "count_back"),
        get_mark_price_candles(market_id => "market_id", resolution => "resolution", start_timestamp => "start_timestamp", end_timestamp => "end_timestamp", count_back => "count_back"),
        get_market_price_charts(),
        get_synthetic_spot_info(symbol => "symbol"),
        get_deposit_networks(),
        get_exchange_metrics(period => "period", kind => "kind"),
        get_exchange_stats(),
        get_execute_stats(period => "period"),
        get_fastbridge_info(),
        get_funding_rates(),
        get_fundings(market_id => "market_id", resolution => "resolution", start_timestamp => "start_timestamp", end_timestamp => "end_timestamp", count_back => "count_back"),
        get_info(),
        get_layer1_basic_info(),
        get_lease_options(),
        get_order_book_details(),
        get_order_book_orders(market_id => "market_id", limit => "limit"),
        get_order_books(),
        get_pnl(by => "by", value => "value", resolution => "resolution", start_timestamp => "start_timestamp", end_timestamp => "end_timestamp", count_back => "count_back"),
        get_public_pools_metadata(index => "index", limit => "limit"),
        get_recent_trades(market_id => "market_id", limit => "limit"),
        get_status(),
        get_system_config(),
        get_token_list(),
        get_tokens(account_index => "account_index"),
        get_trades(sort_by => "sort_by", limit => "limit"),

    ];
    private [
        create_sub_account(), change_api_key_signed(new_pubkey => "new_pubkey", l1_signature => "l1_signature", nonce => "nonce"),
        update_account_config(account_trading_mode => "account_trading_mode"),
        update_account_asset_config(asset_index => "asset_index", asset_margin_mode => "asset_margin_mode"),
        create_grouped_orders(grouping_type => "grouping_type", orders => "orders"),
        cancel_all_orders(time_in_force => "time_in_force", timestamp_ms => "timestamp_ms"),
        create_rfq(market_index => "market_index", direction => "direction"),
        get_rfq(rfq_id => "rfq_id"),
        list_rfqs(),
        update_rfq(rfq_id => "rfq_id", status => "status"),
        cancel_order(market_index => "market_index", order_index => "order_index"),
        create_order(market_index => "market_index", client_order_index => "client_order_index", base_amount => "base_amount", price => "price", is_ask => "is_ask", order_type => "order_type", time_in_force => "time_in_force"),
        get_account_active_orders(),
        get_account_orders(client_order_indexes => "client_order_indexes"),
        get_account_inactive_orders(limit => "limit"),
        get_account_limits(),
        get_deposit_history(l1_address => "l1_address"),
        get_export(type_ => "type_"),

        get_l1_metadata(l1_address => "l1_address"),
        get_leases(),
        get_liquidations(limit => "limit"),
        get_maker_only_api_keys(),
        get_next_nonce(),
        get_partner_stats(),
        get_position_funding(limit => "limit"),
        get_referral_points(),
        get_referral_user_referrals(l1_address => "l1_address"),



        modify_order(market_index => "market_index", order_index => "order_index", base_amount => "base_amount", price => "price"),
        place_order(market_index => "market_index", client_order_index => "client_order_index", base_amount => "base_amount", price => "price", is_ask => "is_ask", order_type => "order_type", time_in_force => "time_in_force"),
        send_tx(tx_type => "tx_type", tx_info => "tx_info"),

        update_leverage(market_index => "market_index", fraction => "fraction", margin_mode => "margin_mode"),
        update_margin(market_index => "market_index", usdc_amount => "usdc_amount", direction => "direction")
    ];
}

impl LighterClient {
    pub async fn sign_update_account_config(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        self.sign_request("sign_update_account_config", params)
            .await
    }

    pub async fn sign_update_account_asset_config(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        self.sign_request("sign_update_account_asset_config", params)
            .await
    }
    pub async fn sign_create_grouped_orders(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        self.sign_request("sign_create_grouped_orders", params)
            .await
    }

    pub async fn sign_create_order(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        self.sign_request("sign_create_order", params).await
    }

    pub async fn sign_cancel_order(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        self.sign_request("sign_cancel_order", params).await
    }

    pub async fn sign_modify_order(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        self.sign_request("sign_modify_order", params).await
    }

    pub async fn sign_cancel_all_orders(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        self.sign_request("sign_cancel_all_orders", params).await
    }

    pub async fn sign_update_leverage(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        self.sign_request("sign_update_leverage", params).await
    }

    pub async fn sign_update_margin(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        self.sign_request("sign_update_margin", params).await
    }
}

crate::exchanges::impl_exchange_method_wrappers! {@extend; LighterClient; public [
get_transaction(by => "by",value => "value"),
get_transaction_by_l1_hash(hash => "hash"),
create_deposit_intent_address(chain_id => "chain_id",from_addr => "from_addr",amount => "amount"),
get_latest_deposit(l1_address => "l1_address"),]; private [
change_account_tier(account_index => "account_index",new_tier => "new_tier"),
create_read_only_token(name => "name",account_index => "account_index",expiry => "expiry",sub_account_access => "sub_account_access"),
revoke_read_only_token(token_id => "token_id",account_index => "account_index"),
acknowledge_notification(notif_id => "notif_id",account_index => "account_index"),];}

impl LighterClient {
    /// Sign a type-9 subaccount creation without broadcasting it.
    pub async fn sign_create_sub_account(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        self.sign_request("sign_create_sub_account", params).await
    }
    /// Sign type 8 with a caller-supplied L1 wallet signature and explicit nonce.
    pub async fn sign_change_api_key_signed(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        self.sign_request("sign_change_api_key_signed", params)
            .await
    }
}

crate::exchanges::impl_exchange_method_wrappers! { @extend; LighterClient; public []; private [create_public_pool(operator_fee => "operator_fee",initial_total_shares => "initial_total_shares",min_operator_share_rate => "min_operator_share_rate"),update_public_pool(public_pool_index => "public_pool_index",status => "status",operator_fee => "operator_fee",min_operator_share_rate => "min_operator_share_rate"),mint_shares(public_pool_index => "public_pool_index",share_amount => "share_amount"),burn_shares(public_pool_index => "public_pool_index",share_amount => "share_amount"),stake_assets(staking_pool_index => "staking_pool_index",share_amount => "share_amount"),unstake_assets(staking_pool_index => "staking_pool_index",share_amount => "share_amount")];}
impl LighterClient {
    pub async fn sign_create_public_pool(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        self.sign_request("sign_create_public_pool", params).await
    }
    pub async fn sign_update_public_pool(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        self.sign_request("sign_update_public_pool", params).await
    }
    pub async fn sign_mint_shares(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        self.sign_request("sign_mint_shares", params).await
    }
    pub async fn sign_burn_shares(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        self.sign_request("sign_burn_shares", params).await
    }
    pub async fn sign_stake_assets(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        self.sign_request("sign_stake_assets", params).await
    }
    pub async fn sign_unstake_assets(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        self.sign_request("sign_unstake_assets", params).await
    }
}

crate::exchanges::impl_exchange_method_wrappers! {@extend;LighterClient;public [];private [submit_lit_lease(tx_info => "tx_info",lease_amount => "lease_amount",duration_days => "duration_days")];}

crate::exchanges::impl_exchange_method_wrappers! {@extend; LighterClient; public [get_pnl_leaderboard(time_window => "time_window",sort_by => "sort_by",sort_dir => "sort_dir",limit => "limit",offset => "offset"),get_explorer_account_logs(param => "param",limit => "limit",offset => "offset"),get_explorer_account_positions(param => "param"),get_explorer_account_assets(param => "param"),get_explorer_batches(),get_explorer_batch(batch_id => "batchId"),get_explorer_blocks(),get_explorer_block(block_id => "blockId"),get_explorer_log(hash => "hash"),get_explorer_markets(),get_explorer_market_logs(symbol => "symbol"),search_explorer(q => "q"),get_explorer_transaction_stats(aggregation_period => "aggregation_period"),get_explorer_total()]; private [export_historical_trades(l1_address => "l1_address",date => "date")];}

crate::exchanges::impl_exchange_method_wrappers! {@extend; LighterClient; public []; private [transfer_same_master_account(to_account_index => "to_account_index",asset_index => "asset_index",from_route_type => "from_route_type",to_route_type => "to_route_type",amount => "amount"),
/// The recipient may be another user. Transfers have no second confirmation; they execute on submit.
transfer_l2_account(to_account_index => "to_account_index",asset_index => "asset_index",from_route_type => "from_route_type",to_route_type => "to_route_type",amount => "amount")];}
impl LighterClient {
    pub async fn sign_transfer_same_master_account(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        self.sign_request("sign_transfer_same_master_account", params)
            .await
    }
    pub async fn sign_transfer_l2_account(
        &self,
        params: Vec<(String, String)>,
    ) -> Result<LighterSignedTransaction> {
        self.sign_request("sign_transfer_l2_account", params).await
    }
}

crate::exchanges::impl_exchange_method_wrappers! {@extend;LighterClient;public [];private [set_maker_only_api_keys(account_index => "account_index",api_key_indexes => "api_key_indexes")];}

mod business_methods {
    use crate::exchanges::lighter::LighterClient;
    crate::exchanges::impl_exchange_method_wrappers! { @extend; LighterClient; public []; private [
    /// API withdrawals and external transfers have no second confirmation; they execute on submit.
    submit_fast_withdrawal(tx_info => "tx_info",to_address => "to_address"),
    create_referral_code(account_index => "account_index"),
    get_referral_code(account_index => "account_index"),
    update_referral_kickback(account_index => "account_index",kickback_percentage => "kickback_percentage"),
    get_referral_stats(l1_address => "l1_address"),
    update_referral_code(account_index => "account_index",new_referral_code => "new_referral_code"),
    use_referral_code(l1_address => "l1_address",referral_code => "referral_code"),
    respond_to_rfq(rfq_id => "rfq_id",status => "status"),
    /// API withdrawals and external transfers have no second confirmation; they execute on submit.
    withdraw_l2(asset_index => "asset_index", route_type => "route_type", amount => "amount"),
    approve_integrator(integrator_account_index => "integrator_account_index", max_perps_taker_fee => "max_perps_taker_fee", max_perps_maker_fee => "max_perps_maker_fee", max_spot_taker_fee => "max_spot_taker_fee", max_spot_maker_fee => "max_spot_maker_fee", approval_expiry => "approval_expiry", l1_signature => "l1_signature", nonce => "nonce"),
    ]; }

    impl LighterClient {
        pub async fn sign_withdraw_l2(
            &self,
            params: Vec<(String, String)>,
        ) -> crate::Result<crate::exchanges::lighter::LighterSignedTransaction> {
            self.sign_request("sign_withdraw_l2", params).await
        }
        pub async fn sign_approve_integrator(
            &self,
            params: Vec<(String, String)>,
        ) -> crate::Result<crate::exchanges::lighter::LighterSignedTransaction> {
            self.sign_request("sign_approve_integrator", params).await
        }
    }
}
