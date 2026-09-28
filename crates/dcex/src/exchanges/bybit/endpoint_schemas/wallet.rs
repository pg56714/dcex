//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "get_member_wallet_types" => RiskEndpoint {
            path: "/v5/user/get-member-type",
            post: false,
            public: false,
            keys: &["memberIds"],
            required: &[],
            integers: &[],
        },
        _ => return None,
    })
}
