//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "get_affiliate_performance_summary" => RiskEndpoint {
            path: "/api/v5/affiliate/performance/summary",
            post: false,
            public: false,
            keys: &["periodType", "begin", "end"],
            required: &[],
            bools: &[],
            schema: Some(
                r#"{"type":"object","properties":{"periodType":{"type":"string"},"begin":{"type":"string"},"end":{"type":"string"}},"required":[]}"#,
            ),
        },
        "get_affiliate_invitee_detail" => RiskEndpoint {
            path: "/api/v5/affiliate/invitee/detail",
            post: false,
            public: false,
            keys: &["uid", "periodType"],
            required: &["uid"],
            bools: &[],
            schema: Some(
                r#"{"type":"object","properties":{"uid":{"type":"string"},"periodType":{"type":"string"}},"required":["uid"]}"#,
            ),
        },
        "get_affiliate_invitee_list" => RiskEndpoint {
            path: "/api/v5/affiliate/invitee/list",
            post: false,
            public: false,
            keys: &[
                "page",
                "limit",
                "periodType",
                "begin",
                "end",
                "keyword",
                "commissionCategory",
                "orderBy",
                "orderDir",
                "kycStatus",
                "subAffiliateUid",
                "uid",
                "joinTimeBegin",
                "joinTimeEnd",
            ],
            required: &[],
            bools: &[],
            schema: Some(
                r#"{"type":"object","properties":{"page":{"type":"string"},"limit":{"type":"string"},"periodType":{"type":"string"},"begin":{"type":"string"},"end":{"type":"string"},"keyword":{"type":"string"},"commissionCategory":{"type":"string"},"orderBy":{"type":"string"},"orderDir":{"type":"string"},"kycStatus":{"type":"string"},"subAffiliateUid":{"type":"string"},"uid":{"type":"string"},"joinTimeBegin":{"type":"string"},"joinTimeEnd":{"type":"string"}},"required":[]}"#,
            ),
        },
        "get_affiliate_links" => RiskEndpoint {
            path: "/api/v5/affiliate/link/list",
            post: false,
            public: false,
            keys: &["page", "limit", "linkType", "linkStatus"],
            required: &[],
            bools: &[],
            schema: Some(
                r#"{"type":"object","properties":{"page":{"type":"string"},"limit":{"type":"string"},"linkType":{"type":"string"},"linkStatus":{"type":"string"}},"required":[]}"#,
            ),
        },
        "get_affiliate_co_inviters" => RiskEndpoint {
            path: "/api/v5/affiliate/co-inviter/list",
            post: false,
            public: false,
            keys: &["page", "limit", "linkStatus"],
            required: &[],
            bools: &[],
            schema: Some(
                r#"{"type":"object","properties":{"page":{"type":"string"},"limit":{"type":"string"},"linkStatus":{"type":"string"}},"required":[]}"#,
            ),
        },
        "get_sub_affiliates" => RiskEndpoint {
            path: "/api/v5/affiliate/sub-affiliate/list",
            post: false,
            public: false,
            keys: &[
                "page",
                "limit",
                "keyword",
                "commissionCategory",
                "orderBy",
                "orderDir",
            ],
            required: &[],
            bools: &[],
            schema: Some(
                r#"{"type":"object","properties":{"page":{"type":"string"},"limit":{"type":"string"},"keyword":{"type":"string"},"commissionCategory":{"type":"string"},"orderBy":{"type":"string"},"orderDir":{"type":"string"}},"required":[]}"#,
            ),
        },
        _ => return None,
    })
}
