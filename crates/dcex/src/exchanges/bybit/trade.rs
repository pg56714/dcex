pub(in crate::exchanges::bybit) use serde_json::{Map, Value};

pub(in crate::exchanges::bybit) use super::client::BybitClient;
pub(in crate::exchanges::bybit) use super::endpoints::*;
pub(in crate::exchanges::bybit) use super::params::{
    BybitParams, insert_optional_bool, insert_optional_i64, insert_optional_string, push_optional,
    require_one_identifier,
};
pub(in crate::exchanges::bybit) use crate::Result;
pub(in crate::exchanges::bybit) use crate::common::OrderSide;
pub(in crate::exchanges::bybit) use crate::exchange::ValidatedResponse;

/// Documented `/v5/order/create` body keys: <https://bybit-exchange.github.io/docs/v5/order/create-order>.
const ORDER_STRING_KEYS: [&str; 21] = [
    "price",
    "marketUnit",
    "slippageToleranceType",
    "slippageTolerance",
    "orderFilter",
    "triggerPrice",
    "triggerBy",
    "orderIv",
    "timeInForce",
    "takeProfit",
    "stopLoss",
    "tpTriggerBy",
    "slTriggerBy",
    "tpslMode",
    "tpLimitPrice",
    "slLimitPrice",
    "tpOrderType",
    "slOrderType",
    "orderLinkId",
    "smpType",
    "bboSideType",
];
const ORDER_INT_KEYS: [&str; 4] = ["isLeverage", "triggerDirection", "positionIdx", "bboLevel"];
const ORDER_BOOL_KEYS: [&str; 4] = ["rpiTakerAccess", "reduceOnly", "closeOnTrigger", "mmp"];

/// Rejects undocumented keys and enum values before any request, so nothing is silently
/// dropped. Enums: <https://bybit-exchange.github.io/docs/v5/enum>.
pub(in crate::exchanges::bybit) fn validate_order_params(params: &BybitParams) -> Result<()> {
    validate_order_fields(params, &["product_symbol", "category"])
}

fn validate_order_fields(params: &BybitParams, extra_keys: &[&str]) -> Result<()> {
    for (key, _) in params.pairs() {
        let key = key.as_str();
        let known = matches!(key, "side" | "orderType" | "qty")
            || extra_keys.contains(&key)
            || ORDER_STRING_KEYS.contains(&key)
            || ORDER_INT_KEYS.contains(&key)
            || ORDER_BOOL_KEYS.contains(&key);
        if !known {
            return Err(crate::DcexError::InvalidInput(format!(
                "unsupported Bybit order parameter: {key}"
            )));
        }
    }
    for (key, allowed) in [
        ("orderType", &["Market", "Limit"][..]),
        ("timeInForce", &["GTC", "IOC", "FOK", "PostOnly", "RPI"][..]),
        (
            "smpType",
            &["None", "CancelMaker", "CancelTaker", "CancelBoth"][..],
        ),
    ] {
        if let Some(value) = params.get(key)
            && !allowed.contains(&value)
        {
            return Err(crate::DcexError::InvalidInput(format!(
                "invalid Bybit {key}: {value}; expected one of {}",
                allowed.join(", ")
            )));
        }
    }
    Ok(())
}

/// Applies a convenience method's fixed fields, rejecting a conflicting caller value
/// instead of silently replacing it.
fn forced_order_params(params: &BybitParams, forced: &[(&str, &str)]) -> Result<BybitParams> {
    let keys: Vec<&str> = forced.iter().map(|(key, _)| *key).collect();
    for (key, value) in forced {
        // Side is accepted case-insensitively (OrderSide::parse); other fields are exact.
        if let Some(existing) = params.get(key)
            && !(existing == *value || *key == "side" && existing.eq_ignore_ascii_case(value))
        {
            return Err(crate::DcexError::InvalidInput(format!(
                "this Bybit order method sets {key}={value}; got conflicting {key}={existing}"
            )));
        }
    }
    let mut pairs = params.without(&keys);
    pairs.extend(
        forced
            .iter()
            .map(|(key, value)| ((*key).to_string(), (*value).to_string())),
    );
    Ok(BybitParams::from_pairs(pairs))
}

