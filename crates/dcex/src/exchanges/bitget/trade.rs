pub(in crate::exchanges::bitget) use serde_json::Value;

pub(in crate::exchanges::bitget) use crate::Result;
pub(in crate::exchanges::bitget) use crate::exchange::ValidatedResponse;

pub(in crate::exchanges::bitget) use super::client::BitgetClient;
pub(in crate::exchanges::bitget) use super::endpoints::*;
pub(in crate::exchanges::bitget) use super::params::{BitgetParams, require_one_identifier};

pub(in crate::exchanges::bitget) const UTA_ORDER_KEYS: &[&str] = &[
    "category",
    "side",
    "orderType",
    "qty",
    "price",
    "timeInForce",
    "posSide",
    "clientOid",
    "reduceOnly",
    "stpMode",
    "marginMode",
    "tpTriggerBy",
    "slTriggerBy",
    "takeProfit",
    "stopLoss",
    "tpOrderType",
    "slOrderType",
    "tpLimitPrice",
    "slLimitPrice",
    "autoBorrow",
    "pxAmendType",
];

/// Validates a UTA place-order request against the official contract before any request:
/// <https://www.bitget.com/api-doc/uta/trade/Place-Order>. Unknown keys are rejected rather
/// than dropped, and futures-only `reduceOnly` is rejected on SPOT/MARGIN.
pub(in crate::exchanges::bitget) fn validate_uta_order(params: &BitgetParams) -> Result<()> {
    let mut allowed = UTA_ORDER_KEYS.to_vec();
    allowed.push("symbol");
    params.ensure_allowed(&allowed, true)?;
    let one_of = |key: &str, allowed: &[&str]| -> Result<()> {
        match params.get(key) {
            Some(value) if !allowed.contains(&value) => {
                Err(crate::DcexError::InvalidInput(format!(
                    "invalid Bitget {key}: {value}; expected one of {}",
                    allowed.join(", ")
                )))
            }
            _ => Ok(()),
        }
    };
    one_of("timeInForce", &["gtc", "ioc", "fok", "post_only", "rpi"])?;
    one_of("reduceOnly", &["yes", "no"])?;
    one_of("autoBorrow", &["yes", "no"])?;
    one_of("pxAmendType", &["yes", "no"])?;
    let category = params.get("category").unwrap_or_default();
    let futures = ["USDT-FUTURES", "COIN-FUTURES", "USDC-FUTURES"]
        .iter()
        .any(|candidate| candidate.eq_ignore_ascii_case(category));
    // Official Place-Order: autoBorrow is for spot orders only.
    if !category.eq_ignore_ascii_case("SPOT") && params.get("autoBorrow").is_some() {
        return Err(crate::DcexError::InvalidInput(format!(
            "Bitget UTA autoBorrow applies to SPOT only, not {category}"
        )));
    }
    if !futures {
        for key in ["reduceOnly", "posSide", "marginMode"] {
            if params.get(key).is_some() {
                return Err(crate::DcexError::InvalidInput(format!(
                    "Bitget UTA {key} applies to futures categories only, not {category}"
                )));
            }
        }
    }
    Ok(())
}

/// Validates every UTA place-batch element exactly like a single `place_uta_order`, so one
/// unsupported field rejects the whole batch before any request.
pub(in crate::exchanges::bitget) fn validate_uta_batch_orders(orders: &Value) -> Result<()> {
    let items = orders.as_array().ok_or_else(|| {
        crate::DcexError::InvalidInput("Bitget orderList must be a JSON array".to_string())
    })?;
    for item in items {
        let object = item.as_object().ok_or_else(|| {
            crate::DcexError::InvalidInput("each Bitget batch order must be a JSON object".into())
        })?;
        let params = BitgetParams::from_pairs(
            object
                .iter()
                .map(|(key, value)| {
                    let value = match value {
                        Value::String(text) => text.clone(),
                        other => other.to_string(),
                    };
                    (key.clone(), value)
                })
                .collect(),
        );
        for key in ["category", "side", "orderType", "qty"] {
            params.required(key)?;
        }
        require_uta_symbol(&params)?;
        validate_uta_order(&params)?;
    }
    Ok(())
}

