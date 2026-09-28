pub(in crate::exchanges::binance) use super::client::{BinanceClient, BinanceMarket};
pub(in crate::exchanges::binance) use super::endpoints::*;
pub(in crate::exchanges::binance) use super::params::PublicParams;
pub(in crate::exchanges::binance) use crate::Result;
pub(in crate::exchanges::binance) use crate::exchange::ValidatedResponse;
pub(in crate::exchanges::binance) use crate::http::HttpMethod;

macro_rules! subaccount_query_methods {
    ($($name:ident),+ $(,)?) => {
        $(
            pub fn $name(&self) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
                self.subaccount_request(stringify!($name), Vec::new())
            }
        )+
    };
}

impl BinanceClient {
    pub(in crate::exchanges::binance) fn subaccount_request(
        &self,
        method_name: &'static str,
        params: Vec<(String, String)>,
    ) -> crate::exchanges::ExchangeMethodRequest<'_, Self> {
        crate::exchanges::ExchangeMethodRequest::private(self, method_name, params)
    }

    subaccount_query_methods!(
        get_subaccounts,
        get_subaccount_status,
        get_subaccount_transaction_statistics,
        get_subaccount_futures_position_risk,
        get_subaccount_futures_account,
        get_subaccount_margin_account,
        get_subaccount_futures_summary,
        get_subaccount_margin_summary,
        get_subaccount_assets,
        get_subaccount_spot_summary,
        get_subaccount_futures_transfer_history,
        get_subaccount_spot_transfer_history,
        get_subaccount_universal_transfer_history,
        get_subaccount_transfer_history,
    );

    pub(super) async fn subaccount_private_request(
        &self,
        method_name: &str,
        params: &PublicParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (method, path, required): (HttpMethod, &str, &[&str]) = match method_name {
            "get_subaccounts" => (HttpMethod::Get, SUBACCOUNT_LIST, &[]),
            "get_subaccount_status" => (HttpMethod::Get, SUBACCOUNT_STATUS, &[]),
            "get_subaccount_transaction_statistics" => (
                HttpMethod::Get,
                SUBACCOUNT_TRANSACTION_STATISTICS,
                &["email"],
            ),
            "get_subaccount_futures_position_risk" => (
                HttpMethod::Get,
                SUBACCOUNT_FUTURES_POSITION_RISK,
                &["email", "futuresType"],
            ),
            "get_subaccount_futures_account" => (
                HttpMethod::Get,
                SUBACCOUNT_FUTURES_ACCOUNT,
                &["email", "futuresType"],
            ),
            "get_subaccount_margin_account" => {
                (HttpMethod::Get, SUBACCOUNT_MARGIN_ACCOUNT, &["email"])
            }
            "get_subaccount_futures_summary" => (
                HttpMethod::Get,
                SUBACCOUNT_FUTURES_SUMMARY,
                &["futuresType"],
            ),
            "get_subaccount_margin_summary" => (HttpMethod::Get, SUBACCOUNT_MARGIN_SUMMARY, &[]),
            "get_subaccount_assets" => (HttpMethod::Get, SUBACCOUNT_ASSETS, &["email"]),
            "get_subaccount_spot_summary" => (HttpMethod::Get, SUBACCOUNT_SPOT_SUMMARY, &[]),
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
            "get_subaccount_futures_transfer_history" => (
                HttpMethod::Get,
                SUBACCOUNT_FUTURES_TRANSFER_HISTORY,
                &["email", "futuresType"],
            ),
            "transfer_between_subaccount_futures" => (
                HttpMethod::Post,
                SUBACCOUNT_FUTURES_INTERNAL_TRANSFER,
                &["fromEmail", "toEmail", "futuresType", "asset", "amount"],
            ),
            "get_subaccount_spot_transfer_history" => {
                (HttpMethod::Get, SUBACCOUNT_SPOT_TRANSFER_HISTORY, &[])
            }
            "get_subaccount_universal_transfer_history" => {
                (HttpMethod::Get, SUBACCOUNT_UNIVERSAL_TRANSFER, &[])
            }
            "transfer_between_subaccounts" => (
                HttpMethod::Post,
                SUBACCOUNT_UNIVERSAL_TRANSFER,
                &["fromAccountType", "toAccountType", "asset", "amount"],
            ),
            "get_subaccount_transfer_history" => {
                (HttpMethod::Get, SUBACCOUNT_TRANSFER_HISTORY, &[])
            }
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
            _ => return Ok(None),
        };

        for field in required {
            params.required(field)?;
        }
        Ok(Some(
            self.request(method, BinanceMarket::Spot, path, params.without(&[]), true)
                .await?,
        ))
    }
}
