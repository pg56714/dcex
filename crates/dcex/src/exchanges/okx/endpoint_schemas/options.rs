//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "activate_options" => RiskEndpoint {
            path: "/api/v5/account/activate-option",
            post: true,
            public: false,
            keys: &[],
            required: &[],
            bools: &[],
            schema: None,
        },
        "mass_cancel_options_orders" => RiskEndpoint {
            path: "/api/v5/trade/mass-cancel",
            post: true,
            public: false,
            keys: &["instType", "instFamily", "lockInterval"],
            required: &["instType", "instFamily"],
            bools: &[],
            schema: Some(
                r#"{"type":"object","properties":{"instType":{"type":"string"},"instFamily":{"type":"string"},"lockInterval":{"type":"string"}},"required":["instType","instFamily"]}"#,
            ),
        },
        _ => return None,
    })
}
