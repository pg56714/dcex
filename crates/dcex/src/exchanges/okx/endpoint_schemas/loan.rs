//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "set_auto_loan" => RiskEndpoint {
            path: "/api/v5/account/set-auto-loan",
            post: true,
            public: false,
            keys: &["autoLoan"],
            required: &[],
            bools: &["autoLoan"],
            schema: None,
        },
        "get_repayment_currencies" => RiskEndpoint {
            path: "/api/v5/trade/one-click-repay-currency-list-v2",
            post: false,
            public: false,
            keys: &[],
            required: &[],
            bools: &[],
            schema: None,
        },
        "repay_debt" => RiskEndpoint {
            path: "/api/v5/trade/one-click-repay-v2",
            post: true,
            public: false,
            keys: &["debtCcy", "repayCcyList"],
            required: &["debtCcy", "repayCcyList"],
            bools: &[],
            schema: None,
        },
        "get_repayment_history" => RiskEndpoint {
            path: "/api/v5/trade/one-click-repay-history-v2",
            post: false,
            public: false,
            keys: &["after", "before", "limit"],
            required: &[],
            bools: &[],
            schema: None,
        },
        "get_loan_ratio" => RiskEndpoint {
            path: "/api/v5/rubik/stat/margin/loan-ratio",
            post: false,
            public: true,
            keys: &["ccy", "begin", "end", "period"],
            required: &["ccy"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\"},\"begin\":{\"type\":\"string\"},\"end\":{\"type\":\"string\"},\"period\":{\"type\":\"string\"}},\"required\":[\"ccy\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-non-tradable-assets
        "get_public_interest_rate_loan_quota" => RiskEndpoint {
            path: "/api/v5/public/interest-rate-loan-quota",
            post: false,
            public: true,
            keys: &[],
            required: &[],
            bools: &[],
            schema: Some("{\"type\":\"object\",\"properties\":{},\"required\":[]}"),
        },
        // https://www.okx.com/docs-v5/en/#funding-account-rest-api-get-withdrawal-history
        _ => return None,
    })
}
