//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    Some(match name {
        "get_uta_deposit_records" => Endpoint {
            path: "/api/v3/account/deposit-records",
            post: false,
            public: false,
            fields: &["coin", "orderId", "startTime", "endTime", "limit", "cursor"],
            required: &["startTime", "endTime"],
            arrays: &[],
            limit: Some(100),
            days: None,
        },
        // https://www.bitget.com/legacy-docs/classic/common/public/Get-Server-Time
        "set_spot_deposit_account" => Endpoint {
            path: "/api/v2/spot/wallet/modify-deposit-account",
            post: true,
            public: false,
            fields: &["accountType", "coin"],
            required: &["accountType", "coin"],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-spot-account/classic-spot-account#get-deposit-address
        "get_deposit_address" => Endpoint {
            path: "/api/v2/spot/wallet/deposit-address",
            post: false,
            public: false,
            fields: &["coin", "chain", "size"],
            required: &["coin"],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-spot-account/classic-spot-account#get-subaccount-deposit-address
        "set_uta_deposit_account" => Endpoint {
            path: "/api/v3/account/deposit-account",
            post: true,
            public: false,
            fields: &["coin", "accountType"],
            required: &["coin", "accountType"],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/legacy-docs/uta/account/sub-account/SubAccount-Create
        "get_uta_deposit_address" => Endpoint {
            path: "/api/v3/account/deposit-address",
            post: false,
            public: false,
            fields: &["coin", "chain", "size"],
            required: &["coin"],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/account/deposit-withdrawal#get-sub-deposit-address
        "get_uta_sub_deposit_address" => Endpoint {
            path: "/api/v3/account/sub-deposit-address",
            post: false,
            public: false,
            fields: &["subUid", "coin", "chain", "size"],
            required: &["subUid", "coin"],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/account/deposit-withdrawal#get-sub-deposit-records
        "get_uta_sub_deposit_records" => Endpoint {
            path: "/api/v3/account/sub-deposit-records",
            post: false,
            public: false,
            fields: &["subUid", "startTime", "endTime", "coin", "limit", "cursor"],
            required: &["subUid", "startTime", "endTime"],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/account/rate-limit-quota#get-ratelimit-quota
        _ => return None,
    })
}
