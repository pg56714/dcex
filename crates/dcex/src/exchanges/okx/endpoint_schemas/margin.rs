//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "get_position_margin_graph" => RiskEndpoint {
            path: "/api/v5/account/position-builder-graph",
            post: true,
            public: false,
            keys: &[
                "inclRealPosAndEq",
                "simPos",
                "simAsset",
                "type",
                "mmrConfig",
            ],
            required: &["type", "mmrConfig"],
            bools: &["inclRealPosAndEq"],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"inclRealPosAndEq\":{\"type\":\"boolean\"},\"simPos\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"instId\":{\"type\":\"string\"},\"pos\":{\"type\":\"string\"},\"avgPx\":{\"type\":\"string\"},\"lever\":{\"type\":\"string\"}},\"required\":[\"instId\",\"pos\",\"avgPx\"]}},\"simAsset\":{\"type\":\"array\",\"items\":{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\"},\"amt\":{\"type\":\"string\"}},\"required\":[\"ccy\",\"amt\"]}},\"type\":{\"type\":\"string\"},\"mmrConfig\":{\"type\":\"object\",\"properties\":{\"acctLv\":{\"type\":\"string\"},\"lever\":{\"type\":\"string\"}},\"required\":[]}},\"required\":[\"type\",\"mmrConfig\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#trading-account-rest-api-move-positions
        _ => return None,
    })
}
