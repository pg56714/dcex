use serde_json::{Map, Value};

use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::BybitClient;
use super::endpoints::*;
use super::params::{insert_optional_string, BybitParams};

const EARN_CATEGORIES: &[&str] = &["FlexibleSaving", "OnChain"];

impl BybitClient {
    pub(super) async fn earn_public_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let path = match method_name {
            "get_earn_products" => EARN_PRODUCT,
            "get_earn_apr_history" => {
                params.required("productId")?;
                validate_apr_times(params)?;
                EARN_APR_HISTORY
            }
            _ => return Ok(None),
        };
        validate_category(params)?;
        let keys: &[&str] = if path == EARN_PRODUCT {
            &["category", "coin"]
        } else {
            &["category", "productId", "startTime", "endTime"]
        };
        let result = self
            .request(HttpMethod::Get, path, params.only(keys), None, false)
            .await?;
        Ok(Some(result))
    }

    pub(super) async fn earn_private_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_earn_coupons" => {
                validate_enum(params, "category", &["FlexibleSaving", "DualAssets"])?;
                self.get_request(EARN_COUPONS, params.only(&["category"]))
                    .await
            }
            "set_earn_auto_reinvest" => {
                validate_enum(params, "category", &["OnChain"])?;
                let product_id = positive_id(params, "productId")?;
                let position_id = positive_id(params, "positionId")?;
                let auto_reinvest = params.i64_required("autoReinvest")?;
                if !matches!(auto_reinvest, 0 | 1) {
                    return Err(DcexError::InvalidInput(
                        "autoReinvest must be 0 or 1".to_string(),
                    ));
                }
                let mut body = Map::new();
                body.insert("category".to_string(), Value::String("OnChain".to_string()));
                body.insert("productId".to_string(), Value::from(product_id));
                body.insert("positionId".to_string(), Value::from(position_id));
                body.insert("autoReinvest".to_string(), Value::from(auto_reinvest));
                self.post_request(EARN_POSITION_MODIFY, body).await
            }
            "place_earn_order" => {
                validate_category(params)?;
                validate_enum(params, "orderType", &["Stake", "Redeem"])?;
                validate_enum(params, "accountType", &["FUND", "UNIFIED"])?;
                for key in ["amount", "coin", "productId", "orderLinkId"] {
                    params.required(key)?;
                }
                let amount = params.required("amount")?;
                if !amount.parse::<f64>().is_ok_and(|value| value > 0.0) {
                    return Err(DcexError::InvalidInput(
                        "amount must be a positive number".to_string(),
                    ));
                }
                if params.required("orderLinkId")?.len() > 36 {
                    return Err(DcexError::InvalidInput(
                        "orderLinkId must not exceed 36 characters".to_string(),
                    ));
                }
                let mut body = Map::new();
                for key in [
                    "category",
                    "orderType",
                    "accountType",
                    "amount",
                    "coin",
                    "productId",
                    "orderLinkId",
                ] {
                    body.insert(
                        key.to_string(),
                        Value::String(params.required(key)?.to_string()),
                    );
                }
                insert_optional_string(
                    &mut body,
                    "redeemPositionId",
                    params.get("redeemPositionId"),
                );
                insert_optional_string(&mut body, "toAccountType", params.get("toAccountType"));
                if let Some(value) = params.get("interestCard") {
                    body.insert(
                        "interestCard".to_string(),
                        serde_json::from_str(value).map_err(|error| {
                            DcexError::InvalidInput(format!(
                                "invalid JSON parameter interestCard: {error}"
                            ))
                        })?,
                    );
                }
                self.post_request(EARN_PLACE_ORDER, body).await
            }
            "get_earn_order_history" => {
                validate_category(params)?;
                if params.get("category") == Some("OnChain")
                    && params.get("orderId").is_none()
                    && params.get("orderLinkId").is_none()
                {
                    return Err(DcexError::InvalidInput(
                        "orderId or orderLinkId is required for OnChain order history".to_string(),
                    ));
                }
                validate_history(params)?;
                self.get_request(
                    EARN_ORDER_HISTORY,
                    params.only(&[
                        "category",
                        "orderId",
                        "orderLinkId",
                        "productId",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
                    ]),
                )
                .await
            }
            "get_earn_positions" => {
                validate_category(params)?;
                self.get_request(
                    EARN_POSITION,
                    params.only(&["category", "productId", "coin"]),
                )
                .await
            }
            "get_earn_yield_history" => {
                validate_category(params)?;
                if params.get("category") == Some("OnChain") && params.get("productId").is_some() {
                    return Err(DcexError::InvalidInput(
                        "productId is not supported for OnChain yield history".to_string(),
                    ));
                }
                validate_history(params)?;
                self.get_request(
                    EARN_YIELD_HISTORY,
                    params.only(&[
                        "category",
                        "productId",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
                    ]),
                )
                .await
            }
            "get_earn_hourly_yield_history" => {
                validate_enum(params, "category", &["FlexibleSaving"])?;
                validate_history(params)?;
                self.get_request(
                    EARN_HOURLY_YIELD,
                    params.only(&[
                        "category",
                        "productId",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
                    ]),
                )
                .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}