impl BitgetClient {
    pub(super) async fn trade_private_request(
        &self,
        method_name: &str,
        params: &BitgetParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "place_uta_order" => self.place_uta_order_from_params(params).await,
            "place_reality_order" => {
                params.ensure_allowed(
                    &[
                        "category",
                        "side",
                        "orderType",
                        "qty",
                        "price",
                        "clientOid",
                        "product_symbol",
                        "symbol",
                        "productType",
                    ],
                    false,
                )?;
                self.place_reality_order_from_params(params).await
            }
            "place_uta_batch_orders" => {
                self.dispatch_place_uta_batch_orders(method_name, params)
                    .await
            }
            "cancel_uta_order" => self.cancel_uta_order_from_params(params).await,
            "cancel_reality_order" => self.cancel_reality_order_from_params(params).await,
            "cancel_uta_batch_orders" => {
                self.dispatch_cancel_uta_batch_orders(method_name, params)
                    .await
            }
            "get_uta_order" => {
                require_one_identifier(params, &["orderId", "clientOid"])?;
                self.get_private(UTA_ORDER_DETAIL, params.only(&["orderId", "clientOid"]))
                    .await
            }
            "get_uta_open_orders" => {
                params.ensure_allowed(
                    &[
                        "category",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
                        "symbol",
                        "productType",
                        "product_symbol",
                    ],
                    false,
                )?;
                let mut query =
                    params.only(&["category", "startTime", "endTime", "limit", "cursor"]);
                self.push_uta_symbol(&mut query, params)?;
                self.get_private(UTA_PENDING_ORDERS, query).await
            }
            "get_uta_history_orders" => {
                params.ensure_allowed(
                    &[
                        "category",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
                        "symbol",
                        "productType",
                        "product_symbol",
                    ],
                    false,
                )?;
                params.required("category")?;
                let mut query =
                    params.only(&["category", "startTime", "endTime", "limit", "cursor"]);
                self.push_uta_symbol(&mut query, params)?;
                self.get_private(UTA_HISTORY_ORDERS, query).await
            }
            "get_uta_fills" => {
                params.ensure_allowed(
                    &[
                        "category",
                        "orderId",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
                    ],
                    false,
                )?;
                self.get_private(
                    UTA_FILLS,
                    params.only(&[
                        "category",
                        "orderId",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
                    ]),
                )
                .await
            }
            "get_uta_positions" => {
                params.ensure_allowed(
                    &[
                        "category",
                        "posSide",
                        "symbol",
                        "productType",
                        "product_symbol",
                    ],
                    false,
                )?;
                params.required("category")?;
                let mut query = params.only(&["category", "posSide"]);
                self.push_uta_symbol(&mut query, params)?;
                self.get_private(UTA_POSITIONS, query).await
            }
            "place_uta_strategy_order" => {
                params.ensure_allowed(
                    &[
                        "category",
                        "clientOid",
                        "type",
                        "tpslMode",
                        "qty",
                        "side",
                        "posSide",
                        "reduceOnly",
                        "tpTriggerBy",
                        "slTriggerBy",
                        "takeProfit",
                        "stopLoss",
                        "tpOrderType",
                        "slOrderType",
                        "tpLimitPrice",
                        "slLimitPrice",
                        "triggerBy",
                        "triggerPrice",
                        "triggerOrderType",
                        "triggerOrderPrice",
                        "product_symbol",
                        "symbol",
                        "productType",
                    ],
                    false,
                )?;
                params.required("category")?;
                require_uta_symbol(params)?;
                let mut body = params.body(&[
                    "category",
                    "clientOid",
                    "type",
                    "tpslMode",
                    "qty",
                    "side",
                    "posSide",
                    "reduceOnly",
                    "tpTriggerBy",
                    "slTriggerBy",
                    "takeProfit",
                    "stopLoss",
                    "tpOrderType",
                    "slOrderType",
                    "tpLimitPrice",
                    "slLimitPrice",
                    "triggerBy",
                    "triggerPrice",
                    "triggerOrderType",
                    "triggerOrderPrice",
                ]);
                self.insert_required_product_symbol(&mut body, params)?;
                self.post_private(UTA_PLACE_STRATEGY_ORDER, Value::Object(body))
                    .await
            }
            "modify_uta_strategy_order" => {
                params.required("orderId")?;
                params.required("qty")?;
                self.post_private(
                    UTA_MODIFY_STRATEGY_ORDER,
                    Value::Object(params.body(&[
                        "orderId",
                        "clientOid",
                        "qty",
                        "tpTriggerBy",
                        "slTriggerBy",
                        "takeProfit",
                        "stopLoss",
                        "tpOrderType",
                        "slOrderType",
                        "tpLimitPrice",
                        "slLimitPrice",
                        "triggerBy",
                        "triggerPrice",
                        "triggerOrderType",
                        "triggerOrderPrice",
                    ])),
                )
                .await
            }
            "cancel_uta_strategy_order" => {
                params.ensure_allowed(&["orderId", "clientOid"], false)?;
                params.required("orderId")?;
                self.post_private(
                    UTA_CANCEL_STRATEGY_ORDER,
                    Value::Object(params.body(&["orderId", "clientOid"])),
                )
                .await
            }
            "get_uta_unfilled_strategy_orders" => {
                params.ensure_allowed(&["category", "type"], false)?;
                params.required("category")?;
                self.get_private(
                    UTA_UNFILLED_STRATEGY_ORDERS,
                    params.only(&["category", "type"]),
                )
                .await
            }
            "get_uta_history_strategy_orders" => {
                params.ensure_allowed(
                    &[
                        "category",
                        "type",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
                    ],
                    false,
                )?;
                params.required("category")?;
                self.get_private(
                    UTA_HISTORY_STRATEGY_ORDERS,
                    params.only(&[
                        "category",
                        "type",
                        "startTime",
                        "endTime",
                        "limit",
                        "cursor",
                    ]),
                )
                .await
            }

            _ => return Ok(None),
        };
        Ok(Some(result?))
    }

    pub(in crate::exchanges::bitget) async fn place_uta_order_from_params(
        &self,
        params: &BitgetParams,
    ) -> Result<ValidatedResponse> {
        for key in ["category", "side", "orderType", "qty"] {
            params.required(key)?;
        }
        validate_uta_order(params)?;
        let mut body = params.body(UTA_ORDER_KEYS);
        require_uta_symbol(params)?;
        self.insert_uta_symbol(&mut body, params)?;
        self.post_private(UTA_PLACE_ORDER, Value::Object(body))
            .await
    }

    pub(in crate::exchanges::bitget) async fn cancel_uta_order_from_params(
        &self,
        params: &BitgetParams,
    ) -> Result<ValidatedResponse> {
        require_one_identifier(params, &["orderId", "clientOid"])?;
        self.post_private(
            UTA_CANCEL_ORDER,
            Value::Object(params.body(&["orderId", "clientOid", "category"])),
        )
        .await
    }

    pub(in crate::exchanges::bitget) async fn place_reality_order_from_params(
        &self,
        params: &BitgetParams,
    ) -> Result<ValidatedResponse> {
        for key in ["side", "orderType", "qty"] {
            params.required(key)?;
        }
        require_uta_symbol(params)?;
        let mut body = params.body(&["category", "side", "orderType", "qty", "price", "clientOid"]);
        self.insert_uta_symbol(&mut body, params)?;
        self.post_private(REALITY_PLACE_ORDER, Value::Object(body))
            .await
    }

    pub(in crate::exchanges::bitget) async fn cancel_reality_order_from_params(
        &self,
        params: &BitgetParams,
    ) -> Result<ValidatedResponse> {
        require_uta_symbol(params)?;
        require_one_identifier(params, &["orderId", "clientOid"])?;
        let mut body = params.body(&["category", "orderId", "clientOid"]);
        self.insert_uta_symbol(&mut body, params)?;
        self.post_private(REALITY_CANCEL_ORDER, Value::Object(body))
            .await
    }
}

