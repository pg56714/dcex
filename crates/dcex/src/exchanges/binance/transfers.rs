//! Fund movement and batch request implementations.

mod account_operations {
    use crate::Result;
    use crate::exchange::ValidatedResponse;
    use crate::exchanges::binance::account::*;
    use crate::exchanges::binance::client::{BinanceClient, BinanceMarket};

    use crate::exchanges::binance::params::{
        BinanceUniversalTransferHistoryParams, BinanceUniversalTransferParams, push_optional,
        push_optional_display,
    };
    use crate::http::HttpMethod;
    impl BinanceClient {
        pub fn create_universal_transfer(
            &self,
            transfer_type: &str,
            asset: &str,
            amount: &str,
        ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
            crate::exchanges::ExchangeMethodRequest::private(
                self,
                "create_universal_transfer",
                vec![
                    ("type".to_string(), transfer_type.to_string()),
                    ("asset".to_string(), asset.to_string()),
                    ("amount".to_string(), amount.to_string()),
                ],
            )
        }

        pub(in crate::exchanges::binance) async fn send_create_universal_transfer(
            &self,
            transfer_type: &str,
            asset: &str,
            amount: &str,
            request: BinanceUniversalTransferParams<'_>,
        ) -> Result<ValidatedResponse> {
            let mut params = vec![
                ("type".to_string(), transfer_type.to_string()),
                ("asset".to_string(), asset.to_string()),
                ("amount".to_string(), amount.to_string()),
            ];
            push_optional(&mut params, "fromSymbol", request.from_symbol);
            push_optional(&mut params, "toSymbol", request.to_symbol);
            self.request(
                HttpMethod::Post,
                BinanceMarket::Spot,
                UNIVERSAL_TRANSFER,
                params,
                true,
            )
            .await
        }

        pub fn get_universal_transfer_history(
            &self,
            transfer_type: &str,
        ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
            crate::exchanges::ExchangeMethodRequest::private(
                self,
                "get_universal_transfer_history",
                vec![("type".to_string(), transfer_type.to_string())],
            )
        }

        pub(in crate::exchanges::binance) async fn send_get_universal_transfer_history(
            &self,
            transfer_type: &str,
            request: BinanceUniversalTransferHistoryParams<'_>,
        ) -> Result<ValidatedResponse> {
            let mut params = vec![("type".to_string(), transfer_type.to_string())];
            push_optional_display(&mut params, "startTime", request.start_time);
            push_optional_display(&mut params, "endTime", request.end_time);
            push_optional_display(&mut params, "current", request.current);
            push_optional_display(&mut params, "size", request.size);
            push_optional(&mut params, "fromSymbol", request.from_symbol);
            push_optional(&mut params, "toSymbol", request.to_symbol);
            self.request(
                HttpMethod::Get,
                BinanceMarket::Spot,
                UNIVERSAL_TRANSFER,
                params,
                true,
            )
            .await
        }
    }
}

mod subaccount_operations {

    use crate::exchanges::binance::client::BinanceClient;

    impl BinanceClient {
        pub fn transfer_subaccount_futures(
            &self,
            email: &str,
            asset: &str,
            amount: &str,
            transfer_type: u8,
        ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
            self.subaccount_request(
                "transfer_subaccount_futures",
                vec![
                    ("email".to_string(), email.to_string()),
                    ("asset".to_string(), asset.to_string()),
                    ("amount".to_string(), amount.to_string()),
                    ("type".to_string(), transfer_type.to_string()),
                ],
            )
        }

        pub fn transfer_subaccount_margin(
            &self,
            email: &str,
            asset: &str,
            amount: &str,
            transfer_type: u8,
        ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
            self.subaccount_request(
                "transfer_subaccount_margin",
                vec![
                    ("email".to_string(), email.to_string()),
                    ("asset".to_string(), asset.to_string()),
                    ("amount".to_string(), amount.to_string()),
                    ("type".to_string(), transfer_type.to_string()),
                ],
            )
        }

        pub fn transfer_between_subaccount_futures(
            &self,
            from_email: &str,
            to_email: &str,
            futures_type: u8,
            asset: &str,
            amount: &str,
        ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
            self.subaccount_request(
                "transfer_between_subaccount_futures",
                vec![
                    ("fromEmail".to_string(), from_email.to_string()),
                    ("toEmail".to_string(), to_email.to_string()),
                    ("futuresType".to_string(), futures_type.to_string()),
                    ("asset".to_string(), asset.to_string()),
                    ("amount".to_string(), amount.to_string()),
                ],
            )
        }

