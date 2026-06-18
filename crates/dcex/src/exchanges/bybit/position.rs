use serde_json::{Map, Value};

use super::client::BybitClient;
use super::endpoints::*;
use super::params::{insert_optional_string, push_optional, BybitParams};
use crate::exchange::ValidatedResponse;
use crate::Result;

impl BybitClient {
    pub(super) async fn position_private_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_positions" => self.get_positions_from_params(&params).await,
            "set_leverage" => {
                let product_symbol = params.required("product_symbol")?;
                let mut body = Map::new();
                self.insert_symbol_category(&mut body, product_symbol)?;
                body.insert(
                    "buyLeverage".to_string(),
                    Value::String(params.required("leverage")?.to_string()),
                );
                body.insert(
                    "sellLeverage".to_string(),
                    Value::String(params.required("leverage")?.to_string()),
                );
                self.post_request(SET_LEVERAGE, body).await
            }
            "switch_position_mode" => {
                let mut body = Map::new();
                body.insert("category".to_string(), Value::String("linear".to_string()));
                body.insert(
                    "mode".to_string(),
                    Value::Number(params.i64_required("mode")?.into()),
                );
                if let Some(product_symbol) = params.get("product_symbol") {
                    body.insert(
                        "symbol".to_string(),
                        Value::String(self.exchange_symbol(product_symbol)?),
                    );
                }
                insert_optional_string(&mut body, "coin", params.get("coin"));
                self.post_request(SWITCH_POSITION_MODE, body).await
            }
            "get_closed_pnl" => self.get_closed_pnl_from_params(&params).await,
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }

    async fn get_positions_from_params(&self, params: &BybitParams) -> Result<ValidatedResponse> {
        let mut query = vec![
            (
                "category".to_string(),
                params.get("category").unwrap_or("linear").to_string(),
            ),
            (
                "limit".to_string(),
                params.get("limit").unwrap_or("20").to_string(),
            ),
        ];
        if let Some(product_symbol) = params.get("product_symbol") {
            self.push_symbol_category(&mut query, product_symbol, true)?;
        }
        push_optional(&mut query, "settleCoin", params.get("settleCoin"));
        self.get_request(GET_POSITIONS, query).await
    }

    async fn get_closed_pnl_from_params(&self, params: &BybitParams) -> Result<ValidatedResponse> {
        let mut query = vec![
            (
                "category".to_string(),
                params.get("category").unwrap_or("linear").to_string(),
            ),
            (
                "limit".to_string(),
                params.get("limit").unwrap_or("20").to_string(),
            ),
        ];
        if let Some(product_symbol) = params.get("product_symbol") {
            self.push_symbol_category(&mut query, product_symbol, true)?;
        }
        push_optional(&mut query, "startTime", params.get("startTime"));
        self.get_request(GET_CLOSED_PNL, query).await
    }
}
