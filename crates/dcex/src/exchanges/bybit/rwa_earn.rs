use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::BybitClient;
use super::endpoints::*;
use super::params::{string_body, BybitParams};

impl BybitClient {
    pub(super) async fn rwa_earn_public_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, query) = match method_name {
            "get_rwa_earn_products" => (RWA_EARN_PRODUCT, params.only(&["coin"])),
            "get_rwa_earn_nav_chart" => {
                positive_product_id(params.required("productId")?)?;
                validate_times(params, 180)?;
                (
                    RWA_EARN_NAV_CHART,
                    params.only(&["productId", "startTime", "endTime"]),
                )
            }
            _ => return Ok(None),
        };
        Ok(Some(
            self.request(HttpMethod::Get, path, query, None, false)
                .await?,
        ))
    }

    pub(super) async fn rwa_earn_private_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_rwa_earn_positions" => self.get_request(RWA_EARN_POSITION, vec![]).await,
            "get_rwa_earn_orders" => {
                if let Some(order_type) = params.get("orderType") {
                    validate_order_type(order_type)?;
                }
                if let Some(product_id) = params.get("productId") {
                    positive_product_id(product_id)?;
                }
                if params.get("orderId").is_none() && params.get("orderLinkId").is_none() {
                    validate_times(params, 180)?;
                    if let Some(limit) = params.get("limit") {
                        let limit = limit.parse::<u8>().map_err(|error| {
                            DcexError::InvalidInput(format!("invalid limit: {error}"))
                        })?;
                        if !(1..=50).contains(&limit) {
                            return Err(DcexError::InvalidInput(
                                "limit must be between 1 and 50".to_string(),
                            ));
                        }
                    }
                }
                self.get_request(
                    RWA_EARN_ORDER,
                    params.only(&[
                        "orderId",
                        "orderLinkId",
                        "orderType",
                        "productId",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
                    ]),
                )
                .await
            }
            "place_rwa_earn_order" => {
                let product_id = positive_product_id(params.required("productId")?)?;
                let order_type = params.required("orderType")?;
                validate_order_type(order_type)?;
                let coin = params.required("coin")?;
                if coin.is_empty() || !coin.chars().all(|c| c.is_ascii_uppercase()) {
                    return Err(DcexError::InvalidInput(
                        "coin must contain uppercase ASCII letters".to_string(),
                    ));
                }
                let link_id = params.required("orderLinkId")?;
                if link_id.is_empty()
                    || link_id.len() > 36
                    || !link_id
                        .chars()
                        .all(|c| c.is_ascii_alphanumeric() || matches!(c, '-' | '_'))
                {
                    return Err(DcexError::InvalidInput(
                        "orderLinkId must contain 1 to 36 ASCII letters, numbers, '-' or '_'"
                            .to_string(),
                    ));
                }
                let amount_key = if order_type == "Stake" {
                    "stakeAmount"
                } else {
                    "redeemShares"
                };
                let amount = params.required(amount_key)?;
                if !amount.parse::<f64>().is_ok_and(|value| value > 0.0) {
                    return Err(DcexError::InvalidInput(format!(
                        "{amount_key} must be a positive number"
                    )));
                }
                let account_type = params.get("accountType").unwrap_or("FUND");
                if !matches!(account_type, "FUND" | "UNIFIED") {
                    return Err(DcexError::InvalidInput(
                        "accountType must be FUND or UNIFIED".to_string(),
                    ));
                }
                let mut body = string_body(&[
                    ("orderType", order_type),
                    ("coin", coin),
                    ("orderLinkId", link_id),
                    (amount_key, amount),
                    ("accountType", account_type),
                ]);
                body.insert("productId".to_string(), Value::from(product_id));
                self.post_request(RWA_EARN_PLACE_ORDER, body).await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}

fn positive_product_id(value: &str) -> Result<u64> {
    let product_id = value
        .parse::<u64>()
        .map_err(|error| DcexError::InvalidInput(format!("invalid productId: {error}")))?;
    if product_id == 0 {
        return Err(DcexError::InvalidInput(
            "productId must be positive".to_string(),
        ));
    }
    Ok(product_id)
}

fn validate_order_type(value: &str) -> Result<()> {
    if !matches!(value, "Stake" | "Redeem") {
        return Err(DcexError::InvalidInput(
            "orderType must be Stake or Redeem".to_string(),
        ));
    }
    Ok(())
}

fn validate_times(params: &BybitParams, max_span_days: u64) -> Result<()> {
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
        if end < start || end - start > max_span_days * 24 * 60 * 60 {
            return Err(DcexError::InvalidInput(format!(
                "time range must be ordered and no more than {max_span_days} days"
            )));
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn rwa_earn_parameters_are_validated() {
        assert!(positive_product_id("1").is_ok());
        assert!(positive_product_id("0").is_err());
        assert!(validate_order_type("Stake").is_ok());
        assert!(validate_order_type("Mint").is_err());
        let invalid_time = BybitParams::from_pairs(vec![
            ("startTime".to_string(), "2".to_string()),
            ("endTime".to_string(), "1".to_string()),
        ]);
        assert!(validate_times(&invalid_time, 180).is_err());
    }
}
