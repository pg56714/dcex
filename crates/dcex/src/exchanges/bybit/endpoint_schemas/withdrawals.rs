//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "get_asset_withdraw_vasp_list" => RiskEndpoint {
            path: "/v5/asset/withdraw/vasp/list",
            post: false,
            public: false,
            keys: &[],
            required: &[],
            integers: &[],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/asset/withdraw/withdraw-address.mdx
        "get_asset_withdraw_query_address" => RiskEndpoint {
            path: "/v5/asset/withdraw/query-address",
            post: false,
            public: false,
            keys: &["coin", "chain", "addressType", "limit", "cursor"],
            required: &[],
            integers: &["addressType", "limit"],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/asset/withdraw/withdraw-record.mdx
        "get_asset_withdraw_query_record" => RiskEndpoint {
            path: "/v5/asset/withdraw/query-record",
            post: false,
            public: false,
            keys: &[
                "withdrawID",
                "txID",
                "coin",
                "withdrawType",
                "startTime",
                "endTime",
                "limit",
                "cursor",
            ],
            required: &[],
            integers: &["withdrawType", "startTime", "endTime", "limit"],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/crypto-loan/acct-borrow-collateral.mdx
        _ => return None,
    })
}
