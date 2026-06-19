use serde_json::{json, Value};

use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::HyperliquidClient;
use super::params::HyperliquidParams;

impl HyperliquidClient {
    pub async fn public_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = HyperliquidParams::from_pairs(params);
        let payload = match method_name {
            "get_meta" => {
                let mut payload = json!({"type": "meta"});
                insert_optional_string(&mut payload, "dex", params.get("dex"));
                payload
            }
            "get_spot_meta" => json!({"type": "spotMeta"}),
            "get_meta_and_asset_ctxs" => json!({"type": "metaAndAssetCtxs"}),
            "get_spot_meta_and_asset_ctxs" => json!({"type": "spotMetaAndAssetCtxs"}),
            "get_l2book" => json!({
                "type": "l2Book",
                "coin": self.coin(params.required("product_symbol")?)?,
            }),
            "get_candle_snapshot" => {
                let mut request = json!({
                    "coin": self.coin(params.required("product_symbol")?)?,
                    "interval": params.required("interval")?,
                    "startTime": params.required_i64("startTime")?,
                });
                insert_optional_integer(&mut request, "endTime", params.optional_i64("endTime")?);
                json!({
                    "type": "candleSnapshot",
                    "req": request,
                })
            }
            "get_funding_rate_history" => {
                let mut payload = json!({
                    "type": "fundingHistory",
                    "coin": self.coin(params.required("product_symbol")?)?,
                    "startTime": params.required_i64("startTime")?,
                });
                insert_optional_integer(&mut payload, "endTime", params.optional_i64("endTime")?);
                payload
            }
            _ => {
                if let Some(response) = self.account_public_request(method_name, &params).await? {
                    return Ok(response);
                }
                if let Some(response) = self.asset_public_request(method_name, &params).await? {
                    return Ok(response);
                }
                return Err(DcexError::InvalidInput(format!(
                    "unsupported Hyperliquid public method: {method_name}"
                )));
            }
        };
        self.info_payload(payload).await
    }

    pub(super) async fn get_meta_and_asset_ctxs(&self) -> Result<ValidatedResponse> {
        self.info_payload(json!({"type": "metaAndAssetCtxs"})).await
    }
}

fn insert_optional_string(payload: &mut Value, key: &str, value: Option<&str>) {
    if let Some(value) = value {
        if let Some(object) = payload.as_object_mut() {
            object.insert(key.to_string(), Value::String(value.to_string()));
        }
    }
}

fn insert_optional_integer(payload: &mut Value, key: &str, value: Option<i64>) {
    if let Some(value) = value {
        if let Some(object) = payload.as_object_mut() {
            object.insert(key.to_string(), Value::Number(value.into()));
        }
    }
}
