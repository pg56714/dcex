use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::ExtendedClient;
use super::endpoints::*;
use super::params::ExtendedParams;

impl ExtendedClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = ExtendedParams::from_pairs(params);
        let response = match method_name {
            "get_markets" => {
                let mut query = params.only(&["market"]);
                if let Some(product_symbol) = params.get("product_symbol") {
                    query.push(("market".to_string(), self.exchange_symbol(product_symbol)?));
                }
                self.public_get(MARKETS, query).await
            }
            "get_assets" => {
                self.public_get(ASSETS, params.only(&["asset", "type", "collateral"]))
                    .await
            }
            "get_market_stats" | "get_market_statistics" => {
                let market = self.required_market(&params)?;
                self.public_get(&format!("/api/v1/info/markets/{market}/stats"), Vec::new())
                    .await
            }
            "get_order_book" | "get_orderbook" => {
                let market = self.required_market(&params)?;
                self.public_get(
                    &format!("/api/v1/info/markets/{market}/orderbook"),
                    Vec::new(),
                )
                .await
            }
            "get_trades" => {
                let market = self.required_market(&params)?;
                self.public_get(&format!("/api/v1/info/markets/{market}/trades"), Vec::new())
                    .await
            }
            "get_candles" => {
                let market = self.required_market(&params)?;
                let candle_type = params
                    .get("candleType")
                    .or_else(|| params.get("candle_type"))
                    .unwrap_or("trades");
                let interval = params.required("interval")?;
                let limit = params.required("limit")?;
                let mut query = vec![
                    ("interval".to_string(), interval.to_string()),
                    ("limit".to_string(), limit.to_string()),
                ];
                if let Some(end_time) = params.get("endTime") {
                    query.push(("endTime".to_string(), end_time.to_string()));
                }
                self.public_get(
                    &format!("/api/v1/info/candles/{market}/{candle_type}"),
                    query,
                )
                .await
            }
            "get_funding" => {
                let market = self.required_market(&params)?;
                self.public_get(
                    &format!("/api/v1/info/{market}/funding"),
                    params.only(&["startTime", "endTime", "cursor", "limit"]),
                )
                .await
            }
            "get_open_interest" => {
                let market = self.required_market(&params)?;
                self.public_get(
                    &format!("/api/v1/info/{market}/open-interests"),
                    params.only(&["interval", "startTime", "endTime", "limit"]),
                )
                .await
            }
            "get_asset_index_price" => {
                let asset = params.required("asset")?;
                self.public_get(&format!("/api/v1/info/assets/{asset}/price"), Vec::new())
                    .await
            }
            _ => {
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Extended public method: {method_name}"
                )))
            }
        }?;
        Ok(response)
    }

    fn required_market(&self, params: &ExtendedParams) -> Result<String> {
        if let Some(product_symbol) = params.get("product_symbol") {
            return self.exchange_symbol(product_symbol);
        }
        self.exchange_symbol(params.required("market")?)
    }
}
