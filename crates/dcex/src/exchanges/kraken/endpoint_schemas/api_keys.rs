//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) const ENDPOINTS: &[Endpoint] = &[
    Endpoint {
        name: "get_spot_api_key_info",
        path: "/0/private/GetApiKeyInfo",
        method: HttpMethod::Post,
        auth: KrakenAuth::Spot,
        public: false,
        allowed: &["otp"],
        fields: &[Field {
            key: "otp",
            kind: "string",
            required: false,
            values: &[],
            minimum: 0,
        }],
        symbol_key: None,
    },
    Endpoint {
        name: "check_futures_api_key",
        path: "/api/auth/v1/api-keys/v3/check",
        method: HttpMethod::Get,
        auth: KrakenAuth::Futures,
        public: false,
        allowed: &[],
        fields: &[],
        symbol_key: None,
    },
];
