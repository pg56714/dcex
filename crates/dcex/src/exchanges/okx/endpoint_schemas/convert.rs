//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "convert_contract_coin" => RiskEndpoint {
            path: "/api/v5/public/convert-contract-coin",
            post: false,
            public: true,
            keys: &[
                "type",
                "instId",
                "sz",
                "px",
                "unit",
                "opType",
                "product_symbol",
            ],
            required: &["instId", "sz"],
            bools: &[],
            schema: None,
        },
        "get_convert_currency_pair" => RiskEndpoint {
            path: "/api/v5/asset/convert/currency-pair",
            post: false,
            public: false,
            keys: &["fromCcy", "toCcy", "convertMode"],
            required: &["fromCcy", "toCcy"],
            bools: &[],
            schema: None,
        },
        "estimate_convert_quote" => RiskEndpoint {
            path: "/api/v5/asset/convert/estimate-quote",
            post: true,
            public: false,
            keys: &[
                "baseCcy",
                "quoteCcy",
                "side",
                "rfqSz",
                "rfqSzCcy",
                "clQReqId",
                "convertMode",
            ],
            required: &["baseCcy", "quoteCcy", "side", "rfqSz", "rfqSzCcy"],
            bools: &[],
            schema: None,
        },
        "execute_convert_trade" => RiskEndpoint {
            path: "/api/v5/asset/convert/trade",
            post: true,
            public: false,
            keys: &[
                "quoteId",
                "baseCcy",
                "quoteCcy",
                "side",
                "sz",
                "szCcy",
                "clTReqId",
                "convertMode",
            ],
            required: &["quoteId", "baseCcy", "quoteCcy", "side", "sz", "szCcy"],
            bools: &[],
            schema: None,
        },
        _ => return None,
    })
}
