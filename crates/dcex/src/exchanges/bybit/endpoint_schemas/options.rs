//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "get_option_asset_info" => RiskEndpoint {
            path: "/v5/account/option-asset-info",
            post: false,
            public: false,
            keys: &[],
            required: &[],
            integers: &[],
        },
        "get_closed_option_positions" => RiskEndpoint {
            path: "/v5/position/get-closed-positions",
            post: false,
            public: false,
            keys: &[
                "category",
                "symbol",
                "startTime",
                "endTime",
                "limit",
                "cursor",
            ],
            required: &["category"],
            integers: &["startTime", "endTime", "limit"],
        },
        "get_option_delivery_prices" => RiskEndpoint {
            path: "/v5/market/new-delivery-price",
            post: false,
            public: true,
            keys: &["category", "baseCoin", "settleCoin"],
            required: &["category", "baseCoin"],
            integers: &[],
        },
        "get_option_base_coins" => RiskEndpoint {
            path: "/v5/market/option-base-coins",
            post: false,
            public: true,
            keys: &["underlyingType"],
            required: &[],
            integers: &[],
        },
        _ => return None,
    })
}
