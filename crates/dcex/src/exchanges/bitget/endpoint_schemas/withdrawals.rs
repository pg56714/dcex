//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    Some(match name {
        "get_uta_account_max_withdrawal" => Endpoint {
            path: "/api/v3/account/max-withdrawal",
            post: false,
            public: false,
            fields: &["coin"],
            required: &["coin"],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-common-account/classic-common-account#bot-account
        "get_classic_spot_wallet_withdrawal_records" => Endpoint {
            path: "/api/v2/spot/wallet/withdrawal-records",
            post: false,
            public: false,
            fields: &[
                "startTime",
                "endTime",
                "coin",
                "clientOid",
                "idLessThan",
                "orderId",
                "limit",
            ],
            required: &["startTime", "endTime"],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/account/deposit-withdrawal#get-withdrawal-records
        "get_uta_account_withdrawal_records" => Endpoint {
            path: "/api/v3/account/withdrawal-records",
            post: false,
            public: false,
            fields: &[
                "startTime",
                "endTime",
                "coin",
                "orderId",
                "clientOid",
                "limit",
                "cursor",
            ],
            required: &["startTime", "endTime"],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/account/deposit-withdrawal#get-withdraw-address-book
        "get_uta_account_withdraw_address" => Endpoint {
            path: "/api/v3/account/withdraw-address",
            post: false,
            public: false,
            fields: &["coin", "type", "limit", "cursor"],
            required: &[],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/earn-classic-elite/classic-earn-elite#get-elite-product
        _ => return None,
    })
}
