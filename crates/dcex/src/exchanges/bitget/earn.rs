use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::BitgetClient;
use super::endpoints::*;
use super::params::BitgetParams;

impl BitgetClient {
    pub(super) async fn earn_private_request(
        &self,
        method_name: &str,
        params: &BitgetParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_elite_earn_products" => self.get_private(ELITE_EARN_PRODUCTS, Vec::new()).await,
            "get_elite_earn_subscription_info" => {
                params.required("productId")?;
                self.get_private(ELITE_EARN_SUBSCRIBE_INFO, params.only(&["productId"]))
                    .await
            }
            "subscribe_elite_earn" => {
                validate_elite_subscription(params)?;
                self.post_private(
                    ELITE_EARN_SUBSCRIBE,
                    Value::Object(params.body(&[
                        "productSubId",
                        "amount",
                        "coin",
                        "paymentAccount",
                    ])),
                )
                .await
            }
            "get_elite_earn_subscription_result" => {
                params.required("orderId")?;
                self.get_private(ELITE_EARN_SUBSCRIBE_RESULT, params.only(&["orderId"]))
                    .await
            }
            "get_elite_earn_redemption_info" => {
                params.required("productId")?;
                self.get_private(ELITE_EARN_REDEEM_INFO, params.only(&["productId"]))
                    .await
            }
            "redeem_elite_earn" => {
                validate_elite_redemption(params)?;
                self.post_private(
                    ELITE_EARN_REDEEM,
                    Value::Object(params.body(&[
                        "productId",
                        "productSubId",
                        "redeemType",
                        "amount",
                        "receiveAccount",
                        "advancedSettle",
                        "coin",
                    ])),
                )
                .await
            }
            "get_elite_earn_assets" => self.get_private(ELITE_EARN_ASSETS, Vec::new()).await,
            "get_elite_earn_records" => {
                validate_elite_records(params)?;
                self.get_private(
                    ELITE_EARN_RECORDS,
                    params.only(&["type", "startTime", "endTime", "limit", "cursor"]),
                )
                .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}

fn validate_positive_amount(params: &BitgetParams) -> Result<()> {
    let amount = params.required("amount")?;
    if amount.parse::<f64>().is_ok_and(|value| value > 0.0) {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(
            "amount must be a positive number".to_string(),
        ))
    }
}

fn validate_account(params: &BitgetParams, key: &str) -> Result<()> {
    if let Some(value) = params.get(key)
        && !["spot", "unified"].contains(&value)
    {
        return Err(DcexError::InvalidInput(format!(
            "{key} must be spot or unified"
        )));
    }
    Ok(())
}

fn validate_elite_subscription(params: &BitgetParams) -> Result<()> {
    params.required("productSubId")?;
    validate_positive_amount(params)?;
    validate_account(params, "paymentAccount")
}

fn validate_elite_redemption(params: &BitgetParams) -> Result<()> {
    params.required("productId")?;
    params.required("productSubId")?;
    validate_positive_amount(params)?;
    let redeem_type = params.required("redeemType")?;
    if !["fast", "standard"].contains(&redeem_type) {
        return Err(DcexError::InvalidInput(
            "redeemType must be fast or standard".to_string(),
        ));
    }
    params.required("receiveAccount")?;
    validate_account(params, "receiveAccount")?;
    if let Some(value) = params.get("advancedSettle")
        && !["yes", "no"].contains(&value)
    {
        return Err(DcexError::InvalidInput(
            "advancedSettle must be yes or no".to_string(),
        ));
    }
    Ok(())
}

fn validate_elite_records(params: &BitgetParams) -> Result<()> {
    let record_type = params.required("type")?;
    if !["subscribe", "redeem", "interest"].contains(&record_type) {
        return Err(DcexError::InvalidInput(
            "type must be subscribe, redeem, or interest".to_string(),
        ));
    }
    validate_page(params)
}

fn validate_page(params: &BitgetParams) -> Result<()> {
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
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn elite_subscription_requires_positive_amount() {
        let params = BitgetParams::from_pairs(vec![
            ("productSubId".to_string(), "product-sub".to_string()),
            ("amount".to_string(), "-1".to_string()),
        ]);
        assert!(validate_elite_subscription(&params).is_err());
    }

    #[test]
    fn elite_redemption_constrains_accounts_and_types() {
        let params = BitgetParams::from_pairs(vec![
            ("productId".to_string(), "product".to_string()),
            ("productSubId".to_string(), "product-sub".to_string()),
            ("redeemType".to_string(), "instant".to_string()),
            ("amount".to_string(), "1".to_string()),
            ("receiveAccount".to_string(), "funding".to_string()),
        ]);
        assert!(validate_elite_redemption(&params).is_err());
    }
}
