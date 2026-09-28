//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "get_announcements" => RiskEndpoint {
            path: "/v5/announcements/index",
            post: false,
            public: true,
            keys: &["locale", "type", "tag", "page", "limit"],
            required: &["locale"],
            integers: &["page", "limit"],
        },
        _ => return None,
    })
}
