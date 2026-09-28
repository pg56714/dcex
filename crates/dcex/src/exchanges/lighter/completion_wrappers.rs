use super::LighterClient;
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
    ) -> crate::Result<super::LighterSignedTransaction> {
        self.sign_request("sign_withdraw_l2", params).await
    }
    pub async fn sign_approve_integrator(
        &self,
        params: Vec<(String, String)>,
    ) -> crate::Result<super::LighterSignedTransaction> {
        self.sign_request("sign_approve_integrator", params).await
    }
}
