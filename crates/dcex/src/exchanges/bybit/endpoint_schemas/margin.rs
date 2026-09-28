//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "get_margin_currency_data" => RiskEndpoint {
            path: "/v5/spot-margin-trade/currency-data",
            post: false,
            public: false,
            keys: &["currency"],
            required: &[],
            integers: &[],
        },
        _ => return None,
    })
}
