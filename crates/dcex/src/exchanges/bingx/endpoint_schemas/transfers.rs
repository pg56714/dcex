//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    Some(match name {
        "set_sub_account_transfer_authorization" => Endpoint {
            path: "/openApi/account/v1/innerTransfer/authorizeSubAccount",
            verb: "POST",
            public: false,
            fields: &["subUids", "transferable", "recvWindow"],
            required: &["subUids", "transferable"],
            integers: &["recvWindow"],
        },
        "get_internal_transfer_records" => Endpoint {
            path: "/openApi/wallets/v1/capital/innerTransfer/records",
            verb: "GET",
            public: false,
            fields: &[
                "coin",
                "id",
                "transferClientId",
                "startTime",
                "endTime",
                "offset",
                "limit",
                "recvWindow",
            ],
            required: &["coin"],
            integers: &["startTime", "endTime", "offset", "limit", "recvWindow"],
        },
        "get_sub_account_internal_transfer_records" => Endpoint {
            path: "/openApi/wallets/v1/capital/subAccount/innerTransfer/records",
            verb: "GET",
            public: false,
            fields: &[
                "coin",
                "transferClientId",
                "startTime",
                "endTime",
                "offset",
                "limit",
                "recvWindow",
            ],
            required: &["coin"],
            integers: &["startTime", "endTime", "offset", "limit", "recvWindow"],
        },
        _ => return None,
    })
}
