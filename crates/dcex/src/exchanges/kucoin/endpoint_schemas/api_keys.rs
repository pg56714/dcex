//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    Some(match name {
        "get_apikey_info" => Endpoint {
            path: "/api/v1/user/api-key",
            method: HttpMethod::Get,
            market: KucoinMarket::Spot,
            public: false,
            fields: &[],
        },
        // https://www.kucoin.com/docs-new/rest/account-info/deposit/add-deposit-address-v3
        "get_uta_apikey_info" => Endpoint {
            path: "/api/ua/v2/user/api-key",
            method: HttpMethod::Get,
            market: KucoinMarket::Spot,
            public: false,
            fields: &[],
        },
        // https://www.kucoin.com/docs-new/v2/rest/ua/currencies
        _ => return None,
    })
}
