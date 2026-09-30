pub(in crate::exchanges::hyperliquid) use serde_json::{Map, Number, Value};

pub(in crate::exchanges::hyperliquid) use super::endpoints::EXCHANGE;
pub(in crate::exchanges::hyperliquid) use crate::exchange::{ValidatedResponse, unix_timestamp_ms};
pub(in crate::exchanges::hyperliquid) use crate::http::HttpMethod;
pub(in crate::exchanges::hyperliquid) use crate::{DcexError, Result};

pub(in crate::exchanges::hyperliquid) use super::client::HyperliquidClient;
pub(in crate::exchanges::hyperliquid) use super::msgpack::{OrderedValue, encode_msgpack};
pub(in crate::exchanges::hyperliquid) use super::params::HyperliquidParams;

impl HyperliquidClient {
    pub(in crate::exchanges::hyperliquid) async fn additional_user_action(
        &self,
        kind: &str,
        params: &HyperliquidParams,
    ) -> Result<ValidatedResponse> {
        let (nonce, chain_id, signature) = user_signed_fields(params)?;

        let mut action = serde_json::json!({"type":kind,"hyperliquidChain":if self.is_testnet(){"Testnet"}else{"Mainnet"},"signatureChainId":chain_id,"nonce":nonce});
        if kind == "approveAgent" {
            action["agentAddress"] = params.address("agentAddress")?.into();
            if let Some(name) = params.get("agentName") {
                action["agentName"] = name.into();
            }
        } else if kind == "userDexAbstraction" {
            action["user"] = params.address("user")?.into();
            action["enabled"] = params.required_bool("enabled")?.into();
        } else {
            let wei = params.required_u64("wei")?;
            if wei == 0 {
                return Err(DcexError::InvalidInput("wei must be positive".into()));
            }
            action["wei"] = wei.into();
            if kind == "tokenDelegate" {
                action["validator"] = params.address("validator")?.into();
                action["isUndelegate"] = params.required_bool("isUndelegate")?.into();
            }
        }
        let body = serde_json::to_vec(
            &serde_json::json!({"action":action,"nonce":nonce,"signature":signature}),
        )
        .map_err(|e| DcexError::Decode(e.to_string()))?;
        self.request(HttpMethod::Post, EXCHANGE, body, None, false)
            .await
    }
    pub(in crate::exchanges::hyperliquid) async fn place_order_from_params(
        &self,
        params: &HyperliquidParams,
        is_buy_override: Option<bool>,
        reduce_only_override: Option<bool>,
    ) -> Result<ValidatedResponse> {
        let action =
            self.order_action_from_params(params, is_buy_override, reduce_only_override)?;
        self.submit_action(action, params).await
    }

    pub(in crate::exchanges::hyperliquid) async fn place_market_order_from_params(
        &self,
        params: &HyperliquidParams,
        is_buy_override: Option<bool>,
    ) -> Result<ValidatedResponse> {
        let product_symbol = params.required("product_symbol")?;
        let is_buy = match is_buy_override {
            Some(value) => value,
            None => params.required_bool("isBuy")?,
        };
        params.positive_decimal("size")?;
        let slippage = params
            .get("slippage")
            .unwrap_or("0.05")
            .parse::<f64>()
            .map_err(|error| {
                DcexError::InvalidInput(format!("invalid Hyperliquid slippage: {error}"))
            })?;
        if !slippage.is_finite() || !(0.0..1.0).contains(&slippage) {
            return Err(DcexError::InvalidInput(
                "Hyperliquid slippage must be finite and at least 0 but less than 1".to_string(),
            ));
        }
        let (mid_price, sz_decimals, is_spot) = self.mid_price(product_symbol).await?;
        let slippage_multiplier = if is_buy {
            1.0 + slippage
        } else {
            1.0 - slippage
        };
        // Hyperliquid tick rules (and SDK `_slippage_price`): perps allow 6 - szDecimals
        // price decimals, spot allows 8 - szDecimals.
        let max_decimals = if is_spot { 8_u32 } else { 6_u32 };
        let max_price_decimals = max_decimals.saturating_sub(sz_decimals);
        let price =
            format_market_order_price(mid_price * slippage_multiplier, is_buy, max_price_decimals);
        let mut params = params.with_overrides(vec![
            ("price".to_string(), price),
            ("isBuy".to_string(), is_buy.to_string()),
            (
                "reduceOnly".to_string(),
                params
                    .optional_bool("reduceOnly")?
                    .unwrap_or(false)
                    .to_string(),
            ),
        ]);
        if params.get("triggerPx").is_none() && params.get("tpsl").is_none() {
            params.push("tif", "Ioc");
        } else {
            params.push("isMarket", "true");
        }
        self.place_order_from_params(&params, None, None).await
    }

    pub(in crate::exchanges::hyperliquid) async fn cancel_order_from_params(
        &self,
        params: &HyperliquidParams,
    ) -> Result<ValidatedResponse> {
        let action = object(vec![
            ("type", string("cancel")),
            (
                "cancels",
                array(vec![object(vec![
                    (
                        "a",
                        uint(self.asset_id(params.required("product_symbol")?)?),
                    ),
                    ("o", uint(params.required_u64("oid")?)),
                ])]),
            ),
        ]);
        self.submit_action(action, params).await
    }

