//! Offline route coverage for every Bybit REST dispatch name.
//!
//! Each case sends one request through `public_request`/`private_request`
//! against a local single-shot HTTP server and asserts the HTTP verb, the
//! official V5 path, and whether the request carried a Bybit signature.

use std::collections::BTreeSet;
use std::io::{Read, Write};
use std::net::{SocketAddr, TcpListener, TcpStream};
use std::thread;
use std::time::Duration;

use super::client::BybitClient;

struct RouteCase {
    public: bool,
    name: &'static str,
    params: &'static [(&'static str, &'static str)],
    verb: &'static str,
    path: &'static str,
}

const CASES: &[RouteCase] = &[
    RouteCase {
        public: true,
        name: "get_server_time",
        params: &[],
        verb: "GET",
        path: "/v5/market/time",
    },
    RouteCase {
        public: false,
        name: "get_fixed_loan_supply_contract_info",
        params: &[("supplyCurrency", "USDT")],
        verb: "GET",
        path: "/v5/crypto-loan-fixed/supply-contract-info",
    },
    RouteCase {
        public: true,
        name: "get_spot_lever_token_reference",
        params: &[("ltCoin", "BTC3L")],
        verb: "GET",
        path: "/v5/spot-lever-token/reference",
    },
    RouteCase {
        public: false,
        name: "get_spot_lever_token_order_record",
        params: &[],
        verb: "GET",
        path: "/v5/spot-lever-token/order-record",
    },
    RouteCase {
        public: false,
        name: "spot_lever_token_purchase",
        params: &[("ltCoin", "BTC3L"), ("ltAmount", "10")],
        verb: "POST",
        path: "/v5/spot-lever-token/purchase",
    },
    RouteCase {
        public: false,
        name: "spot_lever_token_redeem",
        params: &[("ltCoin", "BTC3L"), ("quantity", "1")],
        verb: "POST",
        path: "/v5/spot-lever-token/redeem",
    },
    RouteCase {
        public: false,
        name: "get_asset_withdraw_vasp_list",
        params: &[],
        verb: "GET",
        path: "/v5/asset/withdraw/vasp/list",
    },
    RouteCase {
        public: false,
        name: "get_asset_withdraw_query_address",
        params: &[],
        verb: "GET",
        path: "/v5/asset/withdraw/query-address",
    },
    RouteCase {
        public: false,
        name: "get_asset_withdraw_query_record",
        params: &[],
        verb: "GET",
        path: "/v5/asset/withdraw/query-record",
    },
    RouteCase {
        public: false,
        name: "get_crypto_loan_borrowable_collateralisable_number",
        params: &[("loanCurrency", "BTC"), ("collateralCurrency", "USDT")],
        verb: "GET",
        path: "/v5/crypto-loan/borrowable-collateralisable-number",
    },
    RouteCase {
        public: false,
        name: "crypto_loan_adjust_ltv",
        params: &[("orderId", "123"), ("amount", "1"), ("direction", "0")],
        verb: "POST",
        path: "/v5/crypto-loan/adjust-ltv",
    },
    RouteCase {
        public: true,
        name: "get_crypto_loan_collateral_data",
        params: &[],
        verb: "GET",
        path: "/v5/crypto-loan/collateral-data",
    },
    RouteCase {
        public: false,
        name: "get_crypto_loan_borrow_history",
        params: &[],
        verb: "GET",
        path: "/v5/crypto-loan/borrow-history",
    },
    RouteCase {
        public: true,
        name: "get_crypto_loan_loanable_data",
        params: &[],
        verb: "GET",
        path: "/v5/crypto-loan/loanable-data",
    },
    RouteCase {
        public: false,
        name: "get_crypto_loan_adjustment_history",
        params: &[],
        verb: "GET",
        path: "/v5/crypto-loan/adjustment-history",
    },
    RouteCase {
        public: false,
        name: "get_crypto_loan_max_collateral_amount",
        params: &[("orderId", "123")],
        verb: "GET",
        path: "/v5/crypto-loan/max-collateral-amount",
    },
    RouteCase {
        public: false,
        name: "get_crypto_loan_repayment_history",
        params: &[],
        verb: "GET",
        path: "/v5/crypto-loan/repayment-history",
    },
    RouteCase {
        public: false,
        name: "crypto_loan_repay",
        params: &[("orderId", "123"), ("amount", "1")],
        verb: "POST",
        path: "/v5/crypto-loan/repay",
    },
    RouteCase {
        public: false,
        name: "get_crypto_loan_ongoing_orders",
        params: &[],
        verb: "GET",
        path: "/v5/crypto-loan/ongoing-orders",
    },
    RouteCase {
        public: false,
        name: "get_spot_x_puzzle_project_list",
        params: &[("status", "1")],
        verb: "GET",
        path: "/v5/spot-x/puzzle/project/list",
    },
    RouteCase {
        public: false,
        name: "get_spot_x_token_splash_project_list",
        params: &[("status", "1")],
        verb: "GET",
        path: "/v5/spot-x/token-splash/project/list",
    },
    RouteCase {
        public: false,
        name: "get_spot_x_token_splash_user_activity_params",
        params: &[],
        verb: "GET",
        path: "/v5/spot-x/token-splash/user/activity-params",
    },
    RouteCase {
        public: false,
        name: "crypto_loan_common_adjust_ltv",
        params: &[("currency", "BTC"), ("amount", "1"), ("direction", "0")],
        verb: "POST",
        path: "/v5/crypto-loan-common/adjust-ltv",
    },
    RouteCase {
        public: true,
        name: "get_crypto_loan_common_collateral_data",
        params: &[],
        verb: "GET",
        path: "/v5/crypto-loan-common/collateral-data",
    },
    RouteCase {
        public: false,
        name: "get_crypto_loan_common_position",
        params: &[],
        verb: "GET",
        path: "/v5/crypto-loan-common/position",
    },
    RouteCase {
        public: false,
        name: "get_crypto_loan_fixed_available_inventory",
        params: &[("currency", "BTC"), ("term", "7"), ("annualRate", "0.02")],
        verb: "GET",
        path: "/v5/crypto-loan-fixed/available-inventory",
    },
    RouteCase {
        public: false,
        name: "get_crypto_loan_fixed_borrow_contract_info",
        params: &[],
        verb: "GET",
        path: "/v5/crypto-loan-fixed/borrow-contract-info",
    },
    RouteCase {
        public: true,
        name: "get_crypto_loan_fixed_borrow_order_quote",
        params: &[("orderCurrency", "USDT"), ("orderBy", "apy")],
        verb: "GET",
        path: "/v5/crypto-loan-fixed/borrow-order-quote",
    },
    RouteCase {
        public: false,
        name: "get_crypto_loan_fixed_borrow_order_info",
        params: &[],
        verb: "GET",
        path: "/v5/crypto-loan-fixed/borrow-order-info",
    },
    RouteCase {
        public: false,
        name: "crypto_loan_fixed_borrow",
        params: &[
            ("orderCurrency", "USDT"),
            ("orderAmount", "1"),
            ("annualRate", "0.02"),
            ("term", "7"),
            (
                "collateralList",
                "[{\"amount\":\"100\",\"currency\":\"USDT\"}]",
            ),
        ],
        verb: "POST",
        path: "/v5/crypto-loan-fixed/borrow",
    },
    RouteCase {
        public: false,
        name: "crypto_loan_fixed_borrow_order_cancel",
        params: &[("orderId", "123")],
        verb: "POST",
        path: "/v5/crypto-loan-fixed/borrow-order-cancel",
    },
    RouteCase {
        public: false,
        name: "crypto_loan_fixed_supply_order_cancel",
        params: &[("orderId", "123")],
        verb: "POST",
        path: "/v5/crypto-loan-fixed/supply-order-cancel",
    },
    RouteCase {
        public: false,
        name: "get_crypto_loan_fixed_renew_info",
        params: &[],
        verb: "GET",
        path: "/v5/crypto-loan-fixed/renew-info",
    },
    RouteCase {
        public: false,
        name: "crypto_loan_fixed_renew",
        params: &[
            ("loanId", "123"),
            (
                "collateralList",
                "[{\"amount\":\"100\",\"currency\":\"USDT\"}]",
            ),
        ],
        verb: "POST",
        path: "/v5/crypto-loan-fixed/renew",
    },
    RouteCase {
        public: false,
        name: "crypto_loan_fixed_repay_collateral",
        params: &[
            ("loanCurrency", "BTC"),
            ("collateralCoin", "USDT"),
            ("amount", "1"),
        ],
        verb: "POST",
        path: "/v5/crypto-loan-fixed/repay-collateral",
    },
    RouteCase {
        public: false,
        name: "get_crypto_loan_fixed_repayment_history",
        params: &[],
        verb: "GET",
        path: "/v5/crypto-loan-fixed/repayment-history",
    },
    RouteCase {
        public: false,
        name: "crypto_loan_fixed_fully_repay",
        params: &[("loanId", "123")],
        verb: "POST",
        path: "/v5/crypto-loan-fixed/fully-repay",
    },
    RouteCase {
        public: true,
        name: "get_crypto_loan_fixed_supply_order_quote",
        params: &[("orderCurrency", "USDT"), ("orderBy", "apy")],
        verb: "GET",
        path: "/v5/crypto-loan-fixed/supply-order-quote",
    },
    RouteCase {
        public: false,
        name: "get_crypto_loan_fixed_supply_order_info",
        params: &[],
        verb: "GET",
        path: "/v5/crypto-loan-fixed/supply-order-info",
    },
    RouteCase {
        public: false,
        name: "crypto_loan_fixed_supply",
        params: &[
            ("orderCurrency", "USDT"),
            ("orderAmount", "1"),
            ("annualRate", "0.02"),
            ("term", "7"),
        ],
        verb: "POST",
        path: "/v5/crypto-loan-fixed/supply",
    },
    RouteCase {
        public: false,
        name: "get_crypto_loan_flexible_available_inventory",
        params: &[("currency", "BTC")],
        verb: "GET",
        path: "/v5/crypto-loan-flexible/available-inventory",
    },
    RouteCase {
        public: false,
        name: "crypto_loan_flexible_borrow",
        params: &[
            ("loanCurrency", "BTC"),
            ("loanAmount", "1"),
            (
                "collateralList",
                "[{\"amount\":\"100\",\"currency\":\"USDT\"}]",
            ),
        ],
        verb: "POST",
        path: "/v5/crypto-loan-flexible/borrow",
    },
    RouteCase {
        public: false,
        name: "get_crypto_loan_flexible_borrow_history",
        params: &[],
        verb: "GET",
        path: "/v5/crypto-loan-flexible/borrow-history",
    },
    RouteCase {
        public: false,
        name: "crypto_loan_flexible_repay_collateral",
        params: &[
            ("loanCurrency", "BTC"),
            ("collateralCoin", "USDT"),
            ("amount", "1"),
        ],
        verb: "POST",
        path: "/v5/crypto-loan-flexible/repay-collateral",
    },
    RouteCase {
        public: false,
        name: "get_crypto_loan_flexible_repayment_history",
        params: &[],
        verb: "GET",
        path: "/v5/crypto-loan-flexible/repayment-history",
    },
    RouteCase {
        public: false,
        name: "crypto_loan_flexible_repay",
        params: &[("loanCurrency", "BTC"), ("amount", "1")],
        verb: "POST",
        path: "/v5/crypto-loan-flexible/repay",
    },
    RouteCase {
        public: false,
        name: "get_crypto_loan_flexible_ongoing_coin",
        params: &[],
        verb: "GET",
        path: "/v5/crypto-loan-flexible/ongoing-coin",
    },
    RouteCase {
        public: true,
        name: "get_crypto_loan_common_loanable_data",
        params: &[],
        verb: "GET",
        path: "/v5/crypto-loan-common/loanable-data",
    },
    RouteCase {
        public: false,
        name: "get_crypto_loan_common_adjustment_history",
        params: &[],
        verb: "GET",
        path: "/v5/crypto-loan-common/adjustment-history",
    },
    RouteCase {
        public: false,
        name: "crypto_loan_common_max_loan",
        params: &[("currency", "BTC")],
        verb: "POST",
        path: "/v5/crypto-loan-common/max-loan",
    },
    RouteCase {
        public: false,
        name: "get_crypto_loan_common_max_collateral_amount",
        params: &[("currency", "BTC")],
        verb: "GET",
        path: "/v5/crypto-loan-common/max-collateral-amount",
    },
    RouteCase {
        public: false,
        name: "get_all_api_rate_limits",
        params: &[],
        verb: "GET",
        path: "/v5/apilimit/query-all",
    },
    RouteCase {
        public: false,
        name: "get_api_rate_limit_cap",
        params: &[],
        verb: "GET",
        path: "/v5/apilimit/query-cap",
    },
    RouteCase {
        public: false,
        name: "get_api_rate_limits",
        params: &[("uids", "2")],
        verb: "GET",
        path: "/v5/apilimit/query",
    },
    RouteCase {
        public: false,
        name: "set_api_rate_limits",
        params: &[(
            "list",
            "[{\"uids\":\"2\",\"bizType\":\"DERIVATIVES\",\"rate\":10}]",
        )],
        verb: "POST",
        path: "/v5/apilimit/set",
    },
    RouteCase {
        public: false,
        name: "submit_deposit_information",
        params: &[
            ("depositId", "123"),
            ("questionnaire", "{\"test\":\"fixture\"}"),
        ],
        verb: "POST",
        path: "/v5/asset/travel-rule/deposit/submit",
    },
    RouteCase {
        public: true,
        name: "get_announcements",
        params: &[("locale", "en-US")],
        verb: "GET",
        path: "/v5/announcements/index",
    },
    RouteCase {
        public: false,
        name: "execute_small_balance_quote",
        params: &[("quoteId", "quote-1")],
        verb: "POST",
        path: "/v5/asset/covert/small-balance-execute",
    },
    RouteCase {
        public: false,
        name: "get_small_balance_history",
        params: &[],
        verb: "GET",
        path: "/v5/asset/covert/small-balance-history",
    },
    RouteCase {
        public: false,
        name: "request_small_balance_quote",
        params: &[
            ("accountType", "eb_convert_uta"),
            ("fromCoinList", "[\"BTC\",\"ETH\"]"),
            ("toCoin", "USDC"),
        ],
        verb: "POST",
        path: "/v5/asset/covert/get-quote",
    },
    RouteCase {
        public: false,
        name: "get_small_balance_coins",
        params: &[("accountType", "eb_convert_uta")],
        verb: "GET",
        path: "/v5/asset/covert/small-balance-list",
    },
    RouteCase {
        public: false,
        name: "get_convert_coins",
        params: &[("accountType", "eb_convert_uta")],
        verb: "GET",
        path: "/v5/asset/exchange/query-coin-list",
    },
    RouteCase {
        public: false,
        name: "get_convert_history",
        params: &[],
        verb: "GET",
        path: "/v5/asset/exchange/query-convert-history",
    },
    RouteCase {
        public: false,
        name: "get_sub_account_deposit_address",
        params: &[("coin", "USDT"), ("chainType", "ETH"), ("subMemberId", "2")],
        verb: "GET",
        path: "/v5/asset/deposit/query-sub-member-address",
    },
    RouteCase {
        public: false,
        name: "get_exchange_order_records",
        params: &[],
        verb: "GET",
        path: "/v5/asset/exchange/order-record",
    },
    RouteCase {
        public: true,
        name: "get_fee_group_info",
        params: &[("productType", "contract")],
        verb: "GET",
        path: "/v5/market/fee-group-info",
    },
    RouteCase {
        public: true,
        name: "get_index_price_components",
        params: &[("indexName", "BTCUSDT")],
        verb: "GET",
        path: "/v5/market/index-price-components",
    },
    RouteCase {
        public: true,
        name: "get_option_delivery_prices",
        params: &[("category", "option"), ("baseCoin", "BTC")],
        verb: "GET",
        path: "/v5/market/new-delivery-price",
    },
    RouteCase {
        public: true,
        name: "get_option_base_coins",
        params: &[],
        verb: "GET",
        path: "/v5/market/option-base-coins",
    },
    RouteCase {
        public: false,
        name: "get_pre_upgrade_closed_pnl",
        params: &[("category", "linear"), ("symbol", "BTCUSDT")],
        verb: "GET",
        path: "/v5/pre-upgrade/position/closed-pnl",
    },
    RouteCase {
        public: false,
        name: "get_pre_upgrade_delivery_records",
        params: &[("category", "option")],
        verb: "GET",
        path: "/v5/pre-upgrade/asset/delivery-record",
    },
    RouteCase {
        public: false,
        name: "get_pre_upgrade_executions",
        params: &[("category", "linear")],
        verb: "GET",
        path: "/v5/pre-upgrade/execution/list",
    },
    RouteCase {
        public: false,
        name: "get_pre_upgrade_order_history",
        params: &[("category", "linear")],
        verb: "GET",
        path: "/v5/pre-upgrade/order/history",
    },
    RouteCase {
        public: false,
        name: "get_pre_upgrade_settlement_records",
        params: &[("category", "linear")],
        verb: "GET",
        path: "/v5/pre-upgrade/asset/settlement-record",
    },
    RouteCase {
        public: false,
        name: "get_pre_upgrade_transaction_log",
        params: &[("category", "linear")],
        verb: "GET",
        path: "/v5/pre-upgrade/account/transaction-log",
    },
    RouteCase {
        public: false,
        name: "get_margin_currency_data",
        params: &[],
        verb: "GET",
        path: "/v5/spot-margin-trade/currency-data",
    },
    RouteCase {
        public: false,
        name: "create_sub_account_api_key",
        params: &[
            ("subuid", "2"),
            ("readOnly", "1"),
            ("permissions", "{\"Spot\":[\"SpotTrade\"]}"),
        ],
        verb: "POST",
        path: "/v5/user/create-sub-api",
    },
    RouteCase {
        public: false,
        name: "create_sub_account",
        params: &[("username", "trader123"), ("memberType", "1")],
        verb: "POST",
        path: "/v5/user/create-sub-member",
    },
    RouteCase {
        public: false,
        name: "set_sub_account_frozen",
        params: &[("subuid", "2"), ("frozen", "1")],
        verb: "POST",
        path: "/v5/user/frozen-sub-member",
    },
    RouteCase {
        public: false,
        name: "get_sub_account_api_keys",
        params: &[("subMemberId", "2")],
        verb: "GET",
        path: "/v5/user/sub-apikeys",
    },
    RouteCase {
        public: false,
        name: "modify_api_key",
        params: &[("confirm", "true"), ("readOnly", "1")],
        verb: "POST",
        path: "/v5/user/update-api",
    },
    RouteCase {
        public: false,
        name: "modify_sub_account_api_key",
        params: &[],
        verb: "POST",
        path: "/v5/user/update-sub-api",
    },
    RouteCase {
        public: false,
        name: "get_sub_accounts_paginated",
        params: &[],
        verb: "GET",
        path: "/v5/user/submembers",
    },
    RouteCase {
        public: false,
        name: "delete_api_key",
        params: &[("confirm", "true")],
        verb: "POST",
        path: "/v5/user/delete-api",
    },
    RouteCase {
        public: false,
        name: "delete_sub_account_api_key",
        params: &[],
        verb: "POST",
        path: "/v5/user/delete-sub-api",
    },
    RouteCase {
        public: false,
        name: "delete_sub_account",
        params: &[("subMemberId", "2")],
        verb: "POST",
        path: "/v5/user/del-submember",
    },
    RouteCase {
        public: false,
        name: "sign_trading_agreement",
        params: &[("categoryV2", "1"), ("agree", "true")],
        verb: "POST",
        path: "/v5/user/agreement",
    },
    RouteCase {
        public: false,
        name: "get_sub_accounts",
        params: &[],
        verb: "GET",
        path: "/v5/user/query-sub-members",
    },
    RouteCase {
        public: false,
        name: "get_member_wallet_types",
        params: &[],
        verb: "GET",
        path: "/v5/user/get-member-type",
    },
    RouteCase {
        public: false,
        name: "get_smp_group",
        params: &[],
        verb: "GET",
        path: "/v5/account/smp-group",
    },
    RouteCase {
        public: false,
        name: "get_trade_behavior_config",
        params: &[],
        verb: "GET",
        path: "/v5/account/user-setting-config",
    },
    RouteCase {
        public: false,
        name: "set_delta_mode",
        params: &[("deltaEnable", "1")],
        verb: "POST",
        path: "/v5/account/set-delta-mode",
    },
    RouteCase {
        public: false,
        name: "set_spot_hedging",
        params: &[("setHedgingMode", "ON")],
        verb: "POST",
        path: "/v5/account/set-hedging-mode",
    },
    RouteCase {
        public: false,
        name: "set_price_limit_behavior",
        params: &[("category", "spot"), ("modifyEnable", "true")],
        verb: "POST",
        path: "/v5/account/set-limit-px-action",
    },
    RouteCase {
        public: false,
        name: "get_closed_option_positions",
        params: &[("category", "option"), ("limit", "100")],
        verb: "GET",
        path: "/v5/position/get-closed-positions",
    },
    RouteCase {
        public: false,
        name: "get_move_position_history",
        params: &[
            ("category", "option"),
            ("status", "Filled"),
            ("limit", "200"),
        ],
        verb: "GET",
        path: "/v5/position/move-history",
    },
    RouteCase {
        public: false,
        name: "move_positions",
        params: &[
            ("fromUid", "1"),
            ("toUid", "2"),
            (
                "list",
                "[{\"category\":\"linear\",\"symbol\":\"BTCUSDT\",\"side\":\"Sell\",\"qty\":\"0.01\",\"price\":\"50000\"}]",
            ),
        ],
        verb: "POST",
        path: "/v5/position/move-positions",
    },
    RouteCase {
        public: false,
        name: "get_account_instruments",
        params: &[("category", "linear")],
        verb: "GET",
        path: "/v5/account/instruments-info",
    },
    RouteCase {
        public: false,
        name: "get_dcp_info",
        params: &[],
        verb: "GET",
        path: "/v5/account/query-dcp-info",
    },
    RouteCase {
        public: false,
        name: "get_coin_greeks",
        params: &[],
        verb: "GET",
        path: "/v5/asset/coin-greeks",
    },
    RouteCase {
        public: false,
        name: "repay_liability",
        params: &[],
        verb: "POST",
        path: "/v5/account/quick-repayment",
    },
    RouteCase {
        public: false,
        name: "set_collateral_coin",
        params: &[("coin", "BTC"), ("collateralSwitch", "ON")],
        verb: "POST",
        path: "/v5/account/set-collateral-switch",
    },
    RouteCase {
        public: false,
        name: "batch_set_collateral_coins",
        params: &[(
            "request",
            "[{\"coin\":\"BTC\",\"collateralSwitch\":\"ON\"}]",
        )],
        verb: "POST",
        path: "/v5/account/set-collateral-switch-batch",
    },
    RouteCase {
        public: false,
        name: "get_asset_overview",
        params: &[],
        verb: "GET",
        path: "/v5/asset/asset-overview",
    },
    RouteCase {
        public: false,
        name: "get_delivery_records",
        params: &[
            ("category", "linear"),
            ("startTime", "1700000000000"),
            ("endTime", "1700000060000"),
            ("limit", "10"),
        ],
        verb: "GET",
        path: "/v5/asset/delivery-record",
    },
    RouteCase {
        public: false,
        name: "get_settlement_records",
        params: &[
            ("category", "linear"),
            ("startTime", "1700000000000"),
            ("endTime", "1700000060000"),
            ("limit", "10"),
        ],
        verb: "GET",
        path: "/v5/asset/settlement-record",
    },
    RouteCase {
        public: false,
        name: "get_funding_account_history",
        params: &[
            ("createTimeFrom", "1700000000"),
            ("createTimeTo", "1700000600"),
            ("limit", "10"),
        ],
        verb: "GET",
        path: "/v5/asset/fundinghistory",
    },
    RouteCase {
        public: false,
        name: "request_convert_quote",
        params: &[
            ("accountType", "eb_convert_funding"),
            ("fromCoin", "ETH"),
            ("toCoin", "BTC"),
            ("requestCoin", "ETH"),
            ("requestAmount", "0.1"),
        ],
        verb: "POST",
        path: "/v5/asset/exchange/quote-apply",
    },
    RouteCase {
        public: false,
        name: "execute_convert_quote",
        params: &[("quoteTxId", "quote-1")],
        verb: "POST",
        path: "/v5/asset/exchange/convert-execute",
    },
    RouteCase {
        public: false,
        name: "get_convert_result",
        params: &[
            ("quoteTxId", "quote-1"),
            ("accountType", "eb_convert_funding"),
        ],
        verb: "GET",
        path: "/v5/asset/exchange/convert-result-query",
    },
    RouteCase {
        public: true,
        name: "get_full_orderbook",
        params: &[("category", "linear"), ("symbol", "BTCUSDT")],
        verb: "GET",
        path: "/v5/market/full_orderbook",
    },
    RouteCase {
        public: true,
        name: "get_rpi_orderbook",
        params: &[("symbol", "BTCUSDT"), ("limit", "10")],
        verb: "GET",
        path: "/v5/market/rpi_orderbook",
    },
    RouteCase {
        public: false,
        name: "confirm_pending_mmr",
        params: &[("category", "linear"), ("symbol", "BTCUSDT")],
        verb: "POST",
        path: "/v5/position/confirm-pending-mmr",
    },
    RouteCase {
        public: false,
        name: "get_position_symbol_info",
        params: &[("category", "linear")],
        verb: "GET",
        path: "/v5/position/symbol-info",
    },
    RouteCase {
        public: true,
        name: "get_system_status",
        params: &[],
        verb: "GET",
        path: "/v5/system/status",
    },
    RouteCase {
        public: false,
        name: "get_api_key_info",
        params: &[],
        verb: "GET",
        path: "/v5/user/query-api",
    },
    RouteCase {
        public: false,
        name: "get_option_asset_info",
        params: &[],
        verb: "GET",
        path: "/v5/account/option-asset-info",
    },
    RouteCase {
        public: false,
        name: "get_portfolio_margin_info",
        params: &[],
        verb: "GET",
        path: "/v5/asset/portfolio-margin",
    },
    RouteCase {
        public: false,
        name: "get_repayment_info",
        params: &[],
        verb: "GET",
        path: "/v5/account/pay-info",
    },
    RouteCase {
        public: false,
        name: "get_trade_analysis",
        params: &[("symbol", "BTCUSDT")],
        verb: "GET",
        path: "/v5/account/trade-info-for-analysis",
    },
    RouteCase {
        public: false,
        name: "get_total_members_assets",
        params: &[],
        verb: "GET",
        path: "/v5/asset/total-members-assets",
    },
    RouteCase {
        public: true,
        name: "get_mark_price_kline",
        params: &[("product_symbol", "BTC-USDT-SWAP"), ("interval", "1m")],
        verb: "GET",
        path: "/v5/market/mark-price-kline",
    },
    RouteCase {
        public: true,
        name: "get_index_price_kline",
        params: &[("product_symbol", "BTC-USDT-SWAP"), ("interval", "1m")],
        verb: "GET",
        path: "/v5/market/index-price-kline",
    },
    RouteCase {
        public: true,
        name: "get_premium_index_price_kline",
        params: &[("product_symbol", "BTC-USDT-SWAP"), ("interval", "1m")],
        verb: "GET",
        path: "/v5/market/premium-index-price-kline",
    },
    RouteCase {
        public: false,
        name: "set_spot_margin_leverage",
        params: &[("leverage", "4"), ("currency", "USDT")],
        verb: "POST",
        path: "/v5/spot-margin-trade/set-leverage",
    },
    RouteCase {
        public: false,
        name: "set_spot_margin_mode",
        params: &[("spotMarginMode", "1")],
        verb: "POST",
        path: "/v5/spot-margin-trade/switch-mode",
    },
    RouteCase {
        public: false,
        name: "create_strategy",
        params: &[
            ("category", "UTA_USDT"),
            ("product_symbol", "BTC-USDT-SWAP"),
            ("side", "Buy"),
            ("strategyType", "twap"),
            ("size", "1"),
            ("duration", "600"),
            ("interval", "30"),
            ("reduceOnly", "false"),
        ],
        verb: "POST",
        path: "/v5/strategy/create",
    },
    RouteCase {
        public: false,
        name: "stop_strategy",
        params: &[("strategyId", "s1")],
        verb: "POST",
        path: "/v5/strategy/stop",
    },
    RouteCase {
        public: false,
        name: "get_strategy_list",
        params: &[("pageSize", "50")],
        verb: "GET",
        path: "/v5/strategy/list",
    },
    RouteCase {
        public: false,
        name: "get_strategy_orders",
        params: &[("strategyId", "s1")],
        verb: "GET",
        path: "/v5/strategy/order-list",
    },
    RouteCase {
        public: true,
        name: "get_instruments_info",
        params: &[("category", "linear")],
        verb: "GET",
        path: "/v5/market/instruments-info",
    },
    RouteCase {
        public: true,
        name: "get_kline",
        params: &[("product_symbol", "BTC-USDT-SWAP"), ("interval", "1m")],
        verb: "GET",
        path: "/v5/market/kline",
    },
    RouteCase {
        public: true,
        name: "get_orderbook",
        params: &[("product_symbol", "BTC-USDT-SWAP")],
        verb: "GET",
        path: "/v5/market/orderbook",
    },
    RouteCase {
        public: true,
        name: "get_tickers",
        params: &[("category", "spot")],
        verb: "GET",
        path: "/v5/market/tickers",
    },
    RouteCase {
        public: true,
        name: "get_funding_rate_history",
        params: &[("product_symbol", "BTC-USDT-SWAP")],
        verb: "GET",
        path: "/v5/market/funding/history",
    },
    RouteCase {
        public: true,
        name: "get_public_trade_history",
        params: &[("category", "linear"), ("product_symbol", "BTC-USDT-SWAP")],
        verb: "GET",
        path: "/v5/market/recent-trade",
    },
    RouteCase {
        public: true,
        name: "get_open_interest",
        params: &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("intervalTime", "5min"),
        ],
        verb: "GET",
        path: "/v5/market/open-interest",
    },
    RouteCase {
        public: true,
        name: "get_long_short_ratio",
        params: &[("product_symbol", "BTC-USDT-SWAP"), ("period", "1h")],
        verb: "GET",
        path: "/v5/market/account-ratio",
    },
    RouteCase {
        public: true,
        name: "get_historical_volatility",
        params: &[("category", "option"), ("baseCoin", "BTC")],
        verb: "GET",
        path: "/v5/market/historical-volatility",
    },
    RouteCase {
        public: true,
        name: "get_insurance_pool",
        params: &[("coin", "USDT")],
        verb: "GET",
        path: "/v5/market/insurance",
    },
    RouteCase {
        public: true,
        name: "get_delivery_price",
        params: &[("category", "linear")],
        verb: "GET",
        path: "/v5/market/delivery-price",
    },
    RouteCase {
        public: true,
        name: "get_order_price_limit",
        params: &[("category", "linear"), ("product_symbol", "BTC-USDT-SWAP")],
        verb: "GET",
        path: "/v5/market/price-limit",
    },
    RouteCase {
        public: true,
        name: "get_adl_alert",
        params: &[("product_symbol", "BTC-USDT-SWAP")],
        verb: "GET",
        path: "/v5/market/adlAlert",
    },
    RouteCase {
        public: true,
        name: "get_risk_limit",
        params: &[("category", "linear")],
        verb: "GET",
        path: "/v5/market/risk-limit",
    },
    RouteCase {
        public: true,
        name: "get_spread_instruments",
        params: &[],
        verb: "GET",
        path: "/v5/spread/instrument",
    },
    RouteCase {
        public: true,
        name: "get_spread_orderbook",
        params: &[("symbol", "SOLUSDT_SOL/USDT")],
        verb: "GET",
        path: "/v5/spread/orderbook",
    },
    RouteCase {
        public: true,
        name: "get_spread_tickers",
        params: &[("symbol", "SOLUSDT_SOL/USDT")],
        verb: "GET",
        path: "/v5/spread/tickers",
    },
    RouteCase {
        public: true,
        name: "get_spread_recent_trades",
        params: &[("symbol", "SOLUSDT_SOL/USDT")],
        verb: "GET",
        path: "/v5/spread/recent-trade",
    },
    RouteCase {
        public: false,
        name: "place_order",
        params: &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("side", "Buy"),
            ("orderType", "Limit"),
            ("qty", "1"),
            ("price", "100"),
        ],
        verb: "POST",
        path: "/v5/order/create",
    },
    RouteCase {
        public: false,
        name: "place_market_order",
        params: &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("side", "Sell"),
            ("qty", "1"),
        ],
        verb: "POST",
        path: "/v5/order/create",
    },
    RouteCase {
        public: false,
        name: "place_market_buy_order",
        params: &[("product_symbol", "BTC-USDT-SWAP"), ("qty", "1")],
        verb: "POST",
        path: "/v5/order/create",
    },
    RouteCase {
        public: false,
        name: "place_market_sell_order",
        params: &[("product_symbol", "BTC-USDT-SWAP"), ("qty", "1")],
        verb: "POST",
        path: "/v5/order/create",
    },
    RouteCase {
        public: false,
        name: "place_limit_order",
        params: &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("side", "Buy"),
            ("qty", "1"),
            ("price", "100"),
        ],
        verb: "POST",
        path: "/v5/order/create",
    },
    RouteCase {
        public: false,
        name: "place_limit_buy_order",
        params: &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("qty", "1"),
            ("price", "100"),
        ],
        verb: "POST",
        path: "/v5/order/create",
    },
    RouteCase {
        public: false,
        name: "place_limit_sell_order",
        params: &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("qty", "1"),
            ("price", "100"),
        ],
        verb: "POST",
        path: "/v5/order/create",
    },
    RouteCase {
        public: false,
        name: "place_post_only_limit_order",
        params: &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("side", "Buy"),
            ("qty", "1"),
            ("price", "100"),
        ],
        verb: "POST",
        path: "/v5/order/create",
    },
    RouteCase {
        public: false,
        name: "place_post_only_limit_buy_order",
        params: &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("qty", "1"),
            ("price", "100"),
        ],
        verb: "POST",
        path: "/v5/order/create",
    },
    RouteCase {
        public: false,
        name: "place_post_only_limit_sell_order",
        params: &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("qty", "1"),
            ("price", "100"),
        ],
        verb: "POST",
        path: "/v5/order/create",
    },
    RouteCase {
        public: false,
        name: "pre_check_order",
        params: &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("side", "Buy"),
            ("orderType", "Limit"),
            ("qty", "1"),
            ("price", "100"),
        ],
        verb: "POST",
        path: "/v5/order/pre-check",
    },
    RouteCase {
        public: false,
        name: "amend_order",
        params: &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("orderId", "order-1"),
            ("price", "101"),
        ],
        verb: "POST",
        path: "/v5/order/amend",
    },
    RouteCase {
        public: false,
        name: "cancel_order",
        params: &[("product_symbol", "BTC-USDT-SWAP"), ("orderId", "order-1")],
        verb: "POST",
        path: "/v5/order/cancel",
    },
    RouteCase {
        public: false,
        name: "get_open_orders",
        params: &[
            ("category", "linear"),
            ("product_symbol", "BTC-USDT-SWAP"),
            ("limit", "20"),
        ],
        verb: "GET",
        path: "/v5/order/realtime",
    },
    RouteCase {
        public: false,
        name: "cancel_all_orders",
        params: &[("category", "linear"), ("product_symbol", "BTC-USDT-SWAP")],
        verb: "POST",
        path: "/v5/order/cancel-all",
    },
    RouteCase {
        public: false,
        name: "get_order_history",
        params: &[("category", "linear"), ("product_symbol", "BTC-USDT-SWAP")],
        verb: "GET",
        path: "/v5/order/history",
    },
    RouteCase {
        public: false,
        name: "get_execution_list",
        params: &[
            ("category", "linear"),
            ("product_symbol", "BTC-USDT-SWAP"),
            ("limit", "50"),
        ],
        verb: "GET",
        path: "/v5/execution/list",
    },
    RouteCase {
        public: false,
        name: "place_batch_order",
        params: &[
            (
                "request",
                "[{\"symbol\":\"BTCUSDT\",\"side\":\"Buy\",\"orderType\":\"Limit\",\"qty\":\"1\",\"price\":\"1\"}]",
            ),
            ("category", "linear"),
        ],
        verb: "POST",
        path: "/v5/order/create-batch",
    },
    RouteCase {
        public: false,
        name: "amend_batch_order",
        params: &[
            (
                "request",
                "[{\"symbol\":\"BTCUSDT\",\"side\":\"Buy\",\"orderType\":\"Limit\",\"qty\":\"1\",\"price\":\"1\"}]",
            ),
            ("category", "linear"),
        ],
        verb: "POST",
        path: "/v5/order/amend-batch",
    },
    RouteCase {
        public: false,
        name: "cancel_batch_orders",
        params: &[
            (
                "request",
                "[{\"symbol\":\"BTCUSDT\",\"side\":\"Buy\",\"orderType\":\"Limit\",\"qty\":\"1\",\"price\":\"1\"}]",
            ),
            ("category", "linear"),
        ],
        verb: "POST",
        path: "/v5/order/cancel-batch",
    },
    RouteCase {
        public: false,
        name: "set_disconnected_cancel_all",
        params: &[("timeWindow", "10")],
        verb: "POST",
        path: "/v5/order/disconnected-cancel-all",
    },
    RouteCase {
        public: false,
        name: "get_borrow_quota",
        params: &[("product_symbol", "BTC-USDT-SPOT"), ("side", "Buy")],
        verb: "GET",
        path: "/v5/order/spot-borrow-check",
    },
    RouteCase {
        public: false,
        name: "get_vip_margin_data",
        params: &[],
        verb: "GET",
        path: "/v5/spot-margin-trade/data",
    },
    RouteCase {
        public: false,
        name: "get_collateral",
        params: &[("currency", "BTC")],
        verb: "GET",
        path: "/v5/spot-margin-trade/collateral",
    },
    RouteCase {
        public: false,
        name: "get_historical_interest_rate",
        params: &[("currency", "USDT")],
        verb: "GET",
        path: "/v5/spot-margin-trade/interest-rate-history",
    },
    RouteCase {
        public: false,
        name: "get_status_and_leverage",
        params: &[],
        verb: "GET",
        path: "/v5/spot-margin-trade/state",
    },
    RouteCase {
        public: false,
        name: "get_margin_max_borrowable",
        params: &[("currency", "USDT")],
        verb: "GET",
        path: "/v5/spot-margin-trade/max-borrowable",
    },
    RouteCase {
        public: false,
        name: "get_margin_position_tiers",
        params: &[("currency", "USDT")],
        verb: "GET",
        path: "/v5/spot-margin-trade/position-tiers",
    },
    RouteCase {
        public: false,
        name: "get_margin_coin_state",
        params: &[("currency", "USDT")],
        verb: "GET",
        path: "/v5/spot-margin-trade/coinstate",
    },
    RouteCase {
        public: false,
        name: "get_margin_repayment_available_amount",
        params: &[("currency", "USDT")],
        verb: "GET",
        path: "/v5/spot-margin-trade/repayment-available-amount",
    },
    RouteCase {
        public: false,
        name: "set_margin_auto_repay_mode",
        params: &[("autoRepayMode", "1"), ("currency", "USDT")],
        verb: "POST",
        path: "/v5/spot-margin-trade/set-auto-repay-mode",
    },
    RouteCase {
        public: false,
        name: "get_margin_auto_repay_mode",
        params: &[("currency", "USDT")],
        verb: "GET",
        path: "/v5/spot-margin-trade/get-auto-repay-mode",
    },
    RouteCase {
        public: false,
        name: "get_fixed_borrow_quote",
        params: &[("orderCurrency", "USDT"), ("limit", "10")],
        verb: "GET",
        path: "/v5/spot-margin-trade/fixedborrow-order-quote",
    },
    RouteCase {
        public: false,
        name: "borrow_fixed_rate",
        params: &[
            ("orderCurrency", "USDT"),
            ("orderAmount", "100"),
            ("annualRate", "0.05"),
            ("term", "7"),
        ],
        verb: "POST",
        path: "/v5/spot-margin-trade/fixedborrow",
    },
    RouteCase {
        public: false,
        name: "renew_fixed_rate_borrow",
        params: &[("loanId", "loan-1")],
        verb: "POST",
        path: "/v5/spot-margin-trade/fixedborrow-renew",
    },
    RouteCase {
        public: false,
        name: "get_fixed_borrow_orders",
        params: &[("limit", "10")],
        verb: "GET",
        path: "/v5/spot-margin-trade/fixedborrow-order-info",
    },
    RouteCase {
        public: false,
        name: "get_fixed_borrow_contracts",
        params: &[("limit", "10")],
        verb: "GET",
        path: "/v5/spot-margin-trade/fixedborrow-contract-info",
    },
    RouteCase {
        public: false,
        name: "get_margin_liability",
        params: &[("currency", "USDT")],
        verb: "GET",
        path: "/v5/spot-margin-trade/liability",
    },
    RouteCase {
        public: false,
        name: "get_flexible_borrow_inventory",
        params: &[("currency", "USDT")],
        verb: "GET",
        path: "/v5/spot-margin-trade/flexible-available-inventory",
    },
    RouteCase {
        public: false,
        name: "get_fixed_borrow_inventory",
        params: &[("currency", "USDT"), ("term", "7"), ("annualRate", "0.05")],
        verb: "GET",
        path: "/v5/spot-margin-trade/fixed-available-inventory",
    },
    RouteCase {
        public: false,
        name: "place_spread_order",
        params: &[
            ("symbol", "SOLUSDT_SOL/USDT"),
            ("side", "Buy"),
            ("orderType", "Limit"),
            ("qty", "0.1"),
            ("price", "21"),
        ],
        verb: "POST",
        path: "/v5/spread/order/create",
    },
    RouteCase {
        public: false,
        name: "amend_spread_order",
        params: &[
            ("symbol", "SOLUSDT_SOL/USDT"),
            ("orderId", "spread-1"),
            ("price", "22"),
        ],
        verb: "POST",
        path: "/v5/spread/order/amend",
    },
    RouteCase {
        public: false,
        name: "cancel_spread_order",
        params: &[("orderId", "spread-1")],
        verb: "POST",
        path: "/v5/spread/order/cancel",
    },
    RouteCase {
        public: false,
        name: "cancel_all_spread_orders",
        params: &[("symbol", "SOLUSDT_SOL/USDT")],
        verb: "POST",
        path: "/v5/spread/order/cancel-all",
    },
    RouteCase {
        public: false,
        name: "get_spread_open_orders",
        params: &[],
        verb: "GET",
        path: "/v5/spread/order/realtime",
    },
    RouteCase {
        public: false,
        name: "get_spread_order_history",
        params: &[],
        verb: "GET",
        path: "/v5/spread/order/history",
    },
    RouteCase {
        public: false,
        name: "get_spread_trade_history",
        params: &[],
        verb: "GET",
        path: "/v5/spread/execution/list",
    },
    RouteCase {
        public: false,
        name: "get_spread_max_qty",
        params: &[
            ("symbol", "SOLUSDT_SOL/USDT"),
            ("side", "1"),
            ("orderPrice", "21"),
        ],
        verb: "GET",
        path: "/v5/spread/max-qty",
    },
    RouteCase {
        public: false,
        name: "get_positions",
        params: &[
            ("category", "linear"),
            ("product_symbol", "BTC-USDT-SWAP"),
            ("limit", "20"),
        ],
        verb: "GET",
        path: "/v5/position/list",
    },
    RouteCase {
        public: false,
        name: "set_leverage",
        params: &[("product_symbol", "BTC-USDT-SWAP"), ("leverage", "5")],
        verb: "POST",
        path: "/v5/position/set-leverage",
    },
    RouteCase {
        public: false,
        name: "switch_position_mode",
        params: &[
            ("mode", "3"),
            ("product_symbol", "BTC-USDT-SWAP"),
            ("category", "linear"),
        ],
        verb: "POST",
        path: "/v5/position/switch-mode",
    },
    RouteCase {
        public: false,
        name: "set_trading_stop",
        params: &[
            ("product_symbol", "BTC-USDT-SWAP"),
            ("tpslMode", "Full"),
            ("positionIdx", "0"),
            ("takeProfit", "120"),
        ],
        verb: "POST",
        path: "/v5/position/trading-stop",
    },
    RouteCase {
        public: false,
        name: "add_position_margin",
        params: &[("product_symbol", "BTC-USDT-SWAP"), ("margin", "10")],
        verb: "POST",
        path: "/v5/position/add-margin",
    },
    RouteCase {
        public: false,
        name: "set_auto_add_margin",
        params: &[("product_symbol", "BTC-USDT-SWAP"), ("autoAddMargin", "1")],
        verb: "POST",
        path: "/v5/position/set-auto-add-margin",
    },
    RouteCase {
        public: false,
        name: "get_closed_pnl",
        params: &[
            ("category", "linear"),
            ("product_symbol", "BTC-USDT-SWAP"),
            ("limit", "20"),
        ],
        verb: "GET",
        path: "/v5/position/closed-pnl",
    },
    RouteCase {
        public: false,
        name: "get_wallet_balance",
        params: &[("coin", "USDT")],
        verb: "GET",
        path: "/v5/account/wallet-balance",
    },
    RouteCase {
        public: false,
        name: "get_transferable_amount",
        params: &[("coins", "USDT,BTC")],
        verb: "GET",
        path: "/v5/account/withdrawal",
    },
    RouteCase {
        public: false,
        name: "upgrade_to_unified_trading_account",
        params: &[],
        verb: "POST",
        path: "/v5/account/upgrade-to-uta",
    },
    RouteCase {
        public: false,
        name: "get_borrow_history",
        params: &[("coin", "USDT"), ("limit", "20")],
        verb: "GET",
        path: "/v5/account/borrow-history",
    },
    RouteCase {
        public: false,
        name: "get_collateral_info",
        params: &[("currency", "USDT")],
        verb: "GET",
        path: "/v5/account/collateral-info",
    },
    RouteCase {
        public: false,
        name: "manual_borrow",
        params: &[("coin", "USDT"), ("amount", "10")],
        verb: "POST",
        path: "/v5/account/borrow",
    },
    RouteCase {
        public: false,
        name: "manual_repay",
        params: &[
            ("coin", "USDT"),
            ("amount", "10"),
            ("repaymentType", "FLEXIBLE"),
        ],
        verb: "POST",
        path: "/v5/account/repay",
    },
    RouteCase {
        public: false,
        name: "manual_repay_without_conversion",
        params: &[
            ("coin", "USDT"),
            ("amount", "10"),
            ("repaymentType", "FLEXIBLE"),
        ],
        verb: "POST",
        path: "/v5/account/no-convert-repay",
    },
    RouteCase {
        public: false,
        name: "get_spot_fee_rates",
        params: &[("product_symbol", "BTC-USDT-SPOT")],
        verb: "GET",
        path: "/v5/account/fee-rate",
    },
    RouteCase {
        public: false,
        name: "get_linear_fee_rates",
        params: &[("product_symbol", "BTC-USDT-SWAP")],
        verb: "GET",
        path: "/v5/account/fee-rate",
    },
    RouteCase {
        public: false,
        name: "get_inverse_fee_rates",
        params: &[("product_symbol", "BTC-USD-SWAP")],
        verb: "GET",
        path: "/v5/account/fee-rate",
    },
    RouteCase {
        public: false,
        name: "get_option_fee_rates",
        params: &[("baseCoin", "BTC")],
        verb: "GET",
        path: "/v5/account/fee-rate",
    },
    RouteCase {
        public: false,
        name: "get_account_info",
        params: &[],
        verb: "GET",
        path: "/v5/account/info",
    },
    RouteCase {
        public: false,
        name: "get_transaction_log",
        params: &[("accountType", "UNIFIED"), ("limit", "20")],
        verb: "GET",
        path: "/v5/account/transaction-log",
    },
    RouteCase {
        public: false,
        name: "set_margin_mode",
        params: &[("margin_mode", "REGULAR_MARGIN")],
        verb: "POST",
        path: "/v5/account/set-margin-mode",
    },
    RouteCase {
        public: false,
        name: "get_coin_info",
        params: &[("coin", "USDT")],
        verb: "GET",
        path: "/v5/asset/coin/query-info",
    },
    RouteCase {
        public: false,
        name: "get_sub_uid",
        params: &[],
        verb: "GET",
        path: "/v5/asset/transfer/query-sub-member-list",
    },
    RouteCase {
        public: false,
        name: "get_spot_asset_info",
        params: &[("coin", "USDT")],
        verb: "GET",
        path: "/v5/asset/transfer/query-asset-info",
    },
    RouteCase {
        public: false,
        name: "get_coins_balance",
        params: &[("accountType", "FUND")],
        verb: "GET",
        path: "/v5/asset/transfer/query-account-coins-balance",
    },
    RouteCase {
        public: false,
        name: "get_coin_balance",
        params: &[("accountType", "FUND"), ("coin", "USDT")],
        verb: "GET",
        path: "/v5/asset/transfer/query-account-coin-balance",
    },
    RouteCase {
        public: false,
        name: "get_withdrawable_amount",
        params: &[("coin", "USDT")],
        verb: "GET",
        path: "/v5/asset/withdraw/withdrawable-amount",
    },
    RouteCase {
        public: false,
        name: "get_internal_transfer_records",
        params: &[("limit", "20")],
        verb: "GET",
        path: "/v5/asset/transfer/query-inter-transfer-list",
    },
    RouteCase {
        public: false,
        name: "get_transferable_coin",
        params: &[("fromAccountType", "FUND"), ("toAccountType", "UNIFIED")],
        verb: "GET",
        path: "/v5/asset/transfer/query-transfer-coin-list",
    },
    RouteCase {
        public: false,
        name: "create_internal_transfer",
        params: &[
            ("coin", "USDT"),
            ("amount", "1"),
            ("fromAccountType", "FUND"),
            ("toAccountType", "UNIFIED"),
            ("transferId", "42b3f4f1-6e4d-4f7e-9c5d-0c5e1f0a1b2c"),
        ],
        verb: "POST",
        path: "/v5/asset/transfer/inter-transfer",
    },
    RouteCase {
        public: false,
        name: "create_universal_transfer",
        params: &[
            ("coin", "USDT"),
            ("amount", "1"),
            ("fromMemberId", "1"),
            ("toMemberId", "2"),
            ("fromAccountType", "FUND"),
            ("toAccountType", "UNIFIED"),
            ("transferId", "42b3f4f1-6e4d-4f7e-9c5d-0c5e1f0a1b2d"),
        ],
        verb: "POST",
        path: "/v5/asset/transfer/universal-transfer",
    },
    RouteCase {
        public: false,
        name: "get_universal_transfer_records",
        params: &[("limit", "20")],
        verb: "GET",
        path: "/v5/asset/transfer/query-universal-transfer-list",
    },
    RouteCase {
        public: false,
        name: "set_deposit_account",
        params: &[("accountType", "FUND")],
        verb: "POST",
        path: "/v5/asset/deposit/deposit-to-account",
    },
    RouteCase {
        public: false,
        name: "get_deposit_records",
        params: &[("limit", "20")],
        verb: "GET",
        path: "/v5/asset/deposit/query-record",
    },
    RouteCase {
        public: false,
        name: "get_sub_deposit_records",
        params: &[("subMemberId", "123"), ("limit", "20")],
        verb: "GET",
        path: "/v5/asset/deposit/query-sub-member-record",
    },
    RouteCase {
        public: false,
        name: "get_internal_deposit_records",
        params: &[("limit", "20")],
        verb: "GET",
        path: "/v5/asset/deposit/query-internal-record",
    },
    RouteCase {
        public: false,
        name: "get_master_deposit_address",
        params: &[("coin", "USDT")],
        verb: "GET",
        path: "/v5/asset/deposit/query-address",
    },
    RouteCase {
        public: true,
        name: "get_earn_products",
        params: &[("category", "FlexibleSaving")],
        verb: "GET",
        path: "/v5/earn/product",
    },
    RouteCase {
        public: true,
        name: "get_advanced_earn_products",
        params: &[("category", "DualAssets")],
        verb: "GET",
        path: "/v5/earn/advance/product",
    },
    RouteCase {
        public: true,
        name: "get_advanced_earn_product_quote",
        params: &[("category", "DualAssets"), ("productId", "product-1")],
        verb: "GET",
        path: "/v5/earn/advance/product-extra-info",
    },
    RouteCase {
        public: true,
        name: "get_liquidity_mining_products",
        params: &[],
        verb: "GET",
        path: "/v5/earn/liquidity-mining/product",
    },
    RouteCase {
        public: true,
        name: "get_fixed_earn_products",
        params: &[],
        verb: "GET",
        path: "/v5/earn/fixed-term/product",
    },
    RouteCase {
        public: true,
        name: "get_hold_to_earn_products",
        params: &[],
        verb: "GET",
        path: "/v5/earn/hold-to-earn/product",
    },
    RouteCase {
        public: true,
        name: "get_byusdt_product",
        params: &[],
        verb: "GET",
        path: "/v5/earn/token/product",
    },
    RouteCase {
        public: true,
        name: "get_byusdt_apr_history",
        params: &[("range", "1")],
        verb: "GET",
        path: "/v5/earn/token/history-apr",
    },
    RouteCase {
        public: true,
        name: "get_rwa_earn_products",
        params: &[("coin", "USDT")],
        verb: "GET",
        path: "/v5/earn/rwa/product",
    },
    RouteCase {
        public: true,
        name: "get_rwa_earn_nav_chart",
        params: &[("productId", "7")],
        verb: "GET",
        path: "/v5/earn/rwa/nav-chart",
    },
    RouteCase {
        public: true,
        name: "get_earn_apr_history",
        params: &[("category", "OnChain"), ("productId", "product-1")],
        verb: "GET",
        path: "/v5/earn/apr-history",
    },
    RouteCase {
        public: true,
        name: "get_launchpool_projects",
        params: &[("status", "1")],
        verb: "GET",
        path: "/v5/spot-x/launchpool/project/list",
    },
    RouteCase {
        public: false,
        name: "place_earn_order",
        params: &[
            ("category", "FlexibleSaving"),
            ("orderType", "Stake"),
            ("accountType", "FUND"),
            ("amount", "1"),
            ("coin", "USDT"),
            ("productId", "430"),
            ("orderLinkId", "earn-1"),
        ],
        verb: "POST",
        path: "/v5/earn/place-order",
    },
    RouteCase {
        public: false,
        name: "get_earn_order_history",
        params: &[("category", "FlexibleSaving")],
        verb: "GET",
        path: "/v5/earn/order",
    },
    RouteCase {
        public: false,
        name: "get_earn_positions",
        params: &[("category", "FlexibleSaving")],
        verb: "GET",
        path: "/v5/earn/position",
    },
    RouteCase {
        public: false,
        name: "get_earn_yield_history",
        params: &[("category", "FlexibleSaving")],
        verb: "GET",
        path: "/v5/earn/yield",
    },
    RouteCase {
        public: false,
        name: "get_earn_hourly_yield_history",
        params: &[("category", "FlexibleSaving")],
        verb: "GET",
        path: "/v5/earn/hourly-yield",
    },
    RouteCase {
        public: false,
        name: "get_earn_coupons",
        params: &[("category", "FlexibleSaving")],
        verb: "GET",
        path: "/v5/earn/coupons",
    },
    RouteCase {
        public: false,
        name: "set_earn_auto_reinvest",
        params: &[
            ("category", "OnChain"),
            ("productId", "430"),
            ("positionId", "5001"),
            ("autoReinvest", "1"),
        ],
        verb: "POST",
        path: "/v5/earn/position/modify",
    },
    RouteCase {
        public: false,
        name: "place_advanced_earn_order",
        params: &[
            ("category", "DualAssets"),
            ("productId", "product-2"),
            ("orderType", "Stake"),
            ("accountType", "FUND"),
            ("orderLinkId", "adv-1"),
            ("amount", "10"),
            ("coin", "USDT"),
            (
                "dualAssetsExtra",
                "{\"orderDirection\":\"Buy\",\"selectPrice\":\"1\",\"apyE8\":\"1\"}",
            ),
        ],
        verb: "POST",
        path: "/v5/earn/advance/place-order",
    },
    RouteCase {
        public: false,
        name: "get_advanced_earn_positions",
        params: &[("category", "DualAssets")],
        verb: "GET",
        path: "/v5/earn/advance/position",
    },
    RouteCase {
        public: false,
        name: "get_advanced_earn_orders",
        params: &[("category", "DualAssets")],
        verb: "GET",
        path: "/v5/earn/advance/order",
    },
    RouteCase {
        public: false,
        name: "get_advanced_earn_redeem_estimates",
        params: &[("category", "SmartLeverage"), ("positionIds", "pos-1")],
        verb: "GET",
        path: "/v5/earn/advance/get-redeem-est-amount-list",
    },
    RouteCase {
        public: false,
        name: "get_double_win_leverage",
        params: &[
            ("productId", "product-3"),
            ("initialPrice", "100"),
            ("lowerPrice", "90"),
            ("upperPrice", "110"),
        ],
        verb: "GET",
        path: "/v5/earn/advance/double-win-leverage",
    },
    RouteCase {
        public: false,
        name: "get_liquidity_mining_positions",
        params: &[],
        verb: "GET",
        path: "/v5/earn/liquidity-mining/position",
    },
    RouteCase {
        public: false,
        name: "get_liquidity_mining_orders",
        params: &[],
        verb: "GET",
        path: "/v5/earn/liquidity-mining/order",
    },
    RouteCase {
        public: false,
        name: "get_liquidity_mining_yield_records",
        params: &[],
        verb: "GET",
        path: "/v5/earn/liquidity-mining/yield-records",
    },
    RouteCase {
        public: false,
        name: "get_liquidity_mining_liquidation_records",
        params: &[],
        verb: "GET",
        path: "/v5/earn/liquidity-mining/liquidation-records",
    },
    RouteCase {
        public: false,
        name: "add_liquidity_mining",
        params: &[
            ("productId", "36"),
            ("orderLinkId", "lm-1"),
            ("quoteAmount", "200"),
            ("quoteAccountType", "FUND"),
            ("leverage", "2"),
        ],
        verb: "POST",
        path: "/v5/earn/liquidity-mining/add-liquidity",
    },
    RouteCase {
        public: false,
        name: "remove_liquidity_mining",
        params: &[
            ("productId", "36"),
            ("orderLinkId", "lm-2"),
            ("positionId", "5001"),
            ("removeRate", "50"),
        ],
        verb: "POST",
        path: "/v5/earn/liquidity-mining/remove-liquidity",
    },
    RouteCase {
        public: false,
        name: "reinvest_liquidity_mining",
        params: &[
            ("productId", "36"),
            ("orderLinkId", "lm-3"),
            ("positionId", "5001"),
        ],
        verb: "POST",
        path: "/v5/earn/liquidity-mining/reinvest",
    },
    RouteCase {
        public: false,
        name: "add_liquidity_mining_margin",
        params: &[
            ("productId", "36"),
            ("orderLinkId", "lm-4"),
            ("positionId", "5001"),
            ("amount", "10"),
            ("quoteAccountType", "FUND"),
        ],
        verb: "POST",
        path: "/v5/earn/liquidity-mining/add-margin",
    },
    RouteCase {
        public: false,
        name: "claim_liquidity_mining_interest",
        params: &[("productId", "36")],
        verb: "POST",
        path: "/v5/earn/liquidity-mining/claim-interest",
    },
    RouteCase {
        public: false,
        name: "get_fixed_earn_positions",
        params: &[],
        verb: "GET",
        path: "/v5/earn/fixed-term/position",
    },
    RouteCase {
        public: false,
        name: "get_fixed_earn_orders",
        params: &[],
        verb: "GET",
        path: "/v5/earn/fixed-term/order",
    },
    RouteCase {
        public: false,
        name: "place_fixed_earn_order",
        params: &[
            ("productId", "fixed-1"),
            ("category", "FixedTermSaving"),
            ("coin", "USDT"),
            ("amount", "10"),
            ("accountType", "FUND"),
            ("orderLinkId", "fixed-link-1"),
        ],
        verb: "POST",
        path: "/v5/earn/fixed-term/place-order",
    },
    RouteCase {
        public: false,
        name: "redeem_fixed_earn",
        params: &[
            ("productId", "fixed-1"),
            ("category", "FundPool"),
            ("positionId", "pos-1"),
        ],
        verb: "POST",
        path: "/v5/earn/fixed-term/redeem",
    },
    RouteCase {
        public: false,
        name: "set_fixed_earn_auto_invest",
        params: &[
            ("productId", "fixed-1"),
            ("category", "FixedTermSaving"),
            ("positionId", "pos-1"),
            ("status", "Enable"),
        ],
        verb: "POST",
        path: "/v5/earn/fixed-term/position/auto-invest",
    },
    RouteCase {
        public: false,
        name: "get_hold_to_earn_yield_history",
        params: &[("limit", "20")],
        verb: "GET",
        path: "/v5/earn/hold-to-earn/yield-history",
    },
    RouteCase {
        public: false,
        name: "get_byusdt_orders",
        params: &[],
        verb: "GET",
        path: "/v5/earn/token/order",
    },
    RouteCase {
        public: false,
        name: "get_byusdt_position",
        params: &[],
        verb: "GET",
        path: "/v5/earn/token/position",
    },
    RouteCase {
        public: false,
        name: "get_byusdt_daily_yield",
        params: &[],
        verb: "GET",
        path: "/v5/earn/token/yield",
    },
    RouteCase {
        public: false,
        name: "get_byusdt_hourly_yield",
        params: &[],
        verb: "GET",
        path: "/v5/earn/token/hourly-yield",
    },
    RouteCase {
        public: false,
        name: "place_byusdt_order",
        params: &[
            ("orderType", "Mint"),
            ("amount", "10"),
            ("accountType", "FlexibleSaving"),
            ("orderLinkId", "by-1"),
        ],
        verb: "POST",
        path: "/v5/earn/token/place-order",
    },
    RouteCase {
        public: false,
        name: "get_rwa_earn_positions",
        params: &[],
        verb: "GET",
        path: "/v5/earn/rwa/position",
    },
    RouteCase {
        public: false,
        name: "get_rwa_earn_orders",
        params: &[],
        verb: "GET",
        path: "/v5/earn/rwa/order",
    },
    RouteCase {
        public: false,
        name: "place_rwa_earn_order",
        params: &[
            ("productId", "7"),
            ("orderType", "Stake"),
            ("coin", "USDT"),
            ("orderLinkId", "rwa-link-1"),
            ("stakeAmount", "10"),
            ("accountType", "FUND"),
        ],
        verb: "POST",
        path: "/v5/earn/rwa/place-order",
    },
    RouteCase {
        public: false,
        name: "get_launchpool_current_staking",
        params: &[],
        verb: "GET",
        path: "/v5/spot-x/launchpool/user/current-staking",
    },
    RouteCase {
        public: false,
        name: "get_launchpool_activity_log",
        params: &[],
        verb: "POST",
        path: "/v5/spot-x/launchpool/user/activity-log",
    },
    RouteCase {
        public: false,
        name: "get_launchpool_history",
        params: &[],
        verb: "POST",
        path: "/v5/spot-x/launchpool/user/history",
    },
    RouteCase {
        public: false,
        name: "get_rfq_public_trades",
        params: &[("limit", "20")],
        verb: "GET",
        path: "/v5/rfq/public-trades",
    },
    RouteCase {
        public: false,
        name: "get_rfq_config",
        params: &[],
        verb: "GET",
        path: "/v5/rfq/config",
    },
    RouteCase {
        public: false,
        name: "create_rfq",
        params: &[
            ("counterparties", "[\"desk\"]"),
            (
                "list",
                "[{\"category\":\"option\",\"symbol\":\"BTC-C\",\"side\":\"Buy\",\"qty\":\"1\"}]",
            ),
        ],
        verb: "POST",
        path: "/v5/rfq/create-rfq",
    },
    RouteCase {
        public: false,
        name: "cancel_rfq",
        params: &[("rfqId", "rfq-1")],
        verb: "POST",
        path: "/v5/rfq/cancel-rfq",
    },
    RouteCase {
        public: false,
        name: "cancel_all_rfqs",
        params: &[],
        verb: "POST",
        path: "/v5/rfq/cancel-all-rfq",
    },
    RouteCase {
        public: false,
        name: "accept_other_rfq_quote",
        params: &[("rfqId", "rfq-1")],
        verb: "POST",
        path: "/v5/rfq/accept-other-quote",
    },
    RouteCase {
        public: false,
        name: "create_rfq_quote",
        params: &[
            ("rfqId", "rfq-1"),
            (
                "quoteBuyList",
                "[{\"category\":\"option\",\"symbol\":\"BTC-C\",\"price\":\"1\"}]",
            ),
        ],
        verb: "POST",
        path: "/v5/rfq/create-quote",
    },
    RouteCase {
        public: false,
        name: "execute_rfq_quote",
        params: &[
            ("rfqId", "rfq-1"),
            ("quoteId", "quote-1"),
            ("quoteSide", "Buy"),
        ],
        verb: "POST",
        path: "/v5/rfq/execute-quote",
    },
    RouteCase {
        public: false,
        name: "cancel_rfq_quote",
        params: &[("quoteId", "quote-1")],
        verb: "POST",
        path: "/v5/rfq/cancel-quote",
    },
    RouteCase {
        public: false,
        name: "cancel_all_rfq_quotes",
        params: &[],
        verb: "POST",
        path: "/v5/rfq/cancel-all-quotes",
    },
    RouteCase {
        public: false,
        name: "get_realtime_rfqs",
        params: &[],
        verb: "GET",
        path: "/v5/rfq/rfq-realtime",
    },
    RouteCase {
        public: false,
        name: "get_rfqs",
        params: &[],
        verb: "GET",
        path: "/v5/rfq/rfq-list",
    },
    RouteCase {
        public: false,
        name: "get_rfq_details",
        params: &[],
        verb: "GET",
        path: "/v5/rfq/rfq-detail-list",
    },
    RouteCase {
        public: false,
        name: "get_realtime_rfq_quotes",
        params: &[],
        verb: "GET",
        path: "/v5/rfq/quote-realtime",
    },
    RouteCase {
        public: false,
        name: "get_rfq_quotes",
        params: &[],
        verb: "GET",
        path: "/v5/rfq/quote-list",
    },
    RouteCase {
        public: false,
        name: "get_rfq_trade_history",
        params: &[],
        verb: "GET",
        path: "/v5/rfq/trade-list",
    },
];

