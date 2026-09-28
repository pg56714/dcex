//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "get_api_key_info" => RiskEndpoint {
            path: "/v5/user/query-api",
            post: false,
            public: false,
            keys: &[],
            required: &[],
            integers: &[],
        },
        "modify_api_key" => RiskEndpoint {
            path: "/v5/user/update-api",
            post: true,
            public: false,
            keys: &["readOnly", "permissions"],
            required: &[],
            integers: &["readOnly"],
        },
        "delete_api_key" => RiskEndpoint {
            path: "/v5/user/delete-api",
            post: true,
            public: false,
            keys: &[],
            required: &[],
            integers: &[],
        },
        _ => return None,
    })
}
