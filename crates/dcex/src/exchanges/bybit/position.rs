use serde_json::{Map, Value};

use super::client::BybitClient;
use super::endpoints::*;
use super::params::{insert_optional_string, push_optional, require_one_identifier, BybitParams};
use crate::exchange::ValidatedResponse;
use crate::Result;

impl BybitClient {
    pub(super) async fn position_private_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "get_positions" => self.get_positions_from_params(params).await,
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
                let body = self.switch_position_mode_body_from_params(params)?;
                self.post_request(SWITCH_POSITION_MODE, body).await
            }
            "get_closed_pnl" => self.get_closed_pnl_from_params(params).await,
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }

    async fn get_positions_from_params(&self, params: &BybitParams) -> Result<ValidatedResponse> {
        let query = self.get_positions_query_from_params(params)?;
        self.get_request(GET_POSITIONS, query).await
    }

    fn switch_position_mode_body_from_params(
        &self,
        params: &BybitParams,
    ) -> Result<Map<String, Value>> {
        require_one_identifier(params, &["product_symbol", "coin"])?;
        let mut body = Map::new();
        body.insert(
            "category".to_string(),
            Value::String(params.get("category").unwrap_or("linear").to_string()),
        );
        body.insert(
            "mode".to_string(),
            Value::Number(params.i64_required("mode")?.into()),
        );
        if let Some(product_symbol) = params.get("product_symbol") {
            self.insert_symbol_category(&mut body, product_symbol)?;
        }
        insert_optional_string(&mut body, "coin", params.get("coin"));
        Ok(body)
    }

    fn get_positions_query_from_params(
        &self,
        params: &BybitParams,
    ) -> Result<Vec<(String, String)>> {
        let category = params.get("category").unwrap_or("linear");
        let mut query = vec![
            ("category".to_string(), category.to_string()),
            (
                "limit".to_string(),
                params.get("limit").unwrap_or("20").to_string(),
            ),
        ];
        if let Some(product_symbol) = params.get("product_symbol") {
            self.push_symbol_category(&mut query, product_symbol, true)?;
        } else if let Some(settle_coin) = params.get("settleCoin") {
            query.push(("settleCoin".to_string(), settle_coin.to_string()));
        } else if category.eq_ignore_ascii_case("linear") {
            query.push(("settleCoin".to_string(), "USDT".to_string()));
        }
        Ok(query)
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

#[cfg(test)]
mod tests {
    use std::time::Duration;

    use super::*;
    use crate::DcexError;

    fn client() -> BybitClient {
        BybitClient::public(5_000, false, Duration::from_secs(1)).expect("client")
    }

    #[test]
    fn positions_default_to_linear_usdt_scope() {
        let query = client()
            .get_positions_query_from_params(&BybitParams::from_pairs(Vec::new()))
            .expect("query");

        assert!(query.contains(&("category".to_string(), "linear".to_string())));
        assert!(query.contains(&("settleCoin".to_string(), "USDT".to_string())));
    }

    #[test]
    fn positions_inverse_symbol_has_one_inferred_category() {
        let query = client()
            .get_positions_query_from_params(&BybitParams::from_pairs(vec![(
                "product_symbol".to_string(),
                "BTC-USD-SWAP".to_string(),
            )]))
            .expect("query");

        assert!(query.contains(&("category".to_string(), "inverse".to_string())));
        assert_eq!(query.iter().filter(|(key, _)| key == "category").count(), 1);
    }

    #[test]
    fn switch_position_mode_requires_symbol_or_coin() {
        let error = client()
            .switch_position_mode_body_from_params(&BybitParams::from_pairs(vec![(
                "mode".to_string(),
                "0".to_string(),
            )]))
            .expect_err("missing selector must fail");

        assert_eq!(
            error,
            DcexError::InvalidInput("one of product_symbol, coin is required".to_string())
        );
    }

    #[test]
    fn switch_position_mode_infers_inverse_category() {
        let body = client()
            .switch_position_mode_body_from_params(&BybitParams::from_pairs(vec![
                ("mode".to_string(), "0".to_string()),
                ("product_symbol".to_string(), "BTC-USD-20261225".to_string()),
            ]))
            .expect("body");

        assert_eq!(
            body.get("category"),
            Some(&Value::String("inverse".to_string()))
        );
        assert_eq!(
            body.get("symbol"),
            Some(&Value::String("BTCUSD".to_string()))
        );
    }
}
