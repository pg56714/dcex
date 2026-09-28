//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    Some(match name {
        "get_margin_hf_account_ledgers" => Endpoint {
            path: "/api/v3/hf/margin/account/ledgers",
            method: HttpMethod::Get,
            market: KucoinMarket::Spot,
            public: false,
            fields: &[
                Field {
                    key: "currency",
                    kind: 's',
                    required: false,
                    path: false,
                    choices: &[],
                    minimum: None,
                    maximum: None,
                },
                Field {
                    key: "direction",
                    kind: 's',
                    required: false,
                    path: false,
                    choices: &["in", "out"],
                    minimum: None,
                    maximum: None,
                },
                Field {
                    key: "bizType",
                    kind: 's',
                    required: false,
                    path: false,
                    choices: &[],
                    minimum: None,
                    maximum: None,
                },
                Field {
                    key: "lastId",
                    kind: 'i',
                    required: false,
                    path: false,
                    choices: &[],
                    minimum: None,
                    maximum: None,
                },
                Field {
                    key: "limit",
                    kind: 'i',
                    required: false,
                    path: false,
                    choices: &[],
                    minimum: Some(1),
                    maximum: Some(200),
                },
                Field {
                    key: "startAt",
                    kind: 'i',
                    required: false,
                    path: false,
                    choices: &[],
                    minimum: None,
                    maximum: None,
                },
                Field {
                    key: "endAt",
                    kind: 'i',
                    required: false,
                    path: false,
                    choices: &[],
                    minimum: None,
                    maximum: None,
                },
            ],
        },
        // https://www.kucoin.com/docs-new/rest/account-info/account-funding/get-account-ledgers-spot-margin
        "get_margin_mark_price" => Endpoint {
            path: "/api/v1/mark-price/{symbol}/current",
            method: HttpMethod::Get,
            market: KucoinMarket::Spot,
            public: true,
            fields: &[Field {
                key: "symbol",
                kind: 's',
                required: true,
                path: true,
                choices: &[],
                minimum: None,
                maximum: None,
            }],
        },
        // https://www.kucoin.com/docs-new/rest/margin-trading/market-data/get-mark-price-list
        "get_margin_mark_prices" => Endpoint {
            path: "/api/v3/mark-price/all-symbols",
            method: HttpMethod::Get,
            market: KucoinMarket::Spot,
            public: true,
            fields: &[],
        },
        // https://www.kucoin.com/docs-new/rest/margin-trading/risk-limit/get-margin-risk-limit
        "get_margin_currency_risk_limits" => Endpoint {
            path: "/api/v3/margin/currencies",
            method: HttpMethod::Get,
            market: KucoinMarket::Spot,
            public: false,
            fields: &[
                Field {
                    key: "isIsolated",
                    kind: 'b',
                    required: false,
                    path: false,
                    choices: &[],
                    minimum: None,
                    maximum: None,
                },
                Field {
                    key: "currency",
                    kind: 's',
                    required: false,
                    path: false,
                    choices: &[],
                    minimum: None,
                    maximum: None,
                },
                Field {
                    key: "symbol",
                    kind: 's',
                    required: false,
                    path: false,
                    choices: &[],
                    minimum: None,
                    maximum: None,
                },
            ],
        },
        // https://www.kucoin.com/docs-new/rest/spot-trading/market-data/get-full-orderbook
        "get_margin_config" => Endpoint {
            path: "/api/v1/margin/config",
            method: HttpMethod::Get,
            market: KucoinMarket::Spot,
            public: true,
            fields: &[],
        },
        // https://www.kucoin.com/docs-new/rest/spot-trading/market-data/get-announcements
        _ => return None,
    })
}
