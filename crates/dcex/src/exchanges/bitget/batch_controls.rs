//! Batch trading bodies verified against official request examples.
use super::{client::BitgetClient, params::BitgetParams};
use crate::exchange::ValidatedResponse;
use crate::{DcexError, Result};
use serde_json::{Map, Value};
use std::collections::HashSet;

impl BitgetClient {
    pub(super) async fn batch_controls_request(
        &self,
        name: &str,
        params: &BitgetParams,
    ) -> Result<Option<ValidatedResponse>> {
        let (path, field, maximum, margin, cancel) = match name {
            "place_cross_margin_batch_orders" => (
                "/api/v2/margin/crossed/batch-place-order",
                "orderList",
                None,
                true,
                false,
            ),
            "place_isolated_margin_batch_orders" => (
                "/api/v2/margin/isolated/batch-place-order",
                "orderList",
                None,
                true,
                false,
            ),
            "cancel_cross_margin_batch_orders" => (
                "/api/v2/margin/crossed/batch-cancel-order",
                "orderIdList",
                None,
                true,
                true,
            ),
            "cancel_isolated_margin_batch_orders" => (
                "/api/v2/margin/isolated/batch-cancel-order",
                "orderIdList",
                None,
                true,
                true,
            ),
            "batch_cancel_replace_spot_orders" => (
                "/api/v2/spot/trade/batch-cancel-replace-order",
                "orderList",
                Some(50),
                false,
                false,
            ),
            "modify_uta_batch_orders" => (
                "/api/v3/trade/batch-modify-order",
                "orders",
                Some(20),
                false,
                false,
            ),
            _ => return Ok(None),
        };
        let allowed = if margin {
            vec![field, "symbol"]
        } else {
            vec![field]
        };
        params.ensure_allowed(&allowed, margin)?;
        let mut value = params.json_required(field)?;
        let items = value
            .as_array_mut()
            .ok_or_else(|| invalid("batch must be an array"))?;
        if items.is_empty() || maximum.is_some_and(|max| items.len() > max) {
            return Err(invalid("batch size exceeds the documented bounds"));
        }
        let outer_symbol = if margin {
            Some(
                self.exchange_symbol(
                    params
                        .get("product_symbol")
                        .or_else(|| params.get("symbol"))
                        .filter(|s| !s.trim().is_empty())
                        .ok_or_else(|| invalid("symbol is required"))?,
                )?,
            )
        } else {
            None
        };
        let mut category = None;
        let mut seen = HashSet::new();
        for value in items {
            let object = value
                .as_object_mut()
                .ok_or_else(|| invalid("batch entries must be objects"))?;
            if let Some(product) = object.remove("product_symbol") {
                if object.contains_key("symbol") {
                    return Err(invalid("provide either symbol or product_symbol"));
                }
                object.insert(
                    "symbol".into(),
                    Value::String(
                        self.exchange_symbol(
                            product
                                .as_str()
                                .ok_or_else(|| invalid("product_symbol must be text"))?,
                        )?,
                    ),
                );
            } else if let Some(symbol) = object
                .get("symbol")
                .and_then(Value::as_str)
                .filter(|s| s.contains('-'))
                .map(str::to_string)
            {
                object.insert(
                    "symbol".into(),
                    Value::String(self.exchange_symbol(&symbol)?),
                );
            }
            if margin && object.contains_key("symbol") {
                return Err(invalid("margin batches specify symbol at the top level"));
            }
            let mut pairs = Vec::new();
            for (key, value) in object.iter() {
                let text = if name == "modify_uta_batch_orders" && key == "requestId" {
                    let id = value
                        .as_u64()
                        .filter(|id| *id <= 999_999_999_999_999_999)
                        .ok_or_else(|| {
                            invalid("requestId must be a number of at most 18 digits")
                        })?;
                    id.to_string()
                } else {
                    value
                        .as_str()
                        .filter(|v| !v.trim().is_empty())
                        .ok_or_else(|| invalid("order fields must be nonempty strings"))?
                        .to_string()
                };
                pairs.push((key.clone(), text));
            }
            if let Some(symbol) = &outer_symbol {
                pairs.push(("symbol".into(), symbol.clone()));
            }
            let entry = BitgetParams::from_pairs(pairs);
            if margin && !cancel {
                super::schema_requests::validate_margin_order_fields(&entry)?;
            } else if cancel {
                entry.ensure_allowed(&["symbol", "orderId", "clientOid"], false)?;
                identifier(&entry)?;
            } else if name == "modify_uta_batch_orders" {
                entry.ensure_allowed(
                    &[
                        "symbol",
                        "category",
                        "orderId",
                        "clientOid",
                        "requestId",
                        "qty",
                        "price",
                        "autoCancel",
                        "pxAmendType",
                    ],
                    false,
                )?;
                let symbol = required(&entry, "symbol")?;
                let this_category = required(&entry, "category")?;
                if ![
                    "SPOT",
                    "MARGIN",
                    "USDT-FUTURES",
                    "COIN-FUTURES",
                    "USDC-FUTURES",
                ]
                .contains(&this_category)
                {
                    return Err(invalid("unsupported category"));
                }
                if category
                    .as_deref()
                    .is_some_and(|expected| expected != this_category)
                {
                    return Err(invalid("all orders must use the same category"));
                }
                category = Some(this_category.to_string());
                let id = identifier(&entry)?;
                if !seen.insert((symbol.to_string(), id)) {
                    return Err(invalid("an order may appear only once per batch"));
                }
                if entry.get("qty").is_none() && entry.get("price").is_none() {
                    return Err(invalid("qty or price is required for amendment"));
                }
                if let Some(id) = entry.get("clientOid")
                    && (id.len() > 32
                        || !id.chars().all(|c| {
                            c.is_ascii_alphanumeric() || matches!(c, '.' | ':' | '/' | '_' | '-')
                        }))
                {
                    return Err(invalid("invalid clientOid"));
                }
                super::trading_controls::validate("modify_uta_order", &entry)?;
            } else {
                entry.ensure_allowed(
                    &[
                        "symbol",
                        "price",
                        "size",
                        "clientOid",
                        "orderId",
                        "newClientOid",
                        "presetTakeProfitPrice",
                        "executeTakeProfitPrice",
                        "presetStopLossPrice",
                        "executeStopLossPrice",
                    ],
                    false,
                )?;
                for key in ["symbol", "price", "size"] {
                    required(&entry, key)?;
                }
                super::trading_controls::validate("cancel_replace_spot_order", &entry)?;
                for key in [
                    "presetTakeProfitPrice",
                    "executeTakeProfitPrice",
                    "presetStopLossPrice",
                    "executeStopLossPrice",
                ] {
                    if entry.get(key).is_some_and(|text| {
                        !text.parse::<f64>().is_ok_and(|n| n.is_finite() && n >= 0.0)
                    }) {
                        return Err(invalid("TP/SL prices must be nonnegative decimals"));
                    }
                }
            }
        }
        let body = if name == "modify_uta_batch_orders" {
            value
        } else {
            let mut body = Map::new();
            if let Some(symbol) = outer_symbol {
                body.insert("symbol".into(), Value::String(symbol));
            }
            body.insert(field.to_string(), value);
            Value::Object(body)
        };
        Ok(Some(self.post_private(path, body).await?))
    }
}

fn invalid(message: &str) -> DcexError {
    DcexError::InvalidInput(format!("Bitget: {message}"))
}
fn required<'a>(params: &'a BitgetParams, key: &str) -> Result<&'a str> {
    params
        .get(key)
        .filter(|value| !value.trim().is_empty())
        .ok_or_else(|| invalid(&format!("{key} is required")))
}
fn identifier(params: &BitgetParams) -> Result<(bool, String)> {
    if let Some(value) = params.get("orderId") {
        return Ok((true, value.to_string()));
    }
    Ok((false, required(params, "clientOid")?.to_string()))
}
