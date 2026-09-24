use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::BybitClient;
use super::endpoints::*;
use super::params::{insert_optional_bool, string_body, BybitParams};

const CATEGORIES: &[&str] = &["FixedTermSaving", "FundPool", "FundPoolPremium"];

impl BybitClient {
    pub(super) async fn fixed_earn_public_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        if method_name != "get_fixed_earn_products" {
            return Ok(None);
        }
        let response = self
            .request(
                HttpMethod::Get,
                FIXED_EARN_PRODUCT,
                params.only(&["coin"]),
                None,
                false,
            )
            .await?;
        Ok(Some(response))
    }

    pub(super) async fn fixed_earn_private_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_fixed_earn_positions" => {
                validate_optional_category(params)?;
                self.get_request(
                    FIXED_EARN_POSITION,
                    params.only(&["productId", "category", "coin"]),
                )
                .await
            }
            "get_fixed_earn_orders" => {
                validate_optional_category(params)?;
                if params.get("productId").is_some() && params.get("category").is_none() {
                    return Err(DcexError::InvalidInput(
                        "category is required when productId is provided".to_string(),
                    ));
                }
                if let Some(order_type) = params.get("orderType") {
                    validate_enum("orderType", order_type, &["Stake", "Redeem", "Reinvest"])?;
                }
                validate_history(params)?;
                self.get_request(
                    FIXED_EARN_ORDER,
                    params.only(&[
                        "orderType",
                        "productId",
                        "category",
                        "orderId",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
                    ]),
                )
                .await
            }
            "place_fixed_earn_order" => {
                let category = params.required("category")?;
                validate_enum("category", category, CATEGORIES)?;
                let amount = params.required("amount")?;
                positive_amount(amount)?;
                validate_account_type(params.required("accountType")?)?;
                validate_order_link_id(params.required("orderLinkId")?)?;
                let mut body = string_body(&[
                    ("productId", params.required("productId")?),
                    ("category", category),
                    ("coin", params.required("coin")?),
                    ("amount", amount),
                    ("accountType", params.required("accountType")?),
                    ("orderLinkId", params.required("orderLinkId")?),
                ]);
                if category != "FundPool" && params.get("autoInvest").is_some() {
                    return Err(DcexError::InvalidInput(
                        "autoInvest is only available for FundPool".to_string(),
                    ));
                }
                insert_optional_bool(&mut body, "autoInvest", params.get("autoInvest"))?;
                self.post_request(FIXED_EARN_PLACE_ORDER, body).await
            }
            "redeem_fixed_earn" => {
                if params.required("category")? != "FundPool" {
                    return Err(DcexError::InvalidInput(
                        "early redemption is only available for FundPool".to_string(),
                    ));
                }
                self.post_request(
                    FIXED_EARN_REDEEM,
                    string_body(&[
                        ("productId", params.required("productId")?),
                        ("category", "FundPool"),
                        ("positionId", params.required("positionId")?),
                    ]),
                )
                .await
            }
            "set_fixed_earn_auto_invest" => {
                let category = params.required("category")?;
                validate_enum("category", category, CATEGORIES)?;
                let status = params.required("status")?;
                validate_enum("status", status, &["Enable", "Disable"])?;
                self.post_request(
                    FIXED_EARN_AUTO_INVEST,
                    string_body(&[
                        ("productId", params.required("productId")?),
                        ("category", category),
                        ("positionId", params.required("positionId")?),
                        ("status", status),
                    ]),
                )
                .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}

fn validate_optional_category(params: &BybitParams) -> Result<()> {
    if let Some(category) = params.get("category") {
        validate_enum("category", category, CATEGORIES)?;
    }
    Ok(())
}

fn validate_enum(key: &str, value: &str, allowed: &[&str]) -> Result<()> {
    if allowed.contains(&value) {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(format!(
            "{key} must be one of {}",
            allowed.join(", ")
        )))
    }
}

fn validate_account_type(value: &str) -> Result<()> {
    validate_enum("accountType", value, &["FUND", "UNIFIED"])
}

fn positive_amount(value: &str) -> Result<()> {
    if value.parse::<f64>().is_ok_and(|amount| amount > 0.0) {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(
            "amount must be a positive number".to_string(),
        ))
    }
}

fn validate_order_link_id(value: &str) -> Result<()> {
    if value.is_empty()
        || value.len() > 36
        || !value
            .chars()
            .all(|character| character.is_ascii_alphanumeric() || matches!(character, '-' | '_'))
    {
        return Err(DcexError::InvalidInput(
            "orderLinkId must contain 1 to 36 ASCII letters, numbers, '-' or '_'".to_string(),
        ));
    }
    Ok(())
}

fn validate_history(params: &BybitParams) -> Result<()> {
    if let Some(limit) = params.get("limit") {
        if !limit
            .parse::<u16>()
            .is_ok_and(|value| (1..=50).contains(&value))
        {
            return Err(DcexError::InvalidInput(
                "limit must be between 1 and 50".to_string(),
            ));
        }
    }
    if let (Some(start), Some(end)) = (params.get("startTime"), params.get("endTime")) {
        let start = start
            .parse::<u64>()
            .map_err(|error| DcexError::InvalidInput(format!("invalid startTime: {error}")))?;
        let end = end
            .parse::<u64>()
            .map_err(|error| DcexError::InvalidInput(format!("invalid endTime: {error}")))?;
        if end < start {
            return Err(DcexError::InvalidInput(
                "endTime must not be earlier than startTime".to_string(),
            ));
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn fixed_earn_category_and_history_are_bounded() {
        assert!(validate_enum("category", "FundPool", CATEGORIES).is_ok());
        assert!(validate_enum("category", "FlexibleSaving", CATEGORIES).is_err());
        let params = BybitParams::from_pairs(vec![("limit".to_string(), "51".to_string())]);
        assert!(validate_history(&params).is_err());
    }
}
