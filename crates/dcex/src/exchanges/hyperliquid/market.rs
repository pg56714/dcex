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
                params.ensure_allowed(&["dex"])?;
                let mut payload = json!({"type": "meta"});
                insert_optional_string(&mut payload, "dex", optional_nonempty(&params, "dex")?);
                payload
            }
            "get_perp_dexs" => {
                params.ensure_allowed(&[])?;
                json!({"type": "perpDexs"})
            }
            "get_spot_meta" => {
                params.ensure_allowed(&[])?;
                json!({"type": "spotMeta"})
            }
            "get_meta_and_asset_ctxs" => {
                params.ensure_allowed(&["dex"])?;
                let mut payload = json!({"type": "metaAndAssetCtxs"});
                insert_optional_string(&mut payload, "dex", optional_nonempty(&params, "dex")?);
                payload
            }
            "get_spot_meta_and_asset_ctxs" => {
                params.ensure_allowed(&[])?;
                json!({"type": "spotMetaAndAssetCtxs"})
            }
            "get_l2book" => {
                params.ensure_allowed(&["product_symbol", "nSigFigs", "mantissa"])?;
                let n_sig_figs = params.optional_u64("nSigFigs")?;
                if let Some(value) = n_sig_figs {
                    if ![2, 3, 4, 5].contains(&value) {
                        return Err(DcexError::InvalidInput(
                            "Hyperliquid nSigFigs must be 2, 3, 4, or 5".to_string(),
                        ));
                    }
                }
                let mantissa = params.optional_u64("mantissa")?;
                if let Some(value) = mantissa {
                    if n_sig_figs != Some(5) || ![1, 2, 5].contains(&value) {
                        return Err(DcexError::InvalidInput(
                            "Hyperliquid mantissa must be 1, 2, or 5 and requires nSigFigs=5"
                                .to_string(),
                        ));
                    }
                }
                let mut payload = json!({
                    "type": "l2Book",
                    "coin": self.coin(params.required("product_symbol")?)?,
                });
                insert_optional_unsigned(&mut payload, "nSigFigs", n_sig_figs);
                insert_optional_unsigned(&mut payload, "mantissa", mantissa);
                payload
            }
            "get_candle_snapshot" => {
                params.ensure_allowed(&["product_symbol", "interval", "startTime", "endTime"])?;
                let interval = params.required_one_of(
                    "interval",
                    &[
                        "1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "8h", "12h", "1d", "3d",
                        "1w", "1M",
                    ],
                )?;
                let start_time = params.required_u64("startTime")?;
                let end_time = params.required_u64("endTime")?;
                if end_time < start_time {
                    return Err(DcexError::InvalidInput(
                        "Hyperliquid endTime must be greater than or equal to startTime"
                            .to_string(),
                    ));
                }
                let request = json!({
                    "coin": self.coin(params.required("product_symbol")?)?,
                    "interval": interval,
                    "startTime": start_time,
                    "endTime": end_time,
                });
                json!({
                    "type": "candleSnapshot",
                    "req": request,
                })
            }
            "get_funding_rate_history" => {
                params.ensure_allowed(&["product_symbol", "startTime", "endTime"])?;
                let start_time = params.required_u64("startTime")?;
                let end_time = params.optional_u64("endTime")?;
                if end_time.is_some_and(|end_time| end_time < start_time) {
                    return Err(DcexError::InvalidInput(
                        "Hyperliquid endTime must be greater than or equal to startTime"
                            .to_string(),
                    ));
                }
                let mut payload = json!({
                    "type": "fundingHistory",
                    "coin": self.coin(params.required("product_symbol")?)?,
                    "startTime": start_time,
                });
                insert_optional_unsigned(&mut payload, "endTime", end_time);
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

    pub(super) async fn get_meta_and_asset_ctxs_raw(
        &self,
        dex: Option<&str>,
    ) -> Result<ValidatedResponse> {
        let mut payload = json!({"type": "metaAndAssetCtxs"});
        insert_optional_string(&mut payload, "dex", dex);
        self.info_payload(payload).await
    }
}

fn optional_nonempty<'a>(params: &'a HyperliquidParams, key: &str) -> Result<Option<&'a str>> {
    params.get(key).map(|_| params.required(key)).transpose()
}

fn insert_optional_string(payload: &mut Value, key: &str, value: Option<&str>) {
    if let Some(value) = value {
        if let Some(object) = payload.as_object_mut() {
            object.insert(key.to_string(), Value::String(value.to_string()));
        }
    }
}

fn insert_optional_unsigned(payload: &mut Value, key: &str, value: Option<u64>) {
    if let Some(value) = value {
        if let Some(object) = payload.as_object_mut() {
            object.insert(key.to_string(), Value::Number(value.into()));
        }
    }
}
