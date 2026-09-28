//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<RiskEndpoint> {
    Some(match name {
        "create_sub_account" => RiskEndpoint {
            path: "/api/v5/users/subaccount/create-subaccount",
            post: true,
            public: false,
            keys: &["subAcct", "type", "label", "pwd"],
            required: &["subAcct", "type"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"subAcct\":{\"type\":\"string\"},\"type\":{\"type\":\"string\"},\"label\":{\"type\":\"string\"},\"pwd\":{\"type\":\"string\"}},\"required\":[\"subAcct\",\"type\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#sub-account-rest-api-create-an-api-key-for-a-sub-account
        "create_sub_account_api_key" => RiskEndpoint {
            path: "/api/v5/users/subaccount/apikey",
            post: true,
            public: false,
            keys: &["subAcct", "label", "passphrase", "perm", "ip"],
            required: &["subAcct", "label", "passphrase"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"subAcct\":{\"type\":\"string\"},\"label\":{\"type\":\"string\"},\"passphrase\":{\"type\":\"string\"},\"perm\":{\"type\":\"string\"},\"ip\":{\"type\":\"string\"}},\"required\":[\"subAcct\",\"label\",\"passphrase\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#sub-account-rest-api-query-the-api-key-of-a-sub-account
        "get_sub_account_api_keys" => RiskEndpoint {
            path: "/api/v5/users/subaccount/apikey",
            post: false,
            public: false,
            keys: &["subAcct", "apiKey"],
            required: &["subAcct"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"subAcct\":{\"type\":\"string\"},\"apiKey\":{\"type\":\"string\"}},\"required\":[\"subAcct\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#sub-account-rest-api-reset-the-api-key-of-a-sub-account
        "modify_sub_account_api_key" => RiskEndpoint {
            path: "/api/v5/users/subaccount/modify-apikey",
            post: true,
            public: false,
            keys: &["subAcct", "apiKey", "label", "perm", "ip"],
            required: &["subAcct", "apiKey"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"subAcct\":{\"type\":\"string\"},\"apiKey\":{\"type\":\"string\"},\"label\":{\"type\":\"string\"},\"perm\":{\"type\":\"string\"},\"ip\":{\"type\":\"string\"}},\"required\":[\"subAcct\",\"apiKey\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#sub-account-rest-api-delete-the-api-key-of-sub-accounts
        "delete_sub_account_api_key" => RiskEndpoint {
            path: "/api/v5/users/subaccount/delete-apikey",
            post: true,
            public: false,
            keys: &["subAcct", "apiKey"],
            required: &["subAcct", "apiKey"],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"subAcct\":{\"type\":\"string\"},\"apiKey\":{\"type\":\"string\"}},\"required\":[\"subAcct\",\"apiKey\"]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#sub-account-rest-api-set-permission-of-transfer-out
        "get_asset_subaccount_managed_subaccount_bills" => RiskEndpoint {
            path: "/api/v5/asset/subaccount/managed-subaccount-bills",
            post: false,
            public: false,
            keys: &[
                "ccy", "type", "subAcct", "subUid", "after", "before", "limit",
            ],
            required: &[],
            bools: &[],
            schema: Some(
                "{\"type\":\"object\",\"properties\":{\"ccy\":{\"type\":\"string\",\"description\":\"Currency, e.g BTC\"},\"type\":{\"type\":\"string\",\"description\":\"Transfer type 0 : Transfers from master account to sub-account 1 : Transfers from sub-account to master account\"},\"subAcct\":{\"type\":\"string\",\"description\":\"Sub-account name\"},\"subUid\":{\"type\":\"string\",\"description\":\"Sub-account UID\"},\"after\":{\"type\":\"string\",\"description\":\"Query the data prior to the requested bill ID creation time (exclude), Unix timestamp in millisecond format, e.g. 1597026383085\"},\"before\":{\"type\":\"string\",\"description\":\"Query the data after the requested bill ID creation time (exclude), Unix timestamp in millisecond format, e.g. 1597026383085\"},\"limit\":{\"type\":\"string\",\"description\":\"Number of results per request. The maximum is 100. The default is 100.\"}},\"required\":[]}",
            ),
        },
        // https://www.okx.com/docs-v5/en/#financial-product-stable-rewards-get-product-info
        _ => return None,
    })
}
