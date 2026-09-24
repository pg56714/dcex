use serde_json::{Map, Value};

use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::{DcexError, Result};

use super::client::BybitClient;
use super::endpoints::*;
use super::params::{insert_optional_i64, insert_optional_string, string_body, BybitParams};

impl BybitClient {
    pub(super) async fn liquidity_mining_public_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        if method_name != "get_liquidity_mining_products" {
            return Ok(None);
        }
        let result = self
            .request(
                HttpMethod::Get,
                LIQUIDITY_MINING_PRODUCT,
                params.only(&["baseCoin", "quoteCoin"]),
                None,
                false,
            )
            .await?;
        Ok(Some(result))
    }

    pub(super) async fn liquidity_mining_private_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_liquidity_mining_positions" => {
                self.get_request(
                    LIQUIDITY_MINING_POSITION,
                    params.only(&["productId", "baseCoin"]),
                )
                .await
            }
            "get_liquidity_mining_orders" => {
                validate_history(params)?;
                if params.get("orderId").is_some() && params.get("orderLinkId").is_some() {
                    return Err(DcexError::InvalidInput(
                        "orderId and orderLinkId are mutually exclusive".to_string(),
                    ));
                }
                validate_optional_enum(
                    params,
                    "orderType",
                    &["AddLiquidity", "RemoveLiquidity", "Reinvest", "AddMargin"],
                )?;
                validate_optional_enum(params, "status", &["Success", "Processing"])?;
                self.get_request(
                    LIQUIDITY_MINING_ORDER,
                    params.only(&[
                        "orderId",
                        "orderLinkId",
                        "productId",
                        "orderType",
                        "startTime",
                        "endTime",
                        "status",
                        "limit",
                        "cursor",
                    ]),
                )
                .await
            }
            "get_liquidity_mining_yield_records" => {
                validate_history(params)?;
                self.get_request(
                    LIQUIDITY_MINING_YIELD_RECORDS,
                    params.only(&[
                        "baseCoin",
                        "quoteCoin",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
                    ]),
                )
                .await
            }
            "get_liquidity_mining_liquidation_records" => {
                validate_history(params)?;
                self.get_request(
                    LIQUIDITY_MINING_LIQUIDATION_RECORDS,
                    params.only(&[
                        "baseCoin",
                        "quoteCoin",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
                    ]),
                )
                .await
            }
            "add_liquidity_mining" => {
                let mut body = order_body(params)?;
                let quote = params.get("quoteAmount");
                let base = params.get("baseAmount");
                if quote.is_none() && base.is_none() {
                    return Err(DcexError::InvalidInput(
                        "quoteAmount or baseAmount is required".to_string(),
                    ));
                }
                if let Some(amount) = quote {
                    positive_amount("quoteAmount", amount)?;
                    validate_account_type(params.required("quoteAccountType")?)?;
                }
                if let Some(amount) = base {
                    positive_amount("baseAmount", amount)?;
                    validate_account_type(params.required("baseAccountType")?)?;
                }
                for key in [
                    "quoteAmount",
                    "baseAmount",
                    "quoteAccountType",
                    "baseAccountType",
                    "leverage",
                ] {
                    insert_optional_string(&mut body, key, params.get(key));
                }
                validate_optional_leverage(params)?;
                self.post_request(LIQUIDITY_MINING_ADD, body).await
            }
            "remove_liquidity_mining" => {
                let mut body = order_body(params)?;
                insert_optional_string(
                    &mut body,
                    "positionId",
                    Some(params.required("positionId")?),
                );
                if let Some(rate) = params.get("removeRate") {
                    let rate = rate.parse::<u8>().map_err(|error| {
                        DcexError::InvalidInput(format!("invalid removeRate: {error}"))
                    })?;
                    if rate > 100 {
                        return Err(DcexError::InvalidInput(
                            "removeRate must be between 0 and 100".to_string(),
                        ));
                    }
                }
                validate_optional_enum(
                    params,
                    "removeType",
                    &["Normal", "SingleQuoteCoin", "SingleBaseCoin"],
                )?;
                insert_optional_i64(&mut body, "removeRate", params.get("removeRate"))?;
                insert_optional_string(&mut body, "removeType", params.get("removeType"));
                self.post_request(LIQUIDITY_MINING_REMOVE, body).await
            }
            "reinvest_liquidity_mining" => {
                let mut body = order_body(params)?;
                insert_optional_string(
                    &mut body,
                    "positionId",
                    Some(params.required("positionId")?),
                );
                validate_optional_leverage(params)?;
                insert_optional_string(&mut body, "leverage", params.get("leverage"));
                self.post_request(LIQUIDITY_MINING_REINVEST, body).await
            }
            "add_liquidity_mining_margin" => {
                let mut body = order_body(params)?;
                let amount = params.required("amount")?;
                positive_amount("amount", amount)?;
                let account_type = params.required("quoteAccountType")?;
                validate_account_type(account_type)?;
                for (key, value) in [
                    ("positionId", params.required("positionId")?),
                    ("amount", amount),
                    ("quoteAccountType", account_type),
                ] {
                    insert_optional_string(&mut body, key, Some(value));
                }
                self.post_request(LIQUIDITY_MINING_ADD_MARGIN, body).await
            }
            "claim_liquidity_mining_interest" => {
                let body = string_body(&[("productId", params.required("productId")?)]);
                self.post_request(LIQUIDITY_MINING_CLAIM, body).await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}