    pub(in crate::exchanges::hyperliquid) async fn cancel_order_by_cloid_from_params(
        &self,
        params: &HyperliquidParams,
    ) -> Result<ValidatedResponse> {
        let action = object(vec![
            ("type", string("cancelByCloid")),
            (
                "cancels",
                array(vec![object(vec![
                    (
                        "asset",
                        uint(self.asset_id(params.required("product_symbol")?)?),
                    ),
                    ("cloid", string(&params.cloid("cloid")?)),
                ])]),
            ),
        ]);
        self.submit_action(action, params).await
    }

    pub(in crate::exchanges::hyperliquid) async fn schedule_cancel_from_params(
        &self,
        params: &HyperliquidParams,
    ) -> Result<ValidatedResponse> {
        let mut fields = vec![("type", string("scheduleCancel"))];
        if let Some(time) = params.optional_u64("time")? {
            let minimum = unix_timestamp_ms()?.saturating_add(5_000);
            if time < minimum {
                return Err(DcexError::InvalidInput(format!(
                    "Hyperliquid schedule cancel time must be at least {minimum}"
                )));
            }
            fields.push(("time", uint(time)));
        }
        let action = object(fields);
        self.submit_action(action, params).await
    }

    pub(in crate::exchanges::hyperliquid) async fn set_user_abstraction_from_params(
        &self,
        params: &HyperliquidParams,
    ) -> Result<ValidatedResponse> {
        let user = params.address("user")?;
        let abstraction = params.required_one_of(
            "abstraction",
            &["disabled", "unifiedAccount", "portfolioMargin"],
        )?;
        let (nonce, chain_id, signature) = user_signed_fields(params)?;
        let payload = serde_json::json!({"action":{"type":"userSetAbstraction","hyperliquidChain":if self.is_testnet(){"Testnet"}else{"Mainnet"},"signatureChainId":chain_id,"user":user,"abstraction":abstraction,"nonce":nonce},"nonce":nonce,"signature":signature});
        let body = serde_json::to_vec(&payload).map_err(|e| DcexError::Decode(e.to_string()))?;
        self.request(HttpMethod::Post, EXCHANGE, body, None, false)
            .await
    }

    pub(in crate::exchanges::hyperliquid) async fn modify_order_from_params(
        &self,
        params: &HyperliquidParams,
    ) -> Result<ValidatedResponse> {
        let order = self.order_value_from_params(params, None, None)?;
        let action = object(vec![
            ("type", string("modify")),
            ("oid", order_identifier(params.required("oid")?)?),
            ("order", order),
        ]);
        self.submit_action(action, params).await
    }

    pub(in crate::exchanges::hyperliquid) async fn update_leverage_from_params(
        &self,
        params: &HyperliquidParams,
    ) -> Result<ValidatedResponse> {
        let action = object(vec![
            ("type", string("updateLeverage")),
            (
                "asset",
                uint(self.asset_id(params.required("product_symbol")?)?),
            ),
            ("isCross", bool_value(params.required_bool("isCross")?)),
            ("leverage", uint(positive_u64(params, "leverage")?)),
        ]);
        self.submit_action(action, params).await
    }

    pub(in crate::exchanges::hyperliquid) async fn update_isolated_margin_from_params(
        &self,
        params: &HyperliquidParams,
    ) -> Result<ValidatedResponse> {
        let action = object(vec![
            ("type", string("updateIsolatedMargin")),
            (
                "asset",
                uint(self.asset_id(params.required("product_symbol")?)?),
            ),
            ("isBuy", bool_value(params.required_bool("isBuy")?)),
            ("ntli", int(params.required_i64("ntli")?)),
        ]);
        self.submit_action(action, params).await
    }

    pub(in crate::exchanges::hyperliquid) async fn place_twap_order_from_params(
        &self,
        params: &HyperliquidParams,
    ) -> Result<ValidatedResponse> {
        let action = object(vec![
            ("type", string("twapOrder")),
            (
                "twap",
                object(vec![
                    (
                        "a",
                        uint(self.asset_id(params.required("product_symbol")?)?),
                    ),
                    ("b", bool_value(params.required_bool("isBuy")?)),
                    ("s", string(params.positive_decimal("size")?)),
                    ("r", bool_value(params.required_bool("reduceOnly")?)),
                    ("m", uint(positive_u64(params, "minutes")?)),
                    ("t", bool_value(params.required_bool("randomize")?)),
                ]),
            ),
        ]);
        self.submit_action(action, params).await
    }

    pub(in crate::exchanges::hyperliquid) async fn cancel_twap_order_from_params(
        &self,
        params: &HyperliquidParams,
    ) -> Result<ValidatedResponse> {
        let action = object(vec![
            ("type", string("twapCancel")),
            (
                "a",
                uint(self.asset_id(params.required("product_symbol")?)?),
            ),
            ("t", uint(params.required_u64("twap_id")?)),
        ]);
        self.submit_action(action, params).await
    }

    pub(in crate::exchanges::hyperliquid) fn order_action_from_params(
        &self,
        params: &HyperliquidParams,
        is_buy_override: Option<bool>,
        reduce_only_override: Option<bool>,
    ) -> Result<OrderedValue> {
        let order = self.order_value_from_params(params, is_buy_override, reduce_only_override)?;
        self.order_action(vec![order], params)
    }

