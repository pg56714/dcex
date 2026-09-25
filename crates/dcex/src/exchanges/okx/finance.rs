use serde_json::{Map, Value};

use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::OkxClient;
use super::endpoints::*;
use super::params::{OkxParams, insert_optional_bool, insert_optional_string};

impl OkxClient {
    pub(super) async fn finance_private_request(
        &self,
        method_name: &str,
        params: &OkxParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_saving_balance" => {
                self.get_request(SAVINGS_BALANCE, params.only(&["ccy"]))
                    .await
            }
            "purchase_redeem_savings" => {
                validate_positive_amount(params)?;
                validate_savings_side(params)?;
                let mut body = params.required_body(&["ccy", "amt", "side"])?;
                insert_optional_string(&mut body, "rate", params.get("rate"));
                self.post_request(SAVINGS_PURCHASE_REDEMPT, Value::Object(body))
                    .await
            }
            "set_savings_lending_rate" => {
                self.post_request(
                    SAVINGS_SET_LENDING_RATE,
                    Value::Object(params.required_body(&["ccy", "rate"])?),
                )
                .await
            }
            "get_savings_lending_history" => {
                self.get_request(
                    SAVINGS_LENDING_HISTORY,
                    params.only(&["ccy", "after", "before", "limit"]),
                )
                .await
            }
            "set_auto_earn" => {
                let action = params.required("action")?;
                if !["turn_on", "turn_off"].contains(&action) {
                    return Err(DcexError::InvalidInput(
                        "action must be turn_on or turn_off".to_string(),
                    ));
                }
                if let Some(earn_type) = params.get("earnType") {
                    if !["0", "1"].contains(&earn_type) {
                        return Err(DcexError::InvalidInput(
                            "earnType must be 0 or 1".to_string(),
                        ));
                    }
                }
                let mut body = params.required_body(&["ccy", "action"])?;
                insert_optional_string(&mut body, "earnType", params.get("earnType"));
                self.post_request(ACCOUNT_SET_AUTO_EARN, Value::Object(body))
                    .await
            }
            "get_staking_offers" => {
                self.get_request(
                    STAKING_OFFERS,
                    params.only(&["productId", "protocolType", "ccy"]),
                )
                .await
            }
            "purchase_staking" => {
                params.required("productId")?;
                let invest_data = params.json_required("investData")?;
                if !invest_data.is_array() {
                    return Err(DcexError::InvalidInput(
                        "investData must be a JSON array".to_string(),
                    ));
                }
                let mut body = Map::new();
                body.insert(
                    "productId".to_string(),
                    Value::String(params.required("productId")?.to_string()),
                );
                body.insert("investData".to_string(), invest_data);
                insert_optional_string(&mut body, "term", params.get("term"));
                insert_optional_string(&mut body, "tag", params.get("tag"));
                self.post_request(STAKING_PURCHASE, Value::Object(body))
                    .await
            }
            "redeem_staking" => {
                let mut body = params.required_body(&["ordId", "protocolType"])?;
                insert_optional_bool(
                    &mut body,
                    "allowEarlyRedeem",
                    params.get("allowEarlyRedeem"),
                )?;
                self.post_request(STAKING_REDEEM, Value::Object(body)).await
            }
            "cancel_staking" => {
                self.post_request(
                    STAKING_CANCEL,
                    Value::Object(params.required_body(&["ordId", "protocolType"])?),
                )
                .await
            }
            "get_active_staking_orders" => {
                self.get_request(
                    STAKING_ACTIVE_ORDERS,
                    params.only(&["productId", "protocolType", "ccy", "state"]),
                )
                .await
            }
            "get_staking_order_history" => {
                self.get_request(
                    STAKING_ORDER_HISTORY,
                    params.only(&[
                        "productId",
                        "protocolType",
                        "ccy",
                        "after",
                        "before",
                        "limit",
                    ]),
                )
                .await
            }
            "get_eth_staking_product_info" => {
                self.get_request(ETH_STAKING_PRODUCT_INFO, Vec::new()).await
            }
            "purchase_eth_staking" => {
                validate_positive_amount(params)?;
                self.post_request(
                    ETH_STAKING_PURCHASE,
                    Value::Object(params.required_body(&["amt"])?),
                )
                .await
            }
            "redeem_eth_staking" => {
                validate_positive_amount(params)?;
                self.post_request(
                    ETH_STAKING_REDEEM,
                    Value::Object(params.required_body(&["amt"])?),
                )
                .await
            }
            "cancel_eth_staking_redemption" => {
                self.post_request(
                    ETH_STAKING_CANCEL_REDEEM,
                    Value::Object(params.required_body(&["ordId"])?),
                )
                .await
            }
            "get_eth_staking_balance" => self.get_request(ETH_STAKING_BALANCE, Vec::new()).await,
            "get_eth_staking_history" => {
                self.get_request(
                    ETH_STAKING_HISTORY,
                    params.only(&["type", "status", "after", "before", "limit"]),
                )
                .await
            }
            "get_sol_staking_product_info" => {
                self.get_request(SOL_STAKING_PRODUCT_INFO, Vec::new()).await
            }
            "purchase_sol_staking" => {
                validate_positive_amount(params)?;
                self.post_request(
                    SOL_STAKING_PURCHASE,
                    Value::Object(params.required_body(&["amt"])?),
                )
                .await
            }
            "redeem_sol_staking" => {
                validate_positive_amount(params)?;
                self.post_request(
                    SOL_STAKING_REDEEM,
                    Value::Object(params.required_body(&["amt"])?),
                )
                .await
            }
            "get_sol_staking_balance" => self.get_request(SOL_STAKING_BALANCE, Vec::new()).await,
            "get_sol_staking_history" => {
                self.get_request(
                    SOL_STAKING_HISTORY,
                    params.only(&["type", "status", "after", "before", "limit"]),
                )
                .await
            }
            "get_flexible_loan_borrow_currencies" => {
                self.get_request(FLEXIBLE_LOAN_BORROW_CURRENCIES, Vec::new())
                    .await
            }
            "get_flexible_loan_collateral_assets" => {
                self.get_request(FLEXIBLE_LOAN_COLLATERAL_ASSETS, params.only(&["ccy"]))
                    .await
            }
            "get_flexible_loan_max_loan" => {
                params.required("borrowCcy")?;
                let supported_collateral = params.json_required("supCollateral")?;
                if !supported_collateral.is_array() {
                    return Err(DcexError::InvalidInput(
                        "supCollateral must be a JSON array".to_string(),
                    ));
                }
                let mut body = Map::new();
                body.insert(
                    "borrowCcy".to_string(),
                    Value::String(params.required("borrowCcy")?.to_string()),
                );
                body.insert("supCollateral".to_string(), supported_collateral);
                self.post_request(FLEXIBLE_LOAN_MAX_LOAN, Value::Object(body))
                    .await
            }
            "get_flexible_loan_max_collateral_redeem" => {
                params.required("ccy")?;
                self.get_request(FLEXIBLE_LOAN_MAX_COLLATERAL_REDEEM, params.only(&["ccy"]))
                    .await
            }
            "adjust_flexible_loan_collateral" => {
                let adjustment_type = params.required("type")?;
                if !["add", "reduce"].contains(&adjustment_type) {
                    return Err(DcexError::InvalidInput(
                        "type must be add or reduce".to_string(),
                    ));
                }
                self.post_request(
                    FLEXIBLE_LOAN_ADJUST_COLLATERAL,
                    Value::Object(params.required_body(&[
                        "type",
                        "collateralCcy",
                        "collateralAmt",
                    ])?),
                )
                .await
            }
            "get_flexible_loan_info" => {
                self.get_request(FLEXIBLE_LOAN_INFO, params.only(&["ordId"]))
                    .await
            }
            "get_flexible_loan_history" => {
                self.get_request(
                    FLEXIBLE_LOAN_HISTORY,
                    params.only(&["type", "after", "before", "limit"]),
                )
                .await
            }
            "get_flexible_loan_interest_accrued" => {
                self.get_request(
                    FLEXIBLE_LOAN_INTEREST_ACCRUED,
                    params.only(&["ccy", "ordId", "after", "before", "limit"]),
                )
                .await
            }
            "borrow_flexible_loan" => {
                let loan_data = params.json_required("loanData")?;
                if !loan_data.is_array() {
                    return Err(DcexError::InvalidInput(
                        "loanData must be a JSON array".to_string(),
                    ));
                }
                let mut body = Map::new();
                body.insert("loanData".to_string(), loan_data);
                body.insert(
                    "clOrdId".to_string(),
                    Value::String(params.required("clOrdId")?.to_string()),
                );
                insert_optional_string(&mut body, "ordId", params.get("ordId"));
                if let Some(collateral_data) = params.json_optional("collateralData")? {
                    if !collateral_data.is_array() {
                        return Err(DcexError::InvalidInput(
                            "collateralData must be a JSON array".to_string(),
                        ));
                    }
                    body.insert("collateralData".to_string(), collateral_data);
                }
                insert_optional_bool(&mut body, "eMode", params.get("eMode"))?;
                self.post_request(FLEXIBLE_LOAN_BORROW, Value::Object(body))
                    .await
            }
            "repay_flexible_loan" => {
                validate_positive_amount(params)?;
                self.post_request(
                    FLEXIBLE_LOAN_REPAY,
                    Value::Object(params.required_body(&["ordId", "ccy", "amt", "clOrdId"])?),
                )
                .await
            }
            "get_flexible_loan_emode_info" => {
                self.get_request(FLEXIBLE_LOAN_EMODE_INFO, Vec::new()).await
            }
            "get_dual_investment_currency_pairs" => {
                self.get_request(DUAL_INVESTMENT_CURRENCY_PAIRS, Vec::new())
                    .await
            }
            "get_dual_investment_products" => {
                params.required("baseCcy")?;
                params.required("quoteCcy")?;
                params.required("optType")?;
                self.get_request(
                    DUAL_INVESTMENT_PRODUCTS,
                    params.only(&["baseCcy", "quoteCcy", "optType"]),
                )
                .await
            }
            "request_dual_investment_quote" => {
                self.post_request(
                    DUAL_INVESTMENT_QUOTE,
                    Value::Object(params.required_body(&[
                        "productId",
                        "notionalSz",
                        "notionalCcy",
                    ])?),
                )
                .await
            }
            "trade_dual_investment" => {
                self.post_request(
                    DUAL_INVESTMENT_TRADE,
                    Value::Object(params.required_body(&["quoteId"])?),
                )
                .await
            }
            "request_dual_investment_redeem_quote" => {
                self.post_request(
                    DUAL_INVESTMENT_REDEEM_QUOTE,
                    Value::Object(params.required_body(&["ordId"])?),
                )
                .await
            }
            "redeem_dual_investment" => {
                self.post_request(
                    DUAL_INVESTMENT_REDEEM,
                    Value::Object(params.required_body(&["ordId", "quoteId"])?),
                )
                .await
            }
            "get_dual_investment_order_status" => {
                params.required("ordId")?;
                self.get_request(DUAL_INVESTMENT_ORDER_STATUS, params.only(&["ordId"]))
                    .await
            }
            "get_dual_investment_order_history" => {
                self.get_request(
                    DUAL_INVESTMENT_ORDER_HISTORY,
                    params.only(&[
                        "ordId",
                        "productId",
                        "uly",
                        "state",
                        "beginId",
                        "endId",
                        "begin",
                        "end",
                        "limit",
                    ]),
                )
                .await
            }
            "get_okusd_limits" => self.get_request(OKUSD_LIMITS, Vec::new()).await,
            "get_okusd_account" => self.get_request(OKUSD_ACCOUNT, Vec::new()).await,
            "get_okusd_rate_history" => {
                self.get_request(OKUSD_RATE_HISTORY, params.only(&["limit", "begin", "end"]))
                    .await
            }
            "get_okusd_subscribe_history" => {
                self.get_request(
                    OKUSD_SUBSCRIBE_HISTORY,
                    params.only(&["limit", "begin", "end"]),
                )
                .await
            }
            "get_okusd_redeem_history" => {
                self.get_request(
                    OKUSD_REDEEM_HISTORY,
                    params.only(&["limit", "begin", "end", "type"]),
                )
                .await
            }
            "get_okusd_rewards_history" => {
                self.get_request(
                    OKUSD_REWARDS_HISTORY,
                    params.only(&["limit", "begin", "end"]),
                )
                .await
            }
            "subscribe_okusd" => {
                validate_okusd_amount(params)?;
                self.post_request(
                    OKUSD_SUBSCRIBE,
                    Value::Object(params.required_body(&["amt", "clOrdId"])?),
                )
                .await
            }
            "redeem_okusd" => {
                validate_okusd_amount(params)?;
                let redeem_type = params.required("redeemType")?;
                if !["1", "2"].contains(&redeem_type) {
                    return Err(DcexError::InvalidInput(
                        "redeemType must be 1 (fast) or 2 (standard)".to_string(),
                    ));
                }
                self.post_request(
                    OKUSD_REDEEM,
                    Value::Object(params.required_body(&["amt", "redeemType", "clOrdId"])?),
                )
                .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}

fn validate_okusd_amount(params: &OkxParams) -> Result<()> {
    let amount = params.required("amt")?;
    if amount.parse::<f64>().is_ok_and(|value| value >= 1.0) {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(
            "OKUSD amt must be at least 1".to_string(),
        ))
    }
}

fn validate_positive_amount(params: &OkxParams) -> Result<()> {
    let amount = params.required("amt")?;
    if amount.parse::<f64>().is_ok_and(|value| value > 0.0) {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(
            "amt must be a positive number".to_string(),
        ))
    }
}

fn validate_savings_side(params: &OkxParams) -> Result<()> {
    let side = params.required("side")?;
    if ["purchase", "redempt"].contains(&side) {
        Ok(())
    } else {
        Err(DcexError::InvalidInput(
            "side must be purchase or redempt".to_string(),
        ))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn savings_side_is_constrained() {
        let params = OkxParams::from_pairs(vec![
            ("ccy".to_string(), "USDT".to_string()),
            ("amt".to_string(), "1".to_string()),
            ("side".to_string(), "redeem".to_string()),
        ]);
        assert!(validate_savings_side(&params).is_err());
    }

    #[test]
    fn staking_amount_must_be_positive() {
        let params = OkxParams::from_pairs(vec![("amt".to_string(), "0".to_string())]);
        assert!(validate_positive_amount(&params).is_err());
    }
}
