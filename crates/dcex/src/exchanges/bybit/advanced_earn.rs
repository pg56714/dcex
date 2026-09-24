use serde_json::{Map, Value};

use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::BybitClient;
use super::endpoints::*;
use super::params::{insert_optional_string, string_body, BybitParams};

const CATEGORIES: &[&str] = &["DualAssets", "SmartLeverage", "DoubleWin", "DiscountBuy"];
const EXTRA_FIELDS: &[&str] = &[
    "dualAssetsExtra",
    "smartLeverageStakeExtra",
    "smartLeverageRedeemExtra",
    "doubleWinStakeExtra",
    "doubleWinRedeemExtra",
    "discountBuyExtra",
    "interestCard",
];

impl BybitClient {
    pub(super) async fn advanced_earn_public_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_advanced_earn_products" => {
                validate_category(params.required("category")?)?;
                self.request(
                    HttpMethod::Get,
                    ADVANCED_EARN_PRODUCT,
                    params.only(&["category", "coin", "duration"]),
                    None,
                    false,
                )
                .await
            }
            "get_advanced_earn_product_quote" => {
                validate_category(params.required("category")?)?;
                params.required("productId")?;
                self.request(
                    HttpMethod::Get,
                    ADVANCED_EARN_PRODUCT_QUOTE,
                    params.only(&["category", "productId"]),
                    None,
                    false,
                )
                .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }

    pub(super) async fn advanced_earn_private_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "place_advanced_earn_order" => {
                self.post_request(ADVANCED_EARN_PLACE_ORDER, advanced_order_body(params)?)
                    .await
            }
            "get_advanced_earn_positions" => {
                validate_category(params.required("category")?)?;
                validate_limit(params, 20)?;
                self.get_request(
                    ADVANCED_EARN_POSITION,
                    params.only(&["category", "productId", "coin", "limit", "cursor"]),
                )
                .await
            }
            "get_advanced_earn_orders" => {
                validate_category(params.required("category")?)?;
                validate_limit(params, 20)?;
                validate_ordered_time_range(params)?;
                self.get_request(
                    ADVANCED_EARN_ORDER,
                    params.only(&[
                        "category",
                        "productId",
                        "orderId",
                        "orderLinkId",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
                    ]),
                )
                .await
            }
            "get_advanced_earn_redeem_estimates" => {
                let category = params.required("category")?;
                validate_enum("category", category, &["SmartLeverage", "DoubleWin"])?;
                let position_ids = params.required("positionIds")?;
                let count = position_ids
                    .split(',')
                    .filter(|value| !value.trim().is_empty())
                    .count();
                if !(1..=5).contains(&count) {
                    return Err(DcexError::InvalidInput(
                        "positionIds must contain between 1 and 5 comma-separated IDs".to_string(),
                    ));
                }
                self.get_request(
                    ADVANCED_EARN_REDEEM_ESTIMATE,
                    params.only(&["category", "positionIds"]),
                )
                .await
            }
            "get_double_win_leverage" => {
                for key in ["productId", "initialPrice", "lowerPrice", "upperPrice"] {
                    params.required(key)?;
                }
                self.get_request(
                    DOUBLE_WIN_LEVERAGE,
                    params.only(&["productId", "initialPrice", "lowerPrice", "upperPrice"]),
                )
                .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}

fn advanced_order_body(params: &BybitParams) -> Result<Map<String, Value>> {
    let category = params.required("category")?;
    validate_category(category)?;
    let order_type = params.required("orderType")?;
    validate_enum("orderType", order_type, &["Stake", "Redeem"])?;
    let account_type = params.required("accountType")?;
    validate_enum("accountType", account_type, &["FUND", "UNIFIED"])?;
    let order_link_id = params.required("orderLinkId")?;
    validate_order_link_id(category, order_link_id)?;

    let required_extra = match (category, order_type) {
        ("DualAssets", "Stake") => "dualAssetsExtra",
        ("SmartLeverage", "Stake") => "smartLeverageStakeExtra",
        ("SmartLeverage", "Redeem") => "smartLeverageRedeemExtra",
        ("DoubleWin", "Stake") => "doubleWinStakeExtra",
        ("DoubleWin", "Redeem") => "doubleWinRedeemExtra",
        ("DiscountBuy", "Stake") => "discountBuyExtra",
        ("DualAssets" | "DiscountBuy", "Redeem") => {
            return Err(DcexError::InvalidInput(format!(
                "{category} does not support Redeem orders"
            )));
        }
        _ => unreachable!(),
    };
    let extra = required_json_object(params, required_extra)?;

    if order_type == "Stake" {
        params.required("amount")?;
        params.required("coin")?;
        validate_positive_amount(params.required("amount")?)?;
    }

    let mut body = string_body(&[
        ("category", category),
        ("productId", params.required("productId")?),
        ("orderType", order_type),
        ("accountType", account_type),
        ("orderLinkId", order_link_id),
    ]);
    insert_optional_string(&mut body, "amount", params.get("amount"));
    insert_optional_string(&mut body, "coin", params.get("coin"));
    body.insert(required_extra.to_string(), extra);

    for key in EXTRA_FIELDS {
        if *key == required_extra || params.get(key).is_none() {
            continue;
        }
        if *key == "interestCard" && category == "DualAssets" && order_type == "Stake" {
            body.insert(key.to_string(), required_json_object(params, key)?);
            continue;
        }
        return Err(DcexError::InvalidInput(format!(
            "{key} is not valid for {category} {order_type}"
        )));
    }
    Ok(body)
}