fn single_shot_server() -> (SocketAddr, thread::JoinHandle<String>) {
    let listener = TcpListener::bind("127.0.0.1:0").expect("bind");
    let address = listener.local_addr().expect("address");
    let handle = thread::spawn(move || {
        let (mut stream, _) = listener.accept().expect("accept");
        let mut buffer = [0u8; 8192];
        let mut request = Vec::new();
        loop {
            let size = stream.read(&mut buffer).expect("read");
            if size == 0 {
                return String::new();
            }
            request.extend_from_slice(&buffer[..size]);
            let text = String::from_utf8_lossy(&request);
            if let Some((head, body)) = text.split_once("\r\n\r\n") {
                let content_length = head
                    .lines()
                    .find_map(|line| {
                        line.to_ascii_lowercase()
                            .strip_prefix("content-length:")
                            .and_then(|value| value.trim().parse::<usize>().ok())
                    })
                    .unwrap_or(0);
                if body.len() >= content_length {
                    break;
                }
            }
        }
        let body = r#"{"retCode":0,"retMsg":"OK","result":{}}"#;
        let response = format!(
            "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n{}",
            body.len(),
            body
        );
        stream.write_all(response.as_bytes()).expect("write");
        String::from_utf8_lossy(&request).into_owned()
    });
    (address, handle)
}

