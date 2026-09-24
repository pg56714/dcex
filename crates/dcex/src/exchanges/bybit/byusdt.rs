use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::BybitClient;
use super::endpoints::*;
use super::params::{string_body, BybitParams};

const COIN: &str = "BYUSDT";

impl BybitClient {
    pub(super) async fn byusdt_public_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, mut query) = match method_name {
            "get_byusdt_product" => (BYUSDT_PRODUCT, vec![]),
            "get_byusdt_apr_history" => {
                let range = params.required("range")?;
                if !matches!(range, "1" | "2" | "3") {
                    return Err(DcexError::InvalidInput(
                        "range must be 1, 2, or 3".to_string(),
                    ));
                }
                (BYUSDT_APR_HISTORY, params.only(&["range"]))
            }
            _ => return Ok(None),
        };
        query.insert(0, ("coin".to_string(), COIN.to_string()));
        let result = self
            .request(HttpMethod::Get, path, query, None, false)
            .await?;
        Ok(Some(result))
    }

    pub(super) async fn byusdt_private_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_byusdt_orders" => {
                validate_optional_order_type(params)?;
                validate_times(params)?;
                validate_limit(params, Some(100))?;
                if params.get("orderId").is_some() && params.get("orderLinkId").is_some() {
                    return Err(DcexError::InvalidInput(
                        "orderId and orderLinkId are mutually exclusive".to_string(),
                    ));
                }
                self.get_request(
                    BYUSDT_ORDER,
                    query_with_coin(
                        params,
                        &[
                            "orderId",
                            "orderLinkId",
                            "orderType",
                            "startTime",
                            "endTime",
                            "limit",
                            "cursor",
                        ],
                    ),
                )
                .await
            }
            "get_byusdt_position" => {
                self.get_request(BYUSDT_POSITION, query_with_coin(params, &[]))
                    .await
            }
            "get_byusdt_daily_yield" | "get_byusdt_hourly_yield" => {
                validate_times(params)?;
                validate_limit(params, None)?;
                let path = if method_name == "get_byusdt_daily_yield" {
                    BYUSDT_DAILY_YIELD
                } else {
                    BYUSDT_HOURLY_YIELD
                };
                self.get_request(
                    path,
                    query_with_coin(params, &["startTime", "endTime", "limit", "cursor"]),
                )
                .await
            }
            "place_byusdt_order" => {
                let order_type = params.required("orderType")?;
                let account_type = params.required("accountType")?;
                match (order_type, account_type) {
                    ("Mint", "FlexibleSaving") | ("Redeem", "UNIFIED") => {}
                    _ => {
                        return Err(DcexError::InvalidInput(
                            "Mint requires FlexibleSaving; Redeem requires UNIFIED".to_string(),
                        ));
                    }
                }
                let amount = params.required("amount")?;
                if !amount.parse::<f64>().is_ok_and(|value| value > 0.0) {
                    return Err(DcexError::InvalidInput(
                        "amount must be a positive number".to_string(),
                    ));
                }
                let order_link_id = params.required("orderLinkId")?;
                if order_link_id.is_empty()
                    || order_link_id.len() > 36
                    || !order_link_id.chars().all(|character| {
                        character.is_ascii_alphanumeric() || matches!(character, '-' | '_')
                    })
                {
                    return Err(DcexError::InvalidInput(
                        "orderLinkId must contain 1 to 36 ASCII letters, numbers, '-' or '_'"
                            .to_string(),
                    ));
                }
                self.post_request(
                    BYUSDT_PLACE_ORDER,
                    string_body(&[
                        ("coin", COIN),
                        ("orderType", order_type),
                        ("accountType", account_type),
                        ("amount", amount),
                        ("orderLinkId", order_link_id),
                    ]),
                )
                .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}

fn query_with_coin(params: &BybitParams, keys: &[&str]) -> Vec<(String, String)> {
    let mut query = vec![("coin".to_string(), COIN.to_string())];
    query.extend(params.only(keys));
    query
}

fn validate_optional_order_type(params: &BybitParams) -> Result<()> {
    if let Some(value) = params.get("orderType") {
        if !matches!(value, "Mint" | "Redeem") {
            return Err(DcexError::InvalidInput(
                "orderType must be Mint or Redeem".to_string(),
            ));
        }
    }
    Ok(())
}

fn validate_times(params: &BybitParams) -> Result<()> {
    let parse = |key: &str| -> Result<Option<u64>> {
        params
            .get(key)
            .map(|value| {
                value
                    .parse::<u64>()
                    .map_err(|error| DcexError::InvalidInput(format!("invalid {key}: {error}")))
            })
            .transpose()
    };
    if let (Some(start), Some(end)) = (parse("startTime")?, parse("endTime")?) {
        if end < start {
            return Err(DcexError::InvalidInput(
                "endTime must not be earlier than startTime".to_string(),
            ));
        }
    }
    Ok(())
}

fn validate_limit(params: &BybitParams, maximum: Option<u16>) -> Result<()> {
    if let Some(limit) = params.get("limit") {
        let limit = limit
            .parse::<u16>()
            .map_err(|error| DcexError::InvalidInput(format!("invalid limit: {error}")))?;
        if limit == 0 || maximum.is_some_and(|maximum| limit > maximum) {
            return Err(DcexError::InvalidInput(
                "limit must be positive and within the endpoint maximum".to_string(),
            ));
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn byusdt_history_time_and_limit_are_checked() {
        let invalid_time = BybitParams::from_pairs(vec![
            ("startTime".to_string(), "2".to_string()),
            ("endTime".to_string(), "1".to_string()),
        ]);
        assert!(validate_times(&invalid_time).is_err());
        let invalid_limit = BybitParams::from_pairs(vec![("limit".to_string(), "101".to_string())]);
        assert!(validate_limit(&invalid_limit, Some(100)).is_err());
    }
}
