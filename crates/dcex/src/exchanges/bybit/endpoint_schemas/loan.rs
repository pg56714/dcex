//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "get_fixed_loan_supply_contract_info" => RiskEndpoint {
            path: "/v5/crypto-loan-fixed/supply-contract-info",
            post: false,
            public: false,
            keys: &[
                "orderId",
                "supplyId",
                "supplyCurrency",
                "term",
                "limit",
                "cursor",
            ],
            required: &[],
            integers: &["limit"],
        },
        "repay_liability" => RiskEndpoint {
            path: "/v5/account/quick-repayment",
            post: true,
            public: false,
            keys: &["coin"],
            required: &[],
            integers: &[],
        },
        "get_repayment_info" => RiskEndpoint {
            path: "/v5/account/pay-info",
            post: false,
            public: false,
            keys: &["coin"],
            required: &[],
            integers: &[],
        },
        "get_crypto_loan_borrowable_collateralisable_number" => RiskEndpoint {
            path: "/v5/crypto-loan/borrowable-collateralisable-number",
            post: false,
            public: false,
            keys: &["loanCurrency", "collateralCurrency"],
            required: &["loanCurrency", "collateralCurrency"],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/crypto-loan/adjust-collateral.mdx
        "crypto_loan_adjust_ltv" => RiskEndpoint {
            path: "/v5/crypto-loan/adjust-ltv",
            post: true,
            public: false,
            keys: &["orderId", "amount", "direction"],
            required: &["orderId", "amount", "direction"],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/crypto-loan/collateral-coin.mdx
        "get_crypto_loan_collateral_data" => RiskEndpoint {
            path: "/v5/crypto-loan/collateral-data",
            post: false,
            public: true,
            keys: &["vipLevel", "currency"],
            required: &[],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/crypto-loan/completed-loan-order.mdx
        "get_crypto_loan_borrow_history" => RiskEndpoint {
            path: "/v5/crypto-loan/borrow-history",
            post: false,
            public: false,
            keys: &[
                "orderId",
                "loanCurrency",
                "collateralCurrency",
                "limit",
                "cursor",
            ],
            required: &[],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/crypto-loan/loan-coin.mdx
        "get_crypto_loan_loanable_data" => RiskEndpoint {
            path: "/v5/crypto-loan/loanable-data",
            post: false,
            public: true,
            keys: &["vipLevel", "currency"],
            required: &[],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/crypto-loan/ltv-adjust-history.mdx
        "get_crypto_loan_adjustment_history" => RiskEndpoint {
            path: "/v5/crypto-loan/adjustment-history",
            post: false,
            public: false,
            keys: &[
                "orderId",
                "adjustId",
                "collateralCurrency",
                "limit",
                "cursor",
            ],
            required: &[],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/crypto-loan/reduce-max-collateral-amt.mdx
        "get_crypto_loan_max_collateral_amount" => RiskEndpoint {
            path: "/v5/crypto-loan/max-collateral-amount",
            post: false,
            public: false,
            keys: &["orderId"],
            required: &["orderId"],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/crypto-loan/repay-transaction.mdx
        "get_crypto_loan_repayment_history" => RiskEndpoint {
            path: "/v5/crypto-loan/repayment-history",
            post: false,
            public: false,
            keys: &["orderId", "repayId", "loanCurrency", "limit", "cursor"],
            required: &[],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/crypto-loan/repay.mdx
        "crypto_loan_repay" => RiskEndpoint {
            path: "/v5/crypto-loan/repay",
            post: true,
            public: false,
            keys: &["orderId", "amount"],
            required: &["orderId", "amount"],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/crypto-loan/unpaid-loan-order.mdx
        "get_crypto_loan_ongoing_orders" => RiskEndpoint {
            path: "/v5/crypto-loan/ongoing-orders",
            post: false,
            public: false,
            keys: &[
                "orderId",
                "loanCurrency",
                "collateralCurrency",
                "loanTermType",
                "loanTerm",
                "limit",
                "cursor",
            ],
            required: &[],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/finance/spot-x/puzzle/puzzle-project-list.mdx
        "crypto_loan_common_adjust_ltv" => RiskEndpoint {
            path: "/v5/crypto-loan-common/adjust-ltv",
            post: true,
            public: false,
            keys: &["currency", "amount", "direction"],
            required: &["currency", "amount", "direction"],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/collateral-coin.mdx
        "get_crypto_loan_common_collateral_data" => RiskEndpoint {
            path: "/v5/crypto-loan-common/collateral-data",
            post: false,
            public: true,
            keys: &["currency"],
            required: &[],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/crypto-loan-position.mdx
        "get_crypto_loan_common_position" => RiskEndpoint {
            path: "/v5/crypto-loan-common/position",
            post: false,
            public: false,
            keys: &[],
            required: &[],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/available-inventory.mdx
        "get_crypto_loan_fixed_available_inventory" => RiskEndpoint {
            path: "/v5/crypto-loan-fixed/available-inventory",
            post: false,
            public: false,
            keys: &["currency", "term", "annualRate"],
            required: &["currency", "term", "annualRate"],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/borrow-contract.mdx
        "get_crypto_loan_fixed_borrow_contract_info" => RiskEndpoint {
            path: "/v5/crypto-loan-fixed/borrow-contract-info",
            post: false,
            public: false,
            keys: &[
                "orderId",
                "loanId",
                "orderCurrency",
                "term",
                "limit",
                "cursor",
            ],
            required: &[],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/borrow-market.mdx
        "get_crypto_loan_fixed_borrow_order_quote" => RiskEndpoint {
            path: "/v5/crypto-loan-fixed/borrow-order-quote",
            post: false,
            public: true,
            keys: &["orderCurrency", "orderBy", "term", "sort", "limit"],
            required: &["orderCurrency", "orderBy"],
            integers: &["sort", "limit"],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/borrow-order.mdx
        "get_crypto_loan_fixed_borrow_order_info" => RiskEndpoint {
            path: "/v5/crypto-loan-fixed/borrow-order-info",
            post: false,
            public: false,
            keys: &[
                "orderId",
                "orderCurrency",
                "state",
                "term",
                "limit",
                "cursor",
            ],
            required: &[],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/borrow.mdx
        "crypto_loan_fixed_borrow" => RiskEndpoint {
            path: "/v5/crypto-loan-fixed/borrow",
            post: true,
            public: false,
            keys: &[
                "orderCurrency",
                "orderAmount",
                "annualRate",
                "term",
                "repayType",
                "strategyType",
                "collateralList",
            ],
            required: &["orderCurrency", "orderAmount", "annualRate", "term"],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/cancel-borrow.mdx
        "crypto_loan_fixed_borrow_order_cancel" => RiskEndpoint {
            path: "/v5/crypto-loan-fixed/borrow-order-cancel",
            post: true,
            public: false,
            keys: &["orderId"],
            required: &["orderId"],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/cancel-supply.mdx
        "crypto_loan_fixed_supply_order_cancel" => RiskEndpoint {
            path: "/v5/crypto-loan-fixed/supply-order-cancel",
            post: true,
            public: false,
            keys: &["orderId", "refundedAccount"],
            required: &["orderId"],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/renew-order.mdx
        "get_crypto_loan_fixed_renew_info" => RiskEndpoint {
            path: "/v5/crypto-loan-fixed/renew-info",
            post: false,
            public: false,
            keys: &["orderId", "orderCurrency", "limit", "cursor"],
            required: &[],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/renew.mdx
        "crypto_loan_fixed_renew" => RiskEndpoint {
            path: "/v5/crypto-loan-fixed/renew",
            post: true,
            public: false,
            keys: &["loanId", "collateralList"],
            required: &["loanId"],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/repay-collateral.mdx
        "crypto_loan_fixed_repay_collateral" => RiskEndpoint {
            path: "/v5/crypto-loan-fixed/repay-collateral",
            post: true,
            public: false,
            keys: &["loanId", "loanCurrency", "collateralCoin", "amount"],
            required: &["loanCurrency", "collateralCoin", "amount"],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/repay-history.mdx
        "get_crypto_loan_fixed_repayment_history" => RiskEndpoint {
            path: "/v5/crypto-loan-fixed/repayment-history",
            post: false,
            public: false,
            keys: &["repayId", "loanCurrency", "limit", "cursor"],
            required: &[],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/repay.mdx
        "crypto_loan_fixed_fully_repay" => RiskEndpoint {
            path: "/v5/crypto-loan-fixed/fully-repay",
            post: true,
            public: false,
            keys: &["loanId", "loanCurrency"],
            required: &[],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/supply-market.mdx
        "get_crypto_loan_fixed_supply_order_quote" => RiskEndpoint {
            path: "/v5/crypto-loan-fixed/supply-order-quote",
            post: false,
            public: true,
            keys: &["orderCurrency", "term", "orderBy", "sort", "limit"],
            required: &["orderCurrency", "orderBy"],
            integers: &["sort", "limit"],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/supply-order.mdx
        "get_crypto_loan_fixed_supply_order_info" => RiskEndpoint {
            path: "/v5/crypto-loan-fixed/supply-order-info",
            post: false,
            public: false,
            keys: &[
                "orderId",
                "orderCurrency",
                "state",
                "term",
                "limit",
                "cursor",
            ],
            required: &[],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/fixed/supply.mdx
        "crypto_loan_fixed_supply" => RiskEndpoint {
            path: "/v5/crypto-loan-fixed/supply",
            post: true,
            public: false,
            keys: &[
                "orderCurrency",
                "orderAmount",
                "annualRate",
                "term",
                "availableSource",
            ],
            required: &["orderCurrency", "orderAmount", "annualRate", "term"],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/flexible/available-inventory.mdx
        "get_crypto_loan_flexible_available_inventory" => RiskEndpoint {
            path: "/v5/crypto-loan-flexible/available-inventory",
            post: false,
            public: false,
            keys: &["currency"],
            required: &["currency"],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/flexible/borrow.mdx
        "crypto_loan_flexible_borrow" => RiskEndpoint {
            path: "/v5/crypto-loan-flexible/borrow",
            post: true,
            public: false,
            keys: &["loanCurrency", "loanAmount", "collateralList"],
            required: &["loanCurrency", "loanAmount"],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/flexible/loan-orders.mdx
        "get_crypto_loan_flexible_borrow_history" => RiskEndpoint {
            path: "/v5/crypto-loan-flexible/borrow-history",
            post: false,
            public: false,
            keys: &["orderId", "loanCurrency", "limit", "cursor"],
            required: &[],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/flexible/repay-collateral.mdx
        "crypto_loan_flexible_repay_collateral" => RiskEndpoint {
            path: "/v5/crypto-loan-flexible/repay-collateral",
            post: true,
            public: false,
            keys: &["loanCurrency", "collateralCoin", "amount"],
            required: &["loanCurrency", "collateralCoin", "amount"],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/flexible/repay-orders.mdx
        "get_crypto_loan_flexible_repayment_history" => RiskEndpoint {
            path: "/v5/crypto-loan-flexible/repayment-history",
            post: false,
            public: false,
            keys: &["repayId", "loanCurrency", "limit", "cursor"],
            required: &[],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/flexible/repay.mdx
        "crypto_loan_flexible_repay" => RiskEndpoint {
            path: "/v5/crypto-loan-flexible/repay",
            post: true,
            public: false,
            keys: &["loanCurrency", "amount"],
            required: &["loanCurrency", "amount"],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/flexible/unpaid-loan-order.mdx
        "get_crypto_loan_flexible_ongoing_coin" => RiskEndpoint {
            path: "/v5/crypto-loan-flexible/ongoing-coin",
            post: false,
            public: false,
            keys: &["loanCurrency"],
            required: &[],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/loan-coin.mdx
        "get_crypto_loan_common_loanable_data" => RiskEndpoint {
            path: "/v5/crypto-loan-common/loanable-data",
            post: false,
            public: true,
            keys: &["vipLevel", "currency"],
            required: &[],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/ltv-adjust-history.mdx
        "get_crypto_loan_common_adjustment_history" => RiskEndpoint {
            path: "/v5/crypto-loan-common/adjustment-history",
            post: false,
            public: false,
            keys: &["adjustId", "collateralCurrency", "limit", "cursor"],
            required: &[],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/max-loan-amt.mdx
        "crypto_loan_common_max_loan" => RiskEndpoint {
            path: "/v5/crypto-loan-common/max-loan",
            post: true,
            public: false,
            keys: &["currency", "collateralList"],
            required: &["currency"],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/new-crypto-loan/reduce-max-collateral-amt.mdx
        "get_crypto_loan_common_max_collateral_amount" => RiskEndpoint {
            path: "/v5/crypto-loan-common/max-collateral-amount",
            post: false,
            public: false,
            keys: &["currency"],
            required: &["currency"],
            integers: &[],
        },
        // https://github.com/bybit-exchange/docs/blob/master/docs/v5/lt/leverage-token-reference.mdx
        _ => return None,
    })
}
