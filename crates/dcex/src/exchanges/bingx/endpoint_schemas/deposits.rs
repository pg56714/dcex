//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    Some(match name {
        "get_deposit_history" => Endpoint {
            path: "/openApi/api/v3/capital/deposit/hisrec",
            verb: "GET",
            public: false,
            fields: &[
                "coin",
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
        "get_deposit_addresses" => Endpoint {
            path: "/openApi/wallets/v1/capital/deposit/address",
            verb: "GET",
            public: false,
            fields: &["coin", "offset", "limit", "recvWindow"],
            required: &["coin"],
            integers: &["offset", "limit", "recvWindow"],
        },
        "get_deposit_risk_records" => Endpoint {
            path: "/openApi/wallets/v1/capital/deposit/riskRecords",
            verb: "GET",
            public: false,
            fields: &["recvWindow"],
            required: &[],
            integers: &["recvWindow"],
        },
        _ => return None,
    })
}