    pub(in crate::exchanges::hyperliquid) fn order_action(
        &self,
        orders: Vec<OrderedValue>,
        params: &HyperliquidParams,
    ) -> Result<OrderedValue> {
        let mut fields = vec![
            ("type", string("order")),
            ("orders", array(orders)),
            (
                "grouping",
                string(match params.get("grouping") {
                    Some(_) => {
                        params.required_one_of("grouping", &["na", "normalTpsl", "positionTpsl"])?
                    }
                    None => "na",
                }),
            ),
        ];
        match (params.get("builder_address"), params.get("fee_ten_bp")) {
            (Some(_), Some(_)) => {
                let address = params.address("builder_address")?;
                fields.push((
                    "builder",
                    object(vec![
                        ("b", string(&address)),
                        ("f", uint(params.required_u64("fee_ten_bp")?)),
                    ]),
                ));
            }
            (None, None) => {}
            _ => {
                return Err(DcexError::InvalidInput(
                    "builder_address and fee_ten_bp must be provided together".to_string(),
                ));
            }
        }
        Ok(object(fields))
    }

    pub(in crate::exchanges::hyperliquid) fn order_value_from_params(
        &self,
        params: &HyperliquidParams,
        is_buy_override: Option<bool>,
        reduce_only_override: Option<bool>,
    ) -> Result<OrderedValue> {
        let is_buy = match is_buy_override {
            Some(value) => value,
            None => params.required_bool("isBuy")?,
        };
        let reduce_only = match reduce_only_override {
            Some(value) => value,
            None => params.required_bool("reduceOnly")?,
        };
        let price = params.positive_decimal("price")?;
        let size = params.positive_decimal("size")?;
        let mut fields = vec![
            (
                "a",
                uint(self.asset_id(params.required("product_symbol")?)?),
            ),
            ("b", bool_value(is_buy)),
            ("p", string(price)),
            ("s", string(size)),
            ("r", bool_value(reduce_only)),
        ];

        if params.get("tif").is_some() {
            if params.get("isMarket").is_some()
                || params.get("triggerPx").is_some()
                || params.get("tpsl").is_some()
            {
                return Err(DcexError::InvalidInput(
                    "Hyperliquid limit orders cannot include trigger fields".to_string(),
                ));
            }
            let tif = params.required_one_of("tif", &["Alo", "Ioc", "Gtc"])?;
            fields.push((
                "t",
                object(vec![("limit", object(vec![("tif", string(tif))]))]),
            ));
        } else if params.get("isMarket").is_some()
            || params.get("triggerPx").is_some()
            || params.get("tpsl").is_some()
        {
            let trigger_price = params.positive_decimal("triggerPx")?;
            let tpsl = params.required_one_of("tpsl", &["tp", "sl"])?;
            fields.push((
                "t",
                object(vec![(
                    "trigger",
                    object(vec![
                        (
                            "isMarket",
                            bool_value(params.optional_bool("isMarket")?.unwrap_or(false)),
                        ),
                        ("triggerPx", string(trigger_price)),
                        ("tpsl", string(tpsl)),
                    ]),
                )]),
            ));
        } else {
            return Err(DcexError::InvalidInput(
                "Hyperliquid orders require tif or trigger fields.".to_string(),
            ));
        }

        if let Some(cloid) = params.optional_cloid("cloid")? {
            fields.push(("c", string(&cloid)));
        }
        Ok(object(fields))
    }

    pub(super) async fn submit_action(
        &self,
        action: OrderedValue,
        params: &HyperliquidParams,
    ) -> Result<ValidatedResponse> {
        let action_msgpack = encode_msgpack(&action);
        let mut payload = Map::new();
        payload.insert("action".to_string(), action.to_json());
        if let Some(vault_address) = params.optional_address("vaultAddress")? {
            payload.insert("vaultAddress".to_string(), Value::String(vault_address));
        }
        if let Some(expires_after) = params.optional_u64("expiresAfter")? {
            payload.insert(
                "expiresAfter".to_string(),
                Value::Number(Number::from(expires_after)),
            );
        }
        if let Some(nonce) = params.optional_u64("nonce")? {
            self.exchange_payload_at_nonce(Value::Object(payload), action_msgpack, nonce)
                .await
        } else {
            self.exchange_payload(Value::Object(payload), action_msgpack)
                .await
        }
    }

    /// Returns `(mid price, szDecimals, is_spot)` for a market order.
    pub(in crate::exchanges::hyperliquid) async fn mid_price(
        &self,
        product_symbol: &str,
    ) -> Result<(f64, u32, bool)> {
        let coin = self.coin(product_symbol)?;
        let spot_asset = self
            .symbol_parts(product_symbol)
            .ok()
            .map(|(_, asset)| asset)
            .filter(|asset| (SPOT_ASSET_OFFSET..HIP3_ASSET_OFFSET).contains(asset));
        if spot_asset.is_some() || coin.starts_with('@') || coin.contains('/') {
            let (mid_price, sz_decimals) = self.spot_mid_price(&coin, spot_asset).await?;
            return Ok((mid_price, sz_decimals, true));
        }
        let dex = coin.split_once(':').map(|(dex, _)| dex);
        let response = self.get_meta_and_asset_ctxs_raw(dex).await?;
        let values = response.data.as_array().ok_or_else(|| {
            DcexError::Decode("Hyperliquid metaAndAssetCtxs response is invalid".to_string())
        })?;
        let universe = values
            .first()
            .and_then(|meta| meta.get("universe"))
            .and_then(Value::as_array)
            .ok_or_else(|| {
                DcexError::Decode("Hyperliquid asset metadata missing universe".to_string())
            })?;
        let asset_index = universe
            .iter()
            .position(|asset| asset.get("name").and_then(Value::as_str) == Some(coin.as_str()))
            .ok_or_else(|| {
                DcexError::InvalidInput(format!(
                    "Hyperliquid metaAndAssetCtxs does not contain coin {coin}"
                ))
            })?;
        let sz_decimals = universe
            .get(asset_index)
            .and_then(|asset| asset.get("szDecimals"))
            .and_then(Value::as_u64)
            .ok_or_else(|| {
                DcexError::Decode("Hyperliquid asset metadata missing szDecimals".to_string())
            })?;
        let sz_decimals = u32::try_from(sz_decimals).map_err(|error| {
            DcexError::Decode(format!("invalid Hyperliquid szDecimals: {error}"))
        })?;
        let contexts = values.get(1).and_then(Value::as_array).ok_or_else(|| {
            DcexError::Decode("Hyperliquid metaAndAssetCtxs response is invalid".to_string())
        })?;
        let context = contexts.get(asset_index).ok_or_else(|| {
            DcexError::InvalidInput(format!(
                "Hyperliquid asset context index out of range: {asset_index}"
            ))
        })?;
        Ok((parse_mid_price(context)?, sz_decimals, false))
    }

