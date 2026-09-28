//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    Some(match name {
        "get_withdrawal_history" => Endpoint {
            path: "/openApi/api/v3/capital/withdraw/history",
            verb: "GET",
            public: false,
            fields: &[
                "id",
                "coin",
                "withdrawOrderId",
                "status",
                "startTime",
                "endTime",
                "offset",
                "limit",
                "txId",
                "recvWindow",
            ],
            required: &[],
            integers: &[
                "status",
                "startTime",
                "endTime",
                "offset",
                "limit",
                "recvWindow",
            ],
        },
        _ => return None,
    })
}
