//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    Some(match name {
        "get_fiat_price" => Endpoint {
            path: "/api/v1/prices",
            method: HttpMethod::Get,
            market: KucoinMarket::Spot,
            public: true,
            fields: &[
                Field {
                    key: "base",
                    kind: 's',
                    required: false,
                    path: false,
                    choices: &[],
                    minimum: None,
                    maximum: None,
                },
                Field {
                    key: "currencies",
                    kind: 's',
                    required: false,
                    path: false,
                    choices: &[],
                    minimum: None,
                    maximum: None,
                },
            ],
        },
        // https://www.kucoin.com/docs-new/rest/spot-trading/market-data/get-market-list
        "get_uta_fiat_price" => Endpoint {
            path: "/api/ua/v2/market/fiat-price",
            method: HttpMethod::Get,
            market: KucoinMarket::Spot,
            public: true,
            fields: &[
                Field {
                    key: "base",
                    kind: 's',
                    required: true,
                    path: false,
                    choices: &[],
                    minimum: None,
                    maximum: None,
                },
                Field {
                    key: "currencies",
                    kind: 'a',
                    required: false,
                    path: false,
                    choices: &[],
                    minimum: None,
                    maximum: None,
                },
            ],
        },
        // https://www.kucoin.com/docs-new/v2/rest/ua/get-announcements
        _ => return None,
    })
}