fn client(base_url: String) -> BybitClient {
    BybitClient::with_base_url(
        Some("api-key".to_string()),
        Some("api-secret".to_string()),
        5_000,
        false,
        Duration::from_secs(5),
        base_url,
    )
    .expect("client")
}

fn params(case: &RouteCase) -> Vec<(String, String)> {
    case.params
        .iter()
        .map(|(key, value)| ((*key).to_string(), (*value).to_string()))
        .collect()
}

#[tokio::test]
async fn every_dispatch_name_hits_its_official_route() {
    let mut failures = Vec::new();
    for case in CASES {
        let (address, handle) = single_shot_server();
        let client = client(format!("http://{address}"));
        let result = if case.public {
            client.public_request(case.name, params(case)).await
        } else {
            client.private_request(case.name, params(case)).await
        };
        if let Err(error) = result {
            // The request never reached the server; connect once so the
            // server thread returns from `accept` and can be joined.
            drop(TcpStream::connect(address));
            let _ = handle.join();
            failures.push(format!("{}: request failed: {error}", case.name));
            continue;
        }
        let request = handle.join().expect("server");
        let request_line = request.lines().next().unwrap_or_default();
        let target = request_line.split(' ').nth(1).unwrap_or_default();
        let path = target.split('?').next().unwrap_or_default();
        let verb = request_line.split(' ').next().unwrap_or_default();
        if (verb, path) != (case.verb, case.path) {
            failures.push(format!(
                "{}: expected {} {}, got {verb} {path}",
                case.name, case.verb, case.path
            ));
        }
        let signed = request.to_ascii_lowercase().contains("\r\nx-bapi-sign:");
        if signed == case.public {
            failures.push(format!(
                "{}: expected signed={}, got signed={signed}",
                case.name, !case.public
            ));
        }
        if verb == "GET" && !request.ends_with("\r\n\r\n") {
            failures.push(format!("{}: GET request carried a body", case.name));
        }
    }
    assert!(failures.is_empty(), "{failures:#?}");
}

