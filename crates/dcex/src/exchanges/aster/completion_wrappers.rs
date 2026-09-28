//! Wrappers for newly documented routes and explicit incomplete-spec pass-through.
use super::client::AsterClient;

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
