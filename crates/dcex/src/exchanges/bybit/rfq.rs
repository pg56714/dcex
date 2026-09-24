use serde_json::{Map, Value};

use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::BybitClient;
use super::endpoints::*;
use super::params::{
    insert_optional_bool, insert_optional_i64, insert_optional_string, require_one_identifier,
    string_body, BybitParams,
};

const RFQ_STATUSES: &[&str] = &[
    "Active",
    "PendingFill",
    "Canceled",
    "Filled",
    "Expired",
    "Failed",
];

impl BybitClient {
    pub(super) async fn rfq_private_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_rfq_public_trades" => {
                validate_limit(params)?;
                validate_time_range(params, 30)?;
                self.get_request(
                    RFQ_PUBLIC_TRADES,
                    params.only(&["startTime", "endTime", "limit", "cursor"]),
                )
                .await
            }
            "get_rfq_config" => self.get_request(RFQ_CONFIG, Vec::new()).await,
            "create_rfq" => {
                self.post_request(CREATE_RFQ, create_rfq_body(params)?)
                    .await
            }
            "cancel_rfq" => {
                require_one_identifier(params, &["rfqId", "rfqLinkId"])?;
                self.post_request(
                    CANCEL_RFQ,
                    optional_string_body(params, &["rfqId", "rfqLinkId"]),
                )
                .await
            }
            "cancel_all_rfqs" => self.post_request(CANCEL_ALL_RFQS, Map::new()).await,
            "accept_other_rfq_quote" => {
                self.post_request(
                    ACCEPT_OTHER_RFQ_QUOTE,
                    string_body(&[("rfqId", params.required("rfqId")?)]),
                )
                .await
            }
            "create_rfq_quote" => {
                self.post_request(CREATE_RFQ_QUOTE, create_quote_body(params)?)
                    .await
            }
            "execute_rfq_quote" => {
                let side = params.required("quoteSide")?;
                validate_enum("quoteSide", side, &["Buy", "Sell"])?;
                let mut body = string_body(&[
                    ("rfqId", params.required("rfqId")?),
                    ("quoteId", params.required("quoteId")?),
                    ("quoteSide", side),
                ]);
                insert_optional_bool(&mut body, "isHedge", params.get("isHedge"))?;
                self.post_request(EXECUTE_RFQ_QUOTE, body).await
            }
            "cancel_rfq_quote" => {
                require_one_identifier(params, &["quoteId", "quoteLinkId", "rfqId"])?;
                self.post_request(
                    CANCEL_RFQ_QUOTE,
                    optional_string_body(params, &["quoteId", "quoteLinkId", "rfqId"]),
                )
                .await
            }
            "cancel_all_rfq_quotes" => self.post_request(CANCEL_ALL_RFQ_QUOTES, Map::new()).await,
            "get_realtime_rfqs" => {
                validate_trader_type(params)?;
                self.get_request(
                    RFQ_REALTIME,
                    params.only(&["rfqId", "rfqLinkId", "traderType"]),
                )
                .await
            }
            "get_rfqs" => {
                validate_trader_type(params)?;
                validate_status(params, RFQ_STATUSES)?;
                validate_limit(params)?;
                self.get_request(
                    RFQ_LIST,
                    params.only(&[
                        "rfqId",
                        "rfqLinkId",
                        "traderType",
                        "status",
                        "limit",
                        "cursor",
                    ]),
                )
                .await
            }
            "get_rfq_details" => {
                validate_trader_type(params)?;
                validate_status(params, RFQ_STATUSES)?;
                validate_limit(params)?;
                validate_ordered_time_range(params)?;
                self.get_request(
                    RFQ_DETAIL_LIST,
                    params.only(&[
                        "rfqId",
                        "rfqLinkId",
                        "status",
                        "traderType",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
                    ]),
                )
                .await
            }
            "get_realtime_rfq_quotes" => {
                validate_trader_type(params)?;
                self.get_request(
                    RFQ_QUOTE_REALTIME,
                    params.only(&["rfqId", "quoteId", "quoteLinkId", "traderType"]),
                )
                .await
            }
            "get_rfq_quotes" => {
                validate_trader_type(params)?;
                validate_status(params, RFQ_STATUSES)?;
                validate_limit(params)?;
                self.get_request(
                    RFQ_QUOTE_LIST,
                    params.only(&[
                        "rfqId",
                        "quoteId",
                        "quoteLinkId",
                        "traderType",
                        "status",
                        "limit",
                        "cursor",
                    ]),
                )
                .await
            }
            "get_rfq_trade_history" => {
                validate_trader_type(params)?;
                validate_status(params, &["Filled", "Failed"])?;
                validate_limit(params)?;
                self.get_request(
                    RFQ_TRADE_LIST,
                    params.only(&[
                        "rfqId",
                        "rfqLinkId",
                        "quoteId",
                        "quoteLinkId",
                        "traderType",
                        "status",
                        "limit",
                        "cursor",
                    ]),
                )
                .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}

