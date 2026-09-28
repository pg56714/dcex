//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "set_sub_account_transfer_out" => RiskEndpoint {
            path: "/api/v5/users/subaccount/set-transfer-out",
            post: true,
            public: false,
            keys: &["subAcct", "canTransOut"],
            required: &["subAcct"],
            bools: &["canTransOut"],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"subAcct\":{\"type\":\"string\"},\"canTransOut\":{\"type\":\"boolean\"}},\"required\":[\"subAcct\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#announcement-get-announcements
        _ => return None,
    })
}
