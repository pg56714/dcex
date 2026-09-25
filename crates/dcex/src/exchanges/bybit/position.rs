use serde_json::{Map, Value};

use super::client::BybitClient;
use super::endpoints::*;
use super::params::{insert_optional_string, push_optional, require_one_identifier, BybitParams};
use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

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
            "set_trading_stop" => {
                let body = self.trading_stop_body_from_params(params)?;
                self.post_request(SET_TRADING_STOP, body).await
            }
            "add_position_margin" => {
                let body = self.position_margin_body_from_params(params)?;
                self.post_request(ADD_POSITION_MARGIN, body).await
            }
            "set_auto_add_margin" => {
                let body = self.auto_add_margin_body_from_params(params)?;
                self.post_request(SET_AUTO_ADD_MARGIN, body).await
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

    fn position_index(params: &BybitParams, required: bool) -> Result<Option<i64>> {
        let index = if required || params.get("positionIdx").is_some() {
            Some(params.i64_required("positionIdx")?)
        } else {
            None
        };
        if index.is_some_and(|index| !(0..=2).contains(&index)) {
            return Err(DcexError::InvalidInput(
                "Bybit positionIdx must be 0, 1, or 2".into(),
            ));
        }
        Ok(index)
    }

    fn trading_stop_body_from_params(&self, params: &BybitParams) -> Result<Map<String, Value>> {
        let mut body = Map::new();
        self.insert_symbol_category(&mut body, params.required("product_symbol")?)?;
        let mode = params.required("tpslMode")?;
        if !matches!(mode, "Full" | "Partial") {
            return Err(DcexError::InvalidInput(
                "Bybit tpslMode must be Full or Partial".into(),
            ));
        }
        if body.get("category").and_then(Value::as_str) == Some("option") && mode != "Full" {
            return Err(DcexError::InvalidInput(
                "Bybit option trading stops require Full mode".into(),
            ));
        }
        if !["takeProfit", "stopLoss", "trailingStop"]
            .iter()
            .any(|key| params.get(key).is_some())
        {
            return Err(DcexError::InvalidInput(
                "Bybit trading stop requires a take-profit, stop-loss, or trailing-stop field"
                    .into(),
            ));
        }
        body.insert("tpslMode".into(), Value::String(mode.into()));
        body.insert(
            "positionIdx".into(),
            Value::Number(
                Self::position_index(params, true)?
                    .expect("required")
                    .into(),
            ),
        );
        for key in [
            "takeProfit",
            "stopLoss",
            "trailingStop",
            "tpTriggerBy",
            "slTriggerBy",
            "activePrice",
            "tpOrderType",
            "slOrderType",
            "tpLimitPrice",
            "slLimitPrice",
            "tpSize",
            "slSize",
        ] {
            insert_optional_string(&mut body, key, params.get(key));
        }
        Ok(body)
    }

    fn position_margin_body_from_params(&self, params: &BybitParams) -> Result<Map<String, Value>> {
        let mut body = Map::new();
        self.insert_symbol_category(&mut body, params.required("product_symbol")?)?;
        if !matches!(
            body.get("category").and_then(Value::as_str),
            Some("linear" | "inverse")
        ) {
            return Err(DcexError::InvalidInput(
                "Bybit position margin supports linear or inverse contracts".into(),
            ));
        }
        let margin = params.required("margin")?;
        let absolute = margin.strip_prefix('-').unwrap_or(margin);
        let mut parts = absolute.split('.');
        let whole = parts.next().unwrap_or_default();
        let decimal = parts.next();
        if whole.is_empty()
            || !whole.bytes().all(|byte| byte.is_ascii_digit())
            || decimal.is_some_and(|value| {
                value.is_empty()
                    || value.len() > 4
                    || !value.bytes().all(|byte| byte.is_ascii_digit())
            })
            || parts.next().is_some()
            || absolute.bytes().all(|byte| byte == b'0' || byte == b'.')
        {
            return Err(DcexError::InvalidInput(
                "Bybit margin must be a nonzero decimal with at most 4 places".into(),
            ));
        }
        body.insert("margin".into(), Value::String(margin.into()));
        if let Some(index) = Self::position_index(params, false)? {
            body.insert("positionIdx".into(), Value::Number(index.into()));
        }
        Ok(body)
    }

    fn auto_add_margin_body_from_params(&self, params: &BybitParams) -> Result<Map<String, Value>> {
        let mut body = Map::new();
        self.insert_symbol_category(&mut body, params.required("product_symbol")?)?;
        if body.get("category").and_then(Value::as_str) != Some("linear") {
            return Err(DcexError::InvalidInput(
                "Bybit auto-add margin supports linear contracts only".into(),
            ));
        }
        let enabled = params.i64_required("autoAddMargin")?;
        if !matches!(enabled, 0 | 1) {
            return Err(DcexError::InvalidInput(
                "Bybit autoAddMargin must be 0 or 1".into(),
            ));
        }
        body.insert("autoAddMargin".into(), Value::Number(enabled.into()));
        if let Some(index) = Self::position_index(params, false)? {
            body.insert("positionIdx".into(), Value::Number(index.into()));
        }
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
        } else {
            push_optional(&mut query, "baseCoin", params.get("baseCoin"));
            if let Some(settle_coin) = params.get("settleCoin") {
                query.push(("settleCoin".to_string(), settle_coin.to_string()));
            } else if category.eq_ignore_ascii_case("linear") && params.get("baseCoin").is_none() {
                query.push(("settleCoin".to_string(), "USDT".to_string()));
            }
        }
        push_optional(&mut query, "cursor", params.get("cursor"));
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
        push_optional(&mut query, "endTime", params.get("endTime"));
        push_optional(&mut query, "cursor", params.get("cursor"));
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
                ("product_symbol".to_string(), "BTC-USD-H23-SWAP".to_string()),
            ]))
            .expect("body");

        assert_eq!(
            body.get("category"),
            Some(&Value::String("inverse".to_string()))
        );
        assert_eq!(
            body.get("symbol"),
            Some(&Value::String("BTCUSDH23".to_string()))
        );
    }

    #[test]
    fn trading_stop_builds_canonical_position_body() {
        let body = client()
            .trading_stop_body_from_params(&BybitParams::from_pairs(vec![
                ("product_symbol".into(), "BTC-USDT-SWAP".into()),
                ("tpslMode".into(), "Full".into()),
                ("positionIdx".into(), "0".into()),
                ("takeProfit".into(), "120000".into()),
                ("stopLoss".into(), "90000".into()),
            ]))
            .expect("body");
        assert_eq!(body.get("category"), Some(&Value::String("linear".into())));
        assert_eq!(body.get("symbol"), Some(&Value::String("BTCUSDT".into())));
        assert_eq!(body.get("positionIdx"), Some(&Value::Number(0.into())));
        assert_eq!(body.get("stopLoss"), Some(&Value::String("90000".into())));
        let client = client();
        let request = client.set_trading_stop(
            "BTC-USDT-SWAP",
            "Full",
            0,
            Some("120000"),
            Some("90000"),
            None,
        );
        assert_eq!(request.method_name, "set_trading_stop");
        assert!(request
            .params
            .contains(&("takeProfit".into(), "120000".into())));
        assert!(request
            .params
            .contains(&("stopLoss".into(), "90000".into())));
    }

    #[test]
    fn position_margin_and_auto_add_validate_product_scope() {
        let margin = client()
            .position_margin_body_from_params(&BybitParams::from_pairs(vec![
                ("product_symbol".into(), "BTC-USD-SWAP".into()),
                ("margin".into(), "-10.25".into()),
                ("positionIdx".into(), "2".into()),
            ]))
            .expect("margin body");
        assert_eq!(
            margin.get("category"),
            Some(&Value::String("inverse".into()))
        );
        assert_eq!(margin.get("margin"), Some(&Value::String("-10.25".into())));
        let auto = client()
            .auto_add_margin_body_from_params(&BybitParams::from_pairs(vec![
                ("product_symbol".into(), "BTC-USDT-SWAP".into()),
                ("autoAddMargin".into(), "1".into()),
            ]))
            .expect("auto-add body");
        assert_eq!(auto.get("autoAddMargin"), Some(&Value::Number(1.into())));
        assert!(client()
            .auto_add_margin_body_from_params(&BybitParams::from_pairs(vec![
                ("product_symbol".into(), "BTC-USD-SWAP".into()),
                ("autoAddMargin".into(), "1".into()),
            ]))
            .is_err());
        assert!(client()
            .position_margin_body_from_params(&BybitParams::from_pairs(vec![
                ("product_symbol".into(), "BTC-USDT-SWAP".into()),
                ("margin".into(), "0.0000".into()),
            ]))
            .is_err());
    }
}