fn order_body(params: &BybitParams) -> Result<Map<String, Value>> {
    let order_link_id = params.required("orderLinkId")?;
    if order_link_id.is_empty()
        || order_link_id.len() > 40
        || !order_link_id
            .chars()
            .all(|character| character.is_ascii_alphanumeric() || matches!(character, '-' | '_'))
    {
        return Err(DcexError::InvalidInput(
            "orderLinkId must contain 1 to 40 ASCII letters, numbers, '-' or '_'".to_string(),
        ));
    }
    Ok(string_body(&[
        ("productId", params.required("productId")?),
        ("orderLinkId", order_link_id),
    ]))
}

fn positive_amount(key: &str, value: &str) -> Result<()> {
    if value.parse::<f64>().is_ok_and(|amount| amount > 0.0) {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(format!(
            "{key} must be a positive number"
        )))
    }
}

fn validate_account_type(value: &str) -> Result<()> {
    if matches!(value, "FUND" | "UNIFIED") {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(
            "account type must be FUND or UNIFIED".to_string(),
        ))
    }
}

fn validate_optional_enum(params: &BybitParams, key: &str, values: &[&str]) -> Result<()> {
    if let Some(value) = params.get(key) {
        if !values.contains(&value) {
            return Err(DcexError::InvalidInput(format!(
                "{key} must be one of {}",
                values.join(", ")
            )));
        }
    }
    Ok(())
}

fn validate_optional_leverage(params: &BybitParams) -> Result<()> {
    if let Some(leverage) = params.get("leverage") {
        if !leverage.parse::<u16>().is_ok_and(|value| value > 0) {
            return Err(DcexError::InvalidInput(
                "leverage must be a positive integer".to_string(),
            ));
        }
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

    fn params(values: &[(&str, &str)]) -> BybitParams {
        BybitParams::from_pairs(
            values
                .iter()
                .map(|(key, value)| (key.to_string(), value.to_string()))
                .collect(),
        )
    }

    #[test]
    fn liquidity_order_link_id_is_bounded() {
        assert!(order_body(&params(&[("productId", "1"), ("orderLinkId", "a")])).is_ok());
        assert!(order_body(&params(&[
            ("productId", "1"),
            ("orderLinkId", &"a".repeat(41))
        ]))
        .is_err());
    }

    #[test]
    fn history_limit_and_ordering_are_validated() {
        assert!(validate_history(&params(&[("limit", "51")])).is_err());
        assert!(validate_history(&params(&[("startTime", "2"), ("endTime", "1")])).is_err());
    }
}