fn create_rfq_body(params: &BybitParams) -> Result<Map<String, Value>> {
    let counterparties = required_non_empty_array(params, "counterparties")?;
    let legs = required_non_empty_array(params, "list")?;
    validate_link_id(params, "rfqLinkId")?;

    let mut body = Map::new();
    body.insert("counterparties".to_string(), counterparties);
    body.insert("list".to_string(), legs);
    insert_optional_string(&mut body, "rfqLinkId", params.get("rfqLinkId"));
    insert_optional_bool(&mut body, "anonymous", params.get("anonymous"))?;
    insert_optional_string(&mut body, "strategyType", params.get("strategyType"));
    insert_optional_json(&mut body, params, "hedge")?;
    Ok(body)
}

fn create_quote_body(params: &BybitParams) -> Result<Map<String, Value>> {
    validate_link_id(params, "quoteLinkId")?;
    let buy = optional_array(params, "quoteBuyList")?;
    let sell = optional_array(params, "quoteSellList")?;
    if buy.as_ref().is_none_or(is_empty_array) && sell.as_ref().is_none_or(is_empty_array) {
        return Err(DcexError::InvalidInput(
            "quoteBuyList or quoteSellList must contain at least one quote".to_string(),
        ));
    }

    if let Some(value) = params.get("expireIn") {
        let seconds = value.parse::<i64>().map_err(|error| {
            DcexError::InvalidInput(format!("invalid integer parameter expireIn: {error}"))
        })?;
        if !(10..=120).contains(&seconds) {
            return Err(DcexError::InvalidInput(
                "expireIn must be between 10 and 120".to_string(),
            ));
        }
    }

    let mut body = string_body(&[("rfqId", params.required("rfqId")?)]);
    insert_optional_string(&mut body, "quoteLinkId", params.get("quoteLinkId"));
    insert_optional_bool(&mut body, "anonymous", params.get("anonymous"))?;
    insert_optional_i64(&mut body, "expireIn", params.get("expireIn"))?;
    if let Some(value) = buy {
        body.insert("quoteBuyList".to_string(), value);
    }
    if let Some(value) = sell {
        body.insert("quoteSellList".to_string(), value);
    }
    Ok(body)
}

fn optional_string_body(params: &BybitParams, keys: &[&str]) -> Map<String, Value> {
    let mut body = Map::new();
    for key in keys {
        insert_optional_string(&mut body, key, params.get(key));
    }
    body
}

fn insert_optional_json(
    body: &mut Map<String, Value>,
    params: &BybitParams,
    key: &str,
) -> Result<()> {
    if params.get(key).is_some() {
        body.insert(key.to_string(), params.json_required(key)?);
    }
    Ok(())
}

