//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "get_pm_position_tiers" => RiskEndpoint {
            path: "/api/v5/account/position-tiers",
            post: false,
            public: false,
            keys: &["instType", "instFamily"],
            required: &["instType", "instFamily"],
            bools: &[],
            schema: None,
        },
        "amend_spread_order" => RiskEndpoint {
            path: "/api/v5/sprd/amend-order",
            post: true,
            public: false,
            keys: &["ordId", "clOrdId", "reqId", "newSz", "newPx"],
            required: &[],
            bools: &[],
            schema: None,
        },
        "get_spread_order_history_archive" => RiskEndpoint {
            path: "/api/v5/sprd/orders-history-archive",
            post: false,
            public: false,
            keys: &[
                "sprdId",
                "ordType",
                "state",
                "instType",
                "instFamily",
                "beginId",
                "endId",
                "begin",
                "end",
                "limit",
            ],
            required: &[],
            bools: &[],
            schema: None,
        },
        // https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-bill-types
        "simulate_positions" => RiskEndpoint {
            path: "/api/v5/account/position-builder",
            post: true,
            public: false,
            keys: &[
                "acctLv",
                "inclRealPosAndEq",
                "lever",
                "simPos",
                "simAsset",
                "greeksType",
                "idxVol",
            ],
            required: &[],
            bools: &["inclRealPosAndEq"],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"acctLv\":{\"type\":\"string\"},\"inclRealPosAndEq\":{\"type\":\"boolean\"},\"lever\":{\"type\":\"string\"},\"simPos\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\"},\"pos\":{\"type\":\"string\"},\"avgPx\":{\"type\":\"string\"},\"lever\":{\"type\":\"string\"}},\"required\":[\"instId\",\"pos\",\"avgPx\"]}},\"simAsset\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\"},\"amt\":{\"type\":\"string\"}},\"required\":[\"ccy\",\"amt\"]}},\"greeksType\":{\"type\":\"string\"},\"idxVol\":{\"type\":\"string\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#trading-account-rest-api-position-builder-trend-graph
        "move_positions" => RiskEndpoint {
            path: "/api/v5/account/move-positions",
            post: true,
            public: false,
            keys: &["fromAcct", "toAcct", "legs", "clientId"],
            required: &["fromAcct", "toAcct", "legs", "clientId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"fromAcct\":{\"type\":\"string\"},\"toAcct\":{\"type\":\"string\"},\"legs\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"from\":{\"type\":\"object\",\"properties\":{\"posId\":{\"type\":\"string\"},\"sz\":{\"type\":\"string\"},\"side\":{\"type\":\"string\"}},\"required\":[\"posId\",\"sz\",\"side\"]},\"to\":{\"type\":\"object\",\"properties\":{\"tdMode\":{\"type\":\"string\"},\"posSide\":{\"type\":\"string\"},\"ccy\":{\"type\":\"string\"}},\"required\":[]}},\"required\":[\"from\",\"to\"]}},\"clientId\":{\"type\":\"string\"}},\"required\":[\"fromAcct\",\"toAcct\",\"legs\",\"clientId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#trading-account-rest-api-get-move-positions-history
        "get_move_positions_history" => RiskEndpoint {
            path: "/api/v5/account/move-positions-history",
            post: false,
            public: false,
            keys: &[
                "blockTdId",
                "clientId",
                "beginTs",
                "endTs",
                "limit",
                "state",
            ],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"blockTdId\":{\"type\":\"string\"},\"clientId\":{\"type\":\"string\"},\"beginTs\":{\"type\":\"string\"},\"endTs\":{\"type\":\"string\"},\"limit\":{\"type\":\"string\"},\"state\":{\"type\":\"string\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#trading-account-rest-api-adjust-demo-account-balance
        "get_block_trades" => RiskEndpoint {
            path: "/api/v5/public/block-trades",
            post: false,
            public: true,
            keys: &["instId"],
            required: &["instId"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\"}},\"required\":[\"instId\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#public-data-rest-api-get-estimated-future-settlement-price
        "reset_mmp" => RiskEndpoint {
            path: "/api/v5/account/mmp-reset",
            post: true,
            public: false,
            keys: &["instType", "instFamily"],
            required: &["instFamily"],
            bools: &[],
            schema: Some(
                r#"{"type":"object","properties":{"instType":{"type":"string"},"instFamily":{"type":"string"}},"required":["instFamily"]}"#,
            ),
        },
        "set_mmp_config" => RiskEndpoint {
            path: "/api/v5/account/mmp-config",
            post: true,
            public: false,
            keys: &["instFamily", "timeInterval", "frozenInterval", "qtyLimit"],
            required: &["instFamily", "timeInterval", "frozenInterval", "qtyLimit"],
            bools: &[],
            schema: Some(
                r#"{"type":"object","properties":{"instFamily":{"type":"string"},"timeInterval":{"type":"string"},"frozenInterval":{"type":"string"},"qtyLimit":{"type":"string"}},"required":["instFamily","timeInterval","frozenInterval","qtyLimit"]}"#,
            ),
        },
        "get_mmp_config" => RiskEndpoint {
            path: "/api/v5/account/mmp-config",
            post: false,
            public: false,
            keys: &["instFamily"],
            required: &[],
            bools: &[],
            schema: Some(
                r#"{"type":"object","properties":{"instFamily":{"type":"string"}},"required":[]}"#,
            ),
        },
        _ => return None,
    })
}