        pub fn transfer_subaccount_to_master(
            &self,
            asset: &str,
            amount: &str,
        ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
            self.subaccount_request(
                "transfer_subaccount_to_master",
                vec![
                    ("asset".to_string(), asset.to_string()),
                    ("amount".to_string(), amount.to_string()),
                ],
            )
        }

        pub fn transfer_subaccount_to_subaccount(
            &self,
            to_email: &str,
            asset: &str,
            amount: &str,
        ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
            self.subaccount_request(
                "transfer_subaccount_to_subaccount",
                vec![
                    ("toEmail".to_string(), to_email.to_string()),
                    ("asset".to_string(), asset.to_string()),
                    ("amount".to_string(), amount.to_string()),
                ],
            )
        }

        pub fn transfer_between_subaccounts(
            &self,
            from_account_type: &str,
            to_account_type: &str,
            asset: &str,
            amount: &str,
        ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
            self.subaccount_request(
                "transfer_between_subaccounts",
                vec![
                    ("fromAccountType".to_string(), from_account_type.to_string()),
                    ("toAccountType".to_string(), to_account_type.to_string()),
                    ("asset".to_string(), asset.to_string()),
                    ("amount".to_string(), amount.to_string()),
                ],
            )
        }
    }
}

pub(super) fn subaccount_transfer_route(
    method_name: &str,
) -> (
    crate::http::HttpMethod,
    &'static str,
    &'static [&'static str],
) {
    use super::endpoints::*;
    use crate::http::HttpMethod;
    match method_name {
        "transfer_subaccount_futures" => (
            HttpMethod::Post,
            SUBACCOUNT_FUTURES_TRANSFER,
            &["email", "asset", "amount", "type"],
        ),
        "transfer_subaccount_margin" => (
            HttpMethod::Post,
            SUBACCOUNT_MARGIN_TRANSFER,
            &["email", "asset", "amount", "type"],
        ),
        "transfer_between_subaccount_futures" => (
            HttpMethod::Post,
            SUBACCOUNT_FUTURES_INTERNAL_TRANSFER,
            &["fromEmail", "toEmail", "futuresType", "asset", "amount"],
        ),
        "transfer_between_subaccounts" => (
            HttpMethod::Post,
            SUBACCOUNT_UNIVERSAL_TRANSFER,
            &["fromAccountType", "toAccountType", "asset", "amount"],
        ),
        "transfer_subaccount_to_master" => (
            HttpMethod::Post,
            SUBACCOUNT_TO_MASTER_TRANSFER,
            &["asset", "amount"],
        ),
        "transfer_subaccount_to_subaccount" => (
            HttpMethod::Post,
            SUBACCOUNT_TO_SUBACCOUNT_TRANSFER,
            &["toEmail", "asset", "amount"],
        ),
        _ => unreachable!("validated subaccount transfer method"),
    }
}

impl super::client::BinanceClient {
    pub(in crate::exchanges::binance) async fn transfers_table_request(
        &self,
        name: &str,
        params: &super::params::PublicParams,
        public: bool,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        debug_assert!(
            crate::exchanges::schema::fund_domain(name)
                == Some(crate::exchanges::schema::FundDomain::Transfers)
        );
        self.table_request_transport(name, params, public).await
    }
}

impl super::client::BinanceClient {
    pub(in crate::exchanges::binance) async fn transfers_field_schema_request(
        &self,
        name: &str,
        p: &super::params::PublicParams,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        debug_assert!(
            crate::exchanges::schema::fund_domain(name)
                == Some(crate::exchanges::schema::FundDomain::Transfers)
        );
        self.field_schema_request_transport(name, p).await
    }
}

impl super::client::BinanceClient {
    pub(in crate::exchanges::binance) async fn transfers_catalog_request(
        &self,
        name: &str,
        p: &super::params::PublicParams,
        public: bool,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        debug_assert!(
            crate::exchanges::schema::fund_domain(name)
                == Some(crate::exchanges::schema::FundDomain::Transfers)
        );
        self.catalog_request_transport(name, p, public).await
    }
}

impl super::client::BinanceClient {
    pub(super) async fn subaccount_transfer_request(
        &self,
        method_name: &str,
        params: &super::params::PublicParams,
    ) -> crate::Result<Option<crate::exchange::ValidatedResponse>> {
        let (method, path, required) = subaccount_transfer_route(method_name);
        for field in required {
            params.required(field)?;
        }
        Ok(Some(
            self.request(
                method,
                super::client::BinanceMarket::Spot,
                path,
                params.without(&[]),
                true,
            )
            .await?,
        ))
    }
}
