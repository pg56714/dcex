//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "get_glp_today_performance" => RiskEndpoint {
            path: "/api/v5/users/glp/todayperformance",
            post: false,
            public: false,
            keys: &[],
            required: &[],
            bools: &[],
            schema: Some(r#"{"type":"object","properties":{},"required":[]}"#),
        },
        "get_glp_historical_performance" => RiskEndpoint {
            path: "/api/v5/users/glp/historicalperformance",
            post: false,
            public: false,
            keys: &["program", "begin", "end", "limit"],
            required: &["program"],
            bools: &[],
            schema: Some(
                r#"{"type":"object","properties":{"program":{"type":"string"},"begin":{"type":"string"},"end":{"type":"string"},"limit":{"type":"string"}},"required":["program"]}"#,
            ),
        },
        _ => return None,
    })
}
