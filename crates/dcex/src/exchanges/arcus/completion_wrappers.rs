use super::ArcusClient;
crate::exchanges::impl_exchange_method_wrappers! {
    @extend; ArcusClient;
    public [
        get_commission_rates(),
        check_referral_code(code => "code"),
        get_affiliate_claims(address => "address"),
        get_affiliate_leaderboard(),
        get_referrer(address => "address"),
        get_affiliate_claim(address => "address", id => "id"),
    ];
    private [
        /// API withdrawals and external transfers have no second confirmation; they execute on submit.
        create_withdrawal_signed(ethereum_address => "ethereumAddress", amount => "amount", nonce => "nonce", signature => "signature"),
        /// API withdrawals and external transfers have no second confirmation; they execute on submit.
        create_withdrawal(ethereum_address => "ethereumAddress", amount => "amount", nonce => "nonce"),
        claim_affiliate_commission(address => "address"),
        create_referral_code(address => "address", code => "code", kickback_bps => "kickbackBps"),
        get_affiliate_commissions(address => "address"),
        get_affiliate_info(address => "address"),
        get_referees(address => "address"),
        get_referral_code(address => "address"),
        get_invite_codes(address => "address"),
        redeem_invite_code(address => "address", invite_code => "inviteCode"),
        register_referral(address => "address", code => "code"),
        rename_referral_code(address => "address", code => "code"),
        revoke_referral_code(address => "address"),
        update_referral_kickback(address => "address", kickback_bps => "kickbackBps"),
    ];
}
