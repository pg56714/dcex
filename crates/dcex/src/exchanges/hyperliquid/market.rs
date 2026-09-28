use serde_json::{Value, json};

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
        if let Some(response) = self.catalog_request(method_name, &params, true).await? {
            return Ok(response);
        }
        let payload = match method_name {
            "get_all_mids" => {
                params.ensure_allowed(&["dex"])?;
                json!({"type":"allMids","dex":params.get("dex").unwrap_or("")})
            }
            "get_active_asset_data" => {
                params.ensure_allowed(&["user", "product_symbol"])?;
                json!({"type":"activeAssetData","user":params.address("user")?,"coin":self.coin(params.required("product_symbol")?)?})
            }
            "get_user_twap_slice_fills" => {
                params.ensure_allowed(&["user"])?;
                json!({"type":"userTwapSliceFills","user":params.address("user")?})
            }

            "get_vault_details" => {
                params.ensure_allowed(&["vaultAddress", "user"])?;
                let mut payload = json!({"type":"vaultDetails"});
                payload["vaultAddress"] = params.address("vaultAddress")?.into();
                if params.get("user").is_some() {
                    payload["user"] = params.address("user")?.into();
                }
                payload
            }
            "get_delegations" => {
                params.ensure_allowed(&["user"])?;
                let mut payload = json!({"type":"delegations"});
                payload["user"] = params.address("user")?.into();
                payload
            }
            "get_delegator_summary" => {
                params.ensure_allowed(&["user"])?;
                let mut payload = json!({"type":"delegatorSummary"});
                payload["user"] = params.address("user")?.into();
                payload
            }
            "get_delegator_history" => {
                params.ensure_allowed(&["user"])?;
                let mut payload = json!({"type":"delegatorHistory"});
                payload["user"] = params.address("user")?.into();
                payload
            }
            "get_delegator_rewards" => {
                params.ensure_allowed(&["user"])?;
                let mut payload = json!({"type":"delegatorRewards"});
                payload["user"] = params.address("user")?.into();
                payload
            }
            "get_spot_deploy_state" => {
                params.ensure_allowed(&["user"])?;
                let mut payload = json!({"type":"spotDeployState"});
                payload["user"] = params.address("user")?.into();
                payload
            }
            "get_outcome_meta" => {
                params.ensure_allowed(&[])?;
                let payload = json!({"type":"outcomeMeta"});
                payload
            }
            "get_settled_outcome" => {
                params.ensure_allowed(&["outcome"])?;
                let mut payload = json!({"type":"settledOutcome"});
                payload["outcome"] = params.required_u64("outcome")?.into();
                payload
            }
            "get_outcome_deployer_limits" => {
                params.ensure_allowed(&["venue"])?;
                let mut payload = json!({"type":"outcomeDeployerLimits"});
                payload["venue"] = params.required("venue")?.into();
                payload
            }
            "get_perp_deploy_auction_status" => {
                params.ensure_allowed(&[])?;
                let payload = json!({"type":"perpDeployAuctionStatus"});
                payload
            }
            "get_spot_pair_deploy_auction_status" => {
                params.ensure_allowed(&[])?;
                let payload = json!({"type":"spotPairDeployAuctionStatus"});
                payload
            }
            "get_perps_at_open_interest_cap" => {
                params.ensure_allowed(&["dex"])?;
                let mut payload = json!({"type":"perpsAtOpenInterestCap"});
                if let Some(value) = params.get("dex") {
                    payload["dex"] = value.into();
                }
                payload
            }
            "get_perp_dex_limits" => {
                params.ensure_allowed(&["dex"])?;
                let mut payload = json!({"type":"perpDexLimits"});
                payload["dex"] = params.required("dex")?.into();
                payload
            }
            "get_perp_dex_status" => {
                params.ensure_allowed(&["dex"])?;
                let mut payload = json!({"type":"perpDexStatus"});
                payload["dex"] = params
                    .get("dex")
                    .ok_or_else(|| {
                        DcexError::InvalidInput("dex is required; empty means the first DEX".into())
                    })?
                    .into();
                payload
            }
            "get_all_perp_metas" => {
                params.ensure_allowed(&[])?;
                let payload = json!({"type":"allPerpMetas"});
                payload
            }
            "get_perp_annotation" => {
                params.ensure_allowed(&["product_symbol"])?;
                let mut payload = json!({"type":"perpAnnotation"});
                payload["coin"] = self.coin(params.required("product_symbol")?)?.into();
                payload
            }
            "get_perp_categories" => {
                params.ensure_allowed(&[])?;
                let payload = json!({"type":"perpCategories"});
                payload
            }
            "get_perp_concise_annotations" => {
                params.ensure_allowed(&[])?;
                let payload = json!({"type":"perpConciseAnnotations"});
                payload
            }
            "get_token_details" => {
                params.ensure_allowed(&["tokenId"])?;
                let mut payload = json!({"type":"tokenDetails"});
                let id = params.required("tokenId")?;
                if id.len() != 34
                    || !id.starts_with("0x")
                    || !id[2..].bytes().all(|b| b.is_ascii_hexdigit())
                {
                    return Err(DcexError::InvalidInput(
                        "tokenId must be a 16-byte hex ID".into(),
                    ));
                }
                payload["tokenId"] = id.to_ascii_lowercase().into();
                payload
            }
            "get_user_dex_abstraction" => {
                params.ensure_allowed(&["user"])?;
                let mut payload = json!({"type":"userDexAbstraction"});
                payload["user"] = params.address("user")?.into();
                payload
            }
            "get_user_abstraction" => {
                params.ensure_allowed(&["user"])?;
                let mut payload = json!({"type":"userAbstraction"});
                payload["user"] = params.address("user")?.into();
                payload
            }
            "get_borrow_lend_user_state" => {
                params.ensure_allowed(&["user"])?;
                let mut payload = json!({"type":"borrowLendUserState"});
                payload["user"] = params.address("user")?.into();
                payload
            }
            "get_borrow_lend_reserve_state" => {
                params.ensure_allowed(&["token"])?;
                let mut payload = json!({"type":"borrowLendReserveState"});
                payload["token"] = params.required_u64("token")?.into();
                payload
            }
            "get_all_borrow_lend_reserve_states" => {
                params.ensure_allowed(&[])?;
                let payload = json!({"type":"allBorrowLendReserveStates"});
                payload
            }
            "get_predicted_fundings" => {
                params.ensure_allowed(&[])?;
                json!({"type":"predictedFundings"})
            }
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
                if let Some(value) = n_sig_figs
                    && ![2, 3, 4, 5].contains(&value)
                {
                    return Err(DcexError::InvalidInput(
                        "Hyperliquid nSigFigs must be 2, 3, 4, or 5".to_string(),
                    ));
                }
                let mantissa = params.optional_u64("mantissa")?;
                if let Some(value) = mantissa
                    && (n_sig_figs != Some(5) || ![1, 2, 5].contains(&value))
                {
                    return Err(DcexError::InvalidInput(
                        "Hyperliquid mantissa must be 1, 2, or 5 and requires nSigFigs=5"
                            .to_string(),
                    ));
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
    if let Some(value) = value
        && let Some(object) = payload.as_object_mut()
    {
        object.insert(key.to_string(), Value::String(value.to_string()));
    }
}

fn insert_optional_unsigned(payload: &mut Value, key: &str, value: Option<u64>) {
    if let Some(value) = value
        && let Some(object) = payload.as_object_mut()
    {
        object.insert(key.to_string(), Value::Number(value.into()));
    }
}