    /// Reads a spot mid price and base-token szDecimals from `spotMetaAndAssetCtxs`.
    pub(in crate::exchanges::hyperliquid) async fn spot_mid_price(
        &self,
        coin: &str,
        asset: Option<u64>,
    ) -> Result<(f64, u32)> {
        let response = self
            .info_payload(serde_json::json!({"type": "spotMetaAndAssetCtxs"}))
            .await?;
        let invalid =
            || DcexError::Decode("Hyperliquid spotMetaAndAssetCtxs response is invalid".into());
        let values = response.data.as_array().ok_or_else(invalid)?;
        let meta = values.first().ok_or_else(invalid)?;
        let universe = meta
            .get("universe")
            .and_then(Value::as_array)
            .ok_or_else(invalid)?;
        let spot_index = asset.map(|asset| asset - SPOT_ASSET_OFFSET);
        let position = universe
            .iter()
            .position(|pair| pair.get("name").and_then(Value::as_str) == Some(coin))
            .or_else(|| {
                let index = spot_index?;
                universe
                    .iter()
                    .position(|pair| pair.get("index").and_then(Value::as_u64) == Some(index))
            })
            .ok_or_else(|| {
                DcexError::InvalidInput(format!(
                    "Hyperliquid spotMetaAndAssetCtxs does not contain coin {coin}"
                ))
            })?;
        let pair = &universe[position];
        let name = pair.get("name").and_then(Value::as_str).unwrap_or(coin);
        let base_token = pair
            .get("tokens")
            .and_then(Value::as_array)
            .and_then(|tokens| tokens.first())
            .and_then(Value::as_u64)
            .ok_or_else(invalid)?;
        let sz_decimals = meta
            .get("tokens")
            .and_then(Value::as_array)
            .and_then(|tokens| {
                tokens
                    .iter()
                    .find(|token| token.get("index").and_then(Value::as_u64) == Some(base_token))
            })
            .and_then(|token| token.get("szDecimals"))
            .and_then(Value::as_u64)
            .ok_or_else(|| {
                DcexError::Decode("Hyperliquid spot token missing szDecimals".to_string())
            })?;
        let sz_decimals = u32::try_from(sz_decimals).map_err(|error| {
            DcexError::Decode(format!("invalid Hyperliquid szDecimals: {error}"))
        })?;
        let contexts = values
            .get(1)
            .and_then(Value::as_array)
            .ok_or_else(invalid)?;
        let context = contexts
            .iter()
            .find(|context| context.get("coin").and_then(Value::as_str) == Some(name))
            .or_else(|| contexts.get(position))
            .ok_or_else(|| {
                DcexError::InvalidInput(format!(
                    "Hyperliquid spot asset context not found for {name}"
                ))
            })?;
        Ok((parse_mid_price(context)?, sz_decimals))
    }
}

/// Spot asset ids are `10000 + spot index`; HIP-3 perp dex ids start at 100000.
pub(in crate::exchanges::hyperliquid) const SPOT_ASSET_OFFSET: u64 = 10_000;
pub(in crate::exchanges::hyperliquid) const HIP3_ASSET_OFFSET: u64 = 100_000;

pub(in crate::exchanges::hyperliquid) fn parse_mid_price(context: &Value) -> Result<f64> {
    let mid_price = context
        .get("midPx")
        .ok_or_else(|| DcexError::Decode("Hyperliquid asset context missing midPx".to_string()))?;
    match mid_price {
        Value::String(value) => value
            .parse::<f64>()
            .map_err(|error| DcexError::Decode(error.to_string())),
        Value::Number(value) => value
            .as_f64()
            .ok_or_else(|| DcexError::Decode("invalid Hyperliquid midPx".to_string())),
        _ => Err(DcexError::Decode(
            "invalid Hyperliquid midPx type".to_string(),
        )),
    }
}

impl HyperliquidParams {
    pub(in crate::exchanges::hyperliquid) fn with_overrides(
        &self,
        overrides: Vec<(String, String)>,
    ) -> HyperliquidParams {
        let mut pairs = self.0.clone();
        for (key, value) in overrides {
            if let Some((_, existing)) = pairs.iter_mut().find(|(candidate, _)| candidate == &key) {
                *existing = value;
            } else {
                pairs.push((key, value));
            }
        }
        HyperliquidParams::from_pairs(pairs)
    }

