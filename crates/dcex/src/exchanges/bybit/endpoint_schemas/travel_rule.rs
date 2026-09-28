//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "submit_deposit_information" => RiskEndpoint {
            path: "/v5/asset/travel-rule/deposit/submit",
            post: true,
            public: false,
            keys: &["depositId", "subAccountId", "questionnaire"],
            required: &["depositId", "questionnaire"],
            integers: &["depositId", "subAccountId"],
        },
        // https://raw.githubusercontent.com/bybit-exchange/docs/master/docs/v5/asset/withdraw/vasp-list.mdx
        _ => return None,
    })
}
