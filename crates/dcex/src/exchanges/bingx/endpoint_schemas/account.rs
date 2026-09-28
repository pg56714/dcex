//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    Some(match name {
        "get_api_permissions" => Endpoint {
            path: "/openApi/v1/account/apiPermissions",
            verb: "GET",
            public: false,
            fields: &["recvWindow"],
            required: &[],
            integers: &["recvWindow"],
        },
        "get_api_restrictions" => Endpoint {
            path: "/openApi/v1/account/apiRestrictions",
            verb: "GET",
            public: false,
            fields: &["recvWindow"],
            required: &[],
            integers: &["recvWindow"],
        },
        _ => return None,
    })
}
