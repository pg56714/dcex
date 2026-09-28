//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    Some(match name {
        "get_coin_network_config" => Endpoint {
            path: "/openApi/wallets/v1/capital/config/getall",
            verb: "GET",
            public: false,
            fields: &["coin", "displayName", "recvWindow"],
            required: &[],
            integers: &["recvWindow"],
        },
        _ => return None,
    })
}
