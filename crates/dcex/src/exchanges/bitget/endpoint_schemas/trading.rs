//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    Some(match name {
        "set_futures_all_leverage" => Endpoint {
            path: "/api/v2/mix/account/set-all-leverage",
            post: true,
            public: false,
            fields: &["productType", "leverage"],
            required: &["productType", "leverage"],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-contract-account/classic-contract-account#set-isolated-position-auto-margin
        "get_futures_position_history" => Endpoint {
            path: "/api/v2/mix/position/history-position",
            post: false,
            public: false,
            fields: &[
                "symbol",
                "productType",
                "idLessThan",
                "startTime",
                "endTime",
                "limit",
            ],
            required: &[],
            arrays: &[],
            limit: Some(100),
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-contract-position/classic-contract-position#get-position-adl-rank
        "get_futures_adl_rank" => Endpoint {
            path: "/api/v2/mix/position/adlRank",
            post: false,
            public: false,
            fields: &["productType"],
            required: &["productType"],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-contract-trade/classic-contract-trade#reversal
        "reverse_futures_position" => Endpoint {
            path: "/api/v2/mix/order/click-backhand",
            post: true,
            public: false,
            fields: &[
                "symbol",
                "marginCoin",
                "productType",
                "side",
                "size",
                "tradeSide",
                "clientOid",
            ],
            required: &["symbol", "marginCoin", "productType", "side"],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-contract-trade/classic-contract-trade#get-historical-transaction-details
        "get_futures_fill_history" => Endpoint {
            path: "/api/v2/mix/order/fill-history",
            post: false,
            public: false,
            fields: &[
                "productType",
                "orderId",
                "symbol",
                "startTime",
                "endTime",
                "idLessThan",
                "limit",
            ],
            required: &["productType"],
            arrays: &[],
            limit: Some(100),
            days: Some(7),
        },
        // https://www.bitget.com/docs/catalog/classic-spot-account/classic-spot-account#get-mainsub-transfer-record
        "get_uta_adl_rank" => Endpoint {
            path: "/api/v3/position/adlRank",
            post: false,
            public: false,
            fields: &[],
            required: &[],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/legacy-docs/uta/account/transfer/
        "get_uta_strategy_sub_orders" => Endpoint {
            path: "/api/v3/trade/strategy-sub-orders",
            post: false,
            public: false,
            fields: &["orderId", "limit", "cursor"],
            required: &["orderId"],
            arrays: &[],
            limit: Some(100),
            days: None,
        },
        // https://www.bitget.com/legacy-docs/uta/account/deposit/Get-Deposit-Records
        "get_all_trade_rates" => Endpoint {
            path: "/api/v2/common/all-trade-rate",
            post: false,
            public: false,
            fields: &["businessType"],
            required: &["businessType"],
            arrays: &[],
            limit: Some(100),
            days: None,
        },
        // https://www.bitget.com/docs/catalog/account/account-settings#switch-deduct
        "move_uta_positions" => Endpoint {
            path: "/api/v3/account/move-positions",
            post: true,
            public: false,
            fields: &["fromUid", "toUid", "category", "positionList"],
            required: &["fromUid", "toUid", "category", "positionList"],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/account/assets-balance#get-max-withdrawal
        _ => return None,
    })
}