    pub(in crate::exchanges::hyperliquid) fn push(&mut self, key: &str, value: &str) {
        if self.get(key).is_none() {
            self.0.push((key.to_string(), value.to_string()));
        }
    }
}

pub(in crate::exchanges::hyperliquid) fn object(values: Vec<(&str, OrderedValue)>) -> OrderedValue {
    OrderedValue::Object(
        values
            .into_iter()
            .map(|(key, value)| (key.to_string(), value))
            .collect(),
    )
}

pub(in crate::exchanges::hyperliquid) fn array(values: Vec<OrderedValue>) -> OrderedValue {
    OrderedValue::Array(values)
}

pub(in crate::exchanges::hyperliquid) fn string(value: &str) -> OrderedValue {
    OrderedValue::String(value.to_string())
}

pub(in crate::exchanges::hyperliquid) fn int(value: i64) -> OrderedValue {
    OrderedValue::Int(value)
}

pub(in crate::exchanges::hyperliquid) fn order_identifier(value: &str) -> Result<OrderedValue> {
    if value.starts_with("0x") || value.starts_with("0X") {
        return Ok(string(&super::params::normalize_cloid(value, "oid")?));
    }
    value.parse::<u64>().map(uint).map_err(|error| {
        DcexError::InvalidInput(format!(
            "Hyperliquid oid must be an unsigned integer or client order id: {error}"
        ))
    })
}

pub(in crate::exchanges::hyperliquid) fn uint(value: u64) -> OrderedValue {
    OrderedValue::Uint(value)
}

pub(in crate::exchanges::hyperliquid) fn bool_value(value: bool) -> OrderedValue {
    OrderedValue::Bool(value)
}

pub(in crate::exchanges::hyperliquid) fn positive_u64(
    params: &HyperliquidParams,
    key: &str,
) -> Result<u64> {
    let value = params.required_u64(key)?;
    if value == 0 {
        return Err(DcexError::InvalidInput(format!(
            "Hyperliquid {key} must be greater than zero"
        )));
    }
    Ok(value)
}

pub(super) fn signature_param(params: &HyperliquidParams) -> Result<Value> {
    let signature: Value = serde_json::from_str(params.required("signature")?)
        .map_err(|e| DcexError::InvalidInput(e.to_string()))?;
    if !signature.as_object().is_some_and(|s| {
        s.len() == 3
            && ["r", "s"].iter().all(|k| {
                s.get(*k).and_then(Value::as_str).is_some_and(|v| {
                    v.len() == 66
                        && v.starts_with("0x")
                        && v[2..].bytes().all(|b| b.is_ascii_hexdigit())
                })
            })
            && matches!(s.get("v").and_then(Value::as_u64), Some(27 | 28))
    }) {
        return Err(DcexError::InvalidInput(
            "signature requires 32-byte r/s and v 27 or 28".into(),
        ));
    }

    Ok(signature)
}

pub(super) fn user_signed_fields(params: &HyperliquidParams) -> Result<(u64, &str, Value)> {
    let nonce = params.required_u64("nonce")?;
    let chain_id = params.required("signatureChainId")?;
    if !chain_id.starts_with("0x")
        || chain_id.len() <= 2
        || !chain_id[2..].bytes().all(|b| b.is_ascii_hexdigit())
    {
        return Err(DcexError::InvalidInput(
            "signatureChainId must be a hexadecimal chain ID".into(),
        ));
    }
    let signature = signature_param(params)?;
    Ok((nonce, chain_id, signature))
}

