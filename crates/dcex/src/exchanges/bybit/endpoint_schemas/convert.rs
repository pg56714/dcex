//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "request_convert_quote" => RiskEndpoint {
            path: "/v5/asset/exchange/quote-apply",
            post: true,
            public: false,
            keys: &[
                "accountType",
                "fromCoin",
                "toCoin",
                "requestCoin",
                "requestAmount",
                "fromCoinType",
                "toCoinType",
                "requestId",
            ],
            required: &[
                "accountType",
                "fromCoin",
                "toCoin",
                "requestCoin",
                "requestAmount",
            ],
            integers: &[],
        },
        "execute_convert_quote" => RiskEndpoint {
            path: "/v5/asset/exchange/convert-execute",
            post: true,
            public: false,
            keys: &["quoteTxId"],
            required: &["quoteTxId"],
            integers: &[],
        },
        "get_convert_result" => RiskEndpoint {
            path: "/v5/asset/exchange/convert-result-query",
            post: false,
            public: false,
            keys: &["quoteTxId", "accountType"],
            required: &["quoteTxId", "accountType"],
            integers: &[],
        },
        "get_convert_coins" => RiskEndpoint {
            path: "/v5/asset/exchange/query-coin-list",
            post: false,
            public: false,
            keys: &["accountType", "coin", "side"],
            required: &["accountType"],
            integers: &["side"],
        },
        "get_convert_history" => RiskEndpoint {
            path: "/v5/asset/exchange/query-convert-history",
            post: false,
            public: false,
            keys: &["accountType", "index", "limit"],
            required: &[],
            integers: &["index", "limit"],
        },
        _ => return None,
    })
}