fn required_json_object(params: &BybitParams, key: &str) -> Result<Value> {
    let value = params.json_required(key)?;
    if !value.is_object() {
        return Err(DcexError::InvalidInput(format!(
            "{key} must be a JSON object"
        )));
    }
    Ok(value)
}

fn validate_category(value: &str) -> Result<()> {
    validate_enum("category", value, CATEGORIES)
}

fn validate_enum(key: &str, value: &str, values: &[&str]) -> Result<()> {
    if values.contains(&value) {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(format!(
            "{key} must be one of {}",
            values.join(", ")
        )))
    }
}

fn validate_order_link_id(category: &str, value: &str) -> Result<()> {
    let maximum = match category {
        "DualAssets" | "SmartLeverage" => 36,
        "DoubleWin" => 64,
        "DiscountBuy" => 40,
        _ => unreachable!(),
    };
    if value.is_empty()
        || value.len() > maximum
        || !value
            .chars()
            .all(|character| character.is_ascii_alphanumeric() || matches!(character, '-' | '_'))
    {
        return Err(DcexError::InvalidInput(format!(
            "orderLinkId for {category} must contain 1 to {maximum} ASCII letters, numbers, '-' or '_'"
        )));
    }
    Ok(())
}

fn validate_positive_amount(value: &str) -> Result<()> {
    if value.parse::<f64>().is_ok_and(|amount| amount > 0.0) {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(
            "amount must be a positive number".to_string(),
        ))
    }
}

fn validate_limit(params: &BybitParams, maximum: u16) -> Result<()> {
    if let Some(value) = params.get("limit") {
        let value = value.parse::<u16>().map_err(|error| {
            DcexError::InvalidInput(format!("invalid integer parameter limit: {error}"))
        })?;
        if !(1..=maximum).contains(&value) {
            return Err(DcexError::InvalidInput(format!(
                "limit must be between 1 and {maximum}"
            )));
        }
    }
    Ok(())
}

fn validate_ordered_time_range(params: &BybitParams) -> Result<()> {
    if let (Some(start), Some(end)) = (params.get("startTime"), params.get("endTime")) {
        let start = start.parse::<u64>().map_err(|error| {
            DcexError::InvalidInput(format!("invalid integer parameter startTime: {error}"))
        })?;
        let end = end.parse::<u64>().map_err(|error| {
            DcexError::InvalidInput(format!("invalid integer parameter endTime: {error}"))
        })?;
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

    fn params(values: &[(&str, &str)]) -> BybitParams {
        BybitParams::from_pairs(
            values
                .iter()
                .map(|(key, value)| (key.to_string(), value.to_string()))
                .collect(),
        )
    }

    #[test]
    fn smart_leverage_stake_requires_the_matching_extra_object() {
        let missing = params(&[
            ("category", "SmartLeverage"),
            ("productId", "1"),
            ("orderType", "Stake"),
            ("accountType", "FUND"),
            ("orderLinkId", "smart-1"),
            ("amount", "10"),
            ("coin", "USDT"),
        ]);
        assert!(advanced_order_body(&missing).is_err());

        let valid = params(&[
            ("category", "SmartLeverage"),
            ("productId", "1"),
            ("orderType", "Stake"),
            ("accountType", "FUND"),
            ("orderLinkId", "smart-1"),
            ("amount", "10"),
            ("coin", "USDT"),
            (
                "smartLeverageStakeExtra",
                "{\"initialPrice\":\"1\",\"breakevenPrice\":\"2\"}",
            ),
        ]);
        assert!(advanced_order_body(&valid).is_ok());
    }

    #[test]
    fn discount_buy_rejects_redeem() {
        let value = params(&[
            ("category", "DiscountBuy"),
            ("productId", "1"),
            ("orderType", "Redeem"),
            ("accountType", "FUND"),
            ("orderLinkId", "discount-1"),
        ]);
        assert!(advanced_order_body(&value).is_err());
    }

    #[test]
    fn category_specific_link_id_lengths_are_enforced() {
        assert!(validate_order_link_id("DualAssets", &"a".repeat(36)).is_ok());
        assert!(validate_order_link_id("DualAssets", &"a".repeat(37)).is_err());
        assert!(validate_order_link_id("DoubleWin", &"a".repeat(64)).is_ok());
    }
}