#[test]
fn every_endpoint_constant_has_a_route_case() {
    let source = [
        include_str!("endpoints.rs"),
        include_str!("risk_endpoints.rs"),
        include_str!("strategy.rs"),
        include_str!("market.rs"),
        include_str!("account.rs"),
    ]
    .join("\n");
    let constants: BTreeSet<&str> = source
        .split('"')
        .filter(|segment| segment.starts_with("/v5/"))
        .collect();
    let covered: BTreeSet<&str> = CASES.iter().map(|case| case.path).collect();
    let missing: Vec<&&str> = constants
        .iter()
        .filter(|path| **path != "/v5/market/time" && !covered.contains(**path))
        .collect();
    assert!(
        missing.is_empty(),
        "endpoint constants without a route case: {missing:#?}"
    );
    let unknown: Vec<&&str> = covered
        .iter()
        .filter(|path| !constants.contains(**path))
        .collect();
    assert!(
        unknown.is_empty(),
        "route cases for unknown paths: {unknown:#?}"
    );
}

#[test]
fn route_case_names_are_unique() {
    let mut seen = BTreeSet::new();
    for case in CASES {
        assert!(seen.insert(case.name), "duplicate case {}", case.name);
    }
}

#[tokio::test]
async fn unknown_dispatch_names_are_rejected_without_network() {
    let client = BybitClient::public(5_000, false, Duration::from_secs(1)).expect("client");
    let error = client
        .public_request("get_not_a_bybit_endpoint", Vec::new())
        .await
        .expect_err("public");
    assert!(
        error
            .to_string()
            .contains("unsupported Bybit public method")
    );
    let error = client
        .private_request("get_not_a_bybit_endpoint", Vec::new())
        .await
        .expect_err("private");
    assert!(
        error
            .to_string()
            .contains("unsupported Bybit private method")
    );
}
