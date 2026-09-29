//! Fund and batch request implementations.

mod account_requests {
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::mexc::account::*;
    use crate::exchanges::mexc::client::MexcClient;

    use crate::Result;
    use crate::exchanges::mexc::params::{MexcParams, validate_u64_range};
    use crate::http::HttpMethod;

    impl MexcClient {
        pub(in crate::exchanges::mexc) async fn dispatch_get_withdraw_history(
            &self,
            _method_name: &str,
            params: &MexcParams,
        ) -> Result<ValidatedResponse> {
            {
                params.ensure_allowed(&[
                    "coin",
                    "status",
                    "startTime",
                    "endTime",
                    "limit",
                    "recvWindow",
                ])?;
                validate_u64_range(params, "status", 1, 10)?;
                validate_u64_range(params, "limit", 1, 1_000)?;
                self.spot_private(
                    HttpMethod::Get,
                    SPOT_WITHDRAW_HISTORY,
                    params.only(&[
                        "coin",
                        "status",
                        "startTime",
                        "endTime",
                        "limit",
                        "recvWindow",
                    ]),
                )
                .await
            }
        }
    }
}

mod wallet_requests {
    // Wallet operations.
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::mexc::client::{MexcApi, MexcClient};
    use crate::exchanges::mexc::params::{MexcParams, validate_u64_range};
    use crate::http::HttpMethod;
    use crate::{DcexError, Result};
    impl MexcClient {
        pub(in crate::exchanges::mexc) async fn wallet_schema_request(
            &self,
            name: &str,
            p: &MexcParams,
            public: bool,
        ) -> Result<Option<ValidatedResponse>> {
            let (path, api, verb, signed, allowed, required): (
                &str,
                MexcApi,
                HttpMethod,
                bool,
                &[&str],
                &[&str],
            ) = match name {
                "create_deposit_address" => (
                    "/api/v3/capital/deposit/address",
                    MexcApi::Spot,
                    HttpMethod::Post,
                    true,
                    &["coin", "network"],
                    &["coin", "network"],
                ),
                "get_withdrawal_addresses" => (
                    "/api/v3/capital/withdraw/address",
                    MexcApi::Spot,
                    HttpMethod::Get,
                    true,
                    &["coin", "page", "limit"],
                    &[],
                ),
                _ => return Ok(None),
            };
            if public == signed {
                return Ok(None);
            }
            p.ensure_allowed(allowed)?;
            validate_u64_range(p, "recvWindow", 1, 60_000)?;
            let query = p.only(allowed);
            let unique: std::collections::BTreeSet<_> = query.iter().map(|(k, _)| k).collect();
            if unique.len() != query.len() {
                return Err(DcexError::InvalidInput("duplicate MEXC parameter".into()));
            }
            for key in required {
                if p.required(key)?.trim().is_empty() {
                    return Err(DcexError::InvalidInput(format!("{key} cannot be empty")));
                }
            }
            validate_u64_range(p, "page", 1, u64::MAX)?;
            validate_u64_range(p, "limit", 1, 1000)?;
            validate_u64_range(p, "startTime", 0, u64::MAX)?;
            validate_u64_range(p, "endTime", 0, u64::MAX)?;
            if let (Some(start), Some(end)) = (p.get("startTime"), p.get("endTime"))
                && start.parse::<u64>().unwrap() > end.parse::<u64>().unwrap()
            {
                return Err(DcexError::InvalidInput("startTime exceeds endTime".into()));
            }
            let path = path.to_string();
            Ok(Some(
                self.request(verb, api, path, query, None, signed).await?,
            ))
        }
    }
}

mod wrappers {
    use crate::exchanges::mexc::MexcClient;
    crate::exchanges::impl_exchange_method_wrappers! {
     @extend; MexcClient;
     public [

     ];
     private [
    get_withdraw_history()
     ];
    }
}

impl super::client::MexcClient {
    pub(in crate::exchanges::mexc) async fn withdrawals_field_schema_request(
        &self,
        name: &str,
        p: &super::params::MexcParams,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        if crate::exchanges::schema::fund_domain(name)
            != Some(crate::exchanges::schema::FundDomain::Withdrawals)
        {
            return Err(crate::DcexError::InvalidInput(
                "fund operation routed to the wrong owner".into(),
            ));
        }
        self.field_schema_request_transport(name, p).await
    }
}
