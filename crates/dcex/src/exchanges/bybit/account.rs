pub(in crate::exchanges::bybit) use serde_json::{Map, Value};

pub(in crate::exchanges::bybit) use super::client::BybitClient;
pub(in crate::exchanges::bybit) use super::endpoints::*;
pub(in crate::exchanges::bybit) use super::params::{
    BybitParams, insert_optional_string, push_optional,
};
pub(in crate::exchanges::bybit) use crate::exchange::ValidatedResponse;
pub(in crate::exchanges::bybit) use crate::{DcexError, Result};

impl BybitClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "set_spot_margin_leverage" => {
                params.ensure_allowed(&["leverage", "currency"])?;
                if !params
                    .required("leverage")?
                    .parse::<u32>()
                    .is_ok_and(|v| (2..=10).contains(&v))
                {
                    return Err(DcexError::InvalidInput(
                        "spot margin leverage must be an integer from 2 to 10".into(),
                    ));
                }
                let mut body = Map::new();
                insert_optional_string(&mut body, "leverage", params.get("leverage"));
                insert_optional_string(&mut body, "currency", params.get("currency"));
                self.post_request("/v5/spot-margin-trade/set-leverage", body)
                    .await
            }
            "set_spot_margin_mode" => {
                params.ensure_allowed(&["spotMarginMode"])?;
                let mode = params.required("spotMarginMode")?;
                if !["0", "1"].contains(&mode) {
                    return Err(DcexError::InvalidInput(
                        "spotMarginMode must be 0 or 1".into(),
                    ));
                }
                let mut body = Map::new();
                body.insert("spotMarginMode".into(), Value::String(mode.into()));
                self.post_request("/v5/spot-margin-trade/switch-mode", body)
                    .await
            }

            "get_wallet_balance" => {
                params.ensure_allowed(&["accountType", "coin"])?;
                // Unified Trading Accounts are the only account type the endpoint serves.
                if params
                    .get("accountType")
                    .is_some_and(|value| value != "UNIFIED")
                {
                    return Err(DcexError::InvalidInput(
                        "Bybit get_wallet_balance accountType must be UNIFIED".into(),
                    ));
                }
                let mut query = vec![("accountType".to_string(), "UNIFIED".to_string())];
                push_optional(&mut query, "coin", params.get("coin"));
                self.get_request(GET_WALLET_BALANCE, query).await
            }
            "get_transferable_amount" => {
                self.dispatch_get_transferable_amount(method_name, params)
                    .await
            }
            "upgrade_to_unified_trading_account" => {
                params.ensure_allowed(&[])?;
                self.post_request(UPGRADE_TO_UNIFIED_ACCOUNT, Map::new())
                    .await
            }
            "get_borrow_history" => {
                params.ensure_allowed(&["limit", "coin", "startTime", "endTime", "cursor"])?;
                let mut query = vec![(
                    "limit".to_string(),
                    params.get("limit").unwrap_or("20").to_string(),
                )];
                push_optional(&mut query, "currency", params.get("coin"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                push_optional(&mut query, "endTime", params.get("endTime"));
                push_optional(&mut query, "cursor", params.get("cursor"));
                self.get_request(GET_BORROW_HISTORY, query).await
            }
            "get_collateral_info" => {
                params.ensure_allowed(&["currency"])?;
                let mut query = Vec::new();
                push_optional(&mut query, "currency", params.get("currency"));
                self.get_request(GET_COLLATERAL_INFO, query).await
            }
            "manual_borrow" => {
                params.ensure_allowed(&["coin", "amount"])?;
                let mut body = Map::new();
                body.insert(
                    "coin".to_string(),
                    Value::String(params.required("coin")?.to_string()),
                );
                body.insert(
                    "amount".to_string(),
                    Value::String(params.required("amount")?.to_string()),
                );
                self.post_request(MANUAL_BORROW, body).await
            }
            "manual_repay" => {
                params.ensure_allowed(&["repaymentType", "coin", "amount"])?;
                let repayment_type = params.get("repaymentType").unwrap_or("FLEXIBLE");
                if !["ALL", "FIXED", "FLEXIBLE"].contains(&repayment_type) {
                    return Err(DcexError::InvalidInput(
                        "repaymentType must be ALL, FIXED, or FLEXIBLE.".to_string(),
                    ));
                }
                if params.get("coin").is_none() && params.get("amount").is_some() {
                    return Err(DcexError::InvalidInput(
                        "coin is required when amount is provided.".to_string(),
                    ));
                }
                if params.get("coin").is_none() && repayment_type != "ALL" {
                    return Err(DcexError::InvalidInput(
                        "repaymentType must be ALL when coin is omitted.".to_string(),
                    ));
                }
                let mut body = Map::new();
                insert_optional_string(&mut body, "coin", params.get("coin"));
                insert_optional_string(&mut body, "amount", params.get("amount"));
                body.insert(
                    "repaymentType".to_string(),
                    Value::String(repayment_type.to_string()),
                );
                self.post_request(MANUAL_REPAY, body).await
            }
            "manual_repay_without_conversion" => {
                params.ensure_allowed(&["repaymentType", "coin", "amount"])?;
                let repayment_type = params.get("repaymentType").unwrap_or("FLEXIBLE");
                if !["ALL", "FIXED", "FLEXIBLE"].contains(&repayment_type) {
                    return Err(DcexError::InvalidInput(
                        "repaymentType must be ALL, FIXED, or FLEXIBLE.".to_string(),
                    ));
                }
                let mut body = Map::new();
                body.insert(
                    "coin".to_string(),
                    Value::String(params.required("coin")?.to_string()),
                );
                insert_optional_string(&mut body, "amount", params.get("amount"));
                body.insert(
                    "repaymentType".to_string(),
                    Value::String(repayment_type.to_string()),
                );
                self.post_request(MANUAL_REPAY_WITHOUT_CONVERSION, body)
                    .await
            }
            "get_spot_fee_rates"
            | "get_linear_fee_rates"
            | "get_inverse_fee_rates"
            | "get_option_fee_rates" => {
                params.ensure_allowed(&["product_symbol", "baseCoin"])?;
                let mut query = Vec::new();
                if let Some(product_symbol) = params.get("product_symbol") {
                    let category = match method_name {
                        "get_spot_fee_rates" => "spot",
                        "get_linear_fee_rates" => "linear",
                        "get_inverse_fee_rates" => "inverse",
                        "get_option_fee_rates" => "option",
                        _ => unreachable!(),
                    };
                    let product_category =
                        self.category_for_product_symbol(product_symbol, category)?;
                    if product_category != category {
                        return Err(crate::DcexError::InvalidInput(format!(
                            "{method_name} does not support product_symbol: {product_symbol}"
                        )));
                    }
                    query.push((
                        "symbol".to_string(),
                        self.symbol_category(product_symbol, Some(category))?.0,
                    ));
                    query.push(("category".to_string(), category.to_string()));
                } else {
                    let category = match method_name {
                        "get_spot_fee_rates" => "spot",
                        "get_linear_fee_rates" => "linear",
                        "get_inverse_fee_rates" => "inverse",
                        "get_option_fee_rates" => "option",
                        _ => unreachable!(),
                    };
                    query.push(("category".to_string(), category.to_string()));
                }
                push_optional(&mut query, "baseCoin", params.get("baseCoin"));
                self.get_request(GET_FEE_RATE, query).await
            }
            "get_account_info" => {
                params.ensure_allowed(&[])?;
                self.get_request(GET_ACCOUNT_INFO, Vec::new()).await
            }
            "get_transaction_log" => {
                params.ensure_allowed(&[
                    "limit",
                    "accountType",
                    "category",
                    "coin",
                    "baseCoin",
                    "type",
                    "transSubType",
                    "startTime",
                    "endTime",
                    "cursor",
                ])?;
                let mut query = vec![(
                    "limit".to_string(),
                    params.get("limit").unwrap_or("20").to_string(),
                )];
                push_optional(&mut query, "accountType", params.get("accountType"));
                push_optional(&mut query, "category", params.get("category"));
                push_optional(&mut query, "currency", params.get("coin"));
                push_optional(&mut query, "baseCoin", params.get("baseCoin"));
                push_optional(&mut query, "type", params.get("type"));
                push_optional(&mut query, "transSubType", params.get("transSubType"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                push_optional(&mut query, "endTime", params.get("endTime"));
                push_optional(&mut query, "cursor", params.get("cursor"));
                self.get_request(GET_TRANSACTION_LOG, query).await
            }
            "set_margin_mode" => {
                params.ensure_allowed(&["setMarginMode"])?;
                let mut body = Map::new();
                body.insert(
                    "setMarginMode".to_string(),
                    Value::String(params.required("setMarginMode")?.to_string()),
                );
                self.post_request(SET_MARGIN_MODE, body).await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
