use serde_json::Value;

use crate::exchange::ValidatedResponse;
use crate::http::HttpMethod;
use crate::Result;

use super::client::BitmexClient;
use super::endpoints::*;
use super::params::{insert_optional_number, insert_optional_string, BitmexParams};

const GET_POSITION_KEYS: &[&str] = &[
    "filter",
    "columns",
    "count",
    "targetAccountId",
    "targetAccountIds",
];
const MARGINING_MODE_KEYS: &[&str] = &["targetAccountId", "targetAccountIds"];
const MARGIN_KEYS: &[&str] = &["currency", "targetAccountId", "targetAccountIds"];

impl BitmexClient {
    pub(super) async fn position_private_request(
        &self,
        method_name: &str,
        params: &BitmexParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_positions" => {
                self.get_private(GET_POSITIONS, params.only(GET_POSITION_KEYS))
                    .await
            }
            "switch_mode" => {
                let mut body = params.body(&[], &[], &["enabled"], &[]);
                self.insert_required_product_symbol(&mut body, params)?;
                self.private_json(HttpMethod::Post, SWITCH_MODE, Value::Object(body))
                    .await
            }
            "set_leverage" => {
                let mut body = params.body(&[], &["leverage", "targetAccountId"], &[], &[]);
                self.insert_required_product_symbol(&mut body, params)?;
                self.private_json(HttpMethod::Post, LEVERAGE, Value::Object(body))
                    .await
            }
            "set_margining_mode" => {
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
                self.get_private(MARGINING_MODE, params.only(MARGINING_MODE_KEYS))
                    .await
            }
            "get_margin" => self.get_private(GET_MARGIN, params.only(MARGIN_KEYS)).await,
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }
}
