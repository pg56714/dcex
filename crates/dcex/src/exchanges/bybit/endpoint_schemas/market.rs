//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "get_server_time" => RiskEndpoint {
            path: "/v5/market/time",
            post: false,
            public: true,
            keys: &[],
            required: &[],
            integers: &[],
        },
        "get_account_instruments" => RiskEndpoint {
            path: "/v5/account/instruments-info",
            post: false,
            public: false,
            keys: &["category", "symbol", "limit", "cursor", "product_symbol"],
            required: &["category"],
            integers: &["limit"],
        },
        "get_full_orderbook" => RiskEndpoint {
            path: "/v5/market/full_orderbook",
            post: false,
            public: true,
            keys: &["category", "symbol", "product_symbol"],
            required: &["category", "symbol"],
            integers: &[],
        },
        "get_rpi_orderbook" => RiskEndpoint {
            path: "/v5/market/rpi_orderbook",
            post: false,
            public: true,
            keys: &["category", "symbol", "limit", "product_symbol"],
            required: &["symbol", "limit"],
            integers: &["limit"],
        },
        "get_position_symbol_info" => RiskEndpoint {
            path: "/v5/position/symbol-info",
            post: false,
            public: false,
            keys: &["category", "symbol", "product_symbol"],
            required: &["category"],
            integers: &[],
        },
        "get_system_status" => RiskEndpoint {
            path: "/v5/system/status",
            post: false,
            public: true,
            keys: &["id", "state"],
            required: &[],
            integers: &[],
        },
        "get_fee_group_info" => RiskEndpoint {
            path: "/v5/market/fee-group-info",
            post: false,
            public: true,
            keys: &["productType", "groupId"],
            required: &["productType"],
            integers: &[],
        },
        "get_index_price_components" => RiskEndpoint {
            path: "/v5/market/index-price-components",
            post: false,
            public: true,
            keys: &["indexName"],
            required: &["indexName"],
            integers: &[],
        },
        _ => return None,
    })
}