pub(in crate::exchanges::bitget) fn require_uta_symbol(params: &BitgetParams) -> Result<()> {
    require_one_identifier(params, &["product_symbol", "symbol"])
}

#[cfg(test)]
mod tests {
    use super::*;

    fn uta(items: &[(&str, &str)]) -> BitgetParams {
        let mut pairs = vec![
            ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
            ("side".to_string(), "buy".to_string()),
            ("orderType".to_string(), "limit".to_string()),
            ("qty".to_string(), "1".to_string()),
        ];
        pairs.extend(
            items
                .iter()
                .map(|(key, value)| ((*key).to_string(), (*value).to_string())),
        );
        BitgetParams::from_pairs(pairs)
    }

    #[test]
    fn uta_order_accepts_documented_values() {
        for tif in ["gtc", "ioc", "fok", "post_only", "rpi"] {
            validate_uta_order(&uta(&[
                ("category", "USDT-FUTURES"),
                ("timeInForce", tif),
                ("reduceOnly", "yes"),
                ("posSide", "long"),
                ("stpMode", "cancel_both"),
            ]))
            .expect("documented futures values");
        }
        validate_uta_order(&uta(&[
            ("category", "SPOT"),
            ("autoBorrow", "no"),
            ("pxAmendType", "yes"),
            ("clientOid", "c1"),
        ]))
        .expect("documented spot values");
    }

