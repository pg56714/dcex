use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::BybitClient;
use super::endpoints::{HOLD_TO_EARN_PRODUCT, HOLD_TO_EARN_YIELD_HISTORY};
use super::params::BybitParams;

impl BybitClient {
    pub(super) async fn hold_to_earn_public_request(
        &self,
        method_name: &str,
        _params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        if method_name != "get_hold_to_earn_products" {
            return Ok(None);
        }
        let result = self
            .request(HttpMethod::Get, HOLD_TO_EARN_PRODUCT, vec![], None, false)
            .await?;
        Ok(Some(result))
    }

    pub(super) async fn hold_to_earn_private_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        if method_name != "get_hold_to_earn_yield_history" {
            return Ok(None);
        }
        let limit = params
            .required("limit")?
            .parse::<u16>()
            .map_err(|error| DcexError::InvalidInput(format!("invalid limit: {error}")))?;
        if !(1..=49).contains(&limit) {
            return Err(DcexError::InvalidInput(
                "limit must be between 1 and 49".to_string(),
            ));
        }
        let start = parse_optional_time(params, "timeStart")?;
        let end = parse_optional_time(params, "timeEnd")?;
        if let (Some(start), Some(end)) = (start, end) {
            if end < start {
                return Err(DcexError::InvalidInput(
                    "timeEnd must not be earlier than timeStart".to_string(),
                ));
            }
        }
        let result = self
            .get_request(
                HOLD_TO_EARN_YIELD_HISTORY,
                params.only(&["timeStart", "timeEnd", "limit", "cursor"]),
            )
            .await?;
        Ok(Some(result))
    }
}

fn parse_optional_time(params: &BybitParams, key: &str) -> Result<Option<u64>> {
    params
        .get(key)
        .map(|value| {
            value
                .parse::<u64>()
                .map_err(|error| DcexError::InvalidInput(format!("invalid {key}: {error}")))
        })
        .transpose()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn unix_seconds_must_be_unsigned() {
        let params = BybitParams::from_pairs(vec![("timeStart".to_string(), "-1".to_string())]);
        assert!(parse_optional_time(&params, "timeStart").is_err());
    }
}
