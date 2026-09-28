//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "get_spot_lever_token_reference" => RiskEndpoint {
            path: "/v5/spot-lever-token/reference",
            post: false,
            public: true,
            keys: &["ltCoin"],
            required: &["ltCoin"],
            integers: &[],
        },
        // https://github.com/bybit-exchange/docs/blob/master/docs/v5/lt/order-record.mdx
        "get_spot_lever_token_order_record" => RiskEndpoint {
            path: "/v5/spot-lever-token/order-record",
            post: false,
            public: false,
            keys: &[
                "ltCoin",
                "orderId",
                "startTime",
                "endTime",
                "limit",
                "ltOrderType",
                "serialNo",
            ],
            required: &[],
            integers: &["startTime", "endTime", "limit", "ltOrderType"],
        },
        // https://github.com/bybit-exchange/docs/blob/master/docs/v5/lt/purchase.mdx
        "spot_lever_token_purchase" => RiskEndpoint {
            path: "/v5/spot-lever-token/purchase",
            post: true,
            public: false,
            keys: &["ltCoin", "ltAmount", "serialNo"],
            required: &["ltCoin", "ltAmount"],
            integers: &[],
        },
        // https://github.com/bybit-exchange/docs/blob/master/docs/v5/lt/redeem.mdx
        "spot_lever_token_redeem" => RiskEndpoint {
            path: "/v5/spot-lever-token/redeem",
            post: true,
            public: false,
            keys: &["ltCoin", "quantity", "serialNo"],
            required: &["ltCoin", "quantity"],
            integers: &[],
        },
        _ => return None,
    })
}
