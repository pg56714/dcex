use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::Result;

use super::client::BitmexClient;
use super::endpoints::*;
use super::params::{
    insert_optional_number, insert_optional_string, validate_bool, validate_enum, validate_i64,
    validate_json_object, validate_number, validate_u64_range, BitmexParams,
};

const GET_POSITION_KEYS: &[&str] = &[
    "filter",
    "columns",
    "count",
    "targetAccountId",
    "targetAccountIds",
    "targetAccountIds[]",
];
const MARGINING_MODE_KEYS: &[&str] = &["targetAccountId", "targetAccountIds", "targetAccountIds[]"];
const MARGIN_KEYS: &[&str] = &[
    "currency",
    "targetAccountId",
    "targetAccountIds",
    "targetAccountIds[]",
];

impl BitmexClient {
    pub(super) async fn position_private_request(
        &self,
        method_name: &str,
        params: &BitmexParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_positions" => {
                params.ensure_allowed(GET_POSITION_KEYS)?;
                validate_json_object(params, "filter")?;
                validate_u64_range(params, "count", 0, i32::MAX as u64)?;
                validate_i64(params, "targetAccountId")?;
                self.get_private(GET_POSITIONS, params.only(GET_POSITION_KEYS))
                    .await
            }
            "switch_mode" => {
                params.ensure_allowed(&["product_symbol", "symbol", "enabled"])?;
                validate_bool(params, "enabled")?;
                let mut body = params.body(&[], &[], &["enabled"], &[]);
                self.insert_required_product_symbol(&mut body, params)?;
                self.private_json(HttpMethod::Post, SWITCH_MODE, Value::Object(body))
                    .await
            }
            "set_leverage" => {
                params.ensure_allowed(&[
                    "product_symbol",
                    "symbol",
                    "leverage",
                    "targetAccountId",
                ])?;
                params.required("leverage")?;
                validate_number(params, "leverage")?;
                validate_leverage(params)?;
                validate_i64(params, "targetAccountId")?;
                let mut body = params.body(&[], &["leverage", "targetAccountId"], &[], &[]);
                self.insert_required_product_symbol(&mut body, params)?;
                self.private_json(HttpMethod::Post, LEVERAGE, Value::Object(body))
                    .await
            }
            "set_margining_mode" => {
                params.ensure_allowed(&["multi_asset", "marginingMode", "targetAccountId"])?;
                validate_bool(params, "multi_asset")?;
                validate_enum(params, "marginingMode", &["", "MultiAsset"])?;
                validate_number(params, "targetAccountId")?;
                let mut body = serde_json::Map::new();
                if params
                    .get("multi_asset")
                    .is_some_and(|value| matches!(value, "true" | "True"))
                {
                    body.insert(
                        "marginingMode".to_string(),
                        Value::String("MultiAsset".to_string()),
                    );
                }
                insert_optional_string(&mut body, "marginingMode", params.get("marginingMode"));
                insert_optional_number(&mut body, "targetAccountId", params.get("targetAccountId"));
                self.private_json(HttpMethod::Post, MARGINING_MODE, Value::Object(body))
                    .await
            }
            "get_margining_mode" => {
                params.ensure_allowed(MARGINING_MODE_KEYS)?;
                validate_i64(params, "targetAccountId")?;
                self.get_private(MARGINING_MODE, params.only(MARGINING_MODE_KEYS))
                    .await
            }
            "get_margin" => {
                params.ensure_allowed(MARGIN_KEYS)?;
                validate_i64(params, "targetAccountId")?;
                self.get_private(GET_MARGIN, params.only(MARGIN_KEYS)).await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}

fn validate_leverage(params: &BitmexParams) -> Result<()> {
    let Some(value) = params.get("leverage") else {
        return Ok(());
    };
    let leverage = value.parse::<f64>().map_err(|_| {
        crate::DcexError::InvalidInput("BitMEX leverage must be a number".to_string())
    })?;
    if leverage == 0.0 || (0.01..=100.0).contains(&leverage) {
        return Ok(());
    }
    Err(crate::DcexError::InvalidInput(
        "BitMEX leverage must be 0 or between 0.01 and 100".to_string(),
    ))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn leverage_matches_documented_range() {
        for value in ["0", "0.01", "100"] {
            let params =
                BitmexParams::from_pairs(vec![("leverage".to_string(), value.to_string())]);
            assert!(validate_leverage(&params).is_ok());
        }
        for value in ["-1", "0.001", "100.01"] {
            let params =
                BitmexParams::from_pairs(vec![("leverage".to_string(), value.to_string())]);
            assert!(validate_leverage(&params).is_err());
        }
    }
}
