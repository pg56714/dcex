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
        get_withdrawal_delay()
    ];
    private [
        cancel_all_orders(time_in_force => "time_in_force", timestamp_ms => "timestamp_ms"),
        cancel_order(market_index => "market_index", order_index => "order_index"),
        create_order(market_index => "market_index", client_order_index => "client_order_index", base_amount => "base_amount", price => "price", is_ask => "is_ask", order_type => "order_type", time_in_force => "time_in_force"),
        get_account_active_orders(),
        get_account_inactive_orders(limit => "limit"),
        get_account_limits(),
        get_deposit_history(l1_address => "l1_address"),
        get_export(type_ => "type_"),
        get_fastwithdraw_info(),
        get_l1_metadata(l1_address => "l1_address"),
        get_leases(),
        get_liquidations(limit => "limit"),
        get_maker_only_api_keys(),
        get_next_nonce(),
        get_partner_stats(),
        get_position_funding(limit => "limit"),
        get_referral_points(),
        get_referral_user_referrals(l1_address => "l1_address"),
        get_transfer_fee_info(),
        get_transfer_history(),
        get_withdraw_history(),
        modify_order(market_index => "market_index", order_index => "order_index", base_amount => "base_amount", price => "price"),
        place_order(market_index => "market_index", client_order_index => "client_order_index", base_amount => "base_amount", price => "price", is_ask => "is_ask", order_type => "order_type", time_in_force => "time_in_force"),
        send_tx(tx_type => "tx_type", tx_info => "tx_info"),
        send_tx_batch(tx_types => "tx_types", tx_infos => "tx_infos"),
        update_leverage(market_index => "market_index", fraction => "fraction", margin_mode => "margin_mode"),
        update_margin(market_index => "market_index", usdc_amount => "usdc_amount", direction => "direction")
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
