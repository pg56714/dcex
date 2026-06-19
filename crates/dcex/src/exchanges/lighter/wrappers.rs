use crate::Result;

use super::{LighterClient, LighterSignedTransaction};

crate::exchanges::impl_exchange_method_wrappers! {
    LighterClient;
    public [
        get_account,
        get_account_metadata,
        get_accounts_by_l1_address,
        get_announcement,
        get_api_keys,
        get_asset_details,
        get_candles,
        get_deposit_networks,
        get_exchange_metrics,
        get_exchange_stats,
        get_execute_stats,
        get_fastbridge_info,
        get_funding_rates,
        get_fundings,
        get_info,
        get_layer1_basic_info,
        get_lease_options,
        get_order_book_details,
        get_order_book_orders,
        get_order_books,
        get_pnl,
        get_public_pools_metadata,
        get_recent_trades,
        get_status,
        get_system_config,
        get_token_list,
        get_tokens,
        get_trades,
        get_withdrawal_delay
    ];
    private [
        cancel_all_orders,
        cancel_order,
        create_order,
        get_account_active_orders,
        get_account_inactive_orders,
        get_account_limits,
        get_deposit_history,
        get_export,
        get_fastwithdraw_info,
        get_l1_metadata,
        get_leases,
        get_liquidations,
        get_maker_only_api_keys,
        get_next_nonce,
        get_partner_stats,
        get_position_funding,
        get_referral_points,
        get_referral_user_referrals,
        get_transfer_fee_info,
        get_transfer_history,
        get_withdraw_history,
        modify_order,
        place_order,
        send_tx,
        send_tx_batch,
        update_leverage,
        update_margin
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
