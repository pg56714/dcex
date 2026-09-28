//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    Some(match name {
        "get_uta_borrowable_currencies" => Endpoint {
            path: "/api/ua/v2/market/borrowable-currency",
            method: HttpMethod::Get,
            market: KucoinMarket::Spot,
            public: true,
            fields: &[],
        },
        // https://www.kucoin.com/docs-new/v2/rest/ua/get-borrowing-rates-and-limits
        "get_uta_borrowing_rates_limits" => Endpoint {
            path: "/api/ua/v2/account/interest-limits",
            method: HttpMethod::Get,
            market: KucoinMarket::Spot,
            public: false,
            fields: &[Field {
                key: "currency",
                kind: 's',
                required: true,
                path: false,
                choices: &[],
                minimum: None,
                maximum: None,
            }],
        },
        // https://www.kucoin.com/docs-new/v2/rest/ua/get-collateral-ratio
        "get_loan_info" => Endpoint {
            path: "/api/v1/otc-loan/loan",
            method: HttpMethod::Get,
            market: KucoinMarket::Spot,
            public: false,
            fields: &[],
        },
        // https://www.kucoin.com/docs-new/rest/vip-lending/get-accounts
        "get_accounts" => Endpoint {
            path: "/api/v1/otc-loan/accounts",
            method: HttpMethod::Get,
            market: KucoinMarket::Spot,
            public: false,
            fields: &[],
        },
        // https://www.kucoin.com/docs-new/rest/vip-lending/get-collateral-ratio
        "get_discount_rate_configs" => Endpoint {
            path: "/api/v1/otc-loan/discount-rate-configs",
            method: HttpMethod::Get,
            market: KucoinMarket::Spot,
            public: false,
            fields: &[],
        },
        // https://www.kucoin.com/docs-new/v2/rest/ua/get-oes-custody-quota
        "get_uta_accounts" => Endpoint {
            path: "/api/ua/v2/otc-loan/account",
            method: HttpMethod::Get,
            market: KucoinMarket::Spot,
            public: false,
            fields: &[Field {
                key: "accountType",
                kind: 's',
                required: false,
                path: false,
                choices: &["UNIFIED"],
                minimum: None,
                maximum: None,
            }],
        },
        // https://www.kucoin.com/docs-new/v2/rest/ua/vip-lending/get-collateral-ratio
        "get_uta_discount_rate_configs" => Endpoint {
            path: "/api/ua/v2/otc-loan/discount-rate",
            method: HttpMethod::Get,
            market: KucoinMarket::Spot,
            public: false,
            fields: &[Field {
                key: "accountType",
                kind: 's',
                required: false,
                path: false,
                choices: &["UNIFIED"],
                minimum: None,
                maximum: None,
            }],
        },
        // https://www.kucoin.com/docs-new/v2/rest/ua/vip-lending/get-loan-info
        "get_uta_loan_info" => Endpoint {
            path: "/api/ua/v2/otc-loan/loan",
            method: HttpMethod::Get,
            market: KucoinMarket::Spot,
            public: false,
            fields: &[Field {
                key: "accountType",
                kind: 's',
                required: false,
                path: false,
                choices: &["UNIFIED"],
                minimum: None,
                maximum: None,
            }],
        },
        // https://www.kucoin.com/docs-new/v2/rest/ua/withdrawal-history
        _ => return None,
    })
}
