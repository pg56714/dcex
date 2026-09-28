//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    Some(match name {
        "get_standard_futures_positions" => Endpoint {
            path: "/openApi/contract/v1/allPosition",
            verb: "GET",
            public: false,
            fields: &["recvWindow"],
            required: &[],
            integers: &["recvWindow"],
        },
        "get_standard_futures_orders" => Endpoint {
            path: "/openApi/contract/v1/allOrders",
            verb: "GET",
            public: false,
            fields: &[
                "product_symbol",
                "orderId",
                "startTime",
                "endTime",
                "limit",
                "recvWindow",
            ],
            required: &["product_symbol"],
            integers: &["orderId", "startTime", "endTime", "limit", "recvWindow"],
        },
        "get_standard_futures_balance" => Endpoint {
            path: "/openApi/contract/v1/balance",
            verb: "GET",
            public: false,
            fields: &["recvWindow"],
            required: &[],
            integers: &["recvWindow"],
        },
        _ => return None,
    })
}
