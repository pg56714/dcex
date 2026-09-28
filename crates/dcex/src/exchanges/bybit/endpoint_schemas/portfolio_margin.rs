//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "get_portfolio_margin_info" => RiskEndpoint {
            path: "/v5/asset/portfolio-margin",
            post: false,
            public: false,
            keys: &["baseCoin"],
            required: &[],
            integers: &[],
        },
        _ => return None,
    })
}