fn validate_category(params: &BybitParams) -> Result<()> {
    validate_enum(params, "category", EARN_CATEGORIES)
}

fn validate_enum(params: &BybitParams, key: &str, values: &[&str]) -> Result<()> {
    let value = params.required(key)?;
    if values.contains(&value) {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(format!(
            "{key} must be one of {}",
            values.join(", ")
        )))
    }
}

fn validate_history(params: &BybitParams) -> Result<()> {
    if let Some(limit) = params.get("limit") {
        let limit = limit.parse::<u16>().map_err(|error| {
            DcexError::InvalidInput(format!("invalid integer parameter limit: {error}"))
        })?;
        if !(1..=100).contains(&limit) {
            return Err(DcexError::InvalidInput(
                "limit must be between 1 and 100".to_string(),
            ));
        }
    }
    if let (Some(start), Some(end)) = (params.get("startTime"), params.get("endTime")) {
        let start = start.parse::<u64>().map_err(|error| {
            DcexError::InvalidInput(format!("invalid integer parameter startTime: {error}"))
        })?;
        let end = end.parse::<u64>().map_err(|error| {
            DcexError::InvalidInput(format!("invalid integer parameter endTime: {error}"))
        })?;
        const SEVEN_DAYS_MS: u64 = 7 * 24 * 60 * 60 * 1_000;
        if end < start || end - start > SEVEN_DAYS_MS {
            return Err(DcexError::InvalidInput(
                "startTime and endTime must define a range no longer than 7 days".to_string(),
            ));
        }
    }
    Ok(())
}

fn positive_id(params: &BybitParams, key: &str) -> Result<i64> {
    let value = params.i64_required(key)?;
    if value <= 0 {
        return Err(DcexError::InvalidInput(format!("{key} must be positive")));
    }
    Ok(value)
}

fn validate_apr_times(params: &BybitParams) -> Result<()> {
    let parse = |key: &str| -> Result<Option<u64>> {
        params
            .get(key)
            .map(|value| {
                value.parse::<u64>().map_err(|error| {
                    DcexError::InvalidInput(format!("invalid integer parameter {key}: {error}"))
                })
            })
            .transpose()
    };
    if let (Some(start), Some(end)) = (parse("startTime")?, parse("endTime")?) {
        const MAX_APR_RANGE_MS: u64 = 182 * 24 * 60 * 60 * 1_000;
        if end < start || end - start > MAX_APR_RANGE_MS {
            return Err(DcexError::InvalidInput(
                "APR history range must be ordered and no longer than 182 days".to_string(),
            ));
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn history_rejects_ranges_over_seven_days() {
        let params = BybitParams::from_pairs(vec![
            ("startTime".to_string(), "0".to_string()),
            ("endTime".to_string(), "604800001".to_string()),
        ]);
        assert!(validate_history(&params).is_err());
    }

    #[test]
    fn category_is_limited_to_supported_easy_earn_products() {
        let params =
            BybitParams::from_pairs(vec![("category".to_string(), "FixedSaving".to_string())]);
        assert!(validate_category(&params).is_err());
    }

    #[test]
    fn apr_history_rejects_ranges_over_182_days() {
        let params = BybitParams::from_pairs(vec![
            ("startTime".to_string(), "0".to_string()),
            ("endTime".to_string(), "15724800001".to_string()),
        ]);
        assert!(validate_apr_times(&params).is_err());
    }
}
