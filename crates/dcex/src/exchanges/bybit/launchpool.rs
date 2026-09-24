use serde_json::{Map, Value};

use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::BybitClient;
use super::endpoints::*;
use super::params::BybitParams;

impl BybitClient {
    pub(super) async fn launchpool_public_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        if method_name != "get_launchpool_projects" {
            return Ok(None);
        }
        let status = parse_u64(params, "status")?.ok_or_else(|| {
            DcexError::InvalidInput("missing required parameter: status".to_string())
        })?;
        if status > 2 {
            return Err(DcexError::InvalidInput(
                "status must be 0, 1, or 2".to_string(),
            ));
        }
        validate_bounded(params, "limit", 10)?;
        let result = self
            .request(
                HttpMethod::Get,
                LAUNCHPOOL_PROJECTS,
                params.only(&["status", "activityCoin", "projectId", "cursor", "limit"]),
                None,
                false,
            )
            .await?;
        Ok(Some(result))
    }

    pub(super) async fn launchpool_private_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_launchpool_current_staking" => {
                self.get_request(LAUNCHPOOL_CURRENT_STAKING, vec![]).await
            }
            "get_launchpool_activity_log" => {
                validate_bounded(params, "pageSize", 10)?;
                validate_bounded(params, "current", 100)?;
                validate_time_pair(params)?;
                validate_optional_max(params, "type", 10)?;
                validate_optional_max(params, "status", 2)?;
                let body = launchpool_body(
                    params,
                    &["stakeCoin", "startTime", "endTime"],
                    &["type", "status", "pageSize", "current"],
                )?;
                self.post_request(LAUNCHPOOL_ACTIVITY_LOG, body).await
            }
            "get_launchpool_history" => {
                validate_bounded(params, "pageSize", 10)?;
                validate_bounded(params, "current", 100)?;
                validate_time_pair(params)?;
                let body = launchpool_body(
                    params,
                    &["stakeCoin", "rewardCoin", "startTime", "endTime"],
                    &["pageSize", "current"],
                )?;
                self.post_request(LAUNCHPOOL_HISTORY, body).await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}

fn parse_u64(params: &BybitParams, key: &str) -> Result<Option<u64>> {
    params
        .get(key)
        .map(|value| {
            value
                .parse::<u64>()
                .map_err(|error| DcexError::InvalidInput(format!("invalid {key}: {error}")))
        })
        .transpose()
}

fn validate_bounded(params: &BybitParams, key: &str, maximum: u64) -> Result<()> {
    if let Some(value) = parse_u64(params, key)? {
        if !(1..=maximum).contains(&value) {
            return Err(DcexError::InvalidInput(format!(
                "{key} must be between 1 and {maximum}"
            )));
        }
    }
    Ok(())
}

fn validate_optional_max(params: &BybitParams, key: &str, maximum: u64) -> Result<()> {
    if let Some(value) = parse_u64(params, key)? {
        if value > maximum {
            return Err(DcexError::InvalidInput(format!(
                "{key} must not exceed {maximum}"
            )));
        }
    }
    Ok(())
}

fn validate_time_pair(params: &BybitParams) -> Result<()> {
    match (params.get("startTime"), params.get("endTime")) {
        (None, None) => Ok(()),
        (Some(start), Some(end)) => {
            let parse = |value: &str| -> Result<u64> {
                if value.len() != 13 {
                    return Err(DcexError::InvalidInput(
                        "Launchpool times must be 13-digit Unix milliseconds".to_string(),
                    ));
                }
                value
                    .parse::<u64>()
                    .map_err(|error| DcexError::InvalidInput(format!("invalid time: {error}")))
            };
            if parse(start)? > parse(end)? {
                return Err(DcexError::InvalidInput(
                    "endTime must not be earlier than startTime".to_string(),
                ));
            }
            Ok(())
        }
        _ => Err(DcexError::InvalidInput(
            "startTime and endTime must be provided together".to_string(),
        )),
    }
}

fn launchpool_body(
    params: &BybitParams,
    string_keys: &[&str],
    integer_keys: &[&str],
) -> Result<Map<String, Value>> {
    let mut body = Map::new();
    for key in string_keys {
        if let Some(value) = params.get(key) {
            body.insert((*key).to_string(), Value::String(value.to_string()));
        }
    }
    for key in integer_keys {
        if let Some(value) = parse_u64(params, key)? {
            body.insert((*key).to_string(), Value::from(value));
        }
    }
    Ok(body)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn launchpool_filters_are_bounded_and_times_are_paired() {
        let invalid_page = BybitParams::from_pairs(vec![("pageSize".into(), "11".into())]);
        assert!(validate_bounded(&invalid_page, "pageSize", 10).is_err());
        let unpaired = BybitParams::from_pairs(vec![("startTime".into(), "1705000000000".into())]);
        assert!(validate_time_pair(&unpaired).is_err());
        let paired = BybitParams::from_pairs(vec![
            ("startTime".into(), "1705000000000".into()),
            ("endTime".into(), "1705000000001".into()),
        ]);
        assert!(validate_time_pair(&paired).is_ok());
    }
}
