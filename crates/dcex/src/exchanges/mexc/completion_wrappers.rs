//! Reviewed MEXC additional endpoint wrappers.
use super::client::MexcClient;

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
