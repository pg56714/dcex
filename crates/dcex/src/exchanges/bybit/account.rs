use serde_json::{Map, Value};

use super::client::BybitClient;
use super::endpoints::*;
use super::params::{BybitParams, insert_optional_string, push_optional};
use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

impl BybitClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_wallet_balance" => {
                let mut query = vec![("accountType".to_string(), "UNIFIED".to_string())];
                push_optional(&mut query, "coin", params.get("coin"));
                self.get_request(GET_WALLET_BALANCE, query).await
            }
            "get_transferable_amount" => {
                let coins = params.required("coins")?;
                if coins.is_empty() {
                    return Err(DcexError::InvalidInput(
                        "coins must contain at least one coin.".to_string(),
                    ));
                }
                let count = coins.split(',').filter(|coin| !coin.is_empty()).count();
                if count > 20 {
                    return Err(DcexError::InvalidInput(
                        "coins must contain no more than 20 coins.".to_string(),
                    ));
                }
                self.get_request(
                    GET_TRANSFERABLE_AMOUNT,
                    vec![("coinName".to_string(), coins.to_string())],
                )
                .await
            }
            "upgrade_to_unified_trading_account" => {
                self.post_request(UPGRADE_TO_UNIFIED_ACCOUNT, Map::new())
                    .await
            }
            "get_borrow_history" => {
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
                let mut query = Vec::new();
                push_optional(
                    &mut query,
                    "currency",
                    params.get("currency").or_else(|| params.get("coin")),
                );
                self.get_request(GET_COLLATERAL_INFO, query).await
            }
            "manual_borrow" => {
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
                    query.push(("symbol".to_string(), self.exchange_symbol(product_symbol)?));
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
            "get_account_info" => self.get_request(GET_ACCOUNT_INFO, Vec::new()).await,
            "get_transaction_log" => {
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
                let mut body = Map::new();
                body.insert(
                    "setMarginMode".to_string(),
                    Value::String(params.required("margin_mode")?.to_string()),
                );
                self.post_request(SET_MARGIN_MODE, body).await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
