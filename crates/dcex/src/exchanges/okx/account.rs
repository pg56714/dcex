use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::Result;

use super::client::OkxClient;
use super::endpoints::*;
use super::params::{insert_optional_string, push_optional, push_optional_owned, OkxParams};

impl OkxClient {
    pub(super) async fn account_private_request(
        &self,
        method_name: &str,
        params: &OkxParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_account_instruments" => {
                let mut query = vec![(
                    "instType".to_string(),
                    params.required("instType")?.to_string(),
                )];
                self.push_inst_id(&mut query, params, "product_symbol")?;
                push_optional(&mut query, "instFamily", params.get("instFamily"));
                push_optional(&mut query, "uly", params.get("uly"));
                self.get_request(ACCOUNT_INSTRUMENTS, query).await
            }
            "get_account_balance" => {
                let mut query = Vec::new();
                push_optional_owned(&mut query, "ccy", params.csv("ccy")?);
                self.get_request(ACCOUNT_BALANCE, query).await
            }
            "get_positions" => {
                let mut query = Vec::new();
                push_optional(&mut query, "instType", params.get("instType"));
                self.push_inst_id(&mut query, params, "product_symbol")?;
                self.get_request(ACCOUNT_POSITIONS, query).await
            }
            "get_positions_history" => {
                let mut query =
                    params.only(&["instType", "mgnMode", "type", "after", "before", "limit"]);
                self.push_inst_id(&mut query, params, "product_symbol")?;
                self.get_request(ACCOUNT_POSITIONS_HISTORY, query).await
            }
            "get_position_risk" => {
                self.get_request(ACCOUNT_POSITION_RISK, params.only(&["instType"]))
                    .await
            }
            "get_account_bills" => {
                let mut query = params.only(&[
                    "instType", "ccy", "mgnMode", "ctType", "type", "subType", "begin", "end",
                    "limit",
                ]);
                self.push_inst_id(&mut query, params, "product_symbol")?;
                self.get_request(ACCOUNT_BILLS, query).await
            }
            "get_account_bills_archive" => {
                let mut query = params.only(&[
                    "instType", "ccy", "mgnMode", "ctType", "type", "subType", "begin", "end",
                    "limit",
                ]);
                self.push_inst_id(&mut query, params, "product_symbol")?;
                self.get_request(ACCOUNT_BILLS_ARCHIVE, query).await
            }
            "get_account_bills_history_archive" => {
                self.get_request(
                    ACCOUNT_BILLS_HISTORY_ARCHIVE,
                    params.required_only(&["year", "quarter"])?,
                )
                .await
            }
            "post_account_bills_history_archive" => {
                self.post_request(
                    ACCOUNT_BILLS_HISTORY_ARCHIVE,
                    Value::Object(params.required_body(&["year", "quarter"])?),
                )
                .await
            }
            "get_account_config" => self.get_request(ACCOUNT_CONFIG, Vec::new()).await,
            "set_position_mode" => {
                self.post_request(
                    ACCOUNT_SET_POSITION_MODE,
                    Value::Object(params.required_body(&["posMode"])?),
                )
                .await
            }
            "set_leverage" => {
                let mut body = params.required_body(&["lever", "mgnMode"])?;
                self.insert_inst_id(&mut body, params, "product_symbol")?;
                insert_optional_string(&mut body, "ccy", params.get("ccy"));
                insert_optional_string(&mut body, "posSide", params.get("posSide"));
                self.post_request(ACCOUNT_SET_LEVERAGE, Value::Object(body))
                    .await
            }
            "get_max_order_size" => {
                let mut query =
                    vec![("tdMode".to_string(), params.required("tdMode")?.to_string())];
                self.push_required_inst_id(&mut query, params)?;
                push_optional(&mut query, "ccy", params.get("ccy"));
                push_optional(&mut query, "px", params.get("px"));
                push_optional(&mut query, "leverage", params.get("leverage"));
                self.get_request(ACCOUNT_MAX_SIZE, query).await
            }
            "get_max_avail_size" => {
                let mut query =
                    vec![("tdMode".to_string(), params.required("tdMode")?.to_string())];
                self.push_required_inst_id(&mut query, params)?;
                push_optional(&mut query, "ccy", params.get("ccy"));
                push_optional(&mut query, "reduceOnly", params.get("reduceOnly"));
                push_optional(&mut query, "px", params.get("px"));
                self.get_request(ACCOUNT_MAX_AVAIL_SIZE, query).await
            }
            "get_leverage" => {
                let mut query = vec![(
                    "mgnMode".to_string(),
                    params.required("mgnMode")?.to_string(),
                )];
                self.push_inst_id(&mut query, params, "product_symbol")?;
                push_optional(&mut query, "ccy", params.get("ccy"));
                self.get_request(ACCOUNT_LEVERAGE_INFO, query).await
            }
            "get_adjust_leverage" => {
                let mut query = params.required_only(&["instType", "mgnMode", "lever"])?;
                self.push_inst_id(&mut query, params, "product_symbol")?;
                push_optional(&mut query, "ccy", params.get("ccy"));
                push_optional(&mut query, "posSide", params.get("posSide"));
                self.get_request(ACCOUNT_ADJUST_LEVERAGE_INFO, query).await
            }
            "get_max_loan" => {
                let mut query = vec![(
                    "mgnMode".to_string(),
                    params.required("mgnMode")?.to_string(),
                )];
                self.push_inst_id(&mut query, params, "product_symbol")?;
                push_optional(&mut query, "ccy", params.get("ccy"));
                push_optional(&mut query, "mgnCcy", params.get("mgnCcy"));
                self.get_request(ACCOUNT_MAX_LOAN, query).await
            }
            "get_fee_rates" => {
                let mut query = vec![(
                    "instType".to_string(),
                    params.required("instType")?.to_string(),
                )];
                push_optional(&mut query, "ruleType", params.get("ruleType"));
                self.push_inst_id(&mut query, params, "product_symbol")?;
                push_optional(&mut query, "uly", params.get("uly"));
                push_optional(&mut query, "instFamily", params.get("instFamily"));
                self.get_request(ACCOUNT_TRADE_FEE, query).await
            }
            "get_interest_accrued" => {
                let mut query = params.only(&["ccy", "mgnMode", "after", "before", "limit"]);
                self.push_inst_id(&mut query, params, "product_symbol")?;
                self.get_request(ACCOUNT_INTEREST_ACCRUED, query).await
            }
            "get_interest_rate" => {
                self.get_request(ACCOUNT_INTEREST_RATE, params.only(&["ccy"]))
                    .await
            }
            "set_greeks" => {
                self.post_request(
                    ACCOUNT_SET_GREEKS,
                    Value::Object(params.required_body(&["greeksType"])?),
                )
                .await
            }
            "get_max_withdrawal" => {
                let mut query = Vec::new();
                push_optional_owned(&mut query, "ccy", params.csv("ccy")?);
                self.get_request(ACCOUNT_MAX_WITHDRAWAL, query).await
            }
            "get_interest_limits" => {
                self.get_request(ACCOUNT_INTEREST_LIMITS, params.only(&["ccy"]))
                    .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
