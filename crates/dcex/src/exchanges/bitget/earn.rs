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
            "get_earn_account_assets" => {
                self.get_private(EARN_ACCOUNT_ASSETS, params.only(&["coin"]))
                    .await
            }
            "get_savings_account" => self.get_private(SAVINGS_ACCOUNT, Vec::new()).await,
            "get_savings_products" => {
                if let Some(filter) = params.get("filter") {
                    if !["available", "held", "available_and_held", "all"].contains(&filter) {
                        return Err(DcexError::InvalidInput(
                            "filter must be available, held, available_and_held, or all"
                                .to_string(),
                        ));
                    }
                }
                self.get_private(SAVINGS_PRODUCTS, params.only(&["coin", "filter"]))
                    .await
            }
            "get_savings_assets" => {
                validate_period_type(params)?;
                validate_page(params)?;
                self.get_private(
                    SAVINGS_ASSETS,
                    params.only(&["periodType", "startTime", "endTime", "limit", "idLessThan"]),
                )
                .await
            }
            "get_savings_records" => {
                validate_period_type(params)?;
                validate_page(params)?;
                if let Some(order_type) = params.get("orderType") {
                    if !["subscribe", "redeem", "pay_interest", "deduction"].contains(&order_type) {
                        return Err(DcexError::InvalidInput(
                            "orderType must be subscribe, redeem, pay_interest, or deduction"
                                .to_string(),
                        ));
                    }
                }
                self.get_private(
                    SAVINGS_RECORDS,
                    params.only(&[
                        "coin",
                        "periodType",
                        "orderType",
                        "startTime",
                        "endTime",
                        "limit",
                        "idLessThan",
                    ]),
                )
                .await
            }
            "get_savings_subscription_info" => {
                params.required("productId")?;
                validate_period_type(params)?;
                self.get_private(
                    SAVINGS_SUBSCRIBE_INFO,
                    params.only(&["productId", "periodType"]),
                )
                .await
            }
            "subscribe_savings" => {
                require_savings_amount(params)?;
                self.post_private(
                    SAVINGS_SUBSCRIBE,
                    Value::Object(params.body(&["productId", "periodType", "amount"])),
                )
                .await
            }
            "get_savings_subscription_result" => {
                params.required("orderId")?;
                validate_period_type(params)?;
                self.get_private(
                    SAVINGS_SUBSCRIBE_RESULT,
                    params.only(&["orderId", "periodType"]),
                )
                .await
            }
            "redeem_savings" => {
                require_savings_amount(params)?;
                self.post_private(
                    SAVINGS_REDEEM,
                    Value::Object(params.body(&["productId", "orderId", "periodType", "amount"])),
                )
                .await
            }
            "get_savings_redemption_result" => {
                params.required("orderId")?;
                validate_period_type(params)?;
                self.get_private(
                    SAVINGS_REDEEM_RESULT,
                    params.only(&["orderId", "periodType"]),
                )
                .await
            }
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
    if let Some(value) = params.get(key) {
        if !["spot", "unified"].contains(&value) {
            return Err(DcexError::InvalidInput(format!(
                "{key} must be spot or unified"
            )));
        }
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
    if let Some(value) = params.get("advancedSettle") {
        if !["yes", "no"].contains(&value) {
            return Err(DcexError::InvalidInput(
                "advancedSettle must be yes or no".to_string(),
            ));
        }
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

fn validate_period_type(params: &BitgetParams) -> Result<()> {
    let value = params.required("periodType")?;
    if ["flexible", "fixed"].contains(&value) {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(
            "periodType must be flexible or fixed".to_string(),
        ))
    }
}

fn require_savings_amount(params: &BitgetParams) -> Result<()> {
    params.required("productId")?;
    validate_period_type(params)?;
    let amount = params.required("amount")?;
    if amount.parse::<f64>().is_ok_and(|value| value > 0.0) {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(
            "amount must be a positive number".to_string(),
        ))
    }
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
    fn savings_mutations_require_positive_amounts() {
        let params = BitgetParams::from_pairs(vec![
            ("productId".to_string(), "product".to_string()),
            ("periodType".to_string(), "flexible".to_string()),
            ("amount".to_string(), "0".to_string()),
        ]);
        assert!(require_savings_amount(&params).is_err());
    }

    #[test]
    fn savings_period_type_is_constrained() {
        let params =
            BitgetParams::from_pairs(vec![("periodType".to_string(), "weekly".to_string())]);
        assert!(validate_period_type(&params).is_err());
    }

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
