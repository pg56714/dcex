use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::BitmexClient;
use super::endpoints::ACCOUNT_INFO;
use super::endpoints::USER_COMMISSION;
use super::params::BitmexParams;

const WALLET_SUMMARY_KEYS: &[&str] = &[
    "currency",
    "startTime",
    "endTime",
    "targetAccountId",
    "targetAccountIds",
    "targetAccountIds[]",
];

impl BitmexClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &BitmexParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_futures_fee_rates" => self.get_private(USER_COMMISSION, Vec::new()).await,
            "get_wallet_summary" => {
                self.get_private(ACCOUNT_INFO, params.only(WALLET_SUMMARY_KEYS))
                    .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
