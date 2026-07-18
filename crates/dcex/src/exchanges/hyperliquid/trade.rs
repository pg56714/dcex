use serde_json::{Map, Number, Value};

use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};

use super::client::HyperliquidClient;
use super::msgpack::{encode_msgpack, OrderedValue};
use super::params::HyperliquidParams;

impl HyperliquidClient {
    pub async fn private_request(
        &self,
        method_name: &str,
        params: Vec<(String, String)>,
    ) -> Result<ValidatedResponse> {
        let params = HyperliquidParams::from_pairs(params);
        match method_name {
            "place_order" => self.place_order_from_params(&params, None, None).await,
            "place_future_market_order" => self.place_market_order_from_params(&params, None).await,
            "place_future_market_buy_order" => {
                self.place_market_order_from_params(&params, Some(true))
                    .await
            }
            "place_future_market_sell_order" => {
                self.place_market_order_from_params(&params, Some(false))
                    .await
            }
            "place_future_limit_order" => {
                self.place_order_from_params(&params, None, Some(false))
                    .await
            }
            "place_future_limit_buy_order" => {
                self.place_order_from_params(&params, Some(true), Some(false))
                    .await
            }
            "place_future_limit_sell_order" => {
                self.place_order_from_params(&params, Some(false), Some(false))
                    .await
            }
            "cancel_order" => self.cancel_order_from_params(&params).await,
            "cancel_order_by_cloid" => self.cancel_order_by_cloid_from_params(&params).await,
            "schedule_cancel" => self.schedule_cancel_from_params(&params).await,
            "modify_order" => self.modify_order_from_params(&params).await,
            "modify_batch_orders" => self.modify_batch_orders_from_params(&params).await,
            "update_leverage" => self.update_leverage_from_params(&params).await,
            "update_isolate_margin" => self.update_isolate_margin_from_params(&params).await,
            "place_twap_order" => self.place_twap_order_from_params(&params).await,
            "cancel_twap_order" => self.cancel_twap_order_from_params(&params).await,
            _ => Err(DcexError::InvalidInput(format!(
                "unsupported Hyperliquid private method: {method_name}"
            ))),
        }
    }

    async fn place_order_from_params(
        &self,
        params: &HyperliquidParams,
        is_buy_override: Option<bool>,
        reduce_only_override: Option<bool>,
    ) -> Result<ValidatedResponse> {
        let action =
            self.order_action_from_params(params, is_buy_override, reduce_only_override)?;
        self.submit_action(action, params).await
    }

    async fn place_market_order_from_params(
        &self,
        params: &HyperliquidParams,
        is_buy_override: Option<bool>,
    ) -> Result<ValidatedResponse> {
        let product_symbol = params.required("product_symbol")?;
        let is_buy = match is_buy_override {
            Some(value) => value,
            None => params.required_bool("isBuy")?,
        };
        let (mid_price, sz_decimals) = self.mid_price(product_symbol).await?;
        let slippage_multiplier = if is_buy { 1.03 } else { 0.97 };
        let max_price_decimals = 6_u32.saturating_sub(sz_decimals);
        let price =
            format_market_order_price(mid_price * slippage_multiplier, is_buy, max_price_decimals);
        let mut params = params.with_overrides(vec![
            ("price".to_string(), price),
            ("isBuy".to_string(), is_buy.to_string()),
            ("reduceOnly".to_string(), "false".to_string()),
        ]);
        if params.get("triggerPx").is_none() && params.get("tpsl").is_none() {
            params.push("tif", "Ioc");
        } else {
            params.push("isMarket", "true");
        }
        self.place_order_from_params(&params, None, None).await
    }

