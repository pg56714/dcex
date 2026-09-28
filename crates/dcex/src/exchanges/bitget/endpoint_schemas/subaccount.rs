//! Business-specific endpoint and field metadata.
use super::super::*;
pub(super) fn endpoint(name: &str) -> Option<Endpoint> {
    Some(match name {
        "get_futures_sub_account_assets" => Endpoint {
            path: "/api/v2/mix/account/sub-account-assets",
            post: false,
            public: false,
            fields: &["productType"],
            required: &["productType"],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-contract-account/classic-contract-account#my-estimated-open-count
        "get_spot_sub_account_assets" => Endpoint {
            path: "/api/v2/spot/account/subaccount-assets",
            post: false,
            public: false,
            fields: &["idLessThan", "limit"],
            required: &[],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-spot-account/classic-spot-account#sub-transfer
        "get_uta_sub_accounts" => Endpoint {
            path: "/api/v3/user/sub-list",
            post: false,
            public: false,
            fields: &["limit", "cursor"],
            required: &[],
            arrays: &[],
            limit: Some(100),
            days: Some(90),
        },
        // https://www.bitget.com/legacy-docs/uta/account/sub-account/Get-SubAccount-Unified-Assets
        "get_uta_sub_account_assets" => Endpoint {
            path: "/api/v3/account/sub-unified-assets",
            post: false,
            public: false,
            fields: &["subUid", "cursor", "limit"],
            required: &[],
            arrays: &[],
            limit: Some(50),
            days: Some(90),
        },
        // https://www.bitget.com/legacy-docs/uta/strategy/Get-Strategy-Sub-Orders
        "get_sub_account_deposit_address" => Endpoint {
            path: "/api/v2/spot/wallet/subaccount-deposit-address",
            post: false,
            public: false,
            fields: &["subUid", "coin", "chain", "size"],
            required: &["subUid", "coin"],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-spot-account/classic-spot-account#get-subaccount-deposit-records
        "get_sub_account_deposit_records" => Endpoint {
            path: "/api/v2/spot/wallet/subaccount-deposit-records",
            post: false,
            public: false,
            fields: &[
                "subUid",
                "coin",
                "startTime",
                "endTime",
                "idLessThan",
                "limit",
            ],
            required: &["subUid"],
            arrays: &[],
            limit: Some(100),
            days: None,
        },
        // https://www.bitget.com/legacy-docs/uta/account/Deposit-Account
        "create_uta_sub_account" => Endpoint {
            path: "/api/v3/user/create-sub",
            post: true,
            public: false,
            fields: &["username", "accountMode", "note"],
            required: &["username"],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/legacy-docs/uta/public/Get-Cash-Dividend-Records
        "classic_create_virtual_subaccount" => Endpoint {
            path: "/api/v2/user/create-virtual-subaccount",
            post: true,
            public: false,
            fields: &["subAccountList"],
            required: &["subAccountList"],
            arrays: &["subAccountList"],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-common-vsubaccount/classic-common-vsubaccount#create-virtual-subaccount-apikey
        "classic_create_virtual_subaccount_apikey" => Endpoint {
            path: "/api/v2/user/create-virtual-subaccount-apikey",
            post: true,
            public: false,
            fields: &["subAccountUid", "passphrase", "label", "permList", "ipList"],
            required: &["subAccountUid", "passphrase", "label", "permList"],
            arrays: &["permList", "ipList"],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-common-vsubaccount/classic-common-vsubaccount#modify-virtual-subaccount
        "classic_modify_virtual_subaccount" => Endpoint {
            path: "/api/v2/user/modify-virtual-subaccount",
            post: true,
            public: false,
            fields: &["subAccountUid", "permList", "status"],
            required: &["subAccountUid", "permList", "status"],
            arrays: &["permList"],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-common-vsubaccount/classic-common-vsubaccount#modify-virtual-subaccount-apikey
        "classic_modify_virtual_subaccount_apikey" => Endpoint {
            path: "/api/v2/user/modify-virtual-subaccount-apikey",
            post: true,
            public: false,
            fields: &[
                "subAccountUid",
                "passphrase",
                "label",
                "subAccountApiKey",
                "ipList",
                "permList",
            ],
            required: &["subAccountUid", "passphrase", "label", "subAccountApiKey"],
            arrays: &["ipList", "permList"],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-common-vsubaccount/classic-common-vsubaccount#get-virtual-subaccounts
        "get_classic_virtual_subaccount_list" => Endpoint {
            path: "/api/v2/user/virtual-subaccount-list",
            post: false,
            public: false,
            fields: &["limit", "idLessThan", "status"],
            required: &[],
            arrays: &[],
            limit: Some(500),
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-common-vsubaccount/classic-common-vsubaccount#get-subaccount-apikey-list
        "get_classic_virtual_subaccount_apikey_list" => Endpoint {
            path: "/api/v2/user/virtual-subaccount-apikey-list",
            post: false,
            public: false,
            fields: &["subAccountUid"],
            required: &["subAccountUid"],
            arrays: &[],
            limit: None,
            days: None,
        },
        // https://www.bitget.com/docs/catalog/classic-margin-common/classic-margin-common#get-the-leverage-interest-rate
        "batch_create_classic_sub_accounts" => Endpoint {
            path: "/api/v2/user/batch-create-subaccount-and-apikey",
            post: true,
            public: false,
            fields: &["accounts"],
            required: &["accounts"],
            arrays: &[],
            limit: None,
            days: None,
        },
        _ => return None,
    })
}
