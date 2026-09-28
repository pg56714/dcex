use super::BinanceClient;
crate::exchanges::impl_exchange_method_wrappers! { @extend; BinanceClient; public []; private [
accept_options_block_order(block_order_matching_key => "blockOrderMatchingKey"),
get_options_account_block_trades(),
cancel_options_block_order(block_order_matching_key => "blockOrderMatchingKey"),
extend_options_block_order(block_order_matching_key => "blockOrderMatchingKey"),
create_options_block_order(liquidity => "liquidity",legs => "legs"),
get_options_block_order_details(block_order_matching_key => "blockOrderMatchingKey"),
get_options_block_orders(),
/// API withdrawals and external transfers have no second confirmation; they execute on submit.
withdraw_managed_sub_account(from_email => "fromEmail",asset => "asset",amount => "amount"),
disable_fast_withdraw_switch(),
enable_fast_withdraw_switch(),
/// API withdrawals and external transfers have no second confirmation; they execute on submit.
create_withdrawal(coin => "coin",address => "address",amount => "amount"),
/// API withdrawals and external transfers have no second confirmation; they execute on submit.
create_broker_withdrawal(address => "address",coin => "coin",amount => "amount",withdraw_order_id => "withdrawOrderId",questionnaire => "questionnaire",originator_pii => "originatorPii"),
submit_broker_deposit_questionnaire(sub_account_id => "subAccountId",deposit_id => "depositId",questionnaire => "questionnaire",beneficiary_pii => "beneficiaryPii"),
/// API withdrawals and external transfers have no second confirmation; they execute on submit.
create_travel_rule_withdrawal(coin => "coin",address => "address",amount => "amount",questionnaire => "questionnaire"),
]; }