pub(in crate::exchanges::hyperliquid) fn validate_private_params(
    method_name: &str,
    params: &HyperliquidParams,
) -> Result<()> {
    const ORDER_FIELDS: &[&str] = &[
        "product_symbol",
        "isBuy",
        "price",
        "size",
        "reduceOnly",
        "tif",
        "isMarket",
        "triggerPx",
        "tpsl",
        "cloid",
        "grouping",
        "builder_address",
        "fee_ten_bp",
        "vaultAddress",
        "expiresAfter",
    ];
    const MARKET_FIELDS: &[&str] = &[
        "product_symbol",
        "isBuy",
        "size",
        "reduceOnly",
        "slippage",
        "triggerPx",
        "tpsl",
        "cloid",
        "grouping",
        "builder_address",
        "fee_ten_bp",
        "vaultAddress",
        "expiresAfter",
    ];

    let allowed: &[&str] = match method_name {
        "borrow_lend_signed" => &[
            "action",
            "nonce",
            "signature",
            "vaultAddress",
            "expiresAfter",
        ],
        "approve_agent_signed" => &[
            "agentAddress",
            "agentName",
            "nonce",
            "signature",
            "signatureChainId",
        ],
        "create_sub_account" => &["name", "nonce", "expiresAfter"],
        "transfer_sub_account_usd" => &[
            "subAccountUser",
            "isDeposit",
            "usd",
            "nonce",
            "expiresAfter",
        ],
        "transfer_sub_account_spot" => &[
            "subAccountUser",
            "isDeposit",
            "token",
            "amount",
            "nonce",
            "expiresAfter",
        ],
        "transfer_vault_usd" => &["targetVault", "isDeposit", "usd", "nonce", "expiresAfter"],
        "enable_agent_dex_abstraction" => &["nonce", "expiresAfter"],
        "transfer_hip3_liquidator" => &["dex", "ntl", "isDeposit", "nonce", "expiresAfter"],
        "deposit_staking_signed" => &["wei", "nonce", "signature", "signatureChainId"],
        "withdraw_staking_signed" => &["wei", "nonce", "signature", "signatureChainId"],
        "delegate_tokens_signed" => &[
            "validator",
            "wei",
            "isUndelegate",
            "nonce",
            "signature",
            "signatureChainId",
        ],
        "set_user_dex_abstraction_signed" => {
            &["user", "enabled", "nonce", "signature", "signatureChainId"]
        }
        "place_order" => ORDER_FIELDS,
        "place_future_market_order" => MARKET_FIELDS,
        "place_future_market_buy_order" | "place_future_market_sell_order" => &[
            "product_symbol",
            "size",
            "reduceOnly",
            "slippage",
            "triggerPx",
            "tpsl",
            "cloid",
            "grouping",
            "builder_address",
            "fee_ten_bp",
            "vaultAddress",
            "expiresAfter",
        ],
        "place_future_limit_order" => &[
            "product_symbol",
            "isBuy",
            "price",
            "size",
            "tif",
            "cloid",
            "grouping",
            "builder_address",
            "fee_ten_bp",
            "vaultAddress",
            "expiresAfter",
        ],
        "place_future_limit_buy_order" | "place_future_limit_sell_order" => &[
            "product_symbol",
            "price",
            "size",
            "tif",
            "cloid",
            "grouping",
            "builder_address",
            "fee_ten_bp",
            "vaultAddress",
            "expiresAfter",
        ],
        "place_batch_orders" => &[
            "orders",
            "grouping",
            "builder_address",
            "fee_ten_bp",
            "vaultAddress",
            "expiresAfter",
        ],
        "cancel_batch_orders" | "cancel_batch_orders_by_cloid" => {
            &["cancels", "vaultAddress", "expiresAfter"]
        }
        "cancel_order" => &["product_symbol", "oid", "vaultAddress", "expiresAfter"],
        "cancel_order_by_cloid" => &["product_symbol", "cloid", "vaultAddress", "expiresAfter"],
        "schedule_cancel" => &["time", "vaultAddress", "expiresAfter"],
        "noop" => &["nonce", "vaultAddress", "expiresAfter"],
        "reserve_request_weight" => &["weight", "expiresAfter"],
        "set_agent_abstraction" => &["abstraction", "vaultAddress", "expiresAfter"],
        "set_user_abstraction" => &[
            "user",
            "abstraction",
            "nonce",
            "signature",
            "signatureChainId",
        ],
        "transfer_between_dexes" => &["sourceDex", "destinationDex", "token", "amount"],
        "transfer_usdc_spot_perp" => {
            &["amount", "toPerp", "nonce", "signature", "signatureChainId"]
        }
        "modify_order" => &[
            "oid",
            "product_symbol",
            "isBuy",
            "price",
            "size",
            "reduceOnly",
            "tif",
            "isMarket",
            "triggerPx",
            "tpsl",
            "cloid",
            "vaultAddress",
            "expiresAfter",
        ],
        "modify_batch_orders" => &["modifies", "vaultAddress", "expiresAfter"],
        "update_leverage" => &[
            "product_symbol",
            "isCross",
            "leverage",
            "vaultAddress",
            "expiresAfter",
        ],
        "update_isolated_margin" => &[
            "product_symbol",
            "isBuy",
            "ntli",
            "vaultAddress",
            "expiresAfter",
        ],
        "place_twap_order" => &[
            "product_symbol",
            "isBuy",
            "size",
            "reduceOnly",
            "minutes",
            "randomize",
            "vaultAddress",
            "expiresAfter",
        ],
        "cancel_twap_order" => &["product_symbol", "twap_id", "vaultAddress", "expiresAfter"],
        _ => return Ok(()),
    };
    params.ensure_allowed(allowed)
}

/// Parses a non-empty JSON array of flat objects into per-item params.
///
/// Values must be strings, booleans or integers; floats are rejected so prices and sizes
/// stay exact decimal strings on the wire. `null` values are treated as absent.
pub(in crate::exchanges::hyperliquid) fn batch_items(
    params: &HyperliquidParams,
    key: &str,
    allowed: &[&str],
) -> Result<Vec<HyperliquidParams>> {
    let value: Value = serde_json::from_str(params.required(key)?).map_err(|error| {
        DcexError::InvalidInput(format!("invalid JSON parameter {key}: {error}"))
    })?;
    let items = value.as_array().ok_or_else(|| {
        DcexError::InvalidInput(format!("Hyperliquid {key} must be a JSON array"))
    })?;
    if items.is_empty() {
        return Err(DcexError::InvalidInput(format!(
            "Hyperliquid {key} must not be empty"
        )));
    }
    items
        .iter()
        .map(|item| {
            let fields = item.as_object().ok_or_else(|| {
                DcexError::InvalidInput(format!("Hyperliquid {key} items must be JSON objects"))
            })?;
            let mut pairs = Vec::with_capacity(fields.len());
            for (field, value) in fields {
                let value = match value {
                    Value::Null => continue,
                    Value::String(value) => value.clone(),
                    Value::Bool(value) => value.to_string(),
                    Value::Number(value) if value.is_i64() || value.is_u64() => value.to_string(),
                    _ => {
                        return Err(DcexError::InvalidInput(format!(
                            "Hyperliquid {key} field {field} must be a string, boolean or integer"
                        )));
                    }
                };
                pairs.push((field.clone(), value));
            }
            let item = HyperliquidParams::from_pairs(pairs);
            item.ensure_allowed(allowed)?;
            Ok(item)
        })
        .collect()
}