fn required_non_empty_array(params: &BybitParams, key: &str) -> Result<Value> {
    let value = params.json_required(key)?;
    if !value.as_array().is_some_and(|items| !items.is_empty()) {
        return Err(DcexError::InvalidInput(format!(
            "{key} must be a non-empty JSON array"
        )));
    }
    Ok(value)
}

fn optional_array(params: &BybitParams, key: &str) -> Result<Option<Value>> {
    let Some(_) = params.get(key) else {
        return Ok(None);
    };
    let value = params.json_required(key)?;
    if !value.is_array() {
        return Err(DcexError::InvalidInput(format!(
            "{key} must be a JSON array"
        )));
    }
    Ok(Some(value))
}

fn is_empty_array(value: &Value) -> bool {
    value.as_array().is_some_and(Vec::is_empty)
}

fn validate_link_id(params: &BybitParams, key: &str) -> Result<()> {
    if let Some(value) = params.get(key) {
        if !(1..=32).contains(&value.len())
            || !value
                .chars()
                .all(|character| character.is_ascii_alphanumeric())
        {
            return Err(DcexError::InvalidInput(format!(
                "{key} must contain 1 to 32 ASCII letters or numbers"
            )));
        }
    }
    Ok(())
}

fn validate_trader_type(params: &BybitParams) -> Result<()> {
    if let Some(value) = params.get("traderType") {
        validate_enum("traderType", value, &["quote", "request"])?;
    }
    Ok(())
}

fn validate_status(params: &BybitParams, values: &[&str]) -> Result<()> {
    if let Some(value) = params.get("status") {
        validate_enum("status", value, values)?;
    }
    Ok(())
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

fn validate_limit(params: &BybitParams) -> Result<()> {
    if let Some(value) = params.get("limit") {
        let limit = value.parse::<u16>().map_err(|error| {
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

fn validate_ordered_time_range(params: &BybitParams) -> Result<()> {
    if let (Some(start), Some(end)) = (params.get("startTime"), params.get("endTime")) {
        let start = parse_time("startTime", start)?;
        let end = parse_time("endTime", end)?;
        if end < start {
            return Err(DcexError::InvalidInput(
                "endTime must not be earlier than startTime".to_string(),
            ));
        }
    }
    Ok(())
}

fn validate_time_range(params: &BybitParams, maximum_days: u64) -> Result<()> {
    validate_ordered_time_range(params)?;
    if let (Some(start), Some(end)) = (params.get("startTime"), params.get("endTime")) {
        let start = parse_time("startTime", start)?;
        let end = parse_time("endTime", end)?;
        let maximum = maximum_days * 24 * 60 * 60 * 1_000;
        if end - start > maximum {
            return Err(DcexError::InvalidInput(format!(
                "startTime and endTime must define a range no longer than {maximum_days} days"
            )));
        }
    }
    Ok(())
}

fn parse_time(key: &str, value: &str) -> Result<u64> {
    value.parse::<u64>().map_err(|error| {
        DcexError::InvalidInput(format!("invalid integer parameter {key}: {error}"))
    })
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
    fn create_rfq_requires_non_empty_json_arrays() {
        assert!(create_rfq_body(&params(&[("counterparties", "[]"), ("list", "[]")])).is_err());
        assert!(create_rfq_body(&params(&[
            ("counterparties", "[\"desk\"]"),
            ("list", "[{\"category\":\"linear\"}]")
        ]))
        .is_ok());
    }

    #[test]
    fn create_quote_requires_at_least_one_side() {
        assert!(create_quote_body(&params(&[("rfqId", "1")])).is_err());
        assert!(create_quote_body(&params(&[
            ("rfqId", "1"),
            ("quoteBuyList", "[{\"price\":\"1\"}]")
        ]))
        .is_ok());
    }

    #[test]
    fn public_history_rejects_ranges_over_thirty_days() {
        let value = params(&[("startTime", "0"), ("endTime", "2592000001")]);
        assert!(validate_time_range(&value, 30).is_err());
    }
}
