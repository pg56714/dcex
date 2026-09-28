//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    Some(match name {
        "get_uta_funding_assets" => Endpoint {
            path: "/api/v3/account/funding-assets",
            post: false,
            public: false,
            fields: &["coin"],
            required: &[],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/account/assets-balance#get-funding-financial-records
        _ => return None,
    })
}
