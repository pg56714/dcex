use super::client::OkxClient;
crate::exchanges::impl_exchange_method_wrappers! {
    @extend;
    OkxClient;
    public [
        get_mm_instrument_types(),
    ];
    private [
        reset_mmp(inst_family => "instFamily"),
        set_mmp_config(inst_family => "instFamily", time_interval => "timeInterval", frozen_interval => "frozenInterval", qty_limit => "qtyLimit"),
        get_mmp_config(),
        get_glp_today_performance(),
        get_glp_historical_performance(program => "program"),
        mass_cancel_options_orders(inst_type => "instType", inst_family => "instFamily"),
        create_rfq_quote(rfq_id => "rfqId", quote_side => "quoteSide", legs => "legs"),
        cancel_rfq_quote(),
        get_rfq_maker_instrument_settings(),
        set_rfq_maker_instrument_settings(inst_type => "instType", data => "data"),
        reset_rfq_mmp(),
        set_rfq_mmp_config(time_interval => "timeInterval", frozen_interval => "frozenInterval", count_limit => "countLimit"),
        get_rfq_mmp_config(),
        cancel_rfq_batch_quotes(),
        cancel_all_rfq_quotes(),
        set_rfq_cancel_all_after(time_out => "timeOut"),
        /// API withdrawals and external transfers have no second confirmation; they execute on submit.
        create_withdrawal(ccy => "ccy", amt => "amt", dest => "dest", to_addr => "toAddr"),
        cancel_withdrawal(wd_id => "wdId"),
        /// API withdrawals and external transfers have no second confirmation; they execute on submit.
        create_fiat_withdrawal(payment_acct_id => "paymentAcctId", ccy => "ccy", amt => "amt", payment_method => "paymentMethod", client_id => "clientId"),
        cancel_fiat_withdrawal(ord_id => "ordId"),
        get_affiliate_performance_summary(),
        get_affiliate_invitee_detail(uid => "uid"),
        get_affiliate_invitee_list(),
        get_affiliate_links(),
        get_affiliate_co_inviters(),
        get_sub_affiliates(),
    ];
}