pub(in crate::exchanges::hyperliquid) fn normalize_batch_modifies(
    value: OrderedValue,
) -> Result<OrderedValue> {
    let OrderedValue::Array(modifies) = value else {
        return Err(DcexError::InvalidInput(
            "Hyperliquid modifies must be a JSON array".to_string(),
        ));
    };
    if modifies.is_empty() {
        return Err(DcexError::InvalidInput(
            "Hyperliquid modifies must not be empty".to_string(),
        ));
    }
    modifies
        .iter()
        .map(normalize_modify)
        .collect::<Result<Vec<_>>>()
        .map(array)
}

pub(in crate::exchanges::hyperliquid) fn normalize_modify(
    value: &OrderedValue,
) -> Result<OrderedValue> {
    let fields = exact_object(value, "modify", &["oid", "order"], &["oid", "order"])?;
    Ok(object(vec![
        ("oid", normalize_wire_oid(field(fields, "oid")?)?),
        ("order", normalize_wire_order(field(fields, "order")?)?),
    ]))
}

pub(super) fn normalize_wire_order(value: &OrderedValue) -> Result<OrderedValue> {
    let fields = exact_object(
        value,
        "modify order",
        &["a", "b", "p", "s", "r", "t", "c"],
        &["a", "b", "p", "s", "r", "t"],
    )?;
    let mut normalized = vec![
        ("a", normalize_unsigned(field(fields, "a")?, "a")?),
        ("b", normalize_boolean(field(fields, "b")?, "b")?),
        ("p", normalize_positive_string(field(fields, "p")?, "p")?),
        ("s", normalize_positive_string(field(fields, "s")?, "s")?),
        ("r", normalize_boolean(field(fields, "r")?, "r")?),
        ("t", normalize_wire_order_type(field(fields, "t")?)?),
    ];
    if let Some(cloid) = optional_field(fields, "c") {
        let OrderedValue::String(cloid) = cloid else {
            return Err(DcexError::InvalidInput(
                "Hyperliquid modify order c must be a string".to_string(),
            ));
        };
        normalized.push(("c", string(&super::params::normalize_cloid(cloid, "c")?)));
    }
    Ok(object(normalized))
}

pub(in crate::exchanges::hyperliquid) fn normalize_wire_order_type(
    value: &OrderedValue,
) -> Result<OrderedValue> {
    let fields = exact_object(value, "modify order type", &["limit", "trigger"], &[])?;
    match (
        optional_field(fields, "limit"),
        optional_field(fields, "trigger"),
    ) {
        (Some(limit), None) => {
            let limit = exact_object(limit, "modify limit type", &["tif"], &["tif"])?;
            let OrderedValue::String(tif) = field(limit, "tif")? else {
                return Err(DcexError::InvalidInput(
                    "Hyperliquid modify tif must be a string".to_string(),
                ));
            };
            if !["Alo", "Ioc", "Gtc"].contains(&tif.as_str()) {
                return Err(DcexError::InvalidInput(format!(
                    "invalid Hyperliquid tif: {tif}"
                )));
            }
            Ok(object(vec![("limit", object(vec![("tif", string(tif))]))]))
        }
        (None, Some(trigger)) => {
            let trigger = exact_object(
                trigger,
                "modify trigger type",
                &["isMarket", "triggerPx", "tpsl"],
                &["isMarket", "triggerPx", "tpsl"],
            )?;
            let OrderedValue::String(tpsl) = field(trigger, "tpsl")? else {
                return Err(DcexError::InvalidInput(
                    "Hyperliquid modify tpsl must be a string".to_string(),
                ));
            };
            if !["tp", "sl"].contains(&tpsl.as_str()) {
                return Err(DcexError::InvalidInput(format!(
                    "invalid Hyperliquid tpsl: {tpsl}"
                )));
            }
            Ok(object(vec![(
                "trigger",
                object(vec![
                    (
                        "isMarket",
                        normalize_boolean(field(trigger, "isMarket")?, "isMarket")?,
                    ),
                    (
                        "triggerPx",
                        normalize_positive_string(field(trigger, "triggerPx")?, "triggerPx")?,
                    ),
                    ("tpsl", string(tpsl)),
                ]),
            )]))
        }
        _ => Err(DcexError::InvalidInput(
            "Hyperliquid modify order type requires exactly one of limit or trigger".to_string(),
        )),
    }
}

pub(in crate::exchanges::hyperliquid) fn normalize_wire_oid(
    value: &OrderedValue,
) -> Result<OrderedValue> {
    match value {
        OrderedValue::String(value) => Ok(string(&super::params::normalize_cloid(value, "oid")?)),
        _ => normalize_unsigned(value, "oid"),
    }
}

pub(in crate::exchanges::hyperliquid) fn normalize_unsigned(
    value: &OrderedValue,
    key: &str,
) -> Result<OrderedValue> {
    match value {
        OrderedValue::Uint(value) => Ok(uint(*value)),
        OrderedValue::Int(value) if *value >= 0 => Ok(uint(*value as u64)),
        _ => Err(DcexError::InvalidInput(format!(
            "Hyperliquid {key} must be an unsigned integer"
        ))),
    }
}

pub(in crate::exchanges::hyperliquid) fn normalize_boolean(
    value: &OrderedValue,
    key: &str,
) -> Result<OrderedValue> {
    match value {
        OrderedValue::Bool(value) => Ok(bool_value(*value)),
        _ => Err(DcexError::InvalidInput(format!(
            "Hyperliquid {key} must be a boolean"
        ))),
    }
}

