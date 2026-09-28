//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "get_announcements" => RiskEndpoint {
            path: "/api/v5/support/announcements",
            post: false,
            public: true,
            keys: &["annType", "page"],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"annType\":{\"type\":\"string\"},\"page\":{\"type\":\"string\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#announcement-get-announcement-types
        "get_announcement_types" => RiskEndpoint {
            path: "/api/v5/support/announcement-types",
            post: false,
            public: true,
            keys: &[],
            required: &[],
            bools: &[],
            schema: Some("{\"type\":\"object\",\"properties\":{},\"required\":[]}"),
        },
        // https://www.okx.com/docs-v5/en/#order-book-trading-grid-trading-post-place-grid-algo-order
        _ => return None,
    })
}