    async fn cancel_order_from_params(
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
                    ("o", int(params.required_i64("oid")?)),
                ])]),
            ),
        ]);
        self.submit_action(action, params).await
    }

    async fn cancel_order_by_cloid_from_params(
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
                    ("cloid", string(params.required("cloid")?)),
                ])]),
            ),
        ]);
        self.submit_action(action, params).await
    }

    async fn schedule_cancel_from_params(
        &self,
        params: &HyperliquidParams,
    ) -> Result<ValidatedResponse> {
        let time = params
            .optional_i64("time")?
            .map_or(OrderedValue::Null, OrderedValue::Int);
        let action = object(vec![("type", string("scheduleCancel")), ("time", time)]);
        self.submit_action(action, params).await
    }

    async fn modify_order_from_params(
        &self,
        params: &HyperliquidParams,
    ) -> Result<ValidatedResponse> {
        let order = self.order_value_from_params(params, None, None)?;
        let action = object(vec![
            ("type", string("modify")),
            ("oid", order_identifier(params.required("oid")?)),
            ("order", order),
        ]);
        self.submit_action(action, params).await
    }

    async fn modify_batch_orders_from_params(
        &self,
        params: &HyperliquidParams,
    ) -> Result<ValidatedResponse> {
        let action = object(vec![
            ("type", string("batchModify")),
            ("modifies", params.ordered_json_required("modifies")?),
        ]);
        self.submit_action(action, params).await
    }

    async fn update_leverage_from_params(
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
            ("leverage", int(params.required_i64("leverage")?)),
        ]);
        self.submit_action(action, params).await
    }

    async fn update_isolate_margin_from_params(
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

    async fn place_twap_order_from_params(
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
                    ("s", string(params.required("size")?)),
                    ("r", bool_value(params.required_bool("reduceOnly")?)),
                    ("m", int(params.required_i64("minutes")?)),
                    ("t", bool_value(params.required_bool("randomize")?)),
                ]),
            ),
        ]);
        self.submit_action(action, params).await
    }

    async fn cancel_twap_order_from_params(
        &self,
        params: &HyperliquidParams,
    ) -> Result<ValidatedResponse> {
        let action = object(vec![
            ("type", string("twapCancel")),
            (
                "a",
                uint(self.asset_id(params.required("product_symbol")?)?),
            ),
            ("t", int(params.required_i64("twap_id")?)),
        ]);
        self.submit_action(action, params).await
    }

    fn order_action_from_params(
        &self,
        params: &HyperliquidParams,
        is_buy_override: Option<bool>,
        reduce_only_override: Option<bool>,
    ) -> Result<OrderedValue> {
        let mut fields = vec![
            ("type", string("order")),
            (
                "orders",
                array(vec![self.order_value_from_params(
                    params,
                    is_buy_override,
                    reduce_only_override,
                )?]),
            ),
            ("grouping", string(params.get("grouping").unwrap_or("na"))),
        ];
        match (params.get("builder_address"), params.get("fee_ten_bp")) {
            (Some(address), Some(fee)) => fields.push((
                "builder",
                object(vec![
                    ("b", string(address)),
                    ("f", int(parse_i64(fee, "fee_ten_bp")?)),
                ]),
            )),
            (None, None) => {}
            _ => {
                return Err(DcexError::InvalidInput(
                    "builder_address and fee_ten_bp must be provided together".to_string(),
                ))
            }
        }
        Ok(object(fields))
    }

    fn order_value_from_params(
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
        let mut fields = vec![
            (
                "a",
                uint(self.asset_id(params.required("product_symbol")?)?),
            ),
            ("b", bool_value(is_buy)),
            ("p", string(params.required("price")?)),
            ("s", string(params.required("size")?)),
            ("r", bool_value(reduce_only)),
        ];

        if let Some(tif) = params.get("tif") {
            fields.push((
                "t",
                object(vec![("limit", object(vec![("tif", string(tif))]))]),
            ));
        } else if params.get("isMarket").is_some() {
            let trigger_price = params.required("triggerPx")?;
            let tpsl = params.required("tpsl")?;
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

        if let Some(cloid) = params.get("cloid") {
            fields.push(("c", string(cloid)));
        }
        Ok(object(fields))
    }

    async fn submit_action(
        &self,
        action: OrderedValue,
        params: &HyperliquidParams,
    ) -> Result<ValidatedResponse> {
        let action_msgpack = encode_msgpack(&action);
        let mut payload = Map::new();
        payload.insert("action".to_string(), action.to_json());
        if let Some(vault_address) = params.get("vaultAddress") {
            payload.insert(
                "vaultAddress".to_string(),
                Value::String(vault_address.to_string()),
            );
        }
        if let Some(expires_after) = params.optional_u64("expiresAfter")? {
            payload.insert(
                "expiresAfter".to_string(),
                Value::Number(Number::from(expires_after)),
            );
        }
        self.exchange_payload(Value::Object(payload), action_msgpack)
            .await
    }

    async fn mid_price(&self, product_symbol: &str) -> Result<(f64, u32)> {
        let asset_id = self.asset_id(product_symbol)? as usize;
        let response = self.get_meta_and_asset_ctxs_raw().await?;
        let values = response.data.as_array().ok_or_else(|| {
            DcexError::Decode("Hyperliquid metaAndAssetCtxs response is invalid".to_string())
        })?;
        let sz_decimals = values
            .first()
            .and_then(|meta| meta.get("universe"))
            .and_then(Value::as_array)
            .and_then(|universe| universe.get(asset_id))
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
        let context = contexts.get(asset_id).ok_or_else(|| {
            DcexError::InvalidInput(format!("Hyperliquid asset id out of range: {asset_id}"))
        })?;
        let mid_price = context.get("midPx").ok_or_else(|| {
            DcexError::Decode("Hyperliquid asset context missing midPx".to_string())
        })?;
        let mid_price = match mid_price {
            Value::String(value) => value
                .parse::<f64>()
                .map_err(|error| DcexError::Decode(error.to_string())),
            Value::Number(value) => value
                .as_f64()
                .ok_or_else(|| DcexError::Decode("invalid Hyperliquid midPx".to_string())),
            _ => Err(DcexError::Decode(
                "invalid Hyperliquid midPx type".to_string(),
            )),
        }?;
        Ok((mid_price, sz_decimals))
    }
}