pub(in crate::exchanges::hyperliquid) fn normalize_positive_string(
    value: &OrderedValue,
    key: &str,
) -> Result<OrderedValue> {
    let OrderedValue::String(value) = value else {
        return Err(DcexError::InvalidInput(format!(
            "Hyperliquid {key} must be a decimal string"
        )));
    };
    let parsed = value
        .parse::<f64>()
        .map_err(|error| DcexError::InvalidInput(format!("invalid Hyperliquid {key}: {error}")))?;
    if !parsed.is_finite() || parsed <= 0.0 {
        return Err(DcexError::InvalidInput(format!(
            "Hyperliquid {key} must be a finite positive decimal string"
        )));
    }
    Ok(string(value))
}

pub(in crate::exchanges::hyperliquid) fn exact_object<'a>(
    value: &'a OrderedValue,
    label: &str,
    allowed: &[&str],
    required: &[&str],
) -> Result<&'a [(String, OrderedValue)]> {
    let OrderedValue::Object(fields) = value else {
        return Err(DcexError::InvalidInput(format!(
            "Hyperliquid {label} must be a JSON object"
        )));
    };
    for (index, (key, _)) in fields.iter().enumerate() {
        if !allowed.contains(&key.as_str()) {
            return Err(DcexError::InvalidInput(format!(
                "unsupported Hyperliquid {label} field: {key}"
            )));
        }
        if fields[..index].iter().any(|(previous, _)| previous == key) {
            return Err(DcexError::InvalidInput(format!(
                "duplicate Hyperliquid {label} field: {key}"
            )));
        }
    }
    for key in required {
        if optional_field(fields, key).is_none() {
            return Err(DcexError::InvalidInput(format!(
                "missing Hyperliquid {label} field: {key}"
            )));
        }
    }
    Ok(fields)
}

pub(in crate::exchanges::hyperliquid) fn field<'a>(
    fields: &'a [(String, OrderedValue)],
    key: &str,
) -> Result<&'a OrderedValue> {
    optional_field(fields, key)
        .ok_or_else(|| DcexError::InvalidInput(format!("missing Hyperliquid field: {key}")))
}

pub(in crate::exchanges::hyperliquid) fn optional_field<'a>(
    fields: &'a [(String, OrderedValue)],
    key: &str,
) -> Option<&'a OrderedValue> {
    fields
        .iter()
        .find_map(|(candidate, value)| (candidate == key).then_some(value))
}

pub(in crate::exchanges::hyperliquid) fn format_market_order_price(
    value: f64,
    is_buy: bool,
    max_decimals: u32,
) -> String {
    if value <= 0.0 || !value.is_finite() {
        return "0".to_string();
    }
    let adjusted = value.log10().floor() as i32;
    let significant_step = 10_f64.powi(adjusted - 4);
    let decimal_step = 10_f64.powi(-(max_decimals as i32));
    let step = significant_step.max(decimal_step);
    let units = value / step;
    let rounded = if is_buy {
        units.ceil() * step
    } else {
        units.floor() * step
    };
    let formatted = format!("{rounded:.12}");
    formatted
        .trim_end_matches('0')
        .trim_end_matches('.')
        .to_string()
}

#[cfg(test)]
mod tests {
    use std::time::Duration;

    use super::*;

    #[test]
    pub(in crate::exchanges::hyperliquid) fn order_requires_limit_or_trigger_type() {
        let client = HyperliquidClient::public(false, Duration::from_secs(1)).expect("client");
        let params = HyperliquidParams::from_pairs(vec![
            ("product_symbol".to_string(), "BTC".to_string()),
            ("isBuy".to_string(), "true".to_string()),
            ("price".to_string(), "100".to_string()),
            ("size".to_string(), "1".to_string()),
            ("reduceOnly".to_string(), "false".to_string()),
        ]);

        assert!(client.order_value_from_params(&params, None, None).is_err());
    }

    #[test]
    pub(in crate::exchanges::hyperliquid) fn modify_identifier_preserves_cloid() {
        assert_eq!(
            order_identifier("0x1234567890abcdef1234567890abcdef").expect("cloid"),
            OrderedValue::String("0x1234567890abcdef1234567890abcdef".to_string())
        );
        assert_eq!(order_identifier("42").expect("oid"), OrderedValue::Uint(42));
    }

    #[test]
    pub(in crate::exchanges::hyperliquid) fn market_price_respects_significant_figures_and_asset_decimals()
     {
        assert_eq!(format_market_order_price(0.090527, true, 5), "0.09053");
        assert_eq!(format_market_order_price(0.090527, false, 5), "0.09052");
        assert_eq!(format_market_order_price(103.0, true, 1), "103");
    }

    #[test]
    pub(in crate::exchanges::hyperliquid) fn transfer_rejects_identical_dexes_before_network() {
        let client = HyperliquidClient::public(false, Duration::from_secs(1)).expect("client");
        let error = crate::http::block_on(async move {
            client
                .private_request(
                    "transfer_between_dexes",
                    vec![
                        ("sourceDex".into(), "spot".into()),
                        ("destinationDex".into(), "spot".into()),
                        ("token".into(), "USDC:0x0".into()),
                        ("amount".into(), "1".into()),
                    ],
                )
                .await
        })
        .expect_err("identical dexes");
        assert!(error.to_string().contains("distinct source"));
    }
}
