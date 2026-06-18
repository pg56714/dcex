use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::BitmexClient;
use super::endpoints::{GET_EXECUTIONS, GET_TRADE_HISTORY, GET_TRADING_VOLUME};
use super::params::BitmexParams;

const HISTORY_KEYS: &[&str] = &[
    "filter",
    "columns",
    "count",
    "start",
    "reverse",
    "startTime",
    "endTime",
    "targetAccountId",
    "targetAccountIds",
    "targetAccountIds[]",
];

impl BitmexClient {
    pub(super) async fn trading_private_request(
        &self,
        method_name: &str,
        params: &BitmexParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_executions" => {
                let mut query = params.only(HISTORY_KEYS);
                self.push_product_symbol(&mut query, params)?;
                self.get_private(GET_EXECUTIONS, query).await
            }
            "get_trade_history" => {
                let mut query = params.only(HISTORY_KEYS);
                self.push_product_symbol(&mut query, params)?;
                self.get_private(GET_TRADE_HISTORY, query).await
            }
            "get_trading_volume" => self.get_private(GET_TRADING_VOLUME, Vec::new()).await,
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
