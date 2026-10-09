pub(in crate::exchanges::okx) use serde_json::Value;

pub(in crate::exchanges::okx) use crate::Result;
pub(in crate::exchanges::okx) use crate::exchange::ValidatedResponse;

pub(in crate::exchanges::okx) use super::client::OkxClient;
pub(in crate::exchanges::okx) use super::endpoints::*;
pub(in crate::exchanges::okx) use super::params::{
    OkxParams, insert_optional_bool, insert_optional_string, push_optional, push_optional_owned,
};

impl OkxClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &OkxParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_account_instruments" => {
                params.ensure_allowed(&["instType", "instFamily", "seriesId"])?;
                let mut query = vec![(
                    "instType".to_string(),
                    params.required("instType")?.to_string(),
                )];
                self.push_inst_id(&mut query, params, "product_symbol")?;
                push_optional(&mut query, "instFamily", params.get("instFamily"));
                push_optional(&mut query, "seriesId", params.get("seriesId"));
                self.get_request(ACCOUNT_INSTRUMENTS, query).await
            }
            "get_account_balance" => {
                params.ensure_allowed(&["ccy"])?;
                let mut query = Vec::new();
                push_optional_owned(&mut query, "ccy", params.csv("ccy")?);
                self.get_request(ACCOUNT_BALANCE, query).await
            }
            "get_positions" => {
                params.ensure_allowed(&["instType", "posId"])?;
                let mut query = Vec::new();
                push_optional(&mut query, "instType", params.get("instType"));
                push_optional(&mut query, "posId", params.get("posId"));
                self.push_inst_id(&mut query, params, "product_symbol")?;
                self.get_request(ACCOUNT_POSITIONS, query).await
            }
            "get_positions_history" => {
                params.ensure_allowed(&[
                    "instType", "posId", "mgnMode", "type", "after", "before", "limit",
                ])?;
                let mut query = params.only(&[
                    "instType", "posId", "mgnMode", "type", "after", "before", "limit",
                ]);
                self.push_inst_id(&mut query, params, "product_symbol")?;
                self.get_request(ACCOUNT_POSITIONS_HISTORY, query).await
            }
            "get_position_risk" => {
                params.ensure_allowed(&["instType"])?;
                self.get_request(ACCOUNT_POSITION_RISK, params.only(&["instType"]))
                    .await
            }
            "get_account_bills" => {
                params.ensure_allowed(&[
                    "instType", "ccy", "mgnMode", "ctType", "type", "subType", "after", "before",
                    "begin", "end", "limit",
                ])?;
                let mut query = params.only(&[
                    "instType", "ccy", "mgnMode", "ctType", "type", "subType", "after", "before",
                    "begin", "end", "limit",
                ]);
                self.push_inst_id(&mut query, params, "product_symbol")?;
                self.get_request(ACCOUNT_BILLS, query).await
            }
            "get_account_bills_archive" => {
                params.ensure_allowed(&[
                    "instType", "ccy", "mgnMode", "ctType", "type", "subType", "after", "before",
                    "begin", "end", "limit",
                ])?;
                let mut query = params.only(&[
                    "instType", "ccy", "mgnMode", "ctType", "type", "subType", "after", "before",
                    "begin", "end", "limit",
                ]);
                self.push_inst_id(&mut query, params, "product_symbol")?;
                self.get_request(ACCOUNT_BILLS_ARCHIVE, query).await
            }
            "get_account_bills_history_archive" => {
                params.ensure_allowed(&["year", "quarter", "type"])?;
                let mut query = params.required_only(&["year", "quarter"])?;
                push_optional(&mut query, "type", params.get("type"));
                self.get_request(ACCOUNT_BILLS_HISTORY_ARCHIVE, query).await
            }
            "post_account_bills_history_archive" => {
                params.ensure_allowed(&["year", "quarter", "type"])?;
                let mut body = params.required_body(&["year", "quarter"])?;
                insert_optional_string(&mut body, "type", params.get("type"));
                self.post_request(ACCOUNT_BILLS_HISTORY_ARCHIVE, Value::Object(body))
                    .await
            }
            "get_account_config" => {
                params.ensure_allowed(&[])?;
                self.get_request(ACCOUNT_CONFIG, Vec::new()).await
            }
            "set_position_mode" => {
                params.ensure_allowed(&["posMode"])?;
                self.post_request(
                    ACCOUNT_SET_POSITION_MODE,
                    Value::Object(params.required_body(&["posMode"])?),
                )
                .await
            }
            "set_leverage" => {
                params.ensure_allowed(&["lever", "mgnMode", "ccy", "posSide", "product_symbol"])?;
                let mut body = params.required_body(&["lever", "mgnMode"])?;
                self.insert_inst_id(&mut body, params, "product_symbol")?;
                insert_optional_string(&mut body, "ccy", params.get("ccy"));
                insert_optional_string(&mut body, "posSide", params.get("posSide"));
                self.post_request(ACCOUNT_SET_LEVERAGE, Value::Object(body))
                    .await
            }
            "get_max_order_size" => {
                params.ensure_allowed(&[
                    "tdMode",
                    "ccy",
                    "px",
                    "leverage",
                    "tradeQuoteCcy",
                    "outcome",
                    "product_symbol",
                ])?;
                let mut query =
                    vec![("tdMode".to_string(), params.required("tdMode")?.to_string())];
                self.push_required_inst_id(&mut query, params)?;
                push_optional(&mut query, "ccy", params.get("ccy"));
                push_optional(&mut query, "px", params.get("px"));
                push_optional(&mut query, "leverage", params.get("leverage"));
                push_optional(&mut query, "tradeQuoteCcy", params.get("tradeQuoteCcy"));
                push_optional(&mut query, "outcome", params.get("outcome"));
                self.get_request(ACCOUNT_MAX_SIZE, query).await
            }
            "get_max_avail_size" => {
                params.ensure_allowed(&[
                    "tdMode",
                    "ccy",
                    "reduceOnly",
                    "px",
                    "tradeQuoteCcy",
                    "product_symbol",
                ])?;
                let mut query =
                    vec![("tdMode".to_string(), params.required("tdMode")?.to_string())];
                self.push_required_inst_id(&mut query, params)?;
                push_optional(&mut query, "ccy", params.get("ccy"));
                push_optional(&mut query, "reduceOnly", params.get("reduceOnly"));
                push_optional(&mut query, "px", params.get("px"));
                push_optional(&mut query, "tradeQuoteCcy", params.get("tradeQuoteCcy"));
                self.get_request(ACCOUNT_MAX_AVAIL_SIZE, query).await
            }
            "get_leverage" => {
                params.ensure_allowed(&["mgnMode", "ccy", "product_symbol"])?;
                let mut query = vec![(
                    "mgnMode".to_string(),
                    params.required("mgnMode")?.to_string(),
                )];
                self.push_inst_id(&mut query, params, "product_symbol")?;
                push_optional(&mut query, "ccy", params.get("ccy"));
                self.get_request(ACCOUNT_LEVERAGE_INFO, query).await
            }
            "get_adjust_leverage" => {
                params.ensure_allowed(&[
                    "instType",
                    "mgnMode",
                    "lever",
                    "ccy",
                    "posSide",
                    "product_symbol",
                ])?;
                let mut query = params.required_only(&["instType", "mgnMode", "lever"])?;
                self.push_inst_id(&mut query, params, "product_symbol")?;
                push_optional(&mut query, "ccy", params.get("ccy"));
                push_optional(&mut query, "posSide", params.get("posSide"));
                self.get_request(ACCOUNT_ADJUST_LEVERAGE_INFO, query).await
            }
            "get_max_loan" => {
                params.ensure_allowed(&[
                    "mgnMode",
                    "ccy",
                    "mgnCcy",
                    "tradeQuoteCcy",
                    "product_symbol",
                ])?;
                let mut query = vec![(
                    "mgnMode".to_string(),
                    params.required("mgnMode")?.to_string(),
                )];
                self.push_inst_id(&mut query, params, "product_symbol")?;
                push_optional(&mut query, "ccy", params.get("ccy"));
                push_optional(&mut query, "mgnCcy", params.get("mgnCcy"));
                push_optional(&mut query, "tradeQuoteCcy", params.get("tradeQuoteCcy"));
                self.get_request(ACCOUNT_MAX_LOAN, query).await
            }
            "get_spot_fee_rates"
            | "get_margin_fee_rates"
            | "get_swap_fee_rates"
            | "get_futures_fee_rates"
            | "get_option_fee_rates" => {
                params.ensure_allowed(&["instFamily", "groupId"])?;
                let inst_type = match method_name {
                    "get_spot_fee_rates" => "SPOT",
                    "get_margin_fee_rates" => "MARGIN",
                    "get_swap_fee_rates" => "SWAP",
                    "get_futures_fee_rates" => "FUTURES",
                    "get_option_fee_rates" => "OPTION",
                    _ => unreachable!(),
                };
                let mut query = vec![("instType".to_string(), inst_type.to_string())];
                self.push_inst_id(&mut query, params, "product_symbol")?;
                push_optional(&mut query, "instFamily", params.get("instFamily"));
                push_optional(&mut query, "groupId", params.get("groupId"));
                self.get_request(ACCOUNT_TRADE_FEE, query).await
            }
            "get_interest_accrued" => {
                params.ensure_allowed(&["type", "ccy", "mgnMode", "after", "before", "limit"])?;
                let mut query =
                    params.only(&["type", "ccy", "mgnMode", "after", "before", "limit"]);
                self.push_inst_id(&mut query, params, "product_symbol")?;
                self.get_request(ACCOUNT_INTEREST_ACCRUED, query).await
            }
            "get_interest_rate" => {
                params.ensure_allowed(&["ccy"])?;
                self.get_request(ACCOUNT_INTEREST_RATE, params.only(&["ccy"]))
                    .await
            }
            "set_greeks" => {
                params.ensure_allowed(&["greeksType"])?;
                self.post_request(
                    ACCOUNT_SET_GREEKS,
                    Value::Object(params.required_body(&["greeksType"])?),
                )
                .await
            }
            "get_max_withdrawal" => self.dispatch_get_max_withdrawal(method_name, params).await,
            "get_interest_limits" => {
                params.ensure_allowed(&["type", "ccy"])?;
                self.get_request(ACCOUNT_INTEREST_LIMITS, params.only(&["type", "ccy"]))
                    .await
            }
            "spot_manual_borrow_repay" => {
                params.ensure_allowed(&["side", "ccy", "amt"])?;
                let side = params.required("side")?;
                if !["borrow", "repay"].contains(&side) {
                    return Err(crate::DcexError::InvalidInput(
                        "side must be borrow or repay.".to_string(),
                    ));
                }
                self.post_request(
                    ACCOUNT_SPOT_MANUAL_BORROW_REPAY,
                    Value::Object(params.required_body(&["ccy", "side", "amt"])?),
                )
                .await
            }
            "set_spot_auto_repay" => {
                params.ensure_allowed(&["autoRepay"])?;
                let mut body = serde_json::Map::new();
                insert_optional_bool(&mut body, "autoRepay", params.get("autoRepay"))?;
                if !body.contains_key("autoRepay") {
                    return Err(crate::DcexError::InvalidInput(
                        "missing required parameter: autoRepay".to_string(),
                    ));
                }
                self.post_request(ACCOUNT_SET_AUTO_REPAY, Value::Object(body))
                    .await
            }
            "get_spot_borrow_repay_history" => {
                params.ensure_allowed(&["ccy", "type", "after", "before", "limit"])?;
                self.get_request(
                    ACCOUNT_SPOT_BORROW_REPAY_HISTORY,
                    params.only(&["ccy", "type", "after", "before", "limit"]),
                )
                .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