impl HyperliquidParams {
    fn with_overrides(&self, overrides: Vec<(String, String)>) -> HyperliquidParams {
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

    fn push(&mut self, key: &str, value: &str) {
        if self.get(key).is_none() {
            self.0.push((key.to_string(), value.to_string()));
        }
    }
}

fn object(values: Vec<(&str, OrderedValue)>) -> OrderedValue {
    OrderedValue::Object(
        values
            .into_iter()
            .map(|(key, value)| (key.to_string(), value))
            .collect(),
    )
}

fn array(values: Vec<OrderedValue>) -> OrderedValue {
    OrderedValue::Array(values)
}

fn string(value: &str) -> OrderedValue {
    OrderedValue::String(value.to_string())
}

fn int(value: i64) -> OrderedValue {
    OrderedValue::Int(value)
}

fn order_identifier(value: &str) -> OrderedValue {
    value.parse::<i64>().map_or_else(|_| string(value), int)
}

fn uint(value: u64) -> OrderedValue {
    OrderedValue::Uint(value)
}

fn bool_value(value: bool) -> OrderedValue {
    OrderedValue::Bool(value)
}

fn parse_i64(value: &str, key: &str) -> Result<i64> {
    value.parse::<i64>().map_err(|error| {
        DcexError::InvalidInput(format!("invalid integer parameter {key}: {error}"))
    })
}

fn format_market_order_price(value: f64, is_buy: bool, max_decimals: u32) -> String {
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
    fn order_requires_limit_or_trigger_type() {
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
    fn modify_identifier_preserves_cloid() {
        assert_eq!(
            order_identifier("0x1234567890abcdef1234567890abcdef"),
            OrderedValue::String("0x1234567890abcdef1234567890abcdef".to_string())
        );
        assert_eq!(order_identifier("42"), OrderedValue::Int(42));
    }

    #[test]
    fn market_price_respects_significant_figures_and_asset_decimals() {
        assert_eq!(format_market_order_price(0.090527, true, 5), "0.09053");
        assert_eq!(format_market_order_price(0.090527, false, 5), "0.09052");
        assert_eq!(format_market_order_price(103.0, true, 1), "103");
    }
}
