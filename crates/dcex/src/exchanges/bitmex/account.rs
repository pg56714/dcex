use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::BitmexClient;
use super::endpoints::USER_COMMISSION;
use super::endpoints::WALLET_SUMMARY;
use super::params::BitmexParams;

const WALLET_SUMMARY_KEYS: &[&str] = &["currency", "startTime", "endTime"];

impl BitmexClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &BitmexParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_futures_fee_rates" => {
                params.ensure_allowed(&[])?;
                self.get_private(USER_COMMISSION, Vec::new()).await
            }
            "get_wallet_summary" => {
                params.ensure_allowed(WALLET_SUMMARY_KEYS)?;
                self.get_private(WALLET_SUMMARY, params.only(WALLET_SUMMARY_KEYS))
                    .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
