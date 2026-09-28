//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    Some(match name {
        "place_spot_oco" => Endpoint {
            path: "/openApi/spot/v1/oco/order",
            verb: "POST",
            public: false,
            fields: &[
                "product_symbol",
                "side",
                "quantity",
                "limitPrice",
                "triggerPrice",
                "orderPrice",
                "listClientOrderId",
                "aboveClientOrderId",
                "belowClientOrderId",
                "recvWindow",
            ],
            required: &[
                "product_symbol",
                "side",
                "quantity",
                "limitPrice",
                "triggerPrice",
                "orderPrice",
            ],
            integers: &["recvWindow"],
        },
        "cancel_spot_oco" => Endpoint {
            path: "/openApi/spot/v1/oco/cancel",
            verb: "POST",
            public: false,
            fields: &["orderId", "clientOrderId", "recvWindow"],
            required: &[],
            integers: &["recvWindow"],
        },
        "get_spot_oco" => Endpoint {
            path: "/openApi/spot/v1/oco/orderList",
            verb: "GET",
            public: false,
            fields: &["orderListId", "clientOrderId", "recvWindow"],
            required: &[],
            integers: &["recvWindow"],
        },
        "get_spot_open_oco" => Endpoint {
            path: "/openApi/spot/v1/oco/openOrderList",
            verb: "GET",
            public: false,
            fields: &["pageIndex", "pageSize", "recvWindow"],
            required: &["pageIndex", "pageSize"],
            integers: &["pageIndex", "pageSize", "recvWindow"],
        },
        "get_spot_oco_history" => Endpoint {
            path: "/openApi/spot/v1/oco/historyOrderList",
            verb: "GET",
            public: false,
            fields: &[
                "pageIndex",
                "pageSize",
                "startTime",
                "endTime",
                "recvWindow",
            ],
            required: &["pageIndex", "pageSize"],
            integers: &[
                "pageIndex",
                "pageSize",
                "startTime",
                "endTime",
                "recvWindow",
            ],
        },
        _ => return None,
    })
}