    #[test]
    fn uta_order_rejects_unknown_keys_and_unsupported_values() {
        for items in [
            &[("category", "SPOT"), ("presetTakeProfit", "1")][..],
            &[("category", "SPOT"), ("productType", "SPOT")],
            &[("category", "USDT-FUTURES"), ("timeInForce", "GTC")],
            &[("category", "USDT-FUTURES"), ("timeInForce", "gtd")],
            &[("category", "USDT-FUTURES"), ("reduceOnly", "true")],
            &[("category", "SPOT"), ("reduceOnly", "no")],
            &[("category", "MARGIN"), ("posSide", "long")],
        ] {
            assert!(validate_uta_order(&uta(items)).is_err(), "{items:?}");
        }
    }

    #[test]
    fn uta_batch_elements_are_validated_like_single_orders() {
        let valid = serde_json::json!([
            {"category": "USDT-FUTURES", "symbol": "BTCUSDT", "side": "buy",
             "orderType": "limit", "qty": "1", "price": "100", "timeInForce": "post_only",
             "reduceOnly": "yes", "clientOid": "c1"}
        ]);
        validate_uta_batch_orders(&valid).expect("documented batch element");
        let base = r#""symbol":"BTCUSDT","side":"buy","orderType":"limit","qty":"1""#;
        for extra in [
            r#""category":"SPOT","reduceOnly":"yes""#,
            r#""category":"USDT-FUTURES","timeInForce":"GTC""#,
            r#""category":"SPOT","presetTakeProfit":"1""#,
            r#""side2":"x""#,
            r#""category":"SPOT","autoBorrow":"true""#,
            r#""category":"USDT-FUTURES","autoBorrow":"yes""#,
            r#""category":"MARGIN","autoBorrow":"yes""#,
            r#""category":"SPOT","pxAmendType":"1""#,
        ] {
            let bad: Value = serde_json::from_str(&format!("[{{{base},{extra}}}]")).unwrap();
            assert!(validate_uta_batch_orders(&bad).is_err(), "{bad}");
        }
    }

    #[test]
    pub(in crate::exchanges::bitget) fn preserves_uta_protection_fields() {
        let params = BitgetParams::from_pairs(vec![
            ("takeProfit".to_string(), "110".to_string()),
            ("stopLoss".to_string(), "90".to_string()),
            ("tpOrderType".to_string(), "limit".to_string()),
            ("slLimitPrice".to_string(), "89".to_string()),
        ]);
        let body = params.body(UTA_ORDER_KEYS);
        assert!(body.contains_key("takeProfit"));
        assert!(body.contains_key("stopLoss"));
        assert!(body.contains_key("tpOrderType"));
        assert!(body.contains_key("slLimitPrice"));
    }
}
