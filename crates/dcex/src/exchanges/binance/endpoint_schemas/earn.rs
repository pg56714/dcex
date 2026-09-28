//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) const ENDPOINTS: &[Endpoint] = &[
    Endpoint {
        name: "get_bfusd_redemption_history",
        market: BinanceMarket::Spot,
        symbol_market: BinanceMarket::Spot,
        method: HttpMethod::Get,
        path: "/sapi/v1/bfusd/history/redemptionHistory",
        public: false,
        api_key: false,
        allowed: &["startTime", "endTime", "current", "size", "recvWindow"],
        fields: &[
            Field {
                key: "startTime",
                kind: 'i',
                required: false,
                choices: &[],
            },
            Field {
                key: "endTime",
                kind: 'i',
                required: false,
                choices: &[],
            },
            Field {
                key: "current",
                kind: 'i',
                required: false,
                choices: &[],
            },
            Field {
                key: "size",
                kind: 'i',
                required: false,
                choices: &[],
            },
            Field {
                key: "recvWindow",
                kind: 'i',
                required: false,
                choices: &[],
            },
        ],
    },
    Endpoint {
        name: "get_rwusd_redemption_history",
        market: BinanceMarket::Spot,
        symbol_market: BinanceMarket::Spot,
        method: HttpMethod::Get,
        path: "/sapi/v1/rwusd/history/redemptionHistory",
        public: false,
        api_key: false,
        allowed: &["startTime", "endTime", "current", "size", "recvWindow"],
        fields: &[
            Field {
                key: "startTime",
                kind: 'i',
                required: false,
                choices: &[],
            },
            Field {
                key: "endTime",
                kind: 'i',
                required: false,
                choices: &[],
            },
            Field {
                key: "current",
                kind: 'i',
                required: false,
                choices: &[],
            },
            Field {
                key: "size",
                kind: 'i',
                required: false,
                choices: &[],
            },
            Field {
                key: "recvWindow",
                kind: 'i',
                required: false,
                choices: &[],
            },
        ],
    },
    Endpoint {
        name: "get_yield_arena_activities",
        market: BinanceMarket::Spot,
        symbol_market: BinanceMarket::Spot,
        method: HttpMethod::Get,
        path: "/sapi/v1/earn/arena/activities",
        public: false,
        api_key: false,
        allowed: &["lang", "recvWindow"],
        fields: &[
            Field {
                key: "lang",
                kind: 's',
                required: false,
                choices: &[],
            },
            Field {
                key: "recvWindow",
                kind: 'i',
                required: false,
                choices: &[],
            },
        ],
    },
];
