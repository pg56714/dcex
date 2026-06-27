use crate::Result;

use super::{LighterClient, LighterSignedTransaction};

crate::exchanges::impl_exchange_method_wrappers! {
    LighterClient;
    public [
        get_account(by => "by", value => "value") => get_account_with,
        get_account_metadata(by => "by", value => "value") => get_account_metadata_with,
        get_accounts_by_l1_address(l1_address => "l1_address") => get_accounts_by_l1_address_with,
        get_announcement() => get_announcement_with,
        get_api_keys(account_index => "account_index") => get_api_keys_with,
        get_asset_details() => get_asset_details_with,
        get_candles(market_id => "market_id", resolution => "resolution", start_timestamp => "start_timestamp", end_timestamp => "end_timestamp", count_back => "count_back") => get_candles_with,
        get_deposit_networks() => get_deposit_networks_with,
        get_exchange_metrics(period => "period", kind => "kind") => get_exchange_metrics_with,
        get_exchange_stats() => get_exchange_stats_with,
        get_execute_stats(period => "period") => get_execute_stats_with,
        get_fastbridge_info() => get_fastbridge_info_with,
        get_funding_rates() => get_funding_rates_with,
        get_fundings(market_id => "market_id", resolution => "resolution", start_timestamp => "start_timestamp", end_timestamp => "end_timestamp", count_back => "count_back") => get_fundings_with,
        get_info() => get_info_with,
        get_layer1_basic_info() => get_layer1_basic_info_with,
        get_lease_options() => get_lease_options_with,
        get_order_book_details() => get_order_book_details_with,
        get_order_book_orders(market_id => "market_id", limit => "limit") => get_order_book_orders_with,
        get_order_books() => get_order_books_with,
        get_pnl(by => "by", value => "value", resolution => "resolution", start_timestamp => "start_timestamp", end_timestamp => "end_timestamp", count_back => "count_back") => get_pnl_with,
        get_public_pools_metadata(index => "index", limit => "limit") => get_public_pools_metadata_with,
        get_recent_trades(market_id => "market_id", limit => "limit") => get_recent_trades_with,
        get_status() => get_status_with,
        get_system_config() => get_system_config_with,
        get_token_list() => get_token_list_with,
        get_tokens(account_index => "account_index") => get_tokens_with,
        get_trades(sort_by => "sort_by", limit => "limit") => get_trades_with,
        get_withdrawal_delay() => get_withdrawal_delay_with
    ];
    private [
        cancel_all_orders(time_in_force => "time_in_force", timestamp_ms => "timestamp_ms") => cancel_all_orders_with,
        cancel_order(market_index => "market_index", order_index => "order_index") => cancel_order_with,
        create_order(market_index => "market_index", client_order_index => "client_order_index", base_amount => "base_amount", price => "price", is_ask => "is_ask", order_type => "order_type", time_in_force => "time_in_force") => create_order_with,
        get_account_active_orders() => get_account_active_orders_with,
        get_account_inactive_orders(limit => "limit") => get_account_inactive_orders_with,
        get_account_limits() => get_account_limits_with,
        get_deposit_history(l1_address => "l1_address") => get_deposit_history_with,
        get_export(type_ => "type_") => get_export_with,
        get_fastwithdraw_info() => get_fastwithdraw_info_with,
        get_l1_metadata(l1_address => "l1_address") => get_l1_metadata_with,
        get_leases() => get_leases_with,
        get_liquidations(limit => "limit") => get_liquidations_with,
        get_maker_only_api_keys() => get_maker_only_api_keys_with,
        get_next_nonce() => get_next_nonce_with,
        get_partner_stats() => get_partner_stats_with,
        get_position_funding(limit => "limit") => get_position_funding_with,
        get_referral_points() => get_referral_points_with,
        get_referral_user_referrals(l1_address => "l1_address") => get_referral_user_referrals_with,
        get_transfer_fee_info() => get_transfer_fee_info_with,
        get_transfer_history() => get_transfer_history_with,
        get_withdraw_history() => get_withdraw_history_with,
        modify_order(market_index => "market_index", order_index => "order_index", base_amount => "base_amount", price => "price") => modify_order_with,
        place_order(market_index => "market_index", client_order_index => "client_order_index", base_amount => "base_amount", price => "price", is_ask => "is_ask", order_type => "order_type", time_in_force => "time_in_force") => place_order_with,
        send_tx(tx_type => "tx_type", tx_info => "tx_info") => send_tx_with,
        send_tx_batch(tx_types => "tx_types", tx_infos => "tx_infos") => send_tx_batch_with,
        update_leverage(market_index => "market_index", fraction => "fraction", margin_mode => "margin_mode") => update_leverage_with,
        update_margin(market_index => "market_index", usdc_amount => "usdc_amount", direction => "direction") => update_margin_with
    ];
}

impl LighterClient {
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
