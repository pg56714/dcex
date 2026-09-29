//! Fund and batch request implementations.

mod account_requests {
    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::kucoin::account::*;
    use crate::exchanges::kucoin::client::{KucoinClient, KucoinMarket};

    use crate::exchanges::kucoin::params::{
        KucoinParams, generate_client_oid, insert_optional_string, insert_required_string,
        validate_positive_number, validate_text_length,
    };
    use serde_json::{Map, Value};
    impl KucoinClient {
        pub(in crate::exchanges::kucoin) async fn dispatch_get_transfer_quotas(
            &self,
            _method_name: &str,
            params: &KucoinParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&["currency", "account_type", "type", "tag"])?;
                let account_type = params.required_any(&["account_type", "type"])?;
                if !matches!(
                    account_type,
                    "MAIN" | "TRADE" | "MARGIN" | "ISOLATED" | "MARGIN_V2" | "ISOLATED_V2"
                ) {
                    return Err(crate::DcexError::InvalidInput(format!(
                        "unsupported KuCoin account type: {account_type}"
                    )));
                }
                let mut query = Vec::new();
                query.push((
                    "currency".to_string(),
                    params.required("currency")?.to_string(),
                ));
                query.push(("type".to_string(), account_type.to_string()));
                if let Some(tag) = params.get("tag") {
                    query.push(("tag".to_string(), tag.to_string()));
                }
                self.private_get(KucoinMarket::Spot, SPOT_TRANSFER_QUOTAS, query)
                    .await
            }
        }
        pub(in crate::exchanges::kucoin) async fn dispatch_flex_transfer(
            &self,
            _method_name: &str,
            params: &KucoinParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&[
                    "clientOid",
                    "currency",
                    "amount",
                    "fromUserId",
                    "fromAccountType",
                    "fromAccountTag",
                    "transfer_type",
                    "type",
                    "toUserId",
                    "toAccountType",
                    "toAccountTag",
                ])?;
                validate_positive_number(params, "amount")?;
                validate_text_length(params, "clientOid", 128, true)?;
                let transfer_type = params
                    .get_any(&["transfer_type", "type"])
                    .unwrap_or("INTERNAL");
                if !matches!(
                    transfer_type,
                    "INTERNAL" | "PARENT_TO_SUB" | "SUB_TO_PARENT" | "SUB_TO_SUB"
                ) {
                    return Err(crate::DcexError::InvalidInput(format!(
                        "unsupported KuCoin transfer type: {transfer_type}"
                    )));
                }
                validate_transfer_parties(params, transfer_type)?;
                validate_transfer_account_versions(params, transfer_type)?;
                validate_account_tag(params, "fromAccountType", "fromAccountTag")?;
                validate_account_tag(params, "toAccountType", "toAccountTag")?;
                let mut body = Map::new();
                let client_oid = params
                    .get("clientOid")
                    .map(str::to_string)
                    .unwrap_or_else(generate_client_oid);
                insert_required_string(&mut body, "clientOid", &client_oid);
                insert_required_string(&mut body, "type", transfer_type);
                insert_required_string(&mut body, "currency", params.required("currency")?);
                insert_required_string(&mut body, "amount", params.required("amount")?);
                insert_required_string(
                    &mut body,
                    "fromAccountType",
                    params.required("fromAccountType")?,
                );
                insert_required_string(
                    &mut body,
                    "toAccountType",
                    params.required("toAccountType")?,
                );
                insert_optional_string(&mut body, "fromUserId", params.get("fromUserId"));
                insert_optional_string(&mut body, "fromAccountTag", params.get("fromAccountTag"));
                insert_optional_string(&mut body, "toUserId", params.get("toUserId"));
                insert_optional_string(&mut body, "toAccountTag", params.get("toAccountTag"));
                self.private_post(KucoinMarket::Spot, SPOT_FLEX_TRANSFER, Value::Object(body))
                    .await
            }
        }
    }
}

mod wrappers {
    use crate::exchanges::kucoin::KucoinClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; KucoinClient;
     public [

     ];
     private [
    transfer_uta_accounts(client_oid => "clientOid", transfer_type => "transferType", currency => "currency", amount => "amount", from_account_type => "fromAccountType", from_account_tag => "fromAccountTag", to_account_type => "toAccountType", to_account_tag => "toAccountTag"),
    get_uta_transfer_quota(account_type => "accountType", currency => "currency"),
    flex_transfer(currency => "currency", amount => "amount", from_account_type => "fromAccountType", to_account_type => "toAccountType"),
    get_transfer_quotas(currency => "currency", account_type => "account_type")
     ];
    }
}

impl super::client::KucoinClient {
    pub(in crate::exchanges::kucoin) async fn transfers_table_request(
        &self,
        name: &str,
        params: &super::params::KucoinParams,
        public: bool,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        if crate::exchanges::schema::fund_domain(name)
            != Some(crate::exchanges::schema::FundDomain::Transfers)
        {
            return Err(crate::DcexError::InvalidInput(
                "fund operation routed to the wrong owner".into(),
            ));
        }
        self.table_request_transport(name, params, public).await
    }
}

impl super::client::KucoinClient {
    pub(in crate::exchanges::kucoin) async fn transfers_catalog_request(
        &self,
        name: &str,
        params: &super::params::KucoinParams,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        if crate::exchanges::schema::fund_domain(name)
            != Some(crate::exchanges::schema::FundDomain::Transfers)
        {
            return Err(crate::DcexError::InvalidInput(
                "fund operation routed to the wrong owner".into(),
            ));
        }
        self.catalog_request_transport(name, params).await
    }
}
