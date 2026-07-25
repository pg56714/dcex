use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::BitmexClient;
use super::endpoints::{GET_EXECUTIONS, GET_TRADE_HISTORY, GET_TRADING_VOLUME};
use super::params::{
    validate_bool, validate_enum, validate_i64, validate_json_object, validate_u64_range,
    BitmexParams,
};

const HISTORY_KEYS: &[&str] = &[
    "pool",
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
                validate_history_params(params)?;
                let mut query = params.only(HISTORY_KEYS);
                self.push_product_symbol(&mut query, params)?;
                self.get_private(GET_EXECUTIONS, query).await
            }
            "get_trade_history" => {
                validate_history_params(params)?;
                let mut query = params.only(HISTORY_KEYS);
                self.push_product_symbol(&mut query, params)?;
                self.get_private(GET_TRADE_HISTORY, query).await
            }
            "get_trading_volume" => {
                params.ensure_allowed(&[])?;
                self.get_private(GET_TRADING_VOLUME, Vec::new()).await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}

fn validate_history_params(params: &BitmexParams) -> Result<()> {
    let mut allowed = HISTORY_KEYS.to_vec();
    allowed.extend(["product_symbol", "symbol"]);
    params.ensure_allowed(&allowed)?;
    validate_enum(params, "pool", &["Primary", "Secondary", "Aggregated"])?;
    validate_json_object(params, "filter")?;
    validate_u64_range(params, "count", 0, 500)?;
    validate_u64_range(params, "start", 0, i32::MAX as u64)?;
    validate_bool(params, "reverse")?;
    validate_i64(params, "targetAccountId")?;
    Ok(())
}
