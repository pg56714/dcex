//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    Some(match name {
        "convert_futures_union_asset" => Endpoint {
            path: "/api/v2/mix/account/union-convert",
            post: true,
            public: false,
            fields: &["coin", "amount"],
            required: &["coin", "amount"],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-contract-account/classic-contract-account#get-union-transfer-limits
        "get_uta_convert_records" => Endpoint {
            path: "/api/v3/account/convert-records",
            post: false,
            public: false,
            fields: &[
                "fromCoin",
                "toCoin",
                "startTime",
                "endTime",
                "limit",
                "cursor",
            ],
            required: &[],
            arrays: &[],
            limit: Some(100),
            days: Some(30),
        },
        // https://www.bitget.com/docs/catalog/account/account-settings#adjust-account-mode
        "get_uta_small_assets_history" => Endpoint {
            path: "/api/v3/convert/small-assets-history",
            post: false,
            public: false,
            fields: &["orderId", "startTime", "endTime", "limit", "cursor"],
            required: &[],
            arrays: &[],
            limit: Some(100),
            days: None,
        },
        // https://www.bitget.com/docs/catalog/account/small-assets#get-small-assets
        "get_uta_small_assets" => Endpoint {
            path: "/api/v3/convert/small-assets",
            post: false,
            public: false,
            fields: &[],
            required: &[],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/account/small-assets#small-assets-trade
        "uta_small_assets_trade" => Endpoint {
            path: "/api/v3/convert/small-assets-trade",
            post: true,
            public: false,
            fields: &["fromCoinList"],
            required: &["fromCoinList"],
            arrays: &["fromCoinList"],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/account/sub-accounts#delete-sub-account
        "get_classic_convert_currencies" => Endpoint {
            path: "/api/v2/convert/currencies",
            post: false,
            public: true,
            fields: &[],
            required: &[],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-spot-convert/classic-spot-convert#get-quoted-price
        "get_classic_quoted_price" => Endpoint {
            path: "/api/v2/convert/quoted-price",
            post: false,
            public: false,
            fields: &["fromCoin", "toCoin", "fromCoinSize", "toCoinSize"],
            required: &["fromCoin", "toCoin"],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-spot-convert/classic-spot-convert#convert
        "classic_trade" => Endpoint {
            path: "/api/v2/convert/trade",
            post: true,
            public: false,
            fields: &[
                "fromCoin",
                "fromCoinSize",
                "cnvtPrice",
                "toCoin",
                "toCoinSize",
                "traceId",
            ],
            required: &[
                "fromCoin",
                "fromCoinSize",
                "cnvtPrice",
                "toCoin",
                "toCoinSize",
                "traceId",
            ],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-spot-convert/classic-spot-convert#get-convert-history
        "get_classic_convert_record" => Endpoint {
            path: "/api/v2/convert/convert-record",
            post: false,
            public: false,
            fields: &["startTime", "endTime", "limit", "idLessThan"],
            required: &["startTime", "endTime"],
            arrays: &[],
            limit: Some(100),
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-spot-market/classic-spot-market#get-merge-depth
        _ => return None,
    })
}