/// Documented `/v5/order/amend` fields: <https://bybit-exchange.github.io/docs/v5/order/amend-order>.
const AMEND_ORDER_KEYS: &[&str] = &[
    "orderId",
    "orderLinkId",
    "orderIv",
    "triggerPrice",
    "qty",
    "price",
    "tpslMode",
    "takeProfit",
    "stopLoss",
    "tpTriggerBy",
    "slTriggerBy",
    "triggerBy",
    "tpLimitPrice",
    "slLimitPrice",
];

fn ensure_amend_keys(params: &BybitParams, extra_keys: &[&str]) -> Result<()> {
    for (key, _) in params.pairs() {
        if !(AMEND_ORDER_KEYS.contains(&key.as_str()) || extra_keys.contains(&key.as_str())) {
            return Err(crate::DcexError::InvalidInput(format!(
                "unsupported Bybit amend parameter: {key}"
            )));
        }
    }
    Ok(())
}

/// Validates every create-batch / amend-batch element like the single-order path, so an
/// unsupported field rejects the whole batch before any request.
/// <https://bybit-exchange.github.io/docs/v5/order/batch-place>,
/// <https://bybit-exchange.github.io/docs/v5/order/batch-amend>.
pub(in crate::exchanges::bybit) fn validate_batch_request(
    request: &Value,
    amend: bool,
) -> Result<()> {
    let items = request.as_array().ok_or_else(|| {
        crate::DcexError::InvalidInput("Bybit batch request must be a JSON array".to_string())
    })?;
    for item in items {
        let object = item.as_object().ok_or_else(|| {
            crate::DcexError::InvalidInput("each Bybit batch item must be a JSON object".into())
        })?;
        let params = BybitParams::from_pairs(
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
        params.required("symbol")?;
        if amend {
            ensure_amend_keys(&params, &["symbol"])?;
            require_one_identifier(&params, &["orderId", "orderLinkId"])?;
        } else {
            validate_order_fields(&params, &["symbol"])?;
            for key in ORDER_BOOL_KEYS {
                if let Some(value) = params.get(key)
                    && !matches!(value, "true" | "false")
                {
                    return Err(crate::DcexError::InvalidInput(format!(
                        "invalid boolean parameter {key}: {value}"
                    )));
                }
            }
        }
    }
    Ok(())
}

impl BybitClient {
    pub(super) async fn trade_private_request(
        &self,
        method_name: &str,
        params: &BybitParams,
    ) -> Result<Option<ValidatedResponse>> {
        let result = match method_name {
            "place_order" => self.place_order_from_params(params).await,
            "pre_check_order" => self.pre_check_order_from_params(params).await,
            "set_disconnected_cancel_all" => {
                let mut body = Map::new();
                insert_optional_string(&mut body, "product", params.get("product"));
                body.insert(
                    "timeWindow".to_string(),
                    Value::Number(params.i64_required("timeWindow")?.into()),
                );
                self.post_request(DISCONNECTED_CANCEL_ALL, body).await
            }
            "place_market_order" => {
                self.place_order_from_params(&forced_order_params(
                    params,
                    &[("orderType", "Market")],
                )?)
                .await
            }
            "place_market_buy_order" => {
                self.place_order_from_params(&forced_order_params(
                    params,
                    &[("side", "Buy"), ("orderType", "Market")],
                )?)
                .await
            }
            "place_market_sell_order" => {
                self.place_order_from_params(&forced_order_params(
                    params,
                    &[("side", "Sell"), ("orderType", "Market")],
                )?)
                .await
            }
            "place_limit_order" => {
                self.place_order_from_params(&forced_order_params(
                    params,
                    &[("orderType", "Limit")],
                )?)
                .await
            }
            "place_limit_buy_order" => {
                self.place_order_from_params(&forced_order_params(
                    params,
                    &[("side", "Buy"), ("orderType", "Limit")],
                )?)
                .await
            }
            "place_limit_sell_order" => {
                self.place_order_from_params(&forced_order_params(
                    params,
                    &[("side", "Sell"), ("orderType", "Limit")],
                )?)
                .await
            }
            "place_post_only_limit_order" => {
                self.place_order_from_params(&forced_order_params(
                    params,
                    &[("orderType", "Limit"), ("timeInForce", "PostOnly")],
                )?)
                .await
            }
            "place_post_only_limit_buy_order" => {
                self.place_order_from_params(&forced_order_params(
                    params,
                    &[
                        ("side", "Buy"),
                        ("orderType", "Limit"),
                        ("timeInForce", "PostOnly"),
                    ],
                )?)
                .await
            }
            "place_post_only_limit_sell_order" => {
                self.place_order_from_params(&forced_order_params(
                    params,
                    &[
                        ("side", "Sell"),
                        ("orderType", "Limit"),
                        ("timeInForce", "PostOnly"),
                    ],
                )?)
                .await
            }
            "amend_order" => self.amend_order_from_params(params).await,
            "cancel_order" => self.cancel_order_from_params(params).await,
            "get_open_orders" => self.get_open_orders_from_params(params).await,
            "cancel_batch_orders" => self.dispatch_cancel_batch_orders(method_name, params).await,
            "cancel_all_orders" => self.cancel_all_orders_from_params(params).await,
            "get_order_history" => self.get_order_history_from_params(params).await,
            "get_execution_list" => self.get_execution_list_from_params(params).await,
            "place_batch_order" => self.dispatch_place_batch_order(method_name, params).await,
            "amend_batch_order" => self.dispatch_amend_batch_order(method_name, params).await,
            "get_borrow_quota" => {
                let product_symbol = params.required("product_symbol")?;
                let query = vec![
                    ("category".to_string(), "spot".to_string()),
                    (
                        "symbol".to_string(),
                        self.symbol_category(product_symbol, Some("spot"))?.0,
                    ),
                    (
                        "side".to_string(),
                        OrderSide::parse(params.required("side")?)?
                            .to_exchange("bybit")?
                            .to_string(),
                    ),
                ];
                self.get_request(GET_BORROW_QUOTA, query).await
            }
            "get_vip_margin_data" => {
                self.get_request(VIP_MARGIN_DATA, params.only(&["vipLevel", "currency"]))
                    .await
            }
            "get_collateral" => {
                self.get_request(SPOT_MARGIN_COLLATERAL, params.only(&["currency"]))
                    .await
            }
            "get_historical_interest_rate" => {
                let mut query = vec![(
                    "currency".to_string(),
                    params.required("currency")?.to_string(),
                )];
                push_optional(&mut query, "vipLevel", params.get("vipLevel"));
                push_optional(&mut query, "startTime", params.get("startTime"));
                push_optional(&mut query, "endTime", params.get("endTime"));
                self.get_request(HISTORICAL_INTEREST, query).await
            }
            "get_status_and_leverage" => self.get_request(STATUS_AND_LEVERAGE, Vec::new()).await,
            "get_margin_max_borrowable" => {
                self.get_request(
                    MARGIN_MAX_BORROWABLE,
                    vec![(
                        "currency".to_string(),
                        params.required("currency")?.to_string(),
                    )],
                )
                .await
            }
            "get_margin_position_tiers" => {
                self.get_request(MARGIN_POSITION_TIERS, params.only(&["currency"]))
                    .await
            }
            "get_margin_coin_state" => {
                self.get_request(MARGIN_COIN_STATE, params.only(&["currency"]))
                    .await
            }
            "get_margin_repayment_available_amount" => {
                self.get_request(
                    MARGIN_REPAYMENT_AVAILABLE_AMOUNT,
                    vec![(
                        "currency".to_string(),
                        params.required("currency")?.to_string(),
                    )],
                )
                .await
            }
            "set_margin_auto_repay_mode" => {
                let mode = params.required("autoRepayMode")?;
                if !["0", "1"].contains(&mode) {
                    return Err(crate::DcexError::InvalidInput(
                        "autoRepayMode must be 0 or 1.".to_string(),
                    ));
                }
                let mut body = Map::new();
                insert_optional_string(&mut body, "currency", params.get("currency"));
                body.insert("autoRepayMode".to_string(), Value::String(mode.to_string()));
                self.post_request(SET_MARGIN_AUTO_REPAY_MODE, body).await
            }
            "get_margin_auto_repay_mode" => {
                self.get_request(GET_MARGIN_AUTO_REPAY_MODE, params.only(&["currency"]))
                    .await
            }
            "get_fixed_borrow_quote" => {
                let mut query = vec![(
                    "orderCurrency".to_string(),
                    params.required("orderCurrency")?.to_string(),
                )];
                for key in ["term", "orderBy", "sort", "limit"] {
                    push_optional(&mut query, key, params.get(key));
                }
                self.get_request(FIXED_BORROW_QUOTE, query).await
            }
            "borrow_fixed_rate" => {
                let mut body = Map::new();
                for key in ["orderCurrency", "orderAmount", "annualRate", "term"] {
                    body.insert(
                        key.to_string(),
                        Value::String(params.required(key)?.to_string()),
                    );
                }
                for key in ["repayType", "strategyType"] {
                    insert_optional_string(&mut body, key, params.get(key));
                }
                self.post_request(FIXED_BORROW, body).await
            }
            "renew_fixed_rate_borrow" => {
                let mut body = Map::new();
                body.insert(
                    "loanId".to_string(),
                    Value::String(params.required("loanId")?.to_string()),
                );
                insert_optional_string(&mut body, "qty", params.get("qty"));
                self.post_request(FIXED_BORROW_RENEW, body).await
            }
            "get_fixed_borrow_orders" => {
                self.get_request(
                    FIXED_BORROW_ORDER_INFO,
                    params.only(&[
                        "orderId",
                        "orderCurrency",
                        "state",
                        "term",
                        "limit",
                        "cursor",
                    ]),
                )
                .await
            }
            "get_fixed_borrow_contracts" => {
                self.get_request(
                    FIXED_BORROW_CONTRACT_INFO,
                    params.only(&["orderId", "orderCurrency", "term", "limit", "cursor"]),
                )
                .await
            }
            "get_margin_liability" => {
                self.get_request(
                    MARGIN_LIABILITY,
                    vec![(
                        "currency".to_string(),
                        params.required("currency")?.to_string(),
                    )],
                )
                .await
            }
            "get_flexible_borrow_inventory" => {
                self.get_request(
                    FLEXIBLE_BORROW_INVENTORY,
                    vec![(
                        "currency".to_string(),
                        params.required("currency")?.to_string(),
                    )],
                )
                .await
            }
            "get_fixed_borrow_inventory" => {
                self.get_request(
                    FIXED_BORROW_INVENTORY,
                    vec![
                        (
                            "currency".to_string(),
                            params.required("currency")?.to_string(),
                        ),
                        ("term".to_string(), params.required("term")?.to_string()),
                        (
                            "annualRate".to_string(),
                            params.required("annualRate")?.to_string(),
                        ),
                    ],
                )
                .await
            }
            _ => return Ok(None),
        };
        Ok(Some(result?))
    }

    pub(in crate::exchanges::bybit) async fn place_order_from_params(
        &self,
        params: &BybitParams,
    ) -> Result<ValidatedResponse> {
        self.order_validation_request(params, PLACE_ORDER).await
    }

    pub(in crate::exchanges::bybit) async fn pre_check_order_from_params(
        &self,
        params: &BybitParams,
    ) -> Result<ValidatedResponse> {
        self.order_validation_request(params, ORDER_PRE_CHECK).await
    }

    pub(in crate::exchanges::bybit) async fn order_validation_request(
        &self,
        params: &BybitParams,
        endpoint: &str,
    ) -> Result<ValidatedResponse> {
        let body = self.order_body_from_params(params)?;
        self.post_request(endpoint, body).await
    }

    pub(in crate::exchanges::bybit) fn order_body_from_params(
        &self,
        params: &BybitParams,
    ) -> Result<Map<String, Value>> {
        validate_order_params(params)?;
        let product_symbol = params.required("product_symbol")?;
        let mut body = Map::new();
        self.insert_symbol_category(&mut body, product_symbol, params.get("category"))?;
        body.insert(
            "side".to_string(),
            Value::String(
                OrderSide::parse(params.required("side")?)?
                    .to_exchange("bybit")?
                    .to_string(),
            ),
        );
        body.insert(
            "orderType".to_string(),
            Value::String(params.required("orderType")?.to_string()),
        );
        body.insert(
            "qty".to_string(),
            Value::String(params.required("qty")?.to_string()),
        );
        for key in ORDER_STRING_KEYS {
            insert_optional_string(&mut body, key, params.get(key));
        }
        for key in ORDER_INT_KEYS {
            insert_optional_i64(&mut body, key, params.get(key))?;
        }
        for key in ORDER_BOOL_KEYS {
            insert_optional_bool(&mut body, key, params.get(key))?;
        }
        Ok(body)
    }

    pub(in crate::exchanges::bybit) async fn amend_order_from_params(
        &self,
        params: &BybitParams,
    ) -> Result<ValidatedResponse> {
        ensure_amend_keys(params, &["product_symbol", "category"])?;
        require_one_identifier(params, &["orderId", "orderLinkId"])?;
        let product_symbol = params.required("product_symbol")?;
        let mut body = Map::new();
        self.insert_symbol_category(&mut body, product_symbol, params.get("category"))?;
        for key in [
            "orderId",
            "orderLinkId",
            "orderIv",
            "triggerPrice",
            "qty",
            "price",
            "tpslMode",
            "takeProfit",
            "stopLoss",
            "tpTriggerBy",
            "slTriggerBy",
            "triggerBy",
            "tpLimitPrice",
            "slLimitPrice",
        ] {
            insert_optional_string(&mut body, key, params.get(key));
        }
        self.post_request(AMEND_ORDER, body).await
    }

    pub(in crate::exchanges::bybit) async fn cancel_order_from_params(
        &self,
        params: &BybitParams,
    ) -> Result<ValidatedResponse> {
        require_one_identifier(params, &["orderId", "orderLinkId"])?;
        let product_symbol = params.required("product_symbol")?;
        let mut body = Map::new();
        self.insert_symbol_category(&mut body, product_symbol, params.get("category"))?;
        for key in ["orderId", "orderLinkId", "orderFilter"] {
            insert_optional_string(&mut body, key, params.get(key));
        }
        self.post_request(CANCEL_ORDER, body).await
    }

    pub(in crate::exchanges::bybit) async fn get_open_orders_from_params(
        &self,
        params: &BybitParams,
    ) -> Result<ValidatedResponse> {
        let category = params.get("category").unwrap_or("linear");
        let mut query = vec![
            ("category".to_string(), category.to_string()),
            (
                "limit".to_string(),
                params.get("limit").unwrap_or("20").to_string(),
            ),
        ];
        if let Some(product_symbol) = params.get("product_symbol") {
            self.push_symbol_category(&mut query, product_symbol, params.get("category"), true)?;
        } else {
            push_optional(&mut query, "baseCoin", params.get("baseCoin"));
            if let Some(settle_coin) = params.get("settleCoin") {
                query.push(("settleCoin".to_string(), settle_coin.to_string()));
            } else if category == "linear" {
                query.push(("settleCoin".to_string(), "USDT".to_string()));
            }
        }
        for key in [
            "orderId",
            "orderLinkId",
            "openOnly",
            "orderFilter",
            "cursor",
        ] {
            push_optional(&mut query, key, params.get(key));
        }
        self.get_request(GET_OPEN_ORDERS, query).await
    }

    pub(in crate::exchanges::bybit) async fn cancel_all_orders_from_params(
        &self,
        params: &BybitParams,
    ) -> Result<ValidatedResponse> {
        let body = self.cancel_all_orders_body_from_params(params)?;
        self.post_request(CANCEL_ALL_ORDERS, body).await
    }

    pub(in crate::exchanges::bybit) fn cancel_all_orders_body_from_params(
        &self,
        params: &BybitParams,
    ) -> Result<Map<String, Value>> {
        let mut body = Map::new();
        body.insert(
            "category".to_string(),
            Value::String(params.get("category").unwrap_or("linear").to_string()),
        );
        if let Some(product_symbol) = params.get("product_symbol") {
            self.insert_symbol_category(&mut body, product_symbol, params.get("category"))?;
        }
        for key in ["baseCoin", "settleCoin", "orderFilter", "stopOrderType"] {
            insert_optional_string(&mut body, key, params.get(key));
        }
        let category = body
            .get("category")
            .and_then(Value::as_str)
            .unwrap_or("linear");
        if ["linear", "inverse"]
            .iter()
            .any(|candidate| category.eq_ignore_ascii_case(candidate))
            && !["symbol", "baseCoin", "settleCoin"]
                .iter()
                .any(|key| body.contains_key(*key))
        {
            return Err(crate::DcexError::InvalidInput(
                "one of product_symbol, baseCoin, settleCoin is required for Bybit linear or inverse cancel-all"
                    .to_string(),
            ));
        }
        Ok(body)
    }

    pub(in crate::exchanges::bybit) async fn get_order_history_from_params(
        &self,
        params: &BybitParams,
    ) -> Result<ValidatedResponse> {
        let mut query = vec![(
            "category".to_string(),
            params.get("category").unwrap_or("linear").to_string(),
        )];
        if let Some(product_symbol) = params.get("product_symbol") {
            self.push_symbol_category(&mut query, product_symbol, params.get("category"), true)?;
        }
        for key in [
            "baseCoin",
            "settleCoin",
            "orderId",
            "orderLinkId",
            "orderFilter",
            "orderStatus",
            "startTime",
            "endTime",
            "cursor",
            "limit",
        ] {
            push_optional(&mut query, key, params.get(key));
        }
        self.get_request(GET_ORDER_HISTORY, query).await
    }

    pub(in crate::exchanges::bybit) async fn get_execution_list_from_params(
        &self,
        params: &BybitParams,
    ) -> Result<ValidatedResponse> {
        let mut query = vec![
            (
                "category".to_string(),
                params.get("category").unwrap_or("linear").to_string(),
            ),
            (
                "limit".to_string(),
                params.get("limit").unwrap_or("50").to_string(),
            ),
        ];
        if let Some(product_symbol) = params.get("product_symbol") {
            self.push_symbol_category(&mut query, product_symbol, params.get("category"), true)?;
        }
        for key in [
            "orderId",
            "orderLinkId",
            "baseCoin",
            "settleCoin",
            "startTime",
            "endTime",
            "execType",
            "cursor",
        ] {
            push_optional(&mut query, key, params.get(key));
        }
        self.get_request(GET_EXECUTION_LIST, query).await
    }
}

#[cfg(test)]
mod tests {
    use std::time::Duration;

    use super::*;
    use crate::DcexError;

    fn order(items: &[(&str, &str)]) -> BybitParams {
        let mut pairs = vec![
            ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
            ("side".to_string(), "Buy".to_string()),
            ("orderType".to_string(), "Limit".to_string()),
            ("qty".to_string(), "1".to_string()),
            ("price".to_string(), "100".to_string()),
        ];
        for (key, value) in items {
            pairs.retain(|(existing, _)| existing != key);
            pairs.push(((*key).to_string(), (*value).to_string()));
        }
        BybitParams::from_pairs(pairs)
    }

    #[test]
    fn order_accepts_documented_enums_and_rejects_others() {
        for tif in ["GTC", "IOC", "FOK", "PostOnly", "RPI"] {
            client()
                .order_body_from_params(&order(&[("timeInForce", tif), ("smpType", "CancelBoth")]))
                .expect("documented timeInForce");
        }
        for (key, value) in [
            ("timeInForce", "GTX"),
            ("timeInForce", "postonly"),
            ("orderType", "LIMIT"),
            ("smpType", "CancelAll"),
            ("clientOrderId", "x"),
            ("postOnly", "true"),
        ] {
            assert!(
                client()
                    .order_body_from_params(&order(&[(key, value)]))
                    .is_err(),
                "{key}={value}"
            );
        }
    }

    #[test]
    fn batch_items_are_validated_like_single_orders() {
        let place = serde_json::json!([
            {"symbol": "BTCUSDT", "side": "Buy", "orderType": "Limit", "qty": "1",
             "price": "100", "timeInForce": "PostOnly", "orderLinkId": "a", "reduceOnly": false}
        ]);
        validate_batch_request(&place, false).expect("documented create-batch item");
        let amend = serde_json::json!([{"symbol": "BTCUSDT", "orderId": "1", "price": "101"}]);
        validate_batch_request(&amend, true).expect("documented amend-batch item");
        for (bad, is_amend) in [
            (
                serde_json::json!([{"symbol": "BTCUSDT", "timeInForce": "GTX"}]),
                false,
            ),
            (
                serde_json::json!([{"symbol": "BTCUSDT", "clientOrderId": "x"}]),
                false,
            ),
            (
                serde_json::json!([{"symbol": "BTCUSDT", "reduceOnly": "yes"}]),
                false,
            ),
            (
                serde_json::json!([{"symbol": "BTCUSDT", "orderId": "1", "side": "Buy"}]),
                true,
            ),
            (
                serde_json::json!([{"symbol": "BTCUSDT", "price": "1"}]),
                true,
            ),
            (serde_json::json!([{"orderId": "1"}]), true),
        ] {
            assert!(validate_batch_request(&bad, is_amend).is_err(), "{bad}");
        }
    }

    #[test]
    fn amend_rejects_undocumented_keys() {
        let params = BybitParams::from_pairs(vec![
            ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
            ("orderId".to_string(), "1".to_string()),
            ("timeInForce".to_string(), "IOC".to_string()),
        ]);
        assert!(ensure_amend_keys(&params, &["product_symbol", "category"]).is_err());
    }

    #[test]
    fn convenience_side_conflict_is_case_insensitive() {
        let params = order(&[("side", "buy")]);
        assert!(forced_order_params(&params, &[("side", "Buy")]).is_ok());
        let params = order(&[("side", "sell")]);
        assert!(forced_order_params(&params, &[("side", "Buy")]).is_err());
    }

    #[test]
    fn convenience_methods_reject_conflicting_fixed_fields() {
        let params = order(&[("timeInForce", "IOC")]);
        assert!(forced_order_params(&params, &[("timeInForce", "PostOnly")]).is_err());
        let params = order(&[("timeInForce", "PostOnly")]);
        let forced = forced_order_params(&params, &[("timeInForce", "PostOnly")]).expect("same");
        assert_eq!(forced.get("timeInForce"), Some("PostOnly"));
    }

    pub(in crate::exchanges::bybit) fn client() -> BybitClient {
        BybitClient::public(5_000, false, Duration::from_secs(1)).expect("client")
    }

    #[test]
    pub(in crate::exchanges::bybit) fn linear_cancel_all_requires_a_scope() {
        let error = client()
            .cancel_all_orders_body_from_params(&BybitParams::from_pairs(Vec::new()))
            .expect_err("missing scope must fail");

        assert_eq!(
            error,
            DcexError::InvalidInput(
                "one of product_symbol, baseCoin, settleCoin is required for Bybit linear or inverse cancel-all"
                    .to_string()
            )
        );
    }

    #[test]
    pub(in crate::exchanges::bybit) fn cancel_all_forwards_official_scope_and_filter_fields() {
        let body = client()
            .cancel_all_orders_body_from_params(&BybitParams::from_pairs(vec![
                ("category".to_string(), "linear".to_string()),
                ("settleCoin".to_string(), "USDT".to_string()),
                ("orderFilter".to_string(), "Order".to_string()),
            ]))
            .expect("body");

        assert_eq!(
            body.get("settleCoin"),
            Some(&Value::String("USDT".to_string()))
        );
        assert_eq!(
            body.get("orderFilter"),
            Some(&Value::String("Order".to_string()))
        );
    }

    #[test]
    pub(in crate::exchanges::bybit) fn cancel_all_infers_inverse_category_from_symbol() {
        let body = client()
            .cancel_all_orders_body_from_params(&BybitParams::from_pairs(vec![(
                "product_symbol".to_string(),
                "BTC-USD-SWAP".to_string(),
            )]))
            .expect("body");

        assert_eq!(
            body.get("category"),
            Some(&Value::String("inverse".to_string()))
        );
        assert_eq!(
            body.get("symbol"),
            Some(&Value::String("BTCUSD".to_string()))
        );
    }

    #[test]
    pub(in crate::exchanges::bybit) fn order_body_preserves_official_json_types_and_current_fields()
    {
        let body = client()
            .order_body_from_params(&BybitParams::from_pairs(vec![
                ("product_symbol".to_string(), "BTC-USDT-SWAP".to_string()),
                ("side".to_string(), "Buy".to_string()),
                ("orderType".to_string(), "Market".to_string()),
                ("qty".to_string(), "1".to_string()),
                ("isLeverage".to_string(), "1".to_string()),
                ("positionIdx".to_string(), "2".to_string()),
                ("bboLevel".to_string(), "3".to_string()),
                ("reduceOnly".to_string(), "true".to_string()),
                ("closeOnTrigger".to_string(), "false".to_string()),
                ("rpiTakerAccess".to_string(), "true".to_string()),
                ("mmp".to_string(), "false".to_string()),
                ("orderLinkId".to_string(), "client-order".to_string()),
                ("smpType".to_string(), "CancelMaker".to_string()),
                ("slippageToleranceType".to_string(), "Percent".to_string()),
                ("slippageTolerance".to_string(), "0.5".to_string()),
                ("bboSideType".to_string(), "Queue".to_string()),
            ]))
            .expect("body");

        assert_eq!(body.get("isLeverage"), Some(&Value::Number(1.into())));
        assert_eq!(body.get("positionIdx"), Some(&Value::Number(2.into())));
        assert_eq!(body.get("bboLevel"), Some(&Value::Number(3.into())));
        assert_eq!(body.get("reduceOnly"), Some(&Value::Bool(true)));
        assert_eq!(body.get("closeOnTrigger"), Some(&Value::Bool(false)));
        assert_eq!(body.get("rpiTakerAccess"), Some(&Value::Bool(true)));
        assert_eq!(body.get("mmp"), Some(&Value::Bool(false)));
        assert_eq!(
            body.get("orderLinkId"),
            Some(&Value::String("client-order".to_string()))
        );
        assert_eq!(
            body.get("slippageToleranceType"),
            Some(&Value::String("Percent".to_string()))
        );
    }
}
