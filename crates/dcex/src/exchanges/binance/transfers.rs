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
