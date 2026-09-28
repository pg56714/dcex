use std::collections::BTreeMap;

use serde_json::Value;

use super::client::ArcusClient;
use super::endpoints::public_path;
use super::params::required;
use crate::exchange::ValidatedResponse;
use crate::http::{HttpMethod, HttpRequest};
use crate::{DcexError, Result};

impl ArcusClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        if super::completion::handles(method_name, true) {
            return self.completion_request(method_name, params).await;
        }
        if super::metadata::handles(method_name, true) {
            return self.metadata_request(method_name, params).await;
        }
        if method_name == "get_api_keys" {
            return self.onboarding_request(method_name, params).await;
        }
        let mut collected: BTreeMap<String, String> = BTreeMap::new();
        for (key, value) in params {
            if let Some(previous) = collected.get_mut(&key) {
                if method_name == "get_order_history" && key == "status" {
                    previous.push(',');
                    previous.push_str(&value);
                } else {
                    return Err(DcexError::InvalidInput(format!(
                        "duplicate Arcus parameter: {key}"
                    )));
                }
            } else {
                collected.insert(key, value);
            }
        }
        let mut params = collected;
        super::query_validation::validate(method_name, &params)?;
        let path = public_path(method_name)?;
        let path = if matches!(method_name, "get_bbo" | "get_l2_orderbook") {
            let market = required(&params, "market")?;
            if market.is_empty()
                || !market
                    .bytes()
                    .all(|byte| byte.is_ascii_alphanumeric() || byte == b'-')
            {
                return Err(DcexError::InvalidInput(
                    "Arcus market path must be a market display name".into(),
                ));
            }
            format!("{path}/{market}")
        } else if method_name == "get_order_status" {
            let order_id = required(&params, "order_id")?;
            if order_id.is_empty()
                || !order_id
                    .bytes()
                    .all(|byte| byte.is_ascii_alphanumeric() || byte == b'-')
            {
                return Err(DcexError::InvalidInput("invalid Arcus order ID".into()));
            }
            format!("{path}/{order_id}")
        } else if matches!(method_name, "get_trade" | "get_fill") {
            let trade_id = required(&params, "trade_id")?;
            if trade_id.is_empty()
                || !trade_id
                    .bytes()
                    .all(|byte| byte.is_ascii_alphanumeric() || byte == b'-')
            {
                return Err(DcexError::InvalidInput("invalid Arcus trade ID".into()));
            }
            format!("{path}/{trade_id}")
        } else {
            path.to_string()
        };
        if matches!(method_name, "get_bbo" | "get_l2_orderbook") {
            params.remove("market");
        } else if method_name == "get_order_status" {
            params.remove("order_id");
        } else if matches!(method_name, "get_trade" | "get_fill") {
            params.remove("trade_id");
        }
        let mut request = HttpRequest::new(HttpMethod::Get, &self.base_url, path);
        request.query = params.into_iter().collect();
        if let Some(api_key) = &self.api_key {
            request = request.header("X-API-Key", api_key);
        }
        self.execute(request).await
    }

    pub(super) async fn market_info(&self, product_symbol: &str) -> Result<Value> {
        let response = self.public_request("get_markets", vec![]).await?;
        response.data["markets"]
            .as_array()
            .and_then(|markets| {
                markets.iter().find(|market| {
                    let id_match = market["marketId"]
                        .as_u64()
                        .is_some_and(|id| id.to_string() == product_symbol);
                    let symbol_match = market["marketDisplayName"].as_str().is_some_and(|symbol| {
                        symbol == product_symbol || format!("{symbol}-SWAP") == product_symbol
                    });
                    id_match || symbol_match
                })
            })
            .cloned()
            .ok_or_else(|| {
                DcexError::InvalidInput(format!("unknown Arcus market: {product_symbol}"))
            })
    }
}
